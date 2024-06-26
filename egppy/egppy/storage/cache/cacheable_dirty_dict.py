"""Cacheable Dirty Dictionary Base Class module."""
from __future__ import annotations
from typing import Any
from copy import deepcopy
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from egppy.storage.cache.cacheable_obj_abc import CacheableObjABC
from egppy.storage.cache.cacheable_mixin import CacheableMixin


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class CacheableDirtyDict(dict, CacheableMixin, CacheableObjABC):
    """Cacheable Dirty Dictionary Class.
    Builtin dictionaries are fast but use a lot of space. This class is a base class
    for EGP objects using builtin dictionary methods without wrapping them.
    As a consequence when the dictionary is modified the object is not automatically
    marked as dirty, this must be done manually by the user using the dirty() method.
    """

    def __init__(self, *args, **kwargs) -> None:
        """Constructor."""
        super().__init__(*args, **kwargs)
        CacheableMixin.__init__(self)

    def consistency(self) -> None:
        """Check the consistency of the object."""

    def copyback(self) -> CacheableDirtyDict:
        """Copy the object back."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        self.clean()
        return self

    def to_json(self) -> dict[str, Any]:
        """Return a JSON serializable dictionary."""
        if _LOG_VERIFY:
            self.verify()
            if _LOG_CONSISTENCY:
                self.consistency()
        return deepcopy(x=self)

    def verify(self) -> None:
        """Verify the genetic code object."""
        assert not (x for x in self if not isinstance(x, str)), "Keys must be strings."
