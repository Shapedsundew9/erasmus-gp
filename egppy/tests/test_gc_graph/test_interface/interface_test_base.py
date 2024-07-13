"""Base class of interface tests."""
import unittest
from egppy.gc_graph.interface.interface_class_factory import TupleInterface
from egppy.gc_graph.ep_type import ep_type_lookup, INVALID_EP_TYPE_VALUE


class InterfaceTestBase(unittest.TestCase):
    """Base class for interface tests.
    FIXME: Not done yet
    """

    # The interface type to test. Define in subclass.
    itype: type[TupleInterface] = TupleInterface

    @classmethod
    def get_test_cls(cls) -> type:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_interface_cls(cls) -> type:
        """Get the Interface class."""
        return cls.itype

    def setUp(self) -> None:
        self.interface_type = self.get_interface_cls()
        self.interface = self.interface_type([ep_type_lookup['n2v']['bool']] * 4)

    def test_len(self) -> None:
        """Test the length of the interface."""
        if self.running_in_test_base_class():
            return
        self.assertEqual(len(self.interface), 4)

    def test_iter(self) -> None:
        """Test the iteration of the interface."""
        if self.running_in_test_base_class():
            return
        for idx, ept in enumerate(self.interface):
            self.assertEqual(ept, ep_type_lookup['n2v']['bool'])
            self.assertEqual(self.interface[idx], ep_type_lookup['n2v']['bool'])

    def test_consistency(self) -> None:
        """Test the consistency of the interface."""
        if self.running_in_test_base_class():
            return
        self.interface.consistency()

    def test_verify(self) -> None:
        """Test the verification of the interface."""
        if self.running_in_test_base_class():
            return
        self.interface.verify()

    def test_verify_assert1(self) -> None:
        """Test when the interface to too long."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            iface = self.interface_type([ep_type_lookup['n2v']['bool']] * 257)
            iface.verify()

    def test_verify_assert2(self) -> None:
        """Test when the interface has an invalid type."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            iface = self.interface_type([INVALID_EP_TYPE_VALUE] * 4)
            iface.verify()


if __name__ == '__main__':
    unittest.main()
