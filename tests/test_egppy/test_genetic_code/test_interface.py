"""Unit tests for the Interface, SrcInterface, and DstInterface classes."""

import unittest

from egppy.genetic_code.c_graph_constants import DstRow, EPCls, SrcRow
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.endpoint_abc import EndPointABC
from egppy.genetic_code.interface import (
    DstInterface,
    Interface,
    SrcInterface,
    unpack_dst_ref,
    unpack_ref,
    unpack_src_ref,
)
from egppy.genetic_code.types_def import types_def_store


class TestInterface(unittest.TestCase):
    """Unit tests for the Interface class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        # Create some test endpoints with proper indices
        self.ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        self.ep2 = EndPoint(DstRow.A, 1, EPCls.DST, "float")
        self.ep3 = EndPoint(DstRow.A, 0, EPCls.DST, "bool")  # Index 0 for standalone use

        # Create test interfaces
        self.interface1 = Interface([self.ep1, self.ep2], DstRow.A)
        self.interface2 = Interface([self.ep3], DstRow.A)

    def test_add_operator_basic(self) -> None:
        """Test basic addition of two interfaces."""
        interface1 = Interface([self.ep1, self.ep2], DstRow.A)
        interface2 = Interface([self.ep3], DstRow.A)

        result = interface1 + interface2

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)
        self.assertEqual(result[2].typ.uid, self.ep3.typ.uid)

        # Check indices are correct
        self.assertEqual(result[0].idx, 0)
        self.assertEqual(result[1].idx, 1)
        self.assertEqual(result[2].idx, 2)

    def test_add_operator_both_empty(self) -> None:
        """Test adding two empty interfaces."""
        empty1 = Interface([], DstRow.A)
        empty2 = Interface([], DstRow.A)
        result = empty1 + empty2

        self.assertEqual(len(result), 0)

    def test_add_operator_chaining(self) -> None:
        """Test chaining multiple additions."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep2 = EndPoint(DstRow.A, 0, EPCls.DST, "float")
        ep3 = EndPoint(DstRow.A, 0, EPCls.DST, "bool")

        interface1 = Interface([ep1], DstRow.A)
        interface2 = Interface([ep2], DstRow.A)
        interface3 = Interface([ep3], DstRow.A)

        result = interface1 + interface2 + interface3

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)
        self.assertEqual(result[2].typ.uid, ep3.typ.uid)

    def test_add_operator_empty_left(self) -> None:
        """Test adding empty interface on the left."""
        empty = Interface([], DstRow.A)
        result = empty + self.interface1

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)

    def test_add_operator_empty_right(self) -> None:
        """Test adding empty interface on the right."""
        empty = Interface([], DstRow.A)
        result = self.interface1 + empty

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)

    def test_add_operator_original_unchanged(self) -> None:
        """Test that addition doesn't modify original interfaces."""
        interface1 = Interface([self.ep1, self.ep2], DstRow.A)
        interface2 = Interface([self.ep3], DstRow.A)

        original_len1 = len(interface1)
        original_len2 = len(interface2)

        _ = interface1 + interface2

        self.assertEqual(len(interface1), original_len1)
        self.assertEqual(len(interface2), original_len2)

    def test_add_operator_wrong_type(self) -> None:
        """Test that adding non-Interface raises TypeError."""
        with self.assertRaises(TypeError) as context:
            _ = self.interface1 + "not an interface"  # type: ignore
        self.assertIn("Interface", str(context.exception))

    def test_append(self) -> None:
        """Test appending endpoints to interface."""
        interface = Interface([self.ep1], DstRow.A)
        ep_new = EndPoint(DstRow.A, 1, EPCls.DST, "str")
        interface.append(ep_new)
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[1].typ.uid, ep_new.typ.uid)
        # Check that idx was updated
        self.assertEqual(interface[1].idx, 1)

    def test_cls_empty_interface(self) -> None:
        """Test that cls() returns DST for empty interface."""
        interface = Interface([], DstRow.A)
        self.assertEqual(interface.cls, EPCls.DST)

    def test_cls_with_endpoints(self) -> None:
        """Test that cls() returns the class of the first endpoint."""
        interface = Interface([self.ep1, self.ep2], DstRow.A)
        self.assertEqual(interface.cls, EPCls.DST)

    def test_consistency(self) -> None:
        """Test the consistency() method."""
        # Consistency is normally called by verify() when CONSISTENCY logging is enabled
        # We can call it directly here
        interface = Interface([self.ep1, self.ep2], DstRow.A)
        interface.consistency()  # Should not raise

    def test_consistency_with_logging(self) -> None:
        """Test the consistency() method with CONSISTENCY logging enabled."""
        # pylint: disable=import-outside-toplevel
        from egpcommon.egp_log import CONSISTENCY

        # Get the logger
        from egppy.genetic_code import interface as interface_module

        # pylint: disable=protected-access
        logger = interface_module._logger

        # Save original level
        original_level = logger.level

        try:
            # Enable CONSISTENCY logging
            logger.setLevel(CONSISTENCY)

            # Create and verify interface - this should trigger consistency()
            interface = Interface([self.ep1, self.ep2], DstRow.A)
            interface.verify()  # This will call consistency() internally

        finally:
            # Restore original level
            logger.setLevel(original_level)

    def test_equality(self) -> None:
        """Test equality of Interface instances."""
        interface1 = Interface([self.ep1, self.ep2], DstRow.A)
        interface2 = Interface([self.ep1, self.ep2], DstRow.A)
        interface3 = Interface([self.ep1], DstRow.A)

        self.assertEqual(interface1, interface2)
        self.assertNotEqual(interface1, interface3)
        self.assertNotEqual(interface1, "not an interface")

    def test_extend(self) -> None:
        """Test extending interface with multiple endpoints."""
        interface = Interface([self.ep1], DstRow.A)
        new_eps: list[EndPointABC] = [
            EndPoint(DstRow.A, 1, EPCls.DST, "str"),
            EndPoint(DstRow.A, 2, EPCls.DST, "bool"),
        ]
        interface.extend(new_eps)
        self.assertEqual(len(interface), 3)
        # Check that indices were updated
        self.assertEqual(interface[1].idx, 1)
        self.assertEqual(interface[2].idx, 2)

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        self.assertEqual(self.interface1[0], self.ep1)
        self.assertEqual(self.interface1[1], self.ep2)

    def test_hash(self) -> None:
        """Test that hash is computed correctly."""
        interface1 = Interface([self.ep1, self.ep2], DstRow.A)
        interface2 = Interface([self.ep1, self.ep2], DstRow.A)
        # Equal interfaces should have equal hashes
        self.assertEqual(hash(interface1), hash(interface2))

    def test_init_with_5tuple(self) -> None:
        """Test initialization with EndPointMemberType (5-tuple)."""
        interface = Interface([(DstRow.A, 0, EPCls.DST, "int", None)], DstRow.A)
        self.assertEqual(len(interface), 1)
        self.assertEqual(str(interface[0].typ), "int")

    def test_init_with_endpoints(self) -> None:
        """Test Interface initialization with EndPoint objects."""
        interface = Interface([self.ep1, self.ep2], DstRow.A)
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], self.ep1)
        self.assertEqual(interface[1], self.ep2)

    def test_init_with_invalid_type(self) -> None:
        """Test that ValueError is raised with invalid endpoint type."""
        with self.assertRaises(TypeError) as context:
            Interface([123.45], row=DstRow.A)  # type: ignore
        self.assertIn("Unsupported endpoints type", str(context.exception))

    def test_init_with_sequences_3tuple(self) -> None:
        """Test initialization with sequences containing [ref_row, ref_idx, typ]."""
        interface = Interface([["I", 0, "int"], ["I", 1, "float"]], row=DstRow.A)
        self.assertEqual(len(interface), 2)
        self.assertEqual(str(interface[0].typ), "int")
        self.assertEqual(str(interface[1].typ), "float")

    def test_init_with_source_row(self) -> None:
        """Test initialization with source row creates source endpoints."""
        interface = Interface(["int", "float"], row=SrcRow.I)
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0].cls, EPCls.SRC)
        self.assertEqual(interface[1].cls, EPCls.SRC)

    def test_init_with_types(self) -> None:
        """Test Interface initialization with type strings."""
        interface = Interface(["int", "float", "bool"], row=DstRow.A)
        self.assertEqual(len(interface), 3)
        self.assertEqual(str(interface[0].typ), "int")
        self.assertEqual(str(interface[1].typ), "float")
        self.assertEqual(str(interface[2].typ), "bool")

    def test_init_with_typesdef(self) -> None:
        """Test initialization with TypesDef objects."""
        int_type = types_def_store["int"]
        float_type = types_def_store["float"]
        interface = Interface([int_type, float_type], row=DstRow.A)
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0].typ, int_type)
        self.assertEqual(interface[1].typ, float_type)

    def test_iteration(self) -> None:
        """Test iteration over interface."""
        eps = list(self.interface1)
        self.assertEqual(len(eps), 2)
        self.assertEqual(eps[0], self.ep1)
        self.assertEqual(eps[1], self.ep2)

    def test_len(self) -> None:
        """Test __len__ method."""
        self.assertEqual(len(self.interface1), 2)
        self.assertEqual(len(self.interface2), 1)

    def test_ordered_td_uids(self) -> None:
        """Test the ordered_td_uids() method."""
        interface = Interface(["int", "float", "bool"], row=DstRow.A)
        uids = interface.sorted_unique_td_uids()
        # Should return sorted unique UIDs
        self.assertEqual(len(uids), 3)
        self.assertEqual(uids, sorted(uids))

    def test_setitem(self) -> None:
        """Test setting an endpoint at a specific index."""
        interface = Interface([self.ep1, self.ep2], DstRow.A)
        new_ep = EndPoint(DstRow.A, 0, EPCls.DST, "str")
        interface[0] = new_ep
        self.assertEqual(interface[0].typ.uid, new_ep.typ.uid)
        self.assertEqual(interface[0].idx, 0)  # Index should be updated

    def test_setitem_out_of_range(self) -> None:
        """Test that IndexError is raised for out-of-range index."""
        interface = Interface([self.ep1], DstRow.A)
        with self.assertRaises(IndexError) as context:
            interface[5] = self.ep2
        self.assertIn("out of range", str(context.exception))

    def test_setitem_wrong_type(self) -> None:
        """Test that TypeError is raised when setting non-EndPoint."""
        interface = Interface([self.ep1], DstRow.A)
        with self.assertRaises(TypeError) as context:
            interface[0] = "not an endpoint"  # type: ignore
        self.assertIn("Expected EndPointABC", str(context.exception))

    def test_str(self) -> None:
        """Test string representation."""
        s = str(self.interface1)
        self.assertIn("Interface", s)
        self.assertIn("int", s)
        self.assertIn("float", s)

    def test_to_json(self) -> None:
        """Test the to_json() method."""
        interface = Interface([self.ep1, self.ep2], row=DstRow.A)
        json_data = interface.to_json()
        self.assertIsInstance(json_data, list)
        self.assertEqual(len(json_data), 2)

    def test_to_json_c_graph(self) -> None:
        """Test the to_json() method with json_c_graph=True."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int", [["I", 0]])
        interface = Interface([ep1], row=DstRow.A)
        json_data = interface.to_json(json_c_graph=True)
        self.assertIsInstance(json_data, list)
        self.assertEqual(len(json_data), 1)

    def test_to_td_uids(self) -> None:
        """Test the to_td_uids() method."""
        interface = Interface(["int", "float"], row=DstRow.A)
        uids = interface.to_td_uids()
        self.assertIsInstance(uids, list)
        self.assertEqual(len(uids), 2)

    def test_types(self) -> None:
        """Test the types() method."""
        interface = Interface(["int", "float", "int"], row=DstRow.A)
        otu, indices = interface.types_and_indices()
        # Should have 2 unique types (int and float)
        self.assertEqual(len(otu), 2)
        # Indices should map to the ordered types
        self.assertEqual(len(indices), 3)

    def test_unconnected_eps(self) -> None:
        """Test the unconnected_eps() method."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")  # No refs
        ep2 = EndPoint(DstRow.A, 1, EPCls.DST, "float", [["I", 0]])  # Has ref
        interface = Interface([ep1, ep2], DstRow.A)
        unconnected = interface.unconnected_eps()
        self.assertEqual(len(unconnected), 1)
        self.assertEqual(unconnected[0], ep1)

    def test_verify_different_classes(self) -> None:
        """Test that verify fails when endpoints have different classes."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep2 = EndPoint(SrcRow.A, 1, EPCls.SRC, "float")
        interface = Interface.__new__(Interface)
        interface.endpoints = [ep1, ep2]
        with self.assertRaises(ValueError) as context:
            interface.verify()
        self.assertIn("same class", str(context.exception))

    def test_verify_different_rows(self) -> None:
        """Test that verify fails when endpoints have different rows."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep2 = EndPoint(DstRow.B, 1, EPCls.DST, "float")
        interface = Interface.__new__(Interface)
        interface.endpoints = [ep1, ep2]
        with self.assertRaises(ValueError) as context:
            interface.verify()
        self.assertIn("same row", str(context.exception))

    def test_verify_empty_interface(self) -> None:
        """Test that verify passes for empty interface."""
        interface = Interface([], DstRow.A)
        interface.verify()  # Should not raise

    def test_verify_not_endpoint_instances(self) -> None:
        """Test that verify fails when endpoints are not EndPoint instances."""
        interface = Interface.__new__(Interface)
        interface.endpoints = [self.ep1, "not an endpoint"]  # type: ignore
        with self.assertRaises(ValueError) as context:
            interface.verify()
        self.assertIn("EndPoint instances", str(context.exception))


