"""Cacheable Dirty Dictionary Base Class module."""
from __future__ import annotations
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC, SEQUENCE_NUMBER_GENERATOR


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableTuple(tuple, CacheableObjABC):
    """Cacheable Tuple Class.
    Cacheable tuple objects cannot be modified so will never mark themseleves dirty.
    However, the dirty() and clean() methods are provided for consistency and can be used
    to copyback() automatically should that have someside effect that requires it.
    """


    def __init__(self, *args, **kwargs) -> None:
        """Constructor."""
        tuple.__init__(*args, **kwargs)
        self._dirty: bool = True
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

    def consistency(self) -> None:
        """Check the consistency of the object."""

    def copyback(self) -> CacheableTuple:
        """Copy the object back."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        self.clean()
        return self

    def dirty(self) -> None:
        """Mark the object as dirty."""
        self._dirty = True
        self.touch()

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self._dirty

    def seq_num(self) -> int:
        """Dirty dicts do not track sequence numbers."""
        return self._seq_num

    def touch(self) -> None:
        """Dirty dict objects cannot be touched."""
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        return list(self)

    def verify(self) -> None:
        """Verify the genetic code object."""
