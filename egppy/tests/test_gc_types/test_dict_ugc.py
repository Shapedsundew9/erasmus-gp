"""Test case for UGCDict class."""
import unittest
from egppy.gc_types.ugc_class_factory import UGCDict
from tests.test_gc_types.ugc_test_base import UGCTestBase


class TestUGCDict(UGCTestBase):
    """
    Test case for UGCDict class.
    Test cases are inherited from UGCTestBase.
    """
    ugc_type = UGCDict


if __name__ == '__main__':
    unittest.main()
