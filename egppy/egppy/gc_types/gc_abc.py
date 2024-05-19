"""Genetic Code Abstract Base Class"""
from __future__ import annotations
from typing import Any
from collections.abc import MutableMapping
from abc import abstractmethod


class GCABC(MutableMapping):
    """Abstract Base Class for Genetic Code Types"""

    def __delitem__(self, key: Any) -> None:
        """Delete an item from the object."""
        assert False, "GC's do not support __delitem__."

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """Equality comparison."""

    @abstractmethod
    def __ne__(self, other: Any) -> bool:
        """Inequality comparison."""

    def clear(self) -> None:
        """Illegal method."""
        raise AssertionError("GC's do not support clear. Items are flushed (full purge).")

    @abstractmethod
    def clean(self) -> None:
        """Mark the object as clean."""

    @abstractmethod
    def dirty(self) -> None:
        """Mark the object as dirty."""

    @abstractmethod
    def is_dirty(self) -> bool:
        """Check if the object is dirty."""

    @abstractmethod
    def is_locked(self) -> bool:
        """Check if the object is locked."""

    @abstractmethod
    def lock(self) -> None:
        """Lock the object."""

    def pop(self, key: Any, default: Any = None) -> Any:
        """Illegal method."""
        raise AssertionError("GC's do not support pop. Items are purged.")

    def popitem(self) -> tuple:
        """Illegal method."""
        raise AssertionError("GC's do not support popitem. Items are purged.")
