"""Comprehensive unit tests for json_cgraph module.

This module provides comprehensive testing of all functions in the json_cgraph module,
including valid_src_rows, valid_dst_rows, valid_rows, valid_jcg, json_cgraph_to_interfaces,
and c_graph_type.
"""

import unittest
from unittest.mock import patch

from egpcommon.egp_log import DEBUG
from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.json_cgraph import (
    CGT_VALID_DST_ROWS,
    CGT_VALID_ROWS,
    CGT_VALID_SRC_ROWS,
    _logger,
    c_graph_type,
    json_cgraph_to_interfaces,
    valid_dst_rows,
    valid_jcg,
    valid_rows,
    valid_src_rows,
)


class TestValidSrcRowsComprehensive(unittest.TestCase):
    """Comprehensive tests for valid_src_rows function."""

    def test_valid_src_rows_if_then(self) -> None:
        """Test valid_src_rows for IF_THEN graph type."""
        result = valid_src_rows(CGraphType.IF_THEN)

        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.F, result)
        self.assertIn(DstRow.O, result)
        self.assertIn(DstRow.P, result)
        self.assertIn(DstRow.U, result)

        self.assertEqual(result[DstRow.F], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I}))

    def test_valid_src_rows_if_then_else(self) -> None:
        """Test valid_src_rows for IF_THEN_ELSE graph type."""
        result = valid_src_rows(CGraphType.IF_THEN_ELSE)

        self.assertIn(DstRow.B, result)
        self.assertEqual(result[DstRow.B], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.P], frozenset({SrcRow.I, SrcRow.B}))

    def test_valid_src_rows_empty(self) -> None:
        """Test valid_src_rows for EMPTY graph type."""
        result = valid_src_rows(CGraphType.EMPTY)

        self.assertIn(DstRow.O, result)
        self.assertEqual(result[DstRow.O], frozenset())

    def test_valid_src_rows_for_loop(self) -> None:
        """Test valid_src_rows for FOR_LOOP graph type."""
        result = valid_src_rows(CGraphType.FOR_LOOP)

        self.assertIn(DstRow.L, result)
        self.assertEqual(result[DstRow.L], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I, SrcRow.L}))

    def test_valid_src_rows_while_loop(self) -> None:
        """Test valid_src_rows for WHILE_LOOP graph type."""
        result = valid_src_rows(CGraphType.WHILE_LOOP)

        self.assertIn(DstRow.W, result)
        self.assertEqual(result[DstRow.W], frozenset({SrcRow.A}))

    def test_valid_src_rows_standard(self) -> None:
        """Test valid_src_rows for STANDARD graph type."""
        result = valid_src_rows(CGraphType.STANDARD)

        self.assertIn(DstRow.B, result)
        self.assertEqual(result[DstRow.B], frozenset({SrcRow.I, SrcRow.A}))
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A, SrcRow.B}))

    def test_valid_src_rows_primitive(self) -> None:
        """Test valid_src_rows for PRIMITIVE graph type."""
        result = valid_src_rows(CGraphType.PRIMITIVE)

        self.assertEqual(result[DstRow.A], frozenset({SrcRow.I}))
        self.assertEqual(result[DstRow.O], frozenset({SrcRow.I, SrcRow.A}))

    def test_valid_src_rows_unknown(self) -> None:
        """Test valid_src_rows for UNKNOWN graph type (superset)."""
        result = valid_src_rows(CGraphType.UNKNOWN)

        # UNKNOWN should contain all possible valid connections
        self.assertIn(DstRow.F, result)
        self.assertIn(DstRow.L, result)
        self.assertIn(DstRow.W, result)
        self.assertIn(DstRow.B, result)

    def test_valid_src_rows_reserved(self) -> None:
        """Test valid_src_rows for RESERVED graph types."""
        for reserved_type in [
            CGraphType.RESERVED_8,
            CGraphType.RESERVED_9,
            CGraphType.RESERVED_10,
        ]:
            result = valid_src_rows(reserved_type)
            # Should only have U row (superset)
            self.assertEqual(len(result), 1)
            self.assertIn(DstRow.U, result)

    def test_valid_src_rows_u_is_superset(self) -> None:
        """Test that U row is always a superset of all other sources."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            result = valid_src_rows(graph_type)
            all_sources = frozenset().union(
                *[srcs for dst, srcs in result.items() if dst != DstRow.U]
            )
            self.assertEqual(result[DstRow.U], all_sources, f"Failed for {graph_type}")


class TestValidDstRowsComprehensive(unittest.TestCase):
    """Comprehensive tests for valid_dst_rows function."""

    def test_valid_dst_rows_if_then(self) -> None:
        """Test valid_dst_rows for IF_THEN graph type."""
        result = valid_dst_rows(CGraphType.IF_THEN)

        self.assertIn(SrcRow.I, result)
        self.assertIn(SrcRow.A, result)
        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.F, DstRow.O, DstRow.P}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))

    def test_valid_dst_rows_if_then_else(self) -> None:
        """Test valid_dst_rows for IF_THEN_ELSE graph type."""
        result = valid_dst_rows(CGraphType.IF_THEN_ELSE)

        self.assertIn(SrcRow.B, result)
        self.assertEqual(result[SrcRow.B], frozenset({DstRow.P}))

    def test_valid_dst_rows_empty(self) -> None:
        """Test valid_dst_rows for EMPTY graph type."""
        result = valid_dst_rows(CGraphType.EMPTY)

        self.assertIn(SrcRow.I, result)
        self.assertEqual(result[SrcRow.I], frozenset())

    def test_valid_dst_rows_for_loop(self) -> None:
        """Test valid_dst_rows for FOR_LOOP graph type."""
        result = valid_dst_rows(CGraphType.FOR_LOOP)

        self.assertIn(SrcRow.L, result)
        self.assertEqual(result[SrcRow.L], frozenset({DstRow.A}))

    def test_valid_dst_rows_while_loop(self) -> None:
        """Test valid_dst_rows for WHILE_LOOP graph type."""
        result = valid_dst_rows(CGraphType.WHILE_LOOP)

        self.assertIn(SrcRow.A, result)
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O, DstRow.W}))

    def test_valid_dst_rows_standard(self) -> None:
        """Test valid_dst_rows for STANDARD graph type."""
        result = valid_dst_rows(CGraphType.STANDARD)

        self.assertEqual(result[SrcRow.B], frozenset({DstRow.O}))

    def test_valid_dst_rows_primitive(self) -> None:
        """Test valid_dst_rows for PRIMITIVE graph type."""
        result = valid_dst_rows(CGraphType.PRIMITIVE)

        self.assertEqual(result[SrcRow.I], frozenset({DstRow.A, DstRow.O}))
        self.assertEqual(result[SrcRow.A], frozenset({DstRow.O}))

    def test_valid_dst_rows_unknown(self) -> None:
        """Test valid_dst_rows for UNKNOWN graph type."""
        result = valid_dst_rows(CGraphType.UNKNOWN)

        # Should contain all possible destinations
        self.assertIn(SrcRow.L, result)
        self.assertIn(DstRow.U, result[SrcRow.I])

    def test_valid_dst_rows_reserved(self) -> None:
        """Test valid_dst_rows for RESERVED graph types."""
        for reserved_type in [
            CGraphType.RESERVED_8,
            CGraphType.RESERVED_9,
            CGraphType.RESERVED_10,
        ]:
            result = valid_dst_rows(reserved_type)
            self.assertEqual(result, {})


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

    def test_valid_rows_primitive(self) -> None:
        """Test valid_rows for PRIMITIVE graph type."""
        result = valid_rows(CGraphType.PRIMITIVE)

        # PRIMITIVE should have I, A, O
        self.assertIn(SrcRow.I, result)
        self.assertIn(DstRow.A, result)
        self.assertIn(DstRow.O, result)
        self.assertNotIn(DstRow.B, result)
        self.assertNotIn(DstRow.F, result)


class TestValidJCG(unittest.TestCase):
    """Test the valid_jcg function for JSON Connection Graph validation."""

    def test_valid_jcg_empty(self) -> None:
        """Test validation of an empty JSON connection graph."""
        jcg = {DstRow.O: [], DstRow.U: []}
        self.assertTrue(valid_jcg(jcg))

    def test_valid_jcg_primitive(self) -> None:
        """Test validation of a primitive JSON connection graph."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        self.assertTrue(valid_jcg(jcg))

    def test_valid_jcg_invalid_key(self) -> None:
        """Test that invalid keys raise ValueError."""
        jcg = {"InvalidKey": [], DstRow.O: [], DstRow.U: []}
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        self.assertIn("Invalid key", str(context.exception))

    def test_valid_jcg_invalid_value_type(self) -> None:
        """Test that invalid value types raise TypeError."""
        jcg = {DstRow.O: "not a list", DstRow.U: []}
        with self.assertRaises(TypeError) as context:
            valid_jcg(jcg)
        self.assertIn("Invalid value", str(context.exception))

    def test_valid_jcg_invalid_endpoint_structure(self) -> None:
        """Test that invalid endpoint structures raise TypeError."""
        jcg = {DstRow.O: ["not a list"], DstRow.U: []}
        with self.assertRaises(TypeError) as context:
            valid_jcg(jcg)
        self.assertIn("Expected a list", str(context.exception))

    def test_valid_jcg_invalid_source_row_type(self) -> None:
        """Test that non-string source rows raise TypeError."""
        jcg = {DstRow.O: [[123, 0, "int"]], DstRow.U: []}
        with self.assertRaises(TypeError) as context:
            valid_jcg(jcg)
        self.assertIn("Expected a destination row", str(context.exception))

    def test_valid_jcg_invalid_source_row_value(self) -> None:
        """Test that invalid source row values raise ValueError."""
        jcg = {DstRow.O: [["X", 0, "int"]], DstRow.U: []}
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        self.assertIn("Expected a valid source row", str(context.exception))

    def test_valid_jcg_invalid_index_type(self) -> None:
        """Test that non-integer indices raise TypeError."""
        jcg = {DstRow.O: [["I", "0", "int"]], DstRow.U: []}
        with self.assertRaises(TypeError) as context:
            valid_jcg(jcg)
        self.assertIn("Expected an integer index", str(context.exception))

    def test_valid_jcg_invalid_type_type(self) -> None:
        """Test that non-string types raise TypeError."""
        jcg = {DstRow.O: [["I", 0, 123]], DstRow.U: []}
        with self.assertRaises(TypeError) as context:
            valid_jcg(jcg)
        self.assertIn("Expected a list of endpoint int types", str(context.exception))

    def test_valid_jcg_invalid_source_for_destination(self) -> None:
        """Test that invalid source->destination connections raise ValueError."""
        # In PRIMITIVE graphs, only I can connect to A
        jcg = {DstRow.A: [["B", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        self.assertIn("Invalid source row", str(context.exception))

    def test_valid_jcg_index_out_of_range_negative(self) -> None:
        """Test that negative indices raise ValueError."""
        # Create a STANDARD graph with valid structure first
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.O: [["A", -1, "int"]],  # Negative index on valid row
            DstRow.U: [],
        }
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        # The error is caught during index validation
        self.assertIn("Index", str(context.exception))

    def test_valid_jcg_index_out_of_range_too_large(self) -> None:
        """Test that indices >= 256 raise ValueError."""
        # Create a STANDARD graph with valid structure
        jcg = {
            DstRow.A: [["I", 0, "int"]],  # Only 1 element (index 0)
            DstRow.O: [["A", 256, "int"]],  # Index 256 is out of range
            DstRow.U: [],
        }
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        # The error is caught during index validation
        self.assertIn("Index", str(context.exception))

    def test_valid_jcg_invalid_endpoint_type(self) -> None:
        """Test that invalid TypesDef types raise ValueError."""
        # Create a STANDARD graph structure to avoid early validation
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.O: [["A", 0, "invalid_type"]],  # Invalid type string
            DstRow.U: [],
        }
        with self.assertRaises(ValueError) as context:
            valid_jcg(jcg)
        # The error is caught during endpoint type validation
        self.assertIn("Invalid endpoint type", str(context.exception))

    def test_valid_jcg_missing_destination_row(self) -> None:
        """Test that references to non-existent destination rows are caught."""
        # Create graph where O references a non-existent row B
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.O: [["B", 0, "int"]],  # References B which doesn't exist
            DstRow.U: [],
        }
        with self.assertRaises(ValueError) as ctx:
            valid_jcg(jcg)
        # Validation catches invalid source row B for destination O
        self.assertIn("Invalid source row", str(ctx.exception))


