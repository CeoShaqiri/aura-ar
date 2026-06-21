"""
Aura AR — Cloud API Server
Runs on Hetzner CAX31 (ceo-of-aura.cloud) inside Docker.

Endpoints:
  POST /api/v1/upload        — Verify subscription (DB + n8n), enforce export limit, save GLB
  GET  /view/{model_id}      — Serve luxury AR viewer with the model
  GET  /models/{filename}    — Serve GLB files (path-traversal safe)
  GET  /health               — Health check + DB ping

Multi-user: each API key gets its own private folder keyed by HMAC-SHA256
of the key — the raw key is never stored on disk or in the DB.
"""

import hashlib
import hmac
import os
import re
import uuid
from contextlib import asynccontextmanager

import aiofiles
import httpx
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse

import db

# ─────────────────────────────────────────────────────────────────────────────
# Config — all tuneable via environment variables in docker-compose.yml
# ─────────────────────────────────────────────────────────────────────────────
FILES_DIR        = os.environ.get("FILES_DIR", "/data/models")
N8N_WEBHOOK_URL  = os.environ.get("N8N_WEBHOOK_URL", "")   # e.g. https://aura-intelligence.ch/webhook/verify-key
PUBLIC_DOMAIN    = os.environ.get("PUBLIC_DOMAIN", "ceo.aura-intelligence.ch")
MAX_UPLOAD_BYTES = 150 * 1024 * 1024  # 150 MB — enough for any compressed GLB

# UUID4 pattern — used to validate path parameters and filenames
_UUID_RE     = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$')
_GLB_FILE_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\.glb$')

# Load the viewer HTML template once at startup
_TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "viewer_template.html")
with open(_TEMPLATE_PATH, "r", encoding="utf-8") as _f:
    _VIEWER_TEMPLATE = _f.read()


# ─────────────────────────────────────────────────────────────────────────────
# App lifespan — DB pool open / close
# ─────────────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init_pool()
    yield
    await db.close_pool()


app = FastAPI(
    title="Aura AR API",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan,
)

# Mount OCR verification router (Legacy Grant identity check)
try:
    from ocr_verify import router as _ocr_router
    app.include_router(_ocr_router)
except ImportError:
    pass  # OCR dependencies optional — endpoint simply won't be registered

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _user_folder(api_key: str) -> str:
    """
    Return a private, deterministic folder path for this API key.
    Uses HMAC-SHA256 so the raw key is never written to disk.
    Creates the directory if it does not exist.
    """
    key_hash = hmac.new(b"aura-salt", api_key.encode(), hashlib.sha256).hexdigest()
    folder = os.path.join(FILES_DIR, key_hash)
    os.makedirs(folder, exist_ok=True)
    return folder


async def _verify_subscription(api_key: str) -> tuple:
    """
    Two-step subscription check:

    1. Look up the HMAC-SHA256 hash of the key in our PostgreSQL DB.
       If the user exists and is active, check the export limit and return.

    2. If the user is NOT in the DB yet (first-ever deploy), fall back to n8n
       to validate the legacy key, then provision a new user + subscription row.

    Returns tuple: (status: str, user_name: str, user_id: str | None)
      status one of: "active", "inactive", "error"
    """
    key_hash = db.hash_api_key(api_key)

    # ── 1. DB lookup ──────────────────────────────────────────────────────────
    try:
        user = await db.get_user_by_key_hash(key_hash)
        if user:
            status = user["verified_status"]
            if status == "active":
                return "active", user["full_name"], str(user["id"])
            if status in ("suspended", "expired"):
                return "inactive", "", None
            # 'pending' falls through to n8n re-validation below
    except Exception:
        pass  # DB down — proceed to n8n fallback

    # ── 2. n8n fallback (unknown key / first deploy / pending) ───────────────
    if not N8N_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail="Subscription validation service not configured.")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                N8N_WEBHOOK_URL,
                json={"api_key": api_key},
                headers={"Content-Type": "application/json"},
            )
        if resp.status_code == 200:
            body      = resp.json()
            n8n_status = str(body.get("status", "")).strip().lower()
            user_name  = str(body.get("user_name", "")).strip()
            email      = str(body.get("email",     "")).strip() or f"unknown+{key_hash[:8]}@aura.local"
            tier       = str(body.get("tier",      "pro")).strip().lower()

            if n8n_status == "active":
                # Provision / update user and subscription in DB
                try:
                    upserted = await db.upsert_user(email, user_name, api_key, "active")
                    uid      = str(upserted["id"])
                    await db.upsert_subscription(uid, tier)
                except Exception:
                    uid = None
                return "active", user_name, uid

        return "inactive", "", None
    except Exception:
        return "error", "", None


def _render_viewer(model_id: str, user_name: str = "") -> str:
    """Replace %%PLACEHOLDER%% tokens in the viewer template."""
    glb_src   = f"/models/{model_id}.glb"
    cloud_url = f"https://{PUBLIC_DOMAIN}/view/{model_id}"
    artist    = user_name if user_name else "An Aura Artist"
    return (
        _VIEWER_TEMPLATE
        .replace("%%SCENE%%",   model_id[:8])
        .replace("%%GLB_SRC%%", glb_src)
        .replace("%%GLB_DL%%",  glb_src)
        .replace("%%SESSION%%", model_id)
        .replace("%%LAN_URL%%", cloud_url)
        .replace("%%ARTIST%%",  artist)
    )


