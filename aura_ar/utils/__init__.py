from .logger import get_logger
from .properties import register_properties, unregister_properties
from .compatibility import VersionChecker, check_and_report

try:
    from .export_handler import export_webxr, WebXRExportHandler
except Exception as _e:
    print(f"❌ [The Aura Standard] Failed to load export_handler: {_e}")
    export_webxr = None
    WebXRExportHandler = None

try:
    from .deployment import ARDeploymentManager
except Exception as _e:
    print(f"❌ [The Aura Standard] Failed to load deployment: {_e}")
    ARDeploymentManager = None

__all__ = [
    'get_logger',
    'register_properties',
    'unregister_properties',
    'VersionChecker',
    'check_and_report',
    'export_webxr',
    'WebXRExportHandler',
    'ARDeploymentManager'
]
