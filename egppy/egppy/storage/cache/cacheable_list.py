"""Cacheable Dictionary Base Class module."""
from typing import Any, overload, SupportsIndex, Iterable
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_list import CacheableDirtyList


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableList(CacheableDirtyList):
    """Cacheable List Class.
    The CacheableList uses a builtin list for storage but wraps the __setitem__
    method to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __getitem__(self, x: slice | SupportsIndex) -> Any:
        """Get an element of the list."""
        self.touch()
        return super().__getitem__(x)

    @overload
    def __setitem__(self, i: SupportsIndex, value: Any, /) -> None: ...
    @overload
    def __setitem__(self, s: slice, value: Iterable[Any], /) -> None: ...

    def __setitem__(self, x: slice | SupportsIndex, value: Any) -> None:
        """Set an element of the list."""
        super().__setitem__(x, value)
        self.dirty()
