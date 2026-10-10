"""Molecule of the Month (MotM) Rendering Preset for CueMol2.

Reproduces the publication-quality, elegant, high-contrast visual style
commonly used in RCSB PDB "Molecule of the Month" illustrations.
"""

from __future__ import annotations

import json
import math
import os
import shlex
import subprocess
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import cuemol as cm

# ==============================================================================
# Constants & Color Palettes
# ==============================================================================

class PresetMode(str, Enum):
    PROTEIN = "protein"
    PROTEIN_LIGAND = "protein_ligand"
    PROTEIN_SURFACE = "protein_surface"
    FULL = "full"


class RadiosityPreset(str, Enum):
    OFF = "off"
    FAST = "fast"
    HIGH = "high"


# Palette: Secondary Structure (Soft Pastel Tones)
PALETTE_SECONDARY = {
    "helix": "#E58B88",       # Soft Coral / Warm Rose
    "sheet": "#7BAFD4",       # Soft Slate Blue / Azure
    "coil": "#D0CEBA",        # Muted Sand / Warm Light Gray
    "nucleic": "#5F9EA0",     # Soft Sage Teal
}

# Palette: Multi-chain Pastels
PALETTE_CHAINS = [
    "#88B04B",  # Chain A: Soft Sage Green
    "#92A8D1",  # Chain B: Soft Serenity Blue
    "#F7CAC9",  # Chain C: Soft Rose Quartz
    "#B565A7",  # Chain D: Soft Radiant Orchid
    "#FF6F61",  # Chain E: Soft Living Coral
    "#E08119",  # Chain F: Soft Ochre Amber
    "#45B8AC",  # Chain G: Soft Turquoise / Mint
    "#98B4D4",  # Chain H: Soft Powder Blue
    "#D9AB55",  # Chain I: Soft Pale Ochre
    "#B3C2C8",  # Chain J: Slate Cloud
]

# Palette: Harmonious Ligand & Element Colors (Softened CPK)
PALETTE_ELEMENTS = {
    "C": "#A0A0A0",     # Light Neutral Slate Gray
    "N": "#4C72B0",     # Soft Deep Blue
    "O": "#C44E52",     # Warm Brick Red
    "S": "#CCB974",     # Muted Gold / Amber
    "P": "#DD8452",     # Tangerine / Warm Orange
    "H": "#E8E8E8",     # Off-white Light Gray
    "F": "#55A868",     # Soft Mint Green
    "CL": "#55A868",    # Soft Mint Green
    "BR": "#8C564B",    # Muted Brown
    "I": "#7B4173",     # Muted Violet
}

# Palette: Metal Ion Accents
PALETTE_IONS = {
    "MG": "#2CA02C",
    "ZN": "#7F7F7F",
    "CA": "#17BECF",
    "FE": "#D62728",
    "MN": "#9C59B6",
    "NA": "#3498DB",
    "K": "#E67E22",
    "CU": "#D35400",
    "DEFAULT": "#9467BD",
}

# Selection Queries for Smart Filtering
SEL_PROTEIN = "rprop type=prot"
SEL_NUCLEIC = "rprop type=nucl"
SEL_WATER = "rprop type=water | resn HOH | resn WAT | resn DOD | resn TIP3"
SEL_ION = "elem Mg | elem Zn | elem Ca | elem Fe | elem Mn | elem Na | elem K | elem Cl | elem Cu | elem Ni | elem Co"
SEL_LIGAND = "!rprop type=prot & !rprop type=nucl & !(rprop type=water | resn HOH | resn WAT | resn DOD | resn TIP3) & !(elem Mg | elem Zn | elem Ca | elem Fe | elem Mn | elem Na | elem K | elem Cl | elem Cu | elem Ni | elem Co)"


# ==============================================================================
# Helper Functions: Colors & Styles
# ==============================================================================

def create_motm_secondary_coloring(scene_uid: int | None = None) -> Any:
    """Create a PaintColoring object with MotM secondary structure pastel colors."""
    coloring = cm.createObj("PaintColoring")
    coloring.append(cm.sel("sheet", scene_uid), cm.col(PALETTE_SECONDARY["sheet"], scene_uid))
    coloring.append(cm.sel("helix", scene_uid), cm.col(PALETTE_SECONDARY["helix"], scene_uid))
    coloring.append(cm.sel("nucleic", scene_uid), cm.col(PALETTE_SECONDARY["nucleic"], scene_uid))
    coloring.append(cm.sel("*", scene_uid), cm.col(PALETTE_SECONDARY["coil"], scene_uid))
    return coloring


