"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""

from datetime import UTC, datetime
from typing import Any

from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import properties_store, signature_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import EGC_KVT
from egpcommon.properties import PropertiesBD
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import JSONCGraph
from egppy.genetic_code.genetic_code import GCABC, NULL_SIGNATURE, GCMixin
from egppy.genetic_code.interface import Interface
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class EGCMixin(GCMixin):
    """Embryonic Genetic Code Mixin Class."""

    # The types are used for perising the genetic code object to a database.
    GC_KEY_TYPES: dict[str, dict[str, str | bool]] = EGC_KVT

    # Keys that reference other GC's
    REFERENCE_KEYS: set[str] = {"gca", "gcb", "ancestora", "ancestorb", "pgc"}

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Connection Graph
        # It is intentional that the cgraph cannot be defaulted.
        cgraph: CGraph | dict[str, Interface] | JSONCGraph = gcabc["cgraph"]
        self["cgraph"] = cgraph.copy() if isinstance(cgraph, CGraph) else CGraph(cgraph)

        # GCA
        tgca: str | bytes | GCABC = NULL_SIGNATURE if gcabc.get("gca") is None else gcabc["gca"]
        gca: str | bytes = tgca["signature"] if isinstance(tgca, GCABC) else tgca
        self["gca"] = signature_store[bytes.fromhex(gca) if isinstance(gca, str) else gca]

        # GCB
        tgcb: str | bytes | GCABC = NULL_SIGNATURE if gcabc.get("gcb") is None else gcabc["gcb"]
        gcb: str | bytes = tgcb["signature"] if isinstance(tgcb, GCABC) else tgcb
        self["gcb"] = signature_store[bytes.fromhex(gcb) if isinstance(gcb, str) else gcb]

        # Ancestor A
        taa: str | bytes | GCABC = (
            NULL_SIGNATURE if gcabc.get("ancestora") is None else gcabc["ancestora"]
        )
        ancestora: str | bytes = taa["signature"] if isinstance(taa, GCABC) else taa
        self["ancestora"] = signature_store[
            bytes.fromhex(ancestora) if isinstance(ancestora, str) else ancestora
        ]

        # Ancestor B
        tab: str | bytes | GCABC = (
            NULL_SIGNATURE if gcabc.get("ancestorb") is None else gcabc["ancestorb"]
        )
        ancestorb: str | bytes = tab["signature"] if isinstance(tab, GCABC) else tab
        self["ancestorb"] = signature_store[
            bytes.fromhex(ancestorb) if isinstance(ancestorb, str) else ancestorb
        ]

        # Parent Genetic Code
        tpgc: str | bytes | GCABC = NULL_SIGNATURE if gcabc.get("pgc") is None else gcabc["pgc"]
        pgc: str | bytes = tpgc["signature"] if isinstance(tpgc, GCABC) else tpgc
        self["pgc"] = signature_store[bytes.fromhex(pgc) if isinstance(pgc, str) else pgc]

        # Created Timestamp
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = datetime.fromisoformat(tmp) if isinstance(tmp, str) else tmp

        # Properties
        prps: int | dict[str, Any] = gcabc.get("properties", 0)
        self["properties"] = properties_store[
            prps if isinstance(prps, int) else PropertiesBD(prps, False).to_int()
        ]

        # Signature
        tmp: str | bytes = gcabc.get("signature", NULL_SIGNATURE)
        self["signature"] = signature_store[bytes.fromhex(tmp) if isinstance(tmp, str) else tmp]

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self, CommonObj), "GGC must be a CommonObj."

        if _logger.isEnabledFor(level=DEBUG):

            # Check types and lengths
            self.debug_type_error(
                isinstance(self["cgraph"], CGraph), "graph must be a Connection Graph object"
            )
            self.debug_type_error(isinstance(self["gca"], bytes), "gca must be a bytes object")
            self.debug_value_error(len(self["gca"]) == 32, "gca must be 32 bytes")
            self.debug_type_error(isinstance(self["gcb"], bytes), "gcb must be a bytes object")
            self.debug_value_error(len(self["gcb"]) == 32, "gcb must be 32 bytes")
            self.debug_type_error(
                isinstance(self["ancestora"], bytes), "ancestora must be a bytes object"
            )
            self.debug_value_error(len(self["ancestora"]) == 32, "ancestora must be 32 bytes")
            self.debug_type_error(
                isinstance(self["ancestorb"], bytes), "ancestorb must be a bytes object"
            )
            self.debug_value_error(len(self["ancestorb"]) == 32, "ancestorb must be 32 bytes")
            self.debug_type_error(isinstance(self["pgc"], bytes), "pgc must be a bytes object")
            self.debug_value_error(len(self["pgc"]) == 32, "pgc must be 32 bytes")
            self.debug_type_error(
                isinstance(self["signature"], bytes), "signature must be a bytes object"
            )
            self.debug_value_error(len(self["signature"]) == 32, "signature must be 32 bytes")

        # Call base class verify at the end
        super().verify()


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
