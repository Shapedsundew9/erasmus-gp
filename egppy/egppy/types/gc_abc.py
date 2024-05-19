"""Genetic Code Abstract Base Class"""
from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod


class GCABC(MutableMapping):
    """Abstract Base Class for Genetic Code Types"""

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison."""

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty."""

    def clear(self) -> None:
        """Illegal method."""
        raise AssertionError("GC's do not support clear. Items are flushed (full purge).")

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("GC's do not support pop. Items are purged.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("GC's do not support popitem. Items are purged.")
