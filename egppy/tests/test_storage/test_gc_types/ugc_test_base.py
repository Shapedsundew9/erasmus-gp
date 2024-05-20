"""Tests for the DirtyDictUGC class."""
import unittest
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.ugc_class_factory import DirtyDictUGC


class UGCTestBase(unittest.TestCase):
    """
    Test base class for UGC classes.

    """
    # The UGC class to test. Override this in subclasses.
    ugc_type = DirtyDictUGC

    @classmethod
    def get_cls(cls) -> type[GCABC]:
        """Get the UGC class."""
        return cls.ugc_type

    def setUp(self) -> None:
        self.type: type[GCABC] = self.get_cls()
        self.ugc = self.type()
        self.ugc1 = self.type()
        self.ugc2 = self.type()

    def test_set_item(self) -> None:
        """
        Test the set_item method.
        """
        self.ugc['key'] = 'value'
        self.assertEqual(first=self.ugc['key'], second='value')

    def test_get_item(self) -> None:
        """
        Test the get_item method.
        """
        self.ugc['key'] = 'value'
        self.assertEqual(first=self.ugc['key'], second='value')

    def test_del_item(self) -> None:
        """
        Test the del_item method.
        """
        self.ugc['key'] = 'value'
        del self.ugc['key']
        self.assertNotIn(member='key', container=self.ugc)

    def test_contains(self) -> None:
        """
        Test the contains method.
        """
        self.ugc['key'] = 'value'
        self.assertIn(member='key', container=self.ugc)

    def test_len(self) -> None:
        """
        Test the len method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        self.assertEqual(first=len(self.ugc), second=2)

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        keys = list(self.ugc)
        self.assertEqual(first=keys, second=['key1', 'key2'])

    def test_clear(self) -> None:
        """
        Test the clear method.
        """
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.clear()

    def test_dirty(self) -> None:
        """
        Test the dirty method.
        """
        self.ugc.clean()
        self.ugc.dirty()
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_is_dirty(self) -> None:
        """
        Test the is_dirty method.
        For a DirtyDict*GC object, is_dirty() should return True until clean() is called
        and updating the object *may* not update the dirty flag.
        """
        self.ugc['key1'] = 'value1'
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_clean(self) -> None:
        """
        Test the clean method.
        """
        self.ugc['key'] = 'value'
        self.assertTrue(expr=self.ugc.is_dirty())
        self.ugc.clean()
        self.assertFalse(expr=self.ugc.is_dirty())

    def test_pop(self) -> None:
        """
        Test the pop method.
        """
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.pop(key='key')

    def test_popitem(self) -> None:
        """
        Test the popitem method.
        """
        self.ugc['key'] = 'value'
        with self.assertRaises(expected_exception=AssertionError):
            self.ugc.popitem()

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        keys = self.ugc.keys()
        self.assertEqual(first=list(keys), second=['key1', 'key2'])

    def test_items(self) -> None:
        """
        Test the items method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        items = self.ugc.items()
        self.assertEqual(first=list(items), second=[('key1', 'value1'), ('key2', 'value2')])

    def test_values(self) -> None:
        """
        Test the values method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        values = self.ugc.values()
        self.assertEqual(first=list(values), second=['value1', 'value2'])

    def test_eq(self) -> None:
        """
        Test the __eq__ method.
        """
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
        self.ugc['key'] = 'value'
        value = self.ugc.get('key')
        self.assertEqual(first=value, second='value')

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
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
        self.ugc['key1'] = 'value1'
        self.ugc.update({'key2': 'value2', 'key3': 'value3'})
        self.assertEqual(first=self.ugc['key2'], second='value2')
        self.assertEqual(first=self.ugc['key3'], second='value3')
        self.assertTrue(expr=self.ugc.is_dirty())

    def test_copyback(self) -> None:
        """
        Test the copyback method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc['key2'] = 'value2'
        self.ugc['key3'] = 'value3'

        copy: GCABC = self.ugc.copyback()
        self.assertEqual(first=copy['key1'], second='value1')
        self.assertEqual(first=copy['key2'], second='value2')
        self.assertEqual(first=copy['key3'], second='value3')
