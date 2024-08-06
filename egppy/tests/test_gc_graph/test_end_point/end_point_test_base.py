"""Unit tests for the End Point classes."""
from tests.test_gc_graph.test_end_point.x_end_point_ref_test_base import XEndPointRefTestBase
from egppy.gc_graph.ep_type import ep_type_lookup
from egppy.gc_graph.end_point.end_point import (EndPoint, SrcEndPointRef,
    DstEndPointRef)
from egppy.gc_graph.typing import ROWS, DestinationRow, EndPointClass, SourceRow
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EndPointTestBase(XEndPointRefTestBase):
    """Test cases for the EndPointRef class."""

    # Override this in subclasses.
    endpoint_type = EndPoint
    src_ref_type = SrcEndPointRef
    dst_ref_type = DstEndPointRef

    @classmethod
    def get_src_ref_cls(cls) -> type:
        """Get the Source Ref class."""
        return cls.src_ref_type

    @classmethod
    def get_dst_ref_cls(cls) -> type:
        """Get the Destination Ref class."""
        return cls.dst_ref_type

    def setUp(self) -> None:
        """
        Set up the test case by initializing the row, index, and endpoint.
        """
        # As a destination row
        self.row1 = DestinationRow.B
        self.idx1 = 0
        self.typ1 = ep_type_lookup['n2v']['int']
        self.cls1 = EndPointClass.DST
        self.refs1 = [self.get_src_ref_cls()(SourceRow.A, 0)]
        self.endpoint = self.get_endpoint_cls()(
            self.row1, self.idx1, self.typ1, self.cls1, self.refs1)

        # Endpoint2 must be same class but different with invalid refs
        self.row2 = DestinationRow.B
        self.idx2 = 1
        self.typ2 = ep_type_lookup['n2v']['float']
        self.cls2 = EndPointClass.DST
        self.refs2 = [self.get_src_ref_cls()(SourceRow.B, 1)]
        self.endpoint2 = self.get_endpoint_cls()(
            self.row2, self.idx2, self.typ2, self.cls2, self.refs2)

    def test_eq(self) -> None:
        """
        Test the __eq__() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint, self.endpoint)
        self.assertNotEqual(self.endpoint, self.endpoint2)

    def test_get_typ(self) -> None:
        """
        Test the get_typ() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.get_typ(), self.typ1)
        self.assertEqual(self.endpoint2.get_typ(), self.typ2)

    def test_get_cls(self) -> None:
        """
        Test the get_cls() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.get_cls(), self.cls1)
        self.assertEqual(self.endpoint2.get_cls(), self.cls2)

    def test_get_refs(self) -> None:
        """
        Test the get_refs() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint.get_refs(), self.refs1)
        self.assertEqual(self.endpoint2.get_refs(), self.refs2)

    def test_as_ref(self) -> None:
        """
        Test the as_ref() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        ref_cls = self.get_src_ref_cls() if self.endpoint.is_src() else self.get_dst_ref_cls()
        self.assertEqual(self.endpoint.as_ref(), ref_cls(self.row1, self.idx1))

    def test_copy(self) -> None:
        """
        Test the copy() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.endpoint, self.endpoint.copy())
        self.assertEqual(self.endpoint2, self.endpoint2.copy())

    def test_move_cls_copy(self) -> None:
        """
        Test the move_copy() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_row = SourceRow.I if self.endpoint.is_dst() else DestinationRow.B
        new_cls = EndPointClass.SRC if self.endpoint.is_dst() else EndPointClass.DST
        new_endpoint = self.endpoint.move_cls_copy(new_row, new_cls)
        self.assertEqual(new_endpoint.get_row(), new_row)
        self.assertEqual(new_endpoint.get_cls(), new_cls)
        self.assertEqual(new_endpoint.get_typ(), self.typ1)
        self.assertEqual(new_endpoint.get_refs(), [])

    def test_move_copy(self) -> None:
        """
        Test the move_copy() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_row = SourceRow.I if self.endpoint.is_src() else DestinationRow.A
        new_endpoint = self.endpoint.move_copy(new_row)
        self.assertEqual(new_endpoint.get_row(), new_row)
        self.assertEqual(new_endpoint.get_cls(), self.cls1)
        self.assertEqual(new_endpoint.get_typ(), self.typ1)
        self.assertEqual(new_endpoint.get_refs(), [])

    def test_del_invalid_refs(self) -> None:
        """
        Test the del_invalid_refs() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        self.endpoint.del_invalid_refs()
        self.assertEqual(self.endpoint.get_refs(), self.refs1)
        self.endpoint2.del_invalid_refs()
        self.assertEqual(self.endpoint2.get_refs(), [])

    def test_set_typ(self) -> None:
        """
        Test the set_typ() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_typ = ep_type_lookup['n2v']['str']
        self.endpoint.set_typ(new_typ)
        self.assertEqual(self.endpoint.get_typ(), new_typ)

    def test_set_cls(self) -> None:
        """
        Test the set_cls() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_cls = EndPointClass.SRC
        self.endpoint.set_cls(new_cls)
        self.assertEqual(self.endpoint.get_cls(), new_cls)

    def test_set_refs(self) -> None:
        """
        Test the set_refs() method of the endpoint.
        """
        if self.running_in_test_base_class():
            return
        new_refs = [self.get_src_ref_cls()(ROWS[1], 0)]
        self.endpoint.set_refs(new_refs)
        self.assertEqual(self.endpoint.get_refs(), new_refs)
