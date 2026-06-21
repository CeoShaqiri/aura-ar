"""
Blender Version Compatibility Checker
Ensures addon works on all versions 4.0+
"""

import bpy


class VersionChecker:
    """Check Blender version compatibility"""
    
    MINIMUM_VERSION = (4, 0, 0)
    RECOMMENDED_VERSION = (4, 1, 0)
    
    @staticmethod
    def get_blender_version():
        """Get current Blender version as tuple"""
        return bpy.app.version
    
    @staticmethod
    def get_blender_version_string():
        """Get human-readable Blender version"""
        return bpy.app.version_string
    
    @staticmethod
    def check_compatibility():
        """Check if current Blender version is compatible
        
        Returns:
            tuple: (is_compatible: bool, status: str, version_info: dict)
        """
        current = bpy.app.version
        minimum = VersionChecker.MINIMUM_VERSION
        
        # Check if version is >= 4.0.0
        if current >= minimum:
            is_compatible = True
            
            # Determine status
            if current >= (5, 0, 0):
                status = "✅ Compatible (Blender 5.x+)"
            elif current >= VersionChecker.RECOMMENDED_VERSION:
                status = "✅ Compatible & Recommended (Blender 4.1+)"
            elif current >= minimum:
                status = "✅ Compatible (Blender 4.0.x)"
            else:
                status = "❌ Not Compatible"
                is_compatible = False
        else:
            is_compatible = False
            status = f"❌ Version too old (requires 4.0.0, you have {bpy.app.version_string})"
        
        version_info = {
            'current': bpy.app.version_string,
            'current_tuple': current,
            'minimum': f"{minimum[0]}.{minimum[1]}.{minimum[2]}",
            'recommended': f"{VersionChecker.RECOMMENDED_VERSION[0]}.{VersionChecker.RECOMMENDED_VERSION[1]}.{VersionChecker.RECOMMENDED_VERSION[2]}",
            'is_compatible': is_compatible,
            'status': status
        }
        
        return is_compatible, status, version_info
    
    @staticmethod
    def print_version_info():
        """Print version info to console"""
        is_compatible, status, info = VersionChecker.check_compatibility()
        
        print("\n" + "="*60)
        print("BLENDER VERSION CHECK")
        print("="*60)
        print(f"Current Version: {info['current']}")
        print(f"Minimum Required: Blender {info['minimum']}")
        print(f"Recommended: Blender {info['recommended']}+")
        print(f"Status: {status}")
        print("="*60 + "\n")
        
        return is_compatible


def check_and_report():
    """Check compatibility on addon load"""
    is_compatible, status, info = VersionChecker.check_compatibility()
    
    if is_compatible:
        print(f"✅ WebXR Addon: {status}")
        return True
    else:
        print(f"❌ WebXR Addon: {status}")
        print(f"   Please upgrade to Blender 4.0.0 or newer")
        return False
