"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""

from copy import deepcopy
from datetime import UTC, datetime
from itertools import count
from typing import Any
from uuid import UUID

from egpcommon.common import ANONYMOUS_CREATOR, NULL_STR, NULL_TUPLE, sha256_signature
from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import properties_store, signature_store, uuid_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import EGC_KVT
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.c_graph import CGraph, c_graph_type
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import JSONCGraph, SrcRow
from egppy.genetic_code.genetic_code import (
    GCABC,
    MERMAID_FOOTER,
    MERMAID_HEADER,
    mc_connection_str,
    mc_gc_str,
    mc_unknown_str,
)
from egppy.genetic_code.json_cgraph import json_cgraph_to_interfaces
from egppy.genetic_code.types_def import types_def_store
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class EGCDict(CacheableDict, GCABC):  # type: ignore
    """Embryonic Genetic Code Dictionary Class."""

    # The types are used for perising the genetic code object to a database.
    GC_KEY_TYPES: dict[str, dict[str, str | bool]] = EGC_KVT

    # Keys that reference other GC's
    REFERENCE_KEYS: set[str] = {"gca", "gcb", "ancestora", "ancestorb", "pgc"}

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Initialize the EGCDict.
        Args:
            gcabc: The genetic code object or dictionary to initialize from.
        """
        super().__init__()
        self.set_members(gcabc if gcabc is not None else {})

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the EGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        assert isinstance(self, GCABC), "EGC must be a GCABC object."

        # Connection Graph
        # It is intentional that the cgraph cannot be defaulted.
        cgraph: CGraphABC | JSONCGraph = gcabc["cgraph"]
        if isinstance(cgraph, CGraphABC):
            self["cgraph"] = cgraph
        else:
            # json_cgraph_to_interfaces may return a type not statically recognized
            # as valid input for CGraph,
            # but runtime checks ensure correctness; type ignore is required
            # for pyright/mypy compatibility.
            self["cgraph"] = CGraph(json_cgraph_to_interfaces(cgraph))

        # GCA
        # NULL signatures are now represented as None for storage and computation efficiency.
        tgca: str | bytes | GCABC | None = gcabc.get("gca")
        if tgca is None:
            self["gca"] = None
        else:
            gca: str | bytes = tgca["signature"] if isinstance(tgca, GCABC) else tgca
            self["gca"] = signature_store[bytes.fromhex(gca) if isinstance(gca, str) else gca]

        # GCB
        tgcb: str | bytes | GCABC | None = gcabc.get("gcb")
        if tgcb is None:
            self["gcb"] = None
        else:
            gcb: str | bytes = tgcb["signature"] if isinstance(tgcb, GCABC) else tgcb
            self["gcb"] = signature_store[bytes.fromhex(gcb) if isinstance(gcb, str) else gcb]

        # Ancestor A
        taa: str | bytes | GCABC | None = gcabc.get("ancestora")
        if taa is None:
            self["ancestora"] = None
        else:
            ancestora: str | bytes = taa["signature"] if isinstance(taa, GCABC) else taa
            self["ancestora"] = signature_store[
                bytes.fromhex(ancestora) if isinstance(ancestora, str) else ancestora
            ]

        # Ancestor B
        tab: str | bytes | GCABC | None = gcabc.get("ancestorb")
        if tab is None:
            self["ancestorb"] = None
        else:
            ancestorb: str | bytes = tab["signature"] if isinstance(tab, GCABC) else tab
            self["ancestorb"] = signature_store[
                bytes.fromhex(ancestorb) if isinstance(ancestorb, str) else ancestorb
            ]

        # Parent Genetic Code
        tpgc: str | bytes | GCABC | None = gcabc.get("pgc")
        if tpgc is None:
            self["pgc"] = None
        else:
            pgc: str | bytes = tpgc["signature"] if isinstance(tpgc, GCABC) else tpgc
            self["pgc"] = signature_store[bytes.fromhex(pgc) if isinstance(pgc, str) else pgc]

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

        # Signature
        tmp: str | bytes | None = gcabc.get("signature")
        if tmp is None:
            self["signature"] = sha256_signature(
                self["ancestora"],
                self["ancestorb"],
                self["gca"],
                self["gcb"],
                self["cgraph"].to_json(True),
                self["pgc"],
                NULL_TUPLE,
                NULL_STR,
                NULL_STR,
                int(self["created"].timestamp()),
                self["creator"].bytes,
            )
        else:
            self["signature"] = signature_store[bytes.fromhex(tmp) if isinstance(tmp, str) else tmp]

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)

    def __eq__(self, other: object) -> bool:
        """Return True if the genetic code objects have the same signature."""
        assert isinstance(self, GCABC)
        return isinstance(other, GCABC) and self["signature"] == other["signature"]

    def __hash__(self) -> int:
        """Return the hash of the genetic code object.
        Signature is guaranteed unique for a given genetic code.
        """
        assert isinstance(self, GCABC)
        assert self["signature"] is not None, "Signature must not be None."
        return hash(self["signature"])

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

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        # Only keys that are persisted in the DB are included in the JSON.
        for key in (k for k in self if self.GC_KEY_TYPES.get(k, {})):
            value = self[key]
            if key == "meta_data":
                assert isinstance(value, dict), "Meta data must be a dict."
                md = deepcopy(value)
                if (
                    "function" in md
                    and "python3" in md["function"]
                    and "0" in md["function"]["python3"]
                    and "imports" in md["function"]["python3"]["0"]
                ):
                    md["function"]["python3"]["0"]["imports"] = [
                        imp.to_json() for imp in self["imports"]
                    ]
                retval[key] = md
            elif key == "properties":
                # Make properties humman readable.
                assert isinstance(value, int), "Properties must be an int."
                retval[key] = PropertiesBD(value).to_json()
            elif key.endswith("_types"):
                # Make types human readable.
                retval[key] = [types_def_store[t].name for t in value]
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value["signature"].hex() if value is not None else None
            elif isinstance(value, CGraphABC):
                # Need to set json_c_graph to True so that the endpoints are correctly serialized
                retval[key] = value.to_json(json_c_graph=True)
            elif getattr(self[key], "to_json", None) is not None:
                retval[key] = self[key].to_json()
            elif isinstance(value, bytes):
                retval[key] = value.hex()
            elif value is None:
                retval[key] = None
            elif isinstance(value, datetime):
                retval[key] = value.isoformat()
            elif isinstance(value, UUID):
                retval[key] = str(value)
            else:
                retval[key] = value
                if _logger.isEnabledFor(DEBUG):
                    assert isinstance(
                        value, (int, str, float, list, dict, tuple)
                    ), f"Invalid type: {type(value)}"
        return retval

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
            # Type and length validation for all members
            self.debug_type_error(
                isinstance(self["cgraph"], CGraphABC), "cgraph must be a Connection Graph object"
            )
            self.debug_type_error(
                self["gca"] is None or isinstance(self["gca"], bytes),
                "gca must be None or a bytes object",
            )
            if self["gca"] is not None:
                self.debug_value_error(len(self["gca"]) == 32, "gca must be 32 bytes")
            self.debug_type_error(
                self["gcb"] is None or isinstance(self["gcb"], bytes),
                "gcb must be None or a bytes object",
            )
            if self["gcb"] is not None:
                self.debug_value_error(len(self["gcb"]) == 32, "gcb must be 32 bytes")
            self.debug_type_error(
                self["ancestora"] is None or isinstance(self["ancestora"], bytes),
                "ancestora must be None or a bytes object",
            )
            if self["ancestora"] is not None:
                self.debug_value_error(len(self["ancestora"]) == 32, "ancestora must be 32 bytes")
            self.debug_type_error(
                self["ancestorb"] is None or isinstance(self["ancestorb"], bytes),
                "ancestorb must be None or a bytes object",
            )
            if self["ancestorb"] is not None:
                self.debug_value_error(len(self["ancestorb"]) == 32, "ancestorb must be 32 bytes")
            self.debug_type_error(
                self["pgc"] is None or isinstance(self["pgc"], bytes),
                "pgc must be None or a bytes object",
            )
            if self["pgc"] is not None:
                self.debug_value_error(len(self["pgc"]) == 32, "pgc must be 32 bytes")
            self.debug_type_error(
                isinstance(self["signature"], bytes), "signature must be a bytes object"
            )
            self.debug_value_error(len(self["signature"]) == 32, "signature must be 32 bytes")
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
        has_row_a = "Ad" in cgraph or "As" in cgraph
        has_row_b = "Bd" in cgraph or "Bs" in cgraph

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
