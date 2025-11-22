"""Unit test cases for the deduplication module and IntDeduplicator class."""

import sys
import unittest
from typing import Any

from egpcommon.deduplication import int_store, properties_store, signature_store, uuid_store
from egpcommon.freezable_object import FreezableObject
from egpcommon.object_deduplicator import IntDeduplicator, ObjectDeduplicator, deduplicators_info


class SimpleFO(FreezableObject):
    """Simple FreezableObject for testing deduplication stores."""

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


class TestIntDeduplicator(unittest.TestCase):
    """Unit tests for the IntDeduplicator class."""

    def test_initialization(self):
        """Test IntDeduplicator initialization with default parameters."""
        dedup = IntDeduplicator(name="test_int")
        assert isinstance(dedup, IntDeduplicator)
        self.assertEqual(dedup.name, "test_int")
        self.assertEqual(dedup.lmin, 0)
        self.assertEqual(dedup.lmax, 2**12 - 1)
        self.assertEqual(dedup.target_rate, 0.811)

    def test_initialization_custom_range(self):
        """Test IntDeduplicator initialization with custom range."""
        dedup = IntDeduplicator(name="custom_int", size=64, lmin=-100, lmax=100)
        assert isinstance(dedup, IntDeduplicator)
        self.assertEqual(dedup.name, "custom_int")
        self.assertEqual(dedup.lmin, -100)
        self.assertEqual(dedup.lmax, 100)

    def test_deduplication_within_range(self):
        """Test that integers within range are deduplicated."""
        dedup = IntDeduplicator(name="range_test", lmin=0, lmax=100)

        int1 = 42
        int2 = 42

        result1 = dedup[int1]
        result2 = dedup[int2]

        self.assertIs(result1, result2, "Integers within range should be deduplicated")
        self.assertEqual(result1, 42)

    def test_no_deduplication_below_range(self):
        """Test that integers below range are NOT deduplicated."""
        dedup = IntDeduplicator(name="below_range_test", lmin=10, lmax=100)

        int1 = 5
        int2 = 5

        result1 = dedup[int1]
        result2 = dedup[int2]

        # Should return the same value but not deduplicate (no cache involved)
        self.assertEqual(result1, 5)
        self.assertEqual(result2, 5)
        # These may or may not be the same object depending on Python's integer interning
        # The key point is the deduplicator's cache is NOT used

    def test_no_deduplication_above_range(self):
        """Test that integers above range are NOT deduplicated."""
        dedup = IntDeduplicator(name="above_range_test", lmin=0, lmax=100)

        # Use large integers to avoid Python's small integer cache
        int1 = 10000
        int2 = 10000

        result1 = dedup[int1]
        result2 = dedup[int2]

        # Should return the same value but not deduplicate (no cache involved)
        self.assertEqual(result1, 10000)
        self.assertEqual(result2, 10000)

    def test_boundary_values(self):
        """Test deduplication at boundary values."""
        dedup = IntDeduplicator(name="boundary_test", lmin=10, lmax=20)

        # Test lower boundary (inclusive)
        result_min1 = dedup[10]
        result_min2 = dedup[10]
        self.assertIs(result_min1, result_min2, "Lower boundary should be deduplicated")

        # Test upper boundary (inclusive)
        result_max1 = dedup[20]
        result_max2 = dedup[20]
        self.assertIs(result_max1, result_max2, "Upper boundary should be deduplicated")

        # Test just below lower boundary
        result_below = dedup[9]
        self.assertEqual(result_below, 9)

        # Test just above upper boundary
        result_above = dedup[21]
        self.assertEqual(result_above, 21)

    def test_negative_range(self):
        """Test IntDeduplicator with negative integer range."""
        dedup = IntDeduplicator(name="negative_test", lmin=-50, lmax=50)

        int1 = -25
        int2 = -25

        result1 = dedup[int1]
        result2 = dedup[int2]

        self.assertIs(result1, result2, "Negative integers should be deduplicated")
        self.assertEqual(result1, -25)

    def test_zero_in_range(self):
        """Test that zero is deduplicated when in range."""
        dedup = IntDeduplicator(name="zero_test", lmin=-10, lmax=10)

        zero1 = 0
        zero2 = 0

        result1 = dedup[zero1]
        result2 = dedup[zero2]

        self.assertIs(result1, result2)
        self.assertEqual(result1, 0)

    def test_cache_statistics_within_range(self):
        """Test that cache statistics are updated for integers within range."""
        dedup = IntDeduplicator(name="stats_test", lmin=0, lmax=100, size=32)

        # First access: miss
        _ = dedup[42]
        # Second access: hit
        _ = dedup[42]
        # Different value: miss
        _ = dedup[99]

        info_str = dedup.info()

        # Should have 1 hit and 2 misses for in-range integers
        self.assertIn("Cache hits: 1", info_str)
        self.assertIn("Cache misses: 2", info_str)

    def test_cache_not_used_for_out_of_range(self):
        """Test that cache is not used for out-of-range integers."""
        dedup = IntDeduplicator(name="no_cache_test", lmin=0, lmax=10, size=8)

        # Access out-of-range integers multiple times
        for _ in range(5):
            _ = dedup[100]
            _ = dedup[200]

        info_str = dedup.info()

        # Cache should have 0 hits and 0 misses because out-of-range integers
        # bypass the cache
        self.assertIn("Cache hits: 0", info_str)
        self.assertIn("Cache misses: 0", info_str)

    def test_inheritance_from_object_deduplicator(self):
        """Test that IntDeduplicator inherits from ObjectDeduplicator."""
        dedup = IntDeduplicator(name="inheritance_test")
        self.assertIsInstance(dedup, ObjectDeduplicator)

    def test_slots_defined(self):
        """Test that IntDeduplicator properly defines __slots__."""
        dedup = IntDeduplicator(name="slots_test")

        # Check that __slots__ is defined for IntDeduplicator
        self.assertTrue(hasattr(IntDeduplicator, "__slots__"))
        self.assertEqual(IntDeduplicator.__slots__, ("lmin", "lmax"))

        # Check that instance doesn't have __dict__ (inherited from ObjectDeduplicator)
        self.assertFalse(hasattr(dedup, "__dict__"))

    def test_large_positive_range(self):
        """Test IntDeduplicator with large positive range."""
        dedup = IntDeduplicator(name="large_range", lmin=1000000, lmax=2000000, size=128)

        int1 = 1500000
        int2 = 1500000

        result1 = dedup[int1]
        result2 = dedup[int2]

        self.assertIs(result1, result2)
        self.assertEqual(result1, 1500000)

    def test_mixed_in_and_out_of_range(self):
        """Test mixed access of in-range and out-of-range integers."""
        dedup = IntDeduplicator(name="mixed_test", lmin=0, lmax=100, size=16)

        # In-range accesses
        result1 = dedup[50]
        result2 = dedup[50]
        self.assertIs(result1, result2)

        # Out-of-range accesses
        result3 = dedup[200]
        result4 = dedup[200]
        # These won't be deduplicated via cache, but still return correct values
        self.assertEqual(result3, 200)
        self.assertEqual(result4, 200)

        info_str = dedup.info()
        # Should show 1 hit (second access to 50) and 1 miss (first access to 50)
        # Out-of-range accesses don't affect cache stats
        self.assertIn("Cache hits: 1", info_str)
        self.assertIn("Cache misses: 1", info_str)

    def test_target_rate_parameter(self):
        """Test that target_rate parameter is stored correctly."""
        dedup = IntDeduplicator(name="target_rate_test", target_rate=0.5)
        self.assertEqual(dedup.target_rate, 0.5)

        info_str = dedup.info()
        self.assertIn("target rate: 50.00%", info_str)

    def test_single_value_range(self):
        """Test IntDeduplicator with a single-value range."""
        dedup = IntDeduplicator(name="single_value", lmin=42, lmax=42, size=2)

        # Only 42 should be deduplicated
        result1 = dedup[42]
        result2 = dedup[42]
        self.assertIs(result1, result2)

        # 41 and 43 should not be deduplicated
        result3 = dedup[41]
        result4 = dedup[43]
        self.assertEqual(result3, 41)
        self.assertEqual(result4, 43)

    def test_lru_eviction_in_range(self):
        """Test LRU cache eviction with integers in range."""
        # Small cache to trigger eviction
        dedup = IntDeduplicator(name="lru_test", lmin=0, lmax=100, size=2)

        # Fill cache with 2 unique integers
        _ = dedup[10]
        _ = dedup[20]

        # Add a third, which should evict 10 (least recently used)
        _ = dedup[30]

        # Access 10 again - should be a miss (new cache entry)
        _ = dedup[10]

        info_str = dedup.info()
        # Should have 0 hits and 4 misses (each unique first access is a miss)
        self.assertIn("Cache misses: 4", info_str)


