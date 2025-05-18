"""Bit dict definition for an EGP type."""

from typing import Any
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Types definition bit dict configuration
X_POS = 8
Y_POS = 0
X_MAX = 63
Y_MAX = 15
FX_MAX = 7

TT_RESERVED: dict[str, dict[str, Any]] = {
    "reserved_tt": {
        "type": "uint",
        "start": 16,
        "width": 12,
        "description": "Reserved for future use.",
        "valid": {"value": {0}},
    },
    "xuid": {
        "type": "uint",
        "start": 0,
        "width": 16,
        "description": "Compound type XUID (TT > 0).",
    },
}

TYPESDEF_CONFIG: dict[str, dict[str, Any]] = {
    "reserved": {
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
    "ttsp": {
        "type": "bitdict",
        "start": 0,
        "width": 28,
        "selector": "tt",
        "description": "Template Type specific properties.",
        "subtype": [
            {
                "io": {
                    "type": "bool",
                    "start": 27,
                    "width": 1,
                    "description": "Wildcard types.",
                    "default": False,
                    "valid": {"range": [(2,)]},
                },
                "iosp": {
                    "type": "bitdict",
                    "start": 0,
                    "width": 27,
                    "description": "IO specific properties.",
                    "selector": "io",
                    "subtype": [
                        {
                            "fx": {
                                "type": "uint",
                                "start": 24,
                                "width": 3,
                                "description": "Fixed set.",
                                "default": 0,
                                "valid": {"range": [(FX_MAX + 1,)]},
                            },
                            "reserved": {
                                "type": "uint",
                                "start": 16,
                                "width": 8,
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
                        },
                        {
                            "reserved": {
                                "type": "uint",
                                "start": 16,
                                "width": 11,
                                "default": 0,
                                "description": "Reserved for future use.",
                                "valid": {"value": {0}},
                            },
                            "reserved_x": {
                                "type": "uint",
                                "start": 14,
                                "width": 2,
                                "default": 0,
                                "description": "Reserved for future use.",
                                "valid": {"value": {0}},
                            },
                            "x": {
                                "type": "uint",
                                "start": X_POS,
                                "width": 6,
                                "description": "X coordinate.",
                                "default": 0,
                                "valid": {"range": [(X_MAX + 1,)]},
                            },
                            "reserved_y": {
                                "type": "uint",
                                "start": 4,
                                "width": 4,
                                "default": 0,
                                "description": "Reserved for future use.",
                                "valid": {"value": {0}},
                            },
                            "y": {
                                "type": "uint",
                                "start": Y_POS,
                                "width": 4,
                                "description": "Y coordinate.",
                                "default": 0,
                                "valid": {"range": [(Y_MAX + 1,)]},
                            },
                        },
                    ],
                },
            },
            TT_RESERVED,
            TT_RESERVED,
            TT_RESERVED,
            TT_RESERVED,
            TT_RESERVED,
            TT_RESERVED,
            TT_RESERVED,
        ],
    },
}