class TestUnpackFunctions(unittest.TestCase):
    """Unit tests for the unpack_ref, unpack_src_ref, and unpack_dst_ref functions."""

    def test_unpack_dst_ref(self) -> None:
        """Test unpack_dst_ref with destination row."""
        ref = ["O", 7]
        row, idx = unpack_dst_ref(ref)
        self.assertEqual(row, DstRow.O)
        self.assertEqual(idx, 7)

    def test_unpack_ref_with_list(self) -> None:
        """Test unpack_ref with a list."""
        ref = ["A", 5]
        row, idx = unpack_ref(ref)
        self.assertEqual(row, "A")
        self.assertEqual(idx, 5)

    def test_unpack_ref_with_tuple(self) -> None:
        """Test unpack_ref with a tuple."""
        ref = (SrcRow.I, 10)
        row, idx = unpack_ref(ref)
        self.assertEqual(row, SrcRow.I)
        self.assertEqual(idx, 10)

    def test_unpack_src_ref(self) -> None:
        """Test unpack_src_ref with source row."""
        ref = ["I", 3]
        row, idx = unpack_src_ref(ref)
        self.assertEqual(row, SrcRow.I)
        self.assertEqual(idx, 3)


class TestSrcInterface(unittest.TestCase):
    """Unit tests for the SrcInterface class."""

    def test_add_src_interfaces(self) -> None:
        """Test adding two SrcInterface instances."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 0, EPCls.SRC, "float")

        interface1 = SrcInterface([ep1], SrcRow.I)
        interface2 = SrcInterface([ep2], SrcRow.I)

        result = interface1 + interface2

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)

    def test_init(self) -> None:
        """Test SrcInterface initialization."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 1, EPCls.SRC, "float")
        interface = SrcInterface([ep1, ep2], SrcRow.I)

        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], ep1)
        self.assertEqual(interface[1], ep2)

    def test_init_with_types(self) -> None:
        """Test SrcInterface initialization with type strings."""
        interface = SrcInterface(["int", "float"], row=SrcRow.I)
        self.assertEqual(len(interface), 2)
        self.assertEqual(str(interface[0].typ), "int")
        self.assertEqual(str(interface[1].typ), "float")


