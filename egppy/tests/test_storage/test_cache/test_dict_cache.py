"""Test the UserDictCache class."""

from egppy.common.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egppy.storage.cache.cache import DictCache
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.storage.store.storable_obj_abc import StorableObjABC
from tests.test_storage.store_test_base import DEFAULT_VALUES
from tests.test_storage.test_cache.cache_test_base import CacheTestBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestDictCacheCacheableDict(CacheTestBase):
    """Test case for UserDictCache class using CacheableDict."""

    store_type = DictCache
    value_type = CacheableDict
    value: StorableObjABC = CacheableDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDict(DEFAULT_VALUES[2])


class TestDictCacheCacheableDirtyDict(CacheTestBase):
    """Test case for UserDictCache class using CacheableDict."""

    store_type = DictCache
    value_type = CacheableDirtyDict
    value: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[2])
