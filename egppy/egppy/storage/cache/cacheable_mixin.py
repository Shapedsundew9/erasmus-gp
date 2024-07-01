"""Cacheable Dirty Dictionary Base Class module."""
from __future__ import annotations
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import SEQUENCE_NUMBER_GENERATOR


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableMixin():
    """Cacheable Mixin Class.
    Used to add cacheable functionality to a class.
    """

    def __init__(self) -> None:
        """Constructor."""
        self._dirty: bool = True
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

    def consistency(self) -> None:
        """Check the consistency of the object."""

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
