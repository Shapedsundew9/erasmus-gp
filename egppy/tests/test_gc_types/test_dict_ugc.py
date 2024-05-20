"""Test case for DictUGC class."""
import unittest
from egppy.gc_types.ugc_class_factory import DictUGC
from tests.test_gc_types.ugc_test_base import UGCTestBase


class TestDictUGC(UGCTestBase):
    """
    Test case for DictUGC class.
    Test cases are inherited from UGCTestBase.
    """
    ugc_type = DictUGC


if __name__ == '__main__':
    unittest.main()
