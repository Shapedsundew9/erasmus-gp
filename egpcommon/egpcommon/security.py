"""Security functions for EGPPY."""

from io import TextIOWrapper
from json import dump, load
from uuid import UUID

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


def dump_signed_json(data: dict | list, fileptr: TextIOWrapper) -> None:
    """Dump a signed JSON file.

    Sign with this creator's UUID & signature and dump the JSON object.
    """
    # TODO: Implementation Needed
    dump(data, fileptr, indent=4, sort_keys=True)


def get_signature(creator: UUID) -> bytes:
    """Get the creators signature.
    May be the local creator, Erasmus, or a validated community creator.
    """
    return bytes()  # TODO: Implementation Needed


def load_signed_json(fileptr: TextIOWrapper) -> dict | list:
    """Load a signed JSON file.

    Validate that creator UUID and signature is correct and return the JSON object.
    """
    # TODO: Implementation Needed
    return load(fileptr)
