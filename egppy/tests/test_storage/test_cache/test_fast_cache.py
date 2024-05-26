"""Test the FastCache class."""
from egppy.storage.cache.cache_class_factory import FastCache
from tests.test_storage.test_cache.fast_cache_test_base import FastCacheTestBase


class TestFastCache(FastCacheTestBase):
    """
    Test case for FastCache class.
    Test cases are inherited from CacheTestBase.
    """
    store_type = FastCache
