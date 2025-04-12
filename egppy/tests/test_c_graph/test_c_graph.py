"""Test Connection Graphs."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.c_graph_class_factory import MutableCGraph
from tests.test_c_graph.c_graph_test_base import CGraphTestBase, MutableCGraphTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestFrozenCGraph(CGraphTestBase):
    """Test cases for the FrozenCGraph class."""


class TestMutableCGraph(MutableCGraphTestBase):
    """Test cases for the MutableCGraph class."""

    gcgtype = MutableCGraph