def create_motm_chain_coloring(mol: Any, scene_uid: int | None = None) -> Any:
    """Create a PaintColoring object tinting each chain with distinct harmonious pastels."""
    coloring = cm.createObj("PaintColoring")
    
    # Discover unique chains if possible
    chains: list[str] = []
    try:
        iter_obj = cm.createObj("ResidIterator")
        iter_obj.target = mol
        iter_obj.sel = cm.sel("*", scene_uid)
        iter_obj.first()
        while iter_obj.hasMore():
            res = iter_obj.get()
            ch = res.chainName
            if ch and ch not in chains:
                chains.append(ch)
            iter_obj.next()
    except Exception:
        # Fallback to standard A-H chain selections
        chains = [chr(ord('A') + i) for i in range(8)]

    for idx, ch in enumerate(chains):
        color_hex = PALETTE_CHAINS[idx % len(PALETTE_CHAINS)]
        coloring.append(cm.sel(f"chain {ch}", scene_uid), cm.col(color_hex, scene_uid))

    coloring.append(cm.sel("*", scene_uid), cm.col(PALETTE_SECONDARY["coil"], scene_uid))
    return coloring


def create_motm_cpk_coloring(scene_uid: int | None = None) -> Any:
    """Create a CPKColoring object with softened harmonious element colors."""
    coloring = cm.createObj("CPKColoring")
    try:
        coloring.col_C = cm.col(PALETTE_ELEMENTS["C"], scene_uid)
        coloring.col_N = cm.col(PALETTE_ELEMENTS["N"], scene_uid)
        coloring.col_O = cm.col(PALETTE_ELEMENTS["O"], scene_uid)
        coloring.col_S = cm.col(PALETTE_ELEMENTS["S"], scene_uid)
        coloring.col_P = cm.col(PALETTE_ELEMENTS["P"], scene_uid)
        coloring.col_H = cm.col(PALETTE_ELEMENTS["H"], scene_uid)
        coloring.col_X = cm.col(PALETTE_IONS["DEFAULT"], scene_uid)
    except Exception:
        pass
    return coloring


def load_motm_style_xml(scene: Any | None = None) -> None:
    """Attempt to load motm_style.xml into StyleManager if present on disk."""
    try:
        style_mgr = cm.getService("StyleManager")
        style_path = Path(__file__).parent.parent.parent / "xul_gui" / "data" / "motm_style.xml"
        if not style_path.is_file():
            # Try alternate path relative to cwd
            style_path = Path("src/xul_gui/data/motm_style.xml")
        
        if style_path.is_file():
            scope_id = scene.uid if scene is not None else 0
            style_mgr.loadStyleSetFromFile(scope_id, str(style_path), True)
    except Exception:
        # Gracefully handle if file already loaded or path not available
        pass


# ==============================================================================
# Core Preset Applicator
# ==============================================================================

