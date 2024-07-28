"""General Genetic Code Class Factory.

A General Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from math import isclose
from typing import Any
from egppy.gc_types.cgc_class_factory import CGCMixin
from egppy.gc_types.gc import GCABC, GCProtocol
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_obj import CacheableDirtyDict
from egppy.storage.cache.cacheable_obj import CacheableDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GGCMixin(CGCMixin, GCProtocol):
    """General Genetic Code Mixin Class."""

    GC_KEY_TYPES: dict[str, str] = {
        '_e_count': "INT",
        '_e_total': "FLOAT",
        '_evolvability': "FLOAT",
        '_f_count': "INT",
        '_f_total': "FLOAT",
        '_fitness': "FLOAT",
        'e_count': "INT",
        'e_total': "FLOAT",
        'evolvability': "FLOAT",
        'f_count': "INT",
        'f_total': "FLOAT",
        'fitness': "FLOAT",
        'population_uid': "SMALLINT",
        'survivability': "FLOAT"
    } | CGCMixin.GC_KEY_TYPES

    def consistency(self: GCProtocol) -> None:
        """Check the genetic code object for consistency."""
        super().consistency()
        assert self['e_count'] >= self['_e_count'], \
            "Evolvability count must be greater than or equal to the higher layer count."
        assert self['e_total'] >= self['_e_total'], \
            "Evolvability total must be greater than or equal to the higher layer total."
        assert self['_e_total'] >= self['_e_count'], \
            "Evolvability total must be greater than or equal to the evolvability count."
        assert isclose(self['_evolvability'], self['_e_total'] / self['_e_count']), \
            "Evolvability must be the total evolvability divided by the count."
        assert self['f_count'] >= self['_f_count'], \
            "Fitness count must be greater than or equal to the higher layer count."
        assert self['f_total'] >= self['_f_total'], \
            "Fitness total must be greater than or equal to the higher layer total."
        assert self['_f_total'] >= self['_f_count'], \
            "Fitness total must be greater than or equal to the fitness count."
        assert isclose(self['_fitness'], self['_f_total'] / self['_f_count']), \
            "Fitness must be the total fitness divided by the count."

    def set_members(self: GCProtocol, gcabc: GCABC | dict[str, Any]) -> None:
        """Set the attributes of the UGC.

        Args:
            gcabc: The genetic code object or dictionary to set the attributes.
        """
        super().set_members(gcabc)
        self['_e_count'] = gcabc.get('_e_count', 1)
        self['_e_total'] = gcabc.get('_e_total', 0.0)
        self['_evolvability'] = self['_e_total'] / self['_e_count']
        self['_f_count'] = gcabc.get('_f_count', 1)
        self['_f_total'] = gcabc.get('_f_total', 0.0)
        self['_fitness'] = self['_f_total'] / self['_f_count']
        self['e_count'] = gcabc.get('e_count', self['_e_count'])
        self['e_total'] = gcabc.get('e_total', self['_e_total'])
        assert self['e_count'] > 0, "e_count must be greater than 0."
        self['evolvability'] = self['e_total'] / self['e_count']
        self['f_count'] = gcabc.get('f_count', self['_f_count'])
        self['f_total'] = gcabc.get('f_total', self['_f_total'])
        assert self['f_count'] > 0, "f_count must be greater than 0."
        self['fitness'] = self['f_total'] / self['f_count']
        self['population_uid'] = gcabc.get('population_uid', 0)
        self['survivability'] = gcabc.get('survivability', 0.0)

    def verify(self: GCProtocol) -> None:
        """Verify the genetic code object."""
        super().verify()

        # The evolvability update count when the genetic code was copied from the higher layer.
        assert self['_e_count'] >= 0, "Evolvability count must be greater than or equal to 0."
        assert self['_e_count'] <= 2**31-1, "Evolvability count must be less than 2**31-1."

        # The total evolvability when the genetic code was copied from the higher layer.
        assert self['_e_total'] >= 0.0, "Evolvability total must be greater than or equal to 0.0."
        assert self['_e_total'] <= 2**31-1, "Evolvability total must be less than 2**31-1."

        # The evolvability when the genetic code was copied from the higher layer.
        assert self['_evolvability'] >= 0.0, "Evolvability must be greater than or equal to 0.0."
        assert self['_evolvability'] <= 1.0, "Evolvability must be less than or equal to 1.0."

        # The fitness update count when the genetic code was copied from the higher layer.
        assert self['_f_count'] >= 0, "Fitness count must be greater than or equal to 0."
        assert self['_f_count'] <= 2**31-1, "Fitness count must be less than 2**31-1."

        # The total fitness when the genetic code was copied from the higher layer.
        assert self['_f_total'] >= 0.0, "Fitness total must be greater than or equal to 0.0."
        assert self['_f_total'] <= 2**31-1, "Fitness total must be less than 2**31-1."

        # The fitness when the genetic code was copied from the higher layer.
        assert self['_fitness'] >= 0.0, "Fitness must be greater than or equal to 0.0."
        assert self['_fitness'] <= 1.0, "Fitness must be less than or equal to 1.0."

        # The number of evolvability updates in this genetic codes life time.
        assert self['e_count'] >= 0, "Evolvability count must be greater than or equal to 0."
        assert self['e_count'] <= 2**31-1, "Evolvability count must be less than 2**31-1."

        # The total evolvability in this genetic codes life time.
        assert self['e_total'] >= 0.0, "Evolvability total must be greater than or equal to 0.0."
        assert self['e_total'] <= 2**31-1, "Evolvability total must be less than 2**31-1."

        # The number of descendants.
        assert self['descendants'] >= 0, "Descendants must be greater than or equal to 0."
        assert self['descendants'] <= 2**31-1, "Descendants must be less than 2**31-1."

        # The current evolvability.
        assert self['evolvability'] >= 0.0, "Evolvability must be greater than or equal to 0.0."
        assert self['evolvability'] <= 1.0, "Evolvability must be less than or equal to 1.0."

        # The number of fitness updates in this genetic codes life time.
        assert self['f_count'] >= 0, "Fitness count must be greater than or equal to 0."
        assert self['f_count'] <= 2**31-1, "Fitness count must be less than 2**31-1."

        # The total fitness in this genetic codes life time.
        assert self['f_total'] >= 0.0, "Fitness total must be greater than or equal to 0.0."
        assert self['f_total'] <= 2**31-1, "Fitness total must be less than 2**31-1."

        # The current fitness.
        assert self['fitness'] >= 0.0, "Fitness must be greater than or equal to 0.0."
        assert self['fitness'] <= 1.0, "Fitness must be less than or equal to 1.0."

        # The population UID.
        assert self['population_uid'] >= 0, "Population UID must be greater than or equal to 0."
        assert self['population_uid'] <= 2**16-1, "Population UID must be less than 2**16-1."

        # The survivability.
        assert self['survivability'] >= 0.0, "Survivability must be greater than or equal to 0.0."
        assert self['survivability'] <= 1.0, "Survivability must be less than or equal to 1.0."


class GGCDirtyDict(CacheableDirtyDict, GGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictGGC"""
        super().__init__()
        self.set_members(gcabc)

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


class GGCDict(CacheableDict, GGCMixin, GCProtocol, GCABC):
    """Dirty Dictionary Embryonic Genetic Code Class."""

    def __init__(self, gcabc: GCABC | dict[str, Any]) -> None:
        """Constructor for DirtyDictGGC"""
        super().__init__()
        self.set_members(gcabc)

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
