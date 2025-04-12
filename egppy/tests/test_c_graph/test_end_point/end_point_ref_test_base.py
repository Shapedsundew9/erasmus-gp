"""Unit tests for the EndpointRef class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.end_point.end_point import EndPointRef
from egppy.c_graph.c_graph_constants import EndPointClass
from tests.test_c_graph.test_end_point.generic_end_point_test_base import GenericEndPointTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


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
