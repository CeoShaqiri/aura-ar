import bpy
import os
import json
from bpy.types import Panel

def _addons():
    try:
        from ..operators.export import _detect_addons
        return _detect_addons()
    except Exception:
        return {}


def _read_deploy_log():
    """Load the deployment log JSON; return [] if missing or corrupt."""
    log_path = os.path.join(os.path.expanduser("~"), ".aura_ar_exports", "deploy_log.json")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _section(layout, title, icon='NONE'):
    """Luxury section divider — decorative label with generous spacing."""
    layout.separator(factor=1.0)
    row = layout.row(align=False)
    row.alignment = 'LEFT'
    if icon != 'NONE':
        row.label(text=f"  {title}", icon=icon)
    else:
        row.label(text=f"  {title}")
    layout.separator(factor=0.2)


# ============================================================================
# ◆  MAIN DASHBOARD
# ============================================================================

class WEBXR_PT_ar_dashboard(Panel):
    """The Aura Standard — Command Centre"""
    bl_label      = "The Aura Standard"
    bl_idname     = "WEBXR_PT_ar_dashboard"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"

    def draw_header(self, context):
        self.layout.label(text="", icon='WORLD')

    def draw(self, context):
        layout = self.layout
        scene  = context.scene
        props  = getattr(scene, "webxr_props", None)

        if props is None:
            box = layout.box()
            box.alert = True
            box.label(text="Re-enable The Aura Standard addon.", icon='ERROR')
            return

        addon_prefs = context.preferences.addons.get("aura_ar")
        has_key     = bool(addon_prefs and addon_prefs.preferences.aura_api_key.strip())
        artist      = (addon_prefs.preferences.artist_name.strip() if addon_prefs else "")

        # ── Status badge ─────────────────────────────────────────────
        layout.separator(factor=0.5)
        badge = layout.box()
        badge_row = badge.row(align=True)
        badge_row.alignment = 'CENTER'
        if has_key:
            badge_row.label(
                text=f"  ◆  CLOUD READY  ·  {artist or 'Creator'}  ◆",
                icon='KEYINGSET'
            )
        else:
            badge = layout.box()
            badge.alert = True
            badge_row = badge.row(align=True)
            badge_row.alignment = 'CENTER'
            badge_row.label(
                text="  ◇  LOCAL MODE  ·  Add API Key in Preferences",
                icon='ERROR'
            )

        # ── Hero launch button ────────────────────────────────────────
        layout.separator(factor=1.4)
        launch_col = layout.column(align=True)
        launch_col.scale_y = 2.8
        launch_col.operator(
            "webxr.export_model",
            icon='WORLD',
            text="  ◆  LAUNCH TO AR",
        )
        layout.separator(factor=1.0)

        # ── Scene intel ───────────────────────────────────────────────
        _section(layout, "Scene Intel", 'OUTLINER_OB_MESH')
        intel_box = layout.box()
        intel_col = intel_box.column(align=True)
        intel_col.scale_y = 1.1

        obj_count   = len(scene.objects)
        mesh_count  = sum(1 for o in scene.objects if o.type == 'MESH')
        total_verts = sum(len(o.data.vertices) for o in scene.objects if o.type == 'MESH')

        split = intel_col.split(factor=0.5, align=True)
        split.label(text=f"  Objects    {obj_count}")
        split.label(text=f"Meshes    {mesh_count}")
        split2 = intel_col.split(factor=0.5, align=True)
        split2.label(text=f"  Vertices   {total_verts:,}")
        if context.selected_objects:
            sel_v = sum(
                len(o.data.vertices)
                for o in context.selected_objects
                if o.type == 'MESH'
            )
            split2.label(text=f"Selected  {sel_v:,}", icon='RESTRICT_SELECT_OFF')

        # ── Scene mode ────────────────────────────────────────────────
        _section(layout, "Scene Mode", 'SCENE_DATA')
        mode_box = layout.box()
        mode_col = mode_box.column(align=True)
        mode_col.prop(props, "scene_mode", text="")
        layout.separator(factor=0.4)
        preset_row = layout.row(align=True)
        preset_row.scale_y = 1.3
        preset_row.operator("webxr.architecture_preset", icon='HOME',        text="Architecture")
        preset_row.operator("webxr.character_preset",    icon='ARMATURE_DATA', text="Character")

        # ── Optimise ──────────────────────────────────────────────────
        _section(layout, "Export Settings", 'PREFERENCES')
        cfg_box = layout.box()
        cfg_col = cfg_box.column(align=True)
        cfg_col.scale_y = 1.15
        sub = cfg_col.column(align=True)
        sub.enabled = getattr(props, 'optimize_mesh', True)
        sub.prop(props, "decimate_ratio", slider=True, text="Geometry")
        cfg_col.prop(props, "texture_quality", text="Textures")

        layout.separator(factor=0.6)
        opt_row = layout.row(align=True)
        opt_row.scale_y = 1.2
        opt_row.operator("webxr.optimize_ar",       icon='MOD_SIMPLIFY', text="Optimize")
        opt_row.operator("webxr.check_ar_ready",    icon='VIEWZOOM',     text="Validate")

        # ── Last deployment ───────────────────────────────────────────
        cloud_url = getattr(props, 'cloud_ar_url', '')
        if cloud_url:
            _section(layout, "Last Deployment", 'CHECKMARK')
            dep_box = layout.box()
            dep_col = dep_box.column(align=True)
            dep_col.scale_y = 1.1
            dep_col.label(
                text="  " + (cloud_url[:46] + ("…" if len(cloud_url) > 46 else "")),
                icon='LINKED'
            )
            layout.separator(factor=0.4)
            copy_row = layout.row(align=True)
            copy_row.scale_y = 1.4
            copy_row.operator("webxr.copy_cloud_url", icon='COPY_ID', text="  Copy AR Link")

        # ── Share / Cloudflare ────────────────────────────────────────
        if props.last_viewer_url:
            _section(layout, "Public Share", 'WORLD')
            from ..operators.cloudflare import _tunnel_proc
            tunnel_on = (_tunnel_proc is not None and _tunnel_proc.poll() is None)
            share_box = layout.box()
            share_col = share_box.column(align=True)
            share_col.scale_y = 1.1

            if tunnel_on:
                share_col.label(text="  ◆  Tunnel Active", icon='KEYINGSET')
                public_url = getattr(props, 'mobile_ar_url', '')
                if public_url and 'trycloudflare' in public_url:
                    share_col.label(
                        text="  " + (public_url[:46] + ('…' if len(public_url) > 46 else '')),
                        icon='LINKED'
                    )
                layout.separator(factor=0.4)
                t_row = layout.row(align=True)
                t_row.scale_y = 1.3
                t_row.operator("webxr.copy_public_url", icon='COPY_ID', text="  Copy Link")
                t_row.operator("webxr.stop_tunnel",     icon='CANCEL',  text="Stop")
            else:
                share_col.label(text="  Works on any network, anywhere.", icon='INFO')
                layout.separator(factor=0.4)
                gen_row = layout.row(align=True)
                gen_row.scale_y = 1.5
                gen_row.operator(
                    "webxr.start_tunnel",
                    icon='WORLD',
                    text="  Generate Public AR Link"
                )
        else:
            layout.separator(factor=1.0)
            hint = layout.box()
            hint_col = hint.column(align=True)
            hint_col.scale_y = 1.1
            hint_col.label(text="  Ready for first deployment.", icon='INFO')
            hint_col.label(text="  Select a mesh and press LAUNCH above.")

        layout.separator(factor=1.2)


