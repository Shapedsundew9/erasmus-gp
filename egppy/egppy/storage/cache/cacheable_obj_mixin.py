"""Cacheable Dictionary Base Class module."""

from itertools import count

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.storage.store.storable_obj_mixin import StorableObjMixin

# Universal sequence number generator
SEQUENCE_NUMBER_GENERATOR = count(start=-(2**63))


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableObjMixin(StorableObjMixin):
    """Cacheable Mixin Class.
    Used to add cacheable functionality to a class.
    """

    __slots__ = ("_dirty", "_seq_num")

    def __init__(self) -> None:
        """Constructor."""
        self._dirty: bool = True
        # deepcode ignore unguarded~next~call: Cannot raise StopIteration
        self._seq_num: int = next(SEQUENCE_NUMBER_GENERATOR)

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

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
