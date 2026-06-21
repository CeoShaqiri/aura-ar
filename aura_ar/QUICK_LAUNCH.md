# 🚀 WebXR Addon - Quick Launch Guide

## ✅ Your Addon is Ready!

**Package Location:**

```
c:\Users\senav\dist\webxr_exporter_20260415_050508.zip
```

**Size:** 56.8 KB  
**Status:** ✅ Ready for installation  
**Blender Versions:** 4.0 and above

---

## 📥 Installation (5 Minutes)

### Step 1: Open Blender

- Launch **Blender 4.0** or newer
- Open **Preferences** (`Edit → Preferences` on Windows)

### Step 2: Navigate to Addons

- Click **"Add-ons"** in the left sidebar
- Click **"Install..."** button (top right)

### Step 3: Select ZIP File

- Navigate to: `c:\Users\senav\dist\`
- Select: `webxr_exporter_20260415_050508.zip`
- Click **"Install Add-on"**

### Step 4: Enable Addon

- Search for "WebXR" in the search box
- Check the ✅ box next to "Import-Addon: WebXR Exporter"

### Step 5: Verify Installation

- Check **console output** (Window → Toggle System Console)
- You should see: `✅ WebXR Addon loaded successfully!`

### Step 6: Restart Blender (Recommended)

- Close and reopen Blender
- New **"AR" workspace tab** should appear in top menu bar

---

## 🧪 Quick Test (2 Minutes)

1. **Open default Blender scene** (with default cube)
2. **Look for AR workspace** - New tab should be visible at top
3. **Switch to AR workspace**
4. **Create a test cube** (if needed)
5. **Click "Deploy to AR"** button in AR Dashboard panel
6. **Check console for** ✅ success message and file locations

---

## 📂 What Gets Generated

After clicking "Deploy to AR", you'll see 3 files created:

```
webxr_exporter/exports/
├── model_YYYYMMDD_HHMMSS.glb      (Your 3D model)
├── ar_YYYYMMDD_HHMMSS.qr          (QR code image)
└── deployment_YYYYMMDD_HHMMSS.txt (Instructions)
```

---

## 🎯 Key Features at a Glance

| Feature               | Location          | What It Does                          |
| --------------------- | ----------------- | ------------------------------------- |
| **Deploy to AR**      | AR Dashboard      | Exports model + generates QR code     |
| **Preview Materials** | AR Tools          | Shows how model looks in AR lighting  |
| **Check ARready**     | AR Tools          | Validates scene for AR export         |
| **Optimize Model**    | AR Tools          | Reduces polygon count for performance |
| **Material Optimize** | AR Tools          | Simplifies materials for web          |
| **Format Selection**  | Advanced Settings | Choose GLB/glTF/FBX export            |
| **Texture Quality**   | Advanced Settings | Control texture resolution            |
| **Debug Mode**        | Advanced Settings | Enable verbose console logging        |

---

## 🎥 What Users Can Do With Your QR Code

1. **Scan QR code** with iPhone/Android camera
2. **View AR model** in their physical space (laptop camera on desktop)
3. **Share QR code** with others
4. **No app needed** - Works in web browser via WebXR standard

---

## ❓ Troubleshooting

**AR workspace doesn't appear:**

- Restart Blender after installation
- Check console for any error messages

**Export button does nothing:**

- Select at least one object in scene
- Check that objects aren't empty meshes
- Look at console for error details

**QR code not generated:**

- Ensure `pillow` and `qrcode` libraries are installed
- Check file permissions in `exports/` folder

**See the full guide:**

- [INSTALL_AND_TEST.md](./INSTALL_AND_TEST.md) - Comprehensive 10-step test suite

---

**Need help?** Check the console output for detailed error messages (Window → Toggle System Console)

**Ready to test?** Install the addon and run the verification tests in INSTALL_AND_TEST.md!

🎉 Your AR addon is complete and ready to use!
