"""Unit tests for the EndPoint, SourceEndPoint, and DestinationEndPoint classes."""

import unittest

from egppy.genetic_code.c_graph_constants import SINGLE_ONLY_ROWS, DstRow, EPCls, SrcRow
from egppy.genetic_code.endpoint import DstEndPoint, EndPoint, SrcEndPoint
from egppy.genetic_code.types_def import TypesDef, types_def_store


class TestEndPoint(unittest.TestCase):
    """Unit tests for the EndPoint class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        self.ep_src = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        self.ep_dst = EndPoint(DstRow.F, 0, EPCls.DST, "float")

    def test_comparison(self) -> None:
        """Test comparison operators."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.A, 1, EPCls.SRC, "int")
        self.assertLess(ep1, ep2)
        self.assertLessEqual(ep1, ep2)
        self.assertGreater(ep2, ep1)
        self.assertGreaterEqual(ep2, ep1)
        self.assertNotEqual(ep1, ep2)

    def test_comparison_with_non_endpoint(self) -> None:
        """Test comparison operators with non-EndPoint objects."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        # Comparison with non-EndPoint should return NotImplemented
        # pylint: disable=unnecessary-dunder-call
        result = ep.__lt__("not an endpoint")
        self.assertEqual(result, NotImplemented)
        result = ep.__le__("not an endpoint")
        self.assertEqual(result, NotImplemented)
        result = ep.__gt__("not an endpoint")
        self.assertEqual(result, NotImplemented)
        result = ep.__ge__("not an endpoint")
        self.assertEqual(result, NotImplemented)

    def test_connect(self) -> None:
        """Test connecting endpoints."""
        ep_src1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep_dst1 = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep_src1.connect(ep_dst1)
        self.assertEqual(ep_src1.refs, [[ep_dst1.row, ep_dst1.idx]])

        ep_src2 = EndPoint(SrcRow.L, 0, EPCls.SRC, "float")
        ep_dst1.connect(ep_src2)
        self.assertEqual(ep_dst1.refs, [[ep_src2.row, ep_src2.idx]])

        # Test connecting a destination to multiple sources (should replace)
        ep_src3 = EndPoint(SrcRow.B, 2, EPCls.SRC, "float")
        ep_dst1.connect(ep_src3)
        self.assertEqual(ep_dst1.refs, [[ep_src3.row, ep_src3.idx]])

        # Test single connection rows
        ep_f = EndPoint(DstRow.F, 0, EPCls.DST, "float")
        ep_f.refs = [[SrcRow.I, 0], [SrcRow.I, 1]]
        with self.assertRaises(ValueError):
            ep_f.verify()

    def test_equality(self) -> None:
        """Test equality and inequality of EndPoint instances."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep3 = EndPoint(DstRow.F, 0, EPCls.DST, "float")
        self.assertEqual(ep1, ep2)
        self.assertNotEqual(ep1, ep3)
        self.assertNotEqual(ep1, "not an endpoint")

    def test_hash(self) -> None:
        """Test hashing of endpoints."""
        h1 = hash(self.ep_src)
        self.ep_src.refs = [[SrcRow.A, 1]]
        h2 = hash(self.ep_src)
        self.assertNotEqual(h1, h2)
        h3 = hash(self.ep_src)
        h4 = hash(self.ep_src)
        self.assertEqual(h3, h4)

    def test_init(self) -> None:
        """Test EndPoint initialization."""
        self.assertEqual(self.ep_src.row, SrcRow.I)
        self.assertEqual(self.ep_src.idx, 0)
        self.assertEqual(self.ep_src.cls, EPCls.SRC)
        self.assertEqual(str(self.ep_src.typ), "int")
        self.assertEqual(self.ep_src.refs, [])

        self.assertEqual(self.ep_dst.row, DstRow.F)
        self.assertEqual(self.ep_dst.idx, 0)
        self.assertEqual(self.ep_dst.cls, EPCls.DST)
        self.assertEqual(str(self.ep_dst.typ), "float")
        self.assertEqual(self.ep_dst.refs, [])

        with self.assertRaises(ValueError):
            EndPoint(DstRow.F, 1, EPCls.DST, "float").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.A, 256, EPCls.DST, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(DstRow.A, -1, EPCls.SRC, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.L, 1, EPCls.SRC, "int").verify()

    def test_init_from_endpoint(self) -> None:
        """Test copy constructor from another EndPoint."""
        original = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [["A", 1]])
        copy = EndPoint(original)
        self.assertEqual(copy, original)
        # Verify deep copy of refs
        self.assertIsNot(copy.refs, original.refs)
        self.assertIsNot(copy.refs[0], original.refs[0])
        # Modify copy should not affect original
        copy.refs[0][1] = 99
        self.assertEqual(original.refs[0][1], 1)

    def test_init_from_tuple(self) -> None:
        """Test initialization from a 5-tuple."""
        tuple_data = (SrcRow.I, 0, EPCls.SRC, types_def_store["int"], [["A", 1]])
        ep = EndPoint(tuple_data)
        self.assertEqual(ep.row, SrcRow.I)
        self.assertEqual(ep.idx, 0)
        self.assertEqual(ep.cls, EPCls.SRC)
        self.assertEqual(str(ep.typ), "int")
        self.assertEqual(ep.refs, [["A", 1]])

        # Test with None refs
        tuple_data_no_refs = (SrcRow.I, 0, EPCls.SRC, types_def_store["int"], None)
        ep2 = EndPoint(tuple_data_no_refs)
        self.assertEqual(ep2.refs, [])

    def test_init_invalid_arguments(self) -> None:
        """Test initialization with invalid arguments."""
        # Invalid single argument (not EndPointABC or tuple)
        with self.assertRaises(TypeError):
            EndPoint("invalid")

        # Invalid tuple length
        with self.assertRaises(TypeError):
            EndPoint(("I", 0, EPCls.SRC))

        # Invalid number of arguments
        with self.assertRaises(TypeError):
            EndPoint()

        with self.assertRaises(TypeError):
            EndPoint("I", 0)

        with self.assertRaises(TypeError):
            EndPoint("I", 0, EPCls.SRC, "int", [], "extra")

    def test_init_with_types_def_instance(self) -> None:
        """Test initialization with TypesDef instance instead of string."""
        typ = types_def_store["float"]
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, typ)
        self.assertIsInstance(ep.typ, TypesDef)
        self.assertEqual(str(ep.typ), "float")

    def test_is_connected(self) -> None:
        """Test is_connected method."""
        self.assertFalse(self.ep_src.is_connected())
        self.ep_src.refs = [[DstRow.A, 1]]
        self.assertTrue(self.ep_src.is_connected())

    def test_str_representation(self) -> None:
        """Test string representation of endpoints."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [[DstRow.A, 1]])
        str_repr = str(ep)
        self.assertIn("EndPoint", str_repr)
        self.assertIn("row=I", str_repr)
        self.assertIn("idx=0", str_repr)
        self.assertIn("cls=", str_repr)
        self.assertIn("typ=int", str_repr)
        self.assertIn("refs", str_repr)

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        self.ep_src.refs = [[DstRow.A, 1]]
        json_obj = self.ep_src.to_json()
        expected_json = {
            "row": "I",
            "idx": 0,
            "cls": EPCls.SRC,
            "typ": "int",
            "refs": [["A", 1]],
        }
        self.assertEqual(json_obj, expected_json)

        ep_dst = EndPoint(DstRow.A, 0, EPCls.DST, "int", [["I", 0]])
        json_c_graph = ep_dst.to_json(json_c_graph=True)
        self.assertEqual(json_c_graph, ["I", 0, "int"])

        with self.assertRaises(ValueError):
            self.ep_src.to_json(json_c_graph=True)

        # Test error when DST endpoint has no refs for json_c_graph format
        ep_dst_no_refs = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        with self.assertRaises(ValueError):
            ep_dst_no_refs.to_json(json_c_graph=True)


class TestEndPointEdgeCases(unittest.TestCase):
    """Additional edge case tests for comprehensive coverage."""

    def test_boundary_index_values(self) -> None:
        """Test endpoints with boundary index values."""
        # Index 0 (minimum)
        ep0 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep0.verify()

        # Index 255 (maximum)
        ep255 = EndPoint(SrcRow.I, 255, EPCls.SRC, "int")
        ep255.verify()

        # Sort them
        self.assertLess(ep0, ep255)

    def test_comparison_same_idx(self) -> None:
        """Test comparison of endpoints with same index."""
        ep1 = EndPoint(SrcRow.I, 5, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 5, EPCls.SRC, "float")
        self.assertFalse(ep1 < ep2)
        self.assertTrue(ep1 <= ep2)
        self.assertFalse(ep1 > ep2)
        self.assertTrue(ep1 >= ep2)

    def test_connect_multiple_src_to_dst(self) -> None:
        """Test connecting multiple sources to multiple destinations."""
        src = SrcEndPoint(SrcRow.I, 0, "int")
        dst1 = DstEndPoint(DstRow.A, 0, "int")
        dst2 = DstEndPoint(DstRow.A, 1, "int")
        dst3 = DstEndPoint(DstRow.B, 0, "int")

        # Source can connect to multiple destinations
        src.connect(dst1)
        self.assertEqual(len(src.refs), 1)
        src.connect(dst2)
        self.assertEqual(len(src.refs), 2)
        src.connect(dst3)
        self.assertEqual(len(src.refs), 3)

        self.assertEqual(src.refs[0], ["A", 0])
        self.assertEqual(src.refs[1], ["A", 1])
        self.assertEqual(src.refs[2], ["B", 0])

    def test_connect_preserves_existing_refs_for_src(self) -> None:
        """Test that connect() appends to existing refs for source endpoints."""
        src = SrcEndPoint(SrcRow.I, 0, "int", [["A", 0]])
        dst = DstEndPoint(DstRow.A, 1, "int")

        src.connect(dst)
        self.assertEqual(len(src.refs), 2)
        self.assertEqual(src.refs[0], ["A", 0])
        self.assertEqual(src.refs[1], ["A", 1])

    def test_connect_replaces_refs_for_dst(self) -> None:
        """Test that connect() replaces refs for destination endpoints."""
        dst = DstEndPoint(DstRow.A, 0, "int", [["I", 0]])
        src = SrcEndPoint(SrcRow.I, 1, "int")

        dst.connect(src)
        self.assertEqual(len(dst.refs), 1)
        self.assertEqual(dst.refs[0], ["I", 1])

    def test_different_row_same_idx_comparison(self) -> None:
        """Test comparison of endpoints with different rows but same idx."""
        ep_src = EndPoint(SrcRow.I, 5, EPCls.SRC, "int")
        ep_dst = EndPoint(DstRow.A, 5, EPCls.DST, "int")
        # Comparison is based on idx only
        self.assertFalse(ep_src < ep_dst)
        self.assertTrue(ep_src <= ep_dst)

    def test_equality_different_refs_order(self) -> None:
        """Test that endpoints with different ref order are not equal."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [["A", 0], ["A", 1]])
        ep2 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [["A", 1], ["A", 0]])
        self.assertNotEqual(ep1, ep2)

    def test_equality_different_typ(self) -> None:
        """Test that endpoints with different types are not equal."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 0, EPCls.SRC, "float")
        self.assertNotEqual(ep1, ep2)

    def test_hash_changes_with_modifications(self) -> None:
        """Test that hash changes when endpoint is modified."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        h1 = hash(ep)

        ep.refs = [[DstRow.A, 0]]
        h2 = hash(ep)
        self.assertNotEqual(h1, h2)

        ep.refs.append([DstRow.A, 1])
        h3 = hash(ep)
        self.assertNotEqual(h2, h3)

    def test_hash_consistency_with_equality(self) -> None:
        """Test that equal endpoints have equal hashes."""
        ep1 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [[DstRow.A, 0]])
        ep2 = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [[DstRow.A, 0]])
        self.assertEqual(ep1, ep2)
        self.assertEqual(hash(ep1), hash(ep2))

    def test_init_refs_deep_copy(self) -> None:
        """Test that refs are deep copied during initialization."""
        original_refs = [[DstRow.A, 0], [DstRow.A, 1]]
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", original_refs)

        # Modify original refs
        original_refs[0][1] = 99
        original_refs.append(["B", 0])

        # Endpoint refs should be unchanged
        self.assertEqual(ep.refs, [["A", 0], ["A", 1]])

    def test_to_json_with_multiple_refs(self) -> None:
        """Test to_json() with multiple references."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [[DstRow.A, 0], [DstRow.A, 1], [DstRow.B, 2]])
        json_obj = ep.to_json()
        self.assertIsInstance(json_obj, dict)
        # Type narrowing for pyright
        if isinstance(json_obj, dict):
            refs_list = json_obj["refs"]
            self.assertEqual(len(refs_list), 3)
            self.assertEqual(refs_list[0], ["A", 0])
            self.assertEqual(refs_list[1], ["A", 1])
            self.assertEqual(refs_list[2], ["B", 2])

    def test_verify_all_valid_rows(self) -> None:
        """Test verify() with all valid row types."""
        # Test all source rows
        for row in SrcRow:
            idx = 0 if row in SINGLE_ONLY_ROWS else 5
            ep = EndPoint(row, idx, EPCls.SRC, "int")
            ep.verify()  # Should not raise

        # Test all destination rows (except U which is special)
        for row in DstRow:
            if row == DstRow.U:
                continue  # U is invalid
            idx = 0 if row in SINGLE_ONLY_ROWS else 5
            ep = EndPoint(row, idx, EPCls.DST, "int")
            ep.verify()  # Should not raise


class TestEndPointSubclasses(unittest.TestCase):
    """Unit tests for the EndPoint, SourceEndPoint, and DestinationEndPoint classes."""

    def test_destination_endpoint(self) -> None:
        """Test that a DestinationEndPoint is created correctly."""
        row = DstRow.F
        idx = 0
        typ: TypesDef | int | str = "float"
        refs = [["B", 2]]
        ep = DstEndPoint(row, idx, typ, refs)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EPCls.DST)
        self.assertEqual(str(ep.typ), "float")
        self.assertEqual(ep.refs, refs)

        with self.assertRaises(ValueError):
            DstEndPoint(DstRow.F, 1, "float").verify()

    def test_source_endpoint(self) -> None:
        """Test that a SourceEndPoint is created correctly."""
        row = SrcRow.I
        idx = 0
        typ: TypesDef | int | str = "int"
        refs = [["A", 1]]
        ep = SrcEndPoint(row, idx, typ, refs)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EPCls.SRC)
        self.assertEqual(str(ep.typ), "int")
        self.assertEqual(ep.refs, refs)


class TestEndPointVerify(unittest.TestCase):
    """Comprehensive tests for EndPoint.verify() method."""

    def test_verify_dst_max_one_reference(self) -> None:
        """Test verify() enforces DST endpoints can have at most 1 reference."""
        ep = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep.refs = [[SrcRow.I, 0], [SrcRow.I, 1]]
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("can have at most 1 reference", str(cm.exception))

    def test_verify_dst_must_reference_src_rows(self) -> None:
        """Test verify() ensures DST endpoints reference SRC rows."""
        ep = EndPoint(DstRow.A, 0, EPCls.DST, "int")
        ep.refs = [[DstRow.O, 0]]  # O is a destination-only row
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must reference a source row", str(cm.exception))
        self.assertIn("Valid source rows", str(cm.exception))

    def test_verify_dst_row_class_compatibility(self) -> None:
        """Test verify() enforces DST class must use destination rows."""
        # Try to create DST endpoint with source-only row 'I'
        ep = EndPoint(SrcRow.I, 0, EPCls.DST, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must use a destination row", str(cm.exception))
        self.assertIn("Valid destination rows", str(cm.exception))

    def test_verify_index_range(self) -> None:
        """Test verify() with invalid index values."""
        # Negative index
        ep = EndPoint(SrcRow.I, -1, EPCls.SRC, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must be between 0 and 255", str(cm.exception))

        # Index too large
        ep = EndPoint(SrcRow.I, 256, EPCls.SRC, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must be between 0 and 255", str(cm.exception))

    def test_verify_ref_index_must_be_int(self) -> None:
        """Test verify() requires ref index to be an integer."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [["A", "0"]]  # type: ignore  # Index as string
        with self.assertRaises(TypeError) as cm:
            ep.verify()
        self.assertIn("Reference index must be an integer", str(cm.exception))

    def test_verify_ref_index_range(self) -> None:
        """Test verify() requires ref index to be in valid range."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [[DstRow.A, -1]]  # Negative index
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must be between 0 and 255", str(cm.exception))

        ep.refs = [[DstRow.A, 256]]  # Too large
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must be between 0 and 255", str(cm.exception))

    def test_verify_ref_must_have_two_elements(self) -> None:
        """Test verify() requires refs to have exactly 2 elements."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [[DstRow.A]]  # Only 1 element
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must have exactly 2 elements", str(cm.exception))

        ep.refs = [[DstRow.A, 0, 0]]  # 3 elements
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must have exactly 2 elements", str(cm.exception))

    def test_verify_ref_row_must_be_string(self) -> None:
        """Test verify() requires ref row to be a string."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [[123, 0]]  # type: ignore  # Row as int
        with self.assertRaises(TypeError) as cm:
            ep.verify()
        self.assertIn("Reference row must be a string", str(cm.exception))

    def test_verify_ref_row_must_be_valid(self) -> None:
        """Test verify() requires ref row to be a valid row."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [["Z", 0]]  # type: ignore  # Invalid row
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("Reference row must be a valid row", str(cm.exception))
        self.assertIn("Valid rows", str(cm.exception))

    def test_verify_ref_structure_must_be_list(self) -> None:
        """Test verify() requires each ref to be a list."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [("A", 0)]  # type: ignore  # Tuple instead of list
        with self.assertRaises(TypeError) as cm:
            ep.verify()
        self.assertIn("Reference must be a list", str(cm.exception))

    def test_verify_row_u_invalid(self) -> None:
        """Test verify() rejects row 'U' for non-DST endpoints."""
        # U row is special and should trigger an error
        ep = EndPoint(DstRow.U, 0, EPCls.DST, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("cannot be 'U'", str(cm.exception))

    def test_verify_single_only_row_constraint(self) -> None:
        """Test verify() enforces single-endpoint constraint for F, W, L rows."""
        # F row can only have index 0
        ep = EndPoint(DstRow.F, 1, EPCls.DST, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("can only have a single endpoint", str(cm.exception))

        # W row can only have index 0
        ep = EndPoint(DstRow.W, 5, EPCls.DST, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("can only have a single endpoint", str(cm.exception))

        # L row (source) can only have index 0
        ep = EndPoint(SrcRow.L, 2, EPCls.SRC, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("can only have a single endpoint", str(cm.exception))

    def test_verify_src_must_reference_dst_rows(self) -> None:
        """Test verify() ensures SRC endpoints reference DST rows."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        ep.refs = [[SrcRow.I, 0]]  # I is a source-only row
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must reference a destination row", str(cm.exception))
        self.assertIn("Valid destination rows", str(cm.exception))

    def test_verify_src_row_class_compatibility(self) -> None:
        """Test verify() enforces SRC class must use source rows."""
        # Try to create SRC endpoint with destination-only row 'O'
        ep = EndPoint(DstRow.O, 0, EPCls.SRC, "int")
        with self.assertRaises(ValueError) as cm:
            ep.verify()
        self.assertIn("must use a source row", str(cm.exception))
        self.assertIn("Valid source rows", str(cm.exception))

    def test_verify_typ_must_be_typesdef(self) -> None:
        """Test verify() requires typ to be a TypesDef instance."""
        ep = EndPoint(SrcRow.I, 0, EPCls.SRC, "int")
        # Replace typ with invalid type
        ep.typ = "not_a_typesdef"  # type: ignore
        with self.assertRaises(TypeError) as cm:
            ep.verify()
        self.assertIn("must be a TypesDef instance", str(cm.exception))

    def test_verify_valid_endpoints(self) -> None:
        """Test verify() succeeds for valid endpoints."""
        # Valid SRC endpoint
        ep_src = EndPoint(SrcRow.I, 0, EPCls.SRC, "int", [["A", 0], ["A", 1]])
        ep_src.verify()  # Should not raise

        # Valid DST endpoint
        ep_dst = EndPoint(DstRow.A, 5, EPCls.DST, "float", [["I", 0]])
        ep_dst.verify()  # Should not raise

        # Valid endpoint with no refs
        ep_no_refs = EndPoint(SrcRow.B, 10, EPCls.SRC, "int")
        ep_no_refs.verify()  # Should not raise


if __name__ == "__main__":
    unittest.main()
