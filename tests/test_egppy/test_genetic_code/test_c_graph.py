"""Unit tests for the CGraph class and related functions.

This module tests the Connection Graph functionality based on the specifications
in graph.md, including all graph types: If-Then, If-Then-Else, Empty, For-Loop,
While-Loop, Standard, and Primitive.
"""

import unittest

from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    CGraph,
    c_graph_type,
    json_cgraph_to_interfaces,
    valid_dst_rows,
    valid_jcg,
    valid_rows,
    valid_src_rows,
)
from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.interface import Interface


class TestValidSrcRows(unittest.TestCase):
    """Test the valid_src_rows function for all graph types."""

    def test_if_then_valid_src_rows(self) -> None:
        """Test valid source rows for If-Then graphs."""
        result = valid_src_rows(CGraphType.IF_THEN)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.F, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)
        self.assertIn(DstRow.U, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.F], frozenset({SrcRow.I}))  # Only I can connect to F
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))  # Only I can connect to A
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))  # I and A to O
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I}))  # Only I can connect to P

    def test_if_then_else_valid_src_rows(self) -> None:
        """Test valid source rows for If-Then-Else graphs."""
        result = valid_src_rows(CGraphType.IF_THEN_ELSE)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.B, result)
        self.assertIn(DstRow.F, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.F], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.B], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I, SrcRow.B}))

    def test_empty_valid_src_rows(self) -> None:
        """Test valid source rows for Empty graphs."""
        result = valid_src_rows(CGraphType.EMPTY)

        # Empty graphs only have O row with no connections
        self.assertIn(DstRow.O, result)
        self.assertEqual(result[DstRow.O], frozenset())

    def test_for_loop_valid_src_rows(self) -> None:
        """Test valid source rows for For-Loop graphs."""
        result = valid_src_rows(CGraphType.FOR_LOOP)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.L, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.L], frozenset({SrcRow.I}))  # Only I to L
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I, SrcRow.L}))  # I and L to A
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))  # I and A to O
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I}))  # Only I to P

    def test_while_loop_valid_src_rows(self) -> None:
        """Test valid source rows for While-Loop graphs."""
        result = valid_src_rows(CGraphType.WHILE_LOOP)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.L, result)
        self.assertIn(DstRow.W, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.L], frozenset({SrcRow.I}))  # Only I to L
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I, SrcRow.L}))  # I and L to A
        self.assertEqual(result[DstRow.W], frozenset({SrcRow.A}))  # Only A to W
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))  # I and A to O
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I}))  # Only I to P

    def test_standard_valid_src_rows(self) -> None:
        """Test valid source rows for Standard graphs."""
        result = valid_src_rows(CGraphType.STANDARD)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.B, result)
        self.assertIn(DstRow.O, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))  # Only I to A
        self.assertEqual(result[DstRow.B], frozenset({SrcRow.I, SrcRow.A}))  # I and A to B
        self.assertEqual(
            result[DstRow.O], frozenset({SrcRow.I, SrcRow.A, SrcRow.B})
        )  # I, A, B to O

    def test_primitive_valid_src_rows(self) -> None:
        """Test valid source rows for Primitive graphs."""
        result = valid_src_rows(CGraphType.PRIMITIVE)

        # Check required rows exist
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.O, result)

        # Check connectivity rules
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))  # Only I to A
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))  # I and A to O

    def test_unknown_valid_src_rows(self) -> None:
        """Test valid source rows for Unknown graph type (superset)."""
        result = valid_src_rows(CGraphType.UNKNOWN)

        # Unknown should be the superset of all valid connections
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.B, result)
        self.assertIn(DstRow.F, result)
        self.assertIn(DstRow.L, result)
        self.assertIn(DstRow.W, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)
        self.assertIn(DstRow.U, result)

    def test_u_row_is_superset(self) -> None:
        """Test that U row contains all sources from other rows."""
        for graph_type in [
            CGraphType.IF_THEN,
            CGraphType.IF_THEN_ELSE,
            CGraphType.FOR_LOOP,
            CGraphType.WHILE_LOOP,
            CGraphType.STANDARD,
            CGraphType.PRIMITIVE,
        ]:
            result = valid_src_rows(graph_type)
            all_sources = frozenset().union(
                *[srcs for dst, srcs in result.items() if dst != DstRow.U]
            )
            self.assertEqual(result[DstRow.U], all_sources, f"Failed for {graph_type}")