# ============================================================================
# ◆  MISSION LOG
# ============================================================================

class WEBXR_PT_deploy_log(Panel):
    """Mission Log — last 10 cloud AR deployments"""
    bl_label      = "Mission Log"
    bl_idname     = "WEBXR_PT_deploy_log"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='PRESET')

    def draw(self, context):
        layout = self.layout
        entries = _read_deploy_log()

        if not entries:
            layout.separator(factor=0.6)
            empty = layout.box()
            ec = empty.column(align=True)
            ec.scale_y = 1.1
            ec.label(text="  No deployments yet.", icon='INFO')
            ec.label(text="  Your AR links will appear here.")
            layout.separator(factor=0.6)
            return

        layout.separator(factor=0.6)
        for entry in entries[:10]:
            ts    = entry.get("ts",    "")
            scene = entry.get("scene", "Unknown")
            url   = entry.get("url",   "")

            box = layout.box()
            col = box.column(align=True)
            col.scale_y = 1.1

            header_row = col.row(align=False)
            header_row.label(text=f"  {scene}", icon='FILE_3D')
            header_row.label(text=ts)

            col.separator(factor=0.3)
            col.label(
                text="  " + (url[:44] + ("…" if len(url) > 44 else "")),
                icon='LINKED'
            )
            col.separator(factor=0.3)

            btn_row = col.row(align=True)
            btn_row.scale_y = 1.3
            op_copy = btn_row.operator("webxr.copy_log_url", icon='COPY_ID', text="Copy")
            op_copy.log_url = url
            op_open = btn_row.operator("webxr.open_log_url", icon='URL',     text="Open")
            op_open.log_url = url

            layout.separator(factor=0.3)

        layout.separator(factor=0.6)


# ============================================================================
# ◆  AR TOOLS
# ============================================================================