class TestJsonCGraphToInterfaces(unittest.TestCase):
    """Test the json_cgraph_to_interfaces function."""

    def test_json_cgraph_to_interfaces_empty(self) -> None:
        """Test conversion of empty graph."""
        jcg = {DstRow.O: [], DstRow.U: []}
        interfaces = json_cgraph_to_interfaces(jcg)

        self.assertIn("Is", interfaces)
        self.assertIn("Od", interfaces)
        self.assertEqual(len(interfaces["Od"]), 0)

    def test_json_cgraph_to_interfaces_creates_missing_interfaces(self) -> None:
        """Test that missing complementary interfaces are created."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        interfaces = json_cgraph_to_interfaces(jcg)

        # Should create both Ad and As
        self.assertIn("Ad", interfaces)
        self.assertIn("As", interfaces)

    def test_json_cgraph_to_interfaces_creates_pd_for_conditional(self) -> None:
        """Test that Pd is created for conditional graphs."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],  # P is required for conditional graphs
            DstRow.U: [],
        }
        interfaces = json_cgraph_to_interfaces(jcg)

        # Should create Pd for conditional graphs
        self.assertIn("Pd", interfaces)

    def test_json_cgraph_to_interfaces_creates_pd_for_loop(self) -> None:
        """Test that Pd is created for loop graphs."""
        jcg = {
            DstRow.L: [["I", 0, "list"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],  # P is required for loop graphs
            DstRow.U: [],
        }
        interfaces = json_cgraph_to_interfaces(jcg)

        # Should create Pd for loop graphs
        self.assertIn("Pd", interfaces)

    def test_json_cgraph_to_interfaces_type_inconsistency(self) -> None:
        """Test that type inconsistencies raise ValueError."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["I", 0, "str"]],  # Same source, different type
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }

        with self.assertRaises(ValueError) as context:
            json_cgraph_to_interfaces(jcg)
        self.assertIn("Type inconsistency", str(context.exception))

    def test_json_cgraph_to_interfaces_with_debug_logging(self) -> None:
        """Test that validation is called when DEBUG logging is enabled."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            # Should not raise - valid graph
            interfaces = json_cgraph_to_interfaces(jcg)
            self.assertIsInstance(interfaces, dict)

    def test_json_cgraph_to_interfaces_sorted_source_endpoints(self) -> None:
        """Test that source endpoints are sorted by index."""
        jcg = {
            DstRow.A: [["I", 2, "int"], ["I", 0, "str"], ["I", 1, "bool"]],
            DstRow.O: [["A", 0, "str"]],
            DstRow.U: [],
        }
        interfaces = json_cgraph_to_interfaces(jcg)

        # Source endpoints should be sorted by index
        is_interface = interfaces["Is"]
        indices = [ep[1] for ep in is_interface]
        self.assertEqual(indices, [0, 1, 2])

    def test_json_cgraph_to_interfaces_creates_as_when_ad_exists(self) -> None:
        """Test that As is created when Ad exists but As doesn't."""
        # This tests line 320 - creating As when Ad exists
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        interfaces = json_cgraph_to_interfaces(jcg)
        # Both As and Ad should exist
        self.assertIn("As", interfaces)
        self.assertIn("Ad", interfaces)

    def test_json_cgraph_to_interfaces_creates_bs_when_bd_exists(self) -> None:
        """Test that Bs is created when Bd exists but Bs doesn't."""
        # This tests line 324 - creating Bs when Bd exists
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }
        interfaces = json_cgraph_to_interfaces(jcg)
        # Both Bs and Bd should exist
        self.assertIn("Bs", interfaces)
        self.assertIn("Bd", interfaces)


