"""Common functions for the EGPPY package."""

from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from pprint import pformat
from typing import Any, Literal, Self
from uuid import UUID
from json import dumps
from collections.abc import Sequence
from random import randint
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# When  it all began...
EGP_EPOCH = datetime(year=2019, month=12, day=25, hour=16, minute=26, second=0, tzinfo=UTC)
ANONYMOUS_CREATOR = UUID("1f8f45ca-0ce8-11f0-a067-73ab69491a6f")


# Constants
NULL_SHA256: bytes = b"\x00" * 32
NULL_SHA256_STR: str = NULL_SHA256.hex()
NULL_UUID: UUID = UUID(int=0)
NULL_TUPLE: tuple = tuple()
NULL_STR: Literal[""] = ""
NULL_FROZENSET: frozenset = frozenset()


# GC Fields with Postgres definitions
EGC_KVT: dict[str, dict[str, Any]] = {
    "graph": {"db_type": "BYTEA", "nullable": False},
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
    ancestora: bytes,
    ancestorb: bytes,
    gca: bytes,
    gcb: bytes,
    graph: dict[str, Any],
    pgc: bytes,
    meta_data: dict[str, Any] | None,
    created: int,
    creator: bytes
) -> bytes:
    """Return the SHA256 signature of the data.
    This function is the basis for identifying *EVERYTHING* in the EGP system.
    The signature is based on the functional elements of the GC *and* the lineage.
    Whilst this means that (theoretically) two GCs with the same function but different
    lineages will have different signatures, this is only even remotely likely
    to occur in very early generations and one variant will then dominate.
    Lineage is part of the signature to ensure traceablity of the origins of the GC through
    the mutuation process. The creation time is captured as this is the seed for the random
    number generator used to create the GC. All this combined means it is possible to
    deterministically recreate the GC from the ancestors and know if the GC can be trusted.
    If the meta_data is provided then the function code is also included in the signature.

    If created > 0 then the created time is encoded in the signature. Note that
    this is used to indicate that the created time should be part of the signature.
    It is a convenience when developing with primitives that get re-generated regularly
    where the changing signature is overhead.

    NOTE: Created is the creation time of the GC in seconds from epoch when > 0

    THIS FUNCTION MUST NOT CHANGE!
    MAKE SURE THE UNIT TESTS PASS!
    """
    hash_obj = sha256(ancestora)
    hash_obj.update(ancestorb)
    hash_obj.update(gca)
    hash_obj.update(gcb)
    hash_obj.update(pgc)
    hash_obj.update(creator)
    hash_obj.update(pformat(graph, compact=True).encode())
    if meta_data is not None and "function" in meta_data:
        definition = meta_data["function"]["python3"]["0"]
        hash_obj.update(definition["inline"].encode())
        if "code" in definition:
            hash_obj.update(definition["code"].encode())
        if "imports" in definition:
            for import_def in definition["imports"]:
                hash_obj.update(dumps(import_def.to_json()).encode())
    if created > 0:
        hash_obj.update(created.to_bytes(8, "big"))
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


def bin_counts(data: Sequence[int], bin_width: int = 10) -> list[int]:
    """
    Calculates the bin counts for a list of integers, starting at 0.

    Args:
        data: A list of integers.
        bin_width: The width of each bin.

    Returns:
        A list of bin counts.
    """
    if not data:
        return []

    max_value = max(data)
    num_bins = (max_value // bin_width) + 1  # Calculate the number of bins needed
    bin_counts_list = [0] * num_bins  # Initialize bin counts to 0

    for value in data:
        bin_index = value // bin_width  # Determine the bin index for each value
        bin_counts_list[bin_index] += 1

    return bin_counts_list


def random_int_tuple_generator(n: int, x: int) -> tuple[int, ...]:
    """
    Generates a tuple of N random integers between 0 and X (exclusive)
    using a generator expression.

    Args:
      n: The number of random integers (tuple length). Must be non-negative.
      x: The maximum value for the random integers (exclusive). Must be non-negative.

    Returns:
      A tuple containing N random integers.

    Raises:
      ValueError: If n or x is negative.
    """
    if n < 0:
        raise ValueError("Number of elements (n) cannot be negative")
    if x < 1:
        # random.randint(0, x) would raise ValueError if x < 1,
        # but explicit check is clearer.
        raise ValueError("Maximum value (x) must be at least 1 for range [0, x)")
    if n == 0:
        return ()  # Return empty tuple immediately if n is 0

    # random.randint(a, b) includes both endpoints a and b.
    return tuple(randint(0, x - 1) for _ in range(n))