class WEBXR_PT_ar_tools(Panel):
    """AR-specific optimization and creative tools"""
    bl_label      = "AR Tools"
    bl_idname     = "WEBXR_PT_ar_tools"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='TOOL_SETTINGS')

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            box = layout.box()
            box.alert = True
            box.label(text="Re-enable The Aura Standard addon.", icon='ERROR')
            return

        layout.separator(factor=0.8)

        # ── Brand & Identity ──────────────────────────────────────────
        _section(layout, "Brand & Identity", 'COMMUNITY')
        brand_box = layout.box()
        brand_col = brand_box.column(align=True)
        brand_col.scale_y = 1.15
        brand_col.prop(props, "show_brand_watermark", toggle=True,
                       text="  Show Watermark on All Viewers")
        sub = brand_col.column(align=True)
        sub.enabled = props.show_brand_watermark
        sub.prop(props, "brand_text", text="Label")
        if props.show_brand_watermark:
            addon_prefs = bpy.context.preferences.addons.get("aura_ar")
            artist_name = addon_prefs.preferences.artist_name.strip() if addon_prefs else ""
            resolved = props.brand_text.strip() or artist_name or "The Aura Standard"
            brand_col.separator(factor=0.4)
            brand_col.label(text=f"  Badge:  '{resolved} via The Aura Standard'", icon='INFO')

        # ── Auto-Rig ─────────────────────────────────────────────────
        _section(layout, "Auto-Rig", 'ARMATURE_DATA')
        rig_box = layout.box()
        rig_col = rig_box.column(align=True)
        rig_col.scale_y = 1.15
        rig_col.prop(props, "auto_rig_on_export", toggle=True,
                     text="  Auto-Rig on Export  (Character Mode)")
        rig_col.separator(factor=0.4)
        rig_col.operator("webxr.auto_rig", icon='ARMATURE_DATA',
                         text="  Auto-Rig Selected Now")

        addons = _addons()
        if addons:
            rig_col.separator(factor=0.4)
            if addons.get("auto_rig_pro"):
                rig_col.label(text="  Auto-Rig Pro detected", icon='CHECKMARK')
            elif addons.get("rigify"):
                rig_col.label(text="  Rigify detected", icon='CHECKMARK')
            else:
                rig_col.label(text="  Fallback: bounding-box armature", icon='INFO')

        # ── Addon Integration ─────────────────────────────────────────
        _section(layout, "Addon Integration", 'PLUGIN')
        addons_box = layout.box()
        addons_col = addons_box.column(align=True)
        addons_col.scale_y = 1.1
        addons_col.operator("webxr.scan_addons", icon='VIEWZOOM',
                            text="  Scan Installed Addons")

        addons = _addons()
        if addons:
            addons_col.separator(factor=0.5)
            grid = addons_col.column(align=True)
            labels = {
                "auto_rig_pro":  ("Auto-Rig Pro",   'ARMATURE_DATA'),
                "rigify":        ("Rigify",          'BONE_DATA'),
                "decal_machine": ("DecalMachine",    'NODE_MATERIAL'),
                "hard_ops":      ("Hard Ops",        'MOD_BOOLEAN'),
                "boxcutter":     ("BoxCutter",       'MOD_BEVEL'),
                "botaniq":       ("Botaniq",         'OUTLINER_OB_CURVES'),
                "retopoflow":    ("RetopoFlow",      'MESH_DATA'),
            }
            for key, (label, icon) in labels.items():
                row = grid.row(align=False)
                row.label(
                    text=f"  {label}",
                    icon='CHECKMARK' if addons.get(key) else 'REMOVE'
                )
            if addons.get("decal_machine"):
                addons_col.separator(factor=0.5)
                addons_col.prop(props, "bake_decals_on_export", toggle=True,
                                text="  Bake Decals on Every Deploy")
                addons_col.operator("webxr.bake_decals", icon='RENDER_STILL',
                                    text="  Bake DecalMachine Decals Now")
            if addons.get("hard_ops") or addons.get("boxcutter"):
                addons_col.prop(props, "apply_hard_ops_mods", toggle=True,
                                text="  Apply Hard Ops Mods on Export")

        # ── Materials ────────────────────────────────────────────────
        _section(layout, "Materials", 'MATERIAL')
        mat_col = layout.column(align=True)
        mat_col.scale_y = 1.2
        mat_col.operator("webxr.material_optimize", icon='MATERIAL',
                         text="  Optimize Materials")

        layout.separator(factor=1.2)


# ============================================================================
# ◆  ADVANCED SETTINGS
# ============================================================================