class TestDstInterface(unittest.TestCase):
    """Unit tests for the DstInterface class."""

    def test_add_dst_interfaces(self) -> None:
        """Test adding two DstInterface instances."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep2 = EndPoint(DstRow.A, 0, EPCls.DST, "float")

        interface1 = DstInterface([ep1], DstRow.A)
        interface2 = DstInterface([ep2], DstRow.A)

        result = interface1 + interface2

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)

    def test_init(self) -> None:
        """Test DstInterface initialization."""
        ep1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep2 = EndPoint(DstRow.A, 1, EPCls.DST, "float")
        interface = DstInterface([ep1, ep2], DstRow.A)

        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], ep1)
        self.assertEqual(interface[1], ep2)

    def test_init_with_sequences(self) -> None:
        """Test DstInterface initialization with sequences."""
        interface = DstInterface([["I", 0, "int"]], row=DstRow.A)
        self.assertEqual(len(interface), 1)
        self.assertEqual(str(interface[0].typ), "int")

    def test_init_with_types(self) -> None:
        """Test DstInterface initialization with type strings."""
        interface = DstInterface(["int", "float"], row=DstRow.A)
        self.assertEqual(len(interface), 2)
        self.assertEqual(str(interface[0].typ), "int")
        self.assertEqual(str(interface[1].typ), "float")


if __name__ == "__main__":
    unittest.main()
