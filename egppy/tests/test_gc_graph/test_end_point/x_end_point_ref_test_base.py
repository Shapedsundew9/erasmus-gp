"""Unit tests for the Src & Dst EndpointRef classes."""
from tests.test_gc_graph.test_end_point.end_point_ref_test_base import EndPointRefTestBase
from egppy.gc_graph.egp_typing import EndPointClass
from egppy.gc_graph.end_point.end_point import DstEndPointRef
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class XEndPointRefTestBase(EndPointRefTestBase):
    """Test cases for the EndPointRef class."""

    # Override this in subclasses.
    endpoint_type = DstEndPointRef

    def test_key(self) -> None:
        """
        Test the key() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertIn(self.endpoint.key_base(), self.endpoint.key())
        if self.endpoint.is_src():
            self.assertEqual(self.endpoint.key(), self.endpoint.force_key(EndPointClass.SRC))
        if self.endpoint.is_dst():
            self.assertEqual(self.endpoint.key(), self.endpoint.force_key(EndPointClass.DST))

    def test_invert_key(self) -> None:
        """
        Test the invert_key() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertIn(self.endpoint.key_base(), self.endpoint.invert_key())
        if self.endpoint.is_src():
            self.assertEqual(self.endpoint.invert_key(),
                self.endpoint.force_key(EndPointClass.DST))
        if self.endpoint.is_dst():
            self.assertEqual(self.endpoint.invert_key(),
                self.endpoint.force_key(EndPointClass.SRC))