class WEBXR_PT_advanced_settings(Panel):
    """Advanced export, geometry and rendering settings"""
    bl_label      = "Advanced"
    bl_idname     = "WEBXR_PT_advanced_settings"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='PREFERENCES')

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            box = layout.box()
            box.alert = True
            box.label(text="Re-enable The Aura Standard addon.", icon='ERROR')
            return

        layout.separator(factor=0.8)

        # ── Geometry ─────────────────────────────────────────────────
        _section(layout, "Geometry", 'MOD_SIMPLIFY')
        geo_box = layout.box()
        geo_col = geo_box.column(align=True)
        geo_col.scale_y = 1.15
        geo_col.prop(props, "optimize_mesh", toggle=True,
                     text="  Decimate Mesh on Export")
        sub = geo_col.column(align=True)
        sub.enabled = props.optimize_mesh
        sub.prop(props, "decimate_ratio", slider=True, text="Ratio")

        if props.optimize_mesh:
            total_verts = sum(
                len(o.data.vertices)
                for o in context.scene.objects if o.type == 'MESH'
            )
            estimated = int(total_verts * getattr(props, 'decimate_ratio', 0.7))
            geo_col.separator(factor=0.4)
            geo_col.prop(props, "use_instance_dedup", toggle=True,
                         text="  Auto-Instance Repeated Geometry")
            est_box = geo_box.box()
            est_col = est_box.column(align=True)
            split = est_col.split(factor=0.5)
            split.label(text=f"  Now     {total_verts:,}")
            split.label(text=f"After  ~{estimated:,}")

        # ── Compression ───────────────────────────────────────────────
        _section(layout, "DRACO Compression", 'FORCE_CHARGE')
        draco_box = layout.box()
        draco_col = draco_box.column(align=True)
        draco_col.scale_y = 1.15
        draco_col.prop(props, "use_draco_compression", toggle=True,
                       text="  Enable DRACO  (recommended for architecture)")
        sub = draco_col.column(align=True)
        sub.enabled = getattr(props, 'use_draco_compression', False)
        sub.prop(props, "draco_compression_level", slider=True,
                 text="Level  (0 = fast · 10 = smallest)")

        # ── Export format ──────────────────────────────────────────────
        _section(layout, "Export Format", 'FILE_3D')
        fmt_box = layout.box()
        fmt_col = fmt_box.column(align=True)
        fmt_col.scale_y = 1.15
        fmt_col.prop(props, "export_format", expand=True, text="")
        if getattr(props, 'export_format', 'GLB') == 'FBX':
            fmt_col.separator(factor=0.3)
            fmt_col.label(text="  FBX saved alongside for client delivery.", icon='INFO')

        # ── Texture cap ───────────────────────────────────────────────
        _section(layout, "Texture Resolution", 'TEXTURE')
        tex_box = layout.box()
        tex_col = tex_box.column(align=True)
        tex_col.scale_y = 1.15
        tex_col.prop(props, "texture_quality", expand=False, text="Max Size")
        tex_col.operator("webxr.material_optimize", icon='MATERIAL',
                         text="  Resize Textures Now")

        # ── Lighting ──────────────────────────────────────────────────
        _section(layout, "Lighting", 'LIGHT_SUN')
        light_box = layout.box()
        light_col = light_box.column(align=True)
        light_col.scale_y = 1.15
        light_col.prop(props, "bake_lighting", toggle=True,
                       text="  Bake Lighting into Textures")

        # ── Debug ──────────────────────────────────────────────────────
        _section(layout, "Developer", 'CONSOLE')
        dev_box = layout.box()
        dev_col = dev_box.column(align=True)
        dev_col.scale_y = 1.1
        dev_col.prop(props, "enable_debug", toggle=True, text="  Debug Mode")

        if props.enable_debug:
            dev_col.separator(factor=0.4)
            dev_col.label(text=f"  Blender   {bpy.app.version_string}")
            dev_col.label(text=f"  Objects   {len(context.scene.objects)}")
            dev_col.label(text=f"  Format    {getattr(props, 'export_format', 'GLB')}")
            dev_col.label(text=f"  Decimate  {getattr(props, 'decimate_ratio', 0.7):.0%}")

        layout.separator(factor=1.2)


# ============================================================================
# LEGACY PANELS (backward compatibility — hidden under WebXR tab)
# ============================================================================

class WEBXR_PT_panel(Panel):
    """Main WebXR Export Panel (Legacy)"""
    bl_label      = "1-Click AR Deploy"
    bl_idname     = "WEBXR_PT_main_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "WebXR"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="Properties missing. Re-enable addon.", icon='ERROR')
            return
        layout.label(text="  Use the  AR  tab for the full interface.", icon='INFO')
        layout.separator(factor=0.6)
        row = layout.row()
        row.scale_y = 1.8
        row.operator("webxr.export_model", icon='WORLD', text="  Launch to AR")
        layout.separator()
        layout.label(text=f"  Objects in scene: {len(bpy.context.scene.objects)}")


class WEBXR_PT_settings(Panel):
    """WebXR Settings Panel (Legacy)"""
    bl_label      = "Export Settings"
    bl_idname     = "WEBXR_PT_settings_panel"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "WebXR"
    bl_options    = {'DEFAULT_CLOSED'}
    bl_parent_id  = "WEBXR_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="Properties missing. Re-enable addon.", icon='ERROR')
            return
        col = layout.column(align=True)
        col.scale_y = 1.1
        col.prop(props, "export_format",  text="Format")
        col.prop(props, "texture_quality", text="Textures")
        col.prop(props, "bake_lighting",   text="Bake Lighting")
        col.prop(props, "auto_optimize",   text="Auto-Optimize")
        layout.separator()
        layout.prop(props, "enable_debug", text="Debug Mode")


