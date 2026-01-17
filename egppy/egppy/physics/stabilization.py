"""Stabilization routines for EGCode to GGCode conversion.

Stabilization is the procedure that makes a genetic code (Cgraph) fully connected
and capable of generating executable code. There are two main ways this happens:

- **Intended Mutation (Directed Stabilization)**: This uses available PGCs (connectivity
    and matching functionalities) to execute the stabilization in a controlled, directed manner.
- **Default Process (Physics of Erasmus)**: This is the automatic, default process. When
    a mutated genetic code (EG code) attempts to convert into a general genetic code (GG code),
    it must be stable. If it is not, a stabilization process begins. An unstable code is never
    converted to a general genetic code and is considered "stillborn."

The default physical stabilization process is known as Static Full Stack Stabilization.

- **Static**: It operates in escalating stages. After each stage, a check determines stability.
    If stable, the process stops; otherwise, it proceeds to the next stage.
- **Iterative**: The process can restart, but only up to a fixed number of times before failing
    and giving up on all functionalities.

In contrast, a Dynamic Stabilizer randomly selects a stabilization method to start, resulting
in non-deterministic behavior.
"""

from enum import IntEnum
from functools import partial
from typing import Callable

from egpcommon.egp_log import GC_DEBUG, INFO, TRACE, Logger, egp_logger
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.endpoint_abc import EndPointABC
from egppy.genetic_code.genetic_code import GCABC
from egppy.physics.helpers import inherit_members
from egppy.physics.pgc_api import EGCode, GGCode
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)

# Constants
MAX_ATTEMPTS = 8

# The priority sequence for local direct connections
LDC_SEQ = (
    (SrcIfKey.IS, DstIfKey.AD),
    (SrcIfKey.AS, DstIfKey.BD),
    (SrcIfKey.BS, DstIfKey.OD),
)


# Direct Connection Types
class ConnectionType(IntEnum):
    """Types of connections.

    MATCHING: Connection where source and destination types match or are upcastable.
    DOWNCAST: Connection requiring downcasting of source type.
    """

    MATCHING = 0
    DOWNCAST = 1


class StabilizationError(Exception):
    """Raised when stabilization fails."""


def local_direct_connect(_: RuntimeContext, egc: EGCode, ct: ConnectionType) -> bool:
    """Attempt direct connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Direct connections are only made Input -> GCA, GCA -> GCB and GCB -> Output

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
        ct: The type of direct connection to attempt (MATCHING or DOWNCAST).
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    _logger.log(TRACE, "Attempting local direct connect with ct=%s", ct.name)
    cgraph = egc["cgraph"]
    assert isinstance(cgraph, CGraph), "EGCode cgraph is not a CGraph"
    for src_if, dst_if in LDC_SEQ:
        for src_ep, dst_ep in zip(cgraph[src_if], cgraph[dst_if]):
            assert isinstance(src_ep, EndPointABC), "Source endpoint is not an EndPointABC"
            assert isinstance(dst_ep, EndPointABC), "Destination endpoint is not an EndPointABC"
            if ct == ConnectionType.MATCHING and dst_ep.can_connect(src_ep):
                _logger.log(TRACE, "Direct connecting %s to %s", src_ep, dst_ep)
                dst_ep.connect(src_ep)
                src_ep.connect(dst_ep)
            elif ct == ConnectionType.DOWNCAST and dst_ep.can_downcast_connect(src_ep):
                _logger.log(TRACE, "Direct downcast connecting %s to %s", src_ep, dst_ep)
                dst_ep.connect(src_ep)
                src_ep.connect(dst_ep)
            else:
                _logger.log(TRACE, "Cannot connect %s to %s using %s", src_ep, dst_ep, ct.name)
    return cgraph.is_stable()


def local_random_connect(_: RuntimeContext, egc: EGCode, ct: ConnectionType) -> bool:
    """Attempt random connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Random connections are made from any eligible source.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
        ct: The type of connection to attempt (MATCHING or DOWNCAST).
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    _logger.log(TRACE, "Attempting local random connect with ct=%s", ct.name)
    cgraph = egc["cgraph"]
    assert isinstance(cgraph, CGraph), "EGCode cgraph is not a CGraph"
    return cgraph.is_stable()


