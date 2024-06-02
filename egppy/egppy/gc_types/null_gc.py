"""The Null Genetic Code module.

A NULL GC is needed to stub out GC references without requiring None type support.
"""
from __future__ import annotations
from typing import Any
from egppy.gc_types.gc_abc import GCABC
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class NullGC(dict, GCABC):
    """Null Genetic Code Class.

    This class is a stub for genetic code objects.
    """

    def __init__(self) -> None:
        """Constructor for NullGC"""
        super().__init__()
        self['dirty'] = False

    def __delitem__(self, key: str) -> None:
        """Null GC methods do nothing."""

    def __getitem__(self, key: str) -> Any:
        """Null GC methods do nothing."""
        return super().__getitem__(key)

    def __setitem__(self, key, value) -> None:
        """Null GC methods do nothing."""

    def assertions(self) -> None:
        """Null GC methods do nothing."""

    def clean(self) -> None:
        """Null GC methods do nothing."""

    def consistency(self) -> None:
        """Null GC methods do nothing."""

    def copyback(self) -> NullGC:
        """Null GC methods do nothing."""
        return self

    def dirty(self) -> None:
        """Null GC methods do nothing."""

    def from_json(self, json_obj: dict[str, Any] | list) -> None:
        """Null GC methods do nothing."""

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self['dirty']

    def to_json(self) -> dict[str, Any]:
        """Null GC methods do nothing."""
        return {}

    def verify(self) -> None:
        """Null GC methods do nothing."""


NULL_GC = NullGC()