class WEBXR_PT_quick_access(Panel):
    """Quick-access panel for existing sidebar tabs"""
    bl_label      = "The Aura Standard"
    bl_idname     = "WEBXR_PT_quick_access"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "Item"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.separator(factor=0.6)
        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("webxr.export_model",       icon='WORLD',        text="  Launch to AR")
        col.separator(factor=0.4)
        col.scale_y = 1.2
        col.operator("webxr.check_ar_ready",     icon='VIEWZOOM',     text="  AR Check")
        col.operator("webxr.optimize_ar",        icon='MOD_SIMPLIFY', text="  Optimize")
        layout.separator(factor=0.8)
        layout.label(text="  If the AR tab is missing:", icon='INFO')
        layout.operator("webxr.create_ar_workspace", icon='ADD',
                        text="  Create AR Workspace")
        layout.separator(factor=0.6)


def _read_deploy_log():
    """Load the deployment log JSON; return [] if missing or corrupt."""
    log_path = os.path.join(os.path.expanduser("~"), ".aura_ar_exports", "deploy_log.json")
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ============================================================================
# MAIN AR DASHBOARD
# ============================================================================

class WEBXR_PT_ar_dashboard(Panel):
    """The Aura Standard Command Centre"""
    bl_label      = "THE AURA STANDARD"
    bl_idname     = "WEBXR_PT_ar_dashboard"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"

    def draw_header(self, context):
        self.layout.label(text="", icon='WORLD')

    def draw(self, context):
        layout = self.layout
        scene  = context.scene
        props  = getattr(scene, "webxr_props", None)
        if props is None:
            layout.label(text="Re-enable The Aura Standard addon.", icon='ERROR')
            return

        # ── Cloud-key status badge ────────────────────────────────────
        addon_prefs = context.preferences.addons.get("aura_ar")
        has_key     = bool(addon_prefs and addon_prefs.preferences.aura_api_key.strip())
        artist      = (addon_prefs.preferences.artist_name.strip()
                       if addon_prefs else "")

        status_box = layout.box()
        status_row = status_box.row(align=False)
        if has_key:
            status_row.label(
                text=f"  CLOUD READY  —  {artist or 'Creator'}",
                icon='KEYINGSET'
            )
        else:
            status_row.label(
                text="  LOCAL ONLY  —  Add API Key in Preferences",
                icon='ERROR'
            )

        layout.separator(factor=1.2)

        # ── Deploy button (the hero) ──────────────────────────────────
        col = layout.column()
        col.scale_y = 2.2
        col.operator(
            "webxr.export_model",
            icon='EXPORT',
            text="  LAUNCH TO CLOUD AR",
        )

        layout.separator(factor=0.8)

        # ── Scene intel ───────────────────────────────────────────────
        layout.label(text="SCENE INTEL", icon='OUTLINER_OB_MESH')
        grid = layout.box()
        gc   = grid.column(align=True)

        obj_count   = len(scene.objects)
        mesh_count  = sum(1 for o in scene.objects if o.type == 'MESH')
        total_verts = sum(len(o.data.vertices) for o in scene.objects if o.type == 'MESH')

        gc.label(text=f"Objects  {obj_count}     Meshes  {mesh_count}")
        gc.label(text=f"Vertices  {total_verts:,}")
        if context.selected_objects:
            sel_v = sum(
                len(o.data.vertices)
                for o in context.selected_objects
                if o.type == 'MESH'
            )
            gc.label(text=f"Selected  {sel_v:,}", icon='RESTRICT_SELECT_OFF')

        layout.separator(factor=0.8)

        # ── Scene mode ────────────────────────────────────────────────
        layout.label(text="SCENE MODE", icon='SCENE_DATA')
        mode_box = layout.box()
        mode_col = mode_box.column(align=True)
        mode_col.prop(props, "scene_mode", text="")
        mode_row = mode_col.row(align=True)
        mode_row.operator("webxr.architecture_preset", icon='HOME',       text="Architecture")
        mode_row.operator("webxr.character_preset",    icon='ARMATURE_DATA', text="Character")

        layout.separator(factor=0.8)

        # ── Optimise strip ────────────────────────────────────────────
        layout.label(text="OPTIMISE", icon='MOD_SIMPLIFY')
        opt_row = layout.row(align=True)
        opt_row.operator("webxr.optimize_ar",       icon='MOD_SIMPLIFY',  text="Geometry")
        opt_row.operator("webxr.material_optimize", icon='MATERIAL',      text="Textures")
        opt_row.operator("webxr.check_ar_ready",    icon='VIEWZOOM',      text="Validate")

        # Quick-config inline: decimate ratio + texture res
        cfg_box = layout.box()
        cfg_col = cfg_box.column(align=True)
        cfg_col.label(text="EXPORT SETTINGS", icon='PREFERENCES')
        cfg_row = cfg_col.row(align=True)
        sub = cfg_row.column(align=True)
        sub.enabled = getattr(props, 'optimize_mesh', True)
        sub.prop(props, "decimate_ratio", slider=True, text="Decimate")
        cfg_col.prop(props, "texture_quality", text="Textures")

        layout.separator(factor=0.8)

        # ── Last deployment card ──────────────────────────────────────
        cloud_url = getattr(props, 'cloud_ar_url', '')
        if cloud_url:
            layout.label(text="LAST DEPLOYMENT", icon='CHECKMARK')
            dep_box = layout.box()
            dep_col = dep_box.column(align=True)

            dep_col.label(
                text=cloud_url[:48] + ("…" if len(cloud_url) > 48 else ""),
                icon='LINKED'
            )
            dep_row = dep_col.row(align=True)
            dep_row.scale_y = 1.3
            dep_row.operator("webxr.copy_cloud_url",  icon='COPY_ID', text="Copy Live Link")

            layout.separator(factor=0.6)

        # ── Share section (Cloudflare tunnel) ────────────────────────
        if props.last_viewer_url:
            layout.label(text="SHARE", icon='WORLD')
            share_box = layout.box()
            share_col = share_box.column(align=True)

            from ..operators.cloudflare import _tunnel_proc
            tunnel_on = (_tunnel_proc is not None and _tunnel_proc.poll() is None)

            if tunnel_on:
                share_col.label(text="Tunnel LIVE", icon='KEYINGSET')
                public_url = getattr(props, 'mobile_ar_url', '')
                if public_url and 'trycloudflare' in public_url:
                    share_col.label(
                        text=public_url[:48] + ('...' if len(public_url) > 48 else ''),
                        icon='LINKED'
                    )
                t_row = share_col.row(align=True)
                t_row.operator("webxr.copy_public_url", icon='COPY_ID', text="Copy Link")
                t_row.operator("webxr.stop_tunnel",     icon='CANCEL',  text="Stop")
            else:
                share_col.label(text="No WiFi required. Anyone in the world.", icon='INFO')
                share_col.operator(
                    "webxr.start_tunnel",
                    icon='WORLD',
                    text="Generate Public AR Link"
                )

        else:
            # First-run state
            layout.separator(factor=0.4)
            hint = layout.box()
            hint_col = hint.column(align=True)
            hint_col.label(text="Ready for first deployment.", icon='INFO')
            hint_col.label(text="Press LAUNCH TO CLOUD AR above.")


