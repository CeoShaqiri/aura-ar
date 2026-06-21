"""
The Aura Standard — Deploy-to-AR Operator
Architecture:
  - Every deploy generates a unique session_id (UUID4).
  - GLB is exported as {scene}_{session_id}.glb — never reused.
  - All old GLBs in the export dir are wiped before writing the new one.
  - Export dir is fixed under ~ so location never changes after restart.
  - Context-awareness: if the .blend filepath changed since last deploy
    the session resets so you never see a stale model.
  - Full-featured luxury HTML viewer is written on every deploy.
"""

import bpy  # type: ignore
from bpy.types import Operator  # type: ignore
import os
import sys
import uuid
import socket
import subprocess
import webbrowser
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# Module-level server tracker — killed & restarted on every deploy
# ─────────────────────────────────────────────────────────────────────────────
_server_proc = None
_SERVER_PORT  = 8765   # fixed port so the QR URL never changes
_last_deploy_time = 0.0  # guard against duplicate browser opens

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _export_dir():
    """
    Fixed directory under the user home folder — survives reboots and
    never depends on whether the blend file has been saved.  The HTTP
    server always serves from exactly one location.
    """
    d = os.path.join(os.path.expanduser("~"), ".aura_ar_exports")
    os.makedirs(d, exist_ok=True)
    return d

def _lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()

_SERVER_SCRIPT = """\
import sys, os
from http.server import SimpleHTTPRequestHandler, HTTPServer

class NoCacheHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    def log_message(self, *a):
        pass

os.chdir(sys.argv[1])
HTTPServer(("", int(sys.argv[2])), NoCacheHandler).serve_forever()
"""

def _start_server(directory, port):
    global _server_proc
    # Kill the old server so the port is freed and no stale files are served
    if _server_proc is not None:
        try:
            _server_proc.terminate()
            _server_proc.wait(timeout=3)
        except Exception:
            pass
        _server_proc = None

    import tempfile
    script = os.path.join(tempfile.gettempdir(), "aura_ar_server.py")
    with open(script, "w") as f:
        f.write(_SERVER_SCRIPT)
    cmd = [sys.executable, script, directory, str(port)]
    kw = {}
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        kw["startupinfo"] = si
        # NOTE: NOT using DETACHED_PROCESS so we can terminate() it later
    _server_proc = subprocess.Popen(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw
    )

_VIEWER_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta http-equiv="Cache-Control" content="no-cache,no-store,must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<title>%%SCENE%% &mdash; The Aura Standard</title>
<script type="module" src="https://unpkg.com/@google/model-viewer@3.5.0/dist/model-viewer.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --c1:#F28D52;--c2:#BDD9F2;--c3:#5A6B8C;
  --bg:#071526;--glass:rgba(13,31,53,.88);--glass2:rgba(7,15,28,.97);
  --border:rgba(189,217,242,.10);--text:#F2F2F2;--text2:#BDD9F2;--text3:#5A6B8C;
  --r:16px;--rs:11px;
}
html,body{width:100%;height:100%;overflow:hidden;background:var(--bg);background-image:radial-gradient(ellipse 70% 50% at 50% 0%,rgba(242,141,82,.06) 0%,transparent 60%);
  color:var(--text);font-family:'Inter',"Segoe UI",system-ui,-apple-system,sans-serif;
  -webkit-font-smoothing:antialiased}

/* ── model-viewer: fills viewport, model auto-centred ── */
model-viewer{
  position:fixed;top:0;left:0;
  width:100vw;height:100vh;
  display:block;
  z-index:0;
  --progress-bar-color:transparent;--progress-mask:transparent;
}

/* ── loading overlay ─────────────────────────────────── */
#loader{position:fixed;inset:0;z-index:300;background:var(--bg);
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;
  transition:opacity .6s}
#loader.out{opacity:0;pointer-events:none}
.ring{width:68px;height:68px;border-radius:50%;
  background:conic-gradient(from 0deg,var(--c1),var(--c2),var(--c3),var(--c1));
  display:flex;align-items:center;justify-content:center;
  animation:spin 1.1s linear infinite}
.ring::after{content:'';width:50px;height:50px;border-radius:50%;background:var(--bg)}
@keyframes spin{to{transform:rotate(360deg)}}
#l-title{font-size:22px;font-weight:800;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
#l-sub{font-size:13px;color:var(--text3)}

/* ── top bar ─────────────────────────────────────────── */
#topbar{position:fixed;top:0;left:0;right:0;z-index:9998;
  padding:max(env(safe-area-inset-top),12px) 16px 14px;
  display:flex;align-items:center;gap:10px;
  background:linear-gradient(to bottom,rgba(7,12,20,.92) 0%,transparent 100%);
  transition:opacity .3s;pointer-events:none}
#topbar.hidden{opacity:0}
#t-name{font-size:15px;font-weight:800;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.badge{font-size:10px;font-weight:800;letter-spacing:.9px;text-transform:uppercase;
  background:linear-gradient(135deg,var(--c1),var(--c3));
  color:#fff;padding:2px 9px;border-radius:20px}
#tog{margin-left:auto;width:34px;height:34px;border-radius:50%;
  background:rgba(255,255,255,.07);border:1px solid var(--border);
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;pointer-events:all;transition:background .2s}
#tog:hover{background:rgba(255,255,255,.14)}
#tog svg{width:15px;height:15px;stroke:var(--text2);fill:none;stroke-width:2.2}

