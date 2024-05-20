"""Illegal MutableMapping methods in concrete cache classes."""
from typing import Any
from logging import Logger, NullHandler, getLogger, DEBUG


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


class CacheIllegal():
    """Illegal MutableMapping methods in concrete cache classes."""

    def __delitem__(self, key: Any) -> None:
        raise AssertionError("Caches do not support deletion of items. Items are purged.")

    def clear(self) -> None:
        """Illegal method."""
        raise AssertionError("Caches do not support clear. Items are flushed (full purge).")

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("Caches do not support pop. Items are purged.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("Caches do not support popitem. Items are purged.")
