"""Bit dict definition for an EGP type."""

from typing import Any

from egpcommon.egp_log import Logger, egp_logger

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


TYPESDEF_CONFIG: dict[str, dict[str, Any]] = {
    "reserved_31": {
        "type": "bool",
        "start": 31,
        "width": 1,
        "default": False,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "reserved_30_16": {
        "type": "int",
        "start": 16,
        "width": 15,
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
    },
}
