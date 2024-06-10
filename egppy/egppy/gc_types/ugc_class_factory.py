"""Universal Genetic Code Class Factory.

A Universal Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from typing import Union
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.gc_base import GCBase
from egppy.gc_types.gc_illegal import GCIllegal
from egppy.storage.cache.cacheable_dict import CacheableDict
from egppy.storage.cache.cacheable_dirty_dict import CacheableDirtyDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class UGCBase(GCBase):
    """Universal Genetic Code Base Class."""


class DirtyDictUGC(GCIllegal, CacheableDirtyDict, UGCBase, GCABC):
    """Dirty Dictionary Universal Genetic Code Class."""

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for DirtyDictUGC"""
        CacheableDirtyDict.__init__(self, *args, **kwargs)
        UGCBase.__init__(self, *args, **kwargs)


class DictUGC(GCIllegal, CacheableDict, UGCBase, GCABC):
    """Dictionary Universal Genetic Code Class."""

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for DictUGC"""
        CacheableDict.__init__(self, *args, **kwargs)
        UGCBase.__init__(self, *args, **kwargs)


UGCType = DirtyDictUGC | DictUGC
