"""Unit tests for the executor function."""

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging

from egppy.gc_types.gc import GCABC
from egppy.worker.executor.execution_context import ExecutionContext, FunctionInfo

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

    def test_write_function_ec1_basic(self) -> None:
        """Test the write_function function."""
        self.ec1.write_executable(one_to_two)

    def test_write_function_ec2_basic(self) -> None:
        """Test the write_function function."""
        self.ec2.write_executable(one_to_two)

    def test_write_gene_pool_ec1(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        for idx, gc in enumerate(self.gene_pool):
            _logger.debug("Writing gc %d", idx)
            self.ec1.write_executable(gc)

    def test_write_gene_pool_ec2(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        for idx, gc in enumerate(self.gene_pool):
            _logger.debug("Writing gc %d", idx)
            self.ec2.write_executable(gc)
