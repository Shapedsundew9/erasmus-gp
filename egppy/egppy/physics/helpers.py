"""Helper functions for physics of Genetic Codes."""

from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.properties import BitDictABC, CGraphType, GCType, PropertiesBD
from egppy.genetic_code.c_graph import CGraph, IfKey
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, SrcIfKey, SrcRow
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.interface_abc import InterfaceABC
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


def merge_properties(
    rtctxt: RuntimeContext, gca: GCABC | bytes, gcb: GCABC | bytes | None
) -> BitDictABC:
    """Merge GCA and GCB properties for resultant GC."""
    assert gca is not None, "GCA cannot be None as this means the resultant GC is a codon!"

    # Extract GCA properties
    gca = gca if isinstance(gca, GCABC) else rtctxt.gpi[gca]
    _prop_a: BitDictABC | int = gca["properties"]
    prop_a = _prop_a if isinstance(_prop_a, BitDictABC) else PropertiesBD(_prop_a)

    # If GCB is None, return GCA properties
    if gcb is None:
        return prop_a

    # Extract GCB properties
    gcb = gcb if isinstance(gcb, GCABC) else rtctxt.gpi[gcb]
    _prop_b: BitDictABC | int = gcb["properties"]
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


def new_egc(
    rtctxt: RuntimeContext,
    gca: GCABC | bytes,
    gcb: GCABC | bytes | None = None,
    ancestora: GCABC | bytes | None = None,
    ancestorb: GCABC | bytes | None = None,
) -> GCABC:
    """Create a new EGCode from GCA and GCB.

    Args:
        rtctxt: The runtime context.
        gca: The GCA genetic code or its signature.
        gcb: The GCB genetic code or its signature, or None for single-parent GCs.
        ancestora: The ancestor of GCA or its signature, or None.
        ancestorb: The ancestor of GCB or its signature, or None.
    Returns:
        The newly created EGCode. Note that only row A and B (if it is used) interfaces
        are populated with all referencves cleared.
        The I and O rows are left as None for later assignment as well as any other rows for
        the non-standard graph types.
    """
    assert gca is not None, "GCA cannot be None as this means the resultant GC is a codon!"
    _gca = gca if isinstance(gca, GCABC) else rtctxt.gpi[gca]
    _cgraph: dict[IfKey, InterfaceABC] = {
        DstIfKey.AD: Interface(_gca["cgraph"][SrcIfKey.IS], DstRow.A).clr_refs(),
        SrcIfKey.AS: Interface(_gca["cgraph"][DstIfKey.OD], SrcRow.A).clr_refs(),
    }
    if gcb is not None:
        _gcb = gcb if isinstance(gcb, GCABC) else rtctxt.gpi[gcb]
        _cgraph[DstIfKey.BD] = Interface(_gcb["cgraph"][SrcIfKey.IS], DstRow.B).clr_refs()
        _cgraph[SrcIfKey.BS] = Interface(_gcb["cgraph"][DstIfKey.OD], SrcRow.B).clr_refs()
    return EGCode(
        {
            "gca": gca,
            "gcb": gcb,
            "cgraph": CGraph(_cgraph),
            "ancestora": ancestora,
            "ancestorb": ancestorb,
            "pgc": rtctxt.root_gc,
            "creator": rtctxt.creator,
            "properties": merge_properties(rtctxt=rtctxt, gca=gca, gcb=gcb),
        }
    )


def direct_connect_interfaces(
    src_iface: InterfaceABC, dst_iface: InterfaceABC, check: bool = False
) -> None:
    """Directly connect two interfaces together index-to-index.

    Args:
        src_iface: The source interface to connect from.
        dst_iface: The destination interface to connect to.
        check: If True, verify that all the connections can be made before making any.
    """
    if check or _logger.isEnabledFor(DEBUG):
        if len(src_iface) != len(dst_iface):
            raise ValueError("Source and destination interfaces have different lengths.")
        for src_ep, dst_ep in zip(src_iface, dst_iface):
            if not dst_ep.can_connect(src_ep):
                raise ValueError(f"Cannot connect {src_ep} to {dst_ep}")

    # Directly connect index-to-index
    for src_ep, dst_ep in zip(src_iface, dst_iface):
        dst_ep.connect(src_ep)
        src_ep.connect(dst_ep)
