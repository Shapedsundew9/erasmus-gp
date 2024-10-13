"""Storable object base class"""

from typing import Protocol

from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.common_obj_mixin import CommonObjMixin, CommonObjProtocol
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class StorableObjProtocol(CommonObjProtocol, Protocol):
    """Storable object protocol."""

    def modified(self) -> tuple[str | int, ...] | bool:
        """Mark the object as modified"""
        ...  # pylint: disable=unnecessary-ellipsis


class StorableObjMixin(CommonObjMixin, CommonObjABC):
    """Storable Mixin class has methods generic to all storable objects classes."""

    def modified(self) -> tuple[str | int, ...] | bool:
        """Mark the object as modified - always."""
        return True
