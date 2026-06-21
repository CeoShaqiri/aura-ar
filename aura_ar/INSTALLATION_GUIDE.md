# WebXR AR Exporter - Complete User Guide

## 🎯 Quick Start (Blender 4.0+)

### Installation

1. **Download the addon** as `webxr_exporter.zip`

2. **Install in Blender**:
   - Open Blender 4.0+
   - Go to: **Edit > Preferences > Add-ons**
   - Click **Install...**
   - Select `webxr_exporter.zip`
   - Search for "WebXR" and **enable** the addon

3. **Restart Blender** (recommended)

---

## 📍 WHERE IS EVERYTHING?

### 1️⃣ AR WORKSPACE (Top Menu Bar)

After installation, you'll see a new **"AR"** tab in your workspace tabs:

```
┌─────────────────────────────────────────────────────────┐
│ [+] Layout | Modeling | Sculpting | UV Editing | ... | AR  ← NEW!
└─────────────────────────────────────────────────────────┘
```

**Click "AR"** to enter the AR workspace with all tools organized:

```
┌──────────────────────────────────────────────────────────────┐
│ File  Edit  Render  Window  Help                             │
├──────────────────────────────────────────────────────────────┤
│ [+] Layout | Modeling | Sculpting | Rendering | AR ← Click! │
├───────────────────┬──────────────────────────────────────────┤
│                   │  AR Tab (Right Sidebar)                  │
│   3D VIEWPORT     │ ┌──────────────────────────────┐         │
│   (Main editing   │ │ 🔴 AR Dashboard              │         │
│    area)          │ │                              │         │
│                   │ │  🚀 DEPLOY TO AR (big btn)   │         │
│                   │ │                              │         │
│   (Your model)    │ │  Quick Actions:              │         │
│                   │ │  [Preview] [Check]           │         │
│                   │ │  [Optimize] [Materials]      │         │
│                   │ │                              │         │
│                   │ │  Scene Status:               │         │
│                   │ │  📦 Objects: 5 | Meshes: 5   │         │
│                   │ │  🔺 Vertices: 45,234         │         │
│                   │ │                              │         │
│                   │ │  Export Settings:            │         │
│                   │ │  Quality: ████░ 85%          │         │
│                   │ │  Format: glTF Binary ▼       │         │
│                   │ │  Textures: Medium ▼          │         │
│                   │ │  ☑ Optimize Mesh             │         │
│                   │ │                              │         │
│                   │ ├──────────────────────────────┤         │
│                   │ │ 🔴 AR Tools                  │         │
│                   │ │ ☑ Auto Optimize              │         │
│                   │ │ ☐ Bake Lighting              │         │
│                   │ │ [Optimize Materials]         │         │
│                   │ │ [AR Preview]                 │         │
│                   │ │ [Generate Preview Image]     │         │
│                   │ ├──────────────────────────────┤         │
│                   │ │ 🔴 Advanced Settings ▼       │         │
│                   │ │ (Click to expand)            │         │
│                   │ └──────────────────────────────┘         │
└───────────────────┴──────────────────────────────────────────┘
```

---

## 🎮 AR DASHBOARD - Main Interface

### 🚀 Main Export Button

The large **"DEPLOY TO AR"** button is your primary action:

- Exports your scene to WebXR/AR format
- All settings are applied automatically
- Progress is shown in the console

### 🎯 Quick Actions (Below Export)

#### [Preview]

- Shows how your model looks in AR-ready materials
- Switches to material preview mode
- Perfect for checking colors and textures

#### [Check]

- Validates your scene for AR export
- Checks for common issues:
  - ❌ Scene is empty
  - ⚠️ No textured materials
  - ⚠️ Polygon count too high
  - ✅ All good!

#### [Optimize]

- Automatically reduces polygon count
- Adds decimation modifiers (70% of original)
- Makes model lighter for AR devices

#### [Materials]

- Simplifies and optimizes all materials
- Removes unnecessary PBR complexity
- Ensures materials work well on AR devices

### 📊 Scene Status Box

Shows real-time info:

- **Objects**: Total objects in scene
- **Meshes**: Number of mesh objects
- **Vertices**: Total polygons (if >1M, optimization recommended)
- **Selected Vertices**: Only if you have objects selected

### ⚙️ Export Settings

**Quality Slider (1-100%)**

- Higher = better quality, larger file size
- 85% is recommended for AR
- Adjust based on detail needs

**Format Dropdown**

- **glTF Binary (GLB)**: Recommended - Single file, smaller
- **glTF 2.0**: Separate textures, standard format
- **FBX**: For some platforms, not AR-optimized

