"""
Docstring for tests.test_egpseed.test_primordial_boost
"""

from unittest import TestCase

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.physics.runtime_context import RuntimeContext
from egppy.worker.executor.execution_context import ExecutionContext
from egpseed.primordial_boost import load_codons, random_codon_selector_gc
from egpseed.primordial_python import random_codon_selector_py


class TestPrimordialBoost(TestCase):
    """
    Test case for primordial boost functionality.
    """

    @classmethod
    def setUpClass(cls):
        """
        Set up class-level fixtures.
        """
        cls.gpi: GenePoolInterface = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)

    def test_select_random_codon(self):
        """
        Test the select_random_codon_* functions are equivalent.
        """
        ec = ExecutionContext(self.gpi, wmc=True)
        rtctxt = RuntimeContext(self.gpi)
        load_codons(ec.gpi)  # Needs to be done before seeding the random selector
        rcsgc = random_codon_selector_gc(ec)

        py_codons = set()
        boost_codons = set()
        # If there only 100 codons then the odds we at least 1 duplicate is 10%
        # 20% because we do the same thing twice per iteration.
        # If we get unlucky, keep trying but after 20 goes (1 in 10**13) assert
        # it is a failure.
        attempts = 0
        while (len(py_codons) < 5 or len(boost_codons) < 5) and attempts < 20:
            py_codons = {random_codon_selector_py(rtctxt)["signature"] for _ in range(5)}
            boost_codons = {ec.execute(rcsgc, tuple())["signature"] for _ in range(5)}
            self.assertNotEqual(py_codons, boost_codons)
            attempts += 1
        self.assertLess(attempts, 20, "Randomness test failed.")
