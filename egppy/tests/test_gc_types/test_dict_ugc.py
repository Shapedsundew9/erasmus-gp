"""Test case for UGCDict class."""
import unittest
from egppy.gc_types.ugc_class_factory import UGCDict
from tests.test_gc_types.ugc_test_base import UGCTestBase
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestUGCDict(UGCTestBase):
    """
    Test case for UGCDict class.
    Test cases are inherited from UGCTestBase.
    """
    ugc_type = UGCDict


if __name__ == '__main__':
    unittest.main()
