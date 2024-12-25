"""Tests for the ObjectSet class."""

import unittest

from egpcommon.object_set import ObjectSet


class TestObjectSet(unittest.TestCase):
    """
    Unit tests for the ObjectSet class.

    Test Cases:
    - test_add: Verify that a object can be added to the ObjectSet.
    - test_add_duplicate: Verify that adding a duplicate object does not increase the size.
    - test_remove: Verify that a object can be removed from the ObjectSet.
    - test_clean: Verify that the ObjectSet is cleaned up properly.
    - test_contains: Verify that the ObjectSet correctly identifies contained objects.
    - test_len: Verify that the length of the ObjectSet is correctly reported.
    - test_iter: Verify that the ObjectSet can be iterated over and contains the correct objects.
    """

    def setUp(self):
        """Set up the test fixture."""
        self.object_set = ObjectSet("default")

    def test_add(self):
        """Test the add method."""
        tup = (1, 2, 3)
        result = self.object_set.add(tup)
        self.assertIn(tup, self.object_set)
        self.assertEqual(result, tup)

    def test_add_duplicate(self):
        """Test adding a duplicate object."""
        tup = (1, 2, 3)
        initial_length = len(self.object_set)
        self.object_set.add(tup)
        self.assertEqual(len(self.object_set), initial_length + 1)
        result = id(self.object_set.add((1, 2, 3)))
        self.assertEqual(result, id(tup))
        self.assertEqual(len(self.object_set), initial_length + 1)

    def test_remove(self):
        """Test the remove method."""
        tup = (1, 2, 3)
        self.object_set.add(tup)
        self.object_set.remove(tup)
        self.assertNotIn(tup, self.object_set)

    def test_contains(self):
        """Test the __contains__ method."""
        tup = (1, 2, 3)
        self.object_set.add(tup)
        self.assertIn(tup, self.object_set)
        self.assertNotIn((4, 5, 6), self.object_set)

    def test_len(self):
        """Test the __len__ method."""
        self.assertEqual(len(self.object_set), 0)
        self.object_set.add((1, 2, 3))
        self.assertEqual(len(self.object_set), 1)
        self.object_set.add((4, 5, 6))
        self.assertEqual(len(self.object_set), 2)

    def test_iter(self):
        """Test the __iter__ method."""
        tup1 = (1, 2, 3)
        tup2 = (4, 5, 6)
        self.object_set.add(tup1)
        self.object_set.add(tup2)
        self.assertCountEqual(self.object_set, [tup1, tup2])
        self.assertIn(tup2, self.object_set)
