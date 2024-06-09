"""Cacheable Dirty Dictionary Base Class module."""
from __future__ import annotations
from typing import Any
from copy import deepcopy
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableDirtyList(list, CacheableObjABC):
    """Cacheable Dirty List Class.
    Builtin lists are fast but use a fair amount of space. This class is a base class
    for cache objects using builtin list methods without wrapping them.
    As a consequence when the list is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor."""
        super().__init__(*args, **kwargs)
        self._dirty: bool = True

    def clean(self) -> None:
        """Mark the object as clean."""
        self._dirty = False

    def consistency(self) -> None:
        """Check the consistency of the object."""

    def copyback(self) -> CacheableDirtyList:
        """Copy the object back."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        self.clean()
        return self

    def dirty(self) -> None:
        """Mark the object as dirty."""
        self._dirty = True

    def from_json(self, json_obj: dict[str, Any] | list) -> None:
        """Re-initialize the object with data from json_obj."""
        self.__init__(json_obj)  # pylint: disable=unnecessary-dunder-call

    def is_dirty(self) -> bool:
        """Check if the object is dirty."""
        return self._dirty

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        return deepcopy(x=self)

    def verify(self) -> None:
        """Verify the genetic code object."""
