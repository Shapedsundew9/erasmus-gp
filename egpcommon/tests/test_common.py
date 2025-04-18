"""Unit tests for the common module."""

from uuid import uuid4
from typing import Any
from unittest import TestCase
from egpcommon.common import (
    NULL_SHA256,
    sha256_signature,
    bin_counts,
    random_int_tuple_generator,
)


class TestCommon(TestCase):
    """Test cases for the common module."""

    def test_sha256_signature(self) -> None:
        """Test the sha256_signature function."""
        ancestora: bytes = b"ancestora"
        ancestorb: bytes = b"ancestorb"
        pgc: bytes = b"pgc"
        gca: bytes = b"gca"
        gcb: bytes = b"gcb"
        graph: dict[str, Any] = {"a": 1, "b": 2}
        meta_data: dict[str, Any] = {
            "function": {"python3": {"0": {"inline": "def f(x): return x+1"}}}
        }
        created: int = 0
        creator: bytes = uuid4().bytes
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, meta_data, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with None meta_data
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, None, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with empty meta_data
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, {}, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data without function
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, {"a": 1}, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data with function but without code
        meta_data = {"function": {"python3": {"0": {"inline": "def f(x): return x+1"}}}}
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, meta_data, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data with function and code
        meta_data = {
            "function": {"python3": {"0": {"inline": "def f(x): return x+1", "code": "bytecode"}}}
        }
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, meta_data, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Use a created time to create a signature
        created = 2198374
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, meta_data, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

    def test_bin_counts(self) -> None:
        """Test the bin_counts function."""
        # Test with empty data
        self.assertEqual(bin_counts([]), [])

        # Test with single element data
        self.assertEqual(bin_counts([5]), [1])

        # Test with multiple elements in the same bin
        self.assertEqual(bin_counts([1, 2, 3, 4, 5]), [5])

        # Test with elements in different bins
        self.assertEqual(bin_counts([1, 11, 21, 31, 41]), [1, 1, 1, 1, 1])

        # Test with elements in different bins and custom bin width
        self.assertEqual(bin_counts([1, 11, 21, 31, 41], bin_width=20), [2, 2, 1])

        # Test with elements in different bins and custom bin width
        self.assertEqual(bin_counts([1, 11, 21, 31, 41], bin_width=10), [1, 1, 1, 1, 1])

        # Test with elements in different bins and custom bin width
        self.assertEqual(
            bin_counts([1, 11, 21, 31, 41], bin_width=1),
            [
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
            ],
        )

    def test_generate_random_int_tuple_generator(self) -> None:
        """Test the generate_random_int_tuple_generator function."""
        # Test with n = 0
        self.assertEqual(random_int_tuple_generator(0, 10), ())

        # Test with n = 1 and x = 1
        self.assertEqual(random_int_tuple_generator(1, 1), (0,))

        # Test with n = 5 and x = 1
        self.assertEqual(random_int_tuple_generator(5, 1), (0, 0, 0, 0, 0))

        # Test with n = 5 and x = 10
        result = random_int_tuple_generator(5, 10)
        self.assertEqual(len(result), 5)
        self.assertTrue(all(0 <= value < 10 for value in result))

        # Test with n = 10 and x = 100
        result = random_int_tuple_generator(10, 100)
        self.assertEqual(len(result), 10)
        self.assertTrue(all(0 <= value < 100 for value in result))

        # Test with negative n
        with self.assertRaises(ValueError):
            random_int_tuple_generator(-1, 10)

        # Test with negative x
        with self.assertRaises(ValueError):
            random_int_tuple_generator(5, -10)

        # Test with zero x
        with self.assertRaises(ValueError):
            random_int_tuple_generator(5, 0)

        # Test with both n and x negative
        with self.assertRaises(ValueError):
            random_int_tuple_generator(-5, -10)
