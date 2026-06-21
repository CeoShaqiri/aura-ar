"""
WebXR Deployment & Sharing System
Generates QR codes, metadata, viewer links, and client delivery packages.
"""

import json
import os
import socket
import subprocess
import sys
import uuid
import webbrowser
import zipfile
from datetime import datetime


class ARDeploymentManager:
    """Manages AR deployment and sharing."""

    @staticmethod
    def generate_ar_id():
        """Generate unique AR experience ID."""
        return str(uuid.uuid4())[:8]

    @staticmethod
    def generate_qr_code(export_path, model_data, web_url_override=None):
        """Generate QR code for AR model sharing."""
        try:
            import qrcode as _qrcode
        except ImportError:
            raise RuntimeError("qrcode package not installed in Blender's Python.")
        ar_id = ARDeploymentManager.generate_ar_id()
        web_url = web_url_override or f"https://ar.example.com/viewer/{ar_id}"

        qr = _qrcode.QRCode(
            version=1,
            error_correction=_qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(web_url)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_filename = f"ar_{ar_id}_qr.png"
        qr_path = os.path.join(export_path, qr_filename)
        qr_image.save(qr_path)

        return {
            "qr_path": qr_path,
            "qr_image": qr_filename,
            "ar_id": ar_id,
            "web_url": web_url,
        }

    @staticmethod
    def create_ar_metadata(model_info, export_path):
        """Create metadata file for AR model."""
        metadata = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "model": {
                "name": model_info.get("name", "Model"),
                "file": model_info.get("filename"),
                "format": model_info.get("format"),
                "quality": model_info.get("quality"),
                "vertex_count": model_info.get("vertex_count"),
            },
            "ar": {
                "type": "webxr",
                "compatible_devices": ["Android", "iOS", "Desktop"],
                "required_features": ["hit-test", "dom-overlay"],
            },
            "sharing": {
                "ar_id": model_info.get("ar_id"),
                "web_url": model_info.get("web_url"),
                "qr_code": model_info.get("qr_image"),
            },
        }

        metadata_path = os.path.join(export_path, f"ar_metadata_{model_info['ar_id']}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return metadata_path

    @staticmethod
    def create_deployment_info(model_data, export_dir):
        """Create deployment info file for users."""
        ar_id = model_data["ar_id"]
        info = f"""
AR MODEL DEPLOYMENT INFORMATION
===============================

Model: {model_data['name']}
File: {model_data['filename']}
Quality: {model_data['quality']}%
Vertices: {model_data['vertex_count']:,}

Web URL:
{model_data['web_url']}

QR Code:
{model_data['qr_image']}

Technical:
- AR ID: {ar_id}
- Format: {model_data.get('format', 'GLB')}
- File Size: {model_data.get('file_size', 'N/A')} MB
"""

        info_path = os.path.join(export_dir, f"AR_DEPLOYMENT_{ar_id}.txt")
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(info)

        return info_path

    @staticmethod
    def _find_open_port(start_port=8765, attempts=25):
        """Find an available localhost port for the local AR viewer server."""
        for offset in range(attempts):
            port = start_port + offset
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        return None

    @staticmethod
    def _get_local_ip():
        """Best-effort LAN IP lookup for mobile device access."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
        except OSError:
            return "127.0.0.1"
        finally:
            sock.close()

    @staticmethod
    def create_local_viewer(export_dir, model_filename, model_name="AR Model"):
        """Create a local HTML AR viewer bound to the exported model file."""
        viewer_filename = "ar_live_viewer.html"
        viewer_path = os.path.join(export_dir, viewer_filename)

        html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{model_name} - The Aura Standard Live Viewer</title>
  <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; }}
    body {{ font-family: Segoe UI, sans-serif; background: #0f172a; color: #e2e8f0; }}
    header {{ padding: 12px 16px; display: flex; justify-content: space-between; gap: 10px; align-items: center; background: #111827; }}
    .actions {{ display: flex; gap: 8px; flex-wrap: wrap; }}
    button, a {{ border: 1px solid #334155; background: #1f2937; color: #e2e8f0; border-radius: 8px; padding: 8px 12px; text-decoration: none; cursor: pointer; }}
    button.primary {{ background: #22c55e; color: #052e16; border-color: #14532d; font-weight: 700; }}
    model-viewer {{ width: 100%; height: calc(100% - 56px); }}
  </style>
</head>
<body>
  <header>
    <div>The Aura Standard Live Viewer - {model_filename}</div>
    <div class="actions">
      <button class="primary" id="arBtn">Launch AR</button>
      <a href="{model_filename}" download>Download GLB</a>
      <button id="copyBtn">Copy URL</button>
    </div>
  </header>
  <model-viewer id="viewer" src="{model_filename}" alt="{model_name}" camera-controls auto-rotate ar ar-modes="webxr scene-viewer quick-look" ar-scale="auto"></model-viewer>
  <script>
    const viewer = document.getElementById('viewer');
    document.getElementById('arBtn').addEventListener('click', () => viewer.activateAR());
    document.getElementById('copyBtn').addEventListener('click', async () => {{
      try {{
        await navigator.clipboard.writeText(window.location.href);
        alert('Viewer URL copied to clipboard.');
      }} catch (e) {{
        alert('Copy failed. URL: ' + window.location.href);
      }}
    }});
  </script>
</body>
</html>
""".format(model_name=model_name, model_filename=model_filename)

        with open(viewer_path, "w", encoding="utf-8") as f:
            f.write(html)

        return viewer_path

    @staticmethod
    def launch_local_viewer(export_dir, viewer_filename="ar_live_viewer.html"):
        """Start a local server for the export directory and return localhost/LAN URLs."""
        port = ARDeploymentManager._find_open_port()
        if not port:
            raise RuntimeError("No free localhost port found for AR viewer")

        local_ip = ARDeploymentManager._get_local_ip()

        cmd = [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--directory",
            export_dir,
        ]

        creationflags = 0
        startupinfo = None
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            startupinfo=startupinfo,
        )

        localhost_url = f"http://127.0.0.1:{port}/{viewer_filename}"
        lan_url = f"http://{local_ip}:{port}/{viewer_filename}"
        webbrowser.open(localhost_url)

        return {
            "localhost_url": localhost_url,
            "lan_url": lan_url,
            "port": port,
            "ip": local_ip,
        }

    @staticmethod
    def _history_path(export_dir):
        return os.path.join(export_dir, "ar_export_history.json")

    @staticmethod
    def append_export_history(export_dir, entry):
        """Append deployment entry to export history file."""
        path = ARDeploymentManager._history_path(export_dir)
        history = []
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []

        history.insert(0, entry)
        history = history[:50]

        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        return path

    @staticmethod
    def create_client_package(export_dir, model_data):
        """Create a premium client-ready ZIP package for delivery."""
        ar_id = model_data.get("ar_id", "bundle")
        package_path = os.path.join(export_dir, f"AR_CLIENT_PACKAGE_{ar_id}.zip")

        files = [
            model_data.get("filename", ""),
            model_data.get("qr_image", ""),
            f"ar_metadata_{ar_id}.json",
            f"AR_DEPLOYMENT_{ar_id}.txt",
            "ar_live_viewer.html",
        ]

        with zipfile.ZipFile(package_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel in files:
                if not rel:
                    continue
                full = os.path.join(export_dir, rel)
                if os.path.exists(full):
                    zf.write(full, arcname=rel)

        return package_path
