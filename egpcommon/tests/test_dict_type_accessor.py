"""Tests for the DictTypeAccessor class."""
import unittest

from egpcommon.egpcommon.common import DictTypeAccessor


class Accessor(DictTypeAccessor):
    """Accessor class for testing DictTypeAccessor."""
    def __init__(self) -> None:
        self.foo = 'bar'
        self.num = 42


class TestDictTypeAccessor(unittest.TestCase):
    """Test the DictTypeAccessor class."""
    def setUp(self):
        """Set up the test."""
        self.accessor = Accessor()
        self.accessor.foo = 'bar'
        self.accessor.num = 42

    def test_contains(self):
        """Test the contains method."""
        # Accessor does have a contains method but is not a standard container
        self.assertIn('foo', self.accessor)  # type: ignore
        self.assertNotIn('baz', self.accessor)  # type: ignore

    def test_eq(self):
        """Test the eq method."""
        other = Accessor()
        other.foo = 'bar'
        other.num = 42
        self.assertEqual(self.accessor, other)

        other.num = 43
        self.assertNotEqual(self.accessor, other)

    def test_getitem(self):
        """Test the getitem method."""
        self.assertEqual(self.accessor['foo'], 'bar')
        self.assertEqual(self.accessor['num'], 42)
        with self.assertRaises(AttributeError):
            _ = self.accessor['baz']

    def test_setitem(self):
        """Test the setitem method."""
        self.accessor['foo'] = 'qux'
        self.assertEqual(self.accessor.foo, 'qux')

    def test_copy(self):
        """Test the copy method."""
        copy_accessor = self.accessor.copy()
        self.assertEqual(self.accessor, copy_accessor)
        self.assertIsNot(self.accessor, copy_accessor)

    def test_get(self):
        """Test the get method."""
        self.assertEqual(self.accessor.get('foo'), 'bar')
        self.assertEqual(self.accessor.get('baz', 'default'), 'default')

    def test_setdefault(self):
        """Test the setdefault method."""
        self.assertEqual(self.accessor.setdefault('foo', 'new_value'), 'bar')
        self.assertEqual(self.accessor.setdefault('baz', 'new_value'), 'new_value')
        # pylint: disable=no-member
        # Member is created in the line above
        self.assertEqual(self.accessor.baz, 'new_value')  # type: ignore
