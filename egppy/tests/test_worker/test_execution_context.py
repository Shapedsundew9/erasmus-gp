"""Unit tests for the executor function."""

import unittest
from random import seed

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging

from egppy.gc_types.gc import GCABC
from egppy.worker.executor.execution_context import ExecutionContext, FunctionInfo
from egppy.worker.executor.gc_node import GCNode
from egppy.worker.executor.context_writer import write_context_to_file
from .xor_stack_gc import create_gc_matrix, expand_gc_matrix, f_7fffffff, one_to_two, rshift_1_gc

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
enable_debug_logging()


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
        self.ec1.function_map[rshift_1_gc["signature"]] = FunctionInfo(
            f_7fffffff, 0x7FFFFFFF, 2, rshift_1_gc
        )
        self.ec2.function_map[rshift_1_gc["signature"]] = FunctionInfo(
            f_7fffffff, 0x7FFFFFFF, 2, rshift_1_gc
        )
        self.ec1.namespace["f_7fffffff"] = f_7fffffff
        self.ec2.namespace["f_7fffffff"] = f_7fffffff

    def test_write_function_ec1_basic(self) -> None:
        """Test the write_function function."""
        node = self.ec1.write_executable(one_to_two)
        self.assertIsInstance(node, GCNode)
        assert isinstance(node, GCNode), "node is not a GCNode"
        ftext = self.ec1.function_def(node, False)
        self.assertIsInstance(ftext, str)
        expected = (
            "def f_1(i: tuple[int]) -> tuple[int, int]:\n"
            '\t"""Signature: c3efa5f34e03343cd6efd96fed68e6309e48fd9b7d388f12851b04c25483e885\n'
            "\tCreated: 2025-03-29 22:05:08.489847+00:00\n"
            "\tLicense: MIT\n"
            "\tCreator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f\n"
            "\tGeneration: 4\n"
            '\t"""\n'
            "\to1 = f_0()\n"
            "\tt0 = f_7fffffff((o1,))\n"
            "\to0 = i[0] ^ t0\n"
            "\treturn o0, o1"
        )
        self.assertEqual(ftext, expected)

    def test_write_function_ec2_basic(self) -> None:
        """Test the write_function function."""
        node = self.ec2.write_executable(one_to_two)
        self.assertIsInstance(node, GCNode)
        assert isinstance(node, GCNode), "node is not a GCNode"
        ftext = self.ec2.function_def(node, False)
        self.assertIsInstance(ftext, str)
        expected = (
            "def f_0(i: tuple[int]) -> tuple[int, int]:\n"
            '\t"""Signature: c3efa5f34e03343cd6efd96fed68e6309e48fd9b7d388f12851b04c25483e885\n'
            "\tCreated: 2025-03-29 22:05:08.489847+00:00\n"
            "\tLicense: MIT\n"
            "\tCreator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f\n"
            "\tGeneration: 4\n"
            '\t"""\n'
            "\tt0 = 64\n"
            "\to1 = getrandbits(t0)\n"
            "\tt1 = f_7fffffff((o1,))\n"
            "\to0 = i[0] ^ t1\n"
            "\treturn o0, o1"
        )
        self.assertEqual(ftext, expected)

    def test_execute_basic(self) -> None:
        """Test the execute function."""
        self.ec1.write_executable(one_to_two)
        write_context_to_file(self.ec1)
        self.ec2.write_executable(one_to_two)
        write_context_to_file(self.ec2)
        # Must set the seed as we are using getrandbits
        # and it is not seeded in the function
        seed(0)
        r1 = self.ec1.execute(one_to_two["signature"], (0x12345678,))
        # Must set the seed as we are using getrandbits
        # and it is not seeded in the function for reproducibility
        seed(0)
        r2 = self.ec2.execute(one_to_two["signature"], (0x12345678,))
        self.assertIsInstance(r1, tuple)
        self.assertIsInstance(r2, tuple)
        self.assertEqual(r1, r2)

    def test_write_gene_pool_ec1(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        for idx, gc in enumerate(self.gene_pool):
            _logger.debug("Writing gc %d", idx)
            self.ec1.write_executable(gc)
        write_context_to_file(self.ec1)

    def test_write_gene_pool_ec2(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        for idx, gc in enumerate(self.gene_pool):
            _logger.debug("Writing gc %d", idx)
            self.ec2.write_executable(gc)
        write_context_to_file(self.ec2)
