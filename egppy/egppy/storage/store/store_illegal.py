"""Illegal MutableMapping methods in concrete store classes."""
from typing import Any
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StoreIllegal():
    """Illegal MutableMapping methods in concrete store classes."""

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("Stores do not support pop.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("Stores do not support popitem.")