/* ── bottom panel ────────────────────────────────────── */
#panel{position:fixed;bottom:0;left:0;right:0;z-index:9999;isolation:isolate;
  padding:16px 14px calc(14px + env(safe-area-inset-bottom,0px));
  background:var(--glass);
  backdrop-filter:blur(28px) saturate(1.6);
  -webkit-backdrop-filter:blur(28px) saturate(1.6);
  border-top:1px solid var(--border);
  display:flex;flex-direction:column;gap:11px;
  transition:transform .36s cubic-bezier(.4,0,.2,1),opacity .28s}
#panel.hidden{transform:translateY(110%);opacity:0;pointer-events:none}

/* ── primary AR button ───────────────────────────────── */
#btn-ar{width:100%;padding:15px 18px;border:none;border-radius:var(--r);
  font-size:16px;font-weight:800;letter-spacing:.25px;color:#fff;cursor:pointer;
  background:linear-gradient(135deg,var(--c1) 0%,var(--c2) 55%,var(--c3) 100%);
  box-shadow:0 5px 28px rgba(242,141,82,.38),0 1px 0 rgba(255,255,255,.12) inset;
  display:flex;align-items:center;justify-content:center;gap:10px;
  position:relative;overflow:hidden;transition:transform .15s,box-shadow .15s}
#btn-ar::after{content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,.17),transparent);
  opacity:0;transition:opacity .2s}
#btn-ar:hover::after{opacity:1}
#btn-ar:active{transform:scale(.975)}
#btn-ar svg{width:22px;height:22px;flex-shrink:0;fill:none;stroke:currentColor;stroke-width:2}
#btn-ar .pulse{position:absolute;inset:-3px;border-radius:calc(var(--r) + 3px);
  border:2px solid rgba(242,141,82,.6);opacity:0;
  animation:pulse 2.6s ease-out infinite}
@keyframes pulse{0%{transform:scale(1);opacity:.6}75%{transform:scale(1.05);opacity:0}100%{opacity:0}}

/* ── 4-button grid ───────────────────────────────────── */
.sgrid{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}
.sbtn{padding:11px 6px 10px;border:1px solid var(--border);border-radius:var(--rs);
  background:rgba(255,255,255,.05);color:var(--text);
  font-size:11.5px;font-weight:700;cursor:pointer;
  display:flex;flex-direction:column;align-items:center;gap:5px;
  transition:background .2s,transform .15s;white-space:nowrap}
.sbtn:hover{background:rgba(255,255,255,.10)}
.sbtn:active{transform:scale(.95)}
.sbtn svg{width:19px;height:19px;fill:none;stroke:var(--c1);stroke-width:2}
.sbtn span{color:var(--text2);font-size:10.5px}

/* ── toast ───────────────────────────────────────────── */
#toast{position:fixed;top:62px;left:50%;transform:translateX(-50%);
  background:var(--glass2);border:1px solid var(--border);
  border-radius:24px;padding:7px 18px;font-size:12.5px;color:var(--text2);
  z-index:10000;white-space:nowrap;opacity:0;transition:opacity .3s;pointer-events:none}
#toast.show{opacity:1}

/* ── QR modal ────────────────────────────────────────── */
#qrbd{position:fixed;inset:0;z-index:10001;background:rgba(0,0,0,.72);
  backdrop-filter:blur(8px);display:flex;align-items:center;justify-content:center;
  opacity:0;pointer-events:none;transition:opacity .25s}
#qrbd.show{opacity:1;pointer-events:all}
#qrm{background:var(--glass2);border:1px solid var(--border);
  border-radius:var(--r);padding:26px 22px 20px;
  display:flex;flex-direction:column;align-items:center;gap:14px;
  max-width:300px;width:88%;
  transform:scale(.9) translateY(16px);
  transition:transform .3s cubic-bezier(.34,1.56,.64,1)}
#qrbd.show #qrm{transform:scale(1) translateY(0)}
#qrm h3{font-size:16px;font-weight:800;color:var(--text)}
#qr-wrap{background:#fff;border-radius:10px;padding:10px;display:flex}
#qrm p{font-size:11px;color:var(--text3);text-align:center;word-break:break-all;line-height:1.55}
#qr-close{width:100%;padding:11px;border:none;border-radius:var(--rs);
  background:linear-gradient(135deg,var(--c1),var(--c2));
  color:#fff;font-size:14px;font-weight:700;cursor:pointer;transition:opacity .2s}
#qr-close:hover{opacity:.85}

/* ── capture flash ───────────────────────────────────── */
#flash{position:fixed;inset:0;z-index:70;background:#fff;
  opacity:0;pointer-events:none;transition:opacity .08s}

/* ── brand watermark ─────────────────────────────────── */
#brand-badge{position:fixed;bottom:calc(env(safe-area-inset-bottom,0px) + 8px);right:12px;
  z-index:20000;display:flex;align-items:center;gap:6px;
  background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.10);
  border-radius:20px;padding:4px 10px 4px 8px;
  backdrop-filter:blur(10px);pointer-events:none;
  opacity:%%BRAND_OPACITY%%;transition:opacity .3s}
#brand-badge .b-dot{width:6px;height:6px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,var(--c1),var(--c3))}
#brand-badge .b-studio{font-size:10px;font-weight:700;letter-spacing:.5px;
  color:rgba(242,242,242,.80);white-space:nowrap}
