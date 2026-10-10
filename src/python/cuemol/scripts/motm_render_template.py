#!/usr/bin/env python3
"""Molecule of the Month (MotM) Rendering Template Script for CueMol2.

Usage:
    python motm_render_template.py <input.pdb> [options]

Example:
    python motm_render_template.py 1crn.pdb --mode full --output 1crn_motm.png --radiosity fast
    python motm_render_template.py 4hhb.pdb --mode protein_ligand --chain-tint --output 4hhb_motm.png
"""

import argparse
import sys
from pathlib import Path

import cuemol as cm
import cuemol.motm as motm


def main():
    parser = argparse.ArgumentParser(
        description="Render PDB/mmCIF structures in RCSB Molecule of the Month style."
    )
    parser.add_argument("input_pdb", type=str, help="Path to input PDB or mmCIF structure file")
    parser.add_argument(
        "--output", "-o", type=str, default=None, help="Output PNG image path (e.g. motm_render.png)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["protein", "protein_ligand", "protein_surface", "full"],
        default="protein_ligand",
        help="Preset mode (default: protein_ligand)",
    )
    parser.add_argument(
        "--chain-tint",
        action="store_true",
        help="Color multi-chain complexes with distinct pastel hues per chain",
    )
    parser.add_argument(
        "--surface-opacity",
        type=float,
        default=0.45,
        help="Opacity for molecular surface (0.0 to 1.0, default 0.45)",
    )
    parser.add_argument(
        "--radiosity",
        choices=["off", "fast", "high"],
        default="fast",
        help="POV-Ray radiosity quality preset (default: fast)",
    )
    parser.add_argument("--width", type=int, default=1920, help="Output image width in px (default: 1920)")
    parser.add_argument("--height", type=int, default=1440, help="Output image height in px (default: 1440)")
    parser.add_argument("--dpi", type=int, default=300, help="Output image DPI metadata (default: 300)")
    parser.add_argument("--threads", "-j", type=int, default=4, help="POV-Ray rendering threads (default: 4)")
    parser.add_argument("--ortho", action="store_true", help="Use orthographic projection instead of perspective")

    args = parser.parse_args()

    input_path = Path(args.input_pdb)
    if not input_path.is_file():
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Initializing CueMol scene...")
    scene = cm.createScene()

    print(f"[*] Loading molecular structure: {input_path}...")
    mol = cm.load(str(input_path), aScene=scene)
    if mol is None:
        print("Error: Failed to parse structure into CueMol.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Applying 'Molecule of the Month' preset (mode: {args.mode})...")
    renderers = motm.apply_motm_preset(
        mol=mol,
        mode=args.mode,
        chain_tint=args.chain_tint,
        surface_opacity=args.surface_opacity,
        recenter=True,
        bg_white=True,
    )
    print(f"[*] Created renderers: {list(renderers.keys())}")

    if args.ortho:
        motm.center_complex(scene=scene, margin=0.15, ortho=True)

    if args.output:
        out_png = Path(args.output)
        print(f"[*] Raytracing with POV-Ray (radiosity={args.radiosity}, res={args.width}x{args.height})...")
        rendered_file = motm.render_motm_povray(
            scene=scene,
            out_png_file=out_png,
            width=args.width,
            height=args.height,
            radiosity=args.radiosity,
            dpi=args.dpi,
            nthr=args.threads,
        )
        print(f"[✓] Molecule of the Month illustration rendered successfully: {rendered_file}")
    else:
        print("[*] Preset applied to interactive scene. (Pass --output to raytrace to PNG)")


if __name__ == "__main__":
    main()
