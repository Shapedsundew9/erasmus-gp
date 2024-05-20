"""Tests for the DirtyDictUGC class."""
import unittest
from egppy.gc_types.ugc_class_factory import DirtyDictUGC
from tests.test_storage.test_gc_types.ugc_test_base import UGCTestBase


class TestDirtyDictUGC(UGCTestBase):
    """
    Test case for DirtyDictUGC class.
    Test cases are inherited from UGCTestBase.
    """
    ugc_type = DirtyDictUGC

    def test_clean(self) -> None:
        """
        Test the clean method.
        """
        self.ugc['key'] = 'value'
        self.ugc.dirty()
        self.assertTrue(expr=self.ugc.is_dirty())
        self.ugc.clean()
        self.assertFalse(expr=self.ugc.is_dirty())

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        self.ugc['key'] = 'value'
        value = self.ugc.setdefault('key', 'default')
        self.assertEqual(first=value, second='value')
        value = self.ugc.setdefault('new_key', 'default')
        self.assertEqual(first=value, second='default')

    def test_update(self) -> None:
        """
        Test the update method.
        """
        self.ugc['key1'] = 'value1'
        self.ugc.update({'key2': 'value2', 'key3': 'value3'})
        self.assertEqual(first=self.ugc['key2'], second='value2')
        self.assertEqual(first=self.ugc['key3'], second='value3')


if __name__ == '__main__':
    unittest.main()
