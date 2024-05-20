"""Test JSONFileStore class."""
import unittest
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.gc_types.ugc_class_factory import DictUGC


class JSONFileStoreTestCase(unittest.TestCase):
    """Test case for JSONFileStore class."""

    def setUp(self) -> None:
        self.file_path = "test_data.json"
        self.store = JSONFileStore(file_path=self.file_path)

    def test_get_nonexistent_key(self):
        key = "nonexistent_key"
        result = self.store.get(key)
        self.assertIsNone(result)

    def test_set_and_get_key(self):
        key = "test_key"
        value = {"name": "John", "age": 30}
        self.store.set(key, value)
        result = self.store.get(key)
        self.assertEqual(result, value)

    def test_set_and_get_multiple_keys(self):
        key1 = "key1"
        value1 = {"name": "Alice", "age": 25}
        key2 = "key2"
        value2 = {"name": "Bob", "age": 35}
        self.store.set(key1, value1)
        self.store.set(key2, value2)
        result1 = self.store.get(key1)
        result2 = self.store.get(key2)
        self.assertEqual(result1, value1)
        self.assertEqual(result2, value2)

    def test_update_existing_key(self):
        key = "test_key"
        initial_value = {"name": "John", "age": 30}
        updated_value = {"name": "John Doe", "age": 35}
        self.store.set(key, initial_value)
        self.store.set(key, updated_value)
        result = self.store.get(key)
        self.assertEqual(result, updated_value)

    def test_delete_key(self):
        key = "test_key"
        value = {"name": "John", "age": 30}
        self.store.set(key, value)
        self.store.delete(key)
        result = self.store.get(key)
        self.assertIsNone(result)

    def test_clear_store(self):
        key = "test_key"
        value = {"name": "John", "age": 30}
        self.store.set(key, value)
        self.store.clear()
        result = self.store.get(key)
        self.assertIsNone(result)

    def test_serialize_deserialize(self):
        key = "test_key"
        value = {"name": "John", "age": 30}
        self.store.set(key, value)
        self.store.serialize()
        self.store.clear()
        self.store.deserialize()
        result = self.store.get(key)
        self.assertEqual(result, value)

if __name__ == '__main__':
    unittest.main()