"""Test the UserDictCache class."""
from egppy.storage.cache.cache_class_factory import UserDictCache
from tests.test_storage.test_cache.cache_test_base import CacheTestBase


class TestUserDictCache(CacheTestBase):
    """
    Test case for UserDictCache class.
    Test cases are inherited from CacheTestBase.
    """
    store_type = UserDictCache
