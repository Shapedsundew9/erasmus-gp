"""Storable object base class"""

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class StorableObjMixin:
    """Storable Mixin class has methods generic to all storable objects classes."""

    __slots__ = ()

    def modified(self) -> tuple[str | int, ...] | bool:
        """Mark the object as modified - always."""
        return True
