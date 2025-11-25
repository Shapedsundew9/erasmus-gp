"""Stabilization routines for EGCode to GGCode conversion."""

from egpcommon.egp_rnd_gen import EGPRndGen
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.ggc_class_factory import GCABC, GGCDict
from egppy.physics.runtime_context import RuntimeContext


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
    if not gca["cgraph"]["Is"].to_td() == ggc["cgraph"]["Ad"].to_td():
        raise ValueError("GCA row Is does not match GGCode row Ad")
    if not gca["cgraph"]["Od"].to_td() == ggc["cgraph"]["As"].to_td():
        raise ValueError("GCA row Od does not match GGCode row As")
    if not gcb["cgraph"]["Is"].to_td() == ggc["cgraph"]["Bd"].to_td():
        raise ValueError("GCB row Is does not match GGCode row Bd")
    if not gcb["cgraph"]["Od"].to_td() == ggc["cgraph"]["Bs"].to_td():
        raise ValueError("GCB row Od does not match GGCode row Bs")

    # Add to Gene Pool
    gpi[ggc["signature"]] = ggc
    return ggc
