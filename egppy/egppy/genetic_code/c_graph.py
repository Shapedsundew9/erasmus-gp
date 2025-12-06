"""The mutable Connection Graph (CGraph) class implementation."""

from __future__ import annotations

from itertools import chain

from egpcommon.common_obj import CommonObj
from egpcommon.egp_log import VERIFY, Logger, egp_logger
from egpcommon.egp_rnd_gen import EGPRndGen, egp_rng
from egppy.genetic_code.c_graph_abc import CGraphABC, FrozenCGraphABC
from egppy.genetic_code.c_graph_constants import (
    _UNDER_DST_KEY_DICT,
    _UNDER_KEY_DICT,
    _UNDER_ROW_DST_INDEXED,
    _UNDER_SRC_KEY_DICT,
    IMPLY_P_IFKEYS,
    ROW_CLS_INDEXED_ORDERED,
    ROW_CLS_INDEXED_SET,
    DstIfKey,
    DstRow,
    EPCls,
    IfKey,
    SrcIfKey,
    SrcRow,
)
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.endpoint_abc import EndPointABC, EndpointMemberType
from egppy.genetic_code.frozen_c_graph import FrozenCGraph
from egppy.genetic_code.interface import Interface, InterfaceABC
from egppy.genetic_code.interface_abc import FrozenInterfaceABC
from egppy.genetic_code.json_cgraph import c_graph_type, valid_src_rows
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class CGraph(FrozenCGraph, CGraphABC):
    """Mutable CGraph class."""

    # Inherit slots from FrozenCGraph
    __slots__ = ()

    def __init__(  # pylint: disable=super-init-not-called
        self,
        graph: (
            dict[str, list[EndpointMemberType]] | dict[IfKey, FrozenInterfaceABC] | FrozenCGraphABC
        ),
    ) -> None:
        """Initialize the Connection Graph.

        A full copy of all data is made from the provided graph to ensure independence.
        """
        # Initialize CommonObj directly, skipping FrozenCGraph.__init__
        CommonObj.__init__(self)  # pylint: disable=non-parent-init-called

        # Set all interfaces from the provided graph.
        # Note that this is a mutable instance so a full copy of the initializing
        # interfaces are needed (but the graph may not be stable nor valid).
        # In the implementation there is a member slot for every possible interface
        # with the two character interface name preceded by an underscore (e.g. _Is,
        # _Fd, _Ad, etc.). The python object None is used to indicate that an interface
        # does not exist in this graph.
        assert (
            any(key in graph for key in ROW_CLS_INDEXED_SET) and graph
        ), "Input graph not empty but contains no valid interface keys."
        for key in ROW_CLS_INDEXED_ORDERED:
            _key = _UNDER_KEY_DICT[key]
            if key in graph:
                iface = Interface(graph[key])
                assert isinstance(
                    iface, (InterfaceABC, type(None))
                ), f"Invalid interface definition for {key}: {iface}"
                setattr(self, _key, iface)
            elif key in (SrcIfKey.IS, DstIfKey.OD):
                # Is and Od must exist even if empty
                setattr(self, _key, [])  # Empty interface
            else:
                setattr(self, _key, None)

        # Special cases for JSONCGraphs
        # Ensure PD exists if LD, WD, or FD exist and OD is empty
        need_p = any(getattr(self, _UNDER_KEY_DICT[key]) is not None for key in IMPLY_P_IFKEYS)
        if need_p and len(getattr(self, _UNDER_KEY_DICT[DstIfKey.OD])) == 0:
            setattr(self, _UNDER_KEY_DICT[DstIfKey.PD], [])

    def __delitem__(self, key: IfKey) -> None:
        """Delete the interface with the given key."""
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        setattr(self, _UNDER_KEY_DICT[key], None)

    def __hash__(self) -> int:
        """Return the hash of the Connection Graph.
        NOTE: All CGraphABC with the same state must return the same hash value.
        """
        return hash(tuple(hash(iface) for iface in self.values()))

    def __setitem__(self, key: IfKey, value: FrozenInterfaceABC) -> None:
        """Set the interface with the given key."""
        if key not in ROW_CLS_INDEXED_SET:
            raise KeyError(f"Invalid Connection Graph key: {key}")
        if not isinstance(value, FrozenInterfaceABC):
            raise TypeError(f"Value must be an Interface, got {type(value)}")

        # Convert to mutable Interface if it's not already
        if not isinstance(value, InterfaceABC):
            value = Interface(value)

        setattr(self, _UNDER_KEY_DICT[key], value)

    def connect(self, src_row: SrcRow, src_idx: int, dst_row: DstRow, dst_idx: int) -> None:
        """Connect a source endpoint to a destination endpoint.
        Establishes a directed connection from the specified source endpoint
        to the specified destination endpoint updating both endpoints accordingly.
        NOTE: If there is an existing connection to the destination endpoint
        it will be replaced.
        Args:
            src_row: Row identifier of the source interface.
            src_idx: Index of the source endpoint within its interface.
            dst_row: Row identifier of the destination interface.
            dst_idx: Index of the destination endpoint within its interface.
        Raises:
            RuntimeError: If the graph is frozen.
            KeyError: If the specified interfaces do not exist.
            IndexError: If the specified endpoint indices are out of range.
        """
        dst_iface: Interface | None = getattr(self, _UNDER_DST_KEY_DICT[dst_row], None)
        if dst_iface is None:
            raise KeyError(f"Destination interface {dst_row}d does not exist in the graph.")
        src_iface: Interface | None = getattr(self, _UNDER_SRC_KEY_DICT[src_row], None)
        if src_iface is None:
            raise KeyError(f"Source interface {src_row}s does not exist in the graph.")
        dst_ep: EndPointABC = dst_iface[dst_idx]
        src_ep: EndPointABC = src_iface[src_idx]
        dst_ep.connect(src_ep)
        src_ep.connect(dst_ep)

    def connect_all(self, if_locked: bool = True, rng: EGPRndGen = egp_rng) -> None:
        """
        Connect all unconnected destination endpoints in the Connection Graph to randomly
        selected valid source endpoints.

        This method iterates through all unconnected destination endpoints in the graph and randomly
        connects each to a valid source endpoint. The validity of source endpoints is determined by
        the graph type's structural rules.

        Args:
            if_locked (bool): If True, prevents the creation of new input interface endpoints.
                If False, allows extending the input interface ('I') with new endpoints when needed
                and when 'I' is a valid source row for the destination. Defaults to True.
            seed (int | None): Seed for the random number generator to ensure reproducibility.

        Returns:
            None: Modifies the graph in-place by establishing connections between endpoints.

        Process:
            1. Collects all unconnected destination endpoints from all destination interfaces
            2. Shuffles them to ensure random connection order
            3. For each unconnected destination endpoint:
                - Identifies valid source rows based on graph type rules
                - Finds all source endpoints matching the destination's type
                - If if_locked is False and 'I' is a valid source, may create a new input endpoint
                - Randomly selects and connects to a valid source endpoint
                - Creates new input interface endpoint if selected and not locked

        Note:
            - Source endpoint selection respects type compatibility (sep.typ == dep.typ)
            - Graph type rules define which source rows can connect to which destination rows
            - New input interface endpoints are only added when if_locked=False
            and structurally valid
        """
        # Make a list of unconnected endpoints and shuffle it
        ifaces = (getattr(self, key) for key in _UNDER_ROW_DST_INDEXED)
        unconnected: list[EndPoint] = list(
            chain.from_iterable(iface.unconnected_eps() for iface in ifaces if iface is not None)
        )
        rng.shuffle(unconnected)  # type: ignore

        # Connect the unconnected endpoints in a random order
        # First find the set of valid source rows for this graph type.
        vsrc_rows = valid_src_rows(c_graph_type(self))
        i_iface: Interface = getattr(self, "_Is")
        for dep in unconnected:
            # Gather all the viable source interfaces for this destination endpoint.
            valid_src_rows_for_dst = vsrc_rows[DstRow(dep.row)]
            _vifs = (getattr(self, _UNDER_SRC_KEY_DICT[row]) for row in valid_src_rows_for_dst)
            vifs = (vif for vif in _vifs if vif is not None)
            # Gather all the source endpoints that are compatible with the destination endpoint.
            vsrcs = [
                sep for vif in vifs for sep in vif if dep.typ in types_def_store.ancestors(sep.typ)
            ]
            # If the interface of the GC is not fixed (i.e. it is not an empty GC) then
            # a new input interface endpoint is an option, BUT only if I is a valid source
            # for this destination row according to the graph type rules.
            len_is = len(i_iface)
            if not if_locked and SrcRow.I in valid_src_rows_for_dst:
                # Add a new input interface endpoint as a valid source option regardless of whether
                # there are other valid source endpoints. This prevents the sub-GC interfaces from
                # being completely dependent on each other if their types match. Sub-GC interfaces
                # that are not connected to each other at all result in a GC called a _harmony_.
                vsrcs.append(EndPoint(SrcRow.I, len_is, EPCls.SRC, dep.typ, []))
            if vsrcs:
                # Randomly choose a valid source endpoint
                sep: EndPoint = egp_rng.choice(vsrcs)
                # If it is a new input interface endpoint then add it to input interface
                if not if_locked and sep.idx == len_is and sep.row == SrcRow.I:
                    i_iface.endpoints.append(sep)
                # Connect the destination endpoint to the source endpoint
                dep.connect(sep)

    def is_stable(self) -> bool:
        """Return True if the Connection Graph is stable, i.e. all destinations are connected."""
        difs = (getattr(self, key) for key in _UNDER_ROW_DST_INDEXED)
        return all(not iface.unconnected_eps() for iface in difs if iface is not None)

    def stabilize(self, if_locked: bool = True, rng: EGPRndGen = egp_rng) -> None:
        """Stablization involves making all the mandatory connections and
        connecting all the remaining unconnected destination endpoints.
        Destinations are connected to sources in a random order.
        Stabilization is not guaranteed to be successful unless if_locked is False
        in which case unconnected destinations create new source endpoints in the
        input interface as needed.

        After stabilization, check is_stable() to determine if all destinations
        were successfully connected.
        """
        self.connect_all(if_locked, rng)
        if _logger.isEnabledFor(level=VERIFY):
            self.verify()
