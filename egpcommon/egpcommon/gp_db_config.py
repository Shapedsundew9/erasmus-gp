"""Gene Pool Database Configuration
This module contains the configuration for the Gene Pool database table.

The GP schema is used in egppy & egpdbmgr.
"""

from json import dump
from os.path import dirname, join
from typing import Any

from egpcommon.common import ACYBERGENESIS_PROBLEM, EGP_EPOCH, NULL_SHA256
from egpcommon.properties import CGraphType, GCType

# GP GC Fields with Postgres definitions. Value dicts must be compatible
# with a ColumnSchema
EGC_KVT: dict[str, dict[str, Any]] = {
    "cgraph": {"db_type": "BYTEA", "nullable": False, "phy_type": "CGraph"},
    "gca": {"db_type": "BYTEA", "nullable": True, "phy_type": "GCASig"},
    "gcb": {"db_type": "BYTEA", "nullable": True, "phy_type": "GCBSig"},
    "ancestora": {"db_type": "BYTEA", "nullable": True, "phy_type": "AncestorASig"},
    "ancestorb": {"db_type": "BYTEA", "nullable": True, "phy_type": "AncestorBSig"},
    "pgc": {"db_type": "BYTEA", "nullable": True, "phy_type": "PGCSig"},
    "created": {"db_type": "TIMESTAMP", "nullable": False, "phy_type": "Created"},
    "properties": {"db_type": "BIGINT", "nullable": False, "phy_type": "PropertiesInt"},
    "signature": {
        "db_type": "BYTEA",
        "nullable": False,
        "primary_key": True,
        "phy_type": "GCSig",
    },
}
GGC_KVT: dict[str, dict[str, Any]] = EGC_KVT | {
    "_e_count": {"db_type": "INT", "nullable": False, "phy_type": "ECountHL"},
    "_e_total": {"db_type": "FLOAT", "nullable": False, "phy_type": "ETotalHL"},
    "_evolvability": {"db_type": "FLOAT", "nullable": False, "phy_type": "EvolvabilityHL"},
    "_f_count": {"db_type": "INT", "nullable": False, "phy_type": "FCountHL"},
    "_f_total": {"db_type": "FLOAT", "nullable": False, "phy_type": "FTotalHL"},
    "_fitness": {"db_type": "FLOAT", "nullable": False, "phy_type": "FitnessHL"},
    "_lost_descendants": {"db_type": "BIGINT", "nullable": False, "phy_type": "LostDescendantsHL"},
    "_reference_count": {"db_type": "BIGINT", "nullable": False, "phy_type": "ReferenceCountHL"},
    "code": {},  # Not persisted in the database but needed for execution
    "code_depth": {"db_type": "INT", "nullable": False, "phy_type": "CodeDepth"},
    "creator": {"db_type": "UUID", "nullable": False, "phy_type": "Creator"},
    "descendants": {"db_type": "BIGINT", "nullable": False, "phy_type": "Descendants"},
    "e_count": {"db_type": "INT", "nullable": False, "phy_type": "ECountCL"},
    "e_total": {"db_type": "FLOAT", "nullable": False, "phy_type": "ETotalCL"},
    "evolvability": {"db_type": "FLOAT", "nullable": False, "phy_type": "EvolvabilityCL"},
    "f_count": {"db_type": "INT", "nullable": False, "phy_type": "FCountCL"},
    "f_total": {"db_type": "FLOAT", "nullable": False, "phy_type": "FTotalCL"},
    "fitness": {"db_type": "FLOAT", "nullable": False, "phy_type": "FitnessCL"},
    "generation": {"db_type": "BIGINT", "nullable": False, "phy_type": "Generation"},
    "imports": {},  # Not persisted in the database but needed for execution
    "inline": {},  # Not persisted in the database but needed for execution
    "input_types": {"db_type": "INT[]", "nullable": False, "phy_type": "ITypes"},
    "inputs": {"db_type": "BYTEA", "nullable": False, "phy_type": "IIndices"},
    "lost_descendants": {"db_type": "BIGINT", "nullable": False, "phy_type": "LostDescendantsCL"},
    "meta_data": {"db_type": "BYTEA", "nullable": True},
    "num_codes": {"db_type": "INT", "nullable": False, "phy_type": "NumCodes"},
    "num_codons": {"db_type": "INT", "nullable": False, "phy_type": "NumCodons"},
    "num_inputs": {"db_type": "SMALLINT", "nullable": False, "phy_type": "NumInputs"},
    "num_outputs": {"db_type": "SMALLINT", "nullable": False, "phy_type": "NumOutputs"},
    "output_types": {"db_type": "INT[]", "nullable": False, "phy_type": "OTypes"},
    "outputs": {"db_type": "BYTEA", "nullable": False, "phy_type": "OIndices"},
    "population_uid": {"db_type": "SMALLINT", "nullable": False, "phy_type": "PopulationUID"},
    "problem": {"db_type": "BYTEA", "nullable": True, "phy_type": "ProblemSig"},
    "problem_set": {"db_type": "BYTEA", "nullable": True, "phy_type": "ProblemSetSig"},
    "reference_count": {"db_type": "BIGINT", "nullable": False, "phy_type": "ReferenceCountCL"},
    "survivability": {"db_type": "FLOAT", "nullable": False, "phy_type": "Survivability"},
    "updated": {"db_type": "TIMESTAMP", "nullable": False, "phy_type": "Updated"},
}


GCABC_GET_TEMPLATE: dict[str, Any] = {
    "description": "GCABC {name} field extraction",
    "inputs": ["GCABC"],
    "outputs": "{phy_type}",
    "inline": "{{i0}}['{name}']",
}
GCABC_META_TEMPLATE: dict[str, Any] = {
    "description": "GCABC {phy_type} conversion to PSQL type {psql_type}",
    "inputs": "{phy_type}",
    "outputs": "{psql_type}",
    "code_depth": 1,
    "cgraph": {"A": [["I", 0, None]], "O": [["A", 0, None]], "U": []},
    "gca": NULL_SHA256,
    "gcb": NULL_SHA256,
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


def generate_gcabc_json(write: bool = False) -> dict[str, Any]:
    """Generate the GCABC JSON schema.
    This is a convenience function to generate the GCABC JSON schema used in egpseed.
    It is only used during development and testing.
    """

    codon_templates: dict[str, dict[str, Any]] = {}
    for key, val in ((k, v) for k, v in GGC_KVT.items() if "phy_type" in v):
        codon_templates[key] = {
            "description": GCABC_GET_TEMPLATE["description"].format(name=key),
            "inputs": GCABC_GET_TEMPLATE["inputs"],
            "outputs": [GCABC_GET_TEMPLATE["outputs"].format(phy_type=val["phy_type"])],
            "inline": GCABC_GET_TEMPLATE["inline"].format(name=key),
        }

    if write:

        filename = join(
            dirname(__file__),
            "..",
            "..",
            "egpseed",
            "egpseed",
            "data",
            "languages",
            "python",
            "_GCABC.json",
        )

        with open(filename, "w", encoding="utf-8") as f:
            dump(codon_templates, f, indent=4, sort_keys=True)
    return GCABC_GET_TEMPLATE


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate _GCABC.json.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_gcabc_json(write=args.write)
