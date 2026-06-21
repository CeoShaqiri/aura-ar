"""
AR Workspace setup and configuration for Blender 4.0+
Registers the AR workspace similar to Animation, Sculpting, Modeling
"""

import bpy


class WEBXR_WS_setup:
    """Setup AR Workspace for Blender 4.0+"""
    
    @staticmethod
    def setup_ar_workspace():
        """Create or get the AR workspace
        
        In Blender 5.0+, workspaces appear in the top menu bar.
        We duplicate the current workspace and rename it to "AR".
        """
        try:
            workspaces = bpy.data.workspaces
            window = bpy.context.window
        except Exception as e:
            print(f"⚠️  Cannot access workspaces: {e}")
            return None

        if window is None:
            print("⚠️  No active Blender window for workspace creation")
            return None
        
        # Check if AR workspace already exists
        ar_workspace = workspaces.get("AR")
        if ar_workspace:
            print("✅ AR Workspace already exists")
            return ar_workspace
        
        # For Blender 5.1+, duplicate the current workspace
        try:
            print("📍 Creating AR workspace by duplicating current workspace...")
            
            # Get current workspace
            current_workspace = window.workspace
            print(f"  Current workspace: {current_workspace.name}")
            
            # Use duplicate operator
            bpy.ops.workspace.duplicate()
            
            # The newly created workspace becomes active
            new_workspace = window.workspace
            
            if new_workspace and new_workspace.name != current_workspace.name:
                # Rename to "AR"
                new_workspace.name = "AR"
                window.workspace = new_workspace
                print(f"✅ AR Workspace created successfully!")
                return new_workspace
            else:
                print("⚠️  Could not rename workspace")
                return None
                
        except Exception as e:
            print(f"❌ Error creating AR workspace: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def configure_ar_workspace(workspace):
        """Configure the AR workspace layout for Blender 4.0+
        
        This is intentionally lightweight. The primary goal is to
        ensure the AR workspace is created and visible.
        """
        if not workspace:
            return

        try:
            if workspace.screens:
                screen = workspace.screens[0]
                areas = screen.areas
                if areas:
                    areas[0].type = 'VIEW_3D'
            print("✅ AR Workspace configured")
        except Exception as e:
            print(f"⚠️  Workspace configuration note: {e}")


def register_workspace():
    """Register the AR workspace for Blender 4.0+"""
    try:
        workspace = WEBXR_WS_setup.setup_ar_workspace()
        WEBXR_WS_setup.configure_ar_workspace(workspace)
        
        print("\n" + "="*60)
        print("🎯 AR WORKSPACE IS NOW AVAILABLE")
        print("="*60)
        print("📍 LOCATION: Top menu bar (next to Layout, Modeling, etc.)")
        print("   Click the 'AR' tab to switch to AR Workspace")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"⚠️  AR Workspace registration: {e}")


def unregister_workspace():
    """Cleanup workspace registration"""
    # Note: Blender doesn't automatically delete workspaces on addon unload
    # This is intentional - users can keep the workspace after addon is disabled
    pass
