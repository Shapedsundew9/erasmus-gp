"""Test the builtin end point class."""
from tests.test_gc_graph.test_end_point.generic_end_point_test_base import GenericEndPointTestBase
from tests.test_gc_graph.test_end_point.end_point_ref_test_base import EndPointRefTestBase
from tests.test_gc_graph.test_end_point.x_end_point_ref_test_base import XEndPointRefTestBase

from egppy.gc_graph.end_point.builtin_end_point import BuiltinGenericEndPoint
from egppy.gc_graph.end_point.builtin_end_point import BuiltinEndPointRef
from egppy.gc_graph.end_point.builtin_end_point import BuiltinSrcEndPointRef, BuiltinDstEndPointRef


class BuiltinGenericEndPointTest(GenericEndPointTestBase):
    """Test cases for the BuiltinGenericEndPoint class."""
    endpoint_type = BuiltinGenericEndPoint

class BuiltinEndPointRefTest(EndPointRefTestBase):
    """Test cases for the BuiltinEndPoint class."""
    endpoint_type = BuiltinEndPointRef

class BuiltinSrcEndPointRefTest(XEndPointRefTestBase):
    """Test cases for the BuiltinSrcEndPointRef class."""
    endpoint_type = BuiltinSrcEndPointRef

class BuiltinDstEndPointRefTest(XEndPointRefTestBase):
    """Test cases for the BuiltinDstEndPointRef class."""
    endpoint_type = BuiltinDstEndPointRef
