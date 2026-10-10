"""Unit tests for the CueMol2 Molecule of the Month (MotM) preset module."""

import unittest
from xml.etree import ElementTree as ET
from pathlib import Path

import cuemol.motm as motm


class TestMotMPreset(unittest.TestCase):
    """Test suite verifying MotM presets, palette values, and selection filters."""

    def test_preset_modes(self):
        """Verify all expected preset modes are defined."""
        self.assertEqual(motm.PresetMode.PROTEIN.value, "protein")
        self.assertEqual(motm.PresetMode.PROTEIN_LIGAND.value, "protein_ligand")
        self.assertEqual(motm.PresetMode.PROTEIN_SURFACE.value, "protein_surface")
        self.assertEqual(motm.PresetMode.FULL.value, "full")

    def test_radiosity_presets(self):
        """Verify radiosity preset enumerations."""
        self.assertEqual(motm.RadiosityPreset.OFF.value, "off")
        self.assertEqual(motm.RadiosityPreset.FAST.value, "fast")
        self.assertEqual(motm.RadiosityPreset.HIGH.value, "high")

    def test_palette_secondary_structure(self):
        """Verify soft pastel tones for secondary structure elements."""
        self.assertIn("helix", motm.PALETTE_SECONDARY)
        self.assertIn("sheet", motm.PALETTE_SECONDARY)
        self.assertIn("coil", motm.PALETTE_SECONDARY)
        self.assertIn("nucleic", motm.PALETTE_SECONDARY)

        # Ensure hex colors are formatted properly
        for k, v in motm.PALETTE_SECONDARY.items():
            self.assertTrue(v.startswith("#"), f"Color for {k} must start with #: {v}")
            self.assertEqual(len(v), 7, f"Color hex must be 7 chars (#RRGGBB): {v}")

    def test_palette_chains(self):
        """Verify chain pastel palette has sufficient distinct colors."""
        self.assertGreaterEqual(len(motm.PALETTE_CHAINS), 8)
        for c in motm.PALETTE_CHAINS:
            self.assertTrue(c.startswith("#"))
            self.assertEqual(len(c), 7)

    def test_element_colors(self):
        """Verify harmonious element palette contains all essential biological elements."""
        essential_elements = ["C", "N", "O", "S", "P", "H"]
        for elem in essential_elements:
            self.assertIn(elem, motm.PALETTE_ELEMENTS)

    def test_smart_selections(self):
        """Verify selection expressions exclude water solvents and properly capture ions & ligands."""
        self.assertIn("rprop type=water", motm.SEL_WATER)
        self.assertIn("HOH", motm.SEL_WATER)
        self.assertIn("WAT", motm.SEL_WATER)
        self.assertIn("rprop type=prot", motm.SEL_PROTEIN)
        self.assertIn("rprop type=nucl", motm.SEL_NUCLEIC)
        self.assertIn("elem Mg", motm.SEL_ION)

    def test_xml_style_validity(self):
        """Verify motm_style.xml is well-formed XML and contains required style definitions."""
        xml_path = Path(__file__).parent.parent.parent / "xul_gui" / "data" / "motm_style.xml"
        self.assertTrue(xml_path.is_file(), f"XML style file must exist at {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "styles")

        # Check styles present
        style_ids = [s.attrib.get("id") for s in root.findall("style")]
        self.assertIn("MotM_Cartoon", style_ids)
        self.assertIn("MotM_BallStick", style_ids)
        self.assertIn("MotM_IonSphere", style_ids)
        self.assertIn("MotM_Nucl", style_ids)
        self.assertIn("MotM_Surface", style_ids)
        self.assertIn("MotM_SecStrColoring", style_ids)
        self.assertIn("MotM_CPKColoring", style_ids)
        self.assertIn("MotM_ProteinPreset", style_ids)
        self.assertIn("MotM_ProteinLigandPreset", style_ids)
        self.assertIn("MotM_FullPreset", style_ids)


if __name__ == "__main__":
    unittest.main()