class TestCGraphType(unittest.TestCase):
    """Test the c_graph_type function."""

    def test_c_graph_type_empty(self) -> None:
        """Test identification of EMPTY graph type."""
        jcg = {DstRow.O: [], DstRow.U: []}
        self.assertEqual(c_graph_type(jcg), CGraphType.EMPTY)

    def test_c_graph_type_primitive(self) -> None:
        """Test identification of PRIMITIVE graph type."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        self.assertEqual(c_graph_type(jcg), CGraphType.PRIMITIVE)

    def test_c_graph_type_if_then(self) -> None:
        """Test identification of IF_THEN graph type."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.IF_THEN)

    def test_c_graph_type_if_then_else(self) -> None:
        """Test identification of IF_THEN_ELSE graph type."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.B: [["I", 2, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["B", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.IF_THEN_ELSE)

    def test_c_graph_type_for_loop(self) -> None:
        """Test identification of FOR_LOOP graph type."""
        jcg = {
            DstRow.L: [["I", 0, "list"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.FOR_LOOP)

    def test_c_graph_type_while_loop(self) -> None:
        """Test identification of WHILE_LOOP graph type."""
        jcg = {
            DstRow.L: [["I", 0, "int"]],
            DstRow.W: [["A", 0, "bool"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 1, "int"]],
            DstRow.P: [["I", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.WHILE_LOOP)

    def test_c_graph_type_standard(self) -> None:
        """Test identification of STANDARD graph type."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["A", 0, "int"]],
            DstRow.O: [["B", 0, "int"]],
            DstRow.U: [],
        }
        self.assertEqual(c_graph_type(jcg), CGraphType.STANDARD)

    def test_c_graph_type_with_cgraph_abc(self) -> None:
        """Test c_graph_type with CGraphABC instance."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.O: [["A", 0, "int"]], DstRow.U: []}
        interfaces = json_cgraph_to_interfaces(jcg)
        cgraph = CGraph(interfaces)

        # Should work with CGraphABC instance
        self.assertEqual(c_graph_type(cgraph), CGraphType.PRIMITIVE)

    def test_c_graph_type_debug_missing_o(self) -> None:
        """Test c_graph_type raises ValueError when O is missing (DEBUG mode)."""
        jcg = {DstRow.A: [["I", 0, "int"]], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("must have a row O", str(context.exception))

    def test_c_graph_type_debug_missing_u(self) -> None:
        """Test c_graph_type raises ValueError when U is missing (DEBUG mode)."""
        jcg = {DstRow.O: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("must have a row U", str(context.exception))

    def test_c_graph_type_debug_conditional_missing_a(self) -> None:
        """Test c_graph_type raises ValueError for conditional without A (DEBUG mode)."""
        jcg = {DstRow.F: [["I", 0, "bool"]], DstRow.O: [], DstRow.P: [], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("conditional connection graphs must have a row A", str(context.exception))

    def test_c_graph_type_debug_conditional_missing_p(self) -> None:
        """Test c_graph_type raises ValueError for conditional without P (DEBUG mode)."""
        jcg = {DstRow.F: [["I", 0, "bool"]], DstRow.A: [], DstRow.O: [], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("conditional connection graphs must have a row P", str(context.exception))

    def test_c_graph_type_debug_loop_missing_a(self) -> None:
        """Test c_graph_type raises ValueError for loop without A (DEBUG mode)."""
        jcg = {DstRow.L: [["I", 0, "list"]], DstRow.O: [], DstRow.P: [], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("loop connection graphs must have a row A", str(context.exception))

    def test_c_graph_type_debug_loop_missing_p(self) -> None:
        """Test c_graph_type raises ValueError for loop without P (DEBUG mode)."""
        jcg = {DstRow.L: [["I", 0, "list"]], DstRow.A: [], DstRow.O: [], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("loop connection graphs must have a row P", str(context.exception))

    def test_c_graph_type_debug_standard_missing_a(self) -> None:
        """Test c_graph_type raises ValueError for standard without A (DEBUG mode)."""
        jcg = {DstRow.B: [["I", 0, "int"]], DstRow.O: [], DstRow.U: []}

        with patch.object(_logger, "isEnabledFor", return_value=True):
            with self.assertRaises(ValueError) as context:
                c_graph_type(jcg)
            self.assertIn("standard graph must have a row A", str(context.exception))

    def test_c_graph_type_non_debug_if_then(self) -> None:
        """Test c_graph_type for IF_THEN without DEBUG (line 358)."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        with patch.object(_logger, "isEnabledFor", return_value=False):
            self.assertEqual(c_graph_type(jcg), CGraphType.IF_THEN)

    def test_c_graph_type_non_debug_for_loop(self) -> None:
        """Test c_graph_type for FOR_LOOP without DEBUG (line 360)."""
        jcg = {
            DstRow.L: [["I", 0, "list"]],
            DstRow.A: [["L", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }
        with patch.object(_logger, "isEnabledFor", return_value=False):
            self.assertEqual(c_graph_type(jcg), CGraphType.FOR_LOOP)

    def test_c_graph_type_non_debug_standard(self) -> None:
        """Test c_graph_type for STANDARD without DEBUG (line 362)."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }
        with patch.object(_logger, "isEnabledFor", return_value=False):
            self.assertEqual(c_graph_type(jcg), CGraphType.STANDARD)


class TestConstants(unittest.TestCase):
    """Test the pre-computed constant dictionaries."""

    def test_cgt_valid_src_rows_constant(self) -> None:
        """Test that CGT_VALID_SRC_ROWS matches valid_src_rows function."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertEqual(
                CGT_VALID_SRC_ROWS[graph_type],
                valid_src_rows(graph_type),
                f"Mismatch for {graph_type}",
            )

    def test_cgt_valid_dst_rows_constant(self) -> None:
        """Test that CGT_VALID_DST_ROWS matches valid_dst_rows function."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertEqual(
                CGT_VALID_DST_ROWS[graph_type],
                valid_dst_rows(graph_type),
                f"Mismatch for {graph_type}",
            )

    def test_cgt_valid_rows_constant(self) -> None:
        """Test that CGT_VALID_ROWS matches valid_rows function."""
        for graph_type in CGraphType:
            if graph_type.name.startswith("RESERVED"):
                continue
            self.assertEqual(
                CGT_VALID_ROWS[graph_type], valid_rows(graph_type), f"Mismatch for {graph_type}"
            )


if __name__ == "__main__":
    unittest.main()
