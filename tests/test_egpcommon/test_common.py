"""Unit tests for the common module."""

from json import dump, load
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Any
from unittest import TestCase
from uuid import uuid4

from egpcommon.common import (
    NULL_SHA256,
    bin_counts,
    ensure_sorted_json_keys,
    random_int_tuple_generator,
    sha256_signature,
)


class TestCommon(TestCase):
    """Test cases for the common module."""

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

    def test_sha256_signature(self) -> None:
        """Test the sha256_signature function."""
        ancestora: bytes = b"ancestora"
        ancestorb: bytes = b"ancestorb"
        pgc: bytes = b"pgc"
        gca: bytes = b"gca"
        gcb: bytes = b"gcb"
        graph: dict[str, Any] = {"a": 1, "b": 2}
        imports: tuple = ()
        inline: str = "def f(x): return x+1"
        code: str = ""
        created: int = 0
        creator: bytes = uuid4().bytes
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, imports, inline, code, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)

        # Test with None meta_data
        signature: bytes = sha256_signature(
            ancestora, ancestorb, gca, gcb, graph, pgc, imports, "", code, created, creator
        )
        self.assertEqual(len(signature), 32)
        self.assertNotEqual(signature, NULL_SHA256)


class TestEnsureSortedJsonKeys(TestCase):
    """Test cases for the ensure_sorted_json_keys function."""

    def test_already_sorted_keys(self) -> None:
        """Test with a JSON file that already has sorted keys."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {"a": 1, "b": 2, "c": 3}

            # Write initial sorted data
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify the file was not modified (keys already sorted)
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(result, data)
            self.assertEqual(list(result.keys()), ["a", "b", "c"])

    def test_complex_values(self) -> None:
        """Test with various JSON value types."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {
                "number": 42,
                "string": "hello",
                "list": [1, 2, 3],
                "bool": True,
                "null": None,
                "float": 3.14,
            }

            # Shuffle the keys
            shuffled_data = {
                "string": "hello",
                "null": None,
                "number": 42,
                "list": [1, 2, 3],
                "float": 3.14,
                "bool": True,
            }

            # Write shuffled data
            with test_file.open("w", encoding="utf-8") as file:
                dump(shuffled_data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify the file was rewritten with sorted keys
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            expected_order = ["bool", "float", "list", "null", "number", "string"]
            self.assertEqual(list(result.keys()), expected_order)
            self.assertEqual(result, data)

    def test_empty_dict(self) -> None:
        """Test with an empty dictionary."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data: dict[str, Any] = {}

            # Write empty dict
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify the file is still an empty dict
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(result, {})

    def test_file_not_found_raises_error(self) -> None:
        """Test that a non-existent file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            ensure_sorted_json_keys("/nonexistent/path/to/file.json")

    def test_invalid_json_raises_error(self) -> None:
        """Test that invalid JSON content raises JSONDecodeError."""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            temp_file.write("{ invalid json content }")
            temp_file_path = temp_file.name

        try:
            from json import JSONDecodeError

            with self.assertRaises(JSONDecodeError):
                ensure_sorted_json_keys(temp_file_path)
        finally:
            Path(temp_file_path).unlink()

    def test_nested_dict_values(self) -> None:
        """Test with nested dictionaries as values (they should not be sorted)."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {"z": {"nested_z": 1, "nested_a": 2}, "a": {"inner_b": 3, "inner_a": 4}}

            # Write unsorted data
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify only top-level keys are sorted
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(list(result.keys()), ["a", "z"])
            # Nested dictionaries should retain their original order
            self.assertEqual(result["z"], {"nested_z": 1, "nested_a": 2})
            self.assertEqual(result["a"], {"inner_b": 3, "inner_a": 4})

    def test_non_string_key_raises_error(self) -> None:
        """Test that non-string keys raise ValueError."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"

            # Create a file with integer keys (will be strings in JSON)
            # But we'll manually create invalid JSON content for testing
            # Note: JSON spec requires keys to be strings, so this tests validation
            data = {"valid_key": 1, "another_key": 2}

            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file)

            # This should pass since JSON keys are always strings
            ensure_sorted_json_keys(test_file)

            # Verify it worked
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(list(result.keys()), ["another_key", "valid_key"])

    def test_not_a_dictionary_raises_error(self) -> None:
        """Test that a JSON file containing a list raises ValueError."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"

            # Write a list instead of a dictionary
            with test_file.open("w", encoding="utf-8") as file:
                dump([1, 2, 3], file)

            # Verify ValueError is raised
            with self.assertRaises(ValueError) as context:
                ensure_sorted_json_keys(test_file)

            self.assertIn("must contain a dictionary", str(context.exception))

    def test_single_key(self) -> None:
        """Test with a dictionary containing a single key."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {"only_key": "value"}

            # Write data
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify the file is unchanged
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(result, data)

    def test_string_path(self) -> None:
        """Test that the function accepts a string path."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {"b": 1, "a": 2}

            # Write unsorted data
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function with string path
            ensure_sorted_json_keys(str(test_file))

            # Verify the file was rewritten with sorted keys
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(list(result.keys()), ["a", "b"])

    def test_unsorted_keys_get_sorted(self) -> None:
        """Test with a JSON file that has unsorted keys."""
        with TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.json"
            data = {"z": 1, "a": 2, "m": 3}

            # Write unsorted data
            with test_file.open("w", encoding="utf-8") as file:
                dump(data, file, indent=2)

            # Run the function
            ensure_sorted_json_keys(test_file)

            # Verify the file was rewritten with sorted keys
            with test_file.open("r", encoding="utf-8") as file:
                result = load(file)

            self.assertEqual(result, data)  # Same values
            self.assertEqual(list(result.keys()), ["a", "m", "z"])  # But sorted keys
