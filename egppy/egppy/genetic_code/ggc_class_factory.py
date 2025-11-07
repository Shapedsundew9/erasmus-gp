"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from egpcommon.common import ANONYMOUS_CREATOR, EGP_EPOCH, NULL_STR, NULL_TUPLE, sha256_signature
from egpcommon.common_obj import CommonObj
from egpcommon.deduplication import int_store, uuid_store
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.gp_db_config import GGC_KVT
from egpcommon.properties import BASIC_CODON_PROPERTIES
from egppy.genetic_code.egc_class_factory import EGCMixin
from egppy.genetic_code.genetic_code import GCABC, NULL_SIGNATURE
from egppy.genetic_code.import_def import ImportDef
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# pylint: disable=abstract-method
class GGCMixin(EGCMixin):
    """General Genetic Code Mixin Class."""

    GC_KEY_TYPES: dict[str, dict[str, Any]] = GGC_KVT

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert isinstance(self, CommonObj), "GGC must be a CommonObj."
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
                self["gca"] is NULL_SIGNATURE,
                "A code depth of 1 is a codon or empty GC and must have a NULL GCA.",
            )

        if self["code_depth"] > 1:
            self.runtime_error(
                self["gca"] is not NULL_SIGNATURE,
                "A code depth greater than 1 must have a non-NULL GCA.",
            )

        self.runtime_error(
            self["created"] <= self["updated"], "created time must be less than updated time."
        )

        if self["generation"] == 1:
            self.runtime_error(
                self["gca"] is NULL_SIGNATURE,
                "A generation of 1 is a codon and can only have a NULL GCA.",
            )

        if len(self["inputs"]) == 0:
            self.runtime_error(len(self["input_types"]) == 0, "No inputs must have no input types.")

        self.runtime_error(
            len(self["input_types"]) <= len(self["inputs"]),
            "The number of input types must be less than or equal to the number of inputs.",
        )
        self.runtime_error(
            self["lost_descendants"] <= self["reference_count"],
            "lost_descendants must be less than or equal to reference_count.",
        )
        self.runtime_error(
            self["num_codes"] >= self["code_depth"],
            "num_codes must be greater than or equal to code_depth.",
        )

        if len(self["outputs"]) == 0:
            self.runtime_error(
                len(self["output_types"]) == 0, "No outputs must have no output types."
            )

        if len(self["output_types"]) > 0:
            self.runtime_error(
                len(self["output_types"]) <= len(self["outputs"]),
                "The number of output types must be less than or equal to the number of outputs.",
            )

        self.runtime_error(
            self["updated"] <= datetime.now(UTC),
            "updated time must be less than or equal to the current time.",
        )

        # Call base class consistency at the end
        super().consistency()

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

        # TODO: Freeze the cgraph if it is not already frozen.
        # self["cgraph"].freeze()

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
        # TODO: creator can be a reference into an object set as there will be many duplicates
        creator = gcabc.get("creator", ANONYMOUS_CREATOR)
        creator = UUID(creator) if isinstance(creator, str) else creator
        self["creator"] = uuid_store[creator]
        self["descendants"] = int_store[gcabc.get("descendants", 0)]
        self["imports"] = gcabc.get("imports", NULL_TUPLE)
        self["inline"] = gcabc.get("inline", NULL_STR)
        self["code"] = gcabc.get("code", NULL_STR)

        # TODO: What do we need these for internally. Need to write them to the DB
        # but internally we can use the graph interface e.g. self["graph"]["I"]
        self["input_types"], self["inputs"] = self["cgraph"]["Is"].types()
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
        self["output_types"], self["outputs"] = self["cgraph"]["Od"].types()

        self["reference_count"] = int_store[gcabc.get("reference_count", 0)]
        tmp = gcabc.get("updated", datetime.now(UTC))
        self["updated"] = (
            # If the datetime exists it is from the database and has no timezone info.
            tmp.replace(tzinfo=UTC)
            if isinstance(tmp, datetime)
            else datetime.fromisoformat(tmp)
        )

        if self["signature"] is None or self["signature"] == NULL_SIGNATURE:
            self["signature"] = sha256_signature(
                self["ancestora"],
                self["ancestorb"],
                self["gca"],
                self["gcb"],
                self["cgraph"].to_json(),
                self["pgc"],
                self["imports"],
                self["inline"],
                self["code"],
                int(self["created"].timestamp()),
                self["creator"].bytes,
            )
        if _logger.isEnabledFor(DEBUG):
            self.verify()

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

        # The set of types of the inputs in ascending order of type number.
        itypes = self["input_types"]
        self.value_error(
            len(itypes) <= 256, "input_types must have a length less than or equal to 256."
        )
        self.value_error(len(set(itypes)) == len(itypes), "input_types must be unique.")
        self.value_error(
            all(itypes[i] < itypes[i + 1] for i in range(len(itypes) - 1)),
            "input_types must be in ascending order.",
        )

        # The index of the each input parameters type in the 'input_types' list in the order they
        # are required for the function call.
        self.value_error(
            len(self["inputs"]) <= 256, "inputs must have a length less than or equal to 256."
        )
        self.value_error(all(x < 256 for x in self["inputs"]), "inputs indexes must be < 256.")

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

        # The set of types of the outputs in ascending order of type number.
        otypes = self["output_types"]
        self.value_error(
            len(otypes) <= 256, "output_types must have a length less than or equal to 256."
        )
        self.value_error(len(set(otypes)) == len(otypes), "output_types must be unique.")
        self.value_error(
            all(otypes[i] < otypes[i + 1] for i in range(len(otypes) - 1)),
            "output_types must be in ascending order.",
        )

        # The index of the each output parameters type in the 'output_types' list in the order they
        # are returned from the function call.
        self.value_error(
            len(self["outputs"]) <= 256, "outputs must have a length less than or equal to 256."
        )
        self.value_error(all(x < 256 for x in self["outputs"]), "outputs indexes must be < 256.")

        # The properties of the genetic code.
        self.value_error(isinstance(self["properties"], int), "properties must be an integer.")
        self.value_error(
            self["properties"] >= -(2**63), "properties must be greater than or equal to -2**63."
        )
        self.value_error(
            self["properties"] <= 2**63 - 1, "properties must be less than or equal to 2**63-1."
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

        # Call base class verify at the end
        super().verify()


class GGCDict(GGCMixin, CacheableDict, GCABC):  # type: ignore
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DirtyDictGGC"""
        super().__init__()
        # CacheableDict.__init__(self)
        self.set_members(gcabc if gcabc is not None else {})

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)
        GGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)
        GGCMixin.verify(self)


# XGC is an execution genetic code object. It is a read-only GGC object.
# This can be more robustly implemented.
class XGCType(GGCDict):
    """Execution Genetic Code Class."""


# The NULL GC is a placeholder for a genetic code object that does not exist.
NULL_GC: GCABC = GGCDict(
    {
        "cgraph": {"A": [["I", 0, "EGPInvalid"]], "O": [["A", 0, "EGPInvalid"]], "U": []},
        "code_depth": 1,
        "generation": 0,
        "num_codes": 1,
        "num_codons": 1,
        "properties": BASIC_CODON_PROPERTIES,
    }
)
