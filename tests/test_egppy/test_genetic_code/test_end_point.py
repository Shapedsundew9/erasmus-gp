"""Unit tests for the EndPoint, SourceEndPoint, and DestinationEndPoint classes."""

import unittest

from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.end_point import DstEndPoint, EndPoint, SrcEndPoint
from egppy.genetic_code.types_def import TypesDef


class TestEndPoint(unittest.TestCase):
    """Unit tests for the EndPoint class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        self.ep_src = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        self.ep_dst = EndPoint(DstRow.F, 0, EndPointClass.DST, "float")

    def test_init(self) -> None:
        """Test EndPoint initialization."""
        self.assertEqual(self.ep_src.row, SrcRow.I)
        self.assertEqual(self.ep_src.idx, 0)
        self.assertEqual(self.ep_src.cls, EndPointClass.SRC)
        self.assertEqual(str(self.ep_src.typ), "int")
        self.assertEqual(self.ep_src.refs, [])
        self.assertFalse(self.ep_src.is_frozen())

        self.assertEqual(self.ep_dst.row, DstRow.F)
        self.assertEqual(self.ep_dst.idx, 0)
        self.assertEqual(self.ep_dst.cls, EndPointClass.DST)
        self.assertEqual(str(self.ep_dst.typ), "float")
        self.assertEqual(self.ep_dst.refs, [])
        self.assertFalse(self.ep_dst.is_frozen())

        with self.assertRaises(ValueError):
            EndPoint(DstRow.F, 1, EndPointClass.DST, "float").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.A, 256, EndPointClass.DST, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(DstRow.A, -1, EndPointClass.SRC, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.L, 1, EndPointClass.SRC, "int").verify()

    def test_refs_setter(self) -> None:
        """Test the refs setter."""
        # Test with list of lists
        refs1 = [["A", 1]]
        self.ep_src.refs = refs1
        self.assertEqual(self.ep_src.refs, refs1)

        # Test with list of tuples
        refs2 = [("B", 2)]
        self.ep_src.refs = refs2  # type: ignore
        self.assertEqual(self.ep_src.refs, [["B", 2]])

        # Test with list of strings
        refs3 = ["A003"]
        self.ep_src.refs = refs3
        self.assertEqual(self.ep_src.refs, [["A", 3]])

        # Test with mixed list
        refs4 = [["I", 4], ("B", 5), "A006"]
        self.ep_src.refs = refs4  # type: ignore
        self.assertEqual(self.ep_src.refs, [["I", 4], ["B", 5], ["A", 6]])

        # Test with invalid type
        with self.assertRaises(TypeError):
            self.ep_src.refs = [123]  # type: ignore
        with self.assertRaises(ValueError):
            self.ep_src.refs = ["F001"]

    def test_typ_setter(self) -> None:
        """Test the typ setter."""
        self.ep_src.typ = "bool"
        self.assertEqual(str(self.ep_src.typ), "bool")
        new_typ = TypesDef("new_type", 99)
        self.ep_src.typ = new_typ
        self.assertEqual(self.ep_src.typ, new_typ)
        with self.assertRaises(AssertionError):
            self.ep_src.typ = 1.5  # type: ignore

    def test_equality(self) -> None:
        """Test equality and inequality of EndPoint instances."""
        ep1 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep3 = EndPoint(DstRow.F, 0, EndPointClass.DST, "float")
        self.assertEqual(ep1, ep2)
        self.assertNotEqual(ep1, ep3)
        self.assertNotEqual(ep1, "not an endpoint")

    def test_comparison(self) -> None:
        """Test comparison operators."""
        ep1 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep2 = EndPoint(SrcRow.A, 1, EndPointClass.SRC, "int")
        self.assertLess(ep1, ep2)
        self.assertLessEqual(ep1, ep2)
        self.assertGreater(ep2, ep1)
        self.assertGreaterEqual(ep2, ep1)
        self.assertNotEqual(ep1, ep2)

    def test_connect(self) -> None:
        """Test connecting endpoints."""
        ep_src1 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep_dst1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
        ep_src1.connect(ep_dst1)
        self.assertEqual(ep_src1.refs, [[ep_dst1.row, ep_dst1.idx]])

        ep_src2 = EndPoint(SrcRow.L, 0, EndPointClass.SRC, "float")
        ep_dst1.connect(ep_src2)
        self.assertEqual(ep_dst1.refs, [[ep_src2.row, ep_src2.idx]])

        # Test connecting a destination to multiple sources (should replace)
        ep_src3 = EndPoint(SrcRow.B, 2, EndPointClass.SRC, "float")
        ep_dst1.connect(ep_src3)
        self.assertEqual(ep_dst1.refs, [[ep_src3.row, ep_src3.idx]])

        # Test single connection rows
        ep_f = EndPoint(DstRow.F, 0, EndPointClass.DST, "float")
        ep_f.refs = [["I", 0], ["I", 1]]
        with self.assertRaises(ValueError):
            ep_f.verify()

    def test_copy(self) -> None:
        """Test copying an endpoint."""
        self.ep_src.refs = [["A", 1]]
        ep_copy = self.ep_src.copy()
        self.assertEqual(self.ep_src, ep_copy)
        self.assertIsNot(self.ep_src, ep_copy)
        ep_copy.refs = [["B", 2]]
        self.assertNotEqual(self.ep_src.refs, ep_copy.refs)

        ep_clean_copy = self.ep_src.copy(clean=True)
        self.assertEqual(ep_clean_copy.refs, [])

    def test_freeze(self) -> None:
        """Test freezing an endpoint."""
        self.ep_src.refs = [["A", 1]]
        self.ep_src.freeze()
        self.assertTrue(self.ep_src.is_frozen())
        with self.assertRaises(AttributeError):
            self.ep_src.refs = [["B", 2]]
        with self.assertRaises(AttributeError):
            self.ep_src.typ = "float"
        with self.assertRaises(RuntimeError):
            self.ep_src.connect(self.ep_dst)

        # Test freezing with invalid refs
        with self.assertRaises(ValueError):
            ep_invalid_ref = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int", [["Z", 0]])
            ep_invalid_ref.freeze()

    def test_hash(self) -> None:
        """Test hashing of endpoints."""
        h1 = hash(self.ep_src)
        self.ep_src.refs = [["A", 1]]
        h2 = hash(self.ep_src)
        self.assertNotEqual(h1, h2)
        self.ep_src.freeze()
        h3 = hash(self.ep_src)
        h4 = hash(self.ep_src)
        self.assertEqual(h3, h4)

    def test_is_connected(self) -> None:
        """Test is_connected method."""
        self.assertFalse(self.ep_src.is_connected())
        self.ep_src.refs = [["A", 1]]
        self.assertTrue(self.ep_src.is_connected())

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        self.ep_src.refs = [["A", 1]]
        json_obj = self.ep_src.to_json()
        expected_json = {
            "row": "I",
            "idx": 0,
            "cls": EndPointClass.SRC,
            "typ": "int",
            "refs": [["A", 1]],
        }
        self.assertEqual(json_obj, expected_json)

        ep_dst = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", [["I", 0]])
        json_c_graph = ep_dst.to_json(json_c_graph=True)
        self.assertEqual(json_c_graph, ["I", 0, "int"])

        with self.assertRaises(ValueError):
            self.ep_src.to_json(json_c_graph=True)


class TestEndPointSubclasses(unittest.TestCase):
    """Unit tests for the EndPoint, SourceEndPoint, and DestinationEndPoint classes."""

    def test_source_end_point(self) -> None:
        """Test that a SourceEndPoint is created correctly."""
        row = SrcRow.I
        idx = 0
        typ: TypesDef | int | str = "int"
        refs = [["A", 1]]
        ep = SrcEndPoint(row, idx, typ, refs)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EndPointClass.SRC)
        self.assertEqual(str(ep.typ), "int")
        self.assertEqual(ep.refs, refs)

    def test_destination_end_point(self) -> None:
        """Test that a DestinationEndPoint is created correctly."""
        row = DstRow.F
        idx = 0
        typ: TypesDef | int | str = "float"
        refs = [["B", 2]]
        ep = DstEndPoint(row, idx, typ, refs)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EndPointClass.DST)
        self.assertEqual(str(ep.typ), "float")
        self.assertEqual(ep.refs, refs)

        with self.assertRaises(ValueError):
            DstEndPoint(DstRow.F, 1, "float").verify()


if __name__ == "__main__":
    unittest.main()
