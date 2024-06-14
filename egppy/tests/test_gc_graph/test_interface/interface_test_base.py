"""Base class of interface tests."""
import unittest
from egppy.gc_graph.interface.interface_class_factory import ListInterface
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.ep_type import ep_type_lookup


class InterfaceTestBase(unittest.TestCase):
    """Base class for interface tests.
    FIXME: Not done yet
    """

    # The interface type to test. Define in subclass.
    interface_type: type[InterfaceABC] = ListInterface

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
    def get_interface_cls(cls) -> type[InterfaceABC]:
        """Get the Interface class."""
        return cls.interface_type

    def setUp(self) -> None:
        self.interface_type: type[InterfaceABC] = self.get_interface_cls()
        self.interface = self.interface_type()

    def test_append(self) -> None:
        """Test the append method."""
        self.interface.append(ep_type_lookup['n2v']['int'])
        self.assertEqual(self.interface[-1], ep_type_lookup['n2v']['int'])

    def test_extend(self) -> None:
        """Test the extend method."""
        l = [ep_type_lookup['n2v']['int'], ep_type_lookup['n2v']['str']]
        l.extend([ep_type_lookup['n2v']['float'], ep_type_lookup['n2v']['bool']])
        self.assertEqual(l, [1, 2, 3, 4])

    def test_insert(self) -> None:
        """Test the insert method."""
        l = [1, 2, 3]
        l.insert(1, ep_type_lookup['n2v']['int'])
        self.assertEqual(l, [1, 'a', 2, 3])

    def test_remove(self) -> None:
        """Test the remove method."""
        l = [1, 2, 3, 4]
        l.remove(3)
        self.assertEqual(l, [1, 2, 4])

    def test_index(self) -> None:
        """Test the index method."""
        l = [1, 2, 3]
        index = l.index(2)
        self.assertEqual(index, 1)

    def test_count(self) -> None:
        """Test the count method."""
        l = [1, 2, 2, 3]
        count = l.count(2)
        self.assertEqual(count, 2)

    def test_copy(self) -> None:
        """Test the copy method."""
        l = [1, 2, 3]
        l_copy = l.copy()
        self.assertEqual(l, l_copy)
        self.assertIsNot(l, l_copy)

    def test_clear(self) -> None:
        """Test the clear method."""
        l = [1, 2, 3]
        l.clear()
        self.assertEqual(l, [])


if __name__ == '__main__':
    unittest.main()