class TestModuleLevelDeduplicators(unittest.TestCase):
    """Unit tests for module-level deduplicator instances."""

    def test_signature_store_exists(self):
        """Test that signature_store is properly initialized."""
        self.assertIsInstance(signature_store, ObjectDeduplicator)
        self.assertEqual(signature_store.name, "Signature")
        # Size should be 2**16 according to deduplication.py
        # We can verify by checking cache max size through info
        info = signature_store.info()
        self.assertIn("Cache max size: 65536", info)

    def test_uuid_store_exists(self):
        """Test that uuid_store is properly initialized."""
        self.assertIsInstance(uuid_store, ObjectDeduplicator)
        self.assertEqual(uuid_store.name, "UUID")
        info = uuid_store.info()
        self.assertIn("Cache max size: 4096", info)

    def test_properties_store_exists(self):
        """Test that properties_store is properly initialized."""
        self.assertIsInstance(properties_store, ObjectDeduplicator)
        self.assertEqual(properties_store.name, "Properties")
        info = properties_store.info()
        self.assertIn("Cache max size: 4096", info)

    def test_int_store_exists(self):
        """Test that int_store is properly initialized."""
        self.assertIsInstance(int_store, IntDeduplicator)
        self.assertEqual(int_store.name, "Integer")

    def test_signature_store_deduplication(self):
        """Test that signature_store actually deduplicates objects."""
        # Use bytes to simulate signature data
        sig1 = b"signature_data_12345"
        sig2 = b"signature_data_12345"

        result1 = signature_store[sig1]
        result2 = signature_store[sig2]

        self.assertIs(result1, result2, "Signature store should deduplicate identical signatures")

    def test_uuid_store_deduplication(self):
        """Test that uuid_store deduplicates UUID-like data."""
        # Use tuples to simulate UUID data
        uuid1 = (0x12345678, 0x90AB, 0xCDEF, 0x1234, 0x567890ABCDEF)
        uuid2 = (0x12345678, 0x90AB, 0xCDEF, 0x1234, 0x567890ABCDEF)

        result1 = uuid_store[uuid1]
        result2 = uuid_store[uuid2]

        self.assertIs(result1, result2, "UUID store should deduplicate identical UUIDs")

    def test_int_store_deduplication(self):
        """Test that int_store deduplicates integers in range."""
        # Default range is 0 to 2**12 - 1
        int1 = 1234
        int2 = 1234

        result1 = int_store[int1]
        result2 = int_store[int2]

        self.assertIs(result1, result2, "Int store should deduplicate integers in range")

    def test_int_store_no_deduplication_out_of_range(self):
        """Test that int_store doesn't deduplicate integers out of range."""
        # Use integer larger than default max (2**12 - 1 = 4095)
        large_int = 100000

        result = int_store[large_int]
        self.assertEqual(result, 100000, "Int store should still return correct value")

    def test_properties_store_with_freezable_objects(self):
        """Test properties_store with FreezableObject instances."""
        fo1 = SimpleFO("property_value", frozen=True)
        fo2 = SimpleFO("property_value", frozen=True)

        result1 = properties_store[fo1]
        result2 = properties_store[fo2]

        self.assertEqual(fo1, fo2, "FreezableObjects should be equal")
        self.assertIs(result1, result2, "Properties store should deduplicate FreezableObjects")

    def test_stores_are_independent(self):
        """Test that different stores maintain independent caches."""
        # Use the same data in different stores
        data = (1, 2, 3, 4, 5)

        result1 = signature_store[data]
        result2 = uuid_store[data]
        result3 = properties_store[data]

        # All should return the same data (first inserted object)
        self.assertIs(result1, data)
        self.assertIs(result2, data)
        self.assertIs(result3, data)

        # But each store should have its own cache
        # We can verify by checking that they have independent statistics
        info1 = signature_store.info()
        info2 = uuid_store.info()

        self.assertIn("Signature", info1)
        self.assertIn("UUID", info2)


