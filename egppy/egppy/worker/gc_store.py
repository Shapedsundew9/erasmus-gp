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
_REMOTE_STORE = InMemoryStore(GGCDirtyDict)
_CODON_FILE = join(dirname(__file__), '..', 'data', 'codons.json')
_CODON_SIGNATURE_LIST = []
with open(_CODON_FILE, 'r', encoding='ascii') as f:
    for gc in load(f):
        ggc = GGCDirtyDict(gc)
        _REMOTE_STORE[ggc.signature()] = ggc
        _CODON_SIGNATURE_LIST.append(ggc.signature())


CODON_SIGNATURES = tuple(_CODON_SIGNATURE_LIST)
del _CODON_SIGNATURE_LIST
GGC_CACHE = DictCache({
    'max_items': 2**20,
    'purge_count': 2**18,
    'flavor': GGCDict,
    'next_level': _REMOTE_STORE
})
