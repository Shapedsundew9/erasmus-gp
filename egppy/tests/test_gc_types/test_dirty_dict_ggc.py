"""Tests for the GGCDirtyDict class."""
import unittest
from egppy.gc_types.ggc_class_factory import GGCDirtyDict
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger
from tests.test_gc_types.ggc_test_base import GGCTestBase


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class TestGGCDirtyDict(GGCTestBase):
    """
    Test case for GGCDirtyDict class.
    Test cases are inherited from GGCTestBase.
    """
    ugc_type = GGCDirtyDict

    def test_clean(self) -> None:
        """
        Test the clean method.
        """
        self.ggc['key'] = 'value'
        self.ggc.dirty()
        self.assertTrue(expr=self.ggc.is_dirty())
        self.ggc.clean()
        # Dirty objects are never clean
        self.assertTrue(expr=self.ggc.is_dirty())

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        self.ggc['key'] = 'value'
        value = self.ggc.setdefault('key', 'default')
        self.assertEqual(first=value, second='value')
        value = self.ggc.setdefault('new_key', 'default')
        self.assertEqual(first=value, second='default')

    def test_update(self) -> None:
        """
        Test the update method.
        """
        self.ggc['key1'] = 'value1'
        self.ggc.update({'key2': 'value2', 'key3': 'value3'})
        self.assertEqual(first=self.ggc['key2'], second='value2')
        self.assertEqual(first=self.ggc['key3'], second='value3')


if __name__ == '__main__':
    unittest.main()
