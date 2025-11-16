"""Helper functions for physics of Genetic Codes."""

from functools import wraps

from egpcommon.properties import BitDictABC, CGraphType, GCType, PropertiesBD
from egppy.gene_pool.gene_pool_interface import GenePoolInterface, GGCDict
from egppy.genetic_code.genetic_code import GCABC


def merge_properties_base(prop_a: BitDictABC, prop_b: BitDictABC) -> BitDictABC:
    """Merge GCA and GCB properties when the resultant GC has a standard graph type."""

    merged_properties = PropertiesBD()

    # GC Type: take the "higher" type
    merged_properties["gc_type"] = GCType.ORDINARY
    merged_properties["graph_type"] = CGraphType.STANDARD

    # Constant: only if both are constant
    merged_properties["constant"] = prop_a["constant"] and prop_b["constant"]

    # Deterministic: only if both are deterministic
    merged_properties["deterministic"] = prop_a["deterministic"] and prop_b["deterministic"]

    # Abstract: if either is abstract - not used - do we care?
    # TODO: merged_properties["abstract"] = if row I or O has abstract endpoint?

    # Side Effects: if either has side effects
    merged_properties["side_effects"] = prop_a["side_effects"] or prop_b["side_effects"]

    # Other properties can be merged as needed; for now, we set them to default values
    # or implement specific merging logic as required.

    return merged_properties


def merge_properties(gca: GCABC, gcb: GCABC) -> BitDictABC:
    """Merge GCA and GCB properties for resultant GC."""
    _prop_a: BitDictABC | int = gca["properties"]
    _prop_b: BitDictABC | int = gcb["properties"]
    prop_a = _prop_a if isinstance(_prop_a, BitDictABC) else PropertiesBD(_prop_a)
    prop_b = _prop_b if isinstance(_prop_b, BitDictABC) else PropertiesBD(_prop_b)

    # TODO: Implement GC type specific merging logic
    return merge_properties_base(prop_a, prop_b)


def pgc_epilogue(func):
    """Decorator for PGC functions to finalize the resultant GC.

    This decorator wraps PGC functions to convert the resultant EGCode GC into a GGCode GC,
    store it in the Gene Pool Interface, and return the GGCode GC.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> GCABC:
        egc: GCABC = func(*args, **kwargs)

        gpi: GenePoolInterface = args[0].gpi if args else kwargs["rtctxt"].gpi
        gca: GCABC = gpi[egc["gca"]]
        gcb: GCABC = gpi[egc["gcb"]]

        # Populate inherited members
        egc["num_codons"] = gca["num_codons"] + gcb["num_codons"]
        egc["num_codes"] = gca["num_codes"] + gcb["num_codes"] + 1
        egc["generation"] = max(gca["generation"], gcb["generation"]) + 1
        egc["code_depth"] = max(gca["code_depth"], gcb["code_depth"]) + 1

        # Unstable GC's are returned as-is
        if not egc["cgraph"].is_stable():
            return egc

        # Stable GC's are converted to GGCodes and added to the Gene Pool
        ggc: GCABC = GGCDict(egc)
        gpi[ggc["signature"]] = ggc
        return ggc

    return wrapper