**Textures Dropdown**

- **Low (512px)**: Smallest files, fastest loading
- **Medium (1024px)**: Best balance (recommended)
- **High (2048px)**: Best quality, slower on mobile

**Optimize Mesh**

- ☑ Checked = Reduces polygon count automatically
- ☐ Unchecked = Keeps full detail

---

## 🛠️ AR TOOLS TAB

### Optimize Section

- **Auto Optimize**: Enable automatic scene optimization
- **Bake Lighting**: Pre-bake scene lighting into textures (for better AR lighting)

### Materials Section

- **[Optimize Materials]**: Simplify all materials at once

### Preview Section

- **[AR Preview]**: Real-time preview of AR appearance
- **[Generate Preview Image]**: Renders a preview image

---

## 🔧 ADVANCED SETTINGS TAB

### Export Format Options

Three format buttons - click one:

- **glTF**: Two-file format (recommended for web)
- **GLB**: Binary format (best for AR, recommended)
- **FBX**: Autodesk format (good for game engines)

### Texture Settings

Same as main dashboard - fine-tune texture quality

### Lighting Section

- **Bake Lighting into Textures**: Pre-bake lighting
  - Improves AR appearance
  - Makes files independent of scene lighting

### Development Section

- **Debug Mode**: Show technical information
  - Enables console logging with timestamps
  - Shows Blender version and object counts
  - Useful for troubleshooting

---

## 📋 TYPICAL WORKFLOW

### 1. Model Your Object

- Use Blender normally (Layout workspace)
- Apply materials and textures
- Add basic lighting if desired

### 2. Switch to AR Workspace

- Click **"AR"** tab at top
- Everything you need is on the right sidebar

### 3. Prepare & Check

- Click **[Check]** to validate
- Results appear in console (View > Toggle System Console)
- Fix any ⚠️ warnings if needed

### 4. Optimize (Optional)

- Click **[Optimize]** if polygon count too high
- Or check **Auto Optimize** box before export

### 5. Adjust Settings

- **Quality**: Set to 85% for good balance
- **Format**: Keep GLB for AR
- **Textures**: Choose Medium for most cases

### 6. Export!

- Click big **🚀 DEPLOY TO AR** button
- Wait for completion message
- Check console for status

### 7. Use Your Exported File

- Exported file appears in default Blender directory
- Filename: `model_YYYYMMDD_HHMMSS.glb` (or chosen format)
- Upload to your WebXR AR platform

---

## 💡 TIPS & TRICKS

### For Best AR Results:

1. **Keep polygon count under 500K** (use Optimize if needed)
2. **Use PBR materials** (Metallic, Roughness, Normal maps)
3. **Bake lighting** for consistent AR appearance
4. **Test on mobile device** before distributing
5. **Use Medium or High texture quality** (Low loses detail)

### Performance:

- Polygon count affects loading time most
- Texture resolution affects memory usage
- Use Preview tool to check before export

### Troubleshooting:

- **"Scene is empty"**: Add objects to your scene
- **"High polygon count"**: Click [Optimize]
- **Export fails**: Check console (View > Toggle System Console)
- **Materials look wrong**: Try [Optimize Materials]
- **Addon not showing**: Restart Blender

---

## 🎨 WORKSPACE CUSTOMIZATION

The **AR workspace** can be customized! After creation:

1. Arrange areas as you want (drag edges)
2. Change area types (right-click > Change Type)
3. Add/remove panels from the sidebar
4. These settings are saved in your workspace

---

## 🚀 VERSION COMPATIBILITY

- **Blender 4.0+**: ✅ Full support
- **Blender 3.6**: ⚠️ Limited (some UI features may differ)
- **Blender 2.x**: ❌ Not supported

---

## 📦 ADDON FILES EXPLAINED

```
webxr_exporter/
├── __init__.py              # Main addon file - loads everything
├── operators/export.py      # Export operator
├── ui/panels.py             # AR Dashboard, Tools, Settings panels
├── tools/__init__.py        # AR tools (Preview, Optimize, etc.)
├── workspace/__init__.py    # AR Workspace creation
├── utils/properties.py      # Scene properties storage
├── utils/logger.py          # Console logging
└── README.md                # Installation guide
```

---

## ⚠️ KNOWN LIMITATIONS

- Workspace won't auto-reappear if renamed (create new)
- Some Blender versions may have slight UI layout differences
- Complex node materials may lose some details on export

---

## 🔗 SUPPORT & UPDATES

For issues or feature requests, refer to the project repository.

**Happy AR Creating!** 🚀
