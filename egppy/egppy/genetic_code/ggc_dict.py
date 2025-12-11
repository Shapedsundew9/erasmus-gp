"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""

from copy import deepcopy
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from egpcommon.common import EGP_EPOCH, NULL_STR, NULL_TUPLE, SHAPEDSUNDEW9_UUID, sha256_signature
from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import int_store, signature_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import GGC_KVT
from egpcommon.properties import BASIC_CODON_PROPERTIES, CGraphType, GCType, PropertiesBD
from egppy.genetic_code.c_graph_abc import FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.frozen_c_graph import FrozenCGraph, frozen_cgraph_store
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.import_def import ImportDef
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class GGCDict(EGCDict):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    GC_KEY_TYPES: dict[str, dict[str, Any]] = GGC_KVT

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
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

        # TODO: What do we need these for internally. Need to write them to the DB
        # but internally we can use the graph interface e.g. self["graph"]["I"]
        self["input_types"], self["inputs"] = self["cgraph"]["Is"].types_and_indices()
        self["lost_descendants"] = int_store[gcabc.get("lost_descendants", 0)]

        # TODO: Need to resolve the meta_data references. Too deep.
        # Need to pull relevant data in and then destroy the meta data dictionary.
        self["meta_data"] = gcabc.get("meta_data", {})
        if (
            "function" in self["meta_data"]
            and "python3" in self["meta_data"]["function"]
            and "0" in self["meta_data"]["function"]["python3"]
        ):
            base = self["meta_data"]["function"]["python3"]["0"]
            self["inline"] = base["inline"]
            self["code"] = base.get("code", NULL_STR)
            if "imports" in base:
                self["imports"] = tuple(ImportDef(**md).freeze() for md in base["imports"])

        # TODO: What do we need these for internally. Need to write them to the DB
        # but internally we can use the graph interface e.g. self["cgraph"]["O"]
        self["output_types"], self["outputs"] = self["cgraph"]["Od"].types_and_indices()

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

        tmp = gcabc.get("updated", datetime.now(UTC))
        self["updated"] = (
            # If the datetime exists it is from the database and has no timezone info.
            tmp.replace(tzinfo=UTC)
            if isinstance(tmp, datetime)
            else datetime.fromisoformat(tmp)
        )

        if _logger.isEnabledFor(DEBUG):
            self.verify()

    def to_json(self) -> dict[str, int | str | float | list | dict]:
        """Return a JSON serializable dictionary."""
        retval = {}
        assert isinstance(self, GCABC), "GC must be a GCABC object."
        # Only keys that are persisted in the DB are included in the JSON.
        for key in (k for k in self if self.GC_KEY_TYPES.get(k, {})):
            value = self[key]
            if key in {"input_types", "output_types", "inputs", "outputs"}:
                # These are derived from the cgraph so skip them in the JSON.
                continue
            elif key == "meta_data":
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
            elif isinstance(value, GCABC):
                # Must get signatures from GC objects first otherwise will recursively
                # call this function.
                retval[key] = value["signature"].hex() if value is not None else None
            elif isinstance(value, FrozenCGraphABC):
                # Need to set json_c_graph to True so that the endpoints are correctly serialized
                retval[key] = value.to_json(json_c_graph=True)
                typ, idx = value[SrcIfKey.IS].types_and_indices()
                retval["input_types"] = [types_def_store[t].name for t in typ]
                retval["inputs"] = idx.hex()
                typ, idx = value[DstIfKey.OD].types_and_indices()
                retval["output_types"] = [types_def_store[t].name for t in typ]
                retval["outputs"] = idx.hex()
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
        """Verify the genetic code object."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self, CommonObj), "GGC must be a CommonObj."

        # The number of descendants when the genetic code was copied from the higher layer.
        self.value_error(
            self["_lost_descendants"] >= 0,
            "_lost_descendants must be greater than or equal to zero.",
        )
        self.value_error(
            self["_lost_descendants"] <= 2**63 - 1,
            "_lost_descendants must be less than or equal to 2**63-1.",
        )

        # The reference count when the genetic code was copied from the higher layer.
        self.value_error(
            self["_reference_count"] >= 0,
            "_reference_count must be greater than or equal to zero.",
        )
        self.value_error(
            self["_reference_count"] <= 2**63 - 1,
            "_reference_count must be less than or equal to 2**63-1.",
        )

        # The depth of the genetic code in genetic codes. If this is a codon then the depth is 1.
        self.value_error(
            self["code_depth"] >= 1, "code_depth must be greater than or equal to one."
        )
        self.value_error(
            self["code_depth"] <= 2**31 - 1, "code_depth must be less than or equal to 2**31-1."
        )

        # The date and time the genetic code was created. Created time zone must be UTC.
        self.value_error(
            self["created"] <= datetime.now(UTC),
            "created must be less than or equal to the current date and time.",
        )
        self.value_error(
            self["created"] >= EGP_EPOCH, "Created must be greater than or equal to EGP_EPOCH."
        )
        self.value_error(self["created"].tzinfo == UTC, "Created must be in the UTC time zone.")

        # The number of generations of genetic code evolved to create this code. A codon is always
        # generation 1.
        self.value_error(
            self["generation"] >= 0, "generation must be greater than or equal to zero."
        )
        self.value_error(
            self["generation"] <= 2**63 - 1, "generation must be less than or equal to 2**63-1."
        )

        # The number of descendants.
        self.value_error(
            self["descendants"] >= 0, "Descendants must be greater than or equal to 0."
        )
        self.value_error(self["descendants"] <= 2**31 - 1, "Descendants must be less than 2**31-1.")

        # The number of descendants that have been lost in the evolution of the genetic code.
        self.value_error(
            self["lost_descendants"] >= 0,
            "lost_descendants must be greater than or equal to zero.",
        )
        self.value_error(
            self["lost_descendants"] <= 2**63 - 1,
            "lost_descendants must be less than or equal to 2**63-1.",
        )

        # The meta data associated with the genetic code.
        # No verification is performed on the meta data.

        # The number of vertices in the GC code vertex graph.
        self.value_error(self["num_codes"] >= 1, "num_codes must be greater than or equal to one.")
        self.value_error(
            self["num_codes"] <= 2**31 - 1, "num_codes must be less than or equal to 2**31-1."
        )

        # The number of codons in the GC code codon graph.
        self.value_error(
            self["num_codons"] >= 0, "num_codons must be greater than or equal to one."
        )
        self.value_error(
            self["num_codons"] <= 2**31 - 1, "num_codons must be less than or equal to 2**31-1."
        )

        # The properties of the genetic code.
        self.value_error(isinstance(self["properties"], int), "properties must be an integer.")
        properties = PropertiesBD(self["properties"])
        self.value_error(properties.valid(), "properties must be valid.")
        self.value_error(properties.verify(), "properties must verify.")

        # Are the properties consistent with the genetic code?
        graph_type = self["cgraph"].graph_type()
        gc_type = properties["gc_type"]
        self.value_error(
            properties["graph_type"] == graph_type,
            "The cgraph and properties graph types must be consistent.",
        )

        # Is the GC type consistent with the graph type?
        if gc_type == GCType.CODON:
            self.value_error(
                graph_type == CGraphType.PRIMITIVE,
                "If the genetic code is a codon, the code_depth must be 1.",
            )

        if gc_type == GCType.META or gc_type == GCType.ORDINARY_META:
            self.value_error(
                graph_type == CGraphType.STANDARD or graph_type == CGraphType.PRIMITIVE,
                "If the genetic code is meta, the graph must be STANDARD or PRIMITIVE.",
            )

        # The reference count of the genetic code.
        self.value_error(
            self["reference_count"] >= 0,
            "reference_count must be greater than or equal to zero.",
        )
        self.value_error(
            self["reference_count"] <= 2**63 - 1,
            "reference_count must be less than or equal to 2**63-1.",
        )

        # The date and time the genetic code was last updated.
        self.value_error(
            self["updated"] <= datetime.now(UTC),
            "Updated must be less than or equal to the current date and time.",
        )
        self.value_error(
            self["updated"] >= EGP_EPOCH, "Updated must be greater than or equal to EGP_EPOCH."
        )
        self.value_error(self["updated"].tzinfo == UTC, "Updated must be in the UTC time zone.")

        self.runtime_error(
            self["_lost_descendants"] <= self["lost_descendants"],
            "_lost_descendants must be less than or equal to lost_descendants.",
        )
        self.runtime_error(
            self["_reference_count"] <= self["reference_count"],
            "_reference_count must be less than or equal to reference_count.",
        )

        self.runtime_error(
            self["code_depth"] >= 0, "code_depth must be greater than or equal to zero."
        )
        if self["code_depth"] == 1:
            self.runtime_error(
                self["gca"] is None,
                "A code depth of 1 is a codon or empty GC and must have a None GCA.",
            )

        if self["code_depth"] > 1:
            self.runtime_error(
                self["gca"] is not None,
                "A code depth greater than 1 must have a non-None GCA.",
            )

        self.runtime_error(
            self["created"] <= self["updated"], "created time must be less than updated time."
        )

        if self["generation"] == 1:
            self.runtime_error(
                self["gca"] is None,
                "A generation of 1 is a codon and can only have a None GCA.",
            )

        self.runtime_error(
            self["lost_descendants"] <= self["reference_count"],
            "lost_descendants must be less than or equal to reference_count.",
        )
        self.runtime_error(
            self["num_codes"] >= self["code_depth"],
            "num_codes must be greater than or equal to code_depth.",
        )

        self.runtime_error(
            self["updated"] <= datetime.now(UTC),
            "updated time must be less than or equal to the current time.",
        )
        self.debug_type_error(
            isinstance(self["signature"], bytes), "signature must be a bytes object"
        )
        self.debug_value_error(len(self["signature"]) == 32, "signature must be 32 bytes")

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
