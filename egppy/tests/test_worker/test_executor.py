"""Unit tests for the executor function."""

import unittest

from egppy.gc_types.gc import GCABC
from egppy.worker.executor.executor import ExecutionContext, FunctionInfo
from .xor_stack_gc import create_gc_matrix, expand_gc_matrix, f_7fffffff, rshift_1_gc


class TestExecutor(unittest.TestCase):
    """Unit tests for the executor function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class method for test setup."""
        cls.gcm: dict[int, dict[int, list[GCABC]]] = expand_gc_matrix(create_gc_matrix(8), 10)
        cls.gene_pool: list[GCABC] = [
            gc for ni in cls.gcm.values() for rs in ni.values() for gc in rs
        ]

    def setUp(self) -> None:
        super().setUp()
        # 2 different execution contexts
        self.ec1 = ExecutionContext(3)
        self.ec2 = ExecutionContext(50)
        # Hack in pre-defined function
        self.ec1.function_map[rshift_1_gc["signature"]] = FunctionInfo(f_7fffffff, 0x7FFFFFFF, 2)
        self.ec2.function_map[rshift_1_gc["signature"]] = FunctionInfo(f_7fffffff, 0x7FFFFFFF, 2)

    def test_basic_execution(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        gis1 = set()
        gis2 = set()
        for gc in self.gene_pool:
            for ec, gis in ((self.ec1, gis1), (self.ec2, gis2)):
                ng = ec.node_graph(gc)
                ng.line_count()
                ng.mermaid_chart()
                ntw = ng.create_code_graphs()
                for node in ntw:
                    if node.function_info.global_index not in gis:
                        gis.add(node.function_info.global_index)
                        node.code_mermaid_chart()
