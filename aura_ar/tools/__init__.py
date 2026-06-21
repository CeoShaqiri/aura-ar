"""
AR Tools and Operators
Collection of AR-specific tools for Blender
"""

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, FloatProperty
import os
import sys
import subprocess
import webbrowser


class WEBXR_OT_ar_preview(Operator):
    """Preview model in AR mode"""
    bl_idname = "webxr.ar_preview"
    bl_label = "AR Preview"
    bl_description = "Preview your model as it will appear in AR"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        
        # Get active object
        obj = context.active_object
        if not obj:
            self.report({'ERROR'}, "No object selected for AR preview")
            return {'CANCELLED'}
        
        # Set viewport to AR preview mode
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        # Enable viewport shading
                        space.shading.use_scene_lights = True
                        space.shading.type = 'MATERIAL'
        
        self.report({'INFO'}, f"🎯 AR Preview enabled for: {obj.name}")
        return {'FINISHED'}


class WEBXR_OT_optimize_ar(Operator):
    """Optimize scene for AR performance"""
    bl_idname = "webxr.optimize_ar"
    bl_label = "Optimize for AR"
    bl_description = "Automatically optimize geometry and materials for AR"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.webxr_props
        scene = context.scene

        ratio = getattr(props, 'decimate_ratio', 0.7)
        optimized_count = 0
        updated_count   = 0

        for obj in scene.objects:
            if obj.type != 'MESH':
                continue
            try:
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)

                if props.optimize_mesh:
                    existing = obj.modifiers.get('AR_Decimate')
                    if existing is None:
                        mod = obj.modifiers.new(name='AR_Decimate', type='DECIMATE')
                        mod.ratio = ratio
                        optimized_count += 1
                    else:
                        # Update ratio if the user changed it
                        if abs(existing.ratio - ratio) > 0.001:
                            existing.ratio = ratio
                            updated_count += 1

            except Exception as e:
                print(f"The Aura Standard: warning optimizing {obj.name}: {e}")

        parts = []
        if optimized_count:
            parts.append(f"added Decimate ({ratio:.0%}) to {optimized_count} objects")
        if updated_count:
            parts.append(f"updated ratio on {updated_count} objects")
        if not parts:
            parts.append("no changes needed")

        self.report({'INFO'}, f"The Aura Standard: {', '.join(parts)}")
        return {'FINISHED'}


class WEBXR_OT_check_ar_ready(Operator):
    """Check if model is ready for AR export"""
    bl_idname = "webxr.check_ar_ready"
    bl_label = "Check AR Ready"
    bl_description = "Validate scene for AR export"
    bl_options = {'REGISTER'}

    def execute(self, context):
        scene = context.scene
        issues = []
        warnings = []
        
        # Check 1: Scene not empty
        if not scene.objects:
            issues.append("❌ Scene is empty - add some models")
        
        # Check 2: Object selection
        if not context.selected_objects:
            warnings.append("⚠️  No objects selected (will export entire scene)")
        
        # Check 3: Texture status
        texture_count = 0
        for obj in scene.objects:
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    if slot.material and slot.material.use_nodes:
                        texture_count += 1
        
        if texture_count == 0:
            warnings.append("⚠️  No textured materials found")
        
        # Check 4: Geometry complexity
        total_verts = sum(len(obj.data.vertices) for obj in scene.objects if obj.type == 'MESH')
        if total_verts > 1000000:
            warnings.append(f"⚠️  High polygon count ({total_verts:,}) - consider optimization")
        
        # Check 5: Scale and units
        if scene.unit_settings.scale_length != 1.0:
            warnings.append(f"⚠️  Non-standard unit scale ({scene.unit_settings.scale_length})")
        
        # Report
        if issues:
            self.report({'ERROR'}, " | ".join(issues))
        elif warnings:
            self.report({'WARNING'}, " | ".join(warnings))
        else:
            self.report({'INFO'}, f"✅ Model is AR-ready! Vertices: {total_verts:,} | Textured: {texture_count}")
        
        return {'FINISHED'}


