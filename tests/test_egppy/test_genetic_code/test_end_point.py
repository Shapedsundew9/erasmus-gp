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
        self.assertFalse(self.ep_src.is_frozen())

        self.assertEqual(self.ep_dst.row, DstRow.F)
        self.assertEqual(self.ep_dst.idx, 0)
        self.assertEqual(self.ep_dst.cls, EndPointClass.DST)
        self.assertEqual(str(self.ep_dst.typ), "float")
        self.assertFalse(self.ep_dst.is_frozen())

        with self.assertRaises(ValueError):
            EndPoint(DstRow.F, 1, EndPointClass.DST, "float").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.A, 256, EndPointClass.DST, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(DstRow.A, -1, EndPointClass.SRC, "int").verify()
        with self.assertRaises(ValueError):
            EndPoint(SrcRow.L, 1, EndPointClass.SRC, "int").verify()

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

    def test_copy(self) -> None:
        """Test copying an endpoint."""
        ep_copy = self.ep_src.copy()
        self.assertEqual(self.ep_src, ep_copy)
        self.assertIsNot(self.ep_src, ep_copy)
        # Changing the copy's type shouldn't affect the original
        ep_copy.typ = "float"
        self.assertNotEqual(self.ep_src.typ, ep_copy.typ)

    def test_freeze(self) -> None:
        """Test freezing an endpoint."""
        self.ep_src.freeze()
        self.assertTrue(self.ep_src.is_frozen())
        with self.assertRaises(AttributeError):
            self.ep_src.typ = "float"

    def test_hash(self) -> None:
        """Test hashing of endpoints."""
        h1 = hash(self.ep_src)
        # Hash should remain consistent
        h2 = hash(self.ep_src)
        self.assertEqual(h1, h2)
        self.ep_src.freeze()
        h3 = hash(self.ep_src)
        h4 = hash(self.ep_src)
        self.assertEqual(h3, h4)

    def test_to_json(self) -> None:
        """Test JSON conversion."""
        json_obj = self.ep_src.to_json()
        expected_json = {
            "row": "I",
            "idx": 0,
            "cls": EndPointClass.SRC,
            "typ": "int",
        }
        self.assertEqual(json_obj, expected_json)


class TestEndPointSubclasses(unittest.TestCase):
    """Unit tests for the EndPoint, SourceEndPoint, and DestinationEndPoint classes."""

    def test_source_end_point(self) -> None:
        """Test that a SourceEndPoint is created correctly."""
        row = SrcRow.I
        idx = 0
        typ: TypesDef | int | str = "int"
        ep = SrcEndPoint(row, idx, typ)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EndPointClass.SRC)
        self.assertEqual(str(ep.typ), "int")

    def test_destination_end_point(self) -> None:
        """Test that a DestinationEndPoint is created correctly."""
        row = DstRow.F
        idx = 0
        typ: TypesDef | int | str = "float"
        ep = DstEndPoint(row, idx, typ)
        self.assertIsInstance(ep, EndPoint)
        self.assertEqual(ep.row, row)
        self.assertEqual(ep.idx, idx)
        self.assertEqual(ep.cls, EndPointClass.DST)
        self.assertEqual(str(ep.typ), "float")

        with self.assertRaises(ValueError):
            DstEndPoint(DstRow.F, 1, "float").verify()


if __name__ == "__main__":
    unittest.main()