class TestValidDstRows(unittest.TestCase):
    """Test the valid_dst_rows function for all graph types."""

    def test_if_then_valid_dst_rows(self) -> None:
        """Test valid destination rows for If-Then graphs."""
        result = valid_dst_rows(CGraphType.IF_THEN)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.A, result)

        # Check connectivity
        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.F, DstRow.O, DstRow.P}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))

    def test_if_then_else_valid_dst_rows(self) -> None:
        """Test valid destination rows for If-Then-Else graphs."""
        result = valid_dst_rows(CGraphType.IF_THEN_ELSE)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.A, result)
        self.assertIn(SrcRow.B, result)

        # Check connectivity
        self.assertEqual(
            result[SrcRow.I], frozenset({DstRow.A, DstRow.F, DstRow.B, DstRow.P, DstRow.O})
        )
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))
        self.assertEqual(result[SrcRow.B], frozenset({DstRow.P}))

    def test_empty_valid_dst_rows(self) -> None:
        """Test valid destination rows for Empty graphs."""
        result = valid_dst_rows(CGraphType.EMPTY)

        self.assertIn(SrcRow.I, result)
        self.assertEqual(result[SrcRow.I], frozenset())  # No connections

    def test_for_loop_valid_dst_rows(self) -> None:
        """Test valid destination rows for For-Loop graphs."""
        result = valid_dst_rows(CGraphType.FOR_LOOP)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.L, result)
        self.assertIn(SrcRow.A, result)

        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.L, DstRow.O, DstRow.P}))
        self.assertEqual(result[SrcRow.L], frozenset({DstRow.A}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))

    def test_while_loop_valid_dst_rows(self) -> None:
        """Test valid destination rows for While-Loop graphs."""
        result = valid_dst_rows(CGraphType.WHILE_LOOP)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.L, result)
        self.assertIn(SrcRow.A, result)

        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.L, DstRow.O, DstRow.P}))
        self.assertEqual(result[SrcRow.L], frozenset({DstRow.A}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O, DstRow.W}))

    def test_standard_valid_dst_rows(self) -> None:
        """Test valid destination rows for Standard graphs."""
        result = valid_dst_rows(CGraphType.STANDARD)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.A, result)
        self.assertIn(SrcRow.B, result)

        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.B, DstRow.O}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.B, DstRow.O}))
        self.assertEqual(result[SrcRow.B], frozenset({DstRow.O}))

    def test_primitive_valid_dst_rows(self) -> None:
        """Test valid destination rows for Primitive graphs."""
        result = valid_dst_rows(CGraphType.PRIMITIVE)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.A, result)

        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.O}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))


