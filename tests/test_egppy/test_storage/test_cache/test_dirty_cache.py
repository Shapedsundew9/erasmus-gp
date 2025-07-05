"""Test the DirtyDictCache class."""

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.storage.cache.dirty_cache import DirtyDictCache
from egppy.storage.store.storable_obj_abc import StorableObjABC
from test_egppy.test_storage.store_test_base import DEFAULT_VALUES
from test_egppy.test_storage.test_cache.dirty_cache_test_base import DirtyCacheTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestDirtyDictCacheCacheableDict(DirtyCacheTestBase):
    """Test case for DirtyDictCache class using CacheableDict."""

    store_type = DirtyDictCache
    value_type = CacheableDict
    value: StorableObjABC = CacheableDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDict(DEFAULT_VALUES[2])


class TestDirtyDictCacheCacheableDirtyDict(DirtyCacheTestBase):
    """Test case for DirtyDictCache class using CacheableDirtyDict."""

    store_type = DirtyDictCache
    value_type = CacheableDirtyDict
    value: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[0])
    value1: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[1])
    value2: StorableObjABC = CacheableDirtyDict(DEFAULT_VALUES[2])
