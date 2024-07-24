"""Universal Genetic Code Class Factory.

A Universal Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from typing import Any
from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.gc_types.gc import GCABC, GCMixin, GCProtocol
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class UGCDirtyDict(CacheableDirtyDict, GCMixin, GCProtocol, GCABC):
    """Universal Genetic Code Dirty Dictionary Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Initialize the Universal Genetic Code Dirty Dictionary"""
        super().__init__()
        self.set_members(gcabc=gcabc)


class UGCDict(CacheableDict, GCMixin, GCProtocol, GCABC):
    """Universal Genetic Code Dictionary Class."""

    def __init__(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Initialize the Universal Genetic Code Dictionary"""
        super().__init__()
        self.set_members(gcabc=gcabc)


UGCType = UGCDirtyDict | UGCDict
