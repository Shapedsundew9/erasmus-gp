"""Tests for the TupleSet class."""

import unittest

from egpcommon.tuple_set import TupleSet


class TestTupleSet(unittest.TestCase):
    """
    Unit tests for the TupleSet class.

    Test Cases:
    - test_add: Verify that a tuple can be added to the TupleSet.
    - test_add_duplicate: Verify that adding a duplicate tuple does not increase the size.
    - test_remove: Verify that a tuple can be removed from the TupleSet.
    - test_clean: Verify that the TupleSet is cleaned up properly.
    - test_contains: Verify that the TupleSet correctly identifies contained tuples.
    - test_len: Verify that the length of the TupleSet is correctly reported.
    - test_iter: Verify that the TupleSet can be iterated over and contains the correct tuples.
    """

    def setUp(self):
        """Set up the test fixture."""
        self.tuple_set = TupleSet()

    def test_add(self):
        """Test the add method."""
        tup = (1, 2, 3)
        result = self.tuple_set.add(tup)
        self.assertIn(tup, self.tuple_set)
        self.assertEqual(result, tup)

    def test_add_duplicate(self):
        """Test adding a duplicate tuple."""
        tup = (1, 2, 3)
        initial_length = len(self.tuple_set)
        self.tuple_set.add(tup)
        self.assertEqual(len(self.tuple_set), initial_length + 1)
        result = id(self.tuple_set.add((1, 2, 3)))
        self.assertEqual(result, id(tup))
        self.assertEqual(len(self.tuple_set), initial_length + 1)

    def test_remove(self):
        """Test the remove method."""
        tup = (1, 2, 3)
        self.tuple_set.add(tup)
        self.tuple_set.remove(tup)
        self.assertNotIn(tup, self.tuple_set)

    def test_contains(self):
        """Test the __contains__ method."""
        tup = (1, 2, 3)
        self.tuple_set.add(tup)
        self.assertIn(tup, self.tuple_set)
        self.assertNotIn((4, 5, 6), self.tuple_set)

    def test_len(self):
        """Test the __len__ method."""
        self.assertEqual(len(self.tuple_set), 0)
        self.tuple_set.add((1, 2, 3))
        self.assertEqual(len(self.tuple_set), 1)
        self.tuple_set.add((4, 5, 6))
        self.assertEqual(len(self.tuple_set), 2)

    def test_iter(self):
        """Test the __iter__ method."""
        tup1 = (1, 2, 3)
        tup2 = (4, 5, 6)
        self.tuple_set.add(tup1)
        self.tuple_set.add(tup2)
        self.assertCountEqual(self.tuple_set, [tup1, tup2])
        self.assertIn(tup2, self.tuple_set)