STABILIZATION_FUNCTIONS: tuple[Callable[[RuntimeContext, EGCode], bool], ...] = (
    partial(local_direct_connect, ct=ConnectionType.MATCHING),
    partial(local_direct_connect, ct=ConnectionType.DOWNCAST),
    partial(local_random_connect, ct=ConnectionType.MATCHING),
    partial(local_random_connect, ct=ConnectionType.DOWNCAST),
)


def sfss(rtctxt: RuntimeContext, egc: EGCode) -> EGCode:
    """Perform Static Full Stack Stabilization on an EGCode's CGraph.

    The EGCode is modified in place. Stabilization may impact other genetic codes
    closer to the root (top level) genetic code of the tree.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
    Returns:
        The stabilized EGCode.
    Raises:
        StabilizationError: If stabilization fails after the maximum number of attempts.
    """
    attempts = 0
    if _logger.isEnabledFor(GC_DEBUG):
        _logger.log(GC_DEBUG, "Starting SFSS on EGCode with signature %s", egc["signature"])
    while not any(f(rtctxt, egc) for f in STABILIZATION_FUNCTIONS) and attempts < MAX_ATTEMPTS:
        attempts += 1
        _logger.log(GC_DEBUG, "SFSS attempt %d failed, retrying...", attempts)

    if attempts >= MAX_ATTEMPTS:
        _logger.log(
            INFO,
            "SFSS failed after maximum attempts (%d) for EGCode with signature %s",
            MAX_ATTEMPTS,
            egc,
        )
        raise StabilizationError(f"SFSS failed after maximum attempts ({MAX_ATTEMPTS})")
    return egc


def stabilize_gc(rtctxt: RuntimeContext, egc: EGCode) -> GGCode:
    """Stabilize an EGCode to a GGCode raising an SSE as necessary."""

    # Walk the GC structure to ensure all sub-GC's are stable
    # GGCodes are guaranteed stable so only EGCodes need testing
    parent = rtctxt.parent
    discovery_queue: list[tuple[GCABC | None, EGCode]] = [(parent, egc)]
    stabilization_stack: list[tuple[GCABC | None, EGCode]] = []
    while discovery_queue:
        current_parent, current_egc = discovery_queue.pop(0)
        assert isinstance(current_egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
        gca = current_egc["gca"]
        gcb = current_egc["gcb"]
        if not isinstance(gca, GGCode):
            discovery_queue.append((current_egc, gca))
        if not isinstance(gcb, GGCode):
            discovery_queue.append((current_egc, gcb))
        if not current_egc["cgraph"].is_stable():
            stabilization_stack.append((current_parent, current_egc))

    # Now stabilize in reverse order (bottom-up)
    # This ensures that leaves are stabilized before parents
    # NOTE: This can raise a StabilizationError which we just let propagate up
    gpi: GenePoolInterface = rtctxt.gpi
    if _logger.isEnabledFor(GC_DEBUG):
        _logger.log(
            GC_DEBUG,
            "Stabilizing %d EGCodes in stabilization stack",
            len(stabilization_stack),
        )
    for current_parent, current_egc in reversed(stabilization_stack):
        # Sanity checks
        assert isinstance(current_egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
        rtctxt.parent = current_parent
        current_egc = sfss(rtctxt, current_egc)

    # Re-walk the GC structure (which may have changed during stabilization)
    # looking for the, now stable, EGCodes to convert to GGCodes
    item = (parent, egc)
    discovery_queue = [item]
    stable_queue = [item]
    _logger.log(GC_DEBUG, "Collecting stable EGCodes for GGCode conversion")
    while discovery_queue:
        current_parent, current_egc = discovery_queue.pop(0)
        gca = current_egc["gca"]
        gcb = current_egc["gcb"]
        if not isinstance(gca, GGCode):
            item = (current_egc, gca)
            discovery_queue.append(item)
            stable_queue.append(item)
        if not isinstance(gcb, GGCode):
            item = (current_egc, gcb)
            discovery_queue.append(item)
            stable_queue.append(item)

    # Stable GC's are converted to GGCodes and added to the Gene Pool
    _logger.log(GC_DEBUG, "Converting stable EGCodes to GGCodes and storing in the Gene Pool.")
    for current_parent, current_egc in reversed(stable_queue):
        inherit_members(gpi, current_egc)
        ggc = GGCode(current_egc)
        gpi[ggc["signature"]] = ggc

    # Restore the original parent
    rtctxt.parent = parent
    return ggc  # type: ignore [guarranteed to be bound]
