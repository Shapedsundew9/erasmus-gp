"""Test the merge function in egpcommon.common"""

import unittest

from egpcommon.common import merge


class TestMergeFunction(unittest.TestCase):
    """Test the merge function in egpcommon.common"""

    def test_merge_simple(self) -> None:
        """Test merging two simple dictionaries."""
        dict_a = {"key1": "value1"}
        dict_b = {"key2": "value2"}
        expected = {"key1": "value1", "key2": "value2"}
        result = merge(dict_a, dict_b)
        self.assertEqual(result, expected)

    def test_merge_nested(self) -> None:
        """Test merging two nested dictionaries."""
        dict_a = {"key1": {"subkey1": "value1"}}
        dict_b = {"key1": {"subkey2": "value2"}}
        expected = {"key1": {"subkey1": "value1", "subkey2": "value2"}}
        result = merge(dict_a, dict_b)
        self.assertEqual(result, expected)

    def test_merge_conflict(self) -> None:
        """Test merging two dictionaries with a conflict."""
        dict_a = {"key1": "value1"}
        dict_b = {"key1": "value2"}
        with self.assertRaises(ValueError):
            merge(dict_a, dict_b)

    def test_merge_no_new_keys(self) -> None:
        """Test merging two dictionaries with no new keys."""
        dict_a = {"key1": "value1"}
        dict_b = {"key2": "value2"}
        expected = {"key1": "value1"}
        result = merge(dict_a, dict_b, no_new_keys=True)
        self.assertEqual(result, expected)

    def test_merge_update(self) -> None:
        """Test merging two dictionaries with update."""
        dict_a = {"key1": "value1"}
        dict_b = {"key1": "value2"}
        expected = {"key1": "value2"}
        result = merge(dict_a, dict_b, update=True)
        self.assertEqual(result, expected)
