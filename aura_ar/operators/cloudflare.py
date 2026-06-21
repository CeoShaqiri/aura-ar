"""
The Aura Standard — Cloudflare Tunnel Operator
Runs `cloudflared tunnel --url http://localhost:PORT` to generate a public
HTTPS URL that anyone worldwide can scan/open — no same-WiFi requirement.
cloudflared binary is auto-downloaded to the addon's data folder on first use.
"""

import bpy
import os
import sys
import re
import threading
import urllib.request
import subprocess
import platform

# Global process handle so we can stop the tunnel later
_tunnel_proc = None
_tunnel_url  = ""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cf_dir():
    """Persistent folder for the cloudflared binary (next to this file)."""
    d = os.path.join(os.path.dirname(__file__), "_cloudflared")
    os.makedirs(d, exist_ok=True)
    return d


def _cf_binary():
    """Return the path where cloudflared should live (downloaded if needed)."""
    d = _cf_dir()
    name = "cloudflared.exe" if sys.platform == "win32" else "cloudflared"
    return os.path.join(d, name)


def _cf_download_url():
    """Return the correct cloudflared release URL for this OS/arch."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
    elif system == "darwin":
        if "arm" in machine:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-arm64.tgz"
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64.tgz"
    else:
        if "arm" in machine or "aarch" in machine:
            return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"
        return "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"


def _ensure_cloudflared():
    """Download cloudflared if not present. Returns binary path or raises."""
    binary = _cf_binary()
    if os.path.isfile(binary):
        return binary

    url = _cf_download_url()
    dest = binary

    # For macOS tgz we download to a temp file first
    if url.endswith(".tgz"):
        import tempfile, tarfile
        tmp = dest + ".tgz"
        urllib.request.urlretrieve(url, tmp)
        with tarfile.open(tmp, "r:gz") as tar:
            member = next(m for m in tar.getmembers() if "cloudflared" in m.name and not m.isdir())
            with tar.extractfile(member) as src, open(dest, "wb") as out:
                out.write(src.read())
        os.remove(tmp)
    else:
        urllib.request.urlretrieve(url, dest)

    if sys.platform != "win32":
        os.chmod(dest, 0o755)

    return dest


# ---------------------------------------------------------------------------
# Tunnel start operator
# ---------------------------------------------------------------------------

class WEBXR_OT_start_tunnel(bpy.types.Operator):
    """Create a free public HTTPS URL via Cloudflare Tunnel so anyone can view
    the AR experience — no same-WiFi required."""
    bl_idname  = "webxr.start_tunnel"
    bl_label   = "Get Public AR Link"
    bl_description = (
        "Start a Cloudflare Tunnel to get a worldwide-accessible HTTPS URL.\n"
        "Share it via WhatsApp, Telegram, or any messenger — friend opens on phone → AR."
    )
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _tunnel_proc, _tunnel_url

        props = getattr(context.scene, "webxr_props", None)
        if props is None or not props.last_viewer_url:
            self.report({"ERROR"},
                "No viewer running — click 'Deploy to AR' first.")
            return {"CANCELLED"}

        # Extract port from stored local URL (http://127.0.0.1:PORT/...)
        m = re.search(r":(\d+)/", props.last_viewer_url)
        if not m:
            self.report({"ERROR"}, f"Could not determine port from {props.last_viewer_url}")
            return {"CANCELLED"}
        port = m.group(1)
        local = f"http://127.0.0.1:{port}"

        # Stop any existing tunnel
        if _tunnel_proc and _tunnel_proc.poll() is None:
            _tunnel_proc.terminate()
            _tunnel_url = ""

        # Download binary if needed (happens once, ~5 MB)
        bpy.context.window_manager.progress_begin(0, 100)
        bpy.context.window_manager.progress_update(10)
        self.report({"INFO"}, "Preparing cloudflared (first run downloads ~5 MB)…")
        try:
            binary = _ensure_cloudflared()
        except Exception as exc:
            bpy.context.window_manager.progress_end()
            self.report({"ERROR"}, f"Failed to get cloudflared: {exc}")
            return {"CANCELLED"}
        bpy.context.window_manager.progress_update(40)

        # Launch tunnel process
        try:
            proc = subprocess.Popen(
                [binary, "tunnel", "--url", local],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as exc:
            bpy.context.window_manager.progress_end()
            self.report({"ERROR"}, f"Could not start cloudflared: {exc}")
            return {"CANCELLED"}

        _tunnel_proc = proc
        bpy.context.window_manager.progress_update(60)

        # Read output in a thread, looking for the assigned URL
        found = threading.Event()
        url_holder = [""]

        def _reader():
            url_re = re.compile(r"https://[a-z0-9\-]+\.trycloudflare\.com")
            for line in proc.stdout:
                m = url_re.search(line)
                if m and not found.is_set():
                    url_holder[0] = m.group(0)
                    found.set()

        t = threading.Thread(target=_reader, daemon=True)
        t.start()

        # Block up to 20 s for the URL to appear
        found.wait(timeout=20)
        bpy.context.window_manager.progress_end()

        public_url = url_holder[0]
        if not public_url:
            self.report({"WARNING"},
                "Tunnel started but URL not detected yet. Check Blender console in a moment.")
            return {"FINISHED"}

        _tunnel_url = public_url
        viewer_public = public_url + "/ar_viewer.html"

        # Store in props so the panel and QR can use it
        try:
            props.mobile_ar_url = viewer_public
        except Exception:
            pass

        # Copy to clipboard
        try:
            context.window_manager.clipboard = viewer_public
        except Exception:
            pass

        self.report({"INFO"}, f"🌍 Public AR link: {viewer_public}  ← copied to clipboard")
        self.report({"INFO"}, "Share this link via WhatsApp / Telegram — works worldwide, no WiFi needed.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Tunnel stop operator
# ---------------------------------------------------------------------------

class WEBXR_OT_stop_tunnel(bpy.types.Operator):
    """Stop the active Cloudflare Tunnel."""
    bl_idname  = "webxr.stop_tunnel"
    bl_label   = "Stop Public Link"
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _tunnel_proc, _tunnel_url
        if _tunnel_proc and _tunnel_proc.poll() is None:
            _tunnel_proc.terminate()
            _tunnel_proc = None
        _tunnel_url = ""
        try:
            context.scene.webxr_props.mobile_ar_url = ""
        except Exception:
            pass
        self.report({"INFO"}, "Cloudflare Tunnel stopped.")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Copy public URL operator
# ---------------------------------------------------------------------------

class WEBXR_OT_copy_public_url(bpy.types.Operator):
    """Copy the public Cloudflare AR link to clipboard."""
    bl_idname  = "webxr.copy_public_url"
    bl_label   = "Copy Public Link"
    bl_options = {"REGISTER"}

    def execute(self, context):
        url = getattr(context.scene.webxr_props, "mobile_ar_url", "")
        if not url or "trycloudflare" not in url:
            self.report({"WARNING"}, "No public link active — start tunnel first.")
            return {"CANCELLED"}
        try:
            context.window_manager.clipboard = url
        except Exception:
            pass
        self.report({"INFO"}, f"Copied: {url}")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

_classes = [
    WEBXR_OT_start_tunnel,
    WEBXR_OT_stop_tunnel,
    WEBXR_OT_copy_public_url,
]


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)


def unregister():
    global _tunnel_proc
    if _tunnel_proc and _tunnel_proc.poll() is None:
        _tunnel_proc.terminate()
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
