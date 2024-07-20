"""Genetic Code Cache module."""
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.store.json_file_store import JSONFileStore
from egppy.storage.cache.cache_abc import CacheABC, CacheConfig
from egppy.storage.cache.cache import DictCache
from egppy.storage.cache.dirty_cache import DirtyDictCache
from egppy.gc_types.gc import GCABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# TODO: The Gene Pool is temporarily a JsonFileStore. This will be replaced with either a stub
# (as it will not be used locally) or an interface to a database server.
gene_pool = JSONFileStore(file_path="genetic_code_store.json")
remote_cache_client_config: CacheConfig = {
    "max_items": 0,
    "purge_count": 0,
    "next_level": gene_pool,
    "flavor": GCABC  # TODO: Needs correct type
}

# TODO: The remote class client will be a different sort of CacheABC that interfaces with a remote server.
# The current plan is a redis cache.
remote_cache_client: CacheABC = DictCache(config=remote_cache_client_config)
compact_cache_config: CacheConfig = {
    "max_items": 100000,
    "purge_count": 25000,
    "next_level": remote_cache_client,
    "flavor": GCABC  # TODO: Needs correct type
}

compact_cache = DictCache(config=compact_cache_config)
fast_cache_config: CacheConfig = {
    "max_items": 0,
    "purge_count": 0,
    "next_level": compact_cache,
    "flavor": GCABC  # TODO: Needs correct type
}

# Both the compact_cache and the fast_cache interfaces are exposed to the logic layer.
# The fast cache cannot pull data from the compact cache but it can push to it. The
# fast cache can be considered a "working area" for the logic layer.
fast_cache: CacheABC = DirtyDictCache(config=fast_cache_config)
genetic_code_cache: CacheABC = compact_cache
