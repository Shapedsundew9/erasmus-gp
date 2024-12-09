"""The End Point Type Abstract Base Class."""

from __future__ import annotations

from abc import abstractmethod

from egpcommon.common import NULL_TUPLE
from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.import_def import ImportDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class EndPointTypeABC(CommonObjABC):
    """End Point Type ABC class."""

    @abstractmethod
    def __init__(
        self,
        xuid: int,
        name: str,
        container: bool = False,
        itidx1: int = 0,
        itidx2: int = 0,
        inherits: tuple[EndPointTypeABC, ...] = NULL_TUPLE,
        imports: tuple[ImportDef, ...] = NULL_TUPLE,
        children: tuple[EndPointTypeABC, ...] = NULL_TUPLE,
    ) -> None:
        """Initialize the End Point Type."""

    @property
    @abstractmethod
    def children(self) -> tuple[EndPointTypeABC, ...]:
        """Return the tuple of child types."""

    @children.setter
    @abstractmethod
    def children(self, children: tuple[EndPointTypeABC, ...]) -> None:
        """Set the tuple of child types."""

    @property
    @abstractmethod
    def container(self) -> bool:
        """Return True if the type is a container (else is is a scalar)."""

    @container.setter
    @abstractmethod
    def container(self, container: bool) -> None:
        """Set the container flag."""

    @property
    @abstractmethod
    def imports(self) -> tuple[ImportDef, ...]:
        """Return the tuple of imports."""

    @imports.setter
    @abstractmethod
    def imports(self, imports: tuple[ImportDef, ...]) -> None:
        """Set the tuple of imports."""

    @property
    @abstractmethod
    def inherits(self) -> tuple[EndPointTypeABC, ...]:
        """Return the tuple of inherited types."""

    @inherits.setter
    @abstractmethod
    def inherits(self, inherits: tuple[EndPointTypeABC, ...]) -> None:
        """Set the tuple of inherited types."""

    @property
    @abstractmethod
    def itidx1(self) -> int:
        """Return the first index of the type."""

    @itidx1.setter
    @abstractmethod
    def itidx1(self, itidx1: int) -> None:
        """Set the first index of the type."""

    @property
    @abstractmethod
    def itidx2(self) -> int:
        """Return the second index of the type."""

    @itidx2.setter
    @abstractmethod
    def itidx2(self, itidx2: int) -> None:
        """Set the second index of the type."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the type."""

    @name.setter
    @abstractmethod
    def name(self, name: str) -> None:
        """Set the name of the type."""

    @property
    @abstractmethod
    def uid(self) -> int:
        """Return the unique identifier for the type."""

    @uid.setter
    @abstractmethod
    def uid(self, uid: int) -> None:
        """Set the unique identifier for the type."""

    @property
    @abstractmethod
    def xuid(self) -> int:
        """Return the C/SUID for the type."""

    @xuid.setter
    @abstractmethod
    def xuid(self, xuid: int) -> None:
        """Set the C/SUID for the type."""
