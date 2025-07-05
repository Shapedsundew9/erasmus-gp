"""Genetic Code store for the worker object."""

from json import load
from os.path import dirname, join, exists

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.storage.cache.cache import DictCache
from egppy.storage.store.in_memory_store import InMemoryStore

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# FIXME: Temporary store for testing
_REMOTE_STORE = InMemoryStore(GGCDict)
_CODON_FILE = join(
    dirname(__file__), "..", "..", "egpdbmgr", "egpdbmgr", "data", "codons.json"
)
_CODON_SIGNATURE_LIST = []
if exists(_CODON_FILE):
    with open(_CODON_FILE, "r", encoding="ascii") as f:
        for gc in load(f):
            ggc = GGCDict(gc)
            _REMOTE_STORE[ggc["signature"]] = ggc
            _CODON_SIGNATURE_LIST.append(ggc["signature"])


CODON_SIGNATURES = tuple(_CODON_SIGNATURE_LIST)
del _CODON_SIGNATURE_LIST
GGC_CACHE = DictCache(
    {"max_items": 2**20, "purge_count": 2**18,
        "flavor": GGCDict, "next_level": _REMOTE_STORE}
)
