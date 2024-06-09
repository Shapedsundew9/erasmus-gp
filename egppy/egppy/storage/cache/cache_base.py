"""Cache Base class module."""
from typing import Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheBase():
    """Cache Base class has methods generic to all cache classes."""

    def __init__(self) -> None:
        """Must be implemented by subclasses."""
        self.max_size = 0
        raise NotImplementedError

    def __len__(self) -> int:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def consistency(self) -> None:
        """Check the cache for self consistency."""
        for value in self.values():
            value.consistency()

    def values(self) -> Iterable[CacheableObjABC]:
        """Must be implemented by subclasses."""
        raise NotImplementedError

    def verify(self) -> None:
        """Verify the cache.
        Every object stored in the cache is verified as well as basic
        cache parameters.
        """
        for value in self.values():
            value.verify()

        assert len(self) <= self.max_size, "Cache size exceeds max_size."
