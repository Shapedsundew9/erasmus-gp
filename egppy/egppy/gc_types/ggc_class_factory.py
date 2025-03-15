"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""

from datetime import UTC, datetime
from math import isclose
from typing import Any

from egpcommon.common import EGP_EPOCH, GGC_KVT, NULL_STR, NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.properties import PropertiesBD

from egppy.gc_graph.end_point.import_def import ImportDef, import_def_store
from egppy.gc_types.egc_class_factory import EGCMixin
from egppy.gc_types.gc import GCABC, NULL_GC, NULL_PROBLEM, NULL_PROBLEM_SET, NULL_SIGNATURE
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# pylint: disable=abstract-method
class GGCMixin(EGCMixin):
    """General Genetic Code Mixin Class."""

    GC_KEY_TYPES: dict[str, dict[str, str | bool]] = GGC_KVT

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        super().consistency()
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        assert (
            self["e_count"] >= self["_e_count"]
        ), "Evolvability count must be greater than or equal to the higher layer count."
        assert (
            self["e_total"] >= self["_e_total"]
        ), "Evolvability total must be greater than or equal to the higher layer total."
        assert isclose(
            self["_evolvability"], self["_e_total"] / self["_e_count"]
        ), "Evolvability must be the total evolvability divided by the count."
        assert (
            self["f_count"] >= self["_f_count"]
        ), "Fitness count must be greater than or equal to the higher layer count."
        assert (
            self["f_total"] >= self["_f_total"]
        ), "Fitness total must be greater than or equal to the higher layer total."
        assert isclose(
            self["_fitness"], self["_f_total"] / self["_f_count"]
        ), "Fitness must be the total fitness divided by the count."
        assert (
            self["_lost_descendants"] <= self["lost_descendants"]
        ), "_lost_descendants must be less than or equal to lost_descendants."
        assert (
            self["_reference_count"] <= self["reference_count"]
        ), "_reference_count must be less than or equal to reference_count."

        assert self["code_depth"] >= 0, "code_depth must be greater than or equal to zero."
        if self["code_depth"] == 1:
            assert (
                self["gca"] is NULL_GC or self["gca"] is NULL_SIGNATURE
            ), "A code depth of 1 is a codon or empty GC and must have a NULL GCA."

        if self["code_depth"] > 1:
            assert (
                self["gca"] is not NULL_GC and self["gca"] is not NULL_SIGNATURE
            ), "A code depth greater than 1 must have a non-NULL GCA."

        assert self["created"] <= self["updated"], "created time must be less than updated time."

        if self["generation"] == 0:
            assert self is NULL_GC, "A generation of 0 can only be the NULL_GC."

        if self["generation"] == 1:
            assert (
                self["gca"] is NULL_GC or self["gca"] is NULL_SIGNATURE
            ), "A generation of 1 is a codon and can only have a NULL GCA."

        if len(self["inputs"]) == 0:
            assert len(self["input_types"]) == 0, "No inputs must have no input types."

        assert len(self["input_types"]) <= len(
            self["inputs"]
        ), "The number of input types must be less than or equal to the number of inputs."
        assert (
            self["lost_descendants"] <= self["reference_count"]
        ), "lost_descendants must be less than or equal to reference_count."
        assert (
            self["num_codes"] >= self["code_depth"]
        ), "num_codes must be greater than or equal to code_depth."

        if len(self["outputs"]) == 0:
            assert len(self["output_types"]) == 0, "No outputs must have no output types."

        if len(self["output_types"]) > 0:
            assert len(self["output_types"]) <= len(
                self["outputs"]
            ), "The number of output types must be less than or equal to the number of outputs."

        assert self["updated"] <= datetime.now(
            UTC
        ), "updated time must be less than or equal to the current time."

    def set_members(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the GGC.

        Note that no type checking of signatures is performed.
        This allows the opportunity to resolve references to other genetic code objects
        after the genetic code object has been created.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        super().set_members(gcabc)
        assert isinstance(self, GCABC), "GGC must be a GCABC object."
        gca: GCABC | bytes = self["gca"]
        gcb: GCABC | bytes = self["gcb"]
        unknown = isinstance(gca, bytes) or isinstance(gcb, bytes)

        # If one or both of the sub-GC's are unknown then some fields cannot be derived.
        if unknown:
            self["code_depth"] = gcabc["code_depth"]
            self["generation"] = gcabc["generation"]
            self["num_codes"] = gcabc["num_codes"]
            self["num_codons"] = gcabc["num_codons"]
        else:
            # Can derive some values from the sub-GC's.
            assert isinstance(gca, GCABC) and isinstance(gcb, GCABC), "GCA and GCB must be GCABC."
            self["code_depth"] = max(gca["code_depth"], gcb["code_depth"]) + 1
            self["generation"] = max(gca["generation"], gcb["generation"]) + 1
            self["num_codes"] = gca["num_codes"] + gcb["num_codes"] + 1
            self["num_codons"] = max(gca["num_codons"] + gcb["num_codons"], 1)

        # Other values do not depend on the sub-GC's being known.
        self["_e_count"] = gcabc.get("_e_count", 1)
        self["_e_total"] = gcabc.get("_e_total", 0.0)
        self["_evolvability"] = self["_e_total"] / self["_e_count"]
        self["_f_count"] = gcabc.get("_f_count", 1)
        self["_f_total"] = gcabc.get("_f_total", 0.0)
        self["_fitness"] = self["_f_total"] / self["_f_count"]
        self["_lost_descendants"] = gcabc.get("_lost_descendants", 0)
        self["_reference_count"] = gcabc.get("_reference_count", 0)
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = tmp if isinstance(tmp, datetime) else datetime.fromisoformat(tmp)
        self["descendants"] = gcabc.get("descendants", 0)
        self["e_count"] = gcabc.get("e_count", self["_e_count"])
        self["e_total"] = gcabc.get("e_total", self["_e_total"])
        self["evolvability"] = self["e_total"] / self["e_count"]
        self["f_count"] = gcabc.get("f_count", self["_f_count"])
        self["f_total"] = gcabc.get("f_total", self["_f_total"])
        self["fitness"] = self["f_total"] / self["f_count"]
        self["imports"] = NULL_TUPLE
        self["inline"] = NULL_STR
        self["input_types"], self["inputs"] = self["graph"].itypes()
        self["lost_descendants"] = gcabc.get("lost_descendants", 0)
        # TODO: Need to resolve the meta_data references. Too deep.
        # Need to pull relevant data in and then destroy the meta data dictionary.
        self["meta_data"] = gcabc.get("meta_data", {})
        if (
            "function" in self["meta_data"]
            and "python3" in self["meta_data"]["function"]
            and "0" in self["meta_data"]["function"]["python3"]
        ):
            base = self["meta_data"]["function"]["python3"]["0"]
            if "imports" in base and not isinstance(base["imports"], tuple):
                base["imports"] = self["imports"] = tuple(
                    import_def_store.add(ImportDef(**md)) for md in base["imports"]
                )
                self["inline"] = base["inline"]
        self["num_inputs"] = len(self["inputs"])
        self["num_outputs"] = 0  # To keep alphabetical ordering in keys.
        self["output_types"], self["outputs"] = self["graph"].otypes()
        self["num_outputs"] = len(self["outputs"])
        self["population_uid"] = gcabc.get("population_uid", 0)
        tmp = gcabc.get("problem") if gcabc.get("problem") is not None else NULL_PROBLEM
        assert not isinstance(tmp, (bytearray, memoryview)) and tmp is not None
        self["problem"] = tmp if isinstance(tmp, bytes) else bytes.fromhex(tmp)
        tmp = gcabc.get("problem_set") if gcabc.get("problem_set") is not None else NULL_PROBLEM_SET
        assert not isinstance(tmp, (bytearray, memoryview)) and tmp is not None
        self["problem_set"] = tmp if isinstance(tmp, bytes) else bytes.fromhex(tmp)
        props = gcabc.get("properties", 0)
        self["properties"] = props if isinstance(props, int) else PropertiesBD(props).to_int()
        self["reference_count"] = gcabc.get("reference_count", 0)
        assert (
            self["signature"] is NULL_SIGNATURE if self["signature"] == NULL_SIGNATURE else True
        ), "Signature must be NULL_SIGNATURE object if NULL."
        if self["signature"] is NULL_SIGNATURE:
            self["signature"] = self.signature()
        self["survivability"] = gcabc.get("survivability", 0.0)
        tmp = gcabc.get("updated", datetime.now(UTC))
        self["updated"] = tmp if isinstance(tmp, datetime) else datetime.fromisoformat(tmp)
        if _LOG_DEBUG:
            self.verify()

    def verify(self) -> None:
        """Verify the genetic code object."""
        super().verify()
        assert isinstance(self, GCABC), "GGC must be a GCABC object."

        # The evolvability update count when the genetic code was copied from the higher layer.
        assert self["_e_count"] >= 0, "Evolvability count must be greater than or equal to 0."
        assert self["_e_count"] <= 2**31 - 1, "Evolvability count must be less than 2**31-1."

        # The total evolvability when the genetic code was copied from the higher layer.
        assert self["_e_total"] >= 0.0, "Evolvability total must be greater than or equal to 0.0."
        assert self["_e_total"] <= 2**31 - 1, "Evolvability total must be less than 2**31-1."

        # The evolvability when the genetic code was copied from the higher layer.
        assert self["_evolvability"] >= 0.0, "Evolvability must be greater than or equal to 0.0."
        assert self["_evolvability"] <= 1.0, "Evolvability must be less than or equal to 1.0."

        # The fitness update count when the genetic code was copied from the higher layer.
        assert self["_f_count"] >= 0, "Fitness count must be greater than or equal to 0."
        assert self["_f_count"] <= 2**31 - 1, "Fitness count must be less than 2**31-1."

        # The total fitness when the genetic code was copied from the higher layer.
        assert self["_f_total"] >= 0.0, "Fitness total must be greater than or equal to 0.0."
        assert self["_f_total"] <= 2**31 - 1, "Fitness total must be less than 2**31-1."

        # The fitness when the genetic code was copied from the higher layer.
        assert self["_fitness"] >= 0.0, "Fitness must be greater than or equal to 0.0."
        assert self["_fitness"] <= 1.0, "Fitness must be less than or equal to 1.0."

        # The number of descendants when the genetic code was copied from the higher layer.
        assert (
            self["_lost_descendants"] >= 0
        ), "_lost_descendants must be greater than or equal to zero."
        assert (
            self["_lost_descendants"] <= 2**63 - 1
        ), "_lost_descendants must be less than or equal to 2**63-1."

        # The reference count when the genetic code was copied from the higher layer.
        assert (
            self["_reference_count"] >= 0
        ), "_reference_count must be greater than or equal to zero."
        assert (
            self["_reference_count"] <= 2**63 - 1
        ), "_reference_count must be less than or equal to 2**63-1."

        # The depth of the genetic code in genetic codes. If this is a codon then the depth is 1.
        assert self["code_depth"] >= 1, "code_depth must be greater than or equal to one."
        assert self["code_depth"] <= 2**31 - 1, "code_depth must be less than or equal to 2**31-1."

        # The date and time the genetic code was created. Created time zone must be UTC.
        assert self["created"] <= datetime.now(
            UTC
        ), "created must be less than or equal to the current date and time."
        assert self["created"] >= EGP_EPOCH, "Created must be greater than or equal to EGP_EPOCH."
        assert self["created"].tzinfo == UTC, "Created must be in the UTC time zone."

        # The number of generations of genetic code evolved to create this code. A codon is always
        # generation 1.
        assert self["generation"] >= 0, "generation must be greater than or equal to zero."
        assert self["generation"] <= 2**63 - 1, "generation must be less than or equal to 2**63-1."

        # The number of evolvability updates in this genetic codes life time.
        assert self["e_count"] >= 0, "Evolvability count must be greater than or equal to 0."
        assert self["e_count"] <= 2**31 - 1, "Evolvability count must be less than 2**31-1."

        # The total evolvability in this genetic codes life time.
        assert self["e_total"] >= 0.0, "Evolvability total must be greater than or equal to 0.0."
        assert self["e_total"] <= 2**31 - 1, "Evolvability total must be less than 2**31-1."

        # The number of descendants.
        assert self["descendants"] >= 0, "Descendants must be greater than or equal to 0."
        assert self["descendants"] <= 2**31 - 1, "Descendants must be less than 2**31-1."

        # The current evolvability.
        assert self["evolvability"] >= 0.0, "Evolvability must be greater than or equal to 0.0."
        assert self["evolvability"] <= 1.0, "Evolvability must be less than or equal to 1.0."

        # The number of fitness updates in this genetic codes life time.
        assert self["f_count"] >= 0, "Fitness count must be greater than or equal to 0."
        assert self["f_count"] <= 2**31 - 1, "Fitness count must be less than 2**31-1."

        # The total fitness in this genetic codes life time.
        assert self["f_total"] >= 0.0, "Fitness total must be greater than or equal to 0.0."
        assert self["f_total"] <= 2**31 - 1, "Fitness total must be less than 2**31-1."

        # The current fitness.
        assert self["fitness"] >= 0.0, "Fitness must be greater than or equal to 0.0."
        assert self["fitness"] <= 1.0, "Fitness must be less than or equal to 1.0."

        # The set of types of the inputs in ascending order of type number.
        assert (
            len(itypes := self["input_types"]) <= 256
        ), "input_types must have a length less than or equal to 256."
        assert len(set(itypes)) == len(itypes), "input_types must be unique."
        assert all(
            itypes[i] < itypes[i + 1] for i in range(len(itypes) - 1)
        ), "input_types must be in ascending order."

        # The index of the each input parameters type in the 'input_types' list in the order they
        # are required for the function call.
        assert len(self["inputs"]) <= 256, "inputs must have a length less than or equal to 256."
        assert all(x < 256 for x in self["inputs"]), "inputs indexes must be < 256."

        # The number of descendants that have been lost in the evolution of the genetic code.
        assert (
            self["lost_descendants"] >= 0
        ), "lost_descendants must be greater than or equal to zero."
        assert (
            self["lost_descendants"] <= 2**63 - 1
        ), "lost_descendants must be less than or equal to 2**63-1."

        # The meta data associated with the genetic code.
        # No verification is performed on the meta data.

        # The number of vertices in the GC code vertex graph.
        assert self["num_codes"] >= 1, "num_codes must be greater than or equal to one."
        assert self["num_codes"] <= 2**31 - 1, "num_codes must be less than or equal to 2**31-1."

        # The number of codons in the GC code codon graph.
        assert self["num_codons"] >= 0, "num_codons must be greater than or equal to one."
        assert self["num_codons"] <= 2**31 - 1, "num_codons must be less than or equal to 2**31-1."

        # The number of input parameters required by the genetic code (function).
        assert self["num_inputs"] >= 0, "num_inputs must be greater than or equal to zero."
        assert self["num_inputs"] <= 256, "num_inputs must be less than or equal to 256."

        # The number of output parameters returned by the genetic code (function).
        assert self["num_outputs"] >= 0, "num_outputs must be greater than or equal to zero."
        assert self["num_outputs"] <= 256, "num_outputs must be less than or equal to 256."

        # The set of types of the outputs in ascending order of type number.
        assert (
            len(otypes := self["output_types"]) <= 256
        ), "output_types must have a length less than or equal to 256."
        assert len(set(otypes)) == len(otypes), "output_types must be unique."
        assert all(
            otypes[i] < otypes[i + 1] for i in range(len(otypes) - 1)
        ), "output_types must be in ascending order."

        # The index of the each output parameters type in the 'output_types' list in the order they
        # are returned from the function call.
        assert len(self["outputs"]) <= 256, "outputs must have a length less than or equal to 256."
        assert all(x < 256 for x in self["outputs"]), "outputs indexes must be < 256."

        # The population UID.
        assert self["population_uid"] >= 0, "Population UID must be greater than or equal to 0."
        assert self["population_uid"] <= 2**16 - 1, "Population UID must be less than 2**16-1."

        # The problem the genetic code solves.
        assert isinstance(self["problem"], bytes), "problem must be a bytes object."
        assert len(self["problem"]) == 32, "problem must be 32 bytes long."

        # The problem set the genetic code belongs to.
        assert isinstance(self["problem_set"], bytes), "problem_set must be a bytes object."
        assert len(self["problem_set"]) == 32, "problem_set must be 32 bytes long."

        # The properties of the genetic code.
        assert isinstance(self["properties"], int), "properties must be an integer."
        assert self["properties"] >= -(2**63), "properties must be greater than or equal to -2**63."
        assert self["properties"] <= 2**63 - 1, "properties must be less than or equal to 2**63-1."
        assert PropertiesBD(self["properties"]).verify(), "properties failed verification."

        # The reference count of the genetic code.
        assert (
            self["reference_count"] >= 0
        ), "reference_count must be greater than or equal to zero."
        assert (
            self["reference_count"] <= 2**63 - 1
        ), "reference_count must be less than or equal to 2**63-1."

        # The survivability.
        assert self["survivability"] >= 0.0, "Survivability must be greater than or equal to 0.0."
        assert self["survivability"] <= 1.0, "Survivability must be less than or equal to 1.0."

        # The date and time the genetic code was last updated.
        assert self["updated"] <= datetime.now(
            UTC
        ), "Updated must be less than or equal to the current date and time."
        assert self["updated"] >= EGP_EPOCH, "Updated must be greater than or equal to EGP_EPOCH."
        assert self["updated"].tzinfo == UTC, "Updated must be in the UTC time zone."


class GGCDirtyDict(GGCMixin, CacheableDirtyDict, GCABC):  # type: ignore
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any] | None = None) -> None:
        """Constructor for DirtyDictGGC"""
        super().__init__()
        CacheableDirtyDict.__init__(self)
        self.set_members(gcabc if gcabc is not None else {})

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDirtyDict.consistency(self)
        GGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDirtyDict.verify(self)
        GGCMixin.verify(self)


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


GGCType = GGCDirtyDict | GGCDict


# XGC is an execution genetic code object. It is a read-only GGC object.
# This can be more robustly implemented.
class XGCType(GGCDict):
    """Execution Genetic Code Class."""
