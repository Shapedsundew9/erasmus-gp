"""Security functions for EGPPY."""

from json import dump, load
from os.path import getsize
from uuid import UUID

from black.debug import T

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# JSON filesize limit
JSON_FILESIZE_LIMIT = 2**30  # 1 GB


def dump_signed_json(data: dict | list, fullpath: str) -> None:
    """Dump a signed JSON file.

    The most compact JSON format is used to reduce file size. The assumption is that
    the file, if viewed will be done with a JSON capable viewer.
    Sign with this creator's UUID & signature and dump the JSON object.
    """
    # TODO: Implementation Needed
    with open(fullpath, "w", encoding="utf-8") as f:
        dump(data, f, indent=2, sort_keys=True, ensure_ascii=True)
    # Prevents continuing with a file we can't read
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)


def _file_size_limit(fullpath: str, limit: int = 2**30) -> int:
    """Check if the file size is within the limit."""
    size = getsize(fullpath)
    if size > limit:
        raise ValueError(f"File {fullpath} size {size} exceeds limit {limit}.")
    return size


def validate_json_signature(fullpath: str) -> bool:
    """Validate the JSON file signature.
    EGP JSON files are always a list. The first element of the list is the
    data and the second element is the signature.
    No matter how the data is formatted the signed JSON always has this format:
    [
    <data object>,
    "lowercase hexadecimal signature[64]",
    ]
    The signature is thus always characters 1 to 64 inclusive of the penultimate line.
    The signature is the signed sha256 hash of characters from the start of the file to
    the end of the antepenultimate line inclusive (i.e. including the comma after
    the data object).
    Validation ensures that the format of the signature line and the last line are exact.
    """
    # TODO: Implementation Needed
    return True


def get_signature(creator: UUID) -> bytes:
    """Get the creators signature.
    May be the local creator, Erasmus, or a validated community creator.
    """
    return bytes()  # TODO: Implementation Needed


def load_signed_json(fullpath: str) -> dict | list:
    """Load a signed JSON file.

    Validate that creator UUID and signature is correct and return the JSON object.
    """
    _file_size_limit(fullpath, JSON_FILESIZE_LIMIT)
    with open(fullpath, "r", encoding="ascii") as fileptr:
        return load(fileptr)


def load_signed_json_dict(fullpath: str) -> dict:
    """Load a signed JSON file as a dictionary."""
    data = load_signed_json(fullpath)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a dictionary, got {type(data)}")
    return data


def load_signed_json_list(fullpath: str) -> list:
    """Load a signed JSON file as a list."""
    data = load_signed_json(fullpath)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list, got {type(data)}")
    return data
