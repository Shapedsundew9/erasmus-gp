"""Test case for JSONFileStore class."""
import unittest
from egppy.storage.store.json_file_store import JSONFileStore
from tests.test_storage.store_test_base import StoreTestBase


class TestJSONFileStore(StoreTestBase):
    """Test cases for JSONFileStore class.
    Test cases are inherited from StoreTestBase.
    """
    store_type = JSONFileStore


if __name__ == '__main__':
    unittest.main()
