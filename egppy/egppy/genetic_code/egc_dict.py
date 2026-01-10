"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""

from datetime import UTC, datetime
from itertools import count
from typing import Any
from uuid import UUID

from egpcommon.common import ANONYMOUS_CREATOR
from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import properties_store, signature_store, uuid_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import EGC_KVT
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.c_graph import CGraph, c_graph_type
from egppy.genetic_code.c_graph_abc import CGraphABC, FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import DstIfKey, JSONCGraph, SrcIfKey, SrcRow
from egppy.genetic_code.genetic_code import (
    GCABC,
    MERMAID_FOOTER,
    MERMAID_HEADER,
    mc_connection_str,
    mc_gc_str,
    mc_unknown_str,
)
from egppy.genetic_code.json_cgraph import json_cgraph_to_interfaces
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Universal UID generator
UID_GENERATOR = count(start=-(2**63))


# TODO: Once stable this should become a slotted class for performance.
class EGCDict(CacheableDict, GCABC):  # type: ignore
    """Embryonic Genetic Code Dictionary Class."""

    # The types are used for perising the genetic code object to a database.
    GC_KEY_TYPES: dict[str, dict[str, str | bool]] = EGC_KVT

    # Keys that reference other GC's
    REFERENCE_KEYS: frozenset[str] = frozenset({"gca", "gcb", "ancestora", "ancestorb", "pgc"})

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Initialize the EGCDict.
        Args:
            gcabc: The genetic code object or dictionary to initialize from.
        """
        # __init__ must do no more than this. All member setting must be
        # done in set_members() as it is used to rebuild the EGC.
        super().__init__()

        # UID and reference tracking for the EGC.
        # When an EGC is stabilized into a GGCode, all GC's that reference
        # it must be updated to reference the new GGCode instead.
        # These data members are not part of the GCABC interface (hence not set in
        # set_members) but are essential for EGC operation.
        if isinstance(self, EGCDict):
            self["uid"] = next(UID_GENERATOR)
            self["references"] = {}  # dict[(int, str=>field name), EGCDict]

        self.set_members(gcabc if gcabc is not None else {})

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> GCABC:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.

        Returns:
            self
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Connection Graph
        # It is intentional that the cgraph cannot be defaulted.
        cgraph: FrozenCGraphABC | JSONCGraph = gcabc.get("cgraph", CGraph({}))
        if isinstance(cgraph, CGraphABC):
            self["cgraph"] = cgraph
        elif isinstance(cgraph, FrozenCGraphABC):
            # EGDict must be mutable, so convert FrozenCGraph to CGraph
            self["cgraph"] = CGraph(cgraph)
        else:
            # json_cgraph_to_interfaces may return a type not statically recognized
            # as valid input for CGraph,
            # but runtime checks ensure correctness; type ignore is required
            # for pyright/mypy compatibility.
            self["cgraph"] = CGraph(json_cgraph_to_interfaces(cgraph))

        # GCA
        # NULL signatures are now represented as None for storage and computation efficiency.
        tgca: str | bytes | GCABC | None = gcabc.get("gca")
        if isinstance(tgca, str):
            tgca = bytes.fromhex(tgca)
        if isinstance(tgca, bytes):
            self["gca"] = signature_store[tgca]
        else:
            self["gca"] = tgca

        # GCB
        tgcb: str | bytes | GCABC | None = gcabc.get("gcb")
        if isinstance(tgcb, str):
            tgcb = bytes.fromhex(tgcb)
        if isinstance(tgcb, bytes):
            self["gcb"] = signature_store[tgcb]
        else:
            self["gcb"] = tgcb

        # Ancestor A
        taa: str | bytes | GCABC | None = gcabc.get("ancestora")
        if isinstance(taa, str):
            taa = bytes.fromhex(taa)
        if isinstance(taa, bytes):
            self["ancestora"] = signature_store[taa]
        else:
            self["ancestora"] = taa

        # Ancestor B
        tab: str | bytes | GCABC | None = gcabc.get("ancestorb")
        if isinstance(tab, str):
            tab = bytes.fromhex(tab)
        if isinstance(tab, bytes):
            self["ancestorb"] = signature_store[tab]
        else:
            self["ancestorb"] = tab

        # Parent Genetic Code
        tpgc: str | bytes | GCABC | None = gcabc.get("pgc")
        if isinstance(tpgc, str):
            tpgc = bytes.fromhex(tpgc)
        if isinstance(tpgc, bytes):
            self["pgc"] = signature_store[tpgc]
        else:
            self["pgc"] = tpgc

        # Created Timestamp
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = datetime.fromisoformat(tmp) if isinstance(tmp, str) else tmp

        # Properties
        prps: int | dict[str, Any] = gcabc.get("properties", 0)
        self["properties"] = properties_store[
            (
                prps
                if isinstance(prps, int)
                else PropertiesBD(prps, False).to_int() if isinstance(prps, dict) else prps.to_int()
            )
        ]

        # Creator
        creator = gcabc.get("creator", ANONYMOUS_CREATOR)
        creator = UUID(creator) if isinstance(creator, str) else creator
        self["creator"] = uuid_store[creator]

        return self

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)

    def __eq__(self, other: object) -> bool:
        """Return True if the genetic code objects have the same signature."""
        return (
            isinstance(other, GCABC)
            and self["gca"] == other["gca"]
            and self["gcb"] == other["gcb"]
            and self["cgraph"] == other["cgraph"]
        )

    def __hash__(self) -> int:
        """Return the hash of the genetic code object.
        Signature is guaranteed unique for a given genetic code.
        """
        return hash(self["gca"]) ^ hash(self["gcb"]) ^ hash(self["cgraph"])

    def is_codon(self) -> bool:
        """Return True if the genetic code is a codon or meta-codon."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        codon = PropertiesBD.fast_fetch("gc_type", self["properties"])
        retval = codon == GCType.CODON or codon == GCType.META
        assert (
            retval and c_graph_type(self["cgraph"]) == CGraphType.PRIMITIVE
        ) or not retval, "If gc_type is a codon or meta-codon then cgraph must be primitive."
        assert (
            retval and self["ancestora"] is None and self["ancestorb"] is None
        ) or not retval, "Codons must not have ancestors."
        return retval

    def is_conditional(self) -> bool:
        """Return True if the genetic code is conditional."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        cgt: CGraphType = c_graph_type(self["cgraph"])
        return cgt == CGraphType.IF_THEN or cgt == CGraphType.IF_THEN_ELSE

    def is_meta(self) -> bool:
        """Return True if the genetic code is a meta-codon."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        meta = PropertiesBD.fast_fetch("gc_type", self["properties"]) == GCType.META
        assert (
            meta and c_graph_type(self["cgraph"]) == CGraphType.PRIMITIVE
        ) or not meta, "If gc_type is a meta-codon then cgraph must be primitive."
        assert (
            meta and self["ancestora"] is None and self["ancestorb"] is None
        ) or not meta, "Meta-codons must not have ancestors."
        return meta

    def is_pgc(self) -> bool:
        """Return True if the genetic code is a physical genetic code (PGC)."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        is_pgc = PropertiesBD.fast_fetch("is_pgc", self["properties"])
        return is_pgc

    def logical_mermaid_chart(self) -> str:
        """Return a Mermaid chart of the logical genetic code structure."""
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        work_queue: list[tuple[GCABC, GCABC | bytes, GCABC | bytes, str]] = [
            (self, self["gca"], self["gcb"], "0")
        ]
        chart_txt: list[str] = [mc_gc_str(self, "0", SrcRow.I)]
        # Each instance of the same GC must have a unique id in the chart
        counter = count(1)
        while work_queue:
            gc, gca, gcb, cts = work_queue.pop(0)
            # deepcode ignore unguarded~next~call: This is an infinite generator
            nct = str(next(counter))
            for gcx, prefix, row in [(gca, "a" + nct, SrcRow.A), (gcb, "b" + nct, SrcRow.B)]:
                if isinstance(gcx, GCABC) and gcx is not None:
                    work_queue.append((gcx, gcx["gca"], gcx["gcb"], prefix))
                    chart_txt.append(mc_gc_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
                if isinstance(gcx, bytes) and gcx is not None:
                    chart_txt.append(mc_unknown_str(gcx, prefix, row))
                    chart_txt.append(mc_connection_str(gc, cts, gcx, prefix))
        return "\n".join(MERMAID_HEADER + chart_txt + MERMAID_FOOTER)

    def verify(self) -> None:
        """Verify the genetic code object.

        Performs comprehensive runtime validation of the EGC structure including:
        - Type and length validation of all members
        - GC type and connection graph consistency checks
        - Ancestral relationship validation based on GC type
        - Properties validation

        Raises:
            DebugTypeError: If any member has an incorrect type (DEBUG mode only).
            DebugValueError: If any value constraint is violated (DEBUG mode only).
            ValueError: If GC type and connection graph constraints are violated.
            RuntimeError: If properties validation fails.
        """
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)

        assert isinstance(self, GCABC), "EGC must be a GCABC object."
        assert isinstance(self, CommonObj), "EGC must be a CommonObj."

        # Get properties for validation
        properties = PropertiesBD(self["properties"])
        gc_type = properties["gc_type"]
        graph_type = properties["graph_type"]

        if _logger.isEnabledFor(level=DEBUG):

            # These are necessary as EGCDict must use object references to other GC's
            # and GGCDict uses signatures. Due to circular importing we cannot use isinstance
            # checks against GGCDict here.
            if type(self) is EGCDict:  # pylint: disable=unidiomatic-typecheck
                self.debug_type_error(
                    isinstance(self["cgraph"], CGraphABC),
                    "cgraph must be a Connection Graph object",
                )
                self.debug_type_error(
                    self["gca"] is None or isinstance(self["gca"], GCABC),
                    "gca must be None or a GCABC object",
                )
                self.debug_type_error(
                    self["gcb"] is None or isinstance(self["gcb"], GCABC),
                    "gcb must be None or a GCABC object",
                )
                self.debug_type_error(
                    self["ancestora"] is None or isinstance(self["ancestora"], GCABC),
                    "ancestora must be None or a GCABC object",
                )
                self.debug_type_error(
                    self["ancestorb"] is None or isinstance(self["ancestorb"], GCABC),
                    "ancestorb must be None or a GCABC object",
                )
                self.debug_type_error(
                    self["pgc"] is None or isinstance(self["pgc"], GCABC),
                    "pgc must be None or a GCABC object",
                )
            self.debug_type_error(isinstance(self["created"], datetime), "created must be datetime")
            self.debug_type_error(isinstance(self["properties"], int), "properties must be int")

            # Verify the connection graph
            self["cgraph"].verify()

            # Validate properties bitdict
            self.debug_runtime_error(properties.valid(), "Properties bitdict is invalid")

            # GC Type and Connection Graph Type Constraints
            # Reference: egppy/egppy/genetic_code/docs/gc_types.md

            if graph_type == CGraphType.PRIMITIVE:
                # PRIMITIVE graphs can only be used with CODON or META types
                self.debug_value_error(
                    gc_type in (GCType.CODON, GCType.META),
                    f"PRIMITIVE connection graph requires gc_type to be CODON or META, "
                    f"but got {GCType(gc_type).name}",
                )
            elif gc_type == GCType.CODON:
                # CODON type must use PRIMITIVE graph
                self.debug_value_error(
                    graph_type == CGraphType.PRIMITIVE,
                    f"CODON gc_type requires PRIMITIVE connection graph, "
                    f"but got {CGraphType(graph_type).name}",
                )
            elif gc_type == GCType.META:
                # META type must use PRIMITIVE or STANDARD graph
                self.debug_value_error(
                    graph_type == CGraphType.PRIMITIVE,
                    f"META gc_type requires a PRIMITIVE connection graph, "
                    f"but got {CGraphType(graph_type).name}",
                )
            elif gc_type == GCType.ORDINARY:
                # ORDINARY can use STANDARD, IF_THEN, IF_THEN_ELSE, FOR_LOOP, WHILE_LOOP, EMPTY
                self.debug_value_error(
                    graph_type
                    in (
                        CGraphType.STANDARD,
                        CGraphType.IF_THEN,
                        CGraphType.IF_THEN_ELSE,
                        CGraphType.FOR_LOOP,
                        CGraphType.WHILE_LOOP,
                        CGraphType.EMPTY,
                    ),
                    f"ORDINARY gc_type cannot use {CGraphType(graph_type).name} connection graph",
                )
            PropertiesBD(self["properties"]).verify()

        # Ancestral Relationship Validation based on Connection Graph Structure
        # Reference: egppy/egppy/genetic_code/docs/gc_types.md - Validation Rules
        cgraph = self["cgraph"]
        has_row_a = DstIfKey.AD in cgraph or SrcIfKey.AS in cgraph
        has_row_b = DstIfKey.BD in cgraph or SrcIfKey.BS in cgraph

        # Validate gca against connection graph structure
        if has_row_a and graph_type != CGraphType.PRIMITIVE:
            self.value_error(
                self["gca"] is not None,
                "Connection graph has Row A defined, but gca is None",
            )
        else:
            self.value_error(
                self["gca"] is None,
                "Connection graph has no Row A defined, but gca is not None",
            )

        # Validate gcb against connection graph structure
        if has_row_b:
            self.value_error(
                self["gcb"] is not None,
                "Connection graph has Row B defined, but gcb is None",
            )
        else:
            self.value_error(
                self["gcb"] is None,
                "Connection graph has no Row B defined, but gcb is not None",
            )

        # PRIMITIVE graphs have no ancestors or pgc
        if graph_type == CGraphType.PRIMITIVE:
            self.value_error(
                self["ancestora"] is None,
                "PRIMITIVE connection graph requires ancestora to be None",
            )
            self.value_error(
                self["ancestorb"] is None,
                "PRIMITIVE connection graph requires ancestorb to be None",
            )
            self.value_error(
                self["pgc"] is None,
                "PRIMITIVE connection graph requires pgc to be None",
            )

        # CODON type validation (codons have no ancestors)
        if gc_type == GCType.CODON:
            self.value_error(self["gca"] is None, "CODON gc_type requires gca to be None")
            self.value_error(self["gcb"] is None, "CODON gc_type requires gcb to be None")
            self.value_error(
                self["ancestora"] is None,
                "CODON gc_type requires ancestora to be None",
            )
            self.value_error(
                self["ancestorb"] is None,
                "CODON gc_type requires ancestorb to be None",
            )
            self.value_error(self["pgc"] is None, "CODON gc_type requires pgc to be None")

        # META type validation (meta-codons have no ancestors)
        if gc_type == GCType.META:
            self.value_error(
                graph_type == CGraphType.PRIMITIVE,
                "META gc_type requires PRIMITIVE connection graph",
            )
            self.value_error(self["gca"] is None, "META codon requires gca to be None")
            self.value_error(self["gcb"] is None, "META codon requires gcb to be None")
            self.value_error(
                self["ancestora"] is None,
                "META codon requires ancestora to be None",
            )
            self.value_error(
                self["ancestorb"] is None,
                "META codon requires ancestorb to be None",
            )
            self.value_error(self["pgc"] is None, "META codon requires pgc to be None")
            self.value_error(
                not (properties["gctsp"]["type_upcast"] and properties["gctsp"]["type_downcast"]),
                "META codon cannot be both type upcast and type downcast",
            )

        # ORDINARY type validation (ordinary codes have ancestors and pgc)
        if gc_type == GCType.ORDINARY:
            # At least one of gca or gcb must be present for ordinary codes
            self.value_error(
                self["gca"] is not None or self["gcb"] is not None,
                "ORDINARY gc_type requires at least one of gca or gcb to be non-None",
            )

        # Extra coverage is asserted in DEBUG mode
        if _logger.isEnabledFor(level=DEBUG):
            self.is_codon()
            self.is_meta()
            self.is_conditional()

        # Call base class verify at the end
        super().verify()
