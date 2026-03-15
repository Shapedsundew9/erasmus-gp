"""Helper functions for physics of Genetic Codes."""

from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.properties import BitDictABC, CGraphType, GCType, PropertiesBD
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph import CGraph, IfKey
from egppy.genetic_code.c_graph_constants import DstIfKey, DstRow, SrcIfKey, SrcRow
from egppy.genetic_code.frozen_interface import FrozenInterface
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.interface_abc import FrozenInterfaceABC, InterfaceABC
from egppy.genetic_code.types_def import TypesDef
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext

# Logging setup
_logger: Logger = egp_logger(name=__name__)


# Constants
_ROW_O_REF_0 = (((DstRow.O, 0),),)
_ROW_A_REF_0 = (((SrcRow.A, 0),),)

# The priority sequence for local direct connections
LDC_SEQ = (
    (SrcIfKey.IS, DstIfKey.AD),
    (SrcIfKey.AS, DstIfKey.BD),
    (SrcIfKey.BS, DstIfKey.OD),
)


def merge_properties(
    rtctxt: RuntimeContext, gca: GCABC | bytes, gcb: GCABC | bytes | None
) -> BitDictABC:
    """Merge GCA and GCB properties for resultant GC."""
    assert gca is not None, "GCA cannot be None as this means the resultant GC is a codon!"

    # Extract GCA properties
    gca = gca if isinstance(gca, GCABC) else rtctxt.gpi[gca]
    _prop_a = gca["properties"]
    if isinstance(_prop_a, (int, dict, bytes, bytearray, type(None))):
        prop_a = PropertiesBD(_prop_a)
    else:
        prop_a = _prop_a

    # If GCB is None, return GCA properties
    if gcb is None:
        return prop_a

    # Extract GCB properties
    gcb = gcb if isinstance(gcb, GCABC) else rtctxt.gpi[gcb]
    _prop_b = gcb["properties"]
    if isinstance(_prop_b, (int, dict, bytes, bytearray, type(None))):
        prop_b = PropertiesBD(_prop_b)
    else:
        prop_b = _prop_b

    # TODO: Implement GC type specific merging logic
    return merge_properties_base(prop_a, prop_b)


def merge_properties_base(prop_a: BitDictABC, prop_b: BitDictABC) -> BitDictABC:
    """Merge GCA and GCB properties when the resultant GC has a standard graph type."""

    merged_properties = PropertiesBD()

    # GC Type: take the "higher" type
    merged_properties["gc_type"] = GCType.ORDINARY

    # FIXME: Graph Type: for now, always STANDARD
    # but how do we pass in conditional or loop types?
    merged_properties["graph_type"] = CGraphType.STANDARD

    # Constant: only if both are constant
    merged_properties["constant"] = bool(prop_a["constant"] and prop_b["constant"])

    # Deterministic: only if both are deterministic
    merged_properties["deterministic"] = bool(prop_a["deterministic"] and prop_b["deterministic"])

    # Abstract: if either is abstract - not used - do we care?
    # TODO: merged_properties["abstract"] = if row I or O has abstract endpoint?

    # Side Effects: if either has side effects
    merged_properties["side_effects"] = bool(prop_a["side_effects"] or prop_b["side_effects"])

    # Other properties can be merged as needed; for now, we set them to default values
    # or implement specific merging logic as required.

    return merged_properties


def empty_egc(
    rtctxt: RuntimeContext, iface: FrozenInterfaceABC, oface: FrozenInterfaceABC
) -> EGCode:
    """Create an empty EGCode with specified input and output interfaces.

    Args:
        rtctxt: The runtime context.
        iface: The input interface. Copied with references cleared.
        oface: The output interface. Copied with references cleared.
    Returns:
        An empty EGCode with the specified interfaces.
    """
    cgraph_dict: dict[IfKey, InterfaceABC] = {
        SrcIfKey.IS: Interface(iface, SrcRow.I).clr_refs(),
        DstIfKey.OD: Interface(oface, DstRow.O).clr_refs(),
    }
    cgraph = CGraph(cgraph_dict)
    init_dict = {
        "cgraph": cgraph,
        "pgc": rtctxt.root_gc,
        "creator": rtctxt.creator,
        "properties": PropertiesBD(
            {
                "gc_type": GCType.ORDINARY,
                "graph_type": CGraphType.EMPTY,
            }
        ),
    }
    return EGCode(init_dict)


