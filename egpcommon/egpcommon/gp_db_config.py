"""Gene Pool Database Configuration
This module contains the configuration for the Gene Pool database table.

The GP schema is used in egppy & egpdbmgr.
"""

from typing import Any

# Metadata has a dictionary structure with the following keys. The values
# are of type:
# - inline: str
# - imports: list[dict[str, str]]
# - code: str
# - io_map: dict[int, int]
META_DATA_KEYS = {"inline", "code", "imports", "io_map", "name", "description"}


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
    "creator": {"db_type": "UUID", "nullable": False, "phy_type": "UUID", "psql_type": "PsqlUUID"},
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
    "descendants": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
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
    "reference_count": {
        "db_type": "BIGINT",
        "nullable": False,
        "phy_type": "int",
        "psql_type": "PsqlBigInt",
    },
    "updated": {
        "db_type": "TIMESTAMP",
        "nullable": False,
        "phy_type": "datetime",
        "psql_type": "PsqlTimestamp",
    },
}
