"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""
from typing import Any, Mapping
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.gc_types.gc import GCABC, GCBase, GCMixin, GCProtocol, NULL_GC, NULL_SIGNATURE
from egppy.gc_graph.gc_graph_class_factory import EMPTY_GC_GRAPH
from egppy.storage.cache.cacheable_obj import CacheableDict
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EGCMixin(GCMixin, GCProtocol):
    """Embryonic Genetic Code Mixin Class."""

    # The types are used for perising the genetic code object to a database.
    GC_KEY_TYPES: dict[str, str] = {
        'graph': "BYTEA[]",
        'gca': "BYTEA[32]",
        'gcb': "BYTEA[32]",
        'ancestora': "BYTEA[32]",
        'ancestorb': "BYTEA[32]",
        'pgc': "BYTEA[32]",
        'signature': "BYTEA[32]"
    }
    REFERENCE_KEYS: set[str] = {
        'gca',
        'gcb',
        'ancestora',
        'ancestorb',
        'pgc'
    }

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency.

        Raises:
            ValueError: If the genetic code object is inconsistent.
        """
        # Only codons can have GCA, PGC or Ancestor A NULL. Then all must be NULL.
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
                assert False, "One or more of GCA, PGC or Ancestor A is NULL but not all are NULL."
        for key in self:
            if getattr(self[key], 'consistency', None) is not None:
                self[key].consistency()
        if self['signature'] is not NULL_SIGNATURE:
            assert self.signature() == self['signature'], "Signature is incorrect."
        super().consistency()

    def resolve_references(self: GCProtocol, mapping: Mapping[bytes, GCABC]) -> None:
        """Resolve the genetic code object references.
        
        All the reference values must be in the mapping provided. The reference values
        may be a hex string of the sha256 hash or a bytes object of the sha256 hash.
        """
        for key in EGCMixin.REFERENCE_KEYS:
            if not isinstance(self[key], GCABC):
                ref = bytes.fromhex(self[key]) if isinstance(self[key], str) else self[key]
                self[key] = mapping[ref] if ref != NULL_GC else NULL_GC

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        self['graph']=gcabc.get('graph', EMPTY_GC_GRAPH)
        self['gca']=gcabc.get('gca', NULL_GC)
        self['gcb']=gcabc.get('gcb', NULL_GC)
        self['ancestora']=gcabc.get('ancestora', NULL_GC)
        self['ancestorb']=gcabc.get('ancestorb', NULL_GC)
        self['pgc']=gcabc.get('pgc', NULL_GC)
        self['signature']=gcabc.get('signature', NULL_SIGNATURE)

    def verify(self: GCProtocol) -> None:
        """Verify the genetic code object."""
        assert isinstance(self['graph'], GCGraphABC), "graph must be a GC graph object"
        assert issubclass(self['gca'], GCABC), "gca must be a genetic code object"
        assert issubclass(self['gcb'], GCABC), "gcb must be a genetic code object"
        assert issubclass(self['ancestora'], GCABC), "ancestora must be a genetic code object"
        assert issubclass(self['ancestorb'], GCABC), "ancestorb must be a genetic code object"
        assert issubclass(self['pgc'], GCABC), "pgc must be a genetic code object"
        assert isinstance(self['signature'], bytes), "signature must be a bytes object"
        assert len(self['signature']) == 32, "signature must be 32 bytes"
        for key in self:
            assert key in self.GC_KEY_TYPES, f"Invalid key: {key}"
            if getattr(self[key], 'verify', None) is not None:
                self[key].verify()
        super().verify()


class EGCDirtyDict(GCBase, CacheableDirtyDict, EGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DirtyDictEGC"""
        super().__init__()
        self.set_members(gcabc if gcabc is not None else {})

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDirtyDict.consistency(self)
        EGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDirtyDict.verify(self)
        EGCMixin.verify(self)


class EGCDict(GCBase, CacheableDict, EGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DirtyDictEGC"""
        super().__init__()
        self.set_members(gcabc if gcabc is not None else {})

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)
        EGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)
        EGCMixin.verify(self)


EGCType = EGCDirtyDict | EGCDict
