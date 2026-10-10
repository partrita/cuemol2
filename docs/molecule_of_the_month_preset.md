# Molecule of the Month (MotM) Rendering Preset for CueMol2

The Molecule of the Month (MotM) preset creates publication-quality, elegant, high-contrast molecular illustrations reproducing the visual aesthetic popularized by the RCSB PDB "Molecule of the Month" series (David S. Goodsell / RCSB PDB).

---

## Key Features

1. Restrained, Publication-Ready Color Palette:
   - Protein Secondary Structure: Soft pastel coral for $\alpha$-helices, slate blue for $\beta$-sheets, and muted sand/light gray for coils and turns.
   - Multi-Chain Complexes: Harmonious pastel tints distinguishing individual chains (Sage Green, Serenity Blue, Rose Quartz, Living Coral, Orchid, Amber, Mint, etc.).
   - Harmonious Ligand CPK: Softened, non-garish elemental colors (warm slate Carbon, soft deep blue Nitrogen, brick red Oxygen, amber Sulfur, tangerine Phosphorus).
   - Metal Ions: Enlarged CPK spheres with distinct jewel tones (emerald $\text{Mg}^{2+}$, slate $\text{Zn}^{2+}$, cyan $\text{Ca}^{2+}$, rust $\text{Fe}^{2+/3+}$, purple accents).
   - Nucleic Acids: Cadet teal ribbon backbone with clear pastel base-pair ladder rungs.
   - Background: Crisp pure white (`#FFFFFF`) default for high contrast on print and digital displays.

2. Smart Solvent & Artifact Filtering:
   - Automatically renders cofactors, substrates, and metal ions while excluding crystallographic solvent waters (`HOH`, `WAT`, `DOD`, `TIP3`).
   - Handles missing loops and alternate conformations cleanly.

3. POV-Ray Raytracing & Radiosity:
   - Subtle crease and silhouette outlines (`showEdgeLines=True`).
   - Soft shadows and balanced three-point key + fill lighting.
   - Post-render alpha blending for semi-transparent molecular surfaces (SES MolSurf with opacity $0.45$).
   - Three radiosity presets: `off`, `fast`, and `high`.
   - Publication export with configurable resolution and DPI metadata.

---

## Preset Modes

| Mode Name | Identifiers | Generated Visual Components |
| :--- | :--- | :--- |
| Protein Cartoon | `"protein"` | Smooth cartoon ribbon showing $\alpha$-helices, $\beta$-sheets, and coils. |
| Protein + Ligands | `"protein_ligand"` *(Default)* | Cartoon ribbon, Ball & Stick ligands/cofactors, and enlarged CPK metal ion spheres. |
| Protein + Surface | `"protein_surface"` | Cartoon ribbon enclosed in a semi-transparent SES molecular surface ($40-50\%$ opacity). |
| Full Complex | `"full"` | Cartoon, nucleic acid ribbons/ladders, ligands, metal ions, and semi-transparent surface. |

---

## Python API Usage

### 1. Interactive Session / Scripting
```python
import cuemol as cm
import cuemol.motm as motm

# Create scene and load structure
scene = cm.createScene()
mol = cm.load("4hhb.pdb", aScene=scene)

# Apply Molecule of the Month preset
renderers = motm.apply_motm_preset(
    mol=mol,
    mode=motm.PresetMode.PROTEIN_LIGAND, # or 'protein', 'protein_surface', 'full'
    chain_tint=True,                     # Distinct pastel colors for each subunit
    surface_opacity=0.45,                # Opacity for molecular surface
    bg_white=True,                       # Pure white background
    recenter=True                        # Center camera with 15% framing margin
)
```

### 2. High-Res POV-Ray Publication Export
```python
import cuemol as cm
import cuemol.motm as motm

# Raytrace the current scene with soft shadows and radiosity
png_path = motm.render_motm_povray(
    scene=scene,
    out_png_file="hemoglobin_motm.png",
    width=1920,
    height=1440,
    radiosity=motm.RadiosityPreset.FAST, # 'off', 'fast', or 'high'
    dpi=300,
    nthr=8
)
print(f"Rendered to: {png_path}")
```

### 3. One-Liner Batch Workflow
```python
import cuemol.motm as motm

# Load, style, and render in a single call
scene, mol, png = motm.create_motm_illustration(
    pdb_path="1tna.pdb",
    out_png="trna_motm.png",
    mode="full",
    radiosity="fast",
    width=2400,
    height=1800,
    dpi=300
)
```

---

## Command-Line Interface (CLI)

Use `src/python/cuemol/scripts/motm_render_template.py` for headless batch rendering:

```bash
# Render a protein-ligand complex
python src/python/cuemol/scripts/motm_render_template.py 1crn.pdb \
  --mode protein_ligand \
  --output 1crn_motm.png \
  --radiosity fast

# Render a multi-chain complex with subunit pastel tinting
python src/python/cuemol/scripts/motm_render_template.py 4hhb.pdb \
  --mode full \
  --chain-tint \
  --output 4hhb_motm.png \
  --width 3840 --height 2880 --dpi 300 -j 8
```

---

## Color Palette Reference

| Element / Feature | Hex Code | Visual Swatch Description |
| :--- | :--- | :--- |
| $\alpha$-Helix | `#E58B88` | Soft Coral / Warm Rose |
| $\beta$-Sheet | `#7BAFD4` | Soft Slate Blue / Azure |
| Coil / Loop | `#D0CEBA` | Muted Sand / Warm Light Gray |
| Carbon ($\text{C}$) | `#A0A0A0` | Light Slate Neutral Gray |
| Nitrogen ($\text{N}$) | `#4C72B0` | Soft Deep Blue |
| Oxygen ($\text{O}$) | `#C44E52` | Warm Brick Red |
| Sulfur ($\text{S}$) | `#CCB974` | Muted Gold / Amber |
| Phosphorus ($\text{P}$) | `#DD8452` | Tangerine / Warm Orange |
| Metal Ions ($\text{Mg, Zn, Ca, Fe}$) | `#2CA02C` / `#17BECF` / `#D62728` | Jewel Accent Spheres |
| Nucleic Acid Backbone | `#5F9EA0` | Cadet Sage Teal |
| Background | `#FFFFFF` | Pure Clean White |

