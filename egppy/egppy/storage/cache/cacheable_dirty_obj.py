"""Cacheable Dirty Dictionary Base Class module."""
from __future__ import annotations
from typing import Any
from copy import deepcopy
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_obj_base import CacheableObjBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableDirtyObjMixin():
    """Cacheable Dirty Object Mixin Class."""

    def clean(self) -> None:
        """No-op. Dirty objects are always dirty."""

    def dirty(self) -> None:
        """No-op. Dirty objects are always dirty."""

    def is_dirty(self) -> bool:
        """Dirty objects are always dirty."""
        return True

    def seq_num(self) -> int:
        """Dirty objects do not track sequence numbers."""
        return 0

    def touch(self) -> None:
        """Dirty objects cannot be touched."""


class CacheableDirtyDict(dict, CacheableObjBase, CacheableDirtyObjMixin, CacheableObjABC):
    """Cacheable Dirty Dictionary Class.
    Builtin dictionaries are fast but use a lot of space. This class is a base class
    for EGP objects using builtin dictionary methods without wrapping them.
    As a consequence when the dictionary is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """

    def to_json(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert not (x for x in self if not isinstance(x, str)), "Keys must be strings."
        super().verify()


class CacheableDirtyList(list, CacheableObjBase, CacheableDirtyObjMixin, CacheableObjABC):
    """Cacheable Dirty List Class.
    Builtin lists are fast but use a fair amount of space. This class is a base class
    for cache objects using builtin list methods without wrapping them.
    As a consequence when the list is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """

    def to_json(self) -> list:
        """Return a JSON serializable dictionary."""
        return deepcopy(x=self)
