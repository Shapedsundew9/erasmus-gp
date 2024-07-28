"""Common Genetic Code Class Factory.

A Common Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from datetime import datetime
from typing import Any
from egppy.gc_graph.ep_type import validate
from egppy.gc_types.egc_class_factory import EGCMixin
from egppy.gc_types.gc import GCABC, NULL_GC, GCProtocol, PROPERTIES
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CGCMixin(EGCMixin, GCProtocol):
    """Common member definitions for PGC & GGC classes."""

    GC_KEY_TYPES: dict[str, str] = {
        '_lost_descendants': "BIGINT",
        '_reference_count': "BIGINT",
        'code_depth': "INT",
        'codon_depth': "INT",
        'created': "TIMESTAMP",
        'descendants': "BIGINT",
        'generation': "BIGINT",
        'input_types': "SMALLINT[]",
        'inputs': "BYTEA[]",
        'lost_descendants': "BIGINT",
        'meta_data': "BYTEA[]",
        'num_codes': "INT",
        'num_codons': "INT",
        'num_inputs': "SMALLINT",
        'num_outputs': "SMALLINT",
        'output_types': "SMALLINT[]",
        'outputs': "BYTEA[]",
        'properties': "BIGINT",
        'reference_count': "BIGINT",
        'updated': "TIMESTAMP"
    } | EGCMixin.GC_KEY_TYPES

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency."""
        super().consistency()
        assert self['_lost_descendants'] <= self['lost_descendants'], \
            "_lost_descendants must be less than or equal to lost_descendants."
        assert self['_reference_count'] <= self['reference_count'], \
            "_reference_count must be less than or equal to reference_count."
        assert self['code_depth'] == 1 and self['gca'] is NULL_GC, \
            "A code depth of 1 is a codon or empty GC and must have a NULL GCA."
        assert self['code_depth'] > 1 and self['gca'] is not NULL_GC, \
            "A code depth greater than 1 must have a non-NULL GCA."
        assert self['codon_depth'] == 0 and self['gca'] is NULL_GC, \
            "A codon depth of 0 is an empty GC must have a NULL GCA."
        assert self['codon_depth'] == 1 and self['gca'] is NULL_GC, \
            "A codon depth of 1 is a codon and  must have a NULL GCA."
        assert self['codon_depth'] > 1 and self['gca'] is not NULL_GC, \
            "A codon depth greater than 1 must have a non-NULL GCA."
        assert self['created'] <= self['updated'], \
            "created time must be less than updated time."
        assert self['generation'] == 0 and self['gca'] is NULL_GC, \
            "A generation of 0 is a codon or empty GC and must have a NULL GCA."
        assert self['generation'] > 0 and self['gca'] is not NULL_GC, \
            "A generation greater than 0 must have a non-NULL GCA."
        assert (not self['input_types']) == (not self['inputs']), \
            "input_types and inputs both be 0 length or both be > 0 length."
        assert len(self['inputs']) <= len(self['input_types']), \
            "The number of inputs must be less than or equal to the number of input_types."
        assert self['lost_descendants'] <= self['reference_count'], \
            "lost_descendants must be less than or equal to reference_count."
        assert self['num_codes'] >= self['code_depth'], \
            "num_codes must be greater than or equal to code_depth."
        assert self['num_codons'] >= self['codon_depth'], \
            "num_codons must be greater than or equal to codon_depth."
        assert (not self['output_types']) == (not self['outputs']), \
            "output_types and outputs both be 0 length or both be > 0 length."
        assert len(self['outputs']) <= len(self['output_types']), \
            "The number of outputs must be less than or equal to the number of output_types."
        assert self['updated'] <= datetime.now(), \
            "updated time must be less than or equal to the current time."

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the UGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        super().set_members(gcabc)
        self['_lost_descendants'] = gcabc.get('_lost_descendants', 0)
        self['_reference_count'] = gcabc.get('_reference_count', 0)
        self['code_depth'] = gcabc.get('code_depth', 1)
        self['created'] = gcabc.get('created', datetime.now())
        self['descendants'] = gcabc.get('descendants', 0)
        self['generation'] = gcabc.get('generation', 0)
        self['input_types'] = gcabc.get('input_types', [])
        self['inputs'] = gcabc.get('inputs', [])
        self['lost_descendants'] = gcabc.get('lost_descendants', 0)
        self['meta_data'] = gcabc.get('meta_data', {})
        self['num_codes'] = gcabc.get('num_codes', 1)
        self['num_codons'] = gcabc.get('num_codons', 1)
        self['num_inputs'] = gcabc.get('num_inputs', 0)
        self['num_outputs'] = gcabc.get('num_outputs', 0)
        self['output_types'] = gcabc.get('output_types', [])
        self['outputs'] = gcabc.get('outputs', [])
        self['properties'] = gcabc.get('properties', 0)
        self['reference_count'] = gcabc.get('reference_count', 0)
        self['updated'] = gcabc.get('updated', datetime.now())

    def verify(self: GCProtocol) -> None:
        """Verify the common members of the genetic code object."""
        super().verify()

        # The number of descendants when the genetic code was copied from the higher layer.
        assert self['_lost_descendants'] >= 0, \
            "_lost_descendants must be greater than or equal to zero."
        assert self['_lost_descendants'] <= 2**63-1, \
            "_lost_descendants must be less than or equal to 2**63-1."

        # The reference count when the genetic code was copied from the higher layer.
        assert self['_reference_count'] >= 0, \
            "_reference_count must be greater than or equal to zero."
        assert self['_reference_count'] <= 2**63-1, \
            "_reference_count must be less than or equal to 2**63-1."

        # The depth of the genetic code in genetic codes. If this is a codon then the depth is 1.
        assert self['code_depth'] >= 1, "code_depth must be greater than or equal to one."
        assert self['code_depth'] <= 2**31-1, "code_depth must be less than or equal to 2**31-1."

        # The date and time the genetic code was created.
        assert self['created'] <= datetime.now(), \
            "created must be less than or equal to the current date and time."

        # The number of generations of genetic code evolved to create this code. A codon is always
        # generation 1.
        assert self['generation'] >= 0, "generation must be greater than or equal to zero."
        assert self['generation'] <= 2**63-1, "generation must be less than or equal to 2**63-1."

        # The set of types of the inputs in ascending order of type number.
        assert len(itypes := self['input_types']) <= 256, \
            "input_types must have a length less than or equal to 256."
        assert len(set(itypes)) == len(itypes), "input_types must be unique."
        assert all(validate(x) for x in self['input_types']), \
            "input_types must all be valid end point types."
        assert all(itypes[i] < itypes[i+1] for i in range(len(itypes)-1)), \
            "input_types must be in ascending order."

        # The index of the each input parameters type in the 'input_types' list in the order they
        # are required for the function call.
        assert len(self['inputs']) <= 256, "inputs must have a length less than or equal to 256."
        assert all(x < 256 for x in self['inputs']), "inputs indexes must be < 256."

        # The number of descendants that have been lost in the evolution of the genetic code.
        assert self['lost_descendants'] >= 0, \
            "lost_descendants must be greater than or equal to zero."
        assert self['lost_descendants'] <= 2**63-1, \
            "lost_descendants must be less than or equal to 2**63-1."

        # The meta data associated with the genetic code.
        # No verification is performed on the meta data.

        # The number of vertices in the GC code vertex graph.
        assert self['num_codes'] >= 1, "num_codes must be greater than or equal to one."
        assert self['num_codes'] <= 2**31-1, "num_codes must be less than or equal to 2**31-1."

        # The number of codons in the GC code codon graph.
        assert self['num_codons'] >= 0, "num_codons must be greater than or equal to one."
        assert self['num_codons'] <= 2**31-1, "num_codons must be less than or equal to 2**31-1."

        # The number of input parameters required by the genetic code (function).
        assert self['num_inputs'] >= 0, "num_inputs must be greater than or equal to zero."
        assert self['num_inputs'] <= 256, "num_inputs must be less than or equal to 256."

        # The number of output parameters returned by the genetic code (function).
        assert self['num_outputs'] >= 0, "num_outputs must be greater than or equal to zero."
        assert self['num_outputs'] <= 256, "num_outputs must be less than or equal to 256."

        # The set of types of the outputs in ascending order of type number.
        assert len(otypes := self['output_types']) <= 256, \
            "output_types must have a length less than or equal to 256."
        assert len(set(otypes)) == len(otypes), "output_types must be unique."
        assert all(validate(x) for x in self['output_types']), \
            "output_types must all be valid end point types."
        assert all(otypes[i] < otypes[i+1] for i in range(len(otypes)-1)), \
            "output_types must be in ascending order."

        # The index of the each output parameters type in the 'output_types' list in the order they
        # are returned from the function call.
        assert len(self['outputs']) <= 256, "outputs must have a length less than or equal to 256."
        assert all(x < 256 for x in self['outputs']), "outputs indexes must be < 256."

        # The properties of the genetic code.
        assert self['properties'] >= -2**63, "properties must be greater than or equal to -2**63."
        assert self['properties'] <= 2**63-1, "properties must be less than or equal to 2**63-1."
        assert not(sum(PROPERTIES.values()) & ~self['properties']), \
            "Reserved property bits are set."

        # The reference count of the genetic code.
        assert self['reference_count'] >= 0, \
            "reference_count must be greater than or equal to zero."
        assert self['reference_count'] <= 2**63-1, \
            "reference_count must be less than or equal to 2**63-1."

        # The date and time the genetic code was last updated.
        assert self['updated'] <= datetime.now(), \
            "updated must be less than or equal to the current date and time."


class CGCDirtyDict(CacheableDirtyDict, CGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictCGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDirtyDict.consistency(self)
        CGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDirtyDict.verify(self)
        CGCMixin.verify(self)


class CGCDict(CacheableDict, CGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictCGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)
        CGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)
        CGCMixin.verify(self)


CGCType = CGCDirtyDict | CGCDict
