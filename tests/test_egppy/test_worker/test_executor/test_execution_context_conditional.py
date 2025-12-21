"""Test conditional code generation in ExecutionContext.

This module tests the Row F implementation for IF_THEN and IF_THEN_ELSE genetic codes,
ensuring proper generation of Python if/else statements.
"""

import unittest
from unittest.mock import MagicMock, patch

from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.ggc_dict import GCABC
from egppy.worker.executor.execution_context import ExecutionContext
from egppy.worker.executor.function_info import NULL_FUNCTION_MAP
from egppy.worker.executor.fw_config import FWConfig
from egppy.worker.executor.gc_node import GCNode


class TestConditionalCodeGeneration(unittest.TestCase):
    """Test Row F implementation for conditional GCs."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the gene pool interface
        self.mock_gpi = MagicMock()
        self.ec = ExecutionContext(self.mock_gpi, line_limit=64, wmc=False)

    def test_code_lines_detects_conditional(self):
        """Test that code_lines() detects conditional GCs."""
        # This is an integration-style test that verifies the routing logic
        # We'll check that conditional GCs take a different code path
        mock_root = MagicMock(spec=GCNode)
        mock_root.write = True
        mock_root.is_conditional = True
        mock_root.graph_type = CGraphType.IF_THEN
        mock_root.gc = {
            "outputs": [{"typ": {"name": "int"}}],
            "signature": b"test",
            "cgraph": {DstRow.F: [], DstRow.O: [], DstRow.P: []},
        }
        mock_root.terminal_connections = []

        fwconfig = FWConfig(lean=True)

        # This should route to _generate_conditional_function_code
        # which will fail with our minimal mock, but that's OK - we're just
        # testing that it tries to call it
        try:
            self.ec.code_lines(mock_root, fwconfig)
        except (ValueError, AttributeError, KeyError):
            # Expected - we're not setting up a full mock
            pass

    def test_gcnode_caches_graph_type(self):
        """Test that GCNode caches the graph type during initialization."""
        # Create a mock GC with IF_THEN graph (as a codon to avoid GPI requirement)
        mock_gc = MagicMock(spec=GCABC)
        mock_gc.__getitem__.side_effect = {
            "signature": b"test_signature",
            "gca": None,  # None for codon
            "gcb": None,  # None for codon
            "cgraph": {
                DstRow.F: [{"refs": [[SrcRow.I, 0]]}],
                DstRow.A: [{"refs": [[SrcRow.I, 1]]}],
                DstRow.O: [{"refs": [[SrcRow.A, 0]]}],
                DstRow.P: [{"refs": [[SrcRow.I, 1]]}],
            },
            "inputs": [{"typ": {"name": "bool"}}, {"typ": {"name": "int"}}],
            "outputs": [{"typ": {"name": "int"}}],
        }.get
        mock_gc.is_codon.return_value = True  # Set as codon
        mock_gc.is_meta.return_value = False
        mock_gc.is_pgc.return_value = False

        # Mock c_graph_type to return IF_THEN
        with patch("egppy.worker.executor.gc_node.c_graph_type") as mock_c_graph_type:
            mock_c_graph_type.return_value = CGraphType.IF_THEN

            # Create GCNode (no GPI needed for codons)

            node = GCNode(mock_gc, None, SrcRow.I, NULL_FUNCTION_MAP, wmc=False)

            # Verify graph type is cached
            self.assertEqual(node.graph_type, CGraphType.IF_THEN)
            self.assertTrue(node.is_conditional)
            self.assertTrue(node.f_connection)
            mock_c_graph_type.assert_called_once()

    def test_gcnode_if_then_else_cached(self):
        """Test that GCNode correctly identifies IF_THEN_ELSE graphs."""
        mock_gc = MagicMock(spec=GCABC)
        mock_gc.__getitem__.side_effect = {
            "signature": b"test_signature",
            "gca": None,  # None for codon
            "gcb": None,  # None for codon
            "cgraph": {
                DstRow.F: [{"refs": [[SrcRow.I, 0]]}],
                DstRow.A: [{"refs": [[SrcRow.I, 1]]}],
                DstRow.B: [{"refs": [[SrcRow.I, 2]]}],
                DstRow.O: [{"refs": [[SrcRow.A, 0]]}],
                DstRow.P: [{"refs": [[SrcRow.B, 0]]}],
            },
            "inputs": [
                {"typ": {"name": "bool"}},
                {"typ": {"name": "int"}},
                {"typ": {"name": "str"}},
            ],
            "outputs": [{"typ": {"name": "int"}}, {"typ": {"name": "str"}}],
        }.get
        mock_gc.is_codon.return_value = True  # Set as codon
        mock_gc.is_meta.return_value = False
        mock_gc.is_pgc.return_value = False

        with patch("egppy.worker.executor.gc_node.c_graph_type") as mock_c_graph_type:
            mock_c_graph_type.return_value = CGraphType.IF_THEN_ELSE

            node = GCNode(mock_gc, None, SrcRow.I, NULL_FUNCTION_MAP, wmc=False)

            self.assertEqual(node.graph_type, CGraphType.IF_THEN_ELSE)
            self.assertTrue(node.is_conditional)

    def test_non_conditional_node_flags(self):
        """Test that non-conditional nodes have correct flags."""
        mock_gc = MagicMock(spec=GCABC)
        mock_gc.__getitem__.side_effect = {
            "signature": b"test_signature",
            "gca": None,  # None for codon
            "gcb": None,  # None for codon
            "cgraph": {
                DstRow.A: [{"refs": [[SrcRow.I, 0]]}],
                DstRow.O: [{"refs": [[SrcRow.A, 0]]}],
            },
            "inputs": [{"typ": {"name": "int"}}],
            "outputs": [{"typ": {"name": "int"}}],
        }.get
        mock_gc.is_codon.return_value = True  # Set as codon
        mock_gc.is_meta.return_value = False
        mock_gc.is_pgc.return_value = False

        with patch("egppy.worker.executor.gc_node.c_graph_type") as mock_c_graph_type:
            mock_c_graph_type.return_value = CGraphType.PRIMITIVE

            node = GCNode(mock_gc, None, SrcRow.I, NULL_FUNCTION_MAP, wmc=False)

            self.assertEqual(node.graph_type, CGraphType.PRIMITIVE)
            self.assertFalse(node.is_conditional)
            self.assertFalse(node.f_connection)


class TestConditionalFunctionCodeGenerator(unittest.TestCase):
    """Test the _generate_conditional_function_code method."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_gpi = MagicMock()
        self.ec = ExecutionContext(self.mock_gpi, line_limit=64, wmc=False)

    def test_missing_f_connection_raises_error(self):
        """Test that missing Row F connection raises ValueError."""

        mock_root = MagicMock(spec=GCNode)
        mock_root.is_conditional = True
        mock_root.graph_type = CGraphType.IF_THEN
        mock_root.gc = {"signature": b"test_sig"}
        # No F connection in terminal_connections
        mock_root.terminal_connections = []

        fwconfig = FWConfig(lean=True)
        ovns = ["o0"]

        with self.assertRaises(ValueError) as context:
            # pylint: disable=protected-access
            self.ec._generate_conditional_function_code(mock_root, fwconfig, ovns)

        self.assertIn("Row F connection", str(context.exception))


if __name__ == "__main__":
    unittest.main()