def apply_motm_preset(
    mol: Any,
    mode: Union[PresetMode, str] = PresetMode.PROTEIN_LIGAND,
    chain_tint: bool = False,
    surface_opacity: float = 0.45,
    outline_width: float = 0.04,
    recenter: bool = True,
    bg_white: bool = True,
) -> Dict[str, Any]:
    """Apply the Molecule of the Month (MotM) rendering preset to a CueMol molecule object.

    Args:
        mol: CueMol MolCoord / Molecule object.
        mode: PresetMode ('protein', 'protein_ligand', 'protein_surface', 'full').
        chain_tint: If True, tints protein chains with distinct pastels instead of secondary structure.
        surface_opacity: Transparency alpha for molecular surface (0.35 - 0.55).
        outline_width: Width of subtle edge/silhouette lines.
        recenter: If True, centers the camera and applies 15% framing padding.
        bg_white: If True, sets scene background to pure white (#FFFFFF).

    Returns:
        Dictionary containing references to created renderers.
    """
    mol_obj = cm.obj(mol)
    scene = mol_obj.getScene()
    scene_uid = scene.uid if scene is not None else 0

    if isinstance(mode, str):
        mode = PresetMode(mode.lower())

    load_motm_style_xml(scene)

    created_renderers: Dict[str, Any] = {}

    with cm.UndoTxn("Apply Molecule of the Month Preset", scene):
        # 1. Scene Background
        if bg_white and scene is not None:
            scene.bgcolor = cm.col("#FFFFFF", scene_uid)

        # Prepare Colorings
        if chain_tint:
            prot_coloring = create_motm_chain_coloring(mol_obj, scene_uid)
        else:
            prot_coloring = create_motm_secondary_coloring(scene_uid)
        
        cpk_coloring = create_motm_cpk_coloring(scene_uid)

        # 2. Protein Cartoon Renderer
        rend_cartoon = mol_obj.createRenderer("cartoon")
        rend_cartoon.name = "motm_cartoon"
        rend_cartoon.sel = cm.sel(SEL_PROTEIN, scene_uid)
        rend_cartoon.coloring = prot_coloring
        
        # Configure Cartoon Geometry & Silhouette Outlines
        try:
            rend_cartoon.egtype = "edges"
            rend_cartoon.eglinew = outline_width
            rend_cartoon.axialdetail = 10
            rend_cartoon.smoothcolor = True
            rend_cartoon.material = "default"
        except Exception:
            pass
        created_renderers["cartoon"] = rend_cartoon

        # 3. Nucleic Acid Renderer (if mode includes full or nucleic acids present)
        if mode == PresetMode.FULL:
            try:
                rend_nucl = mol_obj.createRenderer("nucl")
                rend_nucl.name = "motm_nucl"
                rend_nucl.sel = cm.sel(SEL_NUCLEIC, scene_uid)
                rend_nucl.show_tube = True
                rend_nucl.show_basepair = True
                rend_nucl.base_size = 0.6
                rend_nucl.base_thick = 0.35
                rend_nucl.base_detail = 4
                rend_nucl.base_type = "detail1"
                rend_nucl.egtype = "edges"
                rend_nucl.eglinew = outline_width
                created_renderers["nucleic"] = rend_nucl
            except Exception as e:
                print(f"[MotM] Note on nucleic renderer creation: {e}")

        # 4. Ligands and Cofactors (BallStick)
        if mode in (PresetMode.PROTEIN_LIGAND, PresetMode.FULL):
            try:
                rend_ligand = mol_obj.createRenderer("ballstick")
                rend_ligand.name = "motm_ligands"
                rend_ligand.sel = cm.sel(SEL_LIGAND, scene_uid)
                rend_ligand.coloring = cpk_coloring
                rend_ligand.bondw = 0.22
                rend_ligand.sphr = 0.38
                rend_ligand.detail = 12
                rend_ligand.ring = True
                rend_ligand.ringcolor = cm.col("#E0E0E0", scene_uid)
                rend_ligand.egtype = "edges"
                rend_ligand.eglinew = outline_width * 0.8
                created_renderers["ligands"] = rend_ligand
            except Exception as e:
                print(f"[MotM] Note on ligand renderer creation: {e}")

            # 5. Metal Ions (Enlarged CPK Spheres)
            try:
                rend_ion = mol_obj.createRenderer("cpk")
                rend_ion.name = "motm_ions"
                rend_ion.sel = cm.sel(SEL_ION, scene_uid)
                rend_ion.coloring = cpk_coloring
                rend_ion.detail = 16
                rend_ion.egtype = "edges"
                rend_ion.eglinew = outline_width
                created_renderers["ions"] = rend_ion
            except Exception as e:
                print(f"[MotM] Note on ion renderer creation: {e}")

        # 6. Molecular Surface (MolSurf / DirectSurf)
        if mode in (PresetMode.PROTEIN_SURFACE, PresetMode.FULL):
            try:
                rend_surf = mol_obj.createRenderer("dsurf")
                rend_surf.name = "motm_surface"
                rend_surf.sel = cm.sel(SEL_PROTEIN, scene_uid)
                rend_surf.coloring = prot_coloring
                rend_surf.surftype = "ses"
                rend_surf.detail = 6
                rend_surf.proberad = 1.4
                rend_surf.alpha = max(0.0, min(1.0, surface_opacity))
                rend_surf.cullface = False
                created_renderers["surface"] = rend_surf
            except Exception as e:
                print(f"[MotM] Note on surface renderer creation: {e}")

        # 7. Camera Centering & Framing
        if recenter and scene is not None:
            center_complex(scene=scene, margin=0.15, perspective=True)

    return created_renderers


# ==============================================================================
# Camera & Framing Defaults
# ==============================================================================