---

## GUI Usage Guide

The Molecule of the Month preset can be applied within the CueMol2 GUI through three intuitive approaches:

### Method 1: Applying via the Style Manager (Recommended UI Workflow)

1. **Load the Style Definition File**:
   - Open CueMol2 and navigate to **[Scene]** or **[Styles]** $\rightarrow$ **[Style Manager...]**.
   - Click the **[Load Style Set...]** button.
   - Select `src/xul_gui/data/motm_style.xml`.
   - The custom MotM renderers, color palettes, and presets are now registered in your GUI session.
2. **Apply Preset to Structure**:
   - In the left **Scene Navigator** tree, right-click your loaded molecule object (e.g. `1CRN`).
   - Navigate to **[Apply Preset...]** / **[Render Preset]**.
   - Select one of the MotM preset options:
     - `MotM: Protein Cartoon` (cartoon ribbon only)
     - `MotM: Protein + Ligands` (default: cartoon + ball-and-stick ligands and ions)
     - `MotM: Protein + Surface` (cartoon + 45% semi-transparent surface)
     - `MotM: Full Molecular Complex` (cartoon + nucleic acids + ligands + ions + surface)

---

### Method 2: Manual Creation via [Create Renderer] Dialog

1. Right-click your molecule object and select **[New Renderer...]** (or press `Ctrl+R`).
2. In the **Create Renderer** dialog:
   - **Renderer type**: select `cartoon`.
   - **Style**: assign `MotM_Cartoon` and `MotM_SecStrColoring`.
     - *Colors applied*: $\alpha$-helices $\rightarrow$ Rose Coral (`#E58B88`), $\beta$-sheets $\rightarrow$ Slate Blue (`#7BAFD4`), coils $\rightarrow$ Light Sand (`#D0CEBA`).
3. For ligand/ion-containing structures, add a second renderer:
   - **Renderer type**: `ballstick` (or `cpk` for ions).
   - **Selection**: `motm_ligand` (or `motm_ion`).
   - **Style**: assign `MotM_BallStick` and `MotM_CPKColoring`.
4. Set Background Color:
   - Right-click in the empty 3D viewport $\rightarrow$ **[Scene Properties]** $\rightarrow$ set **Background Color** to pure white (`#FFFFFF`).

---

### Method 3: One-Click via the Built-in Python Console

1. Open the CueMol2 Python Console by pressing `Ctrl+Shift+P` (or via **[Window]** $\rightarrow$ **[Python Console]**).
2. Execute:
   ```python
   import cuemol.motm as motm

   # Apply preset to the active molecule in the scene
   motm.apply_motm_preset(mol="*", mode="protein_ligand", chain_tint=False)
   ```

---

### High-Resolution POV-Ray Export via GUI

1. In the top menu bar, select **[File]** $\rightarrow$ **[Render Scene (POV-Ray)...]**.
2. In the POV-Ray export dialog:
   - **Resolution**: Set to `1920 x 1440` (or `3840 x 2880` for 300 DPI print).
   - **Edge Lines**: Enable (**On**, outline width `0.04`).
   - **Shadows**: Enable Soft Shadows.
   - **Radiosity**: Select `Fast` or `High Quality`.
3. Click **[Render]** to export the high-contrast publication illustration.

---

## POV-Ray Lighting & Radiosity Settings

- Key Light: Intensity $1.35$, directional diffuse highlight.
- Fill Light: Flash fraction $0.55$, soft shadow fill.
- Ambient Light: Fraction $0.25$, balanced soft ambient occlusion.
- Radiosity Profiles:
  - `off`: Quality 9, AA Depth 2, fast raytracing with soft shadows.
  - `fast`: Quality 11, AA Depth 3, 1-bounce diffuse ambient occlusion gather.
  - `high`: Quality 11, AA Depth 4, high-density gather with antialiasing jitter.


---

## Verification & Test Checklist

- [x] Single-chain Globular Proteins (e.g., Crambin `1CRN`, Myoglobin `1MBN`):
  - Cartoon helices, sheets, and coils display with distinct pastel tones.
  - Crease and silhouette edges outline secondary structures clearly.
- [x] Multi-chain Oligomers & Assemblies (e.g., Hemoglobin `4HHB`, GroEL `1OEL`):
  - Subunits distinguishable when `chain_tint=True`.
  - Interface boundaries remain crisp on pure white background.
- [x] Ligand & Cofactor Complexes (e.g., Carbonic Anhydrase + Inhibitor, Heme groups):
  - Ligand bonds and atoms render with harmonious CPK ball-and-stick.
  - Solvent waters (`HOH`, `WAT`) omitted cleanly without cluttering binding pockets.
  - Metal ions ($\text{Zn}^{2+}$, $\text{Fe}^{2+}$) render as prominent spheres.
- [x] Nucleic Acid & Ribonucleoprotein Complexes (e.g., tRNA `1TRA`, Ribosome fragments):
  - Phosphodiester backbones render with cadet teal ribbons.
  - Base pairs render distinct ladder rungs.
- [x] Molecular Surface (`protein_surface` / `full`):
  - Direct SES surface renders semi-transparently ($\alpha=0.45$) over the interior cartoon.
  - Alpha blending properly composites the raytraced surface over background and ribbons.
