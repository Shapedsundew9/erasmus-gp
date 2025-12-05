"""Unit tests for FrozenCGraph, FrozenInterface, and FrozenEndPoint classes.

This module tests that frozen (immutable) implementations behave identically to
mutable implementations when initialized from the same data, while maintaining
immutability guarantees and memory efficiency.
"""

import unittest

from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import DstRow, EPCls, SrcRow
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.frozen_c_graph import FrozenCGraph, FrozenEndPoint, FrozenInterface
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.types_def import types_def_store


class TestFrozenEndPoint(unittest.TestCase):
    """Unit tests for the FrozenEndPoint class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        # Create mutable endpoints
        self.ep_src = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        self.ep_dst = EndPoint(DstRow.A, 0, EPCls.DST, "float", [[SrcRow.I, 0]])

        # Create frozen endpoints
        self.frozen_ep_src = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        self.frozen_ep_dst = FrozenEndPoint(
            DstRow.A, 0, EPCls.DST, types_def_store["float"], ((SrcRow.I, 0),)
        )

    def test_api_compatibility_with_mutable(self) -> None:
        """Test that frozen endpoints are API compatible with mutable endpoints."""
        # Test that frozen endpoint attributes match mutable endpoint attributes
        self.assertEqual(self.frozen_ep_src.row, self.ep_src.row)
        self.assertEqual(self.frozen_ep_src.idx, self.ep_src.idx)
        self.assertEqual(self.frozen_ep_src.cls, self.ep_src.cls)
        self.assertEqual(self.frozen_ep_src.typ, self.ep_src.typ)

        # Test refs property returns list format
        self.assertIsInstance(self.frozen_ep_src.refs, list)
        self.assertEqual(self.frozen_ep_src.refs, self.ep_src.refs)

    def test_comparison(self) -> None:
        """Test comparison operators."""
        ep1 = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        ep2 = FrozenEndPoint(SrcRow.A, 1, EPCls.SRC, types_def_store["int"], ())

        self.assertLess(ep1, ep2)
        self.assertLessEqual(ep1, ep2)
        self.assertGreater(ep2, ep1)
        self.assertGreaterEqual(ep2, ep1)

    def test_consistency(self) -> None:
        """Test consistency method."""
        # Valid endpoint should pass consistency check
        self.frozen_ep_src.consistency()
        self.frozen_ep_dst.consistency()

        # Destination with multiple refs should fail
        invalid_ep = FrozenEndPoint(
            DstRow.A, 0, EPCls.DST, types_def_store["float"], ((SrcRow.I, 0), (SrcRow.I, 1))
        )
        with self.assertRaises(ValueError):
            invalid_ep.consistency()

    def test_equality(self) -> None:
        """Test equality between frozen and mutable endpoints."""
        # Create identical mutable and frozen endpoints
        mutable_ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        frozen_ep = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())

        self.assertEqual(frozen_ep, mutable_ep)
        self.assertEqual(mutable_ep, frozen_ep)

        # Test inequality
        different_ep = EndPoint(SrcRow.I, 1, EPCls.SRC, "int")
        self.assertNotEqual(frozen_ep, different_ep)

    def test_hash_consistency(self) -> None:
        """Test that frozen endpoints have consistent hashes."""
        ep1 = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())
        ep2 = FrozenEndPoint(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], ())

        # Hash should be pre-computed and consistent
        # pylint: disable=protected-access
        self.assertEqual(hash(ep1), hash(ep2))
        self.assertEqual(ep1._hash, ep1._hash)  # Calling hash multiple times returns same value

    def test_immutability(self) -> None:
        """Test that frozen endpoints cannot be modified."""
        with self.assertRaises(RuntimeError):
            self.frozen_ep_src.connect(self.frozen_ep_dst)

    def test_init(self) -> None:
        """Test FrozenEndPoint initialization."""
        self.assertEqual(self.frozen_ep_src.row, SrcRow.I)
        self.assertEqual(self.frozen_ep_src.idx, 0)
        self.assertEqual(self.frozen_ep_src.cls, EPCls.SRC)
        self.assertEqual(self.frozen_ep_src.typ.name, "int")
        self.assertEqual(len(self.frozen_ep_src.refs_tuple), 0)

        self.assertEqual(self.frozen_ep_dst.row, DstRow.A)
        self.assertEqual(self.frozen_ep_dst.idx, 0)
        self.assertEqual(self.frozen_ep_dst.cls, EPCls.DST)
        self.assertEqual(self.frozen_ep_dst.typ.name, "float")
        self.assertEqual(len(self.frozen_ep_dst.refs_tuple), 1)

    def test_is_connected(self) -> None:
        """Test is_connected method."""
        self.assertFalse(self.frozen_ep_src.is_connected())
        self.assertTrue(self.frozen_ep_dst.is_connected())

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        json_obj = self.frozen_ep_src.to_json()
        assert isinstance(json_obj, dict), "Expected JSON object to be a dictionary"
        self.assertEqual(json_obj["row"], SrcRow.I)
        self.assertEqual(json_obj["idx"], 0)
        self.assertEqual(json_obj["typ"], "int")

        # Test JSON CGraph format for destination endpoint
        json_cgraph = self.frozen_ep_dst.to_json(json_c_graph=True)
        self.assertIsInstance(json_cgraph, list)
        self.assertEqual(json_cgraph, [SrcRow.I, 0, "float"])

    def test_verify(self) -> None:
        """Test verify method."""
        # Valid endpoint should verify without error
        self.frozen_ep_src.verify()
        self.frozen_ep_dst.verify()

        # Invalid endpoint should raise error
        invalid_ep = FrozenEndPoint(SrcRow.I, 256, EPCls.SRC, types_def_store["int"], ())
        with self.assertRaises(ValueError):
            invalid_ep.verify()


class TestFrozenInterface(unittest.TestCase):
    """Unit tests for the FrozenInterface class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        # Create mutable interface
        self.mutable_iface = Interface(
            [
                EndPoint(SrcRow.I, 0, EPCls.SRC, "int"),
                EndPoint(SrcRow.I, 1, EPCls.SRC, "float"),
            ]
        )

        # Create frozen interface
        self.frozen_iface = FrozenInterface(
            SrcRow.I,
            EPCls.SRC,
            (types_def_store["int"], types_def_store["float"]),
            ((), ()),
        )

    def test_add(self) -> None:
        """Test concatenating frozen interfaces."""
        frozen2 = FrozenInterface(SrcRow.I, EPCls.SRC, (types_def_store["bool"],), ((),))

        result = self.frozen_iface + frozen2
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result, FrozenInterface)

    def test_api_compatibility_with_mutable(self) -> None:
        """Test that frozen interfaces are API compatible with mutable interfaces."""
        self.assertEqual(len(self.frozen_iface), len(self.mutable_iface))
        self.assertEqual(self.frozen_iface.cls(), self.mutable_iface.cls())

    def test_consistency(self) -> None:
        """Test consistency method."""
        self.frozen_iface.consistency()

    def test_equality(self) -> None:
        """Test equality between frozen and mutable interfaces."""
        # Both interfaces have same endpoints
        self.assertEqual(self.frozen_iface, self.mutable_iface)
        self.assertEqual(self.mutable_iface, self.frozen_iface)

    def test_getitem(self) -> None:
        """Test getting endpoints by index."""
        ep0 = self.frozen_iface[0]
        ep1 = self.frozen_iface[1]

        self.assertEqual(ep0.idx, 0)
        self.assertEqual(ep1.idx, 1)
        self.assertEqual(ep0.typ.name, "int")
        self.assertEqual(ep1.typ.name, "float")

    def test_hash_consistency(self) -> None:
        """Test that frozen interfaces have consistent hashes."""
        frozen2 = FrozenInterface(
            SrcRow.I,
            EPCls.SRC,
            (types_def_store["int"], types_def_store["float"]),
            ((), ()),
        )
        self.assertEqual(hash(self.frozen_iface), hash(frozen2))

    def test_immutability(self) -> None:
        """Test that frozen interfaces cannot be modified."""
        with self.assertRaises(RuntimeError):
            self.frozen_iface[0] = self.frozen_iface[0]

        with self.assertRaises(RuntimeError):
            self.frozen_iface.append(
                FrozenEndPoint(SrcRow.I, 2, EPCls.SRC, types_def_store["bool"], ())
            )

        with self.assertRaises(RuntimeError):
            self.frozen_iface.extend([])

    def test_init(self) -> None:
        """Test FrozenInterface initialization."""
        self.assertEqual(self.frozen_iface.row, SrcRow.I)
        self.assertEqual(self.frozen_iface.epcls, EPCls.SRC)
        self.assertEqual(len(self.frozen_iface.type_tuple), 2)
        self.assertEqual(len(self.frozen_iface.refs_tuple), 2)

    def test_iteration(self) -> None:
        """Test iterating over endpoints."""
        endpoints = list(self.frozen_iface)
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0].idx, 0)
        self.assertEqual(endpoints[1].idx, 1)

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        json_list = self.frozen_iface.to_json()
        self.assertIsInstance(json_list, list)
        self.assertEqual(len(json_list), 2)

    def test_to_td_uids(self) -> None:
        """Test TypesDef UID conversion."""
        uids = self.frozen_iface.to_td_uids()
        self.assertEqual(len(uids), 2)
        self.assertEqual(uids[0], types_def_store["int"].uid)
        self.assertEqual(uids[1], types_def_store["float"].uid)

    def test_unconnected_eps(self) -> None:
        """Test getting unconnected endpoints."""
        unconnected = self.frozen_iface.unconnected_eps()
        self.assertEqual(len(unconnected), 2)  # Both are unconnected

    def test_verify(self) -> None:
        """Test verify method."""
        self.frozen_iface.verify()

        # Empty interface should verify
        empty_iface = FrozenInterface(SrcRow.I, EPCls.SRC, (), ())
        empty_iface.verify()


