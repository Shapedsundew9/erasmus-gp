"""Dictionary Genetic Code module."""
from typing import Any
from egppy.gc_types.gc_abc import GCABC


class DictBaseGC(dict, GCABC):
    """Dictionary Base Genetic Code Class.
    Builtin dictionaries are fast but use a lot of space. This class is a base class
    for genetic code objects using builtin dictionaries.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for DictGC"""
        super().__init__(*args, **kwargs)
        self['lock'] = False
        self['dirty'] = False

    def __delitem__(self, key: str) -> None:
        """Deleting an item checks the lock."""
        super().__delitem__(key)

    def __getitem__(self, key: str) -> Any:
        """Get an item from the object."""
        return super().__getitem__(key)

    def __setitem__(self, key, value) -> None:
        """Setting an item validates the key:value if _LOG_DEBUG is True."""
        super().__setitem__(key, value)

    def assertions(self) -> None:
        """Abstract method for assertions"""

    def clean(self) -> None:
        """Mark the object as clean."""
        self['dirty'] = False

    def dirty(self) -> None:
        """Mark the object as dirty."""
        self['dirty'] = True

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self['dirty']

    def is_locked(self) -> bool:
        """Check if the object is locked."""
        return self['lock']

    def lock(self) -> None:
        """Lock the object."""
        self['lock'] = True
