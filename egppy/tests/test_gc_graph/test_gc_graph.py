"""Test GC Graphs."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.gc_graph_class_factory import MutableGCGraph
from tests.test_gc_graph.gc_graph_test_base import GCGraphTestBase, MutableGCGraphTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestFrozenGCGraph(GCGraphTestBase):
    """Test cases for the FrozenGCGraph class."""


class TestMutableGCGraph(MutableGCGraphTestBase):
    """Test cases for the MutableGCGraph class."""

    gcgtype = MutableGCGraph