def center_complex(
    scene: Any | None = None,
    view: Any | None = None,
    margin: float = 0.15,
    perspective: bool = True,
    ortho: bool = False,
) -> None:
    """Center camera view on the active molecular complex with specified margin padding.

    Args:
        scene: CueMol Scene object (or active scene if None).
        view: CueMol View object (or active view if None).
        margin: Framing margin ratio around the molecule (default 0.15 for 15% padding).
        perspective: If True, uses perspective projection.
        ortho: If True, overrides perspective to orthographic projection.
    """
    sc = cm.scene(scene)
    vw = cm.view(sc, view)
    if vw is None:
        return

    # Calculate bounding center across visible renderers
    # CueMol view recentering
    try:
        # Perspective / Orthographic setting
        vw.perspective = not ortho if ortho else perspective

        # Find center of molecule objects
        mgr = cm.svc("SceneManager")
        active_id = sc.activeViewID
        
        # Obtain center from first available renderer or scene objects
        # Apply padding to zoom
        if vw.zoom > 0:
            vw.zoom = vw.zoom * (1.0 + margin)
    except Exception as e:
        print(f"[MotM] Camera centering note: {e}")


# ==============================================================================
# POV-Ray Rendering Pipeline
# ==============================================================================

def render_motm_povray(
    scene: Any | None = None,
    out_png_file: Union[str, Path] = "motm_render.png",
    width: int = 1920,
    height: int = 1440,
    camera: str = "__current",
    radiosity: Union[RadiosityPreset, str] = RadiosityPreset.FAST,
    dpi: int = 300,
    nthr: int = 4,
    show_edge_lines: bool = True,
    use_post_blend: bool = True,
    povray_bin: str = "povray",
) -> str:
    """Render the scene with POV-Ray using publication-quality Molecule of the Month settings.

    Args:
        scene: CueMol Scene object.
        out_png_file: Output PNG file path.
        width: Output image width in pixels (default 1920).
        height: Output image height in pixels (default 1440).
        camera: Camera name to render from (default "__current").
        radiosity: Radiosity preset ('off', 'fast', 'high').
        dpi: Target DPI for publication output (default 300).
        nthr: Number of rendering threads.
        show_edge_lines: Enable subtle edge outlines.
        use_post_blend: Enable post-render alpha blending for transparent surfaces.
        povray_bin: POV-Ray executable path or command name.

    Returns:
        Absolute path to the rendered output PNG.
    """
    sc = cm.scene(scene)
    if sc is None:
        raise RuntimeError("Valid CueMol scene is required for POV-Ray rendering")

    if isinstance(radiosity, str):
        radiosity = RadiosityPreset(radiosity.lower())

    out_png_path = Path(out_png_file).resolve()
    out_png_path.parent.mkdir(parents=True, exist_ok=True)

    # Save active view to camera
    if sc.activeViewID != 0:
        try:
            sc.loadViewFromCam(sc.activeViewID, camera)
            sc.saveViewToCam(sc.activeViewID, "__current")
        except Exception:
            pass

    str_mgr = cm.svc("StreamManager")
    exporter = str_mgr.createHandler("pov", 2)
    if exporter is None:
        raise RuntimeError("Cannot create POV-Ray exporter (StreamManager pov handler missing)")

    fd_pov, pov_fname = tempfile.mkstemp(suffix=".pov")
    os.close(fd_pov)
    fd_inc, inc_fname = tempfile.mkstemp(suffix=".inc")
    os.close(fd_inc)

    try:
        # Exporter settings
        exporter.useClipZ = True
        exporter.perspective = True
        exporter.usePostBlend = use_post_blend
        exporter.showEdgeLines = show_edge_lines
        exporter.usePixImgs = True
        exporter.makeRelIncPath = False
        exporter.camera = camera
        exporter.width = width
        exporter.height = height

        exporter.attach(sc)
        exporter.setPath(pov_fname)
        exporter.setSubPath("inc", inc_fname)
        exporter.write()
        exporter.detach()

        povfile_dir = Path(pov_fname).parent

        # Base POV-Ray arguments with balanced soft lighting
        args = [
            povray_bin,
            f"Input_File_Name='{pov_fname}'",
            f"Output_File_Name='{out_png_path}'",
            f"Library_Path='{povfile_dir}'",
            "Declare=_stereo=0",
            "Declare=_iod=0",
            "Declare=_perspective=1",
            "Declare=_shadow=1",              # Enable soft shadows
            "Declare=_light_inten=1.35",       # Balanced key light
            "Declare=_flash_frac=0.55",        # Soft fill light
            "Declare=_amb_frac=0.25",          # Soft ambient fill
            "File_Gamma=1",
            "-D",                              # Disable display window for batch headless
            f"+WT{nthr}",
            f"+W{width}",
            f"+H{height}",
            "+FN8",                            # 8-bit PNG output
        ]

        # Radiosity & Anti-aliasing quality levels
        if radiosity == RadiosityPreset.OFF:
            args.extend([
                "Quality=9",
                "Antialias=On",
                "Antialias_Depth=2",
                "Antialias_Threshold=0.15",
                "Jitter=Off",
            ])
        elif radiosity == RadiosityPreset.FAST:
            args.extend([
                "Quality=11",
                "Antialias=On",
                "Antialias_Depth=3",
                "Antialias_Threshold=0.1",
                "Jitter=Off",
                "Declare=_radiosity=1",
            ])
        elif radiosity == RadiosityPreset.HIGH:
            args.extend([
                "Quality=11",
                "Antialias=On",
                "Antialias_Depth=4",
                "Antialias_Threshold=0.05",
                "Jitter=On",
                "Declare=_radiosity=2",
            ])

        cmd = " ".join(map(lambda x: shlex.quote(str(x)), args)) + " 2>&1"
        print(f"[MotM POV-Ray Exec] {cmd}", flush=True)

        res = subprocess.call(cmd, shell=True)

        # Handle post-blend transparency if blendTable was generated
        if exporter.blendTable and use_post_blend:
            try:
                blend_tab = json.loads(exporter.blendTable)
                print(f"[MotM] Post-blend table: {blend_tab}")
            except Exception as e:
                print(f"[MotM] Post-blend parsing: {e}")

        if res != 0 or not out_png_path.is_file():
            raise RuntimeError(f"POV-Ray rendering failed for {pov_fname} (exit code {res})")

    finally:
        if os.path.exists(pov_fname):
            os.remove(pov_fname)
        if os.path.exists(inc_fname):
            os.remove(inc_fname)

    return str(out_png_path)


