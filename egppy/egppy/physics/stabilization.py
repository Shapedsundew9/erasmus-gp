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

from typing import Callable

from egpcommon.egp_rnd_gen import EGPRndGen
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.genetic_code.endpoint_abc import EndPointABC
from egppy.genetic_code.ggc_dict import GCABC, GGCDict
from egppy.physics.insertion import insert
from egppy.physics.meta import meta_upcast
from egppy.physics.runtime_context import RuntimeContext
from egpseed.primordial_python import EGCode

# Constants
MAX_ATTEMPTS = 8

# The priority sequence for direct connections
DC_SEQ = (
    (SrcIfKey.IS, DstIfKey.AD),
    (SrcIfKey.AS, DstIfKey.BD),
    (SrcIfKey.BS, DstIfKey.OD),
)


class StabilizationError(Exception):
    """Raised when stabilization fails."""


def direct_connect(_: RuntimeContext, egc: EGCode) -> bool:
    """Attempt direct connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Direct connections are only made Input -> GCA, GCA -> GCB and GCB -> Output

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    assert isinstance(egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
    cgraph = egc["cgraph"]
    for src_if, dst_if in DC_SEQ:
        for src_ep, dst_ep in zip(cgraph[src_if], cgraph[dst_if]):
            if dst_ep.can_connect(src_ep):
                dst_ep.connect(src_ep)
                src_ep.connect(dst_ep)
    return cgraph.is_stable()


def upcast_direct_connect(rtctxt: RuntimeContext, egc: EGCode) -> bool:
    """Attempt upcast direct connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Upcast direct connections are only made Input -> GCA, GCA -> GCB and GCB -> Output

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    assert isinstance(egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
    cgraph = egc["cgraph"]
    for src_if, dst_if in DC_SEQ:

        # Build a list of direct connections that require upcasting
        upcast_list: list[tuple[EndPointABC, EndPointABC]] = []
        for src_ep, dst_ep in zip(cgraph[src_if], cgraph[dst_if]):
            assert isinstance(src_ep, EndPointABC), "Source endpoint is not an EndPointABC"
            assert isinstance(dst_ep, EndPointABC), "Destination endpoint is not an EndPointABC"
            if dst_ep.can_upcast_connect(src_ep):
                upcast_list.append((src_ep, dst_ep))

        if upcast_list:
            # Find or create the meta codon to do the upcasting
            mgc = meta_upcast(
                rtctxt,
                [src_ep.typ for src_ep, _ in upcast_list],
                [dst_ep.typ for _, dst_ep in upcast_list],
            )

            # Insert the meta-codon below the source row/interface
            # This is so we know the relative positions of the interfaces
            insert(rtctxt, mgc, egc, src_if)

            # Now set the types.
            cgraph = egc["cgraph"]
            for idx, (src_ep, dst_ep) in enumerate(upcast_list):
                # The insertion changed the cgraph so we need to re-get the endpoints
                src_ep = cgraph[src_if][src_ep.idx]
                dst_ep = cgraph[dst_if][dst_ep.idx]
                assert isinstance(src_ep, EndPointABC), "Source endpoint is not an EndPointABC"
                assert isinstance(dst_ep, EndPointABC), "Destination endpoint is not an EndPointABC"

                # Match the types (this is the type to be upcast) then we can connect
                # directly in the egc (rgc) cgraph
                dst_ep.typ = src_ep.typ
                src_ep.connect(dst_ep)
                dst_ep.connect(src_ep)

                # Find fgc and update its input interface type in ther same spot
                fgc = egc["gca"] if dst_ep.row is DstIfKey.AD else egc["gcb"]
                fgc_cgraph = fgc["cgraph"]
                assert isinstance(fgc_cgraph, CGraphABC), "FGC cgraph is not a CGraphABC"
                fgc_is_ep = fgc_cgraph[SrcIfKey.IS][dst_ep.idx]
                assert isinstance(fgc_is_ep, EndPointABC), "FGC IS endpoint is not an EndPointABC"
                fgc_is_ep.typ = src_ep.typ

                # Find mgc
                mdk, msk, tdk = (
                    (DstIfKey.AD, SrcIfKey.AS, DstIfKey.BD)
                    if fgc["gca"] is mgc
                    else (DstIfKey.BD, SrcIfKey.BS, DstIfKey.AD)
                )

                # Connect the ep to upcast to the mgc input interface
                mgc_dst_ep = fgc_cgraph[mdk][idx]
                assert isinstance(
                    mgc_dst_ep, EndPointABC
                ), f"FGC {mdk} endpoint is not an EndPointABC"
                assert not mgc_dst_ep.is_connected(), f"FGC {mdk} endpoint is already connected"
                assert (
                    mgc_dst_ep.typ == fgc_is_ep.typ
                ), f"FGC {mdk} endpoint type mismatch with FGC IS endpoint"
                mgc_dst_ep.connect(fgc_is_ep)
                fgc_is_ep.connect(mgc_dst_ep)

                # Now connect the mgc output ep (which has been upcast) to the tgc sub-GC
                # ep that needed the upcast
                mgc_src_ep = fgc_cgraph[msk][idx]
                assert isinstance(
                    mgc_src_ep, EndPointABC
                ), f"FGC {msk} endpoint is not an EndPointABC"
                assert (
                    not mgc_src_ep.is_connected()
                ), f"FGC {msk} (MGC) endpoint is already connected"
                tgc_dst_ep = fgc_cgraph[tdk][dst_ep.idx]
                assert isinstance(
                    tgc_dst_ep, EndPointABC
                ), f"TGC {tdk} endpoint is not an EndPointABC"
                assert (
                    mgc_src_ep.typ == tgc_dst_ep.typ
                ), f"FGC {msk} (MGC) and TGC {tdk} endpoint type mismatch"
                mgc_src_ep.connect(tgc_dst_ep)
                tgc_dst_ep.connect(mgc_src_ep)

    return cgraph.is_stable()


def random_connect(rtctxt: RuntimeContext, egc: EGCode) -> bool:
    """Attempt random connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Random connections are made from any eligible source.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    assert isinstance(egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
    cgraph = egc["cgraph"]
    return cgraph.is_stable()


def random_upcast_connect(rtctxt: RuntimeContext, egc: EGCode) -> bool:
    """Attempt random upcast connections for any unconnected destination endpoints
    in an EGCode's CGraph.

    Random upcast connections are made from any eligible source. Upcasting
    will require a at least one meta codon to be inserted.

    Arguments:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        egc: The EGCode to be stabilized. egc is modified in place.
    Returns:
        True if the resulting EGCode is stable, False otherwise.
    """
    assert isinstance(egc["cgraph"], CGraph), "EGCode cgraph is not a CGraph"
    cgraph = egc["cgraph"]
    return cgraph.is_stable()


STABILIZATION_FUNCTIONS: tuple[Callable[[RuntimeContext, EGCode], bool], ...] = (
    direct_connect,
    upcast_direct_connect,
    random_connect,
    random_upcast_connect,
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

    assert isinstance(egc["cgraph"], CGraph), "EGCode c_graph is not a CGraph"

    attempts = 0
    while not any(f(rtctxt, egc) for f in STABILIZATION_FUNCTIONS) and attempts < MAX_ATTEMPTS:
        attempts += 1
    if attempts >= MAX_ATTEMPTS:
        raise StabilizationError(f"SFSS failed after maximum attempts ({MAX_ATTEMPTS})")
    return egc


def stabilize_gc(
    rtctxt: RuntimeContext, egc: GCABC, sse: bool = False, if_locked: bool = True
) -> GCABC:
    """Stabilize an EGCode to a GGCode raising an SSE as necessary."""

    assert isinstance(egc["cgraph"], CGraph), "Resultant GC c_graph is not a CGraph"
    egc["cgraph"].stabilize(if_locked, EGPRndGen(egc["created"]))

    stable = egc["cgraph"].is_stable()
    if not stable and sse:
        raise NotImplementedError("Stabilization failed and SSE requested")
    if not stable:
        raise RuntimeError("Stabilization failed")

    gpi: GenePoolInterface = rtctxt.gpi
    gca: GCABC = gpi[egc["gca"]]
    gcb: GCABC = gpi[egc["gcb"]]

    # Populate inherited members
    egc["num_codons"] = gca["num_codons"] + gcb["num_codons"]
    egc["num_codes"] = gca["num_codes"] + gcb["num_codes"] + 1
    egc["generation"] = max(gca["generation"], gcb["generation"]) + 1
    egc["code_depth"] = max(gca["code_depth"], gcb["code_depth"]) + 1

    # Stable GC's are converted to GGCodes and added to the Gene Pool
    ggc: GCABC = GGCDict(egc)

    # A bit of sanity checking
    if not gca["cgraph"][SrcIfKey.IS].to_td() == ggc["cgraph"][DstIfKey.AD].to_td():
        raise ValueError("GCA row Is does not match GGCode row Ad")
    if not gca["cgraph"][DstIfKey.OD].to_td() == ggc["cgraph"][SrcIfKey.AS].to_td():
        raise ValueError("GCA row Od does not match GGCode row As")
    if not gcb["cgraph"][SrcIfKey.IS].to_td() == ggc["cgraph"][DstIfKey.BD].to_td():
        raise ValueError("GCB row Is does not match GGCode row Bd")
    if not gcb["cgraph"][DstIfKey.OD].to_td() == ggc["cgraph"][SrcIfKey.BS].to_td():
        raise ValueError("GCB row Od does not match GGCode row Bs")

    # Add to Gene Pool
    gpi[ggc["signature"]] = ggc
    return ggc
