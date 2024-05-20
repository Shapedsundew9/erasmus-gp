"""Dirty Dictionary Genetic Code Base Class module."""
from typing import Any
from logging import Logger, NullHandler, getLogger, DEBUG
from copy import deepcopy
from egppy.gc_types.gc_abc import GCABC


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


class DirtyDictBaseGC(dict, GCABC):
    """Dirty Dictionary Genetic Code Base Class.
    Builtin dictionaries are fast but use a lot of space. This class is a base class
    for genetic code objects using builtin dictionary methods without wrapping them.
    As a consequence when the dictionary is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for DictGC"""
        super().__init__(*args, **kwargs)
        self._dirty: bool = True

    def assertions(self) -> None:
        """Abstract method for assertions"""

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

    def copyback(self) -> GCABC:
        """Copy the object back."""
        self.clean()
        return self

    def dirty(self) -> None:
        """Mark the object as dirty."""
        self._dirty = True

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self._dirty

    def json_dict(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self)
