"""
Export Handler - Session-Optimized for The Aura Standard
Ensures unique file paths to prevent cross-session caching.
"""

import os
from datetime import datetime
import bpy  # type: ignore

class WebXRExportHandler:
    """Handles unique timestamped glTF/GLB exports."""
    
    @staticmethod
    def get_export_path():
        """Creates a unique subfolder for this specific export session."""
        # Use a high-resolution timestamp to ensure uniqueness
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generates: //exports/session_20260419_233045/
        export_dir = bpy.path.abspath(f"//exports/session_{session_id}")
        
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
        
        return export_dir
    
    @staticmethod
    def get_filename(format_type):
        """Generates a filename with current scene name and time."""
        timestamp = datetime.now().strftime("%H%M%S")
        scene_name = bpy.context.scene.name.replace(" ", "_") or "Model"
        
        extension = ".glb" if format_type == "GLB" else ".gltf" if format_type == "GLTF" else ".fbx"
        return f"{scene_name}_{timestamp}{extension}"
    
    @staticmethod
    def export_to_glb(context, filepath, quality=85, optimize=True):
        """Standard AR-optimized export logic."""
        props = context.scene.webxr_props
        
        try:
            # Select all objects to ensure nothing is missed in the new session
            bpy.ops.object.select_all(action='SELECT')
            
            if optimize and props.optimize_mesh:
                WebXRExportHandler._apply_optimization(context)
            
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format='GLB2',
                use_selection=False,
                export_apply=True,
                export_draco_mesh_compression_level=16 if quality > 70 else 12,
                export_animations=True,
                export_skins=True,
                export_morph=True
            )
            return True, filepath
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _apply_optimization(context):
        """Non-destructive decimation for mobile AR performance."""
        for obj in context.scene.objects:
            if obj.type == 'MESH':
                if not obj.modifiers.get('AR_Optimize'):
                    context.view_layer.objects.active = obj
                    decimate = obj.modifiers.new(name='AR_Optimize', type='DECIMATE')
                    # PRO TIER: Higher quality decimation
                    decimate.ratio = 0.75 

def export_webxr(scene):
    """Primary entry point for the Aura AR Deploy operator."""
    props = scene.webxr_props
    handler = WebXRExportHandler()
    
    export_dir = handler.get_export_path()
    filename = handler.get_filename(props.export_format)
    filepath = os.path.join(export_dir, filename)
    
    if props.export_format in ['GLB', 'GLTF']:
        success, result = handler.export_to_glb(
            bpy.context,
            filepath,
            quality=props.export_quality,
            optimize=props.optimize_mesh
        )
    else:
        success = bpy.ops.export_scene.fbx(filepath=filepath) == {'FINISHED'}
        result = filepath if success else "FBX Export Failed"
    
    return success, result, filepath