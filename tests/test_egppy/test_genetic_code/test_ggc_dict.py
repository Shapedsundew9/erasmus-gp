"""Unit tests for GGCDict immutable-by-construction (WP6).

Tests cover:
- One-step construction from kwargs and EGCDict builder (T032)
- Immutability: mutation attempts raise TypeError (T033)
- No runtime "immutable" key lifecycle (T034)

See specs/001-anti-pattern-fixes/contracts/genetic-code-mutability-contract.md, Contract 4.
"""

import unittest

from egpcommon.common import EGP_EPOCH, SHAPEDSUNDEW9_UUID
from egpcommon.properties import BASIC_CODON_PROPERTIES
from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.ggc_dict import GGCDict

# Minimal valid GGCDict construction data
_MINIMAL_GGC = {
    "cgraph": {"A": [["I", 0, "None"]], "O": [["A", 0, "None"]]},
    "code_depth": 1,
    "generation": 0,
    "num_codes": 1,
    "num_codons": 1,
    "properties": BASIC_CODON_PROPERTIES,
    "creator": SHAPEDSUNDEW9_UUID,
    "created": EGP_EPOCH,
    "ancestora": None,
    "ancestorb": None,
    "gca": None,
    "gcb": None,
    "pgc": None,
}


class TestGGCDictConstruction(unittest.TestCase):
    """T032: GGCDict one-step construction from kwargs and EGCDict builder."""

    def test_construct_from_dict(self) -> None:
        """GGCDict constructed from a valid dict produces a complete object."""
        ggc = GGCDict(_MINIMAL_GGC)
        self.assertIsInstance(ggc, GGCDict)
        self.assertIn("signature", ggc)

    def test_construct_from_egc_dict(self) -> None:
        """GGCDict constructed from an EGCDict builder with required keys works."""
        # Build an EGCDict and manually add GGCDict-required fields
        # (simulating the resolve_inherited_members workflow)
        egc = EGCDict(_MINIMAL_GGC)
        for key in ("code_depth", "generation", "num_codes", "num_codons"):
            egc[key] = _MINIMAL_GGC[key]
        ggc = GGCDict(egc)
        self.assertIsInstance(ggc, GGCDict)
        self.assertIn("signature", ggc)


class TestGGCDictImmutability(unittest.TestCase):
    """T033: GGCDict mutation attempts must raise TypeError."""

    def setUp(self) -> None:
        """Create a GGCDict for immutability tests."""
        self.ggc = GGCDict(_MINIMAL_GGC)

    def test_setitem_raises_type_error(self) -> None:
        """Setting an item on GGCDict must raise TypeError."""
        with self.assertRaises(TypeError):
            self.ggc["foo"] = "bar"

    def test_setitem_existing_key_raises_type_error(self) -> None:
        """Modifying an existing key must raise TypeError."""
        with self.assertRaises(TypeError):
            self.ggc["signature"] = b"\x00" * 32


class TestGGCDictNoRuntimeFlag(unittest.TestCase):
    """T034: No runtime 'immutable' key lifecycle in GGCDict."""

    def test_no_immutable_key(self) -> None:
        """GGCDict must not contain an 'immutable' key after construction."""
        ggc = GGCDict(_MINIMAL_GGC)
        self.assertNotIn("immutable", ggc)


if __name__ == "__main__":
    unittest.main()
