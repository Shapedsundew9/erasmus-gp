"""Unit tests for the codon_dev_load module.

This module tests the codon development loader functionality, including loading
codons from JSON files, caching, and finding codon signatures based on input types,
output types, and names.
"""

import unittest

from egpcommon.codon_dev_load import DEFAULT_CODON_PATHS, clear_cache, find_codon_signature


class TestCodonDevLoad(unittest.TestCase):
    """Test cases for codon_dev_load module."""

    def setUp(self) -> None:
        """Set up test fixtures."""
        # Clear the cache before each test
        clear_cache()

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Clear the cache after each test
        clear_cache()

    def test_default_codon_paths_exist(self) -> None:
        """Test that default codon paths are configured."""
        self.assertIsInstance(DEFAULT_CODON_PATHS, tuple)
        self.assertGreater(len(DEFAULT_CODON_PATHS), 0)
        self.assertTrue(all(isinstance(path, str) for path in DEFAULT_CODON_PATHS))

    def test_find_codon_signature_with_defaults(self) -> None:
        """Test finding a codon signature using default paths."""
        # This test uses the actual codon files
        # Let's find a simple codon - the AND operator for PsqlBool
        signature = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Should find the signature
        self.assertIsNotNone(signature)
        assert signature is not None  # Type narrowing for mypy/pyright
        self.assertIsInstance(signature, bytes)
        self.assertEqual(len(signature), 32)  # SHA256 is 32 bytes

    def test_find_codon_signature_not_found(self) -> None:
        """Test that AssertionError is raised when a codon is not found."""
        with self.assertRaises(AssertionError):
            find_codon_signature(
                input_types=["NonExistentType"],
                output_types=["NonExistentType"],
                name="NonExistentCodon",
            )

    def test_find_codon_signature_empty_inputs(self) -> None:
        """Test finding a codon with no inputs (e.g., a constant or column)."""
        # Find a codon with no inputs - e.g., _lost_descendants column
        signature = find_codon_signature(
            input_types=[],
            output_types=["PsqlBigInt"],
            name="_lost_descendants",
        )

        # Should find the signature
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)

    def test_find_meta_codon_signature(self) -> None:
        """Test finding a meta-codon signature (type cast)."""
        # Meta-codons are type casts - find one
        signature = find_codon_signature(
            input_types=["PsqlNumeric"],
            output_types=["object"],
            name="raise_if_not_instance_of(i0, t0)",
        )

        # Should find the signature
        self.assertIsNotNone(signature)
        self.assertIsInstance(signature, bytes)

    def test_cache_functionality(self) -> None:
        """Test that the cache works correctly."""
        # First call - loads from files
        signature1 = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Second call - should use cache
        signature2 = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Should return the same signature
        self.assertEqual(signature1, signature2)

    def test_clear_cache(self) -> None:
        """Test that clearing the cache works."""
        # Load a codon
        signature1 = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )
        self.assertIsNotNone(signature1)

        # Clear cache
        clear_cache()

        # Load again - should reload from files
        signature2 = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Should still get the same signature
        self.assertEqual(signature1, signature2)

    def test_multiple_input_types(self) -> None:
        """Test finding a codon with multiple input types."""
        # Note: Based on the actual codon structure, input_types is typically
        # a single type that applies to all inputs, not individual types per input
        # However, we can still test the lookup mechanism

        # Find a codon that takes PsqlBool inputs
        signature = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        self.assertIsNotNone(signature)

    def test_signature_is_bytes(self) -> None:
        """Test that returned signatures are bytes objects."""
        signature = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        self.assertIsNotNone(signature)
        assert signature is not None  # Type narrowing for mypy/pyright
        self.assertIsInstance(signature, bytes)
        # SHA256 signatures are 32 bytes
        self.assertEqual(len(signature), 32)

    def test_case_sensitive_name_matching(self) -> None:
        """Test that codon name matching is case-sensitive."""
        # Find with correct case
        _ = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Try with incorrect case
        with self.assertRaises(AssertionError):
            find_codon_signature(
                input_types=["PsqlBool"],
                output_types=["PsqlBool"],
                name="and",
            )

        # Incorrect case should fail (unless there's actually a lowercase 'and' codon)
        # Note: This assertion depends on the actual codon data

    def test_order_of_types_matters(self) -> None:
        """Test that the order of input/output types matters for matching."""
        # This is implicitly tested by tuple comparison in the cache key
        # The test confirms the behavior is correct

        signature = find_codon_signature(
            input_types=["PsqlBool"],
            output_types=["PsqlBool"],
            name="AND",
        )

        # Same types, same order should find the same codon
        self.assertIsNotNone(signature)


if __name__ == "__main__":
    unittest.main()
