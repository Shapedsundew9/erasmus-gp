"""Common utilities for mutation primitives."""

from copy import deepcopy

from egpcommon.egp_log import Logger, egp_logger
from egppy.physics.pgc_api import EGCode

# Logging setup
_logger: Logger = egp_logger(name=__name__)

# Maximum graph size limit (FR-008)
# TODO: Move this to a central configuration file
MAX_GRAPH_SIZE: int = 1024


def verify_graph_size(rgc: EGCode) -> None:
    """Verify that the genetic code does not exceed the maximum graph size.

    Raises:
        RuntimeError: If the graph size exceeds MAX_GRAPH_SIZE.
    """
    # Use num_codes as a measure of graph size (total sub-GCs + 1)
    # If num_codes is not yet populated, we may need to compute it or skip.
    num_codes = rgc.get("num_codes", 0)
    if num_codes > MAX_GRAPH_SIZE:
        raise RuntimeError(f"Graph size limit exceeded: {num_codes} > {MAX_GRAPH_SIZE}")


def copy_rgc(rgc: EGCode) -> EGCode:
    """Create a deep copy of an EGCode's CGraph for transactional atomicity (FR-010).

    This ensures that mutation operations do not modify the original graph
    unless the entire operation succeeds.
    """
    # Create a new EGCode with the same members
    # We explicitly deepcopy the cgraph to ensure independence
    new_init_dict = {
        "gca": rgc["gca"],
        "gcb": rgc["gcb"],
        "cgraph": deepcopy(rgc["cgraph"]),
        "ancestora": rgc["ancestora"],
        "ancestorb": rgc["ancestorb"],
        "pgc": rgc["pgc"],
        "creator": rgc["creator"],
        "properties": deepcopy(rgc["properties"]),
    }

    # Create the new EGCode
    rgc_new = EGCode(new_init_dict)

    # Inherit other members if they exist
    # These must be set AFTER EGCode(new_init_dict) because set_members() ignores them.
    for key in ["generation", "num_codes", "num_codons", "code_depth", "meta_data"]:
        if key in rgc:
            rgc_new[key] = deepcopy(rgc[key])

    return rgc_new
