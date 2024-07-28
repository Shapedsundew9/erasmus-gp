"""Physical Genetic Code Class Factory.

A Physical Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from math import isclose
from typing import Any
from egppy.gc_types.cgc_class_factory import CGCMixin
from egppy.gc_types.gc import GCABC, GCProtocol, NUM_PGC_LAYERS
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class PGCMixin(CGCMixin, GCProtocol):
    """Physical Genetic Code Mixin Class."""

    GC_KEY_TYPES: dict[str, str] = {
        '_pgc_e_count': "INT[]",
        '_pgc_e_total': "FLOAT[]",
        '_pgc_evolvability': "FLOAT[]",
        '_pgc_f_count': "INT[]",
        '_pgc_f_total': "FLOAT[]",
        '_pgc_fitness': "FLOAT[]",
        'pgc_e_count': "INT[]",
        'pgc_e_total': "FLOAT[]",
        'pgc_evolvability': "FLOAT[]",
        'pgc_f_count': "INT[]",
        'pgc_f_total': "FLOAT[]",
        'pgc_fitness': "FLOAT[]"
    } | CGCMixin.GC_KEY_TYPES

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency."""
        super().consistency()
        assert all(x >= y for x, y in zip(self['pgc_e_count'], self['_pgc_e_count'])), \
            "PGC evolvability count must be greater than or equal to the higher layer count."
        assert all(x >= y for x, y in zip(self['pgc_e_total'], self['_pgc_e_total'])), \
            "PGC evolvability total must be greater than or equal to the higher layer total."
        assert all(x >= y for x, y in zip(self['_pgc_e_total'], self['_pgc_e_count'])), \
            "PGC evolvability total must be greater than or equal to the evolvability count."
        assert all(isclose(x, y / z) for x, y, z in zip(self['pgc_evolvability'], \
            self['pgc_e_total'], self['pgc_e_count'])), \
            "PGC evolvability must be the total evolvability divided by the count."
        assert all(x >= y for x, y in zip(self['pgc_f_count'], self['_pgc_f_count'])), \
            "PGC fitness count must be greater than or equal to the higher layer count."
        assert all(x >= y for x, y in zip(self['pgc_f_total'], self['_pgc_f_total'])), \
            "PGC fitness total must be greater than or equal to the higher layer total."
        assert all(x >= y for x, y in zip(self['_pgc_f_total'], self['_pgc_f_count'])), \
            "PGC fitness total must be greater than or equal to the fitness count."
        assert all(isclose(x, y / z) for x, y, z in zip(self['pgc_fitness'], \
            self['pgc_f_total'], self['pgc_f_count'])), \
            "PGC fitness must be the total fitness divided by the count."

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the UGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        super().set_members(gcabc)
        self['_pgc_e_count'] = gcabc.get('_pgc_e_count', [1] * NUM_PGC_LAYERS)
        self['_pgc_e_total'] = gcabc.get('_pgc_e_total', [0.0] * NUM_PGC_LAYERS)
        self['_pgc_evolvability'] = gcabc.get('_pgc_evolvability', \
            [t/c for t, c in zip(self['_pgc_e_total'], self['_pgc_e_count'])])
        self['_pgc_f_count'] = gcabc.get('_pgc_f_count', [1] * NUM_PGC_LAYERS)
        self['_pgc_f_total'] = gcabc.get('_pgc_f_total', [0.0] * NUM_PGC_LAYERS)
        self['_pgc_fitness'] = gcabc.get('_pgc_fitness', \
            [t/c for t, c in zip(self['_pgc_f_total'], self['_pgc_f_count'])])
        self['pgc_e_count'] = gcabc.get('pgc_e_count', self['_pgc_e_count'])
        self['pgc_e_total'] = gcabc.get('pgc_e_total', self['_pgc_e_total'])
        self['pgc_evolvability'] = gcabc.get('pgc_evolvability', \
            [t/c for t, c in zip(self['pgc_e_total'], self['pgc_e_count'])])
        self['pgc_f_count'] = gcabc.get('pgc_f_count', self['_pgc_f_count'])
        self['pgc_f_total'] = gcabc.get('pgc_f_total', self['_pgc_f_total'])
        self['pgc_fitness'] = gcabc.get('pgc_fitness', \
            [t/c for t, c in zip(self['pgc_f_total'], self['pgc_f_count'])])

    def verify(self: GCProtocol) -> None:
        """Verify the genetic code object."""
        super().verify()
        assert len(self['_pgc_e_count']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability count layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 1 for x in self['_pgc_e_count']), \
            "PGC evolvability count must be greater than or equal to 1."
        assert all(x <= 2**31-1 for x in self['_pgc_e_count']), \
            "PGC evolvability count must be less than 2^31-1."
        assert len(self['_pgc_e_total']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability total layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['_pgc_e_total']), \
            "PGC evolvability total must be greater than or equal to 0.0."
        assert all(x <= 2**31-1 for x in self['_pgc_e_total']), \
            "PGC evolvability total must be less than 2^31-1."
        assert len(self['_pgc_evolvability']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['_pgc_evolvability']), \
            "PGC evolvability must be greater than or equal to 0.0."
        assert all(x <= 1.0 for x in self['_pgc_evolvability']), \
            "PGC evolvability must be less than or equal to 1.0."
        assert len(self['_pgc_f_count']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness count layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 1 for x in self['_pgc_f_count']), \
            "PGC fitness count must be greater than or equal to 1."
        assert all(x <= 2**31-1 for x in self['_pgc_f_count']), \
            "PGC fitness count must be less than 2^31-1."
        assert len(self['_pgc_f_total']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness total layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['_pgc_f_total']), \
            "PGC fitness total must be greater than or equal to 0.0."
        assert all(x <= 2**31-1 for x in self['_pgc_f_total']), \
            "PGC fitness total must be less than 2^31-1."
        assert len(self['_pgc_fitness']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['_pgc_fitness']), \
            "PGC fitness must be greater than or equal to 0.0."
        assert all(x <= 1.0 for x in self['_pgc_fitness']), \
            "PGC fitness must be less than or equal to 1.0."
        assert len(self['pgc_e_count']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability count layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 1 for x in self['pgc_e_count']), \
            "PGC evolvability count must be greater than or equal to 1."
        assert all(x <= 2**31-1 for x in self['pgc_e_count']), \
            "PGC evolvability count must be less than 2^31-1."
        assert len(self['pgc_e_total']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability total layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['pgc_e_total']), \
            "PGC evolvability total must be greater than or equal to 0.0."
        assert all(x <= 2**31-1 for x in self['pgc_e_total']), \
            "PGC evolvability total must be less than 2^31-1."
        assert len(self['pgc_evolvability']) == NUM_PGC_LAYERS, \
            f"The number of PGC evolvability layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['pgc_evolvability']), \
            "PGC evolvability must be greater than or equal to 0.0."
        assert all(x <= 1.0 for x in self['pgc_evolvability']), \
            "PGC evolvability must be less than or equal to 1.0."
        assert len(self['pgc_f_count']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness count layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 1 for x in self['pgc_f_count']), \
            "PGC fitness count must be greater than or equal to 1."
        assert all(x <= 2**31-1 for x in self['pgc_f_count']), \
            "PGC fitness count must be less than 2^31-1."
        assert len(self['pgc_f_total']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness total layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['pgc_f_total']), \
            "PGC fitness total must be greater than or equal to 0.0."
        assert all(x <= 2**31-1 for x in self['pgc_f_total']), \
            "PGC fitness total must be less than 2^31-1."
        assert len(self['pgc_fitness']) == NUM_PGC_LAYERS, \
            f"The number of PGC fitness layers must be {NUM_PGC_LAYERS}."
        assert all(x >= 0.0 for x in self['pgc_fitness']), \
            "PGC fitness must be greater than or equal to 0.0."
        assert all(x <= 1.0 for x in self['pgc_fitness']), \
            "PGC fitness must be less than or equal to 1.0."


class PGCDirtyDict(CacheableDirtyDict, PGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictPGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDirtyDict.consistency(self)
        PGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDirtyDict.verify(self)
        PGCMixin.verify(self)


class PGCDict(CacheableDict, PGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictPGC"""
        super().__init__()
        self.set_members(gcabc)

    def consistency(self) -> None:
        """Check the genetic code object for consistency."""
        # Need to call consistency down both MRO paths.
        CacheableDict.consistency(self)
        PGCMixin.consistency(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        # Need to call verify down both MRO paths.
        CacheableDict.verify(self)
        PGCMixin.verify(self)


PGCType = PGCDirtyDict | PGCDict
