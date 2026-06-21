#!/usr/bin/env python3
"""
WEBXR AR EXPORTER - INSTALLATION & TESTING GUIDE

Complete step-by-step instructions for installing and testing
the addon in Blender 4.0+
"""

╔════════════════════════════════════════════════════════════════════════════╗
║ ║
║ 🚀 WEBXR AR EXPORTER - INSTALLATION & TESTING GUIDE ║
║ ║
║ Your addon is ready! Install it now. ║
║ ║
╚════════════════════════════════════════════════════════════════════════════╝

═════════════════════════════════════════════════════════════════════════════
PART 1: INSTALLATION (5 MINUTES)
═════════════════════════════════════════════════════════════════════════════

✅ YOUR ZIP FILE:
Location: c:\Users\senav\dist\webxr_exporter_20260415_050508.zip
Size: ~57 KB
Status: Ready to install

📋 BLENDER REQUIREMENTS:
✅ Blender 4.0 or newer
✅ Windows / macOS / Linux
✅ English language (recommended)

───────────────────────────────────────────────────────────────────────────

INSTALLATION STEPS (Do this now):

1️⃣ OPEN BLENDER 4.0+

- Launch Blender (any workspace)
- Let it fully load

2️⃣ OPEN ADD-ONS PREFERENCES
Menu: Edit > Preferences

┌─────────────────────────────────────┐
│ Top menu bar: Edit > Preferences │
└─────────────────────────────────────┘

3️⃣ NAVIGATE TO ADD-ONS
Left sidebar: Click "Add-ons" icon

┌────────────────────────┬──────────────────────────────┐
│ Left sidebar icons │ Left sidebar icons │
│ (small icons) │ Look for folder/box icon │
│ ↓ │ That's "Add-ons" │
│ Click: Add-ons │ │
└────────────────────────┴──────────────────────────────┘

4️⃣ CLICK "INSTALL"
Top right of Add-ons window:

┌──────────────────────────────────┐
│ [Install...] [Install from URL] │
└──────────────────────────────────┘

Click: Install...

5️⃣ SELECT THE ZIP FILE
File browser opens:

Navigate to:
C:\Users\senav\dist\

Select: webxr_exporter_20260415_050508.zip

Click: Install Add-on

6️⃣ ENABLE THE ADDON
✅ Search for "WebXR"

You'll see:
┌──────────────────────────────────────┐
│ ☐ 1-Click WebXR Exporter │
│ (by Aura-Intelligence) │
└──────────────────────────────────────┘

Click checkbox to enable (☑️)

7️⃣ RESTART BLENDER (Recommended)
File > Quit
Reopen Blender

OR just continue (might need refresh)

✅ INSTALLATION COMPLETE!

───────────────────────────────────────────────────────────────────────────

VERIFICATION - You should now see:
✅ New "AR" workspace tab at top
✅ Right sidebar has "AR" category
✅ Console shows version check message

═════════════════════════════════════════════════════════════════════════════
PART 2: FINDING THE ADDON (Where is everything?)
═════════════════════════════════════════════════════════════════════════════

After installation, here's where to find things:

🎪 AR WORKSPACE TAB
│
├─ Top menu bar (where Layout, Modeling, Sculpting are):
│
│ ┌─────────────────────────────────────────────────────────┐
│ │ + │ Layout │ Modeling │ Sculpting │ ... │ AR ← NEW! │
│ └─────────────────────────────────────────────────────────┘
│
└─ Click "AR" to switch to AR workspace

🎯 AR DASHBOARD (Right Sidebar)
│
├─ Once in AR workspace, press N (if sidebar hidden)
│
├─ Right side panel shows:
│
│ ┌──────────────────────────────────┐
│ │ 🔴 AR Dashboard │ ← Main UI
│ │ │
│ │ 🚀 DEPLOY TO AR │ ← Big export button
│ │ │
│ │ [Preview] [Check] │ ← Quick actions
│ │ [Optimize] [Materials] │
│ │ │
│ │ Scene Status info │
│ │ Export Settings controls │
│ │ │
│ ├──────────────────────────────────┤
│ │ 🔴 AR Tools │
│ │ [Optimize Materials] │
│ │ [AR Preview] │
│ │ │
│ ├──────────────────────────────────┤
│ │ 🔴 Advanced Settings ▼ │
│ │ [Click to expand] │
│ └──────────────────────────────────┘
│
└─ Tab name: "AR" (on right sidebar)

═════════════════════════════════════════════════════════════════════════════
PART 3: TESTING (Do these now!)
═════════════════════════════════════════════════════════════════════════════

TEST 1: VERIFY ADDON IS LOADED
─────────────────────────────────

1. Open Blender
2. Go to: Windows > Toggle System Console (optional, for debug)
3. Look at console output
4. You should see:

   ✅ WebXR Exporter v1.2 - AR Edition
   ✅ Location: View3D > Sidebar > AR
   ✅ Features: AR Preview, Optimization, One-Click Export
   ✅ New: Dedicated 'AR' Workspace Tab

