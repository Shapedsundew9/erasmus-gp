"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.gc_types.gc import GCABC, GCMixin, GCProtocol, NULL_GC
from egppy.storage.cache.cacheable_obj import CacheableDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EGCMixin(GCMixin):
    """Embryonic Genetic Code Mixin Class."""

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency.

        Raises:
            ValueError: If the genetic code object is inconsistent.
        """
        # Only codons can have GCA, PGC or Ancestor A NULL. Then all must be NULL.
        # TODO: Add graph check to this.
        if self['gca'] is NULL_GC or self['pgc'] is NULL_GC or self['ancestora'] is NULL_GC:
            if (self['gca'] is not NULL_GC
                or self['gcb'] is not NULL_GC
                or self['pgc'] is not NULL_GC
                or self['ancestora'] is not NULL_GC
                or self['ancestorb'] is not NULL_GC):
                _logger.log(level=CONSISTENCY, msg=
                            "\n"
                            f"gca = {self['gca']}\n"
                            f"gcb = {self['gcb']}\n"
                            f"pgc = {self['pgc']}\n"
                            f"ancestora = {self['ancestora']}\n"
                            f"ancestorb = {self['ancestorb']}\n")
                raise ValueError(
                    "One or more of GCA, PGC or Ancestor A is NULL but not all are NULL.")

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        self['graph']=gcabc.get('graph', {})
        self['gca']=gcabc.get('gca', NULL_GC)
        self['gcb']=gcabc.get('gcb', NULL_GC)
        self['ancestora']=gcabc.get('ancestora', NULL_GC)
        self['ancestorb']=gcabc.get('ancestorb', NULL_GC)
        self['pgc']=gcabc.get('pgc', NULL_GC)

    def verify(self: GCProtocol) -> None:
        """Verify the genetic code object.

        Raises:
            ValueError: If the genetic code object is invalid.
        """
        if not isinstance(self['graph'], dict):
            raise ValueError("graph must be a dictionary")
        if not issubclass(self['gca'], GCABC):
            raise ValueError("gca must be a genetic code object")
        if not issubclass(self['gcb'], GCABC):
            raise ValueError("gcb must be a genetic code object")
        if not issubclass(self['ancestora'], GCABC):
            raise ValueError("ancestora must be a genetic code object")
        if not issubclass(self['ancestorb'], GCABC):
            raise ValueError("ancestorb must be a genetic code object")
        if not issubclass(self['pgc'], GCABC):
            raise ValueError("pgc must be a genetic code object")


class EGCDirtyDict(CacheableDirtyDict, EGCMixin, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictEGC"""
        super().__init__()
        self.set_members(gcabc)  # type: ignore


class EGCDict(CacheableDict, EGCMixin, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictEGC"""
        super().__init__()
        self.set_members(gcabc)  # type: ignore


EGCType = EGCDirtyDict | EGCDict
