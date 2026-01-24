"""
Docstring for tests.test_egppy.test_genetic_code.test_types_def_store
"""

import unittest

from annotated_types import T

from egpcommon.type_string_parser import TypeStringParser
from egppy.genetic_code.types_def_store import TypesDefStore, types_def_store


# pylint: disable=protected-access
class TestTypesDefStore(unittest.TestCase):
    """
    Docstring for TestTypesDefStore
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

    def test_new_type(self):
        """Test adding a new type."""
        # Compound new type
        new_type_name = "dict[set[int],dict[str,list[float]]]"

        # Getting the type creates it if it does not exist.
        # This is a recursive process, so all subtypes should be created too.
        new_type = types_def_store[new_type_name]

        self.assertEqual(new_type.name, str(TypeStringParser.parse(new_type_name)))
        self.assertIn("dict[set[int],dict[str,list[float]]]", types_def_store)

        # Check that all subtypes were created
        self.assertIn("set[int]", types_def_store)
        self.assertIn("dict[str,list[float]]", types_def_store)
        self.assertIn("list[float]", types_def_store)

        # Check that parents have the new type as children
        self.assertIn(
            new_type.uid,
            types_def_store["MutableMapping[set[int],dict[str,list[float]]]"].children.tolist(),
        )
        self.assertIn(
            types_def_store["set[int]"].uid, types_def_store["MutableSet[int]"].children.tolist()
        )
        self.assertIn(
            types_def_store["dict[str,list[float]]"].uid,
            types_def_store["MutableMapping[str,list[float]]"].children.tolist(),
        )
        self.assertIn(
            types_def_store["list[float]"].uid,
            types_def_store["MutableSequence[float]"].children.tolist(),
        )


if __name__ == "__main__":
    unittest.main()
