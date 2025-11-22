"""Generate codons."""

from copy import deepcopy
from datetime import datetime
from os.path import dirname, join
from typing import Any

from egpcommon.common import EGP_EPOCH, NULL_STR, SHAPEDSUNDEW9_UUID, sha256_signature
from egpcommon.egp_log import DEBUG, Logger, egp_logger, enable_debug_logging
from egpcommon.properties import CGraphType, GCType
from egpcommon.security import dump_signed_json, load_signed_json_list
from egpcommon.spinner import Spinner
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.ggc_class_factory import NULL_SIGNATURE, GGCDict
from egppy.genetic_code.import_def import ImportDef
from egppy.genetic_code.json_cgraph import json_cgraph_to_interfaces, valid_jcg
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
    "ancestora": NULL_SIGNATURE,
    "ancestorb": NULL_SIGNATURE,
    "pgc": NULL_SIGNATURE,
    "creator": SHAPEDSUNDEW9_UUID,
    "created": EGP_EPOCH.isoformat(),
    "generation": 1,
    "num_codes": 1,
    "num_codons": 1,
    "properties": {
        # The META type allows connections between different endpoint types.
        "gc_type": GCType.META,
        # NOTE: The graph type does not have to be primitive.
        "graph_type": CGraphType.PRIMITIVE,
        "constant": False,
        "deterministic": True,
        "side_effects": False,
        "static_creation": True,
        "gctsp": {"type_upcast": False, "type_downcast": True},
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
    },
    "meta_data": {
        "function": {
            "python3": {
                "0": {
                    "inline": "raise_if_not_both_instances_of({i0}, {i1}, otype)",
                    "description": "Raise if i0 or i1 (itype) is not an instance"
                    " (or child) of otype.",
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
            for inpt, oupt, upcast in ((ctd, ptd, True), (ptd, ctd, False)):

                # Create a copy of the codon template
                codon: dict[str, Any] = deepcopy(codon_template)
                codon["properties"]["gctsp"]["type_upcast"] = upcast
                codon["properties"]["gctsp"]["type_downcast"] = not upcast

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

                assert valid_jcg(codon["cgraph"]), "Invalid codon connection graph at construction."
                codon["signature"] = sha256_signature(
                    codon["ancestora"],
                    codon["ancestorb"],
                    codon["gca"],
                    codon["gcb"],
                    CGraph(json_cgraph_to_interfaces(codon["cgraph"])).to_json(
                        True
                    ),  # type: ignore
                    codon["pgc"],
                    tuple(ImportDef(**md) for md in base["imports"]),
                    base["inline"],
                    NULL_STR,
                    int(datetime.fromisoformat(codon["created"]).timestamp()),
                    codon["creator"].bytes,
                )

                new_codon = GGCDict(codon)
                new_codon.verify()
                codon = new_codon.to_json()
                assert valid_jcg(
                    codon["cgraph"]
                ), "Invalid codon connection graph after verification."

                if codon["signature"] in meta_codons:
                    raise ValueError(f"Duplicate meta codon signature: {codon['signature']}")
                meta_codons[codon["signature"]] = codon

    # If we are debugging verify the signatures are correct
    if _logger.isEnabledFor(DEBUG) and not write:
        codon_dict = {c["signature"]: c for c in load_signed_json_list(OUTPUT_CODON_PATH)}
        for sig, codon in meta_codons.items():
            assert sig in codon_dict, f"Codon signature {sig} not found in existing codons."
            del codon["updated"]  # Ignore updated timestamp for comparison
            del codon_dict[sig]["updated"]
            assert (
                codon == codon_dict[sig]
            ), f"Codon signature {sig} does not match existing codon definition."

    # Write the meta codons to the output file (optional)
    if write:
        dump_signed_json(list(meta_codons.values()), OUTPUT_CODON_PATH)

    _logger.log(DEBUG, "Meta codons generated successfully.")

    # Stop the spinner
    spinner.stop()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate meta codons.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_meta_codons(write=args.write)
