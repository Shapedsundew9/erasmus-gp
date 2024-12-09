"""The End Point Type Class."""

from __future__ import annotations

from egpcommon.common import NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.import_def import ImportDef

from egppy.gc_graph.end_point.end_point_type_abc import EndPointTypeABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# End Point Type UID Bitfield Constants
CUID_LSB: int = 0
CUID_WIDTH: int = 13
CUID_MASK: int = ((1 << CUID_WIDTH) - 1) << CUID_LSB
CUID_MAX: int = (1 << CUID_WIDTH) - 1

SUID_LSB: int = 0
SUID_WIDTH: int = 16
SUID_MASK: int = ((1 << SUID_WIDTH) - 1) << SUID_LSB
SUID_MAX: int = (1 << SUID_WIDTH) - 1

CONTAINER_POS: int = 31
CONTAINER_MASK: int = 1 << CONTAINER_POS

ITIDX1_POS: int = 23
ITIDX1_WIDTH: int = 6
ITIDX1_MASK: int = ((1 << ITIDX1_WIDTH) - 1) << ITIDX1_POS
ITIDX1_MAX: int = (1 << ITIDX1_WIDTH) - 1

ITIDX2_POS: int = 15
ITIDX2_WIDTH: int = 6
ITIDX2_MASK: int = ((1 << ITIDX2_WIDTH) - 1) << ITIDX2_POS
ITIDX2_MAX: int = (1 << ITIDX2_WIDTH) - 1

C_RESERVED_MASK: int = ~(CUID_MASK | CONTAINER_MASK | ITIDX1_MASK | ITIDX2_MASK)
S_RESERVED_MASK: int = ~(SUID_MASK | CONTAINER_MASK)


class EndPointType(EndPointTypeABC):
    """End Point Type class.

    The End Point Type class is a concrete implementation of the End Point Type Abstract Base Class.
    It is used to define types
    """

    def __init__(
        self,
        xuid: int,
        name: str,
        container: bool = False,
        inherits: tuple[EndPointTypeABC, ...] = NULL_TUPLE,
        imports: tuple[ImportDef, ...] = NULL_TUPLE,
        children: tuple[EndPointTypeABC, ...] = NULL_TUPLE,
    ) -> None:
        """Initialize the End Point Type."""
        self._uid: int = -(2**CONTAINER_POS) if container else 0
        self._uid += xuid
        self._name: str = name
        self._container: bool = container
        self._inherits: tuple[EndPointTypeABC, ...] = inherits
        self._imports: tuple[ImportDef, ...] = imports
        self._children: tuple[EndPointTypeABC, ...] = children
        if _LOG_VERIFY:
            self.verify()

    @property
    def children(self) -> tuple[EndPointTypeABC, ...]:
        """Return the tuple of child types."""
        return self._children

    @children.setter
    def children(self, children: tuple[EndPointTypeABC, ...]) -> None:
        """Set the tuple of child types."""
        self._children = children

    @property
    def container(self) -> bool:
        """Return True if the type is a container (else is is a scalar)."""
        return bool(self._uid & CONTAINER_MASK)

    @container.setter
    def container(self, container: bool) -> None:
        """Set the container flag."""
        self._uid = self._uid | CONTAINER_MASK if container else self._uid & ~CONTAINER_MASK

    @property
    def imports(self) -> tuple[ImportDef, ...]:
        """Return the tuple of imports."""
        return self._imports

    @imports.setter
    def imports(self, imports: tuple[ImportDef, ...]) -> None:
        """Set the tuple of imports."""
        self._imports = imports

    @property
    def inherits(self) -> tuple[EndPointTypeABC, ...]:
        """Return the tuple of inherited types."""
        return self._inherits

    @inherits.setter
    def inherits(self, inherits: tuple[EndPointTypeABC, ...]) -> None:
        """Set the tuple of inherited types."""
        self._inherits = inherits

    @property
    def name(self) -> str:
        """Return the name of the type."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the type."""
        self._name = name

    @property
    def uid(self) -> int:
        """Return the unique identifier of the type."""
        return self._uid

    @uid.setter
    def uid(self, uid: int) -> None:
        """Set the unique identifier of the type."""
        self._uid = uid

    @property
    def xuid(self) -> int:
        """Return the unique identifier of the type."""
        return self._uid & CUID_MASK if self.container else self._uid & SUID_MASK

    @xuid.setter
    def xuid(self, xuid: int) -> None:
        """Set the unique identifier of the type."""
        self._uid = (
            (self._uid & ~CUID_MASK) | xuid if self.container else (self._uid & ~SUID_MASK) | xuid
        )

    def __repr__(self) -> str:
        """Return the string representation of the object."""
        return f"EndPointType(uid={self._uid}, name={self.name})"

    def __str__(self) -> str:
        """Return the string representation of the object."""
        return self.name

    def add_inherits(self, inherits: tuple[EndPointTypeABC, ...] | EndPointTypeABC) -> None:
        """Add the inherited types to the existing tuple."""
        if isinstance(inherits, EndPointTypeABC):
            self.inherits = self.inherits + (inherits,)
            return
        if isinstance(inherits, tuple):
            self.inherits = self.inherits + inherits
        assert (
            False
        ), f"Invalid inherits type: {type(inherits)} was \
            expecting tuple[EndPointTypeABC, ...] or EndPointTypeABC"

    def add_imports(self, imports: tuple[ImportDef, ...] | ImportDef) -> None:
        """Add the imports to the existing tuple."""
        if isinstance(imports, ImportDef):
            self.imports = self.imports + (imports,)
            return
        if isinstance(imports, tuple):
            self.imports = self.imports + imports
        assert (
            False
        ), f"Invalid imports type: {type(imports)} was \
            expecting tuple[ImportDef] or ImportDef"

    def add_children(self, children: tuple[EndPointTypeABC, ...] | EndPointTypeABC) -> None:
        """Add the children to the existing tuple."""
        if isinstance(children, EndPointTypeABC):
            self.children = self.children + (children,)
            return
        if isinstance(children, tuple):
            self.children = self.children + children
        assert (
            False
        ), f"Invalid children type: {type(children)} was \
            expecting tuple[EndPointTypeABC, ...] or EndPointTypeABC"

    def verify(self) -> None:
        """Verify the object."""
        assert isinstance(self._uid, int), f"Invalid uid type: {type(self._uid)}"
        assert isinstance(self._name, str), f"Invalid name type: {type(self._name)}"
        assert isinstance(self._container, bool), f"Invalid container type: {type(self._container)}"
        assert isinstance(self._inherits, tuple), f"Invalid inherits type: {type(self._inherits)}"
        assert isinstance(self._imports, tuple), f"Invalid imports type: {type(self._imports)}"
        assert isinstance(self._children, tuple), f"Invalid children type: {type(self._children)}"
        assert self.uid >= -(1 << CONTAINER_POS), f"Invalid uid value: {self.uid}"
        assert self.uid <= SUID_MAX, f"Invalid uid value: {self.uid}"
        assert self.name, "Invalid name value: {self.name}"
        if _LOG_CONSISTENCY:
            self.consistency()