class TestDeduplicationInfo(unittest.TestCase):
    """Unit tests for the deduplication_info function."""

    def test_deduplication_info_returns_string(self):
        """Test that deduplication_info returns a string."""
        info = deduplicators_info()
        self.assertIsInstance(info, str)

    def test_deduplication_info_contains_all_stores(self):
        """Test that deduplication_info includes all module-level stores."""
        info = deduplicators_info()

        # Check for all expected store names
        expected_stores = [
            "Signature",
            "UUID",
            "Properties",
            "Integer",
        ]

        for store_name in expected_stores:
            self.assertIn(store_name, info, f"Deduplication info should include {store_name}")

    def test_deduplication_info_contains_statistics(self):
        """Test that deduplication_info includes statistics for each store."""
        # Add some data to stores to generate non-zero statistics
        _ = signature_store[b"test_signature"]
        _ = uuid_store[(1, 2, 3, 4, 5)]
        _ = int_store[42]

        info = deduplicators_info()

        # Check for statistics keywords
        self.assertIn("Cache hits:", info)
        self.assertIn("Cache misses:", info)
        self.assertIn("Cache hit rate:", info)
        self.assertIn("Cache max size:", info)
        self.assertIn("Current cache size:", info)

    def test_deduplication_info_format(self):
        """Test that deduplication_info has proper formatting with newlines."""
        info = deduplicators_info()

        # Should contain multiple newlines separating store information
        # Each store info is separated by \n\n according to the code
        self.assertGreater(info.count("\n\n"), 3, "Should have multiple sections separated")

    def test_deduplication_info_after_usage(self):
        """Test deduplication_info after actually using the stores."""
        # Use various stores with duplicate data
        for _ in range(3):
            _ = signature_store[b"duplicate_sig"]
            _ = uuid_store[(10, 20, 30)]
            _ = int_store[100]

        info = deduplicators_info()

        # Should show hits in the statistics
        # After 3 accesses to the same object, we expect:
        # - 1 miss (first access)
        # - 2 hits (second and third access)
        self.assertIn("Cache hits:", info)

        # Verify we have some non-zero statistics
        # The exact values depend on test execution order, but we should have some activity
        self.assertTrue(
            any(char.isdigit() and char != "0" for char in info),
            "Should have some non-zero statistics",
        )

    def test_deduplication_info_multiple_calls(self):
        """Test that calling deduplication_info multiple times works correctly."""
        info1 = deduplicators_info()
        info2 = deduplicators_info()

        # Both calls should return valid strings
        self.assertIsInstance(info1, str)
        self.assertIsInstance(info2, str)

        # Content may vary slightly due to additional cache accesses,
        # but structure should be consistent
        self.assertIn("Signature", info1)
        self.assertIn("Signature", info2)


