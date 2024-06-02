"""Test cases for JSONFileStore class."""
from tests.test_storage.store_test_base import StoreTestBase


class JSONFileStoreTestBase(StoreTestBase):
    """Test cases for JSONFileStore Base class.
    Test cases are inherited from StoreTestBase over writing tests that
    return keys to compare them with str(key) as JSON file store keys have
    to be stored as strings and there is no way to convert them back to
    the original key type.
    """

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        keys = set(self.store.keys())
        self.assertEqual(first=keys, second={str(self.key1), str(self.key2)})

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        keys = self.store.keys()
        self.assertEqual(first=list(keys), second=[str(self.key1), str(self.key2)])

    def test_items(self) -> None:
        """
        Test the items method.
        """
        if self.running_in_test_base_class():
            return
        self.store[self.key1] = self.value1
        self.store[self.key2] = self.value2
        items = self.store.items()
        second = [(str(self.key1), self.value1), (str(self.key2), self.value2)]
        self.assertEqual(first=list(items), second=second)