def new_egc(
    rtctxt: RuntimeContext,
    gca: GCABC | bytes,
    gcb: GCABC | bytes | None = None,
    ancestora: GCABC | bytes | None = None,
    ancestorb: GCABC | bytes | None = None,
    rebuild: EGCode | None = None,
) -> EGCode:
    """Create a new EGCode from GCA and GCB.

    Args:
        rtctxt: The runtime context.
        gca: The GCA genetic code or its signature.
        gcb: The GCB genetic code or its signature, or None for single-parent GCs.
        ancestora: The ancestor of GCA or its signature, or None.
        ancestorb: The ancestor of GCB or its signature, or None.
        rebuild: An existing EGCode to rebuild else a new one is created.
    Returns:
        The newly created/rebuilt EGCode. Note that only row A and B (if it is used) interfaces
        are populated with all references cleared.
        The I and O rows as well as any other rows for the non-standard graph types are not
        modified (remain 'None' in the case of a new EGCode).
        All other members are reset e.g. properties, creator etc.
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

    # If we are building merge the updated cgraph into the rebuild
    if rebuild is not None:
        assert isinstance(rebuild["cgraph"], CGraph), "Rebuild must have a mutable cgraph."
        rebuild["cgraph"].update(_cgraph)

    init_dict = {
        "gca": gca,
        "gcb": gcb,
        "cgraph": CGraph(_cgraph) if rebuild is None else rebuild["cgraph"],
        "ancestora": ancestora,
        "ancestorb": ancestorb,
        "pgc": rtctxt.root_gc,
        "creator": rtctxt.creator,
        "properties": merge_properties(rtctxt=rtctxt, gca=gca, gcb=gcb),
    }
    retval = EGCode(init_dict) if rebuild is None else rebuild.set_members(init_dict)
    assert isinstance(retval, EGCode), "New EGCode creation failed - result is not an EGCode."
    return retval


def direct_connect_interfaces(
    src_iface: InterfaceABC, dst_iface: InterfaceABC, check: bool = False
) -> None:
    """Directly connect two interfaces together index-to-index.
    NB: This does not perform any type checking or conversion. It is a helper function
    for fundamental physics not a mutation operator. See local_direct_connect() in
    stabilization.py for a higher-level function that performs type checking.

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


def inherit_members(gpi: GenePoolInterface, egc: EGCode) -> None:
    """Inherit members."""
    gca = egc["gca"]
    gcb = egc["gcb"]

    if isinstance(gca, bytes):
        gca = gpi[gca]
    if gcb is not None and isinstance(gcb, bytes):
        gcb = gpi[gcb]

    # Populate inherited members
    egc["num_codons"] = gca["num_codons"] + gcb["num_codons"]
    egc["num_codes"] = gca["num_codes"] + gcb["num_codes"] + 1
    egc["generation"] = max(gca["generation"], gcb["generation"]) + 1
    egc["code_depth"] = max(gca["code_depth"], gcb["code_depth"]) + 1


def literal_codon(rtctxt: RuntimeContext, obj: object, td: TypesDef) -> GGCDict:
    """Create python literal codon representation of an object.
    A type definition is required to correctly identify obj as it could be
    a templated type.

    Args:
        obj: The object to represent as a literal codon.
        td: The TypesDef of the object.

    Returns:
        A GGCode representing the literal codon.
    """
    return GGCDict(
        {
            "gca": None,
            "gcb": None,
            "cgraph": CGraph(
                {
                    SrcIfKey.AS: FrozenInterface(SrcRow.A, (td,), _ROW_O_REF_0),
                    DstIfKey.OD: FrozenInterface(DstRow.O, (td,), _ROW_A_REF_0),
                }
            ),
            "ancestora": None,
            "ancestorb": None,
            "pgc": rtctxt.root_gc,
            "creator": rtctxt.creator,
            "generation": 1,
            "num_codes": 1,
            "num_codons": 1,
            "code_depth": 1,
            "properties": PropertiesBD(
                {
                    "gc_type": GCType.CODON,
                    "graph_type": CGraphType.PRIMITIVE,
                    "gctsp": {"literal": True},
                }
            ),
            "meta_data": {
                "inline": repr(obj),
                "description": "Custom literal or predefined object.",
                "name": "LiteralCodon",
                "imports": td.imports,
            },
        }
    )
