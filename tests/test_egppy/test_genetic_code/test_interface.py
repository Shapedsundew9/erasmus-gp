"""Unit tests for the Interface, SrcInterface, and DstInterface classes."""

import unittest

from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.end_point import EndPoint
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

    def test_append_incompatible_row(self) -> None:
        """Test that appending an endpoint with different row raises ValueError."""
        interface = Interface([self.ep1])
        ep_wrong_row = EndPoint(DstRow.F, 1, EndPointClass.DST, "str")
        with self.assertRaises(ValueError) as context:
            interface.append(ep_wrong_row)
        self.assertIn("row", str(context.exception).lower())

    def test_extend(self) -> None:
        """Test extending interface with multiple endpoints."""
        interface = Interface([self.ep1])
        new_eps = [
            EndPoint(DstRow.A, 1, EndPointClass.DST, "str"),
            EndPoint(DstRow.A, 2, EndPointClass.DST, "bool"),
        ]
        interface.extend(new_eps)
        self.assertEqual(len(interface), 3)
        # Check that indices were updated
        self.assertEqual(interface[1].idx, 1)
        self.assertEqual(interface[2].idx, 2)

    def test_copy(self) -> None:
        """Test copying an interface."""
        interface_copy = self.interface1.copy()
        self.assertEqual(interface_copy, self.interface1)
        self.assertIsNot(interface_copy, self.interface1)
        self.assertFalse(interface_copy.is_frozen())

    def test_freeze(self) -> None:
        """Test freezing an interface."""
        # Create endpoints with references for freezing
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]])
        ep2 = EndPoint(DstRow.A, 1, EndPointClass.DST, "float", refs=[["I", 1]])
        interface = Interface([ep1, ep2])
        frozen = interface.freeze()
        self.assertTrue(frozen.is_frozen())

        # Test that we cannot modify frozen interface
        ep3 = EndPoint(DstRow.A, 2, EndPointClass.DST, "bool")
        with self.assertRaises(RuntimeError):
            frozen.append(ep3)

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

    def test_add_operator_refs_empty(self) -> None:
        """Test that all endpoint references are empty lists in the new interface."""
        # Create endpoints with some references
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]])
        ep2 = EndPoint(DstRow.A, 1, EndPointClass.DST, "float", refs=[["I", 1]])
        ep3 = EndPoint(DstRow.A, 0, EndPointClass.DST, "bool", refs=[["I", 2]])

        interface1 = Interface([ep1, ep2])
        interface2 = Interface([ep3])

        # Verify source endpoints have references
        self.assertEqual(len(ep1.refs), 1)
        self.assertEqual(len(ep2.refs), 1)
        self.assertEqual(len(ep3.refs), 1)

        # Add the interfaces
        result = interface1 + interface2

        # Verify all endpoints in result have empty references
        for ep in result:
            self.assertEqual(
                ep.refs, [], f"Endpoint {ep.idx} should have empty refs, got {ep.refs}"
            )

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

    def test_add_operator_incompatible_row(self) -> None:
        """Test that adding interfaces with different rows raises ValueError."""
        interface1 = Interface([EndPoint(DstRow.A, 0, EndPointClass.DST, "int")])
        interface2 = Interface([EndPoint(DstRow.F, 0, EndPointClass.DST, "int")])

        with self.assertRaises(ValueError) as context:
            _ = interface1 + interface2
        self.assertIn("row", str(context.exception).lower())

    def test_add_operator_incompatible_class(self) -> None:
        """Test that adding interfaces with different classes raises ValueError."""
        interface1 = Interface([EndPoint(DstRow.A, 0, EndPointClass.DST, "int")])
        interface2 = Interface([EndPoint(DstRow.A, 0, EndPointClass.SRC, "int")])

        with self.assertRaises(ValueError) as context:
            _ = interface1 + interface2
        self.assertIn("class", str(context.exception).lower())

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

    def test_add_operator_with_frozen(self) -> None:
        """Test adding frozen interfaces."""
        # Create endpoints with references for freezing
        ep1 = EndPoint(DstRow.A, 0, EndPointClass.DST, "int", refs=[["I", 0]])
        ep2 = EndPoint(DstRow.A, 0, EndPointClass.DST, "float", refs=[["I", 1]])
        interface1 = Interface([ep1]).freeze()
        interface2 = Interface([ep2]).freeze()

        result = interface1 + interface2

        self.assertEqual(len(result), 2)
        self.assertFalse(result.is_frozen())  # Result should not be frozen

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