✅ TEST PASSED if you see these messages!

───────────────────────────────────────────────────────────────────────────

TEST 2: CHECK AR WORKSPACE TAB EXISTS
─────────────────────────────────────

1. Look at top menu bar
2. Count workspaces: Layout | Modeling | Sculpting | ...
3. Last one should be: AR

┌─────────────────────────────────────────────────────────┐
│ Layout │ Modeling │ Sculpting │ UV Editing │ ... │ AR │
│ ↑ │
│ Should be here! │
└─────────────────────────────────────────────────────────┘

✅ TEST PASSED if "AR" tab exists!

───────────────────────────────────────────────────────────────────────────

TEST 3: CLICK "AR" WORKSPACE
────────────────────────────

1. Click on "AR" tab
2. Blender switches to AR workspace
3. Right sidebar shows "AR Dashboard" on right

┌────────────────────────────────────────────────┐
│ Current Workspace: AR ✅ │
│ │
│ (Workspace switches to AR layout) │
│ │
│ Right panel shows: │
│ ┌─────────────────────────────────────────┐ │
│ │ 🔴 AR Dashboard │ │
│ │ 🔴 AR Tools │ │
│ │ 🔴 Advanced Settings ▼ │ │
│ └─────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘

✅ TEST PASSED if you see AR Dashboard!

───────────────────────────────────────────────────────────────────────────

TEST 4: CREATE A TEST OBJECT & EXPORT
──────────────────────────────────────

1. In AR workspace:
   - You still have the 3D viewport on left
   - Default cube is there (or add one)
2. Make sure cube is visible:
   - Keep default scene or add: Shift+A > Mesh > Cube

3. Click AR Dashboard button to EXPAND if collapsed

4. Scroll in right panel to see:
   - 🚀 DEPLOY TO AR button
   - Quick Action buttons
   - Scene Status
   - Export Settings

5. TEST THE CHECK BUTTON:
   ┌────────────────────────────────────┐
   │ [Preview] [Check] │ ← Click [Check]
   │ [Optimize] [Materials] │
   └────────────────────────────────────┘

   In console, you should see:
   ✅ Model is AR-ready!
   ✅ Objects: 1
   ✅ Vertices: 8 (for default cube)

