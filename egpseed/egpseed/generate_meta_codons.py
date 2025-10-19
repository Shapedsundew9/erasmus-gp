"""Generate codons."""

from copy import deepcopy
from os.path import dirname, join
from typing import Any

from egpcommon.common import ACYBERGENESIS_PROBLEM, EGP_EPOCH
from egpcommon.egp_log import DEBUG, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json
from egpcommon.spinner import Spinner
from egppy.genetic_code.ggc_class_factory import NULL_SIGNATURE, GGCDict
from egppy.genetic_code.types_def import types_def_store

# Standard EGP logging pattern
enable_debug_logging()
_logger: Logger = egp_logger(name=__name__)

# Constants
OUTPUT_CODON_PATH = join(
    dirname(__file__), "..", "..", "egppy", "egppy", "data", "meta_codons.json"
)
CODON_TEMPLATE: dict[str, Any] = {
    "code_depth": 1,
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
}

CODON_ONE_PARAMETER: dict[str, Any] = CODON_TEMPLATE | {
    "cgraph": {"A": [["I", 0, None]], "O": [["A", 0, None]], "U": []},
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

CODON_TWO_PARAMETER: dict[str, Any] = CODON_TEMPLATE | {
    "cgraph": {
        "A": [["I", 0, None], ["I", 1, None]],
        "O": [["A", 0, None], ["A", 1, None]],
        "U": [],
    },
    "meta_data": {
        "function": {
            "python3": {
                "0": {
                    "inline": "raise_if_not_both_instances_of({i0}, {i1}, otype)",
                    "description": "Raise if i0 or i1 (itype) is not an instance (or child) of otype.",
                    "name": "raise_if_not_both_instances_of(itype, itype, otype)",
                    "imports": [
                        {
                            "aip": ["egppy", "physics", "meta"],
                            "name": "raise_if_not_both_instances_of",
                        }
                    ],
                }
            }
        }
    },
}


def generate_meta_codons(write: bool = False) -> None:
    """Generate meta codons.

    Arguments:
        write: If True, write the meta codons to a JSON file.
    """
    _logger.log(DEBUG, "Generating meta codons...")

    # Find the set of type "casts". Types may be cast in two ways:
    #   - To an ancestor (parent, grandparent ... 'object' at the root)
    #   - To a valid child (this implies it was previously cast to a parent)
    # Casts use isinstance() to validate they are correct and so can only be applied
    # to types that have tt = 0
    cast_set: set[tuple[int, int]] = {
        (child.uid, ancestor.uid)
        for child in types_def_store.values()
        if child.tt() == 0
        for ancestor in types_def_store.ancestors(child.uid)
        if ancestor.uid != child.uid
    }

    # Watch progress
    spinner = Spinner("Generating meta codons...")
    spinner.start()

    # Create a type cast codon for every possible cast
    meta_codons: dict[str, dict[str, Any]] = {}
    for cuid, puid in cast_set:

        # Get the parent and child type definitions
        ptd = types_def_store[puid]
        ctd = types_def_store[cuid]

        # One and two parameter variants
        for codon_template in (CODON_ONE_PARAMETER, CODON_TWO_PARAMETER):
            # Do both directions
            for inpt, oupt in ((ctd, ptd), (ptd, ctd)):

                # Create a copy of the codon template
                codon: dict[str, Any] = deepcopy(codon_template)

                # Set the type for the connections in the connection graph
                for ept in codon["cgraph"]["A"]:
                    ept[2] = inpt.name
                for ept in codon["cgraph"]["O"]:
                    ept[2] = oupt.name

                # Replace the placeholder type strings in the meta data
                base = codon["meta_data"]["function"]["python3"]["0"]
                for s, r in (("itype", inpt.name), ("otype", oupt.name)):
                    base["inline"] = base["inline"].replace(s, r)
                    base["description"] = base["description"].replace(s, r)
                    base["name"] = base["name"].replace(s, r)

                new_codon = GGCDict(codon)
                new_codon.verify()
                codon = new_codon.to_json()
                if codon["signature"] in meta_codons:
                    raise ValueError(f"Duplicate meta codon signature: {codon['signature']}")
                meta_codons[codon["signature"]] = codon

    # Write the meta codons to the output file (optional)
    spinner.stop()
    if write:
        dump_signed_json(list(meta_codons.values()), OUTPUT_CODON_PATH)

    _logger.log(DEBUG, "Meta codons generated successfully.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate meta codons.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_meta_codons(write=args.write)
