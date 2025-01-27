"""Unit tests for the executor function."""

import unittest
from egppy.worker.executor import (
    CodeConnection,
    node_graph,
    line_count,
    code_graph,
)
from .xor_stack_gc import gene_pool


class TestExecutor(unittest.TestCase):
    """Unit tests for the executor function."""

    def test_nodegraph(self) -> None:
        """Test the node_graph function."""
        for limit in (4, 5, 7, 12, 17, 32):
            for gc in gene_pool:
                ng = node_graph(gc, limit)
                line_count(ng, limit)
                cc: list[CodeConnection] = code_graph(ng)
