"""Test the builtin end point class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.end_point import (
    DstEndPointRef,
    EndPoint,
    EndPointRef,
    GenericEndPoint,
    SrcEndPointRef,
)
from tests.test_gc_graph.test_end_point.end_point_ref_test_base import EndPointRefTestBase
from tests.test_gc_graph.test_end_point.end_point_test_base import EndPointTestBase
from tests.test_gc_graph.test_end_point.generic_end_point_test_base import GenericEndPointTestBase
from tests.test_gc_graph.test_end_point.x_end_point_ref_test_base import XEndPointRefTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class BuiltinGenericEndPointTest(GenericEndPointTestBase):
    """Test cases for the BuiltinGenericEndPoint class."""

    endpoint_type = GenericEndPoint


class BuiltinEndPointRefTest(EndPointRefTestBase):
    """Test cases for the BuiltinEndPoint class."""

    endpoint_type = EndPointRef


class BuiltinSrcEndPointRefTest(XEndPointRefTestBase):
    """Test cases for the BuiltinSrcEndPointRef class."""

    endpoint_type = SrcEndPointRef


class BuiltinDstEndPointRefTest(XEndPointRefTestBase):
    """Test cases for the BuiltinDstEndPointRef class."""

    endpoint_type = DstEndPointRef


class BuiltinEndPointTest(EndPointTestBase):
    """Test cases for the BuiltinEndPoint class."""

    endpoint_type = EndPoint