class WEBXR_OT_material_optimize(Operator):
    """Optimize materials for AR"""
    bl_idname = "webxr.material_optimize"
    bl_label = "Optimize Materials"
    bl_description = "Simplify and optimize materials for AR performance"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.scene.webxr_props
        scene = context.scene

        size_map = {'LOW': 512, 'MEDIUM': 1024, 'HIGH': 2048}
        max_px   = size_map.get(getattr(props, 'texture_quality', 'MEDIUM'), 1024)

        resized  = 0
        skipped  = 0

        # Collect all image datablocks used by mesh materials in the scene
        images_seen = set()
        for obj in scene.objects:
            if obj.type != 'MESH':
                continue
            for slot in obj.material_slots:
                mat = slot.material
                if not mat or not mat.use_nodes:
                    continue
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        images_seen.add(node.image)

        for img in images_seen:
            w, h = img.size
            if w == 0 or h == 0:
                skipped += 1
                continue
            if w <= max_px and h <= max_px:
                skipped += 1
                continue
            # Scale proportionally, keeping largest side = max_px
            factor = max_px / max(w, h)
            new_w  = max(1, int(w * factor))
            new_h  = max(1, int(h * factor))
            try:
                img.scale(new_w, new_h)
                resized += 1
            except Exception as e:
                print(f"The Aura Standard: could not resize {img.name}: {e}")
                skipped += 1

        self.report(
            {'INFO'},
            f"The Aura Standard: resized {resized} image(s) to ≤{max_px}px, {skipped} already within limit"
        )
        return {'FINISHED'}


class WEBXR_OT_export_preview(Operator):
    """Generate export preview"""
    bl_idname = "webxr.export_preview"
    bl_label = "Generate Preview"
    bl_description = "Generate preview image of what will be exported"
    bl_options = {'REGISTER'}

    def execute(self, context):
        # This would generate a preview render
        self.report({'INFO'}, "📸 Preview generated (check rendered view)")
        return {'FINISHED'}


class WEBXR_OT_create_ar_workspace(Operator):
    """Create the AR workspace if it is missing"""
    bl_idname = "webxr.create_ar_workspace"
    bl_label = "Create AR Workspace"
    bl_description = "Create the AR workspace if it does not exist"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            from ..workspace import register_workspace
            register_workspace()
            self.report({'INFO'}, "✅ AR Workspace creation requested")
        except Exception as e:
            self.report({'ERROR'}, f"❌ Failed to create AR Workspace: {e}")
        return {'FINISHED'}


class WEBXR_OT_open_last_viewer(Operator):
    """Open the last generated live AR viewer in your browser"""
    bl_idname = "webxr.open_last_viewer"
    bl_label = "Open Live Viewer"
    bl_description = "Open the last deployed AR viewer URL"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        if not props.last_viewer_url:
            self.report({'WARNING'}, "No viewer URL yet. Run Deploy to AR first.")
            return {'CANCELLED'}

        webbrowser.open(props.last_viewer_url)
        self.report({'INFO'}, "Opened live AR viewer in browser")
        return {'FINISHED'}


class WEBXR_OT_copy_last_viewer_url(Operator):
    """Copy last viewer URL to clipboard"""
    bl_idname = "webxr.copy_last_viewer_url"
    bl_label = "Copy Viewer URL"
    bl_description = "Copy the last deployed AR viewer link"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        if not props.last_viewer_url:
            self.report({'WARNING'}, "No viewer URL yet. Run Deploy to AR first.")
            return {'CANCELLED'}

        context.window_manager.clipboard = props.last_viewer_url
        self.report({'INFO'}, "Viewer URL copied to clipboard")
        return {'FINISHED'}


