"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""

from datetime import datetime, UTC
from typing import Any

from egpcommon.gp_db_config import EGC_KVT
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.properties import PropertiesBD

from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.genetic_code import GCABC, NULL_SIGNATURE, GCMixin
from egppy.genetic_code.c_graph_constants import JSONCGraph
from egppy.genetic_code.interface import Interface
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

    def consistency(self) -> bool:
        """Check the genetic code object for consistency.

        Raises:
            ValueError: If the genetic code object is inconsistent.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Only codons can have GCA, PGC or Ancestor A NULL. Then all must be NULL.
        if (
            self["gca"] is NULL_SIGNATURE
            or self["pgc"] is NULL_SIGNATURE
            or self["ancestora"] is NULL_SIGNATURE
        ):
            if (
                self["gca"] is not NULL_SIGNATURE
                or self["gcb"] is not NULL_SIGNATURE
                or self["pgc"] is not NULL_SIGNATURE
                or self["ancestora"] is not NULL_SIGNATURE
                or self["ancestorb"] is not NULL_SIGNATURE
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

        return True

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Connection Graph
        cgraph: CGraph | dict[str, Interface] | JSONCGraph = gcabc["cgraph"]
        self["cgraph"] = cgraph.copy() if isinstance(cgraph, CGraph) else CGraph(cgraph)

        # GCA
        tgca: str | bytes | GCABC = gcabc.get("gca", NULL_SIGNATURE)
        gca: str | bytes = tgca["signature"] if isinstance(tgca, GCABC) else tgca
        self["gca"] = bytes.fromhex(gca) if isinstance(gca, str) else gca

        # GCB
        tgcb: str | bytes | GCABC = gcabc.get("gcb", NULL_SIGNATURE)
        gcb: str | bytes = tgcb["signature"] if isinstance(tgcb, GCABC) else tgcb
        self["gcb"] = bytes.fromhex(gcb) if isinstance(gcb, str) else gcb

        # Ancestor A
        taa: str | bytes | GCABC = gcabc.get("ancestora", NULL_SIGNATURE)
        ancestora: str | bytes = taa["signature"] if isinstance(taa, GCABC) else taa
        self["ancestora"] = bytes.fromhex(ancestora) if isinstance(ancestora, str) else ancestora

        # Ancestor B
        tab: str | bytes | GCABC = gcabc.get("ancestorb", NULL_SIGNATURE)
        ancestorb: str | bytes = tab["signature"] if isinstance(tab, GCABC) else tab
        self["ancestorb"] = bytes.fromhex(ancestorb) if isinstance(ancestorb, str) else ancestorb

        # Parent Genetic Code
        tpgc: str | bytes | GCABC = gcabc.get("pgc", NULL_SIGNATURE)
        self["pgc"] = bytes.fromhex(tpgc) if isinstance(tpgc, str) else tpgc
        self["pgc"] = self["pgc"] if isinstance(self["pgc"], bytes) else NULL_SIGNATURE

        # Created Timestamp
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = datetime.fromisoformat(tmp) if isinstance(tmp, str) else tmp

        # Properties
        prps: int | dict[str, Any] = gcabc.get("properties", 0)
        self["properties"] = prps if isinstance(prps, int) else PropertiesBD(prps, False).to_int()

        # Signature
        tmp: str | bytes = gcabc.get("signature", NULL_SIGNATURE)
        self["signature"] = bytes.fromhex(tmp) if isinstance(tmp, str) else tmp

    def verify(self) -> bool:
        """Verify the genetic code object."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self["graph"], CGraph), "graph must be a Connection Graph object"
        assert isinstance(self["gca"], bytes), "gca must be a bytes object"
        assert len(self["gca"]) == 32, "gca must be 32 bytes"
        assert isinstance(self["gcb"], bytes), "gcb must be a bytes object"
        assert len(self["gcb"]) == 32, "gcb must be 32 bytes"
        assert isinstance(self["ancestora"], bytes), "ancestora must be a bytes object"
        assert len(self["ancestora"]) == 32, "ancestora must be 32 bytes"
        assert isinstance(self["ancestorb"], bytes), "ancestorb must be a bytes object"
        if isinstance(self["ancestorb"], bytes):
            assert len(self["ancestorb"]) == 32, "ancestorb must be 32 bytes"
        assert isinstance(self["pgc"], bytes), "pgc must be a bytes object"
        assert len(self["pgc"]) == 32, "pgc must be 32 bytes"
        assert isinstance(self["signature"], bytes), "signature must be a bytes object"
        assert len(self["signature"]) == 32, "signature must be 32 bytes"
        for key in self:
            assert key in self.GC_KEY_TYPES, f"Invalid key: {key}"
            # Recursively calling verify on GCABC's can take a long time.
            if getattr(self[key], "verify", None) is not None and not isinstance(self[key], GCABC):
                self[key].verify()
        return True


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

    def consistency(self) -> bool:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        return CacheableDict.consistency(self) and EGCMixin.consistency(self)

    def verify(self) -> bool:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        return CacheableDict.verify(self) and EGCMixin.verify(self)
