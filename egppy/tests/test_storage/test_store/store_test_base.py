"""Test JSONFileStore class."""
from __future__ import annotations
import unittest
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.null_store import NullStore
from egppy.gc_types.ugc_class_factory import DictUGC


class StoreTestBase(unittest.TestCase):
    """Test case for Store classes."""
    # The Store class to test. Override this in subclasses.
    store_type = NullStore

    @classmethod
    def get_test_cls(cls) -> type[unittest.TestCase]:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls() == StoreTestBase

    @classmethod
    def get_store_cls(cls) -> type[StoreABC]:
        """Get the Store class."""
        return cls.store_type

    def setUp(self) -> None:
        self.type: type[StoreABC] = self.get_store_cls()
        self.store = self.type()
        self.store1 = self.type()
        self.store2 = self.type()

    def test_set_item(self) -> None:
        """
        Test the set_item method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        self.assertEqual(first=self.store['key'], second=value)

    def test_get_item(self) -> None:
        """
        Test the get_item method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        self.assertEqual(first=self.store['key'], second=value)

    def test_del_item(self) -> None:
        """
        Test the del_item method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        del self.store['key']
        self.assertNotIn(member='key', container=self.store)

    def test_contains(self) -> None:
        """
        Test the contains method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        self.assertIn(member='key', container=self.store)

    def test_len(self) -> None:
        """
        Test the len method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value1')
        self.store['key1'] = value
        value = DictUGC(value='value2')
        self.store['key2'] = value
        self.assertEqual(first=len(self.store), second=2)

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value1')
        self.store['key1'] = value
        value = DictUGC(value='value2')
        self.store['key2'] = value
        keys = set(self.store.keys())
        self.assertEqual(first=keys, second={'key1', 'key2'})

    def test_clear(self) -> None:
        """
        Test the clear method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        self.store.clear()
        self.assertEqual(first=len(self.store), second=0)

    def test_pop(self) -> None:
        """
        Test the pop method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        with self.assertRaises(expected_exception=AssertionError):
            self.store.pop(key='key')

    def test_popitem(self) -> None:
        """
        Test the popitem method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        with self.assertRaises(expected_exception=AssertionError):
            self.store.popitem()

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value1')
        self.store['key1'] = value
        value = DictUGC(value='value2')
        self.store['key2'] = value
        keys = self.store.keys()
        self.assertEqual(first=list(keys), second=['key1', 'key2'])

    def test_items(self) -> None:
        """
        Test the items method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value1')
        self.store['key1'] = value
        value = DictUGC(value='value2')
        self.store['key2'] = value
        items = self.store.items()
        second = [('key1', {'value': 'value1'}), ('key2', {'value': 'value2'})]
        self.assertEqual(first=list(items), second=second)

    def test_values(self) -> None:
        """
        Test the values method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value1')
        self.store['key1'] = value
        value = DictUGC(value='value2')
        self.store['key2'] = value
        values = self.store.values()
        self.assertEqual(first=list(values), second=[{'value': 'value1'}, {'value': 'value2'}])

    def test_eq(self) -> None:
        """
        Test the __eq__ method.
        """
        if self.running_in_test_base_class():
            return
        self.store1 = self.type()
        value = DictUGC(value='value1')
        self.store1['key1'] = value
        value = DictUGC(value='value2')
        self.store1['key2'] = value

        self.store2 = self.type()
        value = DictUGC(value='value1')
        self.store2['key1'] = value
        value = DictUGC(value='value2')
        self.store2['key2'] = value

        self.assertEqual(first=self.store1, second=self.store2)

    def test_ne(self) -> None:
        """
        Test the __ne__ method.
        """
        if self.running_in_test_base_class():
            return
        self.store1 = self.type()
        value = DictUGC(value='value1')
        self.store1['key1'] = value
        value = DictUGC(value='value2')
        self.store1['key2'] = value

        self.store2 = self.type()
        value = DictUGC(value='value1')
        self.store2['key1'] = value
        value = DictUGC(value='value2')
        self.store2['key3'] = value

        self.assertNotEqual(first=self.store1, second=self.store2)

    def test_get(self) -> None:
        """
        Test the get method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        self.store['key'] = value
        value = self.store.get('key')
        self.assertEqual(first=value, second=value)

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        if self.running_in_test_base_class():
            return
        value = DictUGC(value='value')
        default = DictUGC(value='default')
        self.store['key'] = value
        value = self.store.setdefault(key='key', default=default)
        self.assertEqual(first=value, second=value)

        value = self.store.setdefault(key='new_key', default=default)
        self.assertEqual(first=value, second=default)

    def test_update(self) -> None:
        """
        Test the update method.
        """
        if self.running_in_test_base_class():
            return
        value1 = DictUGC(value='value1')
        value2 = DictUGC(value='value2')
        value3 = DictUGC(value='value3')
        self.store1['key1'] = value1
        self.store.update({'key2': value2, 'key3': value3})
        self.assertEqual(first=self.store['key2'], second=value2)
        self.assertEqual(first=self.store['key3'], second=value3)
