"""Unit tests for the mutability contract across the genetic code class hierarchy.

Tests cover:
- Constructor chain integrity (WP4): Every mutable class calls super().__init__()
- Mutable hash behavior (WP5): Mutable objects raise TypeError on hash()
- Frozen hash stability (WP5): Frozen objects remain hashable with stable values

See specs/001-anti-pattern-fixes/contracts/genetic-code-mutability-contract.md
"""

import unittest

from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, EPCls, IfKey, SrcIfKey, SrcRow
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.ep_ref import EPRef, EPRefs
from egppy.genetic_code.frozen_c_graph import FrozenCGraph
from egppy.genetic_code.frozen_endpoint import FrozenEndPoint
from egppy.genetic_code.frozen_ep_ref import FrozenEPRef, FrozenEPRefs
from egppy.genetic_code.frozen_interface import FrozenInterface
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.json_cgraph import json_cgraph_to_interfaces
from egppy.genetic_code.types_def_store import types_def_store

# pylint: disable=protected-access


class TestConstructorChainIntegrity(unittest.TestCase):
    """Contract 1: Initialization Chain Integrity (WP4).

    Mutable classes MUST call super().__init__(). Every parent __init__
    in the MRO is called exactly once and no attributes are left uninitialised.
    """

    def test_endpoint_init_chain(self) -> None:
        """EndPoint must call through FrozenEndPoint.__init__ via super()."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        # All attributes from the frozen parent must be set
        self.assertEqual(ep.row, SrcRow.I)
        self.assertEqual(ep.idx, 0)
        self.assertEqual(ep.cls, EPCls.SRC)
        self.assertIsNotNone(ep.typ)
        self.assertIsInstance(ep.refs, EPRefs)

    def test_endpoint_from_frozen(self) -> None:
        """EndPoint constructed from FrozenEndPoint must work via init chain."""
        frozen = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        ep = EndPoint(frozen)
        self.assertEqual(ep.row, frozen.row)
        self.assertEqual(ep.idx, frozen.idx)
        self.assertEqual(ep.cls, frozen.cls)
        self.assertEqual(ep.typ, frozen.typ)
        self.assertIsInstance(ep.refs, EPRefs)

    def test_interface_init_chain(self) -> None:
        """Interface must initialise through the full MRO."""
        iface = Interface(["int", "float"], DstRow.A)
        self.assertEqual(len(iface), 2)
        self.assertEqual(iface._row, DstRow.A)
        self.assertEqual(iface._cls, EPCls.DST)
        self.assertIsInstance(iface.endpoints, list)

    def test_cgraph_init_chain(self) -> None:
        """CGraph must initialise through the full MRO."""
        jcg = {"A": [["I", 0, "int"]], "O": [["A", 0, "int"]]}
        graph = CGraph(json_cgraph_to_interfaces(jcg))
        # Graph must have Is and Od interfaces at minimum
        self.assertIsNotNone(graph[SrcIfKey.IS])
        self.assertIsNotNone(graph[DstIfKey.OD])

    def test_eprefs_init_chain(self) -> None:
        """EPRefs must call through FrozenEPRefs.__init__ via super()."""
        refs = EPRefs([EPRef(SrcRow.I, 0)])
        self.assertEqual(len(refs), 1)
        self.assertIsInstance(refs._refs, list)

    def test_eprefs_empty_init(self) -> None:
        """EPRefs with no args must initialise properly."""
        refs = EPRefs()
        self.assertEqual(len(refs), 0)
        self.assertIsInstance(refs._refs, list)

    def test_frozen_endpoint_has_cached_hash(self) -> None:
        """Frozen endpoints must have pre-computed hash at construction."""
        ep = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        self.assertIsInstance(ep._hash, int)
        self.assertEqual(hash(ep), ep._hash)

    def test_frozen_interface_has_cached_hash(self) -> None:
        """Frozen interfaces must have pre-computed hash at construction."""
        iface = FrozenInterface(SrcRow.I, (types_def_store["int"],), (FrozenEPRefs(iter(())),))
        self.assertIsInstance(iface._hash, int)
        self.assertEqual(hash(iface), iface._hash)

    def test_frozen_cgraph_has_cached_hash(self) -> None:
        """Frozen CGraphs must have pre-computed hash at construction."""
        jcg = {"A": [["I", 0, "int"]], "O": [["A", 0, "int"]]}
        mutable = CGraph(json_cgraph_to_interfaces(jcg))
        frozen = FrozenCGraph(mutable)
        self.assertIsInstance(frozen._hash, int)
        self.assertEqual(hash(frozen), frozen._hash)


class TestMutableHashProhibition(unittest.TestCase):
    """Contract 2: Mutable Hash Behavior (WP5).

    Calling hash() on a mutable genetic-code instance MUST raise TypeError.
    """

    def test_cgraph_not_hashable(self) -> None:
        """CGraph must not be hashable."""
        jcg = {"A": [["I", 0, "int"]], "O": [["A", 0, "int"]]}
        graph = CGraph(json_cgraph_to_interfaces(jcg))
        with self.assertRaises(TypeError):
            hash(graph)

    def test_interface_not_hashable(self) -> None:
        """Interface must not be hashable."""
        iface = Interface(["int", "float"], DstRow.A)
        with self.assertRaises(TypeError):
            hash(iface)

    def test_endpoint_not_hashable(self) -> None:
        """EndPoint must not be hashable."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        with self.assertRaises(TypeError):
            hash(ep)

    def test_epref_not_hashable(self) -> None:
        """EPRef must not be hashable."""
        ref = EPRef(SrcRow.I, 0)
        with self.assertRaises(TypeError):
            hash(ref)

    def test_eprefs_not_hashable(self) -> None:
        """EPRefs must not be hashable."""
        refs = EPRefs([EPRef(SrcRow.I, 0)])
        with self.assertRaises(TypeError):
            hash(refs)


class TestFrozenHashStability(unittest.TestCase):
    """Contract 2: Frozen Hash Stability (WP5).

    Frozen genetic-code instances MUST remain hashable with stable values.
    """

    def test_frozen_endpoint_hashable(self) -> None:
        """FrozenEndPoint must be hashable and produce stable hashes."""
        ep = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        h1 = hash(ep)
        h2 = hash(ep)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)

    def test_frozen_interface_hashable(self) -> None:
        """FrozenInterface must be hashable and produce stable hashes."""
        iface = FrozenInterface(SrcRow.I, (types_def_store["int"],), (FrozenEPRefs(iter(())),))
        h1 = hash(iface)
        h2 = hash(iface)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)

    def test_frozen_cgraph_hashable(self) -> None:
        """FrozenCGraph must be hashable and produce stable hashes."""
        jcg = {"A": [["I", 0, "int"]], "O": [["A", 0, "int"]]}
        mutable = CGraph(json_cgraph_to_interfaces(jcg))
        frozen = FrozenCGraph(mutable)
        h1 = hash(frozen)
        h2 = hash(frozen)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)

    def test_frozen_epref_hashable(self) -> None:
        """FrozenEPRef must be hashable and produce stable hashes."""
        ref = FrozenEPRef(SrcRow.I, 0)
        h1 = hash(ref)
        h2 = hash(ref)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)

    def test_frozen_eprefs_hashable(self) -> None:
        """FrozenEPRefs must be hashable and produce stable hashes."""
        refs = FrozenEPRefs(iter((FrozenEPRef(SrcRow.I, 0),)))
        h1 = hash(refs)
        h2 = hash(refs)
        self.assertEqual(h1, h2)
        self.assertIsInstance(h1, int)


if __name__ == "__main__":
    unittest.main()
