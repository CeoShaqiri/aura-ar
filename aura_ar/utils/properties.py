import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, EnumProperty, StringProperty


class WebXRProperties(bpy.types.PropertyGroup):
    """WebXR addon properties"""

    export_quality: IntProperty(
        name="Export Quality",
        description="Quality of the exported model (1-100)",
        default=85, min=1, max=100, subtype='PERCENTAGE'
    )

    optimize_mesh: BoolProperty(
        name="Optimize Mesh",
        description="Add Decimate modifier to all mesh objects before export",
        default=True
    )

    decimate_ratio: FloatProperty(
        name="Decimate Ratio",
        description="Target ratio of polygons to keep (0.1 = 10%, 1.0 = no decimation). "
                    "Applied when Optimize Mesh is enabled and Smart Target is OFF",
        default=0.7,
        min=0.05,
        max=1.0,
        step=5,
        precision=2,
    )

    use_smart_decimate: BoolProperty(
        name="Smart Poly Target",
        description="Automatically calculate the decimate ratio to hit the AR Poly Target — "
                    "ignores the manual Decimate Ratio. Recommended: ON",
        default=True,
    )

    ar_poly_target: IntProperty(
        name="AR Poly Target",
        description="Maximum triangle count for AR. Aura will auto-calculate the decimate ratio "
                    "to stay at or below this limit. 100k = safe for any mobile device.",
        default=100_000,
        min=10_000,
        max=2_000_000,
        step=10000,
    )

    auto_uv_unwrap: BoolProperty(
        name="Auto UV Unwrap",
        description="Automatically add a UV map (Smart UV Project) to any mesh that lacks one. "
                    "Required for correct texture baking and export",
        default=True,
    )

    export_format: EnumProperty(
        name="Export Format",
        description="Format to export",
        items=[
            ('GLTF', 'glTF 2.0 (.gltf)', 'Export as separate glTF + bin files'),
            ('GLB',  'glTF Binary (.glb)', 'Export as single self-contained GLB — recommended for AR'),
            ('FBX',  'FBX (.fbx)',         'Export as FBX — not natively supported by WebXR, use for client delivery only'),
        ],
        default='GLB'
    )

    texture_quality: EnumProperty(
        name="Texture Resolution",
        description="Maximum texture dimension. Images larger than this are resized before export.",
        items=[
            ('LOW',    'Low  — 512 px',   'Mobile-optimised, smallest file'),
            ('MEDIUM', 'Medium — 1024 px', 'Default, good balance for AR'),
            ('HIGH',   'High — 2048 px',  'Sharp on tablets and large screens'),
        ],
        default='MEDIUM'
    )

    bake_lighting: BoolProperty(
        name="Bake Lighting",
        description="Bake scene lighting into textures",
        default=False
    )

    auto_optimize: BoolProperty(
        name="Auto Optimize",
        description="Automatically optimize scene for AR performance",
        default=True
    )

    enable_debug: BoolProperty(
        name="Enable Debug Mode",
        description="Show debug information in console",
        default=False
    )

    # ── Deployment state ──────────────────────────────────────
    last_viewer_url: StringProperty(
        name="Last Viewer URL",
        description="Local viewer URL for the current session",
        default=""
    )

    last_export_path: StringProperty(
        name="Last Export Path",
        description="Last export directory path",
        default=""
    )

    last_model_file: StringProperty(
        name="Last Model File",
        description="Filename of the last exported GLB (with cache-busting param)",
        default=""
    )

    last_ar_id: StringProperty(
        name="Last AR Session ID",
        description="Unique ID for the current deployment session",
        default=""
    )

    last_blend_path: StringProperty(
        name="Last Blend Path",
        description="Blend file path at time of last export — used to detect file change",
        default=""
    )

    mobile_ar_url: StringProperty(
        name="Mobile / Public AR URL",
        description="LAN or Cloudflare URL for mobile devices",
        default=""
    )

    cloud_ar_url: StringProperty(
        name="Cloud AR URL",
        description="Live public URL on ceo-of-aura.cloud after cloud deploy",
        default=""
    )

    # ── Launch readiness ──────────────────────────────────────
    launch_score: IntProperty(
        name="Launch Score",
        description="Readiness score for community release",
        default=0, min=0, max=100, subtype='PERCENTAGE'
    )

    launch_status: StringProperty(
        name="Launch Status",
        description="Summary of latest launch readiness check",
        default="Not checked"
    )

    edition_tier: EnumProperty(
        name="Edition",
        description="Feature tier for The Aura Standard",
        items=[
            ('FREE',   'Free',   'Core export, preview, and basic AR link tools'),
            ('PRO',    'Pro',    'Includes premium delivery workflow and diagnostics'),
            ('STUDIO', 'Studio', 'Includes all pro features with studio-style workflow defaults'),
        ],
        default='PRO'
    )

    onboarding_dismissed: BoolProperty(
        name="Onboarding Dismissed",
        description="Hide onboarding once the user has completed first steps",
        default=False
    )

    # ── Scene mode ────────────────────────────────────────
    scene_mode: EnumProperty(
        name="Scene Mode",
        description=(
            "Preset that tunes poly target, DRACO compression and instancing "
            "for the type of scene you are deploying"
        ),
        items=[
            ('STANDARD',     'Standard',      'Default 100 k poly target — props, products, heroes'),
            ('ARCHITECTURE', 'Architecture',  'Large / full-building scenes: 500 k polys, DRACO on, instancing on'),
            ('CHARACTER',    'Character',     'Rigged character — higher quality, auto-rig check'),
        ],
        default='STANDARD',
    )

    # ── DRACO mesh compression ────────────────────────────
    use_draco_compression: BoolProperty(
        name="DRACO Mesh Compression",
        description=(
            "Compress mesh geometry with Google DRACO — dramatically reduces GLB "
            "file size for complex / architectural scenes. Supported by all modern AR viewers."
        ),
        default=False,
    )

    draco_compression_level: IntProperty(
        name="DRACO Level",
        description="0 = fastest / largest  →  10 = slowest / smallest",
        default=6, min=0, max=10,
    )

    # ── Instance deduplication ────────────────────────────
    use_instance_dedup: BoolProperty(
        name="Auto-Instance Repeated Objects",
        description=(
            "Detect objects that share the same mesh data (linked duplicates, scatter objects, "
            "windows, columns, furniture…) and export them as GPU instances instead of "
            "copying the mesh — can reduce GLB size by 80 %+ for architectural scenes"
        ),
        default=True,
    )

    # ── Auto-rigging ──────────────────────────────────────
    auto_rig_on_export: BoolProperty(
        name="Auto-Rig on Export",
        description=(
            "Before export, automatically generate a skeleton for any unrigged mesh. "
            "Uses Auto-Rig Pro if installed, otherwise Rigify (built-in). "
            "Only applies in Character mode."
        ),
        default=False,
    )

    # ── Brand watermark ───────────────────────────────────
    show_brand_watermark: BoolProperty(
        name="Brand Watermark",
        description=(
            "Display your studio / artist name as a permanent watermark on every AR viewer "
            "and every screenshot taken through the viewer. Cannot be removed by viewers."
        ),
        default=True,
    )

    brand_text: StringProperty(
        name="Brand Label",
        description=(
            "Text shown in the watermark. Leave empty to use the Artist / Studio Name "
            "set in Add-ons Preferences."
        ),
        default="",
    )

    # ── Addon integration ─────────────────────────────────
    bake_decals_on_export: BoolProperty(
        name="Bake DecalMachine Decals",
        description=(
            "If DecalMachine is installed, bake all decals into the base texture "
            "before GLB export so they appear correctly in every AR viewer"
        ),
        default=False,
    )

    apply_hard_ops_mods: BoolProperty(
        name="Apply Hard Ops Modifiers",
        description=(
            "If Hard Ops / BoxCutter is installed, apply all booleans and modifiers "
            "to a temporary export copy before sending to AR — ensures clean geometry"
        ),
        default=True,
    )


def register_properties():
    """Register custom properties"""
    try:
        bpy.utils.register_class(WebXRProperties)
    except RuntimeError:
        pass

    if not hasattr(bpy.types.Scene, 'webxr_props'):
        bpy.types.Scene.webxr_props = bpy.props.PointerProperty(
            type=WebXRProperties
        )


def unregister_properties():
    """Unregister custom properties"""
    if hasattr(bpy.types.Scene, 'webxr_props'):
        del bpy.types.Scene.webxr_props

    try:
        bpy.utils.unregister_class(WebXRProperties)
    except RuntimeError:
        pass
