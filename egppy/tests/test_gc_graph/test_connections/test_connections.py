"""Test the Connections class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from tests.test_gc_graph.test_connections.connections_test_base import (
    ConnectionsTestBase,
    MutableConnectionsTestBase,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleConnectionsTest(ConnectionsTestBase):
    """Test cases for the Tuple Connections class."""


class ListConnectionsTest(MutableConnectionsTestBase):
    """Test cases for the List Connections class."""
