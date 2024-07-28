"""Universal Genetic Code Class Factory.

A Universal Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from typing import Any
from egppy.gc_types.gc import GCABC, GCProtocol
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.gc_types.ggc_class_factory import GGCMixin
from egppy.gc_types.pgc_class_factory import PGCMixin
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class UGCMixin(GGCMixin, PGCMixin, GCProtocol):
    """Universal Genetic Code Mixin Class."""

    GC_KEY_TYPES: dict[str, str] = GGCMixin.GC_KEY_TYPES | PGCMixin.GC_KEY_TYPES

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency."""
        GGCMixin.consistency(self)
        PGCMixin.consistency(self)

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the UGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        GGCMixin.set_members(self, gcabc)
        PGCMixin.set_members(self, gcabc)

    def verify(self: GCProtocol) -> None:
        """Verify the genetic code object."""
        GGCMixin.verify(self)
        PGCMixin.verify(self)


class UGCDirtyDict(CacheableDirtyDict, UGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictUGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDirtyDict.consistency(self)
        UGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDirtyDict.verify(self)
        UGCMixin.verify(self)


class UGCDict(CacheableDict, UGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictUGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)
        UGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)
        UGCMixin.verify(self)


UGCType = UGCDirtyDict | UGCDict
