"""Test case for GGCDict class."""

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.ggc_class_factory import GGCDict
from tests.test_gc_types.ggc_test_base import GGCTestBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestGGCDict(GGCTestBase):
    """
    Test case for GGCDict class.
    Test cases are inherited from GGCTestBase.
    """

    ugc_type = GGCDict


if __name__ == "__main__":
    unittest.main()