# ============================================================================
# DEPLOYMENT LOG PANEL
# ============================================================================

class WEBXR_PT_deploy_log(Panel):
    """Deployment Log — last 10 cloud AR links"""
    bl_label      = "MISSION LOG"
    bl_idname     = "WEBXR_PT_deploy_log"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category   = "AR"
    bl_options    = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        self.layout.label(text="", icon='PRESET')

    def draw(self, context):
        layout = self.layout
        entries = _read_deploy_log()

        if not entries:
            empty = layout.box()
            ec = empty.column(align=True)
            ec.label(text="No cloud deployments yet.", icon='INFO')
            ec.label(text="Your deployed AR links will appear here.")
            return

        for entry in entries[:10]:
            ts    = entry.get("ts",    "")
            scene = entry.get("scene", "Unknown")
            url   = entry.get("url",   "")

            box = layout.box()
            col = box.column(align=True)

            title_row = col.row(align=False)
            title_row.label(text=scene, icon='FILE_3D')
            title_row.label(text=ts)

            col.label(
                text=url[:46] + ("\u2026" if len(url) > 46 else ""),
                icon='LINKED'
            )

            btn_row = col.row(align=True)
            btn_row.scale_y = 1.2
            op_copy = btn_row.operator("webxr.copy_log_url", icon='COPY_ID', text="Copy")
            op_copy.log_url = url
            op_open = btn_row.operator("webxr.open_log_url", icon='URL',     text="Open")
            op_open.log_url = url


# ============================================================================
# AR TOOLS PANEL
# ============================================================================

