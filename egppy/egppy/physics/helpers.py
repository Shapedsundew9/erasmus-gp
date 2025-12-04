"""Helper functions for physics of Genetic Codes."""

from egpcommon.properties import BitDictABC, CGraphType, GCType, PropertiesBD
from egppy.genetic_code.genetic_code import GCABC


def merge_properties(gca: GCABC, gcb: GCABC) -> BitDictABC:
    """Merge GCA and GCB properties for resultant GC."""
    _prop_a: BitDictABC | int = gca["properties"]
    _prop_b: BitDictABC | int = gcb["properties"]
    prop_a = _prop_a if isinstance(_prop_a, BitDictABC) else PropertiesBD(_prop_a)
    prop_b = _prop_b if isinstance(_prop_b, BitDictABC) else PropertiesBD(_prop_b)

    # TODO: Implement GC type specific merging logic
    return merge_properties_base(prop_a, prop_b)


def merge_properties_base(prop_a: BitDictABC, prop_b: BitDictABC) -> BitDictABC:
    """Merge GCA and GCB properties when the resultant GC has a standard graph type."""

    merged_properties = PropertiesBD()

    # GC Type: take the "higher" type
    gcta = prop_a["gc_type"]
    gctb = prop_b["gc_type"]
    if (
        gcta == GCType.META
        or gcta == GCType.ORDINARY_META
        and gctb == GCType.META
        or gctb == GCType.ORDINARY_META
    ):
        merged_properties["gc_type"] = GCType.ORDINARY_META
    else:
        merged_properties["gc_type"] = GCType.ORDINARY

    # FIXME: Graph Type: for now, always STANDARD
    # but how do we pass in conditional or loop types?
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
