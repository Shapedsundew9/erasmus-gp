"""Bit dict definition for an EGP type."""

from typing import Any
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


TYPESDEF_CONFIG: dict[str, dict[str, Any]] = {
    "reserved_31": {
        "type": "bool",
        "start": 31,
        "width": 1,
        "default": False,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "tt": {
        "type": "uint",
        "start": 28,
        "width": 3,
        "default": 0,
        "description": "Template Type.",
        "valid": {"range": [(8,)]},
    },
    "reserved_27_16": {
        "type": "int",
        "start": 16,
        "width": 12,
        "default": 0,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "xuid": {
        "type": "uint",
        "start": 0,
        "width": 16,
        "default": 0,
        "description": "Single concrete type XUID.",
    }
}
