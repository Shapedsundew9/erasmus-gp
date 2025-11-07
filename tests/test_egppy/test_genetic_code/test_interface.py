"""Unit tests for the Interface, SrcInterface, and DstInterface classes."""

import unittest

from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.end_point_abc import EndPointABC
from egppy.genetic_code.interface import DstInterface, Interface, SrcInterface


class TestInterface(unittest.TestCase):
    """Unit tests for the Interface class."""

    def setUp(self) -> None:
        """Set up for the tests."""
        # Create some test endpoints with proper indices
        self.ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
        self.ep2 = EndPoint(DstRow.A, 1, EndPointClass.DST, "float")
        self.ep3 = EndPoint(DstRow.A, 0, EndPointClass.DST, "bool")  # Index 0 for standalone use

        # Create test interfaces
        self.interface1 = Interface([self.ep1, self.ep2])
        self.interface2 = Interface([self.ep3])

    def test_init_with_endpoints(self) -> None:
        """Test Interface initialization with EndPoint objects."""
        interface = Interface([self.ep1, self.ep2])
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], self.ep1)
        self.assertEqual(interface[1], self.ep2)

    def test_init_with_types(self) -> None:
        """Test Interface initialization with type strings."""
        interface = Interface(["int", "float", "bool"], row=DstRow.A)
        self.assertEqual(len(interface), 3)
        self.assertEqual(str(interface[0].typ), "int")
        self.assertEqual(str(interface[1].typ), "float")
        self.assertEqual(str(interface[2].typ), "bool")

    def test_equality(self) -> None:
        """Test equality of Interface instances."""
        interface1 = Interface([self.ep1, self.ep2])
        interface2 = Interface([self.ep1, self.ep2])
        interface3 = Interface([self.ep1])

        self.assertEqual(interface1, interface2)
        self.assertNotEqual(interface1, interface3)
        self.assertNotEqual(interface1, "not an interface")

    def test_len(self) -> None:
        """Test __len__ method."""
        self.assertEqual(len(self.interface1), 2)
        self.assertEqual(len(self.interface2), 1)

    def test_getitem(self) -> None:
        """Test __getitem__ method."""
        self.assertEqual(self.interface1[0], self.ep1)
        self.assertEqual(self.interface1[1], self.ep2)

    def test_iteration(self) -> None:
        """Test iteration over interface."""
        eps = list(self.interface1)
        self.assertEqual(len(eps), 2)
        self.assertEqual(eps[0], self.ep1)
        self.assertEqual(eps[1], self.ep2)

    def test_str(self) -> None:
        """Test string representation."""
        s = str(self.interface1)
        self.assertIn("Interface", s)
        self.assertIn("int", s)
        self.assertIn("float", s)

    def test_append(self) -> None:
        """Test appending endpoints to interface."""
        interface = Interface([self.ep1])
        ep_new = EndPoint(DstRow.A, 1, EndPointClass.DST, "str")
        interface.append(ep_new)
        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[1].typ.uid, ep_new.typ.uid)
        # Check that idx was updated
        self.assertEqual(interface[1].idx, 1)

    def test_extend(self) -> None:
        """Test extending interface with multiple endpoints."""
        interface = Interface([self.ep1])
        new_eps: list[EndPointABC] = [
            EndPoint(DstRow.A, 1, EndPointClass.DST, "str"),
            EndPoint(DstRow.A, 2, EndPointClass.DST, "bool"),
        ]
        interface.extend(new_eps)
        self.assertEqual(len(interface), 3)
        # Check that indices were updated
        self.assertEqual(interface[1].idx, 1)
        self.assertEqual(interface[2].idx, 2)

    def test_add_operator_basic(self) -> None:
        """Test basic addition of two interfaces."""
        interface1 = Interface([self.ep1, self.ep2])
        interface2 = Interface([self.ep3])

        result = interface1 + interface2

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)
        self.assertEqual(result[2].typ.uid, self.ep3.typ.uid)

        # Check indices are correct
        self.assertEqual(result[0].idx, 0)
        self.assertEqual(result[1].idx, 1)
        self.assertEqual(result[2].idx, 2)

    def test_add_operator_empty_left(self) -> None:
        """Test adding empty interface on the left."""
        empty = Interface([])
        result = empty + self.interface1

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)

    def test_add_operator_empty_right(self) -> None:
        """Test adding empty interface on the right."""
        empty = Interface([])
        result = self.interface1 + empty

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, self.ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, self.ep2.typ.uid)

    def test_add_operator_both_empty(self) -> None:
        """Test adding two empty interfaces."""
        empty1 = Interface([])
        empty2 = Interface([])
        result = empty1 + empty2

        self.assertEqual(len(result), 0)

    def test_add_operator_wrong_type(self) -> None:
        """Test that adding non-Interface raises TypeError."""
        with self.assertRaises(TypeError) as context:
            _ = self.interface1 + "not an interface"  # type: ignore
        self.assertIn("Interface", str(context.exception))

    def test_add_operator_original_unchanged(self) -> None:
        """Test that addition doesn't modify original interfaces."""
        interface1 = Interface([self.ep1, self.ep2])
        interface2 = Interface([self.ep3])

        original_len1 = len(interface1)
        original_len2 = len(interface2)

        _ = interface1 + interface2

        self.assertEqual(len(interface1), original_len1)
        self.assertEqual(len(interface2), original_len2)

    def test_add_operator_chaining(self) -> None:
        """Test chaining multiple additions."""
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
        ep2 = EndPoint(DstRow.A, 0, EndPointClass.DST, "float")
        ep3 = EndPoint(DstRow.A, 0, EndPointClass.DST, "bool")

        interface1 = Interface([ep1])
        interface2 = Interface([ep2])
        interface3 = Interface([ep3])

        result = interface1 + interface2 + interface3

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)
        self.assertEqual(result[2].typ.uid, ep3.typ.uid)


class TestSrcInterface(unittest.TestCase):
    """Unit tests for the SrcInterface class."""

    def test_init(self) -> None:
        """Test SrcInterface initialization."""
        ep1 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 1, EndPointClass.SRC, "float")
        interface = SrcInterface([ep1, ep2])

        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], ep1)
        self.assertEqual(interface[1], ep2)

    def test_add_src_interfaces(self) -> None:
        """Test adding two SrcInterface instances."""
        ep1 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "int")
        ep2 = EndPoint(SrcRow.I, 0, EndPointClass.SRC, "float")

        interface1 = SrcInterface([ep1])
        interface2 = SrcInterface([ep2])

        result = interface1 + interface2

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)


class TestDstInterface(unittest.TestCase):
    """Unit tests for the DstInterface class."""

    def test_init(self) -> None:
        """Test DstInterface initialization."""
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
        ep2 = EndPoint(DstRow.A, 1, EndPointClass.DST, "float")
        interface = DstInterface([ep1, ep2])

        self.assertEqual(len(interface), 2)
        self.assertEqual(interface[0], ep1)
        self.assertEqual(interface[1], ep2)

    def test_add_dst_interfaces(self) -> None:
        """Test adding two DstInterface instances."""
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int")
        ep2 = EndPoint(DstRow.A, 0, EndPointClass.DST, "float")

        interface1 = DstInterface([ep1])
        interface2 = DstInterface([ep2])

        result = interface1 + interface2

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].typ.uid, ep1.typ.uid)
        self.assertEqual(result[1].typ.uid, ep2.typ.uid)


if __name__ == "__main__":
    unittest.main()
