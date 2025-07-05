"""Tests for the GC Store."""

from __future__ import annotations

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.worker.gc_store import CODON_SIGNATURES, GGC_CACHE

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GCStoreTestBase(unittest.TestCase):
    """
    Test base class for GC Store.
    """

    @classmethod
    def get_test_cls(cls) -> type[unittest.TestCase]:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith("TestBase")

    def setUp(self) -> None:
        # NOTE: The ggc_cache is a global object so it does not reset
        # between tests.
        self.cache = GGC_CACHE

    def test_cache(self) -> None:
        """Test the cache."""
        # if self.running_in_test_base_class():
        #    return
        for signature in CODON_SIGNATURES:
            self.cache[signature].verify()  # Pull them all in
        for signature in CODON_SIGNATURES:
            self.assertTrue(expr=signature in self.cache)
        self.cache.verify()
        self.cache.consistency()
