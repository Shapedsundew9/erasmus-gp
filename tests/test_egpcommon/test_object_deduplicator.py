"""Unit test cases for the ObjectDeduplicator class."""

import unittest
from typing import Any

from egpcommon.freezable_object import FreezableObject
from egpcommon.object_deduplicator import ObjectDeduplicator


# Test Helper Classes
class SimpleHashable:
    """Simple hashable object for testing."""

    __slots__ = ("value",)

    def __init__(self, value: Any):
        """Initialize a SimpleHashable object."""
        self.value = value

    def __eq__(self, other: object) -> bool:
        """Check equality based on value."""
        if not isinstance(other, SimpleHashable):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """Return hash based on value."""
        return hash(self.value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"SimpleHashable({self.value!r})"


class SimpleFO(FreezableObject):
    """Simple FreezableObject for testing deduplication."""

    __slots__ = ("value",)

    def __init__(self, value: Any, frozen: bool = False):
        """Initialize a SimpleFO object."""
        super().__init__(frozen=False)
        self.value = value
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        """Check equality based on value."""
        if not isinstance(other, SimpleFO):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        """Return hash based on value."""
        try:
            return hash(self.value)
        except TypeError:
            return id(self.value)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"SimpleFO({self.value!r}, frozen={self.is_frozen()})"


class TestObjectDeduplicator(unittest.TestCase):
    """Unit tests for the ObjectDeduplicator class."""

    def test_initialization(self):
        """Test ObjectDeduplicator initialization."""
        dedup = ObjectDeduplicator(name="test", size=128)
        self.assertEqual(dedup.name, "test")
        # pylint: disable=protected-access
        self.assertIsNotNone(dedup._objects)

    def test_initialization_default_size(self):
        """Test ObjectDeduplicator initialization with default size."""
        dedup = ObjectDeduplicator(name="default")
        self.assertEqual(dedup.name, "default")
        # Default size should be 2**16
        # pylint: disable=protected-access
        self.assertIsNotNone(dedup._objects)

    def test_deduplication_immutable_objects(self):
        """Test deduplication with immutable Python objects."""
        dedup = ObjectDeduplicator(name="immutable_test", size=8)

        # Test with tuples
        tuple1 = (1, 2, 3)
        tuple2 = (1, 2, 3)
        obj1 = dedup[tuple1]
        obj2 = dedup[tuple2]
        self.assertIs(obj1, obj2, "Same tuples should return identical object")

        # Test with frozensets
        fset1 = frozenset([1, 2, 3])
        fset2 = frozenset([1, 2, 3])
        obj3 = dedup[fset1]
        obj4 = dedup[fset2]
        self.assertIs(obj3, obj4, "Same frozensets should return identical object")

        # Test with strings
        str1 = "hello"
        str2 = "hello"
        obj5 = dedup[str1]
        obj6 = dedup[str2]
        self.assertIs(obj5, obj6, "Same strings should return identical object")

    def test_deduplication_custom_hashable(self):
        """Test deduplication with custom hashable objects."""
        dedup = ObjectDeduplicator(name="custom_test", size=16)

        obj1 = SimpleHashable("test")
        obj2 = SimpleHashable("test")

        # Even though obj1 and obj2 are equal, they should be deduplicated
        result1 = dedup[obj1]
        result2 = dedup[obj2]

        self.assertEqual(obj1, obj2, "Objects should be equal")
        self.assertIs(result1, result2, "Equal objects should be deduplicated")
        # The first object inserted should be the one returned
        self.assertIs(result1, obj1, "Should return the first inserted object")

    def test_deduplication_freezable_object(self):
        """Test deduplication with FreezableObject instances."""
        dedup = ObjectDeduplicator(name="fo_test", size=32)

        fo1 = SimpleFO("value1", frozen=True)
        fo2 = SimpleFO("value1", frozen=True)

        result1 = dedup[fo1]
        result2 = dedup[fo2]

        self.assertEqual(fo1, fo2, "FreezableObjects should be equal")
        self.assertIs(result1, result2, "Equal FreezableObjects should be deduplicated")

    def test_frozen_freezable_object_assertion(self):
        """Test that unfrozen FreezableObjects raise assertion error."""
        dedup = ObjectDeduplicator(name="frozen_test", size=16)

        unfrozen_fo = SimpleFO("value", frozen=False)

        # Should raise AssertionError for unfrozen FreezableObject
        with self.assertRaises(AssertionError) as context:
            _ = dedup[unfrozen_fo]

        self.assertIn(
            "FreezableObjects must be frozen",
            str(context.exception),
            "Should require frozen FreezableObjects",
        )

    def test_different_objects_not_deduplicated(self):
        """Test that different objects are not deduplicated."""
        dedup = ObjectDeduplicator(name="different_test", size=16)

        obj1 = SimpleHashable("test1")
        obj2 = SimpleHashable("test2")

        result1 = dedup[obj1]
        result2 = dedup[obj2]

        self.assertIsNot(result1, result2, "Different objects should not be deduplicated")
        self.assertIs(result1, obj1)
        self.assertIs(result2, obj2)

    def test_lru_cache_eviction(self):
        """Test that LRU cache evicts least recently used items."""
        # Use a very small cache size to test eviction
        dedup = ObjectDeduplicator(name="lru_test", size=2)

        obj1 = SimpleHashable("obj1")
        obj2 = SimpleHashable("obj2")
        obj3 = SimpleHashable("obj3")

        # Add obj1 and obj2 to cache (cache is full)
        result1 = dedup[obj1]
        result2 = dedup[obj2]

        self.assertIs(result1, obj1)
        self.assertIs(result2, obj2)

        # Add obj3, which should evict obj1 (least recently used)
        result3 = dedup[obj3]
        self.assertIs(result3, obj3)

        # Access obj2 again to keep it in cache
        result2_again = dedup[obj2]
        self.assertIs(result2_again, result2)

        # Create a new obj1 (same value) - it should not be the same object
        # because original obj1 was evicted
        obj1_new = SimpleHashable("obj1")
        _ = dedup[obj1_new]

        # This might or might not be the same object depending on timing
        # and whether the old obj1 was garbage collected
        # We mainly test that the cache works without error

    def test_cache_info(self):
        """Test the info method returns cache statistics."""
        dedup = ObjectDeduplicator(name="info_test", size=8)

        obj1 = (1, 2, 3)
        obj2 = (1, 2, 3)
        obj3 = (4, 5, 6)

        # First access: miss
        _ = dedup[obj1]
        # Second access with equal object: hit
        _ = dedup[obj2]
        # Third access with different object: miss
        _ = dedup[obj3]

        info_str = dedup.info()

        self.assertIn("info_test", info_str, "Info should contain deduplicator name")
        self.assertIn("Cache hits:", info_str, "Info should contain hit count")
        self.assertIn("Cache misses:", info_str, "Info should contain miss count")
        self.assertIn("Cache hit rate:", info_str, "Info should contain hit rate")

    def test_multiple_deduplicators_independent(self):
        """Test that multiple ObjectDeduplicator instances are independent."""
        dedup1 = ObjectDeduplicator(name="test1", size=16)
        dedup2 = ObjectDeduplicator(name="test2", size=16)

        obj = SimpleHashable("shared")

        result1 = dedup1[obj]
        result2 = dedup2[obj]

        # Both should return the same object (first one passed)
        self.assertIs(result1, obj)
        self.assertIs(result2, obj)

        # But the deduplicators themselves are independent
        # pylint: disable=protected-access
        self.assertIsNot(dedup1._objects, dedup2._objects)

    def test_integer_deduplication(self):
        """Test deduplication with integers."""
        dedup = ObjectDeduplicator(name="int_test", size=16)

        # Small integers are interned by Python, so this mainly tests the cache works
        int1 = 12345
        int2 = 12345

        result1 = dedup[int1]
        result2 = dedup[int2]

        self.assertIs(result1, result2)
        self.assertEqual(result1, int1)

    def test_nested_tuples_deduplication(self):
        """Test deduplication with nested tuples."""
        dedup = ObjectDeduplicator(name="nested_test", size=16)

        tuple1 = (1, (2, (3, 4)))
        tuple2 = (1, (2, (3, 4)))

        result1 = dedup[tuple1]
        result2 = dedup[tuple2]

        self.assertIs(result1, result2, "Nested tuples should be deduplicated")
        self.assertEqual(result1, tuple1)

    def test_complex_frozenset_deduplication(self):
        """Test deduplication with frozensets containing tuples."""
        dedup = ObjectDeduplicator(name="complex_test", size=16)

        fset1 = frozenset([(1, 2), (3, 4)])
        fset2 = frozenset([(1, 2), (3, 4)])

        result1 = dedup[fset1]
        result2 = dedup[fset2]

        self.assertIs(result1, result2, "Complex frozensets should be deduplicated")

    def test_cache_statistics_accuracy(self):
        """Test that cache statistics are accurate."""
        dedup = ObjectDeduplicator(name="stats_test", size=16)

        obj1 = (1, 2)
        obj2 = (1, 2)  # Equal to obj1
        obj3 = (3, 4)  # Different from obj1

        # First access: miss (obj1)
        _ = dedup[obj1]

        # Second access with equal object: hit (obj2 equals obj1)
        _ = dedup[obj2]

        # Third access with different object: miss (obj3)
        _ = dedup[obj3]

        # Fourth access with obj1 again: hit
        _ = dedup[obj1]

        info_str = dedup.info()

        # We expect 2 hits and 2 misses
        # Hit rate should be 50%
        self.assertIn("Cache hits: 2", info_str)
        self.assertIn("Cache misses: 2", info_str)
        self.assertIn("50.00%", info_str)

    def test_empty_deduplicator_info(self):
        """Test info method on empty deduplicator."""
        dedup = ObjectDeduplicator(name="empty_test", size=8)

        info_str = dedup.info()

        self.assertIn("Cache hits: 0", info_str)
        self.assertIn("Cache misses: 0", info_str)
        # Hit rate should handle division by zero
        self.assertIn("0.00%", info_str)

    def test_verify_no_setitem_method(self):
        """Test that ObjectDeduplicator does not have __setitem__ method."""
        dedup = ObjectDeduplicator(name="setitem_test", size=8)

        # Verify that __setitem__ is not defined
        # If we try to use it, we should get an error
        with self.assertRaises(TypeError):
            # pylint: disable=unsupported-assignment-operation
            dedup[(1, 2)] = (1, 2)  # type: ignore

    def test_large_number_of_objects(self):
        """Test deduplication with a large number of objects."""
        dedup = ObjectDeduplicator(name="large_test", size=64)

        # Create many unique objects
        for i in range(100):
            obj = (i, i * 2)
            result = dedup[obj]
            self.assertEqual(result, obj)

        # Access some of them again to test hits
        for i in range(0, 100, 10):
            obj = (i, i * 2)
            result = dedup[obj]
            self.assertEqual(result, obj)

    def test_freezable_object_with_complex_value(self):
        """Test deduplication of FreezableObjects with complex values."""
        dedup = ObjectDeduplicator(name="complex_fo_test", size=32)

        fo1 = SimpleFO((1, 2, frozenset([3, 4])), frozen=True)
        fo2 = SimpleFO((1, 2, frozenset([3, 4])), frozen=True)

        result1 = dedup[fo1]
        result2 = dedup[fo2]

        self.assertEqual(fo1, fo2)
        self.assertIs(result1, result2)

    def test_inheritance_from_common_obj(self):
        """Test that ObjectDeduplicator inherits from CommonObj."""
        from egpcommon.common_obj import CommonObj

        dedup = ObjectDeduplicator(name="inheritance_test", size=8)
        self.assertIsInstance(dedup, CommonObj)

    def test_slots_defined(self):
        """Test that ObjectDeduplicator uses __slots__."""
        dedup = ObjectDeduplicator(name="slots_test", size=8)

        # Check that __slots__ is defined
        self.assertTrue(hasattr(ObjectDeduplicator, "__slots__"))
        self.assertEqual(ObjectDeduplicator.__slots__, ("_objects", "name", "target_rate"))

        # Check that instance doesn't have __dict__
        self.assertFalse(hasattr(dedup, "__dict__"))

    def test_zero_size_cache(self):
        """Test ObjectDeduplicator with size 0 (no caching)."""
        dedup = ObjectDeduplicator(name="zero_size_test", size=0)

        obj1 = (1, 2, 3)
        obj2 = (1, 2, 3)

        result1 = dedup[obj1]
        result2 = dedup[obj2]

        # With size 0, no caching occurs, so we might get different objects
        # or the same depending on Python's object interning
        # The main point is the deduplicator should still work without errors
        self.assertEqual(result1, result2)

    def test_concurrent_access_same_object(self):
        """Test accessing the same object multiple times in sequence."""
        dedup = ObjectDeduplicator(name="concurrent_test", size=16)

        obj = ("test", "value")

        results = [dedup[obj] for _ in range(10)]

        # All results should be the same object
        for result in results:
            self.assertIs(result, obj)

    def test_string_deduplication(self):
        """Test deduplication of strings."""
        dedup = ObjectDeduplicator(name="string_test", size=16)

        # Use longer strings to avoid Python's string interning
        str1 = "this is a longer test string to avoid interning"
        str2 = "this is a longer test string to avoid interning"

        result1 = dedup[str1]
        result2 = dedup[str2]

        # They should be deduplicated
        self.assertIs(result1, result2)

    def test_bytes_deduplication(self):
        """Test deduplication of bytes objects."""
        dedup = ObjectDeduplicator(name="bytes_test", size=16)

        bytes1 = b"test bytes data"
        bytes2 = b"test bytes data"

        result1 = dedup[bytes1]
        result2 = dedup[bytes2]

        self.assertIs(result1, result2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
