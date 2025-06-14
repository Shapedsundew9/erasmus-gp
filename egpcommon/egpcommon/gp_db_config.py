"""Gene Pool Database Configuration
This module contains the configuration for the Gene Pool database table.

The GP schema is used in egppy & egpdbmgr.
"""

from typing import Any, Callable
from egpcommon.conversions import (
    compress_json,
    decompress_json,
    encode_properties,
    decode_properties,
    list_int_to_bytes,
)

# GP GC Fields with Postgres definitions
EGC_KVT: dict[str, dict[str, Any]] = {
    "cgraph": {"db_type": "BYTEA", "nullable": False},
    "gca": {"db_type": "BYTEA", "nullable": True},
    "gcb": {"db_type": "BYTEA", "nullable": True},
    "ancestora": {"db_type": "BYTEA", "nullable": True},
    "ancestorb": {"db_type": "BYTEA", "nullable": True},
    "pgc": {"db_type": "BYTEA", "nullable": True},
    "created": {"db_type": "TIMESTAMP", "nullable": False},
    "properties": {"db_type": "BIGINT", "nullable": False},
    "signature": {"db_type": "BYTEA", "nullable": False},
}
GGC_KVT: dict[str, dict[str, Any]] = EGC_KVT | {
    "_e_count": {"db_type": "INT", "nullable": False},
    "_e_total": {"db_type": "FLOAT", "nullable": False},
    "_evolvability": {"db_type": "FLOAT", "nullable": False},
    "_f_count": {"db_type": "INT", "nullable": False},
    "_f_total": {"db_type": "FLOAT", "nullable": False},
    "_fitness": {"db_type": "FLOAT", "nullable": False},
    "_lost_descendants": {"db_type": "BIGINT", "nullable": False},
    "_reference_count": {"db_type": "BIGINT", "nullable": False},
    "code_depth": {"db_type": "INT", "nullable": False},
    "creator": {"db_type": "UUID", "nullable": False},
    "descendants": {"db_type": "BIGINT", "nullable": False},
    "e_count": {"db_type": "INT", "nullable": False},
    "e_total": {"db_type": "FLOAT", "nullable": False},
    "evolvability": {"db_type": "FLOAT", "nullable": False},
    "f_count": {"db_type": "INT", "nullable": False},
    "f_total": {"db_type": "FLOAT", "nullable": False},
    "fitness": {"db_type": "FLOAT", "nullable": False},
    "generation": {"db_type": "BIGINT", "nullable": False},
    "imports": {},  # Not persisted in the database but needed for execution
    "inline": {},  # Not persisted in the database but needed for execution
    "input_types": {"db_type": "INT[]", "nullable": False},
    "inputs": {"db_type": "BYTEA", "nullable": False},
    "lost_descendants": {"db_type": "BIGINT", "nullable": False},
    "meta_data": {"db_type": "BYTEA", "nullable": True},
    "num_codes": {"db_type": "INT", "nullable": False},
    "num_codons": {"db_type": "INT", "nullable": False},
    "num_inputs": {"db_type": "SMALLINT", "nullable": False},
    "num_outputs": {"db_type": "SMALLINT", "nullable": False},
    "output_types": {"db_type": "INT[]", "nullable": False},
    "outputs": {"db_type": "BYTEA", "nullable": False},
    "population_uid": {"db_type": "SMALLINT", "nullable": False},
    "problem": {"db_type": "BYTEA", "nullable": True},
    "problem_set": {"db_type": "BYTEA", "nullable": True},
    "reference_count": {"db_type": "BIGINT", "nullable": False},
    "survivability": {"db_type": "FLOAT", "nullable": False},
    "updated": {"db_type": "TIMESTAMP", "nullable": False},
}


# Note that encode conversions must produce a type that is compatible with the database type
# and decode conversions must produce a type that is compatible with the application type.
# The conversions *MUST* be symmetric i.e. encode followed by decode must produce the original
# value.
# {name, encode (output to DB), decode (output to application)}
CONVERSIONS: tuple[tuple[str, Callable | None, Callable | None], ...] = (
    ("graph", compress_json, decompress_json),
    ("meta_data", compress_json, decompress_json),
    ("properties", encode_properties, decode_properties),
    ("outputs", list_int_to_bytes, None),
    ("inputs", list_int_to_bytes, None),
)
