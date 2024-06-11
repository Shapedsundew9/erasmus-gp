"""Test JSONFileStore class."""
from __future__ import annotations
from collections.abc import Hashable
import unittest
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.null_store import NullStore
from egppy.gc_types.null_gc import NULL_GC


# Default values for test cases
DEFAULT_VALUES: tuple[dict[str, str], dict[str, int], dict[str, float]] = (
    {'k': 'value'},
    {'k1': 1243},
    {'k2': 0.5678}
)


class StoreTestBase(unittest.TestCase):
    """Test case for Store classes."""

    # The Store class to test. Override this in subclasses.
    store_type = NullStore
    # The Value class to test. Override this in subclasses.
    value_type = StorableObjABC
    # Instances of the Value class. Define these in setUpClass.
    # No values should compare equal.
    value: StorableObjABC = NULL_GC
    value1: StorableObjABC = NULL_GC
    value2: StorableObjABC = NULL_GC
    # Key values for testing. Override these in subclasses to different types.
    key: Hashable = 'key'
    key1: Hashable = 'key1'
    key2: Hashable = 'key2'

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
    def get_store_cls(cls) -> type[StoreABC]:
        """Get the Store class."""
        return cls.store_type

    @classmethod
    def get_value_cls(cls) -> type[StorableObjABC]:
        """Get the Value class."""
        return cls.value_type

    def setUp(self) -> None:
        self.store_type: type[StoreABC] = self.get_store_cls()
        self.store = self.store_type(self.get_value_cls())
        self.store1 = self.store_type(self.get_value_cls())
        self.store2 = self.store_type(self.get_value_cls())
        self.test_type: type = self.get_test_cls()
        self.value: StorableObjABC = self.test_type.value
        self.value1: StorableObjABC = self.test_type.value1
        self.value2: StorableObjABC = self.test_type.value2
        self.key: Hashable = self.test_type.key
        self.key1: Hashable = self.test_type.key1
        self.key2: Hashable = self.test_type.key2

    def test_set_item(self) -> None:
        """
        Test the set_item method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.assertEqual(first=self.store[self.key], second=self.value)

    def test_get_item(self) -> None:
        """
        Test the get_item method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.assertEqual(first=self.store[self.key], second=self.value)

    def test_del_item(self) -> None:
        """
        Test the del_item method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        del self.store[self.key]
        self.assertNotIn(member=self.key, container=self.store)

    def test_contains(self) -> None:
        """
        Test the contains method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.assertIn(member=self.key, container=self.store)

    def test_len(self) -> None:
        """
        Test the len method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        self.assertEqual(first=len(self.store), second=2)

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        keys = set(self.store.keys())
        self.assertEqual(first=keys, second={self.key1, self.key2})

    def test_clear(self) -> None:
        """
        Test the clear method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.store.clear()
        self.assertEqual(first=len(self.store), second=0)

    def test_pop(self) -> None:
        """
        Test the pop method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.store.pop(self.key)
        self.assertNotIn(member=self.key, container=self.store)

    def test_popitem(self) -> None:
        """
        Test the popitem method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        self.store.popitem()
        self.assertNotIn(member=self.key, container=self.store)

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        keys = self.store.keys()
        self.assertEqual(first=list(keys), second=[self.key1, self.key2])

    def test_items(self) -> None:
        """
        Test the items method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        items = self.store.items()
        second = [(self.key1, self.value1), (self.key2, self.value2)]
        self.assertEqual(first=list(items), second=second)

    def test_values(self) -> None:
        """
        Test the values method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        values = self.store.values()
        self.assertEqual(first=list(values), second=[self.value1, self.value2])

    def test_eq(self) -> None:
        """
        Test the __eq__ method.
        """
        if self.running_in_test_base_class():
            return
        self.store1[self.key1] = self.value1
        self.store1[self.key2] = self.value2

        self.store2[self.key1] = self.value1
        self.store2[self.key2] = self.value2

        self.assertEqual(first=self.store1, second=self.store2)

    def test_ne(self) -> None:
        """
        Test the __ne__ method.
        """
        if self.running_in_test_base_class():
            return
        self.store1[self.key1] = self.value1
        self.store1[self.key2] = self.value2

        self.store2[self.key2] = self.value1
        self.store2[self.key1] = self.value2

        self.assertNotEqual(first=self.store1, second=self.store2)

    def test_get(self) -> None:
        """
        Test the get method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value
        value = self.store.get(self.key)
        self.assertEqual(first=self.value, second=value)

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key] = self.value1
        value = self.store.setdefault(self.key,self.value2)
        self.assertEqual(first=value, second=self.value1)

        value = self.store.setdefault('new_key', self.value2)
        self.assertEqual(first=value, second=self.value2)

    def test_update(self) -> None:
        """
        Test the update method.
        """
        if self.running_in_test_base_class():
            return
        self.store1[self.key] = self.value
        self.store.update({self.key1: self.value1, self.key2: self.value2})
        self.assertEqual(first=self.store[self.key1], second=self.value1)
        self.assertEqual(first=self.store[self.key2], second=self.value2)
