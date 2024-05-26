"""Test the FastCache class."""
from egppy.storage.cache.cache_class_factory import FastCache
from tests.test_storage.test_cache.cache_test_base import CacheTestBase


class TestFastCache(CacheTestBase):
    """
    Test case for FastCache class.
    Test cases are inherited from CacheTestBase.
    """
    store_type = FastCache
