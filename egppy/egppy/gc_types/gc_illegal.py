"""Illegal GC class methods in concrete GC classes."""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCIllegal():
    """Illegal GC class methods in concrete GC classes."""

    def clear(self) -> None:
        """Illegal method."""
        raise AssertionError("GCs do not support clear. Items are flushed (full purge).")

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("GCs do not support pop. Items are purged.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("GCs do not support popitem. Items are purged.")