#brand-badge .b-powered{font-size:10px;font-family:'Dancing Script',cursive;font-weight:700;
  background:linear-gradient(135deg,var(--c1),var(--c2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  white-space:nowrap}
</style>
</head>
<body>

<div id="loader">
  <div class="ring"></div>
  <div id="l-title">The Aura Standard</div>
  <div id="l-sub">Loading model&hellip;</div>
</div>

<model-viewer id="mv"
  src="%%GLB_SRC%%"
  ar ar-modes="webxr scene-viewer quick-look"
  camera-controls touch-action="pan-y"
  auto-rotate auto-rotate-delay="800" rotation-per-second="15deg"
  shadow-intensity="1.2" shadow-softness="0.8"
  environment-image="neutral" exposure="1"
  bounds="tight" interpolation-decay="200">
</model-viewer>

<div id="topbar">
  <span id="t-name">%%SCENE%%</span>
  <span class="badge">AR</span>
  <button id="tog" title="Toggle panel" onclick="togglePanel()">
    <svg viewBox="0 0 24 24"><polyline id="tog-pts" points="18 15 12 9 6 15"/></svg>
  </button>
</div>

<div id="toast"></div>
<div id="flash"></div>

<!-- brand watermark — always present, hides during active AR session -->
<div id="brand-badge">
  <div class="b-dot"></div>
  <span class="b-studio">%%BRAND%%</span>
  <span class="b-powered">via The Aura Standard</span>
</div>

<div id="panel">
  <button id="btn-ar" onclick="launchAR()">
    <div class="pulse"></div>
    <svg viewBox="0 0 24 24">
      <path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/>
      <circle cx="12" cy="12" r="3.5"/>
    </svg>
    View in Space
  </button>
  <div class="sgrid">
    <button class="sbtn" onclick="capturePhoto()">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="13" r="4"/>
        <path d="M9 3H5a2 2 0 00-2 2v12a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2h-4"/>
        <polyline points="9 3 9 7 15 7 15 3"/></svg>
      <span>Capture</span>
    </button>
    <button class="sbtn" onclick="downloadModel()">
      <svg viewBox="0 0 24 24">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/></svg>
      <span>Get the Model</span>
    </button>
    <button class="sbtn" onclick="toggleFS()">
      <svg viewBox="0 0 24 24" id="fs-svg">
        <path d="M8 3H5a2 2 0 00-2 2v3M21 8V5a2 2 0 00-2-2h-3M16 21h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"/>
      </svg>
      <span id="fs-lbl">Full Screen</span>
    </button>
    <button class="sbtn" onclick="shareLink()">
      <svg viewBox="0 0 24 24">
        <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
        <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>
        <line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      <span>Share</span>
    </button>
  </div>
</div>

<div id="qrbd" onclick="hideQR()">
  <div id="qrm" onclick="event.stopPropagation()">
    <h3>&#128242; Scan on Mobile</h3>
    <div id="qr-wrap"><div id="qrcode"></div></div>
    <p id="qr-url">%%LAN_URL%%</p>
    <button id="qr-copy" onclick="copyQrUrl()" style="width:100%;padding:8px;margin-bottom:6px;border:1px solid var(--border);border-radius:var(--rs);background:rgba(255,255,255,.08);color:var(--text2);font-size:12px;cursor:pointer;">Copy Link</button>
    <button id="qr-close" onclick="hideQR()">Close</button>
  </div>
</div>

<script>
var LAN_URL    = '%%LAN_URL%%';
var GLB_DL     = '%%GLB_DL%%';
var SESSION_ID = '%%SESSION%%';
var mv = document.getElementById('mv');
var _panelOn = true;
var _modelLoaded = false;
var _arPending = false;
// True on any touch device or narrow screen (phones, tablets, Huawei, etc.)
var _isMobile = (navigator.maxTouchPoints > 0 || window.innerWidth < 1024);

/* ── loader ─────────────────────────────────── */
mv.addEventListener('load', function() {
  _modelLoaded = true;
  var l = document.getElementById('loader');
  l.classList.add('out');
  setTimeout(function(){ l.style.display='none'; }, 700);
  // If user already tapped AR while loading, fire it now
  if (_arPending) { _arPending = false; _doAR(); }
});
setTimeout(function(){
  _modelLoaded = true;
  var l = document.getElementById('loader');
  if (l && l.style.display !== 'none') {
    l.classList.add('out');
    setTimeout(function(){ l.style.display='none'; }, 700);
  }
  if (_arPending) { _arPending = false; _doAR(); }
}, 9000);

/* ── AR launch ──────────────────────────────── */
function _doAR() {
  if (_isMobile) {
    // On ANY mobile/tablet: always try to fire AR directly.
    // activateAR() works for Android Scene Viewer, iOS Quick Look, WebXR.
    // ar-status:failed will fire if the device can't do AR at all.
    try { mv.activateAR(); } catch(e) {
      toast('Open in Android Chrome or iOS Safari for AR', 6000);
    }
  } else {
    // Desktop: show QR code — NEVER on mobile
    showQR();
    toast('Scan with your phone or tablet to launch AR', 5000);
  }
}
function launchAR() {
  if (!_modelLoaded) {
    _arPending = true;
    toast('Loading model\\u2026 AR will launch automatically', 4000);
    return;
  }
  _doAR();
}

/* ── toast ──────────────────────────────────── */
var _tt;
function toast(msg, dur) {
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(_tt);
  _tt = setTimeout(function(){ t.classList.remove('show'); }, dur || 3000);
}

/* ── panel toggle ───────────────────────────── */
function togglePanel() {
  _panelOn = !_panelOn;
  document.getElementById('panel').classList.toggle('hidden', !_panelOn);
  document.getElementById('tog-pts').setAttribute('points',
    _panelOn ? '18 15 12 9 6 15' : '6 9 12 15 18 9');
}

mv.addEventListener('ar-status', function(e) {
  if (e.detail.status === 'session-started') {
    document.getElementById('panel').classList.add('hidden');
    document.getElementById('topbar').classList.add('hidden');
    document.getElementById('brand-badge').style.opacity = '0';
  }
  if (e.detail.status === 'not-presenting') {
    if (_panelOn) document.getElementById('panel').classList.remove('hidden');
    document.getElementById('topbar').classList.remove('hidden');
    document.getElementById('brand-badge').style.opacity = '%%BRAND_OPACITY%%';
  }
  if (e.detail.status === 'failed') {
    if (_isMobile) {
      toast('AR not available on this browser \\u2014 try Chrome (Android) or Safari (iOS)', 6000);
    } else {
      showQR();
      toast('Scan with your phone to launch AR', 5000);
    }
  }
});

/* ── capture ────────────────────────────────── */
function capturePhoto() {
  var fl = document.getElementById('flash');
  fl.style.opacity = '1';
  setTimeout(function(){ fl.style.opacity = '0'; }, 80);
  var url = mv.toDataURL('image/png');
  var a = document.createElement('a');
  a.href = url;
  a.download = 'aura-ar-' + SESSION_ID.slice(0,8) + '.png';
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  toast('Photo saved!');
}

/* ── download GLB ───────────────────────────── */
function downloadModel() {
  var a = document.createElement('a');
  a.href = GLB_DL; a.download = GLB_DL;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  toast('Download started\\u2026');
}

/* ── fullscreen ─────────────────────────────── */
function toggleFS() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(function(){
      toast('Fullscreen blocked by browser');
    });
  } else { document.exitFullscreen(); }
}
document.addEventListener('fullscreenchange', function() {
  document.getElementById('fs-lbl').textContent =
    document.fullscreenElement ? 'Exit Full' : 'Full Screen';
});

