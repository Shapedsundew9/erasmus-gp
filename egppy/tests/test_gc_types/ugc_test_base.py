"""Tests for the DirtyDictUGC class."""
from __future__ import annotations
import unittest
from egppy.storage.cache.cacheable_dirty_dict import CacheableDirtyDict
from egppy.gc_types.ugc_class_factory import UGCType, DictUGC


class UGCTestBase(unittest.TestCase):
    """
    Test base class for UGC classes.

    """
    # The UGC class to test. Override this in subclasses.
    ugc_type: type[UGCType] = DictUGC

    @classmethod
    def get_test_cls(cls) -> type[unittest.TestCase]:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_cls(cls) -> type[UGCType]:
        """Get the UGC class."""
        return cls.ugc_type

    def setUp(self) -> None:
        self.type: type[UGCType] = self.get_cls()
        self.ugc: UGCType = self.type()
        self.ugc1: UGCType = self.type()
        self.ugc2: UGCType = self.type()

    def test_set_item(self) -> None:
        """
        Test the set_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        self.assertEqual(first=self.ugc['key'], second='value')

    def test_get_item(self) -> None:
        """
        Test the get_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        self.assertEqual(first=self.ugc['key'], second='value')

    def test_del_item(self) -> None:
        """
        Test the del_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        del self.ugc['key']
        self.assertNotIn(member='key', container=self.ugc)

    def test_contains(self) -> None:
        """
        Test the contains method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        self.assertIn(member='key', container=self.ugc)

    def test_len(self) -> None:
        """
        Test the len method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        self.assertEqual(first=len(self.ugc), second=2)

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        keys = list(self.ugc)
        self.assertEqual(first=keys, second=['key1', 'key2'])

    def test_clear(self) -> None:
        """
        Test the clear method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.clear()

    def test_dirty(self) -> None:
        """
        Test the dirty method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc.clean()
        self.ugc.dirty()
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_is_dirty(self) -> None:
        """
        Test the is_dirty method.
        For a DirtyDict*GC object, is_dirty() should return True until clean() is called
        and updating the object *may* not update the dirty flag.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_clean(self) -> None:
        """
        Test the clean method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        self.assertTrue(expr=self.ugc.is_dirty())
        self.ugc.clean()
        self.assertFalse(expr=self.ugc.is_dirty())

    def test_pop(self) -> None:
        """
        Test the pop method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.pop(key='key')

    def test_popitem(self) -> None:
        """
        Test the popitem method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.popitem()

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        keys = self.ugc.keys()
        self.assertEqual(first=list(keys), second=['key1', 'key2'])

    def test_items(self) -> None:
        """
        Test the items method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        items = self.ugc.items()
        self.assertEqual(first=list(items), second=[('key1', 'value1'), ('key2', 'value2')])

    def test_values(self) -> None:
        """
        Test the values method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        values = self.ugc.values()
        self.assertEqual(first=list(values), second=['value1', 'value2'])

    def test_eq(self) -> None:
        """
        Test the __eq__ method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc1 = self.type()
        self.ugc1['key1'] = 'value1'
        self.ugc1['key2'] = 'value2'

        self.ugc2 = self.type()
        self.ugc2['key1'] = 'value1'
        self.ugc2['key2'] = 'value2'

        self.assertEqual(first=self.ugc1, second=self.ugc2)

    def test_ne(self) -> None:
        """
        Test the __ne__ method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc1 = self.type()
        self.ugc1['key1'] = 'value1'
        self.ugc1['key2'] = 'value2'

        self.ugc2 = self.type()
        self.ugc2['key1'] = 'value1'
        self.ugc2['key3'] = 'value3'

        self.assertNotEqual(first=self.ugc1, second=self.ugc2)

    def test_get(self) -> None:
        """
        Test the get method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        value = self.ugc.get('key')
        self.assertEqual(first=value, second='value')

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key'] = 'value'
        self.ugc.clean()
        value = self.ugc.setdefault('key', 'default')
        self.assertEqual(first=value, second='value')
        self.assertFalse(expr=self.ugc.is_dirty())

        value = self.ugc.setdefault('new_key', 'default')
        self.assertEqual(first=value, second='default')
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_update(self) -> None:
        """
        Test the update method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc.update({'key2': 'value2', 'key3': 'value3'})
        self.assertEqual(first=self.ugc['key2'], second='value2')
        self.assertEqual(first=self.ugc['key3'], second='value3')
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_copyback(self) -> None:
        """
        Test the copyback method.
        """
        if self.running_in_test_base_class():
            return
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        self.ugc['key3'] = 'value3'

        copy: CacheableDirtyDict = self.ugc.copyback()
        self.assertEqual(first=copy['key1'], second='value1')
        self.assertEqual(first=copy['key2'], second='value2')
        self.assertEqual(first=copy['key3'], second='value3')