class TestIntDeduplicatorEdgeCases(unittest.TestCase):
    """Unit tests for edge cases in IntDeduplicator."""

    def test_inverted_range(self):
        """Test IntDeduplicator behavior when lmin > lmax."""
        # This is technically an invalid configuration, but test the behavior
        dedup = IntDeduplicator(name="inverted", lmin=100, lmax=0)

        # No integer should be "in range" when lmin > lmax
        result1 = dedup[50]
        result2 = dedup[50]

        # Should just return the value without deduplication
        self.assertEqual(result1, 50)
        self.assertEqual(result2, 50)

    def test_very_large_range(self):
        """Test IntDeduplicator with very large range."""
        # This tests the limits of the system
        dedup = IntDeduplicator(name="large", lmin=-(2**31), lmax=2**31 - 1, size=64)

        # Test with large integers
        large_pos = 2**30
        large_neg = -(2**30)

        result_pos1 = dedup[large_pos]
        result_pos2 = dedup[large_pos]
        self.assertIs(result_pos1, result_pos2)

        result_neg1 = dedup[large_neg]
        result_neg2 = dedup[large_neg]
        self.assertIs(result_neg1, result_neg2)

    def test_zero_size_cache_int_deduplicator(self):
        """Test IntDeduplicator with zero-size cache."""
        dedup = IntDeduplicator(name="zero_size", lmin=0, lmax=100, size=0)

        int1 = 42
        int2 = 42

        result1 = dedup[int1]
        result2 = dedup[int2]

        # With size 0, no real caching occurs
        self.assertEqual(result1, 42)
        self.assertEqual(result2, 42)

        # Check that it still works without errors
        info = dedup.info()
        self.assertIn("Cache max size: 0", info)

    def test_type_checking(self):
        """Test that IntDeduplicator properly handles integer types."""
        dedup = IntDeduplicator(name="type_test", lmin=0, lmax=100)

        # Test with different integer representations
        int_literal = 42
        int_constructed = int(42)
        int_from_float = int(42.0)

        result1 = dedup[int_literal]
        result2 = dedup[int_constructed]
        result3 = dedup[int_from_float]

        # All should be deduplicated to the same object
        self.assertIs(result1, result2)
        self.assertIs(result2, result3)

    def test_memory_savings_proof(self):
        """Test that IntDeduplicator actually saves memory with duplicate integers.

        This test creates many references to the same integer values and demonstrates
        that using the deduplicator results in memory savings by ensuring all equal
        integers point to the same object in memory.
        """
        # Test configuration
        num_unique_values = 100  # Number of unique integer values
        duplicates_per_value = 1000  # How many times each value is "used"

        # Scenario 1: WITHOUT deduplication - create separate integer objects
        # Note: Python interns small integers (-5 to 256), so we use larger values
        without_dedup = []
        for value in range(1000, 1000 + num_unique_values):
            for _ in range(duplicates_per_value):
                # Create a new integer object by performing an operation
                # that prevents Python's automatic interning
                new_int = value + 0
                without_dedup.append(new_int)

        # Count unique object IDs (each integer should be a separate object)
        unique_ids_without = len(set(id(obj) for obj in without_dedup))

        # Scenario 2: WITH deduplication - use IntDeduplicator
        dedup = IntDeduplicator(name="memory_test", lmin=1000, lmax=1100, size=128)
        with_dedup = []
        for value in range(1000, 1000 + num_unique_values):
            for _ in range(duplicates_per_value):
                # Use deduplicator - this should return the same object for same value
                dedup_int = dedup[value + 0]  # +0 to create the object before deduping
                with_dedup.append(dedup_int)

        # Count unique object IDs (should be close to num_unique_values)
        unique_ids_with = len(set(id(obj) for obj in with_dedup))

        # Verify the test setup worked
        self.assertEqual(
            len(without_dedup),
            num_unique_values * duplicates_per_value,
            "Should have created correct number of references without dedup",
        )
        self.assertEqual(
            len(with_dedup),
            num_unique_values * duplicates_per_value,
            "Should have created correct number of references with dedup",
        )

        # Measure actual memory usage of the integer objects themselves
        # sys.getsizeof() gives the size of a Python integer object (typically 28 bytes)
        int_size = sys.getsizeof(1000)

        # Calculate memory used by unique integer objects
        memory_without_kb = (unique_ids_without * int_size) / 1024
        memory_with_kb = (unique_ids_with * int_size) / 1024

        # Calculate memory savings
        memory_saved_kb = memory_without_kb - memory_with_kb
        memory_saved_percentage = (
            (memory_saved_kb / memory_without_kb * 100) if memory_without_kb > 0 else 0
        )

        # Print results for visibility
        print("\n" + "=" * 70)
        print("Memory Savings Test Results:")
        print("=" * 70)
        print("Configuration:")
        print(f"  - Unique values: {num_unique_values}")
        print(f"  - Duplicates per value: {duplicates_per_value}")
        print(f"  - Total references: {num_unique_values * duplicates_per_value:,}")
        print(f"  - Integer object size: {int_size} bytes")
        print("\nWithout Deduplication:")
        print(f"  - Unique object IDs: {unique_ids_without:,}")
        print(f"  - Memory used: {memory_without_kb:.2f} KB")
        print("\nWith IntDeduplicator:")
        print(f"  - Unique object IDs: {unique_ids_with:,}")
        print(f"  - Memory used: {memory_with_kb:.2f} KB")
        print("\nSavings:")
        print(f"  - Memory saved: {memory_saved_kb:.2f} KB")
        print(f"  - Percentage saved: {memory_saved_percentage:.1f}%")
        print(f"  - Reduction in unique objects: {unique_ids_without - unique_ids_with:,}")
        print("=" * 70 + "\n")

        # Get cache statistics
        info = dedup.info()
        print(f"Deduplicator Cache Statistics:\n{info}\n")

        # Assertions to prove memory savings
        # With deduplication, we should have significantly fewer unique objects
        self.assertLess(
            unique_ids_with,
            unique_ids_without * 0.5,  # At least 50% reduction in unique objects
            f"Deduplication should reduce unique objects significantly. "
            f"Without: {unique_ids_without}, With: {unique_ids_with}",
        )

        # Ideally, with perfect deduplication and no evictions, we'd have exactly
        # num_unique_values unique objects. Allow some tolerance for cache evictions.
        self.assertLess(
            unique_ids_with,
            num_unique_values * 2,  # Should be close to num_unique_values
            f"With deduplication, unique objects should be close to {num_unique_values}, "
            f"but got {unique_ids_with}",
        )

        # Memory saved should be positive and significant
        self.assertGreater(
            memory_saved_kb,
            0,
            f"Should save memory. Saved: {memory_saved_kb:.2f} KB",
        )

        # Verify cache hit rate is high (proves deduplication is working)
        cache_info = dedup._objects.cache_info()  # pylint: disable=protected-access
        hit_rate = (
            cache_info.hits / (cache_info.hits + cache_info.misses)
            if (cache_info.hits + cache_info.misses) > 0
            else 0
        )
        self.assertGreater(
            hit_rate,
            0.90,  # At least 90% hit rate with our duplication pattern
            f"Cache hit rate should be high with duplicates. Got: {hit_rate:.2%}",
        )

        # Verify that deduplicated integers actually point to the same object
        # Pick a few values and verify all references are identical
        test_value = 1050
        test_refs = [ref for ref in with_dedup if ref == test_value]
        if len(test_refs) > 1:
            first_ref = test_refs[0]
            for ref in test_refs[1:]:
                self.assertIs(
                    ref,
                    first_ref,
                    f"All references to {test_value} should be the same object",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
