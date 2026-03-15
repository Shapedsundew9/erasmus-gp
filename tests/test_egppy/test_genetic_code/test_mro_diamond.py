"""Regression tests for diamond inheritance documentation and MRO safety.

Contracts covered:
- Exact MRO sequences for all five diamonds
- Subclass positive/negative contracts
- Deterministic mismatch message format (class, expected MRO, actual MRO)
- Class docstring hierarchy metadata requirements
- Architecture document section completeness
"""

from __future__ import annotations

import unittest
from pathlib import Path

from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC, FrozenCGraphABC
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.endpoint_abc import EndPointABC, FrozenEndPointABC
from egppy.genetic_code.ep_ref import EPRef, EPRefs
from egppy.genetic_code.ep_ref_abc import EPRefABC, EPRefsABC, FrozenEPRefABC, FrozenEPRefsABC
from egppy.genetic_code.frozen_c_graph import FrozenCGraph
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_ep_ref import FrozenEPRef, FrozenEPRefs
from egppy.genetic_code.frozen_interface import FrozenInterface
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.interface_abc import FrozenInterfaceABC, InterfaceABC

REPO_ROOT = Path(__file__).resolve().parents[3]
ARCH_DOC = REPO_ROOT / "docs/components/worker/diamond_inheritance.md"


class TestDiamondMROContracts(unittest.TestCase):
    """Exact MRO and subclass-contract regression checks for all diamonds."""

    def assert_mro_equals(self, cls: type, expected: tuple[str, ...]) -> None:
        """Assert exact MRO with deterministic mismatch messaging."""
        actual = tuple(base.__name__ for base in cls.__mro__)
        if actual != expected:
            self.fail(
                f"MRO mismatch for {cls.__name__}: "
                f"expected MRO sequence={expected}; "
                f"actual MRO sequence={actual}"
            )

    def test_cgraph_mro_exact(self) -> None:
        expected = (
            "CGraph",
            "FrozenCGraph",
            "CGraphABC",
            "FrozenCGraphABC",
            "MutableMapping",
            "Mapping",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
            "CommonObj",
            "CommonObjABC",
            "ABC",
            "object",
        )
        self.assert_mro_equals(CGraph, expected)

    def test_interface_mro_exact(self) -> None:
        expected = (
            "Interface",
            "CommonObj",
            "FrozenInterface",
            "InterfaceABC",
            "FrozenInterfaceABC",
            "CommonObjABC",
            "ABC",
            "MutableSequence",
            "Sequence",
            "Reversible",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
            "object",
        )
        self.assert_mro_equals(Interface, expected)

    def test_endpoint_mro_exact(self) -> None:
        expected = (
            "EndPoint",
            "FrozenEndPoint",
            "CommonObj",
            "EndPointABC",
            "FrozenEndPointABC",
            "CommonObjABC",
            "ABC",
            "Hashable",
            "object",
        )
        self.assert_mro_equals(EndPoint, expected)

    def test_epref_mro_exact(self) -> None:
        expected = (
            "EPRef",
            "FrozenEPRef",
            "CommonObj",
            "EPRefABC",
            "FrozenEPRefABC",
            "CommonObjABC",
            "ABC",
            "Hashable",
            "object",
        )
        self.assert_mro_equals(EPRef, expected)

    def test_eprefs_mro_exact(self) -> None:
        expected = (
            "EPRefs",
            "FrozenEPRefs",
            "CommonObj",
            "EPRefsABC",
            "FrozenEPRefsABC",
            "CommonObjABC",
            "ABC",
            "Hashable",
            "MutableSequence",
            "Sequence",
            "Reversible",
            "Collection",
            "Sized",
            "Iterable",
            "Container",
            "object",
        )
        self.assert_mro_equals(EPRefs, expected)

    def test_failure_message_format(self) -> None:
        """Mismatch errors must include class name, expected MRO, and actual MRO."""
        with self.assertRaises(AssertionError) as ctx:
            self.assert_mro_equals(CGraph, ("CGraph", "object"))
        msg = str(ctx.exception)
        self.assertIn("MRO mismatch for CGraph", msg)
        self.assertIn("expected MRO sequence=", msg)
        self.assertIn("actual MRO sequence=", msg)

    def test_subclass_contract_positive(self) -> None:
        self.assertTrue(issubclass(CGraph, FrozenCGraphABC))
        self.assertTrue(issubclass(CGraph, CGraphABC))
        self.assertTrue(issubclass(Interface, FrozenInterfaceABC))
        self.assertTrue(issubclass(Interface, InterfaceABC))
        self.assertTrue(issubclass(EndPoint, FrozenEndPointABC))
        self.assertTrue(issubclass(EndPoint, EndPointABC))
        self.assertTrue(issubclass(EPRef, FrozenEPRefABC))
        self.assertTrue(issubclass(EPRef, EPRefABC))
        self.assertTrue(issubclass(EPRefs, FrozenEPRefsABC))
        self.assertTrue(issubclass(EPRefs, EPRefsABC))

    def test_subclass_contract_negative(self) -> None:
        self.assertFalse(issubclass(FrozenCGraph, CGraphABC))
        self.assertFalse(issubclass(FrozenInterface, InterfaceABC))
        self.assertFalse(issubclass(FrozenEndPoint, EndPointABC))
        self.assertFalse(issubclass(FrozenEPRef, EPRefABC))
        self.assertFalse(issubclass(FrozenEPRefs, EPRefsABC))


class TestDiamondDocumentationContracts(unittest.TestCase):
    """Docstring and architecture-document completeness checks."""

    def test_class_docstrings_contain_role_parent_grandparent(self) -> None:
        classes = (
            FrozenCGraphABC,
            CGraphABC,
            FrozenCGraph,
            CGraph,
            FrozenInterfaceABC,
            InterfaceABC,
            FrozenInterface,
            Interface,
            FrozenEndPointABC,
            EndPointABC,
            FrozenEndPoint,
            EndPoint,
            FrozenEPRefABC,
            EPRefABC,
            FrozenEPRefsABC,
            EPRefsABC,
            FrozenEPRef,
            EPRef,
            FrozenEPRefs,
            EPRefs,
        )
        for cls in classes:
            with self.subTest(cls=cls.__name__):
                doc = cls.__doc__ or ""
                self.assertIn("Role:", doc)
                self.assertIn("Direct Parents:", doc)
                self.assertIn("Shared Grandparent:", doc)

    def test_architecture_document_exists(self) -> None:
        self.assertTrue(ARCH_DOC.exists(), f"Missing architecture doc: {ARCH_DOC}")

    def test_architecture_document_required_sections(self) -> None:
        text = ARCH_DOC.read_text(encoding="utf-8")
        required = (
            "## Canonical Inventory",
            "## Family Diagrams",
            "## Full MRO Listings",
            "## Subclass Contract",
            "## Initialization Patterns",
            "## Contributor Playbook For New Frozen/Mutable Pairs",
            "### CGraph Family",
            "### Interface Family",
            "### EndPoint Family",
            "### EPRef Family (EPRef + EPRefs Diamonds)",
            "optional-args-with-early-return",
            "separated-hash-computation",
            "template-method-with-override",
        )
        for marker in required:
            with self.subTest(marker=marker):
                self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
