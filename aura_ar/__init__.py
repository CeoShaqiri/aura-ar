bl_info = {
    "name": "The Aura Standard",
    "author": "The Aura Standard",
    "version": (3, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > AR",
    "description": "The World's First One-Click AR Deployment for Blender. Powered by The Aura Standard.",
    "category": "Import-Export",
    "support": "COMMUNITY",
    "doc_url": "https://ceo-of-aura.cloud",
    "tracker_url": "https://ceo-of-aura.cloud",
}

import bpy
from . import operators
from . import ui
from . import utils
from . import tools
from . import workspace

# Import classes for registration
from .operators import (
    WEBXR_OT_export, WEBXR_OT_copy_cloud_url, WEBXR_OT_copy_log_url, WEBXR_OT_open_log_url,
    WEBXR_OT_start_tunnel, WEBXR_OT_stop_tunnel, WEBXR_OT_copy_public_url,
    WEBXR_OT_architecture_preset, WEBXR_OT_character_preset,
    WEBXR_OT_auto_rig, WEBXR_OT_bake_decals, WEBXR_OT_scan_addons,
)
try:
    from .ui import (
        WEBXR_PT_ar_dashboard,
        WEBXR_PT_deploy_log,
        WEBXR_PT_ar_tools,
        WEBXR_PT_advanced_settings,
        WEBXR_PT_panel,
        WEBXR_PT_settings,
        WEBXR_PT_quick_access,
    )
    has_quick_access = True
except ImportError:
    from .ui import (
        WEBXR_PT_ar_dashboard,
        WEBXR_PT_deploy_log,
        WEBXR_PT_ar_tools,
        WEBXR_PT_advanced_settings,
        WEBXR_PT_panel,
        WEBXR_PT_settings,
    )
    has_quick_access = False

from .utils.properties import WebXRProperties


# ─────────────────────────────────────────────────────────────────────────────
# Addon Preferences — Edit > Preferences > Add-ons > The Aura Standard
# ─────────────────────────────────────────────────────────────────────────────
class AuraARPreferences(bpy.types.AddonPreferences):
    """The Aura Standard cloud deployment settings"""
    bl_idname = __name__  # must equal "aura_ar" — the package folder name

    aura_api_key: bpy.props.StringProperty(
        name="Aura API Key",
        description="Your API key for ceo-of-aura.cloud — get it at https://ceo-of-aura.cloud",
        default="",
        subtype="PASSWORD",
    )

    artist_name: bpy.props.StringProperty(
        name="Artist / Studio Name",
        description="Shown on the viewer page: 'Deployed via Aura · Created by [you]'",
        default="",
    )

    def draw(self, context):
        layout = self.layout

        # ── Identity header ───────────────────────────────────────────
        layout.separator(factor=0.6)
        header_box = layout.box()
        hc = header_box.column(align=True)
        hc.scale_y = 1.2
        title_row = hc.row(align=True)
        title_row.alignment = 'CENTER'
        title_row.label(text="  ◆  THE AURA STANDARD  ◆", icon='WORLD')
        hc.separator(factor=0.3)
        sub_row = hc.row(align=True)
        sub_row.alignment = 'CENTER'
        sub_row.label(text="The World's First Reality Engine for Blender")

        # ── Cloud credentials ──────────────────────────────────────────
        layout.separator(factor=1.0)
        layout.label(text="  ◆  Cloud Credentials", icon='KEYINGSET')
        layout.separator(factor=0.3)
        cred_box = layout.box()
        cc = cred_box.column(align=True)
        cc.scale_y = 1.3
        cc.prop(self, "aura_api_key", text="API Key")
        cc.separator(factor=0.4)
        cc.prop(self, "artist_name",  text="Studio / Artist Name")

        # ── Status ────────────────────────────────────────────────────
        layout.separator(factor=0.8)
        status_box = layout.box()
        if self.aura_api_key.strip():
            status_row = status_box.row(align=True)
            status_row.alignment = 'CENTER'
            status_row.label(
                text="  ◆  CLOUD DEPLOY ACTIVE  ◆",
                icon='CHECKMARK'
            )
        else:
            status_box.alert = True
            status_row = status_box.row(align=True)
            status_row.alignment = 'CENTER'
            status_row.label(
                text="  Paste your API Key above to activate cloud deploy",
                icon='ERROR'
            )

        layout.separator(factor=0.8)

# All classes that need to be registered
addon_classes = [
    WEBXR_OT_export,
    WEBXR_OT_copy_cloud_url,
    WEBXR_OT_copy_log_url,
    WEBXR_OT_open_log_url,
    WEBXR_OT_start_tunnel,
    WEBXR_OT_stop_tunnel,
    WEBXR_OT_copy_public_url,
    WEBXR_OT_architecture_preset,
    WEBXR_OT_character_preset,
    WEBXR_OT_auto_rig,
    WEBXR_OT_bake_decals,
    WEBXR_OT_scan_addons,
    WEBXR_PT_ar_dashboard,
    WEBXR_PT_deploy_log,
    WEBXR_PT_ar_tools,
    WEBXR_PT_advanced_settings,
    WEBXR_PT_panel,
    WEBXR_PT_settings,
    WEBXR_PT_deploy_log,
]

if has_quick_access:
    addon_classes.append(WEBXR_PT_quick_access)


def register():
    """Register addon classes and properties"""
    try:
        print("\n" + "="*60)
        print("🚀 THE AURA STANDARD — REGISTRATION STARTING")
        print("="*60)

        # Check Blender version compatibility first
        print("  1. Checking Blender version...")
        is_compatible = utils.check_and_report()
        if not is_compatible:
            print("⚠️  WARNING: Addon may not work properly on this Blender version")
        
        # Register custom properties first
        print("  2. Registering custom properties...")
        try:
            bpy.utils.register_class(AuraARPreferences)
            utils.properties.register_properties()
            print("     ✅ Properties registered")
        except Exception as e:
            print(f"     ❌ Properties: {e}")
        
        # Register AR tools
        print("  3. Registering AR tools...")
        try:
            tools.register()
            print("     ✅ Tools registered")
        except Exception as e:
            print(f"     ❌ Tools: {e}")
        
        # Register workspace
        print("  4. Creating AR workspace...")
        try:
            workspace.register_workspace()
            print("     ✅ Workspace registered")
        except Exception as e:
            print(f"     ❌ Workspace: {e}")
        
        # Register all UI classes
        print("  5. Registering UI panels...")
        for cls in addon_classes:
            try:
                bpy.utils.register_class(cls)
                print(f"     ✅ {cls.__name__}")
            except RuntimeError as e:
                if "already registered" in str(e):
                    try:
                        bpy.utils.unregister_class(cls)
                    except RuntimeError:
                        pass
                    try:
                        bpy.utils.register_class(cls)
                        print(f"     🔄 {cls.__name__} (reloaded)")
                    except Exception as re:
                        print(f"     ❌ {cls.__name__} reload failed: {re}")
                else:
                    print(f"     ❌ {cls.__name__}: {e}")
        
        print("\n" + "="*60)
        print("✅ The Aura Standard v3.0")
        print("="*60)
        print("📍 Location: View3D > Sidebar (press N) > AR tab")
        print("🎯 Features: AR Preview, Optimization, One-Click Export")
        print("🎪 Feature: Dedicated 'AR' Workspace Tab")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()


def unregister():
    """Unregister addon classes and properties"""
    try:
        # Stop any active Cloudflare tunnel
        from .operators.cloudflare import unregister as cf_unreg
        cf_unreg()
    except Exception:
        pass

    try:
        # Unregister classes in reverse order
        for cls in reversed(addon_classes):
            try:
                bpy.utils.unregister_class(cls)
            except RuntimeError:
                pass  # Already unregistered
        
        # Unregister tools
        tools.unregister()
        
        # Unregister custom properties and preferences
        utils.properties.unregister_properties()
        try:
            bpy.utils.unregister_class(AuraARPreferences)
        except RuntimeError:
            pass
        
        print("❌ WebXR Exporter addon unregistered.\n")
        
    except Exception as e:
        print(f"❌ Unregistration error: {e}")