6. TEST THE EXPORT:
   ┌──────────────────────────────┐
   │ 🚀 DEPLOY TO AR │ ← Click this
   │ (Big button, can't miss) │
   └──────────────────────────────┘

   Wait 5-10 seconds...

   In console, watch for:
   ✅ Starting WebXR export...
   ✅ Model exported: model*...glb
   ✅ QR Code generated: ar*...\_qr.png
   ✅ Export completed successfully!

✅ TEST PASSED if export completes!

───────────────────────────────────────────────────────────────────────────

TEST 5: CHECK EXPORT OUTPUT
───────────────────────────

1. After export, open file explorer:
   C:\Users\senav\webxr_exporter\exports\

   (Addon creates this folder automatically)

2. You should see:
   ✅ model*[date]*[time].glb (the 3D file!)
   ✅ ar*[ID]\_qr.png (QR code image!)
   ✅ AR_DEPLOYMENT*[ID].txt (Instructions!)
   ✅ ar*metadata*[ID].json (Metadata!)

3. VERIFY FILES:
   - GLB file: Should be 50KB-5MB
   - QR code: Should be PNG image
   - TXT file: Should be readable
   - JSON: Should be technical data

✅ TEST PASSED if all 4 files exist!

───────────────────────────────────────────────────────────────────────────

TEST 6: VIEW QR CODE
───────────────────

1. Open the QR code image (ar\_[ID]\_qr.png)
2. Should see a scannable QR code pattern

┌──────────────────────┐
│ ██ ██ █ █ ██ ██ │
│ █ █ █ █ ██ █ │
│ ██ ██ █ █ ██ ██ │
│ ░░░ ░░░ ░ ░░░ ░░ │
│ ░░░ ░░░ ░ ░░░ ░░ │
└──────────────────────┘

✅ TEST PASSED if QR code is visible!

───────────────────────────────────────────────────────────────────────────

TEST 7: READ DEPLOYMENT INFO
───────────────────────────

1. Open AR*DEPLOYMENT*[ID].txt file
2. Should show:

   🎯 MODEL: ...
   ⚙️ QUALITY: 85%

   🌐 SHARE YOUR AR MODEL

   Web URL: https://ar.example.com/viewer/...
   📱 QR CODE: ar\_[ID]\_qr.png

   🚀 HOW TO USE YOUR AR MODEL:
   [Instructions...]

✅ TEST PASSED if file is readable and formatted!

───────────────────────────────────────────────────────────────────────────

TEST 8: TEST SETTINGS & CONTROLS
────────────────────────────────

1. In AR Dashboard, find **Export Settings**:

2. TEST Quality Slider:
   - Drag Quality slider left/right
   - Values should change from 1-100%
     ✅ PASS if slider moves

3. TEST Format Dropdown:
   - Click: "Format: glTF Binary ▼"
   - Options appear: GLB, glTF, FBX
   - Select different format
     ✅ PASS if options appear

4. TEST Texture Quality:
   - Click: "Textures: Medium ▼"
   - Options: Low, Medium, High
   - Select different one
     ✅ PASS if options appear

5. TEST Optimize Mesh checkbox:
   - Click ☐ to check/uncheck
     ✅ PASS if checkbox toggles

6. Export again with different settings
   ✅ PASS if export works with new settings

───────────────────────────────────────────────────────────────────────────

TEST 9: TEST TOOLS & BUTTONS
────────────────────────────

1. Scroll to see AR Tools section

2. TEST [Preview] button:
   - Viewport should switch to material preview mode
     ✅ PASS if viewport changes

3. TEST [Optimize] button:
   - Polygon count should decrease
     ✅ PASS if optimization runs

4. TEST [Check] button again:
   - Should validate scene
   - Show object/vertex counts
     ✅ PASS if info displays

5. TEST [Materials] button:
   - Should optimize materials
     ✅ PASS if runs without errors

───────────────────────────────────────────────────────────────────────────

TEST 10: ADVANCED SETTINGS
──────────────────────────

1. Find "Advanced Settings ▼" section

2. Click to expand (should show more options)

3. OPTIONS should include:
   ✅ Export format buttons (GLB / glTF / FBX)
   ✅ Texture Quality
   ✅ Bake Lighting toggle
   ✅ Debug Mode toggle

4. TEST Debug Mode:
   - Enable Debug Mode checkbox
   - Check console
   - Should show more detailed logging
     ✅ PASS if debug output appears

═════════════════════════════════════════════════════════════════════════════
PART 4: TROUBLESHOOTING
═════════════════════════════════════════════════════════════════════════════

PROBLEM: Addon doesn't appear
SOLUTION:

1. Check Edit > Preferences > Add-ons
2. Search for "WebXR"
3. If not found, reinstall:
   - Remove addon folder
   - Install ZIP again
4. Restart Blender

───────────────────────────────────────────────────────────────────────────

PROBLEM: "AR" tab not showing
SOLUTION:

1. Restart Blender
2. Check console for errors:
   Windows > Toggle System Console
3. Verify addon is enabled (checkbox checked)

───────────────────────────────────────────────────────────────────────────

PROBLEM: Export button not working
SOLUTION:

1. Make sure scene has objects (cube is default)
2. Check console for error messages
3. Try [Check] button first to validate
4. Ensure no read-only folders

───────────────────────────────────────────────────────────────────────────

PROBLEM: QR code not generating
SOLUTION:

1. Install dependencies:
   pip install qrcode pillow
2. Restart Blender
3. Try export again

───────────────────────────────────────────────────────────────────────────

PROBLEM: Export folder not created
SOLUTION:

1. Manual create: C:\Users\senav\webxr_exporter\exports\
2. Give full permissions to folder
3. Try export again

═════════════════════════════════════════════════════════════════════════════
PART 5: NEXT STEPS - TESTING AR (Optional)
═════════════════════════════════════════════════════════════════════════════

Once exports are working, you can test the actual AR:

ON PHONE:

1. Scan QR code with phone camera
2. Browser opens
3. Beautiful AR viewer loads
4. Click "🚀 Launch AR"
5. Camera activates
6. Model appears in AR!

ON LAPTOP:

1. Open deployment info file
2. Copy web URL
3. Paste in browser (localhost or your server)
4. Click "🚀 Launch AR"
5. Webcam activates
6. Model appears in AR!

═════════════════════════════════════════════════════════════════════════════
FINAL CHECKLIST - YOU'RE DONE IF:
═════════════════════════════════════════════════════════════════════════════

✅ Addon installed in Blender
✅ "AR" workspace tab visible
✅ AR Dashboard displays properly
✅ All buttons work ([Check], [Optimize], etc)
✅ Export button works
✅ Files generated in exports folder:
✅ .glb file created
✅ QR code image created
✅ Deployment info created
✅ Metadata created
✅ Console shows success messages
✅ Settings controls work properly

═════════════════════════════════════════════════════════════════════════════

🎉 CONGRATULATIONS! YOUR ADDON IS WORKING!

If all tests passed, you're ready to:

1. Create 3D models
2. Export to AR
3. Share QR codes
4. Have others view in AR

═════════════════════════════════════════════════════════════════════════════

SUPPORT:

- Check documentation in addon folder
- Enable Debug Mode for more info
- See console for error messages (Ctrl+F3)

QUESTIONS?

- See FINAL_SUMMARY.md for features
- See AR_FEATURES_COMPLETE.md for how it works
- See INSTALLATION_GUIDE.md for detailed help

═════════════════════════════════════════════════════════════════════════════

Ready to create AR experiences? 🚀

Happy modeling & sharing!
