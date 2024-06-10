"""Cacheable Dictionary Base Class module."""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_dirty_dict import CacheableDirtyDict


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableDict(CacheableDirtyDict):
    """Cacheable Dictionary  Class.
    The CacheableDict uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __getitem__(self, key: Any) -> Any:
        """Get an item from the dictionary."""
        self.touch()
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item in the dictionary."""
        super().__setitem__(key, value)
        self.dirty()

    def get(self, key: str, default: Any = None) -> Any:
        """Get an item from the dictionary."""
        self.touch()
        return super().get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set a default item in the dictionary."""
        if not key in self:
            super().__setitem__(key, default)
            self.dirty()
            return default
        return self[key]

    def update(self, *args, **kwargs) -> None:
        """Update the dictionary."""
        super().update(*args, **kwargs)
        self.dirty()
