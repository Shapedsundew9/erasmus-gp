"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""

from datetime import UTC, datetime
from typing import Any

from egpcommon.common import (
    EGP_EPOCH,
    NULL_STR,
    NULL_TUPLE,
    SHAPEDSUNDEW9_UUID,
    debug_exceptions,
    sha256_signature,
)
from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import int_store, signature_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import GGC_KVT
from egpcommon.properties import BASIC_CODON_PROPERTIES, CGraphType, GCType, PropertiesBD
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.frozen_c_graph import FrozenCGraph, frozen_cgraph_store
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.gpg_view import GPGCView
from egppy.genetic_code.import_def import ImportDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# TODO: Once stable this should become a slotted class for performance.
class GGCDict(EGCDict):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    GC_KEY_TYPES: dict[str, dict[str, Any]] = GGC_KVT

    def __eq__(self, other: object) -> bool:
        """Equality operator for GGCDict.
        Uses the signature for fast comparison.
        Args:
            other: The other GGCDict to compare to.
        Returns:
            True if the GGCDicts are equal, False otherwise.
        """
        if not isinstance(other, GGCDict):
            return False
        return self["signature"] is other["signature"]

    def __hash__(self) -> int:
        """Hash function for GGCDict.
        Uses the signature for hashing.
        Returns:
            The hash of the GGCDict signature (int)
        """
        return hash(self["signature"])

    def as_gpc_view(self) -> GPGCView:
        """Return a GPGCView of the GGCDict."""
        return GPGCView(self)

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> GCABC:
        """Set the attributes of the GGC.

        Note that no type checking of signatures is performed.
        This allows the opportunity to resolve references to other genetic code objects
        after the genetic code object has been created.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        super().set_members(gcabc)
        if not isinstance(self, GCABC):
            raise ValueError("GGC must be a GCABC object.")

        if not type(self["cgraph"]) is FrozenCGraph:  # pylint: disable=unidiomatic-typecheck
            self["cgraph"] = frozen_cgraph_store[FrozenCGraph(self["cgraph"])]
        else:
            # Make sure it is deduplicated
            self["cgraph"] = frozen_cgraph_store[self["cgraph"]]

        if isinstance(self["gca"], GCABC):
            # TODO: If GCA is an EGCDict we need to resolve it to a GGCDict
            # That requires walking the tree of genetic codes as GCA may itself
            # depend on EGCDict objects. That needs to be implemented as a separate
            # method (using a stack). It is a fundamental assumption that all
            # EGCDicts are stable and can be resolved to GGCDicts.
            self["gca"] = self["gca"]["signature"]
        if isinstance(self["gcb"], GCABC):
            # TODO: If GCB is an EGCDict we need to resolve it to a GGCDict (see GCA)
            self["gcb"] = self["gcb"]["signature"]
        if isinstance(self["ancestora"], GCABC):
            # TODO: If Ancestor A is an EGCDict we need to resolve it to a GGCDict (see GCA)
            self["ancestora"] = self["ancestora"]["signature"]
        if isinstance(self["ancestorb"], GCABC):
            # TODO: If Ancestor B is an EGCDict we need to resolve it to a GGCDict (see GCA)
            self["ancestorb"] = self["ancestorb"]["signature"]
        if isinstance(self["pgc"], GCABC):
            # TODO: If PGC is an EGCDict we need to resolve it to a GGCDict (see GCA)
            self["pgc"] = self["pgc"]["signature"]

        self["code_depth"] = int_store[gcabc["code_depth"]]
        self["generation"] = int_store[gcabc["generation"]]
        self["num_codes"] = int_store[gcabc["num_codes"]]
        self["num_codons"] = int_store[gcabc["num_codons"]]
        self["_lost_descendants"] = int_store[gcabc.get("_lost_descendants", 0)]
        self["_reference_count"] = int_store[gcabc.get("_reference_count", 0)]
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = (
            # If the datetime exists it is from the database and has no timezone info.
            tmp.replace(tzinfo=UTC)
            if isinstance(tmp, datetime)
            else datetime.fromisoformat(tmp)
        )
        self["descendants"] = int_store[gcabc.get("descendants", 0)]
        self["imports"] = gcabc.get("imports", NULL_TUPLE)
        self["inline"] = gcabc.get("inline", NULL_STR)
        self["code"] = gcabc.get("code", NULL_STR)
        self["num_inputs"] = int_store[len(self["cgraph"][SrcIfKey.IS])]
        self["num_outputs"] = int_store[len(self["cgraph"][DstIfKey.OD])]

        # TODO: These are derived properties from self["cgraph"]["SrcIfKey.IS"].
        # self["cgraph"] is the source of truth.
        # self["input_types"], self["inputs"] = self["cgraph"]["Is"].types_and_indices()
        self["lost_descendants"] = int_store[gcabc.get("lost_descendants", 0)]

        # TODO: Need to resolve the meta_data references. Too deep.
        # Need to pull relevant data in and then destroy the meta data dictionary.
        meta_data = gcabc.get("meta_data", {})
        if meta_data:
            self["inline"] = meta_data["inline"]
            self["code"] = meta_data.get("code", NULL_STR)
            self["io_map"] = meta_data["io_map"] if "io_map" in meta_data else {}
            self["name"] = meta_data.get("name", NULL_STR)
            self["description"] = meta_data.get("description", NULL_STR)
            if "imports" in meta_data:
                self["imports"] = tuple(ImportDef(**md).freeze() for md in meta_data["imports"])

        # TODO: What do we need these for internally. Need to write them to the DB
        # but internally we can use the graph interface e.g. self["cgraph"]["O"]
        # self["output_types"], self["outputs"] = self["cgraph"]["Od"].types_and_indices()

        self["reference_count"] = int_store[gcabc.get("reference_count", 0)]

        if self.get("signature") is None:
            self["signature"] = signature_store[
                sha256_signature(
                    self["ancestora"],
                    self["ancestorb"],
                    self["gca"],
                    self["gcb"],
                    self["cgraph"].to_json(True),
                    self["pgc"],
                    self["imports"],
                    self["inline"],
                    self["code"],
                    int(self["created"].timestamp()),
                    self["creator"].bytes,
                )
            ]

        # If this is an EGCDict being converted to a GGCDict then
        # we need to replace references with this object.
        if isinstance(gcabc, EGCDict):
            for (_, field), egc in gcabc["references"].items():
                # Sanity checks
                assert isinstance(egc, EGCDict), "Referenced GC must be an EGCDict"
                assert field in egc, "Referenced field must exist in the EGCDict"
                assert egc[field] is gcabc, "Referenced field must be gcabc"
                egc[field] = self

        if _logger.isEnabledFor(DEBUG):
            self.verify()
        return self

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        return GPGCView(self).to_json()

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self, CommonObj), "GGC must be a CommonObj."

        # The number of descendants when the genetic code was copied from the higher layer.
        if not (self["_lost_descendants"] >= 0):
            raise ValueError("_lost_descendants must be greater than or equal to zero.")
        if not (self["_lost_descendants"] <= 2**63 - 1):
            raise ValueError("_lost_descendants must be less than or equal to 2**63-1.")

        # The reference count when the genetic code was copied from the higher layer.
        if not (self["_reference_count"] >= 0):
            raise ValueError("_reference_count must be greater than or equal to zero.")
        if not (self["_reference_count"] <= 2**63 - 1):
            raise ValueError("_reference_count must be less than or equal to 2**63-1.")

        # The depth of the genetic code in genetic codes. If this is a codon then the depth is 1.
        if not (self["code_depth"] >= 1):
            raise ValueError("code_depth must be greater than or equal to one.")
        if not (self["code_depth"] <= 2**31 - 1):
            raise ValueError("code_depth must be less than or equal to 2**31-1.")

        # The date and time the genetic code was created. Created time zone must be UTC.
        if not (self["created"] <= datetime.now(UTC)):
            raise ValueError("created must be less than or equal to the current date and time.")
        if not (self["created"] >= EGP_EPOCH):
            raise ValueError("Created must be greater than or equal to EGP_EPOCH.")
        if not (self["created"].tzinfo == UTC):
            raise ValueError("Created must be in the UTC time zone.")

        # The number of generations of genetic code evolved to create this code. A codon is always
        # generation 1.
        if not (self["generation"] >= 0):
            raise ValueError("generation must be greater than or equal to zero.")
        if not (self["generation"] <= 2**63 - 1):
            raise ValueError("generation must be less than or equal to 2**63-1.")

        # The number of descendants.
        if not (self["descendants"] >= 0):
            raise ValueError("Descendants must be greater than or equal to 0.")
        if not (self["descendants"] <= 2**31 - 1):
            raise ValueError("Descendants must be less than 2**31-1.")

        # The number of descendants that have been lost in the evolution of the genetic code.
        if not (self["lost_descendants"] >= 0):
            raise ValueError("lost_descendants must be greater than or equal to zero.")
        if not (self["lost_descendants"] <= 2**63 - 1):
            raise ValueError("lost_descendants must be less than or equal to 2**63-1.")

        # The meta data associated with the genetic code.
        # No verification is performed on the meta data.

        # The number of vertices in the GC code vertex graph.
        if not (self["num_codes"] >= 1):
            raise ValueError("num_codes must be greater than or equal to one.")
        if not (self["num_codes"] <= 2**31 - 1):
            raise ValueError("num_codes must be less than or equal to 2**31-1.")

        # The number of codons in the GC code codon graph.
        if not (self["num_codons"] >= 0):
            raise ValueError("num_codons must be greater than or equal to one.")
        if not (self["num_codons"] <= 2**31 - 1):
            raise ValueError("num_codons must be less than or equal to 2**31-1.")

        # The properties of the genetic code.
        if not isinstance(self["properties"], int):
            raise ValueError("properties must be an integer.")
        properties = PropertiesBD(self["properties"])
        if not properties.valid():
            raise ValueError("properties must be valid.")
        if not properties.verify():
            raise ValueError("properties must verify.")

        # Are the properties consistent with the genetic code?
        graph_type = self["cgraph"].graph_type()
        gc_type = properties["gc_type"]
        if not (properties["graph_type"] == graph_type):
            raise ValueError("The cgraph and properties graph types must be consistent.")

        # Is the GC type consistent with the graph type?
        if gc_type == GCType.CODON:
            if not (graph_type == CGraphType.PRIMITIVE):
                raise ValueError("If the genetic code is a codon, the code_depth must be 1.")

        # The reference count of the genetic code.
        if not (self["reference_count"] >= 0):
            raise ValueError("reference_count must be greater than or equal to zero.")
        if not (self["reference_count"] <= 2**63 - 1):
            raise ValueError("reference_count must be less than or equal to 2**63-1.")

        if not (self["_lost_descendants"] <= self["lost_descendants"]):
            raise RuntimeError("_lost_descendants must be less than or equal to lost_descendants.")
        if not (self["_reference_count"] <= self["reference_count"]):
            raise RuntimeError("_reference_count must be less than or equal to reference_count.")

        if not (self["code_depth"] >= 0):
            raise RuntimeError("code_depth must be greater than or equal to zero.")
        if self["code_depth"] == 1:
            if not (self["gca"] is None):
                raise RuntimeError(
                    "A code depth of 1 is a codon or empty GC and must have a None GCA."
                )

        if self["code_depth"] > 1:
            if not (self["gca"] is not None):
                raise RuntimeError("A code depth greater than 1 must have a non-None GCA.")

        if self["generation"] == 1:
            if not (self["gca"] is None):
                raise RuntimeError("A generation of 1 is a codon and can only have a None GCA.")

        if not (self["lost_descendants"] <= self["reference_count"]):
            raise RuntimeError("lost_descendants must be less than or equal to reference_count.")
        if not (self["num_codes"] >= self["code_depth"]):
            raise RuntimeError("num_codes must be greater than or equal to code_depth.")

        if not isinstance(self["signature"], bytes):
            raise debug_exceptions.DebugTypeError("signature must be a bytes object")
        if not (len(self["signature"]) == 32):
            raise debug_exceptions.DebugValueError("signature must be 32 bytes")

        # Call base class verify at the end
        super().verify()


# The NULL GC is a placeholder for a genetic code object that does not exist.
NULL_GC: GCABC = GGCDict(
    {
        "cgraph": {"A": [["I", 0, "EGPInvalid"]], "O": [["A", 0, "EGPInvalid"]], "U": []},
        "code_depth": 1,
        "generation": 0,
        "num_codes": 1,
        "num_codons": 1,
        "properties": BASIC_CODON_PROPERTIES,
        "creator": SHAPEDSUNDEW9_UUID,
        "created": EGP_EPOCH,
        "ancestora": None,
        "ancestorb": None,
        "gca": None,
        "gcb": None,
        "pgc": None,
    }
)
