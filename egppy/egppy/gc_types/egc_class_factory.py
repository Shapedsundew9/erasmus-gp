"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""

from typing import Any, Mapping

from egpcommon.common import EGC_KVT
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.c_graph_abc import CGraphABC
from egppy.c_graph.c_graph_class_factory import NULL_c_graph, FrozenCGraph
from egppy.gc_types.gc import GCABC, NULL_GC, NULL_SIGNATURE, GCMixin
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EGCMixin(GCMixin):
    """Embryonic Genetic Code Mixin Class."""

    # The types are used for perising the genetic code object to a database.
    GC_KEY_TYPES: dict[str, dict[str, str | bool]] = EGC_KVT

    # Keys that reference other GC's
    REFERENCE_KEYS: set[str] = {"gca", "gcb", "ancestora", "ancestorb", "pgc"}

    def consistency(self) -> None:
        """Check the genetic code object for consistency.

        Raises:
            ValueError: If the genetic code object is inconsistent.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Only codons can have GCA, PGC or Ancestor A NULL. Then all must be NULL.
        if self["gca"] is NULL_GC or self["pgc"] is NULL_GC or self["ancestora"] is NULL_GC:
            if (
                self["gca"] is not NULL_GC
                or self["gcb"] is not NULL_GC
                or self["pgc"] is not NULL_GC
                or self["ancestora"] is not NULL_GC
                or self["ancestorb"] is not NULL_GC
            ):
                _logger.log(
                    level=CONSISTENCY,
                    msg="\n"
                    f"gca = {self['gca']}\n"
                    f"gcb = {self['gcb']}\n"
                    f"pgc = {self['pgc']}\n"
                    f"ancestora = {self['ancestora']}\n"
                    f"ancestorb = {self['ancestorb']}\n",
                )
                assert False, "One or more of GCA, PGC or Ancestor A is NULL but not all are NULL."
        for key in (k for k in self if not isinstance(self[k], GCABC)):
            if getattr(self[key], "consistency", None) is not None:
                self[key].consistency()
        if self["signature"] is not NULL_SIGNATURE:
            assert self.signature() == self["signature"], "Signature is incorrect."

    def resolve_references(self, mapping: Mapping[bytes, GCABC]) -> None:
        """Resolve the genetic code object references.

        All the reference values must be in the mapping provided. The reference values
        may be a hex string of the sha256 hash or a bytes object of the sha256 hash.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."
        for key in EGCMixin.REFERENCE_KEYS:
            if not isinstance(self[key], GCABC):
                ref = bytes.fromhex(self[key]) if isinstance(self[key], str) else self[key]
                self[key] = mapping[ref] if ref != NULL_GC else NULL_GC

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."
        tmp = gcabc.get("graph", NULL_c_graph)
        # Seems to by a pylint bug. pylance is happy.
        self["graph"] = (
            FrozenCGraph(tmp)  # pylint: disable=abstract-class-instantiated
            if not isinstance(tmp, CGraphABC)
            else tmp
        )
        tmp = gcabc.get("gca", NULL_GC) if gcabc.get("gca") is not None else NULL_GC
        self["gca"] = tmp if isinstance(tmp, (bytes, GCABC)) else bytes.fromhex(tmp)
        tmp = gcabc.get("gcb", NULL_GC) if gcabc.get("gcb") is not None else NULL_GC
        self["gcb"] = tmp if isinstance(tmp, (bytes, GCABC)) else bytes.fromhex(tmp)
        tmp = gcabc.get("ancestora", NULL_GC) if gcabc.get("ancestora") is not None else NULL_GC
        self["ancestora"] = tmp if isinstance(tmp, (bytes, GCABC)) else bytes.fromhex(tmp)
        tmp = gcabc.get("ancestorb", NULL_GC) if gcabc.get("ancestorb") is not None else NULL_GC
        self["ancestorb"] = tmp if isinstance(tmp, (bytes, GCABC)) else bytes.fromhex(tmp)
        tmp = gcabc.get("pgc", NULL_GC) if gcabc.get("pgc") is not None else NULL_GC
        self["pgc"] = tmp if isinstance(tmp, (bytes, GCABC)) else bytes.fromhex(tmp)
        tmp = gcabc.get("signature", NULL_SIGNATURE)
        if tmp is None:
            tmp = NULL_SIGNATURE
        assert isinstance(tmp, (bytes, str)), "Signature must be a bytes or hex string."
        self["signature"] = tmp if isinstance(tmp, bytes) else bytes.fromhex(tmp)

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self["graph"], CGraphABC), "graph must be a Connection Graph object"
        assert isinstance(self["gca"], (bytes, GCABC)), "gca must be a bytes or genetic code object"
        if isinstance(self["gca"], bytes):
            assert len(self["gca"]) == 32, "gca must be 32 bytes"
        assert isinstance(self["gcb"], (bytes, GCABC)), "gcb must be a bytes or genetic code object"
        if isinstance(self["gcb"], bytes):
            assert len(self["gcb"]) == 32, "gcb must be 32 bytes"
        assert isinstance(
            self["ancestora"], (bytes, GCABC)
        ), "ancestora must be a bytes or genetic code object"
        if isinstance(self["ancestora"], bytes):
            assert len(self["ancestora"]) == 32, "ancestora must be 32 bytes"
        assert isinstance(
            self["ancestorb"], (bytes, GCABC)
        ), "ancestorb must be a bytes or genetic code object"
        if isinstance(self["ancestorb"], bytes):
            assert len(self["ancestorb"]) == 32, "ancestorb must be 32 bytes"
        assert isinstance(self["pgc"], (bytes, GCABC)), "pgc must be a bytes or genetic code object"
        if isinstance(self["pgc"], bytes):
            assert len(self["pgc"]) == 32, "pgc must be 32 bytes"
        assert isinstance(self["signature"], bytes), "signature must be a bytes object"
        assert len(self["signature"]) == 32, "signature must be 32 bytes"
        for key in self:
            assert key in self.GC_KEY_TYPES, f"Invalid key: {key}"
            # Recursively calling verify on GCABC's can take a long time.
            if getattr(self[key], "verify", None) is not None and not isinstance(self[key], GCABC):
                self[key].verify()


class EGCDirtyDict(EGCMixin, CacheableDirtyDict, GCABC):  # type: ignore
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DirtyDictEGC

        gcabc -- the genetic code object or dictionary to set the attributes.

        Valid keys for the genetic code object are:
            graph:CGraphABC -- the genetic code graph object (optional)
            gca:bytes|GCABC -- the genetic code A object (optional)
            gcb:bytes|GCABC -- the genetic code B object (optional)
            ancestora:bytes|GCABC -- the genetic code A ancestor object (optional)
            ancestorb:bytes|GCABC -- the genetic code B ancestor object (optional)
            pgc:bytes|GCABC -- the parent genetic code object (optional)
        """
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


class EGCDict(EGCMixin, CacheableDict, GCABC):  # type: ignore
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DictEGC

        gcabc -- the genetic code object or dictionary to set the attributes.

        Valid keys for the genetic code object are:
            graph:CGraphABC -- the genetic code graph object (optional)
            gca:bytes|GCABC -- the genetic code A object (optional)
            gcb:bytes|GCABC -- the genetic code B object (optional)
            ancestora:bytes|GCABC -- the genetic code A ancestor object (optional)
            ancestorb:bytes|GCABC -- the genetic code B ancestor object (optional)
            pgc:bytes|GCABC -- the parent genetic code object (optional)
        """
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