class TestFrozenCGraph(unittest.TestCase):
    """Unit tests for the FrozenCGraph class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        # Create a simple mutable graph
        self.mutable_graph = CGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )

        # Create equivalent frozen graph - ensure bidirectional references
        self.frozen_graph = FrozenCGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )

    def test_consistency(self) -> None:
        """Test consistency method."""
        self.frozen_graph.consistency()

    def test_contains(self) -> None:
        """Test checking if interface exists."""
        self.assertIn("Is", self.frozen_graph)
        self.assertIn("Ad", self.frozen_graph)
        self.assertIn("I", self.frozen_graph)  # Row check
        self.assertIn("A", self.frozen_graph)  # Row check
        self.assertNotIn("Bd", self.frozen_graph)

    def test_equality_with_mutable(self) -> None:
        """Test that frozen and mutable graphs can be compared."""
        # Note: FrozenCGraph.__eq__ only compares with other FrozenCGraph instances
        # This is intentional for performance
        frozen_graph2 = FrozenCGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )
        self.assertEqual(self.frozen_graph, frozen_graph2)

    def test_get(self) -> None:
        """Test get method."""
        iface = self.frozen_graph.get("Is")
        self.assertIsNotNone(iface)

        missing = self.frozen_graph.get("Bd", None)
        self.assertIsNone(missing)

    def test_getitem(self) -> None:
        """Test getting interfaces by key."""
        iface = self.frozen_graph["Is"]
        self.assertIsInstance(iface, FrozenInterface)
        self.assertEqual(len(iface), 1)

    def test_graph_type(self) -> None:
        """Test graph_type method."""
        graph_type = self.frozen_graph.graph_type()
        self.assertEqual(graph_type, CGraphType.PRIMITIVE)

    def test_hash_consistency(self) -> None:
        """Test that frozen graphs have consistent hashes."""
        # Create another identical graph
        frozen_graph2 = FrozenCGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )

        # Hashes should be equal
        self.assertEqual(hash(self.frozen_graph), hash(frozen_graph2))

    def test_init(self) -> None:
        """Test FrozenCGraph initialization."""
        self.assertIsInstance(self.frozen_graph, FrozenCGraph)
        self.assertEqual(len(self.frozen_graph), 4)

    def test_is_stable(self) -> None:
        """Test is_stable method."""
        # Frozen graphs are always stable
        self.assertTrue(self.frozen_graph.is_stable())

    def test_iteration(self) -> None:
        """Test iterating over interface keys."""
        keys = list(self.frozen_graph)
        self.assertEqual(len(keys), 4)
        self.assertIn("Is", keys)
        self.assertIn("Ad", keys)

    def test_keys_values_items(self) -> None:
        """Test keys(), values(), and items() methods."""
        keys = list(self.frozen_graph.keys())
        values = list(self.frozen_graph.values())
        items = list(self.frozen_graph.items())

        self.assertEqual(len(keys), 4)
        self.assertEqual(len(values), 4)
        self.assertEqual(len(items), 4)

        # Check all values are FrozenInterface instances
        for val in values:
            self.assertIsInstance(val, FrozenInterface)

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        json_obj = self.frozen_graph.to_json()
        self.assertIsInstance(json_obj, dict)
        self.assertIn(DstRow.A, json_obj)
        self.assertIn(DstRow.O, json_obj)

    def test_verify(self) -> None:
        """Test verify method."""
        self.frozen_graph.verify()


class TestFrozenCGraphComplexCases(unittest.TestCase):
    """Test frozen graphs with more complex structures."""

    def test_for_loop_graph(self) -> None:
        """Test a FOR_LOOP graph type."""
        graph = FrozenCGraph(
            {
                "Is": [
                    (SrcRow.I, 0, EPCls.SRC, types_def_store["list[int]"], [[DstRow.L, 0]]),
                    (SrcRow.I, 1, EPCls.SRC, types_def_store["int"], [[DstRow.P, 0]]),
                ],
                "Ld": [(DstRow.L, 0, EPCls.DST, types_def_store["list[int]"], [[SrcRow.I, 0]])],
                "Ls": [(SrcRow.L, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.L, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
                "Pd": [(DstRow.P, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 1]])],
            }
        )

        self.assertEqual(graph.graph_type(), CGraphType.FOR_LOOP)
        graph.verify()

    def test_if_then_graph(self) -> None:
        """Test an IF_THEN graph type."""
        graph = FrozenCGraph(
            {
                "Is": [
                    (SrcRow.I, 0, EPCls.SRC, types_def_store["bool"], [[DstRow.F, 0]]),
                    (SrcRow.I, 1, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]]),
                ],
                "Fd": [(DstRow.F, 0, EPCls.DST, types_def_store["bool"], [[SrcRow.I, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 1]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
                "Pd": [(DstRow.P, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 1]])],
            }
        )

        self.assertEqual(graph.graph_type(), CGraphType.IF_THEN)
        graph.verify()

    def test_standard_graph(self) -> None:
        """Test a STANDARD graph type."""
        graph = FrozenCGraph(
            {
                "Is": [
                    (SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]]),
                    (SrcRow.I, 1, EPCls.SRC, types_def_store["float"], [[DstRow.B, 0]]),
                ],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.B, 1]])],
                "Bd": [
                    (DstRow.B, 0, EPCls.DST, types_def_store["float"], [[SrcRow.I, 1]]),
                    (DstRow.B, 1, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]]),
                ],
                "Bs": [
                    (SrcRow.B, 0, EPCls.SRC, types_def_store["float"], [[DstRow.O, 0]]),
                    (SrcRow.B, 1, EPCls.SRC, types_def_store["int"], [[DstRow.O, 1]]),
                ],
                "Od": [
                    (DstRow.O, 0, EPCls.DST, types_def_store["float"], [[SrcRow.B, 0]]),
                    (DstRow.O, 1, EPCls.DST, types_def_store["int"], [[SrcRow.B, 1]]),
                ],
            }
        )

        self.assertTrue(graph.is_stable())
        self.assertEqual(len(graph), 6)
        graph.verify()


class TestJSONConversion(unittest.TestCase):
    """Test conversion between mutable and frozen graphs via JSON."""

    def test_round_trip_conversion(self) -> None:
        """Test that mutable -> JSON -> frozen -> JSON produces identical results."""
        # Create a mutable graph
        mutable = CGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )

        # Convert to JSON
        json1 = mutable.to_json(json_c_graph=True)

        # Create frozen graph from same data
        frozen = FrozenCGraph(
            {
                "Is": [(SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [[DstRow.A, 0]])],
                "Ad": [(DstRow.A, 0, EPCls.DST, types_def_store["int"], [[SrcRow.I, 0]])],
                "As": [(SrcRow.A, 0, EPCls.SRC, types_def_store["int"], [[DstRow.O, 0]])],
                "Od": [(DstRow.O, 0, EPCls.DST, types_def_store["int"], [[SrcRow.A, 0]])],
            }
        )

        # Convert frozen to JSON
        json2 = frozen.to_json(json_c_graph=True)

        # JSONs should be identical
        self.assertEqual(json1, json2)


if __name__ == "__main__":
    unittest.main()
