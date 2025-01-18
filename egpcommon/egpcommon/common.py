"""Common functions for the EGPPY package."""

from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from pprint import pformat
from typing import Any, Self
from uuid import UUID
from json import dumps

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# When  it all began...
EGP_EPOCH = datetime(year=2019, month=12, day=25, hour=16, minute=26, second=0, tzinfo=UTC)


# Constants
NULL_SHA256: bytes = b"\x00" * 32
NULL_SHA256_STR = NULL_SHA256.hex()
NULL_UUID: UUID = UUID(int=0)
NULL_TUPLE = tuple()


# PROPERTIES must define the bit position of all the properties listed in
# the "properties" field of the entry_format.json definition.
PROPERTIES: dict[str, int] = {
    "constant": 1 << 0,
    "deterministic": 1 << 1,
    "simplification": 1 << 2,
    "literal": 1 << 3,
    "abstract": 1 << 4,
}


# GC Fields with Postgres definitions
EGC_KVT: dict[str, dict[str, Any]] = {
    "graph": {"db_type": "BYTEA", "nullable": False},
    "gca": {"db_type": "BYTEA", "nullable": True},
    "gcb": {"db_type": "BYTEA", "nullable": True},
    "ancestora": {"db_type": "BYTEA", "nullable": True},
    "ancestorb": {"db_type": "BYTEA", "nullable": True},
    "pgc": {"db_type": "BYTEA", "nullable": True},
    "signature": {"db_type": "BYTEA", "nullable": False},
    "num_lines": {},
    "executable": {}
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
    "codon_depth": {"db_type": "INT", "nullable": False},
    "created": {"db_type": "TIMESTAMP", "nullable": False},
    "descendants": {"db_type": "BIGINT", "nullable": False},
    "e_count": {"db_type": "INT", "nullable": False},
    "e_total": {"db_type": "FLOAT", "nullable": False},
    "evolvability": {"db_type": "FLOAT", "nullable": False},
    "f_count": {"db_type": "INT", "nullable": False},
    "f_total": {"db_type": "FLOAT", "nullable": False},
    "fitness": {"db_type": "FLOAT", "nullable": False},
    "generation": {"db_type": "BIGINT", "nullable": False},
    "input_types": {"db_type": "SMALLINT[]", "nullable": False},
    "inputs": {"db_type": "BYTEA", "nullable": False},
    "lost_descendants": {"db_type": "BIGINT", "nullable": False},
    "meta_data": {"db_type": "BYTEA", "nullable": True},
    "num_codes": {"db_type": "INT", "nullable": False},
    "num_codons": {"db_type": "INT", "nullable": False},
    "num_inputs": {"db_type": "SMALLINT", "nullable": False},
    "num_outputs": {"db_type": "SMALLINT", "nullable": False},
    "output_types": {"db_type": "SMALLINT[]", "nullable": False},
    "outputs": {"db_type": "BYTEA", "nullable": False},
    "population_uid": {"db_type": "SMALLINT", "nullable": False},
    "problem": {"db_type": "BYTEA", "nullable": True},
    "problem_set": {"db_type": "BYTEA", "nullable": True},
    "properties": {"db_type": "BIGINT", "nullable": False},
    "reference_count": {"db_type": "BIGINT", "nullable": False},
    "survivability": {"db_type": "FLOAT", "nullable": False},
    "updated": {"db_type": "TIMESTAMP", "nullable": False},
}


# Local Constants
_RESERVED_FILE_NAMES: set[str] = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
def merge(  # pylint: disable=dangerous-default-value
    dict_a: dict[Any, Any],
    dict_b: dict[Any, Any],
    path: list[str] = [],
    no_new_keys: bool = False,
    update=False,
) -> dict[Any, Any]:
    """Merge dict b into a recursively. a is modified.
    This function is equivilent to a.update(b) unless update is False in which case
    if b contains dictionary differing values with the same key a ValueError is raised.
    If there are dictionaries
    in b that have the same key as a then those dictionaries are merged in the same way.
    Keys in a & b (or common key'd sub-dictionaries) where one is a dict and the other
    some other type raise an exception.

    Args
    ----
    a: Dictionary to merge in to.
    b: Dictionary to merge.
    no_new_keys: If True keys in b that are not in a are ignored
    update: When false keys with non-dict values that differ will raise an error.

    Returns
    -------
    a (modified)
    """
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                merge(dict_a[key], dict_b[key], path + [str(key)], no_new_keys, update)
            elif dict_a[key] == dict_b[key]:
                pass  # same leaf value
            elif not update:
                raise ValueError(f"Conflict at {'.'.join(path + [str(key)])}")
            else:
                dict_a[key] = dict_b[key]
        elif not no_new_keys:
            dict_a[key] = dict_b[key]
    return dict_a


def sha256_signature(
    gca: bytes, gcb: bytes, graph: dict[str, Any], meta_data: dict[str, Any] | None
) -> bytes:
    """Return the SHA256 signature of the data.
    This function is the basis for identifying *EVERYTHING* in the EGP system.
    The signature is based on the graph, the gca, and the gcb. If the meta_data
    is provided then the function code is also included in the signature..
    This function must not change!

    Make sure the unit tests pass!
    """
    hash_obj = sha256(gca)
    hash_obj.update(gcb)
    hash_obj.update(pformat(graph, compact=True).encode())
    if meta_data is not None and "function" in meta_data:
        definition =  meta_data["function"]["python3"]["0"]
        hash_obj.update(definition["inline"].encode())
        if "code" in definition:
            hash_obj.update(definition["code"].encode())
        if "imports" in definition:
            for import_def in definition["imports"]:
                hash_obj.update(dumps(import_def.to_json()).encode())
    return hash_obj.digest()


class DictTypeAccessor:
    """Provide very simple get/set dictionary like access to an objects members."""

    def __contains__(self, key: str) -> bool:
        """Check if the attribute exists."""
        return hasattr(self, key)

    def __eq__(self, value: object) -> bool:
        """Check if the object is equal to the value."""
        if not isinstance(value, self.__class__):
            return False
        return self.__dict__ == value.__dict__

    def __getitem__(self, key: str) -> Any:
        """Get the value of the attribute."""
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set the value of the attribute."""
        setattr(self, key, value)

    def copy(self) -> Self:
        """Return a dictionary of the object."""
        return deepcopy(self)

    def get(self, key: str, default: Any = None) -> Any:
        """Get the value of the attribute."""
        return getattr(self, key, default)

    def setdefault(self, key: str, default: Any) -> Any:
        """Get the value of the attribute."""
        if hasattr(self, key):
            return getattr(self, key)
        setattr(self, key, default)
        return default
