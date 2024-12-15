"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""

from datetime import UTC, datetime
from math import isclose
from typing import Any

from egpcommon.common import EGP_EPOCH, GGC_KVT, PROPERTIES
from egpcommon.conversions import encode_properties
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.egc_class_factory import EGCMixin
from egppy.gc_types.gc import GCABC, NULL_GC, NULL_PROBLEM, NULL_PROBLEM_SET
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
        assert (
            self["_e_total"] >= self["_e_count"]
        ), "Evolvability total must be greater than or equal to the evolvability count."
        assert isclose(
            self["_evolvability"], self["_e_total"] / self["_e_count"]
        ), "Evolvability must be the total evolvability divided by the count."
        assert (
            self["f_count"] >= self["_f_count"]
        ), "Fitness count must be greater than or equal to the higher layer count."
        assert (
            self["f_total"] >= self["_f_total"]
        ), "Fitness total must be greater than or equal to the higher layer total."
        assert (
            self["_f_total"] >= self["_f_count"]
        ), "Fitness total must be greater than or equal to the fitness count."
        assert isclose(
            self["_fitness"], self["_f_total"] / self["_f_count"]
        ), "Fitness must be the total fitness divided by the count."
        assert (
            self["_lost_descendants"] <= self["lost_descendants"]
        ), "_lost_descendants must be less than or equal to lost_descendants."
        assert (
            self["_reference_count"] <= self["reference_count"]
        ), "_reference_count must be less than or equal to reference_count."
        assert (
            self["code_depth"] == 1 and self["gca"] is NULL_GC
        ), "A code depth of 1 is a codon or empty GC and must have a NULL GCA."
        assert (
            self["code_depth"] > 1 and self["gca"] is not NULL_GC
        ), "A code depth greater than 1 must have a non-NULL GCA."
        assert (
            self["codon_depth"] == 0 and self["gca"] is NULL_GC
        ), "A codon depth of 0 is an empty GC must have a NULL GCA."
        assert (
            self["codon_depth"] == 1 and self["gca"] is NULL_GC
        ), "A codon depth of 1 is a codon and  must have a NULL GCA."
        assert (
            self["codon_depth"] > 1 and self["gca"] is not NULL_GC
        ), "A codon depth greater than 1 must have a non-NULL GCA."
        assert self["created"] <= self["updated"], "created time must be less than updated time."
        assert (
            self["generation"] == 0 and self["gca"] is NULL_GC
        ), "A generation of 0 is a codon or empty GC and must have a NULL GCA."
        assert (
            self["generation"] > 0 and self["gca"] is not NULL_GC
        ), "A generation greater than 0 must have a non-NULL GCA."
        assert (not self["input_types"]) == (
            not self["inputs"]
        ), "input_types and inputs both be 0 length or both be > 0 length."
        assert len(self["inputs"]) <= len(
            self["input_types"]
        ), "The number of inputs must be less than or equal to the number of input_types."
        assert (
            self["lost_descendants"] <= self["reference_count"]
        ), "lost_descendants must be less than or equal to reference_count."
        assert (
            self["num_codes"] >= self["code_depth"]
        ), "num_codes must be greater than or equal to code_depth."
        assert (
            self["num_codons"] >= self["codon_depth"]
        ), "num_codons must be greater than or equal to codon_depth."
        assert (not self["output_types"]) == (
            not self["outputs"]
        ), "output_types and outputs both be 0 length or both be > 0 length."
        assert len(self["outputs"]) <= len(
            self["output_types"]
        ), "The number of outputs must be less than or equal to the number of output_types."
        assert (
            self["updated"] <= datetime.now()
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
        self["_e_count"] = gcabc.get("_e_count", 1)
        self["_e_total"] = gcabc.get("_e_total", 0.0)
        self["_evolvability"] = self["_e_total"] / self["_e_count"]
        self["_f_count"] = gcabc.get("_f_count", 1)
        self["_f_total"] = gcabc.get("_f_total", 0.0)
        self["_fitness"] = self["_f_total"] / self["_f_count"]
        self["_lost_descendants"] = gcabc.get("_lost_descendants", 0)
        self["_reference_count"] = gcabc.get("_reference_count", 0)
        self["code_depth"] = gcabc.get("code_depth", 1)
        self["codon_depth"] = gcabc.get("codon_depth", 1)
        tmp = gcabc.get("created", datetime.now(UTC))
        self["created"] = tmp if isinstance(tmp, datetime) else datetime.fromisoformat(tmp)
        self["descendants"] = gcabc.get("descendants", 0)
        self["e_count"] = gcabc.get("e_count", self["_e_count"])
        self["e_total"] = gcabc.get("e_total", self["_e_total"])
        self["evolvability"] = self["e_total"] / self["e_count"]
        self["f_count"] = gcabc.get("f_count", self["_f_count"])
        self["f_total"] = gcabc.get("f_total", self["_f_total"])
        self["fitness"] = self["f_total"] / self["f_count"]
        self["generation"] = gcabc.get("generation", 0)
        self["input_types"], self["inputs"] = self["graph"].itypes()
        self["lost_descendants"] = gcabc.get("lost_descendants", 0)
        self["meta_data"] = gcabc.get("meta_data", {})
        self["num_codes"] = gcabc.get("num_codes", 1)
        self["num_codons"] = gcabc.get("num_codons", 1)
        self["num_inputs"] = len(self["inputs"])
        self["num_outputs"] = 0  # To keep alaphabetical ordering in keys.
        self["output_types"], self["outputs"] = self["graph"].otypes()
        self["num_outputs"] = len(self["outputs"])
        self["population_uid"] = gcabc.get("population_uid", 0)
        tmp = gcabc.get("problem") if gcabc.get("problem") is not None else NULL_PROBLEM
        assert not isinstance(tmp, (bytearray, memoryview)) and tmp is not None
        self["problem"] = tmp if isinstance(tmp, bytes) else bytes.fromhex(tmp)
        tmp = gcabc.get("problem_set") if gcabc.get("problem_set") is not None else NULL_PROBLEM_SET
        assert not isinstance(tmp, (bytearray, memoryview)) and tmp is not None
        self["problem_set"] = tmp if isinstance(tmp, bytes) else bytes.fromhex(tmp)
        tmp = gcabc.get("properties", 0)
        self["properties"] = tmp if isinstance(tmp, int) else encode_properties(tmp)
        self["reference_count"] = gcabc.get("reference_count", 0)
        self["survivability"] = gcabc.get("survivability", 0.0)
        tmp = gcabc.get("updated", datetime.now(UTC))
        self["updated"] = tmp if isinstance(tmp, datetime) else datetime.fromisoformat(tmp)

        # Some sanity that GCABC was consistent for derived values. _LOG_DEBUG because this is fast.
        if _LOG_DEBUG:
            assert self["input_types"] == gcabc.get(
                "input_types", self["input_types"]
            ), "input_types must be the input types."
            assert self["inputs"] == gcabc.get(
                "inputs", self["inputs"]
            ), "inputs must be the input indexes."
            assert self["num_inputs"] == gcabc.get(
                "num_inputs", self["num_inputs"]
            ), "num_inputs must be the number of inputs."
            assert self["output_types"] == gcabc.get(
                "output_types", self["output_types"]
            ), "output_types must be the output types."
            assert self["outputs"] == gcabc.get(
                "outputs", self["outputs"]
            ), "outputs must be the output indexes."
            assert self["num_outputs"] == gcabc.get(
                "num_outputs", self["num_outputs"]
            ), "num_outputs must be the number of outputs."

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
        assert self["properties"] >= -(2**63), "properties must be greater than or equal to -2**63."
        assert self["properties"] <= 2**63 - 1, "properties must be less than or equal to 2**63-1."
        assert not (
            ~sum(PROPERTIES.values()) & self["properties"]
        ), "Reserved property bits are set."

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


class GGCDirtyDict(GGCMixin, CacheableDirtyDict, GCABC):
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


class GGCDict(GGCMixin, CacheableDict, GCABC):
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
