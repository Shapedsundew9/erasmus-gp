"""Tests for InterfaceABC."""

from unittest import TestCase

from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.interface import DstInterface, Interface, SrcInterface
from egppy.genetic_code.interface_abc import InterfaceABC


class TestInterfaceABC(TestCase):
    """Test cases for InterfaceABC."""

    def test_abc_defines_required_methods(self) -> None:
        """Test that all required abstract methods are defined in the ABC."""
        abstract_methods = InterfaceABC.__abstractmethods__

        # Check that the expected abstract methods are defined
        expected_methods = frozenset(
            {
                "__getitem__",
                "__iter__",
                "__len__",
                "__setitem__",
                "__delitem__",
                "insert",
                "__eq__",
                "__hash__",
                "__str__",
                "__add__",
                "append",
                "extend",
                "to_json",
                "to_td_uids",
                "to_td",
                "types_and_indices",
                "sorted_unique_td_uids",
                "unconnected_eps",
                "verify",
                "consistency",
                "set_row",
                "set_cls",
                "clr_refs",
                "ref_shift",
                "set_refs",
            }
        )

        # Verify that all expected methods are abstract
        self.assertEqual(abstract_methods, expected_methods)

    def test_dst_interface_inherits_from_abc(self) -> None:
        """Test that DstInterface properly inherits from InterfaceABC."""
        self.assertTrue(issubclass(DstInterface, InterfaceABC))

    def test_interface_abc_is_abstract(self) -> None:
        """Test that InterfaceABC cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            # pylint: disable=abstract-class-instantiated
            InterfaceABC()  # type: ignore[abstract]

    def test_interface_abc_polymorphism(self) -> None:
        """Test that InterfaceABC enables polymorphism."""

        def process_interface(iface: InterfaceABC) -> int:
            """Process any interface and return its length."""
            return len(iface)

        interface = Interface(endpoints=["int", "str"], row=DstRow.A)
        dst_interface = DstInterface(endpoints=["float"], row=DstRow.O)

        # Both should work with the function
        self.assertEqual(process_interface(interface), 2)
        self.assertEqual(process_interface(dst_interface), 1)

    def test_interface_abc_return_types(self) -> None:
        """Test that methods return InterfaceABC types where appropriate."""
        interface = Interface(endpoints=["int"], row=DstRow.A)
        other = Interface(endpoints=["str"], row=DstRow.A)

        # Test __add__ returns InterfaceABC
        result = interface + other
        self.assertIsInstance(result, InterfaceABC)

    def test_interface_abc_type_checking(self) -> None:
        """Test that InterfaceABC works for type checking."""
        interface = Interface(endpoints=["int"], row=DstRow.A)
        dst_interface = DstInterface(endpoints=["str"], row=DstRow.O)
        src_interface = SrcInterface(endpoints=["float"], row=SrcRow.I)

        # All should be instances of InterfaceABC
        self.assertIsInstance(interface, InterfaceABC)
        self.assertIsInstance(dst_interface, InterfaceABC)
        self.assertIsInstance(src_interface, InterfaceABC)

    def test_interface_implements_abstract_methods(self) -> None:
        """Test that Interface implements all required abstract methods."""
        # Create an instance to verify it's a concrete implementation
        interface = Interface(endpoints=["int"], row=DstRow.A)

        # Verify it has all the abstract methods implemented
        self.assertTrue(hasattr(interface, "__getitem__"))
        self.assertTrue(hasattr(interface, "__iter__"))
        self.assertTrue(hasattr(interface, "__len__"))
        self.assertTrue(hasattr(interface, "__setitem__"))
        self.assertTrue(hasattr(interface, "__eq__"))
        self.assertTrue(hasattr(interface, "__hash__"))
        self.assertTrue(hasattr(interface, "__str__"))
        self.assertTrue(hasattr(interface, "__add__"))
        self.assertTrue(hasattr(interface, "append"))
        self.assertTrue(hasattr(interface, "extend"))
        self.assertTrue(hasattr(interface, "cls"))
        self.assertTrue(hasattr(interface, "to_json"))
        self.assertTrue(hasattr(interface, "to_td_uids"))
        self.assertTrue(hasattr(interface, "to_td"))
        self.assertTrue(hasattr(interface, "types_and_indices"))
        self.assertTrue(hasattr(interface, "sorted_unique_td_uids"))
        self.assertTrue(hasattr(interface, "unconnected_eps"))

    def test_interface_inherits_from_abc(self) -> None:
        """Test that Interface properly inherits from InterfaceABC."""
        self.assertTrue(issubclass(Interface, InterfaceABC))

    def test_src_interface_inherits_from_abc(self) -> None:
        """Test that SrcInterface properly inherits from InterfaceABC."""
        self.assertTrue(issubclass(SrcInterface, InterfaceABC))
