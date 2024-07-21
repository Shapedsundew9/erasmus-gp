"""Unit tests for the EndpointRef class."""
from tests.test_gc_graph.test_end_point.generic_end_point_test_base import GenericEndPointTestBase
from egppy.gc_graph.end_point.end_point import EndPointRef
from egppy.gc_graph.egp_typing import EndPointClass


class EndPointRefTestBase(GenericEndPointTestBase):
    """Test cases for the EndPointRef class."""

    # Override this in subclasses.
    endpoint_type = EndPointRef

    def test_eq(self) -> None:
        """
        Test the __eq__() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint, self.get_endpoint_cls()(self.row1, self.idx1))
        self.assertNotEqual(self.endpoint, self.get_endpoint_cls()(self.row2, self.idx2))

    def test_force_key(self) -> None:
        """
        Test the force_key() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertIn(self.endpoint.key_base(), self.endpoint.force_key(EndPointClass.SRC))
        self.assertIn(self.endpoint.key_base(), self.endpoint.force_key(EndPointClass.DST))
