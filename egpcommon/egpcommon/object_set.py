"""ObjectSet class.

A object set is a set of unique objects that may be referenced
in many places. The intent is to reduce memory consumption when a lot of duplicate
objects are used in a program.
"""

from typing import Any
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.object_dict import ObjectDict

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ObjectSet(ObjectDict):
    """ObjectSet class. See ObjectDict for details."""

    # pylint: disable=arguments-differ
    def add(self, obj: Any) -> Any:  # type: ignore
        """Add a object to the set."""
        return super().add(obj, obj)
