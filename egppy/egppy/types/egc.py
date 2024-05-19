"""Embryonic Genetic Code"""
from typing import Any
from logging import Logger, NullHandler, getLogger, DEBUG
from egppy.types.gc_abc import GCABC


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


# Key and value rules
_KEY_RULES: dict[str, Any] = {
    "type": "string",
    "minLength": 1,
    "maxLength": 10,
    "pattern": "^[A-Z]{3}$"
}
class EGC(dict[str, Any], GCABC):
    """Embryonic Genetic Code Class"""

    __slots__: list[str] = ["lock", "idx", "dirty"]

    def __init__(self) -> None:
        """Constructor for EGC validates the object if _LOG_DEBUG is True."""
        super().__init__()
        # Lock the object to prevent further changes. Once locked dervied classes may
        # implement efficient storage methods for the data. This does not make all data
        # immutable, but it does prevent the structure of the data from changing.
        self.lock: bool = False
        # A dervied class may implement an indexed storage method for the data.
        self.idx: int = 0
        # GC is dirty if it has been modified
        self.dirty: bool = False

    def __delitem__(self, key: str) -> None:
        """Deleting an item checks the lock."""
        assert not self.lock, "Cannot delete item from locked object."
        super().__delitem__(key)

    def __getitem__(self, key: str) -> any:
        """Get an item from the object."""

    def __setitem__(self, key, value):
        """Setting an item validates the key:value if _LOG_DEBUG is True."""
        if _LOG_DEBUG:
            self._validate(key, value)
            if key not in self and self._lock:
                raise KeyError(f"Cannot add new key '{key}' to locked object.")
            if key in 
        pass

    def assertions(self):
        """Abstract method for assertions"""
        pass
