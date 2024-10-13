"""Test the builtin end point class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from tests.test_gc_graph.test_interface.interface_test_base import (
    InterfaceTestBase,
    MutableInterfaceTestBase,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TupleInterfaceTest(InterfaceTestBase):
    """Test cases for the Tuple Interface class."""


class ListInterfaceTest(MutableInterfaceTestBase):
    """Test cases for the List Interface class."""
