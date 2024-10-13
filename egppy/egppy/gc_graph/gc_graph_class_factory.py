"""Builtin graph classes for the GC graph."""

from __future__ import annotations

from typing import Any

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.connections.connections_abc import ConnectionsABC
from egppy.gc_graph.connections.connections_class_factory import (
    EMPTY_CONNECTIONS,
    ListConnections,
    TupleConnections,
)
from egppy.gc_graph.end_point.end_point import EndPoint
from egppy.gc_graph.gc_graph_abc import GCGraphABC
from egppy.gc_graph.gc_graph_mixin import GCGraphMixin, key2parts
from egppy.gc_graph.interface.interface_abc import InterfaceABC
from egppy.gc_graph.interface.interface_class_factory import (
    EMPTY_INTERFACE,
    ListInterface,
    TupleInterface,
)
from egppy.gc_graph.typing import ROW_CLS_INDEXED

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Empty GC Graph templates
_EMPTY_INTERFACES: dict[str, InterfaceABC] = {r: EMPTY_INTERFACE for r in ROW_CLS_INDEXED}
_EMPTY_CONNECTIONS: dict[str, ConnectionsABC] = {
    r + "c": EMPTY_CONNECTIONS for r in ROW_CLS_INDEXED
}


class FrozenGCGraph(GCGraphMixin, GCGraphABC):
    """Builtin graph class for the GC graph.

    Frozen graphs are created once and then never modified.
    """

    _TI: type[InterfaceABC] = TupleInterface
    _TC: type[ConnectionsABC] = TupleConnections

    def __init__(self, gc_graph: dict[str, list[list[Any]]] | GCGraphABC) -> None:
        """Initialize the GC graph.
        Construct the internal representation of the graph from the JSON graph.
        """
        self._interfaces: dict[str, InterfaceABC] = _EMPTY_INTERFACES.copy()
        self._connections: dict[str, ConnectionsABC] = _EMPTY_CONNECTIONS.copy()
        self._dirty_ics: set[str] = set()  # Interface and connection keys
        self._lock = False  # Modifiable during initialization

        # Call the mixin constructor & run the sanity checks
        super().__init__(gc_graph)
        self._lock = True

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        if self._lock:
            raise RuntimeError("Cannot modify a static graph.")
        elif (keylen := len(key)) == 2:  # Its an interface
            self._interfaces[key] = EMPTY_INTERFACE
            self._dirty_ics.add(key)
        elif keylen == 3:  # Its connections
            self._connections[key] = EMPTY_CONNECTIONS
            self._dirty_ics.add(key)
        elif keylen == 5:  # Its an endpoint
            iface = self._interfaces[ikey := key[0] + key[4]]
            conns = self._connections[ckey := ikey + "c"]
            i = -1 if key[2] == "-" else int(key[1:4])  # pop!
            del iface[i], conns[i]
            self._dirty_ics.add(ikey)
            self._dirty_ics.add(ckey)
        else:
            raise KeyError(f"Invalid GC Graph key: {key}")
        self.dirty()

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal."""
        if isinstance(other, FrozenGCGraph):
            if self._TI == other._TI and self._TC == other._TC:
                return (
                    self._interfaces == other._interfaces
                    and self._connections == other._connections
                )
            equal = True
            for key in ROW_CLS_INDEXED:
                oiface = other._interfaces[key]
                oconns = other._connections[key + "c"]
                equal &= self._interfaces[key] == (
                    oiface if oiface is EMPTY_INTERFACE else self._TI(oiface)
                )
                equal &= self._connections[key + "c"] == (
                    oconns if oconns is EMPTY_CONNECTIONS else self._TC(oconns)
                )
                if not equal:
                    return False
            return True
        return False

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        if (keylen := len(key)) == 2:  # Its an interface
            iface = self._interfaces.get(key, EMPTY_INTERFACE)
            if iface is EMPTY_INTERFACE:
                raise KeyError(f"Interface {key} does not exist.")
            self.touch()
            return iface
        if keylen == 3:  # Its connections
            conns = self._connections.get(key, EMPTY_CONNECTIONS)
            if conns is EMPTY_CONNECTIONS:
                raise KeyError(f"Connections {key} does not exist.")
            self.touch()
            return conns
        if keylen == 5:  # Its an endpoint
            iface = self._interfaces.get(ikey := key[0] + key[4], EMPTY_INTERFACE)
            if iface is EMPTY_INTERFACE:
                raise KeyError(f"Endpoint {key} does not exist.")
            conns = self._connections.get(ikey + "c", EMPTY_CONNECTIONS)
            assert (
                conns is not EMPTY_CONNECTIONS
            ), f"Connections {key} does not exist when interface does."
            k, i, c = key2parts(key)
            self.touch()
            return EndPoint(k, i, iface[i], c, conns[i])
        raise KeyError(f"Invalid GC Graph key: {key}")

    def __len__(self) -> int:
        """Return the total number of endpoints."""
        return sum(len(self._interfaces[key]) for key in ROW_CLS_INDEXED)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key to the given value."""
        if self._lock:
            raise RuntimeError("Cannot modify a static graph.")
        if (keylen := len(key)) == 2:  # Its an interface
            if value is EMPTY_INTERFACE:
                self._interfaces[key] = EMPTY_INTERFACE
            else:
                self._interfaces[key] = value if isinstance(value, self._TI) else self._TI(value)
            self._dirty_ics.add(key)
        elif keylen == 3:  # Its connections
            if value is EMPTY_CONNECTIONS:
                self._connections[key] = EMPTY_CONNECTIONS
            else:
                self._connections[key] = value if isinstance(value, self._TC) else self._TC(value)
            self._dirty_ics.add(key)
        elif keylen == 5:  # Its an endpoint
            iface = self._interfaces[ikey := key[0] + key[4]]
            conns = self._connections[ckey := ikey + "c"]
            assert isinstance(value, EndPoint), "Value must be an EndPoint."
            if key[1] == "+":
                iface.append(value.get_typ())
                conns.append(value.get_refs())
            else:
                _, i, _ = key2parts(key)
                iface[i] = value.get_typ()
                conns[i] = value.get_refs()
            self._dirty_ics.add(ikey)
            self._dirty_ics.add(ckey)
        else:
            raise KeyError(f"Invalid GC Graph key: {key}")
        self.dirty()

    def clean(self) -> None:
        """Clean the GC Graph."""
        self._dirty_ics.clear()
        super().clean()

    def conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return self._interfaces["Fd"] is not EMPTY_INTERFACE

    def modified(self) -> tuple[str | int, ...] | bool:
        """Return the modification status of the GC Graph."""
        return tuple(self._dirty_ics)


class MutableGCGraph(FrozenGCGraph):
    """Mutable graph class for the GC graph."""

    _TI: type = ListInterface
    _TC: type = ListConnections

    def __init__(self, gc_graph: dict[str, list[list[Any]]] | GCGraphABC) -> None:
        """Initialize the GC graph."""
        super().__init__(gc_graph)
        self._lock = False


# The empty graph
EMPTY_GC_GRAPH = FrozenGCGraph({})