class WEBXR_PT_ar_tools(Panel):
    """AR-specific optimization and preview tools"""
    bl_label = "AR Tools"
    bl_idname = "WEBXR_PT_ar_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AR"
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='TOOL_SETTINGS')

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="WebXR properties missing. Re-enable addon.", icon='ERROR')
            return
        
        # Optimization tools
        layout.label(text="Optimize", icon='MOD_SIMPLIFY')
        col = layout.column(align=True)
        col.prop(props, "auto_optimize", toggle=True)
        col.prop(props, "bake_lighting", toggle=True)

        layout.separator()

        # ── Brand & Identity ──────────────────────────────────────────
        layout.label(text="BRAND & IDENTITY", icon='COMMUNITY')
        brand_box = layout.box()
        brand_col = brand_box.column(align=True)
        brand_col.prop(props, "show_brand_watermark", toggle=True, text="Show Brand Watermark on All Viewers")
        sub = brand_col.column(align=True)
        sub.enabled = props.show_brand_watermark
        sub.prop(props, "brand_text", text="Label Override")
        if props.show_brand_watermark:
            # Show preview of what will appear
            addon_prefs = bpy.context.preferences.addons.get("aura_ar")
            artist_name = addon_prefs.preferences.artist_name.strip() if addon_prefs else ""
            resolved = props.brand_text.strip() or artist_name or "The Aura Standard"
            brand_col.label(text=f"Viewer badge: '{resolved} via The Aura Standard'", icon='INFO')

        layout.separator()

        # ── Auto-Rig ─────────────────────────────────────────────────
        layout.label(text="AUTO-RIG", icon='ARMATURE_DATA')
        rig_box = layout.box()
        rig_col = rig_box.column(align=True)
        rig_col.prop(props, "auto_rig_on_export", toggle=True, text="Auto-Rig on Export (Character Mode)")
        rig_col.operator("webxr.auto_rig", icon='ARMATURE_DATA', text="Auto-Rig Selected Now")
        addons = _addons()
        if addons:
            has_arp = addons.get("auto_rig_pro")
            has_rfy = addons.get("rigify")
            if has_arp:
                rig_col.label(text="Auto-Rig Pro detected — will be used", icon='CHECKMARK')
            elif has_rfy:
                rig_col.label(text="Rigify detected — will be used", icon='CHECKMARK')
            else:
                rig_col.label(text="Fallback: simple bounding-box armature", icon='INFO')

        layout.separator()

        # ── Addon Integration ─────────────────────────────────────────
        layout.label(text="ADDON INTEGRATION", icon='PLUGIN')
        addons_box = layout.box()
        addons_col = addons_box.column(align=True)
        addons_col.operator("webxr.scan_addons", icon='VIEWZOOM', text="Scan Installed Addons")
        addons = _addons()
        if addons:
            grid = addons_col.column(align=True)
            labels = {
                "auto_rig_pro":  ("Auto-Rig Pro",   'ARMATURE_DATA'),
                "rigify":        ("Rigify",          'BONE_DATA'),
                "decal_machine": ("DecalMachine",    'NODE_MATERIAL'),
                "hard_ops":      ("Hard Ops",        'MOD_BOOLEAN'),
                "boxcutter":     ("BoxCutter",       'MOD_BEVEL'),
                "botaniq":       ("Botaniq",         'OUTLINER_OB_CURVES'),
                "retopoflow":    ("RetopoFlow",      'MESH_DATA'),
            }
            for key, (label, icon) in labels.items():
                row = grid.row(align=False)
                if addons.get(key):
                    row.label(text=f"{label}", icon='CHECKMARK')
                else:
                    row.label(text=f"{label}", icon='X')
            # DecalMachine bake shortcut
            if addons.get("decal_machine"):
                addons_col.separator(factor=0.5)
                addons_col.prop(props, "bake_decals_on_export", toggle=True,
                                text="Bake Decals on Every Deploy")
                addons_col.operator("webxr.bake_decals", icon='RENDER_STILL',
                                    text="Bake DecalMachine Decals Now")
            # Hard Ops apply-on-export toggle
            if addons.get("hard_ops") or addons.get("boxcutter"):
                addons_col.prop(props, "apply_hard_ops_mods", toggle=True,
                                text="Apply Hard Ops Mods on Export")

        layout.separator()

        # Material tools
        layout.label(text="Materials", icon='MATERIAL')
        col = layout.column(align=True)
        col.operator("webxr.material_optimize", icon='MATERIAL', text="Optimize Materials")
        
        layout.separator()
        
        # Preview settings
        layout.label(text="Preview", icon='CAMERA_DATA')
        col = layout.column(align=True)
        col.operator("webxr.ar_preview", icon='CAMERA_DATA', text="AR Preview")
        col.operator("webxr.export_preview", icon='RENDER_STILL', text="Generate Preview Image")


# ============================================================================
# ADVANCED SETTINGS PANEL
# ============================================================================

