"""Generate codons."""

from copy import deepcopy
from os.path import dirname, join
from typing import Any

from egpcommon.common import EGP_EPOCH
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json
from egpcommon.spinner import Spinner
from egppy.genetic_code.ggc_class_factory import NULL_SIGNATURE, GGCDict
from egppy.genetic_code.types_def import types_def_store
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)

# Constants
OUTPUT_CODON_PATH = join(
    dirname(__file__), "..", "..", "egpdbmgr", "egpdbmgr", "data", "meta_codons.json"
)
CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
    "cgraph": {"A": [["I", 0, None]], "O": [["I", 0, None]]},
    "gca": NULL_SIGNATURE,
    "gcb": NULL_SIGNATURE,
    "creator": "22c23596-df90-4b87-88a4-9409a0ea764f",
    "created": EGP_EPOCH.isoformat(),
    "generation": 1,
    "num_codes": 1,
    "num_codons": 1,
    "problem": ACYBERGENESIS_PROBLEM,
    "properties": {
        # The META type allows connections between different end point types.
        "gc_type": GCType.META,
        # NOTE: The graph type does not have to be primitive.
        "graph_type": CGraphType.PRIMITIVE,
        "constant": False,
        "deterministic": True,
        "side_effects": False,
        "static_creation": True,
    },
    "meta_data": {
        "function": {
            "python3": {
                "0": {
                    "inline": "raise_if_not_instance_of({i0}, otype)",
                    "description": "Raise if i0 (itype) is not an instance (or child) of otype.",
                    "name": "raise_if_not_instance_of(itype, otype)",
                    "imports": [
                        {"aip": ["egppy", "physics", "meta"], "name": "raise_if_not_instance_of"}
                    ],
                }
            }
        }
    },
}


def generate_meta_codons() -> None:
    """Generate meta codons."""
    if _LOG_DEBUG:
        _logger.debug("Generating meta codons...")

    # Find the set of type "casts". Types may be cast in two ways:
    #   - To a parent
    #   - To a valid child (this implies it was previously cast to a parent)
    # Casts use isinstance() to validate they are correct and so can only be applied
    # to types that have tt = 0
    cast_set: set[tuple[int, int]] = {
        (child.uid, puid)
        for child in types_def_store.values()
        if child.tt() == 0
        for puid in child.parents
    }

    # Watch progress
    spinner = Spinner("Generating meta codons...")
    spinner.start()

    # Create a type cast codon for every possible cast
    meta_codons: list[dict[str, Any]] = []
    for cuid, puid in cast_set:
        # Create a copy of the codon template
        codon: dict[str, Any] = deepcopy(CODON_TEMPLATE)

        # Get the parent and child type definitions
        ptd = types_def_store[puid]
        ctd = types_def_store[cuid]

        # Set the type for the connections in the connection graph
        codon["cgraph"]["A"][0][2] = ptd.name
        codon["cgraph"]["O"][0][2] = ctd.name

        # Replace the placeholder type strings in the meta data
        base = codon["meta_data"]["function"]["python3"]["0"]
        for s, r in (("itype", ptd.name), ("otype", ctd.name)):
            base["inline"] = base["inline"].replace(s, r)
            base["description"] = base["description"].replace(s, r)
            base["name"] = base["name"].replace(s, r)

        new_codon = GGCDict(codon)
        new_codon.consistency()
        codon = new_codon.to_json()
        meta_codons.append(codon)

    # Write the meta codons to the output file
    spinner.stop()
    dump_signed_json(meta_codons, OUTPUT_CODON_PATH)

    if _LOG_DEBUG:
        _logger.debug("Meta codons generated successfully.")


if __name__ == "__main__":
    generate_meta_codons()
