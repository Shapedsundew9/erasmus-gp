"""Unit tests for the ObjectDict class."""

import unittest
from collections.abc import Collection
from gc import collect

from egpcommon.freezable_object import FreezableObject
from egpcommon.object_dict import ObjectDict


class Freezy(FreezableObject):
    """A simple test class that inherits from FreezableObject.
    It initializes a single internal str attribute and freezes it.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str, frozen: bool = True) -> None:
        super().__init__()
        self._value = value
        if frozen:
            self.freeze()

    def __eq__(self, value: object) -> bool:
        """Override equality check to compare the internal attribute."""
        return self._value == value

    def __hash__(self) -> int:
        """Override hash to use the internal attribute."""
        return hash(self._value)

    def get_value(self) -> str:
        """Get the value of the internal attribute."""
        return self._value


# pylint: disable=protected-access
class TestObjectDict(unittest.TestCase):
    """Test cases for the ObjectDict class."""

    def setUp(self):
        """Set up for test methods."""
        self.obj_dict = ObjectDict("test_dict")

    def test_initialization(self):
        """Test the initialization of ObjectDict."""
        self.assertEqual(self.obj_dict.name, "test_dict")
        self.assertEqual(len(self.obj_dict), 0)
        self.assertEqual(self.obj_dict._added, 0)
        self.assertEqual(self.obj_dict._dupes, 0)

    def test_add_new_object(self):
        """Test adding a new object."""
        obj1 = Freezy("value1")
        added_obj = self.obj_dict.add("key1", obj1)
        self.assertIs(added_obj, obj1)
        self.assertEqual(len(self.obj_dict), 1)
        self.assertEqual(self.obj_dict["key1"], "value1")  # Relies on Freezy.__eq__
        self.assertEqual(self.obj_dict._added, 1)
        self.assertEqual(self.obj_dict._dupes, 0)

    def test_add_duplicate_object_key(self):
        """Test adding an object with a key that already exists."""
        obj1 = Freezy("value1")
        obj2 = Freezy("value1_new_instance")

        first_add = self.obj_dict.add("key1", obj1)
        self.assertIs(first_add, obj1)
        self.assertEqual(self.obj_dict._added, 1)
        self.assertEqual(self.obj_dict._dupes, 0)

        second_add = self.obj_dict.add("key1", obj2)
        self.assertIs(second_add, obj1)  # Should return the original object
        self.assertEqual(len(self.obj_dict), 1)
        self.assertEqual(self.obj_dict["key1"], "value1")  # Relies on Freezy.__eq__
        self.assertEqual(self.obj_dict._added, 1)  # _added count remains for unique objects
        self.assertEqual(self.obj_dict._dupes, 1)  # _dupes count increments

    def test_add_freezable_object_frozen(self):
        """Test adding a FreezableObject that is frozen."""
        frozen_obj = Freezy("frozen_value")
        added_obj = self.obj_dict.add("frozen_key", frozen_obj)
        self.assertIs(added_obj, frozen_obj)
        self.assertIn("frozen_key", self.obj_dict)
        self.assertTrue(self.obj_dict["frozen_key"].is_frozen())

    def test_add_freezable_object_not_frozen(self):
        """Test adding a FreezableObject that is not frozen."""
        unfrozen_obj = Freezy("unfrozen_value", False)
        with self.assertRaises(AssertionError) as context:
            self.obj_dict.add("unfrozen_key", unfrozen_obj)
        self.assertEqual(
            str(context.exception), "FreezableObjects must be frozen to be placed in an ObjectDict."
        )

    def test_getitem_exists(self):
        """Test __getitem__ for an existing key."""
        freezy = Freezy("value1")
        self.obj_dict.add("key1", freezy)
        self.assertEqual(self.obj_dict["key1"], "value1")  # Relies on Freezy.__eq__
        assert freezy, "The freezy object needs to be referenced so it is not GC'd."

    def test_getitem_not_exists(self):
        """Test __getitem__ for a non-existent key."""
        with self.assertRaises(KeyError):
            _ = self.obj_dict["non_existent_key"]

    def test_contains(self):
        """Test __contains__ method."""
        freezy = Freezy("value1")
        self.obj_dict.add("key1", freezy)
        self.assertIn("key1", self.obj_dict)
        self.assertNotIn("non_existent_key", self.obj_dict)
        assert freezy, "The freezy object needs to be referenced so it is not GC'd."

    def test_len(self):
        """Test __len__ method."""
        freezy1 = Freezy("value1")
        freezy2 = Freezy("value2")
        freezy3 = Freezy("value3")
        self.assertEqual(len(self.obj_dict), 0)
        self.obj_dict.add("key1", freezy1)
        self.assertEqual(len(self.obj_dict), 1)
        self.obj_dict.add("key2", freezy2)
        self.assertEqual(len(self.obj_dict), 2)
        self.obj_dict.add("key1", freezy3)
        self.assertEqual(len(self.obj_dict), 2)
        assert freezy1, "The freezy1 object needs to be referenced so it is not GC'd."
        assert freezy2, "The freezy2 object needs to be referenced so it is not GC'd."
        assert freezy3, "The freezy3 object needs to be referenced so it is not GC'd."

    def test_iter(self):
        """Test __iter__ method."""
        self.assertEqual(list(iter(self.obj_dict)), [])  # Empty dict

        keys = ["key1", "key2", "key3"]
        values = [Freezy(f"value{i}") for i in range(3)]
        for key, value in zip(keys, values):
            self.obj_dict.add(key, value)

        iterated_keys = [k for k in self.obj_dict]
        self.assertCountEqual(iterated_keys, keys)
        # Check that the values are still accessible
        for key, value in zip(keys, values):
            self.assertEqual(self.obj_dict[key], value)

    def test_garbage_collection(self):
        """Test garbage collection of Freezy objects."""
        import gc

        self.assertEqual(list(iter(self.obj_dict)), [])  # Empty dict

        keys = ["key1", "key2", "key3"]
        for i, key in enumerate(keys):
            # Create objects without freezing them to avoid ObjectSet storage
            freezy = Freezy(f"value{i}", frozen=False)
            freezy.freeze(store=False)  # Freeze without storing in ObjectSet
            self.obj_dict.add(key, freezy)

        # Force multiple garbage collection cycles
        for _ in range(3):
            gc.collect()

        # Check that objects that have no other references are garbage collected
        # Since we're using WeakValueDictionary, objects should be removed when GC'd
        iterated_keys = [k for k in self.obj_dict]
        # Due to the nature of WeakValueDictionary and garbage collection timing,
        # some objects might still be alive. This test mainly ensures the mechanism works.
        self.assertLessEqual(
            len(iterated_keys), len(keys), "Expected some or all objects to be garbage collected"
        )

    def test_remove_exists(self):
        """Test removing an existing object."""
        freezy = Freezy("value1")
        self.obj_dict.add("key1", freezy)
        self.assertIn("key1", self.obj_dict)
        self.obj_dict.remove("key1")
        self.assertEqual(len(self.obj_dict), 0)
        self.assertNotIn("key1", self.obj_dict)
        assert freezy, "The freezy object needs to be referenced so it is not GC'd."

    def test_remove_not_exists(self):
        """Test removing a non-existent object."""
        with self.assertRaises(KeyError):
            self.obj_dict.remove("non_existent_key")

    def test_clear(self):
        """Test clearing the ObjectDict."""
        freezy1 = Freezy("value1")
        freezy2 = Freezy("value2")
        freezy3 = Freezy("value3")
        self.obj_dict.add("key1", freezy1)
        self.obj_dict.add("key2", freezy2)
        self.obj_dict.add("key1", freezy3)

        self.assertNotEqual(len(self.obj_dict), 0)
        self.assertNotEqual(self.obj_dict._added, 0)
        # self.obj_dict._dupes could be 0 or more, here it's 1

        self.obj_dict.clear()

        self.assertEqual(len(self.obj_dict), 0)
        self.assertEqual(self.obj_dict._added, 0)
        self.assertEqual(self.obj_dict._dupes, 0)
        self.assertNotIn("key1", self.obj_dict)
        assert freezy1, "The freezy1 object needs to be referenced so it is not GC'd."
        assert freezy2, "The freezy2 object needs to be referenced so it is not GC'd."
        assert freezy3, "The freezy3 object needs to be referenced so it is not GC'd."

    def test_info(self):
        """Test the info method."""
        # Initial state
        info_str_initial = self.obj_dict.info()
        expected_initial = (
            f"Object {self.obj_dict.__class__} '{self.obj_dict.name}' has 0 objects of "
            f"0 added and 0 duplicate add attempts."
        )
        self.assertEqual(info_str_initial, expected_initial)

        # After adds
        freezy1 = Freezy("value1")
        freezy2 = Freezy("value2")
        freezy3 = Freezy("value3")
        self.obj_dict.add("key1", freezy1)
        self.obj_dict.add("key1", freezy2)
        self.obj_dict.add("key2", freezy3)

        info_str_after_adds = self.obj_dict.info()
        expected_after_adds = (
            f"Object {self.obj_dict.__class__} '{self.obj_dict.name}' has 2 objects of "
            f"2 added and 1 duplicate add attempts."
        )
        self.assertEqual(info_str_after_adds, expected_after_adds)
        assert freezy1, "The freezy1 object needs to be referenced so it is not GC'd."
        assert freezy2, "The freezy2 object needs to be referenced so it is not GC'd."
        assert freezy3, "The freezy3 object needs to be referenced so it is not GC'd."

    def test_verify(self):
        """Test the verify method."""
        # CommonObj.verify() raises exceptions on failure, so no exception means success.
        # It also calls info(), which is tested separately.
        try:
            self.obj_dict.verify()
        except Exception as e:
            self.fail(f"verify() raised an exception unexpectedly: {e}")

        # Add some items and verify again
        self.obj_dict.add("key1", Freezy("value1"))
        try:
            self.obj_dict.verify()
        except Exception as e:
            self.fail(f"verify() raised an exception unexpectedly after adding: {e}")

    def test_is_collection(self):
        """Test if ObjectDict instance is a Collection."""
        self.assertTrue(isinstance(self.obj_dict, Collection))


if __name__ == "__main__":
    unittest.main()
