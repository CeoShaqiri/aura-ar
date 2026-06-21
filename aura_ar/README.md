# WebXR AR Exporter for Blender

**Professional AR addon for Blender 4.0+ with dedicated AR Workspace**

A powerful Blender addon that brings AR experiences to your 3D models with a single click. **Now with a dedicated "AR" workspace** just like Animation, Sculpting, and Modeling!

## 🎯 KEY FEATURES

- 🎪 **Dedicated AR Workspace** - New "AR" tab in top menu (Blender 4.0+)
- 🚀 **One-Click AR Export** - Deploy your scenes to WebXR/AR instantly
- 🌐 **Live Browser Viewer** - Auto-opens a local AR viewer on deploy
- 📱 **Mobile AR URL + QR** - Real phone-ready link generated every export
- 💼 **Client Delivery ZIP** - One-click export package for client handoff
- ✅ **Launch Readiness Check** - Built-in release diagnostics before shipping
- ⚙️ **Smart Optimization** - Automatic mesh & material optimization for AR
- 👁️ **AR Preview** - See how your model looks in AR-ready format
- 📊 **Scene Validation** - Check if your model is AR-ready
- 🎨 **Quality Settings** - Control resolution, quality, and file format
- 🔍 **Debug Mode** - Built-in logging for troubleshooting
- 📦 **Multiple Formats** - Export as glTF 2.0, glTF Binary (GLB), or FBX

## 📍 WHERE IS EVERYTHING?

### AR Workspace (Top Menu)

After installation, click the new **"AR"** tab next to Layout, Modeling, etc.

```
Layout | Modeling | Sculpting | UV Editing | Shading | Rendering | AR ← NEW!
```

### Right Sidebar - AR Dashboard

- 🚀 **DEPLOY TO AR** - Main export button
- **Quick Actions** - Preview, Check, Optimize, Materials
- **Scene Status** - Real-time object and vertex count
- **Export Settings** - Quality, format, texture resolution

### AR Tools Panel

- Auto Optimize settings
- Material optimization
- AR preview tools

### Advanced Settings Panel

- Export format options
- Texture quality control
- Lighting baking
- Debug mode

---

## 🚀 QUICK START

### 1. Install (30 seconds)

- Download → `webxr_exporter.zip`
- Edit > Preferences > Add-ons > Install
- Search "WebXR" → Enable

### 2. Open AR Workspace

- Restart Blender (recommended)
- Click the **"AR"** tab at the top
- See all AR tools on the right

### 3. Prepare Your Model

- Use any Blender workspace to model
- Switch to **AR** workspace when ready
- Click **[Check]** to validate

### 4. Export!

- Click **🚀 DEPLOY TO AR**
- Your file is ready for AR platforms

---

## 📖 FULL DOCUMENTATION

**👉 [See INSTALLATION_GUIDE.md for complete user guide](INSTALLATION_GUIDE.md) 👈**

Includes:

- Detailed workspace layout diagram
- Feature descriptions
- Typical workflow
- Tips & tricks
- Troubleshooting
- Customization guide

---

## 💻 BLENDER COMPATIBILITY

**✅ Works on Blender 4.0 and EVERY version above**

| Version Range       | Status                 |
| ------------------- | ---------------------- |
| Blender 4.0.0+      | ✅ Full Support        |
| Blender 4.1.0+      | ✅ Recommended         |
| Blender 5.0.0+      | ✅ Forward Compatible  |
| All future versions | ✅ Expected Compatible |

**Single .zip installation works on all versions 4.0+**

📖 [See COMPATIBILITY.md for detailed version support](COMPATIBILITY.md)

---

## 📦 PROJECT STRUCTURE

```
webxr_exporter/
├── __init__.py              # Main addon file
├── operators/export.py      # Export operator
├── ui/panels.py             # AR Dashboard, Tools, Settings UI
├── tools/__init__.py        # AR tools (Preview, Check, Optimize)
├── workspace/__init__.py    # AR Workspace creation
├── utils/
│   ├── properties.py        # Scene properties
│   └── logger.py            # Console logging
├── INSTALLATION_GUIDE.md    # Complete user guide
└── README.md                # This file
```

---

## 🎮 AR DASHBOARD OVERVIEW

The **AR Dashboard** is divided into sections:

### 🚀 Main Export

Large button to deploy your model instantly

### 🎯 Quick Actions (4 buttons)

- **[Preview]** - Material preview mode
- **[Check]** - Validate AR readiness
- **[Optimize]** - Reduce polygon count
- **[Materials]** - Optimize all materials

### 📊 Scene Status

Real-time info:

- Object count
- Mesh count
- Total vertices
- Selection info

### ⚙️ Export Controls

- Quality slider (1-100%)
- Export format (GLB recommended)
- Texture quality (Medium recommended)
- Mesh optimization toggle

---

## 🛠️ FOR DEVELOPERS

### Extending the Addon

**Add new tools:**

1. Create operator in `tools/__init__.py`
2. Import in main `__init__.py`
3. Register in `addon_classes`

**Add new UI panels:**

1. Create panel in `ui/panels.py`
2. Import in `ui/__init__.py`
3. Register in main `__init__.py`

**Add properties:**

1. Update `utils/properties.py`
2. Register/unregister in `utils/properties.py`

### Best Practices

- Use relative imports: `from . import module`
- Handle exceptions gracefully
- Use descriptive error messages
- Test on Blender 4.0+

---

## 📝 VERSION HISTORY

- **v1.3** - Launch Pass Edition (current)
  - Live browser viewer auto-open on deploy
  - Mobile AR URL and QR generation from real LAN link
  - Client-ready ZIP package generation
  - Launch readiness score and status panel
  - Premium delivery actions (copy URL, open viewer, open folder)
- **v1.2** - AR Workspace Edition
  - Dedicated AR workspace with "AR" tab
  - Enhanced UI dashboard
  - AR tools & validation
  - Blender 4.0+ optimized
- **v1.1** - Modular structure
  - Organized into operators, ui, utils modules
  - Settings panel added
- **v1.0** - Initial release
  - Basic export functionality

---

## ⚖️ LICENSE

Created by Aura-Intelligence

---

## 🆘 TROUBLESHOOTING

**Addon not showing?**

- Restart Blender
- Check Edit > Preferences > Add-ons > Search "WebXR"

**AR workspace not visible?**

- Restart Blender
- Look at top menu bar for "AR" tab
- Ensure addon is enabled

**Export fails?**

- View > Toggle System Console for debug info
- Enable Debug Mode in Advanced Settings
- Ensure scene is not empty

**Performance issues?**

- Click [Check] to see scene stats
- Use [Optimize] to reduce polygons
- Reduce texture quality to "Low"

---

## 🌟 MADE FOR CREATORS

This addon is designed for:

- 3D Artists
- Game Developers
- AR/VR Developers
- WebXR Content Creators
- Blender Enthusiasts

Perfect for creating AR experiences that run in web browsers immediately!

---

**Happy AR Creating!** 🚀
