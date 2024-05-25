"""Illegal MutableMapping methods in concrete store classes."""
from typing import Any
from logging import Logger, NullHandler, getLogger, DEBUG


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


class StoreIllegal():
    """Illegal MutableMapping methods in concrete store classes."""

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("Stores do not support pop.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("Stores do not support popitem.")
