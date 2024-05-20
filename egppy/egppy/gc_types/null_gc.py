"""The Null Genetic Code module.

A NULL GC is needed to stub out GC references without requiring None type support.
"""
from typing import Any
from egppy.gc_types.gc_abc import GCABC


class NullGC(dict, GCABC):
    """Null Genetic Code Class.

    This class is a stub for genetic code objects.
    """

    def __init__(self) -> None:
        """Constructor for NullGC"""
        super().__init__()
        self['lock'] = True
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

    def _dirty(self) -> None:
        """Null GC methods do nothing."""

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self['dirty']

    def is_locked(self) -> bool:
        """Check if the object is locked."""
        return self['lock']

    def lock(self) -> None:
        """Null GC methods do nothing."""

NULL_GC = NullGC()
