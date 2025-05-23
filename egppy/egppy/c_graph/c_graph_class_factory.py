"""
Builtin graph classes for the Connection Graph.

This module provides classes for creating and managing Connection Graphs,
which are used to represent
graph structures in the GC system. The module includes both frozen (immutable) and mutable
graph classes, allowing for different use cases where graphs need to be either static or
modifiable.

Classes:
    FrozenCGraph: Represents an immutable Connection Graph that cannot be modified after creation.
    MutableCGraph: Represents a mutable Connection Graph that can be modified after creation.

Usage:
    - Use FrozenCGraph when you need a static graph that should not change.
    - Use MutableCGraph when you need a graph that can be modified dynamically.

Example:
    frozen_graph = FrozenCGraph(c_graph_data)
    mutable_graph = MutableCGraph(c_graph_data)
"""

from __future__ import annotations

from random import choice, shuffle
from typing import Any, Callable, MutableSequence

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.connections.connections_abc import ConnectionsABC
from egppy.c_graph.connections.connections_class_factory import (
    NULL_CONNECTIONS,
    ListConnections,
    TupleConnections,
)
from egppy.c_graph.end_point.end_point import DstEndPointRef, EndPoint, SrcEndPointRef
from egppy.c_graph.c_graph_abc import CGraphABC
from egppy.c_graph.c_graph_mixin import CGraphDict, CGraphMixin, key2parts
from egppy.c_graph.interface import (
    NULL_INTERFACE,
    Interface,
    interface,
    mutable_interface,
)
from egppy.c_graph.c_graph_constants import ROW_CLS_INDEXED, DstRow, EPClsPostfix, SrcRow

# Standard EGP logging pattern
# This pattern involves creating a logger instance using the egp_logger function,
# and setting up boolean flags to check if certain logging levels (DEBUG, VERIFY, CONSISTENCY)
# are enabled. This allows for conditional logging based on the configured log level.
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
DST_CONN_POSTFIX: str = EPClsPostfix.DST + "c"

# Constants
_DST_CONN_POSTFIX: str = EPClsPostfix.DST + "c"
SRC_CONN_POSTFIX: str = EPClsPostfix.SRC + "c"


# Empty Connection Graph templates
_NULL_INTERFACES: dict[str, Interface] = {r: NULL_INTERFACE for r in ROW_CLS_INDEXED}
_NULL_CONNECTIONS: dict[str, ConnectionsABC] = {r + "c": NULL_CONNECTIONS for r in ROW_CLS_INDEXED}


class FrozenCGraph(CGraphMixin, CGraphABC):
    """Builtin graph class for the Connection Graph.

    Frozen graphs are created once and then never modified.
    """

    _TI: Callable = lambda _, y: interface(y)
    _TC: type[ConnectionsABC] = TupleConnections

    def __init__(self, c_graph: CGraphDict | CGraphABC) -> None:
        """Initialize the Connection Graph.
        Construct the internal representation of the graph from the JSON graph.
        """
        self._interfaces: dict[str, Interface] = _NULL_INTERFACES.copy()
        self._connections: dict[str, ConnectionsABC] = _NULL_CONNECTIONS.copy()
        self._dirty_ics: set[str] = set()  # Interface and connection keys
        self._lock = False  # Modifiable during initialization

        # Call the mixin constructor & run the sanity checks
        super().__init__(c_graph)
        self._lock = True

    def __delitem__(self, key: str) -> None:
        """Delete the endpoint with the given key."""
        if self._lock:
            raise RuntimeError("Cannot modify a static graph.")
        keylen = len(key)
        if keylen == 2:
            self._delete_interface(key)
        elif keylen == 3:
            self._delete_connections(key)
        elif keylen == 5:
            self._delete_endpoint(key)
        else:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        self.dirty()

    def _delete_interface(self, key: str) -> None:
        """Delete an interface."""
        self._interfaces[key] = NULL_INTERFACE
        self._dirty_ics.add(key)

    def _delete_connections(self, key: str) -> None:
        """Delete connections."""
        self._connections[key] = NULL_CONNECTIONS
        self._dirty_ics.add(key)

    def _delete_endpoint(self, key: str) -> None:
        """Delete an endpoint."""
        ikey = key[0] + key[4]
        ckey = ikey + "c"
        iface = self._interfaces[ikey]
        conns = self._connections[ckey]
        # Determine the index of the endpoint to delete. If key[2] is '-',
        # use -1 (pop the last element).
        # Otherwise, convert the substring key[1:4] to an integer index.
        i = -1 if key[2] == "-" else int(key[1:4])
        assert isinstance(iface, MutableSequence), "Interface must be mutable."
        del iface[i], conns[i]
        self._dirty_ics.add(ikey)
        self._dirty_ics.add(ckey)

    def __getitem__(self, key: str) -> Any:
        """Get the endpoint with the given key."""
        if (keylen := len(key)) == 2:  # Its an interface
            self.touch()
            return self._interfaces.get(key, NULL_INTERFACE)
        if keylen == 3:  # Its connections
            self.touch()
            return self._connections.get(key, NULL_CONNECTIONS)
        if keylen == 5:  # Its an endpoint
            iface = self._interfaces.get(ikey := key[0] + key[4], NULL_INTERFACE)
            if iface is NULL_INTERFACE:
                raise KeyError(f"Endpoint {key} does not exist.")
            conns = self._connections.get(ikey + "c", NULL_CONNECTIONS)
            assert (
                conns is not NULL_CONNECTIONS
            ), f"Connections {key} does not exist when interface does."
            k, i, c = key2parts(key)
            self.touch()
            return EndPoint(k, i, iface[i], c, conns[i])
        raise KeyError(f"Invalid Connection Graph key: {key}")

    def __len__(self) -> int:
        """Return the total number of endpoints."""
        return sum(len(self._interfaces[key]) for key in ROW_CLS_INDEXED)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the endpoint with the given key to the given value."""
        if self._lock:
            raise RuntimeError("Cannot modify a static graph.")
        if (keylen := len(key)) == 2:  # Its an interface
            self._interfaces[key] = value
            self._dirty_ics.add(key)
        elif keylen == 3:  # Its connections
            self._connections[key] = value
            self._dirty_ics.add(key)
        elif keylen == 5:  # Its an endpoint
            iface = self._interfaces[ikey := key[0] + key[4]]
            conns = self._connections[ckey := ikey + "c"]
            assert isinstance(value, EndPoint), "Value must be an EndPoint."
            assert isinstance(iface, MutableSequence), "Interface must be mutable."
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
            raise KeyError(f"Invalid Connection Graph key: {key}")
        self.dirty()

    def clean(self) -> None:
        """Clean the Connection Graph."""
        self._dirty_ics.clear()
        super().clean()

    def is_conditional_graph(self) -> bool:
        """Return True if the graph is conditional i.e. has row F."""
        return self._interfaces["Fd"] is not NULL_INTERFACE

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable, i.e. all destinations are connected."""
        return not (
            self._connections["Fdc"].has_unconnected_eps()
            or self._connections["Adc"].has_unconnected_eps()
            or self._connections["Bdc"].has_unconnected_eps()
            or self._connections["Odc"].has_unconnected_eps()
        )

    def modified(self) -> tuple[str | int, ...] | bool:
        """Return the modification status of the Connection Graph."""
        return tuple(self._dirty_ics)

    def stabilize(self, fixed_interface: bool = True) -> CGraphABC:
        """Frozen graphs cannot change so just return self."""
        return self