class WEBXR_PT_advanced_settings(Panel):
    """Advanced export and optimization settings"""
    bl_label = "Advanced Settings"
    bl_idname = "WEBXR_PT_advanced_settings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon='PREFERENCES')

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="WebXR properties missing. Re-enable addon.", icon='ERROR')
            return

        # ── Geometry optimisation ─────────────────────────────────────
        layout.label(text="Geometry", icon='MOD_SIMPLIFY')
        col = layout.column(align=True)
        col.prop(props, "optimize_mesh", toggle=True, text="Decimate Mesh on Export")

        sub = col.column(align=True)
        sub.enabled = props.optimize_mesh
        sub.prop(props, "decimate_ratio", slider=True, text="Decimate Ratio")

        # Live estimate: total verts → estimated verts after decimate
        if props.optimize_mesh:
            total_verts = sum(
                len(o.data.vertices)
                for o in context.scene.objects
                if o.type == 'MESH'
            )
            estimated = int(total_verts * getattr(props, 'decimate_ratio', 0.7))
            info_box = col.box()
            info_col = info_box.column(align=True)
            info_col.label(text=f"Current:   {total_verts:,} verts")
            info_col.label(text=f"After:     ~{estimated:,} verts")

        layout.separator()

        # ── Export format ──────────────────────────────────────────────
        layout.label(text="Export Format", icon='FILE_3D')
        col = layout.column(align=True)
        col.prop(props, "export_format", expand=True, text="")
        if getattr(props, 'export_format', 'GLB') == 'FBX':
            warn = col.box()
            warn.label(text="FBX: local viewer uses GLB", icon='INFO')
            warn.label(text="FBX file saved alongside for client delivery.")

        layout.separator()

        # ── DRACO compression ──────────────────────────────────────────
        layout.label(text="DRACO Mesh Compression", icon='FORCE_CHARGE')
        col = layout.column(align=True)
        col.prop(props, "use_draco_compression", toggle=True,
                 text="Enable DRACO (recommended for architecture)")
        sub = col.column(align=True)
        sub.enabled = getattr(props, 'use_draco_compression', False)
        sub.prop(props, "draco_compression_level", slider=True, text="Level (0=fast · 10=smallest)")
        # Instance dedup
        col.prop(props, "use_instance_dedup", toggle=True,
                 text="Auto-Instance Repeated Geometry")

        layout.separator()

        # ── Texture settings ───────────────────────────────────────────
        layout.label(text="Texture Resolution Cap", icon='TEXTURE')
        col = layout.column(align=True)
        col.prop(props, "texture_quality", expand=False, text="Max Size")
        col.operator("webxr.material_optimize", icon='MATERIAL',
                     text="Resize Textures Now")

        layout.separator()

        # ── Lighting ──────────────────────────────────────────────────
        layout.label(text="Lighting", icon='LIGHT_SUN')
        col = layout.column(align=True)
        col.prop(props, "bake_lighting", toggle=True, text="Bake Lighting into Textures")

        layout.separator()

        # ── Debug ──────────────────────────────────────────────────────
        layout.label(text="Development", icon='CONSOLE')
        col = layout.column(align=True)
        col.prop(props, "enable_debug", toggle=True, text="Debug Mode")

        if props.enable_debug:
            layout.separator(factor=0.5)
            debug_box = layout.box()
            debug_box.label(text="Debug Info", icon='INFO')
            debug_col = debug_box.column(align=True)
            debug_col.label(text=f"Blender: {bpy.app.version_string}")
            debug_col.label(text=f"Objects: {len(context.scene.objects)}")
            debug_col.label(text=f"Export format: {getattr(props, 'export_format', 'GLB')}")
            debug_col.label(text=f"Decimate: {getattr(props, 'decimate_ratio', 0.7):.0%}")


# ============================================================================
# LEGACY PANELS (For backward compatibility)
# ============================================================================

class WEBXR_PT_panel(Panel):
    """Main WebXR Export Panel (Legacy)"""
    bl_label = "1-Click AR Deploy"
    bl_idname = "WEBXR_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WebXR"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="Properties missing. Re-enable addon.", icon='ERROR')
            return
        
        layout.label(text="Note: Use 'AR' tab for new interface", icon='INFO')
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("webxr.export_model", icon='EXPORT', text="Deploy to AR")
        
        layout.separator()
        layout.label(text="Quick Info:", icon='INFO')
        layout.label(text=f"Objects in scene: {len(bpy.context.scene.objects)}")


class WEBXR_PT_settings(Panel):
    """WebXR Settings Panel (Legacy)"""
    bl_label = "Export Settings"
    bl_idname = "WEBXR_PT_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WebXR"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "WEBXR_PT_main_panel"

    def draw(self, context):
        layout = self.layout
        props = getattr(context.scene, "webxr_props", None)
        if props is None:
            layout.label(text="Properties missing. Re-enable addon.", icon='ERROR')
            return
        
        layout.prop(props, "export_format", text="Export Format")
        layout.prop(props, "texture_quality", text="Texture Quality")
        layout.prop(props, "bake_lighting", text="Bake Lighting")
        layout.prop(props, "auto_optimize", text="Auto-Optimize")
        
        layout.separator()
        layout.label(text="Advanced:", icon='PREFERENCES')
        layout.prop(props, "enable_debug", text="Debug Mode")


class WEBXR_PT_quick_access(Panel):
    """Quick access WebXR panel for existing sidebar tabs"""
    bl_label = "The Aura Standard Quick Access"
    bl_idname = "WEBXR_PT_quick_access"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.label(text="The Aura Standard Export Tools", icon='EXPORT')
        layout.operator("webxr.export_model", icon='EXPORT', text="Deploy to AR")
        layout.operator("webxr.check_ar_ready", icon='ZOOM_IN', text="AR Check")
        layout.operator("webxr.optimize_ar", icon='MOD_SIMPLIFY', text="Optimize")
        layout.separator()
        layout.operator("webxr.create_ar_workspace", icon='ADD', text="Create AR Workspace")
        layout.label(text="If the AR tab is missing, press this.")
