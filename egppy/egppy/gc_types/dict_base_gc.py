"""Dictionary Genetic Code Base Class module."""
from typing import Any
from egppy.gc_types.dirty_dict_base_gc import DirtyDictBaseGC


class DictBaseGC(DirtyDictBaseGC):
    """Dictionary Genetic Code Base Class.
    The DictBaseGC uses a builtin dictionary for storage but wraps the __setitem__
    and update methods to mark the object as dirty when modified. This makes it slightly
    slower but relieves the user from having to keep track of the object's state.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for DictGC"""
        super().__init__(*args, **kwargs)
        self._dirty: bool = True

    def __setitem__(self, key: str, value: Any) -> None:
        """Set an item in the dictionary."""
        super().__setitem__(key, value)
        self.dirty()

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set a default item in the dictionary."""
        if not key in self:
            super().__setitem__(key, default)
            self.dirty()
            return default
        return self[key]

    def update(self, *args, **kwargs) -> None:
        """Update the dictionary."""
        super().update(*args, **kwargs)
        self.dirty()
