"""Genetic Code store for the worker object."""
from json import load
from os.path import join, dirname
from egppy.gc_types.ggc_class_factory import GGCDirtyDict, GGCDict
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.in_memory_store import InMemoryStore
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Temporary store for testing
remote_store = InMemoryStore(GGCDirtyDict)
codon_file = join(dirname(__file__), '..', '..', 'egpseed', 'data', 'codons.json')
with open(codon_file, 'r', encoding='ascii') as f:
    for gc in load(f):
        ggc = GGCDirtyDict(gc)
        remote_store[ggc.signature()] = ggc


ggc_cache = DictCache({
    'max_items': 2**20,
    'purge_count': 2**18,
    'flavor': GGCDict,
    'next_level': remote_store
})