/* ── share ──────────────────────────────────── */
function shareLink() {
  if (navigator.share) {
    navigator.share({ title: '%%SCENE%% \\u2014 The Aura Standard',
      text: 'View my 3D model in AR!', url: LAN_URL }).catch(function(){});
  } else if (navigator.clipboard) {
    navigator.clipboard.writeText(LAN_URL)
      .then(function(){ toast('Link copied!'); });
  } else {
    // Last resort: select the URL text for manual copy
    prompt('Copy this AR link:', LAN_URL);
  }
}

/* ── QR ─────────────────────────────────────── */
var _qrDone = false;
function showQR() {
  document.getElementById('qrbd').classList.add('show');
  if (!_qrDone) {
    new QRCode(document.getElementById('qrcode'), {
      text: LAN_URL, width: 200, height: 200,
      colorDark: '#000', colorLight: '#fff',
      correctLevel: QRCode.CorrectLevel.M
    });
    _qrDone = true;
  }
}
function hideQR() {
  document.getElementById('qrbd').classList.remove('show');
}
function copyQrUrl() {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(LAN_URL).then(function(){ toast('Link copied!'); });
  } else { prompt('Copy this link:', LAN_URL); }
}

/* ── keyboard ───────────────────────────────── */
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') hideQR();
  if (e.key === 'f' || e.key === 'F') toggleFS();
  if (e.key === ' ') togglePanel();
});
</script>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# Addon detection — reads bpy.context.preferences at call time
# ─────────────────────────────────────────────────────────────────────────────