class TestValidRows(unittest.TestCase):
    """Test the valid_rows function."""

    def test_valid_rows_combines_src_and_dst(self) -> None:
        """Test that valid_rows returns union of source and destination rows."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            result = valid_rows(graph_type)
            src_rows = frozenset(valid_dst_rows(graph_type).keys())
            dst_rows = frozenset(valid_src_rows(graph_type).keys())
            expected = src_rows | dst_rows
            self.assertEqual(result, expected, f"Failed for {graph_type}")


class TestValidJCG(unittest.TestCase):
    """Test the valid_jcg function for JSON Connection Graph validation."""

    def test_valid_empty_jcg(self) -> None:
        """Test validation of a valid empty JSON connection graph."""
        jcg = {DstRow.O: [], DstRow.U: []}
        self.assertTrue(valid_jcg(jcg))

    def test_valid_simple_jcg(self) -> None:
        """Test validation of a simple valid JSON connection graph."""
        # A primitive graph with I -> A -> O
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        self.assertTrue(valid_jcg(jcg))

    def test_invalid_key_in_jcg(self) -> None:
        """Test that invalid keys in JCG raise ValueError."""
        jcg = {"X": [], DstRow.U: []}
        with self.assertRaises(ValueError):
            valid_jcg(jcg)

    def test_invalid_value_type_in_jcg(self) -> None:
        """Test that invalid value types raise TypeError."""
        jcg = {DstRow.O: "not a list", DstRow.U: []}
        with self.assertRaises(TypeError):
            valid_jcg(jcg)

    def test_invalid_endpoint_format_in_jcg(self) -> None:
        """Test that invalid endpoint formats raise TypeError."""
        jcg = {DstRow.O: ["not a list"], DstRow.U: []}
        with self.assertRaises(TypeError):
            valid_jcg(jcg)

    def test_invalid_row_in_endpoint(self) -> None:
        """Test that invalid source rows in endpoints raise ValueError."""
        jcg = {DstRow.O: [["X", 0, "int"]], DstRow.U: []}
        with self.assertRaises(ValueError):
            valid_jcg(jcg)

    def test_invalid_index_in_endpoint(self) -> None:
        """Test that invalid indices raise ValueError."""
        jcg = {DstRow.O: [["I", 256, "int"]], DstRow.U: []}  # Index out of range
        with self.assertRaises(ValueError):
            valid_jcg(jcg)

    def test_missing_destination_row(self) -> None:
        """Test that missing required destination rows raise ValueError."""
        jcg = {DstRow.U: []}  # Missing DstRow.O
        with self.assertRaises(ValueError):
            valid_jcg(jcg)


class TestCGraphType(unittest.TestCase):
    """Test the c_graph_type function for identifying graph types."""

    def test_if_then_identification(self) -> None:
        """Test identification of If-Then graphs."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.IF_THEN)

    def test_if_then_else_identification(self) -> None:
        """Test identification of If-Then-Else graphs."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.B: [["I", 2, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["B", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.IF_THEN_ELSE)

    def test_for_loop_identification(self) -> None:
        """Test identification of For-Loop graphs."""
        jcg = {
            DstRow.L: [["I", 0, "list"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.FOR_LOOP)

    def test_while_loop_identification(self) -> None:
        """Test identification of While-Loop graphs."""
        jcg = {
            DstRow.L: [["I", 0, "int"]],
            DstRow.W: [["A", 0, "bool"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 1, "int"]],
            DstRow.P: [["I", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.WHILE_LOOP)

    def test_standard_identification(self) -> None:
        """Test identification of Standard graphs."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["A", 0, "int"]],
            DstRow.O: [["B", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.STANDARD)

    def test_primitive_identification(self) -> None:
        """Test identification of Primitive graphs."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        self.assertEqual(c_graph_type(jcg), CGraphType.PRIMITIVE)

    def test_empty_identification(self) -> None:
        """Test identification of Empty graphs."""
        jcg = {DstRow.O: [], DstRow.U: []}
        self.assertEqual(c_graph_type(jcg), CGraphType.EMPTY)


class TestCGraph(unittest.TestCase):
    """Test the CGraph class."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Create a simple primitive graph for testing
        self.primitive_jcg = json_cgraph_to_interfaces(
            {
                DstRow.A: [["I", 0, "int"]],
                DstRow.O: [["A", 0, "int"]],
                DstRow.U: [],
            }
        )

        # Create an empty graph
        self.empty_jcg = json_cgraph_to_interfaces({DstRow.O: [], DstRow.U: []})

    def test_cgraph_init_from_json(self) -> None:
        """Test CGraph initialization from JSON."""
        cgraph = CGraph(self.primitive_jcg)
        self.assertIsInstance(cgraph, CGraph)
        self.assertFalse(cgraph.is_frozen())

    def test_cgraph_contains(self) -> None:
        """Test CGraph __contains__ method."""
        cgraph = CGraph(self.primitive_jcg)

        # Test row presence
        self.assertIn("A", cgraph)
        self.assertIn("O", cgraph)
        self.assertNotIn("F", cgraph)
        self.assertNotIn("L", cgraph)

        # Test with class postfix
        self.assertIn("Ad", cgraph)
        self.assertIn("Od", cgraph)
        self.assertIn("Is", cgraph)
        self.assertIn("As", cgraph)

    def test_cgraph_getitem(self) -> None:
        """Test CGraph __getitem__ method."""
        cgraph = CGraph(self.primitive_jcg)

        # Get interfaces
        ad_interface = cgraph["Ad"]
        self.assertIsInstance(ad_interface, Interface)

        od_interface = cgraph["Od"]
        self.assertIsInstance(od_interface, Interface)

    def test_cgraph_setitem(self) -> None:
        """Test CGraph __setitem__ method."""
        cgraph = CGraph(self.empty_jcg)

        # Create a new interface
        new_interface = Interface([EndPoint(DstRow.A, 0, EndPointClass.DST, "int")])
        cgraph["Ad"] = new_interface

        self.assertEqual(cgraph["Ad"], new_interface)

    def test_cgraph_setitem_frozen_raises(self) -> None:
        """Test that setting items on frozen CGraph raises RuntimeError."""
        cgraph = CGraph(self.empty_jcg)
        cgraph.freeze()

        new_interface = Interface([EndPoint(DstRow.A, 0, EndPointClass.DST, "int")])
        with self.assertRaises(RuntimeError):
            cgraph["Ad"] = new_interface

    def test_cgraph_delitem(self) -> None:
        """Test CGraph __delitem__ method."""
        cgraph = CGraph(self.primitive_jcg)

        # Delete an interface
        del cgraph["Ad"]
        self.assertNotIn("Ad", cgraph)

    def test_cgraph_delitem_frozen_raises(self) -> None:
        """Test that deleting items from frozen CGraph raises RuntimeError."""
        cgraph = CGraph(self.primitive_jcg)
        cgraph.freeze()

        with self.assertRaises(RuntimeError):
            del cgraph["Ad"]

    def test_cgraph_iter(self) -> None:
        """Test CGraph __iter__ method."""
        cgraph = CGraph(self.primitive_jcg)

        keys = list(cgraph)
        self.assertIn("Is", keys)
        self.assertIn("As", keys)
        self.assertIn("Ad", keys)
        self.assertIn("Od", keys)
        self.assertNotIn("Fd", keys)

    def test_cgraph_eq(self) -> None:
        """Test CGraph equality comparison."""
        cgraph1 = CGraph(self.primitive_jcg)
        cgraph2 = CGraph(self.primitive_jcg)
        cgraph3 = CGraph(self.empty_jcg)

        self.assertEqual(cgraph1, cgraph2)
        self.assertNotEqual(cgraph1, cgraph3)
        self.assertNotEqual(cgraph1, "not a cgraph")

    def test_cgraph_hash_unfrozen(self) -> None:
        """Test CGraph hash for unfrozen graphs."""
        cgraph = CGraph(self.primitive_jcg)

        # Hash should work even when unfrozen
        hash1 = hash(cgraph)
        self.assertIsInstance(hash1, int)

    def test_cgraph_hash_frozen(self) -> None:
        """Test CGraph hash for frozen graphs."""
        cgraph = CGraph(self.primitive_jcg)
        cgraph.freeze()

        # Hash should be consistent for frozen graphs
        hash1 = hash(cgraph)
        hash2 = hash(cgraph)
        self.assertEqual(hash1, hash2)

    def test_cgraph_to_json(self) -> None:
        """Test CGraph to_json conversion."""
        cgraph = CGraph(self.primitive_jcg)
        jcg = cgraph.to_json()

        self.assertIsInstance(jcg, dict)
        self.assertIn(DstRow.A, jcg)
        self.assertIn(DstRow.O, jcg)

    def test_cgraph_is_stable_with_connections(self) -> None:
        """Test is_stable for a fully connected graph."""
        cgraph = CGraph(self.primitive_jcg)
        # The primitive graph from JSON should be stable
        self.assertTrue(cgraph.is_stable())

    def test_cgraph_copy(self) -> None:
        """Test CGraph copy method."""
        cgraph1 = CGraph(self.primitive_jcg)
        cgraph2 = cgraph1.copy()

        # Should be equal but not the same object
        self.assertEqual(cgraph1, cgraph2)
        self.assertIsNot(cgraph1, cgraph2)

        # Copy should not be frozen
        self.assertFalse(cgraph2.is_frozen())

    def test_cgraph_repr(self) -> None:
        """Test CGraph __repr__ method."""
        cgraph = CGraph(self.primitive_jcg)
        repr_str = repr(cgraph)

        self.assertIsInstance(repr_str, str)
        self.assertGreater(len(repr_str), 0)


class TestCGraphConstants(unittest.TestCase):
    """Test the pre-computed constant dictionaries."""

    def test_cgt_valid_src_rows(self) -> None:
        """Test CGT_VALID_SRC_ROWS constant."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertIn(graph_type, CGT_VALID_SRC_ROWS)
            self.assertEqual(CGT_VALID_SRC_ROWS[graph_type], valid_src_rows(graph_type))

    def test_cgt_valid_dst_rows(self) -> None:
        """Test CGT_VALID_DST_ROWS constant."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertIn(graph_type, CGT_VALID_DST_ROWS)
            self.assertEqual(CGT_VALID_DST_ROWS[graph_type], valid_dst_rows(graph_type))

    def test_cgt_valid_rows(self) -> None:
        """Test CGT_VALID_ROWS constant."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertIn(graph_type, CGT_VALID_ROWS)
            self.assertEqual(CGT_VALID_ROWS[graph_type], valid_rows(graph_type))


class TestCGraphGraphTypes(unittest.TestCase):
    """Test CGraph with different graph types to ensure compliance with rules."""

    def test_if_then_graph_rules(self) -> None:
        """Test If-Then graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {
                DstRow.F: [["I", 0, "bool"]],
                DstRow.A: [["I", 1, "int"]],
                DstRow.O: [["A", 0, "int"]],
                DstRow.P: [["I", 1, "int"]],
                DstRow.U: [],
            }
        )
        cgraph = CGraph(jcg)

        # Must not have L, W, B interfaces
        self.assertNotIn("Ld", cgraph)
        self.assertNotIn("Wd", cgraph)
        self.assertNotIn("Bd", cgraph)
        self.assertNotIn("Bs", cgraph)

        # Must have F, A, O, P
        self.assertIn("Fd", cgraph)
        self.assertIn("Ad", cgraph)
        self.assertIn("Od", cgraph)
        self.assertIn("Pd", cgraph)

    def test_if_then_else_graph_rules(self) -> None:
        """Test If-Then-Else graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {
                DstRow.F: [["I", 0, "bool"]],
                DstRow.A: [["I", 1, "int"]],
                DstRow.B: [["I", 2, "int"]],
                DstRow.O: [["A", 0, "int"]],
                DstRow.P: [["B", 0, "int"]],
                DstRow.U: [],
            }
        )
        cgraph = CGraph(jcg)

        # Must not have L, W
        self.assertNotIn("Ld", cgraph)
        self.assertNotIn("Wd", cgraph)

        # Must have F, A, B, O, P
        self.assertIn("Fd", cgraph)
        self.assertIn("Ad", cgraph)
        self.assertIn("Bd", cgraph)
        self.assertIn("Od", cgraph)
        self.assertIn("Pd", cgraph)

    def test_empty_graph_rules(self) -> None:
        """Test Empty graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces({DstRow.O: [], DstRow.U: []})
        cgraph = CGraph(jcg)

        # Must only have O (and potentially I if provided)
        self.assertIn("Od", cgraph)

        # Must not have F, L, W, A, B, P
        self.assertNotIn("Fd", cgraph)
        self.assertNotIn("Ld", cgraph)
        self.assertNotIn("Wd", cgraph)
        self.assertNotIn("Ad", cgraph)
        self.assertNotIn("Bd", cgraph)

    def test_for_loop_graph_rules(self) -> None:
        """Test For-Loop graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {
                DstRow.L: [["I", 0, "list"]],
                DstRow.A: [["L", 0, "int"]],
                DstRow.O: [["A", 0, "int"]],
                DstRow.P: [["I", 1, "int"]],
                DstRow.U: [],
            }
        )
        cgraph = CGraph(jcg)

        # Must not have F, W, B
        self.assertNotIn("Fd", cgraph)
        self.assertNotIn("Wd", cgraph)
        self.assertNotIn("Bd", cgraph)
        self.assertNotIn("Bs", cgraph)

        # Must have L, A, O, P
        self.assertIn("Ld", cgraph)
        self.assertIn("Ad", cgraph)
        self.assertIn("Od", cgraph)
        self.assertIn("Pd", cgraph)

    def test_while_loop_graph_rules(self) -> None:
        """Test While-Loop graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {
                DstRow.L: [["I", 0, "int"]],
                DstRow.W: [["A", 0, "bool"]],
                DstRow.A: [["L", 0, "int"]],
                DstRow.O: [["A", 1, "int"]],
                DstRow.P: [["I", 0, "int"]],
                DstRow.U: [],
            }
        )
        cgraph = CGraph(jcg)

        # Must not have F, B
        self.assertNotIn("Fd", cgraph)
        self.assertNotIn("Bd", cgraph)
        self.assertNotIn("Bs", cgraph)

        # Must have L, W, A, O, P
        self.assertIn("Ld", cgraph)
        self.assertIn("Wd", cgraph)
        self.assertIn("Ad", cgraph)
        self.assertIn("Od", cgraph)
        self.assertIn("Pd", cgraph)

    def test_standard_graph_rules(self) -> None:
        """Test Standard graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {
                DstRow.A: [["I", 0, "int"]],
                DstRow.B: [["A", 0, "int"]],
                DstRow.O: [["B", 0, "int"]],
                DstRow.U: [],
            }
        )
        cgraph = CGraph(jcg)

        # Must not have F, L, W, P
        self.assertNotIn("Fd", cgraph)
        self.assertNotIn("Ld", cgraph)
        self.assertNotIn("Wd", cgraph)
        self.assertNotIn("Pd", cgraph)

        # Must have A, B, O
        self.assertIn("Ad", cgraph)
        self.assertIn("Bd", cgraph)
        self.assertIn("Od", cgraph)

    def test_primitive_graph_rules(self) -> None:
        """Test Primitive graph follows its specific rules."""
        jcg = json_cgraph_to_interfaces(
            {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        )
        cgraph = CGraph(jcg)

        # Must not have F, L, W, P, B
        self.assertNotIn("Fd", cgraph)
        self.assertNotIn("Ld", cgraph)
        self.assertNotIn("Wd", cgraph)
        self.assertNotIn("Pd", cgraph)
        self.assertNotIn("Bd", cgraph)
        self.assertNotIn("Bs", cgraph)

        # Must have A, O
        self.assertIn("Ad", cgraph)
        self.assertIn("Od", cgraph)


if __name__ == "__main__":
    unittest.main()