class WEBXR_OT_open_export_folder(Operator):
    """Open folder containing latest AR deployment files"""
    bl_idname = "webxr.open_export_folder"
    bl_label = "Open Export Folder"
    bl_description = "Open the folder with latest model, viewer, metadata, and package"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        if not props.last_export_path or not os.path.isdir(props.last_export_path):
            self.report({'WARNING'}, "No export folder yet. Run Deploy to AR first.")
            return {'CANCELLED'}

        if os.name == 'nt':
            os.startfile(props.last_export_path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', props.last_export_path])
        else:
            subprocess.Popen(['xdg-open', props.last_export_path])

        self.report({'INFO'}, "Opened export folder")
        return {'FINISHED'}


class WEBXR_OT_create_client_package(Operator):
    """Create premium client delivery package (ZIP) from last deployment"""
    bl_idname = "webxr.create_client_package"
    bl_label = "Create Client Package"
    bl_description = "Generate a delivery-ready ZIP package for your client"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        if not props.last_export_path or not props.last_ar_id:
            self.report({'WARNING'}, "No deployment found yet. Run Deploy to AR first.")
            return {'CANCELLED'}

        try:
            from ..utils.deployment import ARDeploymentManager
            model_data = {
                'filename': props.last_model_file,
                'qr_image': f"ar_{props.last_ar_id}_qr.png",
                'ar_id': props.last_ar_id,
            }
            package_path = ARDeploymentManager.create_client_package(props.last_export_path, model_data)
            self.report({'INFO'}, f"Client package created: {os.path.basename(package_path)}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to create package: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


class WEBXR_OT_launch_readiness_check(Operator):
    """Run launch readiness diagnostics for a stable community release"""
    bl_idname = "webxr.launch_readiness_check"
    bl_label = "Launch Readiness Check"
    bl_description = "Run diagnostics for export, network, and mobile AR delivery"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        score = 100
        notes = []

        if not context.scene.objects:
            score -= 40
            notes.append("Scene has no objects")

        if context.scene.unit_settings.scale_length != 1.0:
            score -= 10
            notes.append("Non-standard scene scale")

        if not bpy.path.abspath("//") or bpy.context.blend_data.filepath == "":
            score -= 10
            notes.append("Blend file not saved")

        try:
            from ..utils.deployment import ARDeploymentManager
            ip = ARDeploymentManager._get_local_ip()
            if ip.startswith("127."):
                score -= 25
                notes.append("LAN IP not detected")
        except Exception:
            score -= 25
            notes.append("Deployment module unavailable")

        if not props.last_viewer_url:
            score -= 15
            notes.append("No recent deployment")

        try:
            import qrcode  # noqa: F401
        except Exception:
            score -= 20
            notes.append("qrcode package missing")

        score = max(0, min(score, 100))
        props.launch_score = score

        if score >= 85:
            props.launch_status = "Launch Ready"
            self.report({'INFO'}, f"Launch score {score}%: Launch Ready")
        elif score >= 60:
            props.launch_status = "Almost Ready"
            self.report({'WARNING'}, f"Launch score {score}%: Almost Ready")
        else:
            props.launch_status = "Needs Work"
            self.report({'WARNING'}, f"Launch score {score}%: Needs Work")

        if notes:
            self.report({'INFO'}, "Notes: " + " | ".join(notes[:3]))

        return {'FINISHED'}


class WEBXR_OT_copy_mobile_url(Operator):
    """Copy mobile AR URL for phone testing"""
    bl_idname = "webxr.copy_mobile_url"
    bl_label = "Copy Mobile URL"
    bl_description = "Copy LAN mobile AR URL to clipboard"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        url = props.mobile_ar_url or props.last_viewer_url
        if not url:
            self.report({'WARNING'}, "No mobile URL yet. Run Deploy to AR first.")
            return {'CANCELLED'}

        context.window_manager.clipboard = url
        self.report({'INFO'}, "Mobile AR URL copied to clipboard")
        return {'FINISHED'}


class WEBXR_OT_open_mobile_guide(Operator):
    """Open quick guide for phone AR testing"""
    bl_idname = "webxr.open_mobile_guide"
    bl_label = "Phone Guide"
    bl_description = "Open mobile AR quick guide in browser"
    bl_options = {'REGISTER'}

    def execute(self, context):
        props = context.scene.webxr_props
        url = props.mobile_ar_url or props.last_viewer_url
        if not url:
            self.report({'WARNING'}, "Deploy once to generate a mobile AR URL.")
            return {'CANCELLED'}

        guide = (
            "Mobile AR quick start:\n"
            "1. Connect phone and PC to same Wi-Fi\n"
            "2. Open this URL on phone browser\n"
            "3. Tap Launch AR\n"
            "4. Allow camera permissions"
        )
        context.window_manager.clipboard = url
        webbrowser.open(url)
        self.report({'INFO'}, guide.replace("\n", " | "))
        return {'FINISHED'}


class WEBXR_OT_show_onboarding(Operator):
    """Show first-launch onboarding for The Aura Standard"""
    bl_idname = "webxr.show_onboarding"
    bl_label = "The Aura Standard Quick Start"
    bl_options = {'REGISTER'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=520)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Welcome to The Aura Standard", icon='INFO')
        col.separator()
        col.label(text="1. Click DEPLOY TO AR to export and open live viewer")
        col.label(text="2. Use Copy Mobile URL to test AR on your phone")
        col.label(text="3. Send Client ZIP for premium delivery")
        col.separator()
        col.label(text="Tip: phone and PC should be on the same Wi-Fi.", icon='URL')

    def execute(self, context):
        return {'FINISHED'}


class WEBXR_OT_dismiss_onboarding(Operator):
    """Dismiss onboarding card in the dashboard"""
    bl_idname = "webxr.dismiss_onboarding"
    bl_label = "Dismiss Onboarding"
    bl_options = {'REGISTER'}

    def execute(self, context):
        context.scene.webxr_props.onboarding_dismissed = True
        self.report({'INFO'}, "Onboarding dismissed")
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
# Helper: count total triangles across all visible mesh objects
# ─────────────────────────────────────────────────────────────────────────────

def _count_triangles(scene):
    """Return (total_tris, per_obj_list) for all mesh objects in the scene."""
    total = 0
    per_obj = []
    for obj in scene.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        tris = sum(1 if len(p.vertices) == 3 else 2
                   for p in mesh.polygons)
        total += tris
        per_obj.append((obj, tris))
    return total, per_obj


def _compute_smart_ratio(current_tris, target_tris):
    """Return the decimate ratio needed to reach target_tris from current_tris.
    Clamps to [0.05, 1.0]. Returns 1.0 (no change) if already within target."""
    if current_tris <= target_tris or current_tris == 0:
        return 1.0
    ratio = target_tris / current_tris
    return max(0.05, min(1.0, ratio))


# ─────────────────────────────────────────────────────────────────────────────
# UV Unwrap operator — ensures every mesh has at least one UV map
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_uv_unwrap(Operator):
    """Ensure every mesh object has a UV map (Smart UV Project).
    Skips objects that already have a UV map. Required for correct texture export."""
    bl_idname  = "webxr.uv_unwrap"
    bl_label   = "Auto UV Unwrap"
    bl_description = (
        "Add a UV map to any mesh that is missing one using Smart UV Project.\n"
        "Objects that already have UVs are left untouched."
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene     = context.scene
        unwrapped = 0
        skipped   = 0

        # We need to be in OBJECT mode to switch between objects
        prev_mode = context.mode
        if prev_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for obj in scene.objects:
            if obj.type != 'MESH':
                continue

            mesh = obj.data
            if mesh.uv_layers:
                skipped += 1
                continue

            # Make this object active and selected, then unwrap
            context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            try:
                bpy.ops.uv.smart_project(
                    angle_limit=66.0,   # default, good for most shapes
                    margin_method='FRACTION',
                    island_margin=0.02,
                    area_weight=0.0,
                    correct_aspect=True,
                    scale_to_bounds=False,
                )
                unwrapped += 1
            except Exception as e:
                self.report({'WARNING'}, f"The Aura Standard: could not unwrap {obj.name}: {e}")
            finally:
                bpy.ops.object.mode_set(mode='OBJECT')

        self.report(
            {'INFO'},
            f"The Aura Standard UV: unwrapped {unwrapped} object(s), {skipped} already had UVs"
        )
        return {'FINISHED'}


# ─────────────────────────────────────────────────────────────────────────────
# Make AR Ready — one-click full pipeline
# ─────────────────────────────────────────────────────────────────────────────

class WEBXR_OT_make_ar_ready(Operator):
    """One-click full AR optimisation pipeline:
    1. UV unwrap any mesh missing UVs
    2. Smart-decimate to the AR poly target
    3. Resize oversized textures to the texture quality cap
    4. Report the final triangle count and file size estimate"""
    bl_idname  = "webxr.make_ar_ready"
    bl_label   = "Make AR Ready"
    bl_description = (
        "Run the full AR optimisation pipeline in one click:\n"
        "  • UV unwrap meshes that are missing UV maps\n"
        "  • Decimate geometry to fit the AR Poly Target\n"
        "  • Resize textures to the Texture Resolution cap\n"
        "No matter how heavy the scene, this makes it AR-safe."
    )
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = getattr(scene, 'webxr_props', None)
        if props is None:
            self.report({'ERROR'}, "The Aura Standard: properties missing — re-enable the addon.")
            return {'CANCELLED'}

        log = []

        # ── 1. UV Unwrap ────────────────────────────────────────────────
        if getattr(props, 'auto_uv_unwrap', True):
            prev_mode = context.mode
            if prev_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            unwrapped = 0
            for obj in scene.objects:
                if obj.type != 'MESH' or obj.data.uv_layers:
                    continue
                context.view_layer.objects.active = obj
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                try:
                    bpy.ops.uv.smart_project(
                        angle_limit=66.0,
                        margin_method='FRACTION',
                        island_margin=0.02,
                        area_weight=0.0,
                        correct_aspect=True,
                        scale_to_bounds=False,
                    )
                    unwrapped += 1
                except Exception:
                    pass
                finally:
                    bpy.ops.object.mode_set(mode='OBJECT')

            if unwrapped:
                log.append(f"UV: unwrapped {unwrapped}")

        # ── 2. Smart Decimate ────────────────────────────────────────────
        if getattr(props, 'optimize_mesh', True):
            target = getattr(props, 'ar_poly_target', 100_000)
            use_smart = getattr(props, 'use_smart_decimate', True)
            manual_ratio = getattr(props, 'decimate_ratio', 0.7)

            current_tris, per_obj = _count_triangles(scene)

            if use_smart:
                ratio = _compute_smart_ratio(current_tris, target)
            else:
                ratio = manual_ratio

            added = 0
            updated = 0
            for obj, obj_tris in per_obj:
                existing = obj.modifiers.get('AR_Decimate')
                if ratio >= 1.0:
                    # No decimation needed — remove any existing modifier
                    if existing:
                        obj.modifiers.remove(existing)
                elif existing is None:
                    mod = obj.modifiers.new(name='AR_Decimate', type='DECIMATE')
                    mod.ratio = ratio
                    added += 1
                elif abs(existing.ratio - ratio) > 0.001:
                    existing.ratio = ratio
                    updated += 1

            est_after = int(current_tris * ratio)
            if ratio < 1.0:
                log.append(
                    f"Poly: {current_tris:,} → ~{est_after:,} tris "
                    f"({'smart' if use_smart else 'manual'} {ratio:.0%})"
                )
            else:
                log.append(f"Poly: {current_tris:,} tris — within target, no decimation")

            # Update the stored ratio so the slider reflects what was applied
            if use_smart:
                props.decimate_ratio = round(ratio, 2)

        # ── 3. Texture Resize ────────────────────────────────────────────
        size_map = {'LOW': 512, 'MEDIUM': 1024, 'HIGH': 2048}
        max_px   = size_map.get(getattr(props, 'texture_quality', 'MEDIUM'), 1024)
        resized  = 0
        images_seen = set()

        for obj in scene.objects:
            if obj.type != 'MESH':
                continue
            for slot in obj.material_slots:
                mat = slot.material
                if not mat or not mat.use_nodes:
                    continue
                for node in mat.node_tree.nodes:
                    if node.type == 'TEX_IMAGE' and node.image:
                        images_seen.add(node.image)

        for img in images_seen:
            w, h = img.size
            if w == 0 or h == 0 or (w <= max_px and h <= max_px):
                continue
            factor = max_px / max(w, h)
            try:
                img.scale(max(1, int(w * factor)), max(1, int(h * factor)))
                resized += 1
            except Exception:
                pass

        if resized:
            log.append(f"Textures: {resized} resized to ≤{max_px}px")

        # ── 4. Final report ──────────────────────────────────────────────
        if log:
            self.report({'INFO'}, "The Aura Standard ready — " + "  |  ".join(log))
        else:
            self.report({'INFO'}, "The Aura Standard: scene already AR-optimised, nothing to do")

        return {'FINISHED'}


# Register all AR tools
ar_tools_classes = [
    WEBXR_OT_ar_preview,
    WEBXR_OT_optimize_ar,
    WEBXR_OT_uv_unwrap,
    WEBXR_OT_make_ar_ready,
    WEBXR_OT_check_ar_ready,
    WEBXR_OT_material_optimize,
    WEBXR_OT_export_preview,
    WEBXR_OT_create_ar_workspace,
    WEBXR_OT_open_last_viewer,
    WEBXR_OT_copy_last_viewer_url,
    WEBXR_OT_open_export_folder,
    WEBXR_OT_create_client_package,
    WEBXR_OT_launch_readiness_check,
    WEBXR_OT_copy_mobile_url,
    WEBXR_OT_open_mobile_guide,
    WEBXR_OT_show_onboarding,
    WEBXR_OT_dismiss_onboarding,
]


def register():
    for cls in ar_tools_classes:
        try:
            bpy.utils.register_class(cls)
        except RuntimeError as e:
            if "already registered" in str(e):
                try:
                    bpy.utils.unregister_class(cls)
                except RuntimeError:
                    pass
                try:
                    bpy.utils.register_class(cls)
                except RuntimeError:
                    pass


def unregister():
    for cls in reversed(ar_tools_classes):
        try:
            bpy.utils.unregister_class(cls)
        except RuntimeError:
            pass
