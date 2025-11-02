"""Gene Pool Database Configuration
This module contains the configuration for the Gene Pool database table.

The GP schema is used in egppy & egpdbmgr.
"""

from json import dump
from os.path import dirname, join
from typing import Any

# GP GC Fields with Postgres definitions.
# {
#   column_name: {
#       "db_type": Postgres data type as string,
#       "nullable": bool, (DB column is nullable)
#       "phy_type": physical type as string (found in pgc_api.py),
#       "psql_type": corresponding PSQL type as string,
#       "signature": bool (if the field is a signature - used for conversions)
#   }
# }
EGC_KVT: dict[str, dict[str, Any]] = {
    "cgraph": {
        "db_type": "BYTEA",
        "nullable": False,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
    },
    "gca": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "gcb": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "ancestora": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "ancestorb": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "pgc": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "created": {
        "db_type": "TIMESTAMP",
        "nullable": False,
        "phy_type": "datetime",
        "psql_type": "PsqlTimestamp",
    },
    "properties": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "signature": {
        "db_type": "BYTEA",
        "nullable": False,
        "primary_key": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
}
GGC_KVT: dict[str, dict[str, Any]] = EGC_KVT | {
    "_e_count": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "_e_total": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "_evolvability": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "_f_count": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "_f_total": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "_fitness": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "_lost_descendants": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "_reference_count": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "code": {},  # Not persisted in the database but needed for execution
    "code_depth": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "creator": {"db_type": "UUID", "nullable": False, "phy_type": "UUID", "psql_type": "PsqlUUID"},
    "descendants": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "e_count": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "e_total": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "evolvability": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "f_count": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "f_total": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "fitness": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "generation": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "imports": {},  # Not persisted in the database but needed for execution
    "inline": {},  # Not persisted in the database but needed for execution
    "input_types": {
        "db_type": "INT[]",
        "nullable": False,
        "phy_type": "list[int]",
        "psql_type": "PsqlIntArray",
    },
    "inputs": {
        "db_type": "BYTEA",
        "nullable": False,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
    },
    "lost_descendants": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "meta_data": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
    },
    "num_codes": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "num_codons": {"db_type": "INT", "nullable": False, "phy_type": "int", "psql_type": "PsqlInt"},
    "num_inputs": {
        "db_type": "SMALLINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlSmallInt",
    },
    "num_outputs": {
        "db_type": "SMALLINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlSmallInt",
    },
    "output_types": {
        "db_type": "INT[]",
        "nullable": False,
        "phy_type": "list[int]",
        "psql_type": "PsqlIntArray",
    },
    "outputs": {
        "db_type": "BYTEA",
        "nullable": False,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
    },
    "population_uid": {
        "db_type": "SMALLINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlSmallInt",
    },
    "problem": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "problem_set": {
        "db_type": "BYTEA",
        "nullable": True,
        "phy_type": "bytes",
        "psql_type": "PsqlBytea",
        "signature": True,
    },
    "reference_count": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "survivability": {
        "db_type": "FLOAT",
        "nullable": False,
        "phy_type": "float",
        "psql_type": "PsqlDoublePrecision",
    },
    "updated": {
        "db_type": "TIMESTAMP",
        "nullable": False,
        "phy_type": "datetime",
        "psql_type": "PsqlTimestamp",
    },
}


GCABC_PSQL_COLUMN_TEMPLATE: dict[str, Any] = {
    "description": "GCABC {name} PSQL column",
    "inputs": [],
    "outputs": "{psql_type}",
    "inline": "{psql_type}('{name}', is_column=True)",
    "properties": {"gctsp": {"python": False, "psql": True}},
}
GCABC_PY_GET_TEMPLATE: dict[str, Any] = {
    "description": "GCABC {name} Python field extraction",
    "inputs": ["GCABC"],
    "outputs": "{phy_type}",
    "inline": "{{i0}}['{name}']",
}


def generate_gcabc_py_json(write: bool = False):
    """Generate the GCABC JSON schema for Python.
    This is a convenience function to generate the GCABC JSON schema used in egpseed.
    It is only used during development and testing.
    """

    codon_templates: dict[str, dict[str, Any]] = {}
    for key, val in ((k, v) for k, v in GGC_KVT.items() if "phy_type" in v):
        codon_templates[key] = {
            "description": GCABC_PY_GET_TEMPLATE["description"].format(name=key),
            "inputs": ["EGCode"] if key in EGC_KVT else ["GGCode"],
            "outputs": [GCABC_PY_GET_TEMPLATE["outputs"].format(phy_type=val["phy_type"])],
            "inline": GCABC_PY_GET_TEMPLATE["inline"].format(name=key),
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


def generate_gcabc_psql_json(write: bool = False):
    """Generate the GCABC JSON schema for PSQL.
    This is a convenience function to generate the GCABC JSON schema used in egpseed.
    It is only used during development and testing.
    """

    codon_templates: dict[str, dict[str, Any]] = {}
    for key, val in ((k, v) for k, v in GGC_KVT.items() if "psql_type" in v):
        codon_templates[key] = {
            "description": GCABC_PSQL_COLUMN_TEMPLATE["description"].format(name=key),
            "inputs": GCABC_PSQL_COLUMN_TEMPLATE["inputs"],
            "outputs": [GCABC_PSQL_COLUMN_TEMPLATE["outputs"].format(psql_type=val["psql_type"])],
            "inline": GCABC_PSQL_COLUMN_TEMPLATE["inline"].format(
                name=key, psql_type=val["psql_type"]
            ),
            "properties": GCABC_PSQL_COLUMN_TEMPLATE["properties"],
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
            "psql",
            "_GCABC.json",
        )

        with open(filename, "w", encoding="utf-8") as f:
            dump(codon_templates, f, indent=4, sort_keys=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate _GCABC.json.")
    parser.add_argument(
        "--write", "-w", action="store_true", help="If set, write the codons to a JSON file."
    )
    args = parser.parse_args()
    generate_gcabc_py_json(write=args.write)
    generate_gcabc_psql_json(write=args.write)