def _find_model_path(model_id: str) -> str | None:
    """
    Locate a model GLB anywhere under FILES_DIR (searches all user sub-folders).
    Returns the absolute path if found, None otherwise.
    """
    # Direct path (legacy / flat layout)
    flat = os.path.join(FILES_DIR, f"{model_id}.glb")
    if os.path.isfile(flat):
        return flat
    # Search one level of user sub-folders
    try:
        for entry in os.scandir(FILES_DIR):
            if entry.is_dir():
                candidate = os.path.join(entry.path, f"{model_id}.glb")
                if os.path.isfile(candidate):
                    return candidate
    except OSError:
        pass
    return None

# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/upload", status_code=201)
async def upload_model(
    file: UploadFile = File(...),
    x_aura_api_key: str = Header(..., alias="X-Aura-Api-Key"),
    x_aura_artist_name: str = Header("", alias="X-Aura-Artist-Name"),
    x_aura_scene_name: str  = Header("", alias="X-Aura-Scene-Name"),
    x_aura_draco: str       = Header("false", alias="X-Aura-Draco"),
):
    """
    Accept a GLB from Blender, verify subscription (DB → n8n fallback),
    enforce the monthly export limit, save to disk, record in assets table,
    and return the public viewer URL.
    """
    # 1. Verify subscription (DB-first, n8n fallback)
    subscription, n8n_user_name, user_id = await _verify_subscription(x_aura_api_key)
    user_name  = x_aura_artist_name.strip() or n8n_user_name
    scene_name = x_aura_scene_name.strip() or "Untitled"
    draco_on   = x_aura_draco.strip().lower() in ("1", "true", "yes")

    if subscription == "inactive":
        raise HTTPException(
            status_code=402,
            detail="Subscription Expired. Please visit ceo-of-aura.cloud to renew.",
        )
    if subscription == "error":
        raise HTTPException(
            status_code=503,
            detail="Subscription check temporarily unavailable. Please try again.",
        )

    # 2. Enforce monthly export limit via DB
    if user_id:
        limit_check = await db.check_and_increment_export(user_id)
        if not limit_check["allowed"]:
            raise HTTPException(
                status_code=429,
                detail=limit_check.get("reason", "Export limit reached."),
            )

    # 3. Only accept GLB files
    if not (file.filename or "").lower().endswith(".glb"):
        raise HTTPException(status_code=400, detail="Only .glb files are accepted.")

    # 4. Read with a hard size cap
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 150 MB.")

    # 5. Persist to the user's private folder
    model_id    = str(uuid.uuid4())
    user_folder = _user_folder(x_aura_api_key)
    dest        = os.path.join(user_folder, f"{model_id}.glb")

    async with aiofiles.open(dest, "wb") as f:
        await f.write(content)

    # 6. Store artist name alongside the model for viewer rendering
    meta_path = os.path.join(user_folder, f"{model_id}.name")
    async with aiofiles.open(meta_path, "w", encoding="utf-8") as mf:
        await mf.write(user_name)

    viewer_url = f"https://{PUBLIC_DOMAIN}/view/{model_id}"

    # 7. Record asset in DB (non-fatal — disk file is the source of truth)
    if user_id:
        try:
            await db.insert_asset(
                user_id    = user_id,
                scene_name = scene_name,
                glb_path   = dest,
                viewer_url = viewer_url,
                file_size  = len(content),
                draco_enabled = draco_on,
            )
        except Exception:
            pass  # DB write failure must never block the upload response

    return {"id": model_id, "url": viewer_url, "user_name": user_name}


@app.get("/view/{model_id}", response_class=HTMLResponse)
async def view_model(model_id: str):
    """Serve the luxury WebXR viewer for a specific model."""
    if not _UUID_RE.match(model_id):
        raise HTTPException(status_code=400, detail="Invalid model ID format.")

    glb_path = _find_model_path(model_id)
    if glb_path is None:
        raise HTTPException(status_code=404, detail="Model not found.")

    # Read stored artist name if available
    name_file = glb_path.replace(".glb", ".name")
    user_name = ""
    try:
        with open(name_file, "r", encoding="utf-8") as nf:
            user_name = nf.read().strip()
    except OSError:
        pass

    return HTMLResponse(content=_render_viewer(model_id, user_name))


@app.get("/models/{filename}")
async def serve_model(filename: str):
    """Serve a GLB file by UUID filename. Resolves across all user sub-folders."""
    if not _GLB_FILE_RE.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename.")

    # Extract model_id (strip .glb) and use shared resolver
    model_id = filename[:-4]
    path = _find_model_path(model_id)
    if path is None:
        raise HTTPException(status_code=404, detail="File not found.")

    return FileResponse(
        path,
        media_type="model/gltf-binary",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@app.get("/health")
async def health():
    db_ok = False
    try:
        pool = db._pool_required()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        pass
    return {"status": "ok", "db": "ok" if db_ok else "unavailable"}
