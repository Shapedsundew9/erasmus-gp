"""Common functions for the EGPPY package."""

from collections.abc import Sequence
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from json import dump, dumps, load
from os import environ
from pathlib import Path
from pprint import pformat
from random import randint
from typing import Any, Literal, Self
from uuid import UUID

from egpcommon.egp_log import Logger, egp_logger
from egpcommon.parallel_exceptions import create_parallel_exceptions

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Create the Debug exception hierarchy
# A debug exception hierarchy is needed to differenciate from when there is an error
# in the EGP application versus an error in the generated code that calls the PGC API.
# A complete set of parallel standard exceptions is created for this purpose. e.g.
# debug_exceptions.DebugValueError, debug_exceptions.DebugTypeError,
# debug_exceptions.DebugRuntimeError etc.
debug_exceptions = create_parallel_exceptions(prefix="Debug", verbose=False)

# When  it all began...
EGP_EPOCH = datetime(year=2019, month=12, day=25, hour=16, minute=26, second=0, tzinfo=UTC)
ANONYMOUS_CREATOR = UUID("1f8f45ca-0ce8-11f0-a067-73ab69491a6f")
SHAPEDSUNDEW9_UUID = UUID("22c23596-df90-4b87-88a4-9409a0ea764f")

# The beginning
# Acybergenesis: https://g.co/gemini/share/101495090943
ACYBERGENESIS_PROBLEM = sha256(b"Acybergenesis Problem").digest()


# Set the EGP profile.
# This is used to determine the environment in which the code is running and
# configure such things as the type of stores to use, how much memory to allocate
# etc.
EGP_DEV_PROFILE = "DEV"
EGP_CI_PROFILE = "CI"
EGP_PROD_PROFILE = "PROD"
EGP_PROFILE: str = environ.get("EGP_PROFILE", "PROD")
assert EGP_PROFILE in (EGP_DEV_PROFILE, EGP_CI_PROFILE, EGP_PROD_PROFILE)


# Some common types
JSONDictType = dict[str, list | dict | int | str | float | bool | None]
JSONListType = list[dict | list | int | str | float | bool | None]
JSONType = JSONDictType | JSONListType


# Constants
NULL_SHA256: bytes = b"\x00" * 32
NULL_SHA256_STR: str = NULL_SHA256.hex()
NULL_UUID: UUID = UUID(int=0)
NULL_TUPLE: tuple = tuple()
NULL_STR: Literal[""] = ""
NULL_FROZENSET: frozenset = frozenset()


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
    imports: tuple,  # tuple[ImportDef, ...] but would be a circular reference
    inline: str,
    code: str,
    created: int,
    creator: bytes,
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
    # The graph must be in a consistent format & order.
    # See CGraph.py CGraph.to_json() for details.
    hash_obj.update(pformat(graph, compact=True).encode())
    if inline:
        hash_obj.update(inline.encode())
        hash_obj.update(code.encode())
        for import_def in imports:
            hash_obj.update(dumps(import_def.to_json()).encode())
    if created > 0:
        hash_obj.update(created.to_bytes(8, "big"))
    return hash_obj.digest()


class DictTypeAccessor:
    """Provide very simple get/set dictionary like access to an objects members."""

    __slots__ = tuple()

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


def ensure_sorted_json_keys(file_path: Path | str) -> None:
    """Load a JSON file, validate it, and ensure keys are sorted.

    This function loads a JSON file, checks that it's a dictionary with string keys,
    verifies if the keys are in sorted order, and rewrites the file with sorted keys
    if necessary.

    Args
    ----
    file_path: Path to the JSON file to check and potentially sort.

    Raises
    ------
    FileNotFoundError: If the file does not exist.
    ValueError: If the JSON content is not a dictionary or if any key is not a string.
    json.JSONDecodeError: If the file does not contain valid JSON.
    """
    # Convert to Path object if string
    path = Path(file_path) if isinstance(file_path, str) else file_path

    # Load the JSON file
    with path.open("r", encoding="utf-8") as file:
        data = load(file)

    # Validate that it's a dictionary
    if not isinstance(data, dict):
        raise ValueError(f"JSON file {path} must contain a dictionary at the root level")

    # Validate that all keys are strings
    for key in data.keys():
        if not isinstance(key, str):
            raise ValueError(f"All keys must be strings, found {type(key).__name__}: {key}")

    # Check if keys are already sorted
    keys = list(data.keys())
    sorted_keys = sorted(keys)

    # If keys are not in sorted order, rewrite the file
    if keys != sorted_keys:
        _logger.info("Rewriting %s with sorted keys", path)
        sorted_data = {key: data[key] for key in sorted_keys}

        with path.open("w", encoding="utf-8") as file:
            dump(sorted_data, file, indent=2, ensure_ascii=False)
            file.write("\n")  # Add trailing newline

        _logger.info("Successfully sorted keys in %s", path)
    else:
        _logger.debug("Keys in %s are already sorted", path)
