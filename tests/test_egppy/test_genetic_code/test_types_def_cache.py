"""
Docstring for tests.test_egppy.test_genetic_code.test_types_def_cache
"""

import unittest

from egppy.genetic_code.types_def import TypesDefStore, types_def_store


# pylint: disable=protected-access
class TestTypesDefCache(unittest.TestCase):
    """
    Docstring for TestTypesDefCache
    """

    def setUp(self):
        # Reset stats before each test if possible, but they are class attributes.
        # We can just read current values and check for increments.
        pass

    def test_ancestors_caching(self):
        """Test caching of ancestors method."""
        # Ensure int type is loaded
        int_type = types_def_store["int"]

        # First call - should be a miss (unless already cached by other tests/runs,
        # but in fresh run it's miss)
        # To be safe, we can clear cache for this specific key if we could, but we can't easily.
        # Instead, we rely on the fact that we can check if it hits or misses.

        # Let's pick a type that is likely loaded.
        ancestors1 = types_def_store.ancestors(int_type)

        # Check stats after first call
        hits1 = TypesDefStore._ancestors_cache_hits
        misses1 = TypesDefStore._ancestors_cache_misses

        # Second call - should be a hit
        ancestors2 = types_def_store.ancestors(int_type)

        hits2 = TypesDefStore._ancestors_cache_hits
        misses2 = TypesDefStore._ancestors_cache_misses

        self.assertEqual(ancestors1, ancestors2)
        self.assertEqual(hits2, hits1 + 1)
        self.assertEqual(misses2, misses1)

    def test_descendants_caching(self):
        """Test caching of descendants method."""
        # Ensure int type is loaded
        int_type = types_def_store["int"]

        # First call
        descendants1 = types_def_store.descendants(int_type)

        # Check stats after first call
        hits1 = TypesDefStore._descendants_cache_hits
        misses1 = TypesDefStore._descendants_cache_misses

        # Second call - should be a hit
        descendants2 = types_def_store.descendants(int_type)

        hits2 = TypesDefStore._descendants_cache_hits
        misses2 = TypesDefStore._descendants_cache_misses

        self.assertEqual(descendants1, descendants2)
        self.assertEqual(hits2, hits1 + 1)
        self.assertEqual(misses2, misses1)

    def test_info(self):
        """Test info method."""
        info = types_def_store.info()
        self.assertIn("Ancestors Cache hits:", info)
        self.assertIn("Descendants Cache hits:", info)


if __name__ == "__main__":
    unittest.main()
