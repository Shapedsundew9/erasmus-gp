"""Unit tests for the common module."""

from hashlib import sha256
from pprint import pformat
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
        gca: bytes = b"gca"
        gcb: bytes = b"gcb"
        graph: dict[str, Any] = {"a": 1, "b": 2}
        meta_data: dict[str, Any] = {
            "function": {"python3": {"0": {"inline": "def f(x): return x+1"}}}
        }
        signature: bytes = sha256_signature(gca, gcb, graph, meta_data)
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with None meta_data
        signature: bytes = sha256_signature(gca, gcb, graph, None)
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with empty meta_data
        signature: bytes = sha256_signature(gca, gcb, graph, {})
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data without function
        signature: bytes = sha256_signature(gca, gcb, graph, {"a": 1})
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data with function but without code
        meta_data = {"function": {"python3": {"0": {"inline": "def f(x): return x+1"}}}}
        signature: bytes = sha256_signature(gca, gcb, graph, meta_data)
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with meta_data with function and code
        meta_data = {
            "function": {"python3": {"0": {"inline": "def f(x): return x+1", "code": "bytecode"}}}
        }
        signature: bytes = sha256_signature(gca, gcb, graph, meta_data)
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test that changing the gca changes the signature
        hash_obj = sha256(b"gca1")
        hash_obj.update(gcb)
        hash_obj.update(pformat(graph, compact=True).encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["inline"].encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["code"].encode())
        signature1: bytes = hash_obj.digest()
        self.assertNotEqual(signature, signature1)

        # Test that changing the gcb changes the signature
        hash_obj = sha256(gca)
        hash_obj.update(b"gcb1")
        hash_obj.update(pformat(graph, compact=True).encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["inline"].encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["code"].encode())
        signature1: bytes = hash_obj.digest()
        self.assertNotEqual(signature, signature1)

        # Test that changing the graph changes the signature
        hash_obj = sha256(gca)
        hash_obj.update(gcb)
        hash_obj.update(pformat({"a": 1, "b": 3}, compact=True).encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["inline"].encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["code"].encode())
        signature1: bytes = hash_obj.digest()
        self.assertNotEqual(signature, signature1)

        # Test that changing the meta_data changes the signature
        hash_obj = sha256(gca)
        hash_obj.update(gcb)
        hash_obj.update(pformat(graph, compact=True).encode())
        hash_obj.update(
            {"function": {"python3": {"0": {"inline": "def f(x): return x+2"}}}}["function"][
                "python3"
            ]["0"]["inline"].encode()
        )
        hash_obj.update(meta_data["function"]["python3"]["0"]["code"].encode())
        signature1: bytes = hash_obj.digest()
        self.assertNotEqual(signature, signature1)

        # Test that changing the meta_data code changes the signature
        hash_obj = sha256(gca)
        hash_obj.update(gcb)
        hash_obj.update(pformat(graph, compact=True).encode())
        hash_obj.update(meta_data["function"]["python3"]["0"]["inline"].encode())
        hash_obj.update(
            {
                "function": {
                    "python3": {"0": {"inline": "def f(x): return x+1", "code": "bytecode1"}}
                }
            }["function"]["python3"]["0"]["code"].encode()
        )
        signature1: bytes = hash_obj.digest()
        self.assertNotEqual(signature, signature1)

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