def _detect_addons():
    """Return a dict of known paid/power addons that The Aura Standard can integrate with."""
    installed = set(bpy.context.preferences.addons.keys())
    return {
        "rigify":          "rigify"          in installed,
        "auto_rig_pro":    any(k.startswith(("auto_rig_pro", "arp_"))          for k in installed),
        "decal_machine":   any(k.startswith(("DECALmachine", "decal_machine")) for k in installed),
        "hard_ops":        any(k.startswith(("HOps", "hardops", "hard_ops"))   for k in installed),
        "boxcutter":       "boxcutter"       in installed,
        "botaniq":         any(k.startswith("botaniq")                         for k in installed),
        "retopoflow":      any(k.startswith("retopoflow")                      for k in installed),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Architecture preset operator
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_architecture_preset(bpy.types.Operator):
    """Apply Architecture mode: 500 k poly target, DRACO on, instancing on, High textures"""
    bl_idname  = "webxr.architecture_preset"
    bl_label   = "Apply Architecture Preset"
    bl_options = set()

    def execute(self, context):
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            self.report({"ERROR"}, "The Aura Standard: properties missing.")
            return {"CANCELLED"}
        props.scene_mode            = 'ARCHITECTURE'
        props.ar_poly_target        = 500_000
        props.use_draco_compression = True
        props.use_instance_dedup    = True
        props.texture_quality       = 'HIGH'
        props.use_smart_decimate    = True
        self.report({"INFO"}, "Architecture preset applied: 500 k polys · DRACO · instancing · high textures")
        return {"FINISHED"}


class WEBXR_OT_character_preset(bpy.types.Operator):
    """Apply Character mode: 80 k poly target, high textures, auto-rig enabled"""
    bl_idname  = "webxr.character_preset"
    bl_label   = "Apply Character Preset"
    bl_options = set()

    def execute(self, context):
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            self.report({"ERROR"}, "The Aura Standard: properties missing.")
            return {"CANCELLED"}
        props.scene_mode            = 'CHARACTER'
        props.ar_poly_target        = 80_000
        props.use_draco_compression = False
        props.texture_quality       = 'HIGH'
        props.use_smart_decimate    = True
        props.auto_rig_on_export    = True
        self.report({"INFO"}, "Character preset applied: 80 k polys · high textures · auto-rig")
        return {"FINISHED"}


# ─────────────────────────────────────────────────────────────────────────────
# Auto-Rig operator
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_auto_rig(bpy.types.Operator):
    """Auto-generate an armature for the selected mesh — uses Auto-Rig Pro if installed, else Rigify"""
    bl_idname  = "webxr.auto_rig"
    bl_label   = "Auto-Rig Selected"
    bl_options = set()

    def execute(self, context):
        addons = _detect_addons()
        mesh_objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not mesh_objects:
            self.report({"WARNING"}, "Select at least one mesh object first.")
            return {"CANCELLED"}

        # Check if any mesh is already rigged (has armature modifier)
        already_rigged = [
            o for o in mesh_objects
            if any(m.type == 'ARMATURE' for m in o.modifiers)
        ]
        if already_rigged:
            self.report({"INFO"}, f"{len(already_rigged)} object(s) already have an armature. Skipping those.")

        unrigged = [o for o in mesh_objects if o not in already_rigged]
        if not unrigged:
            self.report({"INFO"}, "All selected meshes are already rigged.")
            return {"FINISHED"}

        # ── Strategy 1: Auto-Rig Pro ──────────────────────────────────
        if addons["auto_rig_pro"]:
            try:
                # ARP's smart function — place at mesh origin
                for obj in unrigged:
                    context.view_layer.objects.active = obj
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.ops.arp.smart_bones_auto()
                self.report({"INFO"}, f"Auto-Rig Pro applied to {len(unrigged)} object(s).")
                return {"FINISHED"}
            except Exception as e:
                self.report({"WARNING"}, f"Auto-Rig Pro call failed: {e}. Trying Rigify…")

        # ── Strategy 2: Rigify ────────────────────────────────────────
        if addons["rigify"]:
            try:
                bpy.ops.object.select_all(action='DESELECT')
                # Add human metarig at scene origin
                bpy.ops.object.armature_human_metarig_add()
                metarig = context.active_object
                # Scale metarig to match the first unrigged mesh bounds
                target = unrigged[0]
                bbox   = [target.matrix_world @ v.co for v in target.data.vertices]
                if bbox:
                    min_z  = min(v.z for v in bbox)
                    max_z  = max(v.z for v in bbox)
                    height = max_z - min_z
                    metarig.location.z = min_z
                    metarig.scale      = (height / 2.0,) * 3
                bpy.ops.pose.rigify_generate()
                self.report({"INFO"}, "Rigify metarig generated. Parent your meshes to the generated rig.")
                return {"FINISHED"}
            except Exception as e:
                self.report({"WARNING"}, f"Rigify failed: {e}. Falling back to simple armature.")

        # ── Strategy 3: Simple bounding-box armature ──────────────────
        for obj in unrigged:
            bbox   = [obj.matrix_world @ v.co for v in obj.data.vertices]
            if not bbox:
                continue
            min_z  = min(v.z for v in bbox)
            max_z  = max(v.z for v in bbox)
            cx     = sum(v.x for v in bbox) / len(bbox)
            cy     = sum(v.y for v in bbox) / len(bbox)
            height = max_z - min_z or 1.0

            arm_data = bpy.data.armatures.new(f"Aura_Armature_{obj.name}")
            arm_obj  = bpy.data.objects.new(f"Aura_Rig_{obj.name}", arm_data)
            context.collection.objects.link(arm_obj)

            context.view_layer.objects.active = arm_obj
            bpy.ops.object.mode_set(mode='EDIT')
            root  = arm_data.edit_bones.new("root")
            root.head = (cx, cy, min_z)
            root.tail = (cx, cy, min_z + height * 0.5)
            spine = arm_data.edit_bones.new("spine")
            spine.head   = (cx, cy, min_z + height * 0.5)
            spine.tail   = (cx, cy, max_z)
            spine.parent = root
            bpy.ops.object.mode_set(mode='OBJECT')

            # Parent mesh to armature with automatic weights
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            arm_obj.select_set(True)
            context.view_layer.objects.active = arm_obj
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')

        self.report({"INFO"}, f"Simple bounding-box armature added to {len(unrigged)} object(s).")
        return {"FINISHED"}


# ─────────────────────────────────────────────────────────────────────────────
# Bake DecalMachine decals operator
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_bake_decals(bpy.types.Operator):
    """Bake all DecalMachine decals into base textures before AR export"""
    bl_idname  = "webxr.bake_decals"
    bl_label   = "Bake DecalMachine Decals"
    bl_options = set()

    def execute(self, context):
        addons = _detect_addons()
        if not addons["decal_machine"]:
            self.report({"WARNING"}, "DecalMachine is not installed or enabled.")
            return {"CANCELLED"}
        try:
            # DecalMachine bake operator
            bpy.ops.machin3.bake_decals('INVOKE_DEFAULT')
            self.report({"INFO"}, "DecalMachine bake started. Wait for it to finish before deploying.")
        except Exception as e:
            self.report({"ERROR"}, f"DecalMachine bake failed: {e}")
            return {"CANCELLED"}
        return {"FINISHED"}


# ─────────────────────────────────────────────────────────────────────────────
# Scan & report installed power addons
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_scan_addons(bpy.types.Operator):
    """Scan for supported third-party addons and show what The Aura Standard can use"""
    bl_idname  = "webxr.scan_addons"
    bl_label   = "Scan Installed Addons"
    bl_options = set()

    def execute(self, context):
        addons = _detect_addons()
        found  = [k for k, v in addons.items() if v]
        miss   = [k for k, v in addons.items() if not v]
        msg = (
            f"Found: {', '.join(found) or 'none'} | "
            f"Not installed: {', '.join(miss)}"
        )
        self.report({"INFO"}, msg)
        return {"FINISHED"}


def _cloud_upload(glb_path, api_key, artist_name=""):
    """
    Upload a GLB file to the Aura cloud server using only stdlib (urllib).
    No external dependencies — safe to call inside Blender.

    Returns:
        (cloud_url: str, None)  on success
        (None, error_msg: str)  on failure
    """
    import json
    import urllib.error
    import urllib.request
    import ssl

    UPLOAD_URL = "https://ceo.aura-intelligence.ch/api/v1/upload"
    boundary   = uuid.uuid4().hex
    filename   = os.path.basename(glb_path)

    with open(glb_path, "rb") as f:
        glb_bytes = f.read()

    # Build multipart/form-data body manually
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        "Content-Type: model/gltf-binary\r\n\r\n"
    ).encode("utf-8") + glb_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        UPLOAD_URL,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Aura-Api-Key": api_key,
            "X-Aura-Artist-Name": artist_name,
        },
        method="POST",
    )

    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("url"), None
    except urllib.error.HTTPError as e:
        # Surface the exact human-readable message from the server JSON
        try:
            detail = json.loads(e.read().decode("utf-8", errors="replace")).get("detail", "")
        except Exception:
            detail = ""
        msg = detail if detail else f"HTTP {e.code}"
        return None, msg
    except Exception as e:
        return None, str(e)