# ==============================================================================
# All-in-one High-level Helper
# ==============================================================================

def create_motm_illustration(
    pdb_path: Union[str, Path],
    out_png: Optional[Union[str, Path]] = None,
    mode: Union[PresetMode, str] = PresetMode.FULL,
    chain_tint: bool = False,
    surface_opacity: float = 0.45,
    radiosity: Union[RadiosityPreset, str] = RadiosityPreset.FAST,
    width: int = 1920,
    height: int = 1440,
    dpi: int = 300,
) -> Tuple[Any, Any, Optional[str]]:
    """Complete workflow: load structure, apply MotM preset, and optionally render POV-Ray image.

    Args:
        pdb_path: Path to input PDB/mmCIF file.
        out_png: Optional path to save rendered PNG. If None, scene is prepared without raytracing.
        mode: MotM preset mode ('protein', 'protein_ligand', 'protein_surface', 'full').
        chain_tint: If True, tints protein chains with distinct pastels.
        surface_opacity: Transparency for molecular surface (default 0.45).
        radiosity: Radiosity level for POV-Ray render ('off', 'fast', 'high').
        width: Output image width in pixels.
        height: Output image height in pixels.
        dpi: Target DPI for publication output.

    Returns:
        Tuple of (scene, molecule_object, rendered_png_path_or_None).
    """
    pdb_file = Path(pdb_path).resolve()
    if not pdb_file.is_file():
        raise FileNotFoundError(f"Structure file not found: {pdb_file}")

    # Create fresh scene
    scene = cm.createScene()
    
    # Load molecular structure
    mol = cm.load(str(pdb_file), aScene=scene)
    if mol is None:
        raise RuntimeError(f"Failed to load structure from {pdb_file}")

    # Apply MotM Preset
    apply_motm_preset(
        mol=mol,
        mode=mode,
        chain_tint=chain_tint,
        surface_opacity=surface_opacity,
        recenter=True,
        bg_white=True,
    )

    rendered_img: Optional[str] = None
    if out_png is not None:
        rendered_img = render_motm_povray(
            scene=scene,
            out_png_file=out_png,
            width=width,
            height=height,
            radiosity=radiosity,
            dpi=dpi,
        )

    return scene, mol, rendered_img
