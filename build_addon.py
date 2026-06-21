"""
build_addon.py — Packages aura_ar into a Blender-installable zip.
Usage:  python build_addon.py
Output: aura_ar.zip  (in this folder, ready to install via Blender > Preferences > Add-ons)
"""

import os
import glob
import shutil
import zipfile

# ── Config ────────────────────────────────────────────────────────────────────
ADDON_NAME   = "aura_ar"
ADDON_DIR    = os.path.join(os.path.dirname(__file__), ADDON_NAME)
PARENT_DIR   = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# Output one level up — into Own_Blender-Addons alongside other addon zips
OUTPUT_ZIP   = os.path.join(PARENT_DIR, "aura_technologies_ar.zip")

# Files / folders to skip (dev/docs only — not needed at runtime)
EXCLUDE_EXTS = {".md", ".txt"}
EXCLUDE_FILES = {"requirements.txt"}
EXCLUDE_DIRS  = {"__pycache__", ".git", ".vscode"}
# ─────────────────────────────────────────────────────────────────────────────


def should_include(rel_path: str) -> bool:
    parts = rel_path.replace("\\", "/").split("/")
    # Skip excluded dirs anywhere in the path
    if any(p in EXCLUDE_DIRS for p in parts):
        return False
    filename = parts[-1]
    if filename in EXCLUDE_FILES:
        return False
    _, ext = os.path.splitext(filename)
    if ext.lower() in EXCLUDE_EXTS:
        return False
    return True


def build():
    if not os.path.isdir(ADDON_DIR):
        raise FileNotFoundError(f"Addon folder not found: {ADDON_DIR}")

    # ── Remove every old aura_*.zip from BOTH the repo folder and the parent
    #    folder so you can never accidentally install a stale version.
    removed = []
    for search_dir in [os.path.dirname(__file__), PARENT_DIR]:
        for old_zip in glob.glob(os.path.join(search_dir, "aura*.zip")):
            if os.path.abspath(old_zip) != os.path.abspath(OUTPUT_ZIP):
                os.remove(old_zip)
                removed.append(os.path.basename(old_zip))
    # Also remove the output zip itself if it already exists (fresh rebuild)
    if os.path.exists(OUTPUT_ZIP):
        os.remove(OUTPUT_ZIP)
        removed.append(os.path.basename(OUTPUT_ZIP) + " (previous build)")
    if removed:
        print("Removed old zips:")
        for r in removed:
            print(f"  - {r}")

    included = []
    with zipfile.ZipFile(OUTPUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(ADDON_DIR):
            # Prune excluded dirs in-place so os.walk skips them
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for filename in files:
                abs_path = os.path.join(root, filename)
                # Arc path keeps the top-level folder name so Blender installs correctly:
                # aura_ar/__init__.py, aura_ar/operators/export.py …
                arc_path = os.path.relpath(abs_path, os.path.dirname(ADDON_DIR))
                arc_path = arc_path.replace("\\", "/")

                if should_include(arc_path):
                    zf.write(abs_path, arc_path)
                    included.append(arc_path)

    print(f"Built {OUTPUT_ZIP}")
    print(f"  {len(included)} files included:")
    for p in sorted(included):
        print(f"    {p}")

    # ── Wipe the addon from every installed Blender version so the next
    #    reinstall always starts from a clean slate (no stale __pycache__ etc.)
    roaming = os.path.expandvars(r"%APPDATA%\Blender Foundation\Blender")
    wiped = []
    if os.path.isdir(roaming):
        for ver in os.listdir(roaming):
            installed = os.path.join(roaming, ver, "scripts", "addons", ADDON_NAME)
            if os.path.isdir(installed):
                shutil.rmtree(installed)
                wiped.append(installed)
    if wiped:
        print("Uninstalled from Blender:")
        for w in wiped:
            print(f"  - {w}")
        print("  -> Restart Blender, then install the new zip.")
    else:
        print("No installed Blender copy found — just install the zip.")


if __name__ == "__main__":
    build()