class MutableCGraph(FrozenCGraph):
    """Mutable graph class for the Connection Graph."""

    _TI: Callable = lambda _, y: mutable_interface(y)
    _TC: type = ListConnections

    def __init__(self, c_graph: CGraphDict | CGraphABC) -> None:
        """Initialize the Connection Graph."""
        super().__init__(c_graph)
        self._lock = False

    def connect_all(self, fixed_interface: bool = True) -> None:
        """Connect all the unconnected destination endpoints in the Connection Graph."""
        # Make a list of unconnected endpoints and shuffle it
        unconnected: list[tuple[DstRow, int]] = (
            [(DstRow.F, idx) for idx in self._connections["Fdc"].get_unconnected_idx()]
            + [(DstRow.A, idx) for idx in self._connections["Adc"].get_unconnected_idx()]
            + [(DstRow.B, idx) for idx in self._connections["Bdc"].get_unconnected_idx()]
            + [(DstRow.O, idx) for idx in self._connections["Odc"].get_unconnected_idx()]
        )
        shuffle(unconnected)

        # Connect the unconnected endpoints in a random order
        rtype = self._TC.get_ref_iterable_type()
        for drow, didx in unconnected:
            typ = self._interfaces[drow + EPClsPostfix.DST][didx]
            # Find the valid sources for the destination row and endpoint type
            vsrcs = self.valid_srcs(drow, typ)
            # If the interface of the GC is not fixed (i.e. it is not an empty GC) then
            # a new input interface endpoint is an option.
            len_is = len(self._interfaces["Is"])
            if not fixed_interface:
                vsrcs.append((SrcRow.I, len_is))
            if vsrcs:
                # Randomly choose a valid source endpoint
                srow, sidx = choice(vsrcs)
                # If it is a new input interface endpoint then add it to input interface
                if not fixed_interface and sidx == len_is and srow == SrcRow.I:
                    assert isinstance(
                        self._interfaces["Is"], MutableSequence
                    ), "Interface must be mutable."
                    self._interfaces["Is"].append(typ)
                    self._connections["Isc"].append(rtype())
                self._connections[drow + DST_CONN_POSTFIX][didx].append(SrcEndPointRef(srow, sidx))
                self._connections[drow + _DST_CONN_POSTFIX][didx].append(SrcEndPointRef(srow, sidx))
                self._connections[srow + SRC_CONN_POSTFIX][sidx].append(DstEndPointRef(drow, didx))

    def stabilize(self, fixed_interface: bool = True) -> CGraphABC:
        """Stablization involves making all the mandatory connections and
        connecting all the remaining unconnected destination endpoints.
        Destinations are connected to sources in a random order.
        Stabilization is not guaranteed to be successful.
        """
        missing_connections = self.check_required_connections()
        for _ in missing_connections:
            ### TO HERE:
            ### Need to try and make the missing mandatory connections
            ### if we cannot then we know what steady state exceptions to raise and
            ### what the criteria are for a successful stabilization.
            ### NEED TO THINK ABOUT RETURN TYPE!!!!
            pass

        # Connect any remaining unconnected destination endpoints
        self.connect_all(fixed_interface)

        # FIXME: This is a temporary solution to avoid the linting error distraction
        return self


# The empty graph
# NOTE: pylint is spuriously saying that the inherited CacheableObjMixin methods
# are not implemented. This is incorrect as they are implemented in the mixin.
# pylance seems able to figure this out.
NULL_c_graph = FrozenCGraph({})