# ─────────────────────────────────────────────────────────────────────────────
# Deployment log — persists last 10 cloud URLs across Blender sessions
# ─────────────────────────────────────────────────────────────────────────────
_LOG_MAX = 10

def _log_path():
    return os.path.join(os.path.expanduser("~"), ".aura_ar_exports", "deploy_log.json")

def _read_log():
    import json
    try:
        with open(_log_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _write_log(entries):
    import json
    try:
        with open(_log_path(), "w", encoding="utf-8") as f:
            json.dump(entries[:_LOG_MAX], f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def _append_log(scene_name, cloud_url, session_id):
    """Prepend a new entry and keep only the last _LOG_MAX."""
    from datetime import datetime
    entries = _read_log()
    entries.insert(0, {
        "ts":      datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
        "scene":   scene_name,
        "url":     cloud_url,
        "session": session_id,
    })
    _write_log(entries)


def _write_viewer(export_dir, glb_bare, scene_name, lan_url, session_id,
                   brand="", show_brand=True):
    """Write the luxury AR viewer. Uses %% placeholders to avoid any escaping."""
    glb_src      = f"{glb_bare}?v={session_id}"
    brand_text   = (brand.strip() or "The Aura Standard") if show_brand else ""
    brand_opacity = "1" if show_brand else "0"
    html = (
        _VIEWER_TEMPLATE
        .replace("%%SCENE%%",          scene_name)
        .replace("%%GLB_SRC%%",        glb_src)
        .replace("%%GLB_DL%%",         glb_bare)
        .replace("%%SESSION%%",        session_id)
        .replace("%%LAN_URL%%",        lan_url)
        .replace("%%BRAND%%",          brand_text or "The Aura Standard")
        .replace("%%BRAND_OPACITY%%",  brand_opacity)
    )
    out_path = os.path.join(export_dir, "ar_viewer.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)


# ─────────────────────────────────────────────────────────────────────────────
# Operator
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_export(Operator):
    bl_idname  = "webxr.export_model"
    bl_label   = "Deploy to AR"
    bl_options = set()  # no REGISTER — prevents redo/repeat re-invocation

    def execute(self, context):
        scene      = context.scene
        scene_name = scene.name or "Scene"
        props      = getattr(scene, "webxr_props", None)

        export_dir    = _export_dir()
        ip            = _lan_ip()
        port          = _SERVER_PORT

        # ── Read user settings (with safe defaults) ──────────────────────────
        fmt             = getattr(props, 'export_format',        'GLB')      if props else 'GLB'
        optimize_mesh   = getattr(props, 'optimize_mesh',        True)       if props else False
        manual_ratio    = getattr(props, 'decimate_ratio',       0.7)        if props else 0.7
        use_smart       = getattr(props, 'use_smart_decimate',   True)       if props else True
        ar_poly_target  = getattr(props, 'ar_poly_target',       100_000)    if props else 100_000
        auto_uv         = getattr(props, 'auto_uv_unwrap',       True)       if props else True
        scene_mode      = getattr(props, 'scene_mode',           'STANDARD') if props else 'STANDARD'
        use_draco       = getattr(props, 'use_draco_compression', False)     if props else False
        draco_level     = getattr(props, 'draco_compression_level', 6)       if props else 6
        use_dedup       = getattr(props, 'use_instance_dedup',   True)       if props else True
        auto_rig        = getattr(props, 'auto_rig_on_export',   False)      if props else False
        show_brand      = getattr(props, 'show_brand_watermark', True)       if props else True
        brand_text      = getattr(props, 'brand_text',           '')         if props else ''
        bake_decals     = getattr(props, 'bake_decals_on_export', False)     if props else False
        apply_hops      = getattr(props, 'apply_hard_ops_mods',  True)       if props else False

        # ── Architecture mode: override poly target + enable DRACO ──────────
        if scene_mode == 'ARCHITECTURE':
            ar_poly_target = max(ar_poly_target, 500_000)
            use_draco      = True
            use_dedup      = True
        elif scene_mode == 'CHARACTER':
            ar_poly_target = min(ar_poly_target, 80_000)

        # FBX is not WebXR-compatible — fall back to GLB silently for local preview
        # but keep the setting so the exported file extension is correct for delivery
        gltf_fmt       = fmt if fmt in ('GLTF', 'GLB') else 'GLB'
        ext            = '.gltf' if gltf_fmt == 'GLTF' else '.glb'

        # ── Context-awareness: detect blend file change → force fresh session
        current_blend = bpy.data.filepath or ""
        if props is not None and props.last_blend_path != current_blend:
            props.last_viewer_url = ""
            props.last_ar_id      = ""
            props.last_model_file = ""

        # ── Unique session ID per deploy — guarantees a fresh filename
        session_id = str(uuid.uuid4())
        file_bare  = f"{scene_name}_{session_id[:8]}{ext}"
        glb_bare   = f"{scene_name}_{session_id[:8]}.glb"   # AR viewer always needs .glb
        file_path  = os.path.join(export_dir, file_bare)
        glb_path   = os.path.join(export_dir, glb_bare)

        # ── Wipe every old GLB/GLTF so nothing from a previous session survives
        for old in os.listdir(export_dir):
            if old.lower().endswith((".glb", ".gltf", ".bin")):
                try:
                    os.remove(os.path.join(export_dir, old))
                except OSError:
                    pass

        # ── Auto UV Unwrap — add UV map to any mesh that lacks one ───────────
        if auto_uv:
            prev_mode = context.mode
            if prev_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            for obj in scene.objects:
                if obj.type != 'MESH' or obj.data.uv_layers:
                    continue
                context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                try:
                    bpy.ops.uv.smart_project(
                        angle_limit=66.0,
                        margin_method='FRACTION',
                        island_margin=0.02,
                        area_weight=0.0,
                        correct_aspect=True,
                        scale_to_bounds=False,
                    )
                except Exception:
                    pass
                finally:
                    bpy.ops.object.mode_set(mode='OBJECT')

        # ── Auto-rig (Character mode) ─────────────────────────────────────────
        if auto_rig and scene_mode == 'CHARACTER':
            unrigged = [
                o for o in scene.objects
                if o.type == 'MESH'
                and not any(m.type == 'ARMATURE' for m in o.modifiers)
                and o.visible_get()
            ]
            if unrigged:
                # Select them and invoke the auto-rig operator
                bpy.ops.object.select_all(action='DESELECT')
                for o in unrigged:
                    o.select_set(True)
                context.view_layer.objects.active = unrigged[0]
                try:
                    bpy.ops.webxr.auto_rig()
                    self.report({"INFO"}, f"Auto-rig applied to {len(unrigged)} mesh(es).")
                except Exception as e:
                    self.report({"WARNING"}, f"Auto-rig skipped: {e}")

        # ── Bake DecalMachine decals ──────────────────────────────────────────
        if bake_decals and _detect_addons()["decal_machine"]:
            try:
                bpy.ops.machin3.bake_decals()
                self.report({"INFO"}, "DecalMachine decals baked.")
            except Exception as e:
                self.report({"WARNING"}, f"DecalMachine bake skipped: {e}")

        # ── Apply Decimate modifier — smart or manual ─────────────────────────
        if optimize_mesh:
            # Count total triangles to decide ratio
            total_tris = sum(
                sum(1 if len(p.vertices) == 3 else 2 for p in obj.data.polygons)
                for obj in scene.objects if obj.type == 'MESH'
            )
            if use_smart and total_tris > 0:
                decimate_ratio = ar_poly_target / total_tris if total_tris > ar_poly_target else 1.0
                decimate_ratio = max(0.05, min(1.0, decimate_ratio))
            else:
                decimate_ratio = manual_ratio

            if decimate_ratio < 1.0:
                for obj in scene.objects:
                    if obj.type != 'MESH':
                        continue
                    existing = obj.modifiers.get('AR_Decimate')
                    if existing is None:
                        mod = obj.modifiers.new(name='AR_Decimate', type='DECIMATE')
                        mod.ratio = decimate_ratio
                    elif abs(existing.ratio - decimate_ratio) > 0.001:
                        existing.ratio = decimate_ratio
            else:
                # Within target — remove any old AR_Decimate modifiers
                for obj in scene.objects:
                    if obj.type != 'MESH':
                        continue
                    existing = obj.modifiers.get('AR_Decimate')
                    if existing:
                        obj.modifiers.remove(existing)

        # ── Export current visible scene (fallback for older Blender builds)
        export_path = file_path
        export_kwargs = dict(
            filepath=export_path,
            export_format=gltf_fmt,
            use_selection=False,
            use_visible=True,
            export_apply=True,
        )
        if use_draco:
            export_kwargs["export_draco_mesh_compression_enable"] = True
            export_kwargs["export_draco_mesh_compression_level"]  = draco_level  # type: ignore[assignment]

        try:
            bpy.ops.export_scene.gltf(**export_kwargs)
        except TypeError:
            # Older Blender: strip keys that aren't supported
            safe = {k: v for k, v in export_kwargs.items()
                    if k in ("filepath", "export_format", "use_selection")}
            bpy.ops.export_scene.gltf(**safe)

        # For GLTF (separate files), Blender writes <name>.gltf — we also need
        # to have a .glb for the in-browser viewer if user chose GLTF delivery.
        # Re-export as GLB for the local viewer in that case.
        if gltf_fmt == 'GLTF':
            glb_kwargs = dict(
                filepath=glb_path,
                export_format='GLB',
                use_selection=False,
                use_visible=True,
                export_apply=True,
            )
            if use_draco:
                glb_kwargs["export_draco_mesh_compression_enable"] = True
                glb_kwargs["export_draco_mesh_compression_level"]  = draco_level  # type: ignore[assignment]
            try:
                bpy.ops.export_scene.gltf(**glb_kwargs)
            except TypeError:
                safe = {k: v for k, v in glb_kwargs.items()
                        if k in ("filepath", "export_format", "use_selection")}
                bpy.ops.export_scene.gltf(**safe)
        else:
            glb_path = file_path   # GLB export already is the viewer file
            glb_bare = file_bare

        if not os.path.isfile(glb_path):
            self.report({"ERROR"}, "The Aura Standard: GLB export failed — no file was written.")
            return {"CANCELLED"}

        lan_url   = f"http://{ip}:{port}/ar_viewer.html?sid={session_id}"
        local_url = f"http://127.0.0.1:{port}/ar_viewer.html?sid={session_id}"

        # ── Resolve brand label (brand_text → artist_name → "The Aura Standard") ──────
        addon_prefs = context.preferences.addons.get("aura_ar")
        _artist_name = addon_prefs.preferences.artist_name.strip() if addon_prefs else ""
        resolved_brand = brand_text.strip() or _artist_name or "The Aura Standard"

        _write_viewer(export_dir, glb_bare, scene_name, lan_url, session_id,
                      brand=resolved_brand, show_brand=show_brand)
        _start_server(export_dir, port)

        # ── Persist state so sidebar panel can display it
        if props is not None:
            props.last_ar_id       = session_id
            props.last_model_file  = glb_bare
            props.last_viewer_url  = local_url
            props.mobile_ar_url    = lan_url
            props.last_export_path = export_dir
            props.last_blend_path  = current_blend

        import time
        global _last_deploy_time
        now = time.time()
        if now - _last_deploy_time > 3.0:  # only open browser once per 3 s
            webbrowser.open(local_url)
            _last_deploy_time = now
        self.report({"INFO"}, f"The Aura Standard: session {session_id[:8]} deployed  [{gltf_fmt}  poly≤{ar_poly_target:,}]")

        # ── Cloud upload (only if an API key is set in Addon Preferences) ──
        addon_prefs = context.preferences.addons.get("aura_ar")
        if addon_prefs:
            api_key     = addon_prefs.preferences.aura_api_key.strip()
            artist_name = addon_prefs.preferences.artist_name.strip()
            if api_key:
                self.report({"INFO"}, "The Aura Standard: uploading to cloud…")
                cloud_url, err = _cloud_upload(glb_path, api_key, artist_name)
                if cloud_url:
                    if props is not None:
                        props.cloud_ar_url = cloud_url
                    _append_log(scene_name, cloud_url, session_id)
                    webbrowser.open(cloud_url)
                    self.report({"INFO"}, f"The Aura Standard: live at {cloud_url}")
                else:
                    self.report({"WARNING"}, f"The Aura Standard: cloud upload failed — {err}")

        return {"FINISHED"}


class WEBXR_OT_copy_cloud_url(bpy.types.Operator):
    """Copy the live URL to the clipboard"""
    bl_idname  = "webxr.copy_cloud_url"
    bl_label   = "Copy Cloud Link"
    bl_options = set()

    def execute(self, context):
        props = getattr(context.scene, "webxr_props", None)
        url   = getattr(props, "cloud_ar_url", "") if props else ""
        if url:
            context.window_manager.clipboard = url
            self.report({"INFO"}, f"Copied: {url}")
        else:
            self.report({"WARNING"}, "No cloud URL yet — deploy first.")
        return {"FINISHED"}


class WEBXR_OT_copy_log_url(bpy.types.Operator):
    """Copy a deployment log URL to the clipboard"""
    bl_idname  = "webxr.copy_log_url"
    bl_label   = "Copy Log URL"
    bl_options = set()

    log_url: bpy.props.StringProperty(default="")  # type: ignore[assignment]

    def execute(self, context):
        if self.log_url:
            context.window_manager.clipboard = self.log_url
            self.report({"INFO"}, f"Copied: {self.log_url}")
        return {"FINISHED"}


class WEBXR_OT_open_log_url(bpy.types.Operator):
    """Open a deployment log URL in the browser"""
    bl_idname  = "webxr.open_log_url"
    bl_label   = "Open Log URL"
    bl_options = set()

    log_url: bpy.props.StringProperty(default="")  # type: ignore[assignment]

    def execute(self, context):
        if self.log_url:
            import webbrowser
            webbrowser.open(self.log_url)
        return {"FINISHED"}
