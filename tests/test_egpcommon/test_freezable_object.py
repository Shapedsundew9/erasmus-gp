"""Unit test cases for the FreezableObject class."""

import unittest
from collections.abc import Hashable
from copy import deepcopy
from typing import Any

from egpcommon.freezable_object import FreezableObject


# Test Helper Classes
class SimpleValueFO(FreezableObject):
    """Simple value FreezableObject for testing."""

    __slots__ = ("value",)

    def __init__(self, value: Any, frozen: bool = False):  # Default to mutable for test setup ease
        """Initialize a SimpleValueFO object."""
        super().__init__(frozen=False)
        self.value = value
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SimpleValueFO):
            return NotImplemented
        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value) if isinstance(self.value, Hashable) else id(self.value)

    def __repr__(self) -> str:
        return f"SimpleValueFO({self.value!r}, frozen={self.is_frozen()})"


class PointAnatomyFO(FreezableObject):  # Renamed to avoid conflict with potential Point class
    """Point with x, y coordinates."""

    __slots__ = ("x", "y")

    def __init__(self, x: int, y: int, frozen: bool = False):
        """Initialize a PointAnatomyFO object."""
        super().__init__(frozen=False)
        self.x = x
        self.y = y
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PointAnatomyFO):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self) -> int:
        return hash((self.x, self.y))


class CompositeFO(FreezableObject):
    """Composite FreezableObject containing two items."""

    __slots__ = ("item_a", "item_b")

    def __init__(self, item_a: Any, item_b: Any, frozen: bool = False):
        """Initialize a CompositeFO object."""
        super().__init__(frozen=False)
        self.item_a = item_a
        self.item_b = item_b
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CompositeFO):
            return NotImplemented
        return (self.item_a, self.item_b) == (other.item_a, other.item_b)

    def __hash__(self) -> int:  # Simplified hash for testing
        h1 = hash(self.item_a) if isinstance(self.item_a, Hashable) else id(self.item_a)
        h2 = hash(self.item_b) if isinstance(self.item_b, Hashable) else id(self.item_b)
        return hash((h1, h2))


class SlottedOnlyFO(FreezableObject):  # No __dict__
    """Slotted object with a single data slot."""

    __slots__ = ("data",)

    def __init__(self, data: Any, frozen: bool = False):
        """Initialize a SlottedOnlyFO object."""
        super().__init__(frozen=False)
        self.data = data
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SlottedOnlyFO) and self.data == other.data

    def __hash__(self) -> int:
        return hash(self.data)


class UnslottedChildGetsDictFO(FreezableObject):  # Will have a __dict__
    """Child of FreezableObject with no slots."""

    # No __slots__ defined here, so it gets a __dict__
    def __init__(self, attr1: Any, attr2: Any, frozen: bool = False):
        """Initialize an UnslottedChildGetsDictFO object."""
        super().__init__(frozen=False)
        self.attr1 = attr1  # Goes into instance __dict__
        self.attr2 = attr2  # Goes into instance __dict__
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnslottedChildGetsDictFO):
            return NotImplemented
        return (self.attr1, self.attr2) == (other.attr1, other.attr2)

    def __hash__(self) -> int:
        return hash((self.attr1, self.attr2))


class EmptySlotsOnlyFO(FreezableObject):
    """FreezableObject with no data slots."""

    __slots__ = ()  # No new data slots

    def __init__(self, frozen: bool = False):
        super().__init__(frozen=frozen)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EmptySlotsOnlyFO)

    def __hash__(self) -> int:
        return id(EmptySlotsOnlyFO)  # Type hash


class UnsetAttributeFO(FreezableObject):
    """FreezableObject with one set and one unset attribute."""

    __slots__ = ("val_a", "val_b")

    def __init__(self, val_a: Any, frozen: bool = False):
        """Initialize an UnsetAttributeFO object."""
        super().__init__(frozen=False)
        self.val_a = val_a  # val_b is not set
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:  # pragma: no cover
        if not isinstance(other, UnsetAttributeFO):
            return NotImplemented
        has_a_self = hasattr(self, "val_a")
        has_a_other = hasattr(other, "val_a")
        has_b_self = hasattr(self, "val_b")
        has_b_other = hasattr(other, "val_b")
        return (
            has_a_self == has_a_other
            and (not has_a_self or self.val_a == other.val_a)
            and has_b_self == has_b_other
            # pylint: disable=no-member
            and (not has_b_self or self.val_b == other.val_b)
        )

    def __hash__(self) -> int:
        return hash(self.val_a if hasattr(self, "val_a") else None)


class GrandchildWithSlotsFO(PointAnatomyFO):  # Inherits x, y slots
    """Grandchild with additional z_coord slot."""

    __slots__ = ("z_coord",)  # Adds z_coord

    def __init__(self, x: int, y: int, z_coord: int, frozen: bool = False):
        super().__init__(frozen=False, x=x, y=y)
        self.z_coord = z_coord
        if frozen:
            self.freeze()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GrandchildWithSlotsFO):
            return NotImplemented
        return (self.x, self.y, self.z_coord) == (other.x, other.y, other.z_coord)

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z_coord))


class UnknownTypeForTesting:
    """A class that is not hashable and not frozen."""


class TestFreezableObject(unittest.TestCase):
    """Unit tests for the FreezableObject class."""

    def test_initialization_and_is_frozen(self):
        """Test initialization and frozen status."""
        obj_f = SimpleValueFO("val", frozen=True)
        self.assertTrue(obj_f.is_frozen())
        obj_m = SimpleValueFO("val", frozen=False)
        self.assertFalse(obj_m.is_frozen())
        empty_f = EmptySlotsOnlyFO(frozen=True)  # Test base __init__ via super()
        self.assertTrue(empty_f.is_frozen())

    def test_setattr_delattr_frozen(self):
        """Test setting and deleting attributes on frozen objects."""
        obj = SimpleValueFO("data", frozen=True)
        with self.assertRaisesRegex(
            AttributeError, "object is frozen; cannot set attribute 'value'"
        ):
            obj.value = "new"
        with self.assertRaisesRegex(
            AttributeError, "object is frozen; cannot set attribute 'new_attr'"
        ):
            # pylint: disable=attribute-defined-outside-init
            obj.new_attr = "fail"  # type: ignore
        with self.assertRaisesRegex(
            AttributeError, "object is frozen; cannot delete attribute 'value'"
        ):
            del obj.value
        # Test internal _frozen setting bypass (done by freeze/init)
        object.__setattr__(obj, "_frozen", False)
        obj.value = "allowed"
        self.assertEqual(obj.value, "allowed")

    def test_setattr_delattr_mutable(self):
        """Test setting and deleting attributes on mutable objects."""
        obj = SimpleValueFO("data", frozen=False)
        obj.value = "new"
        self.assertEqual(obj.value, "new")
        with self.assertRaises(AttributeError):  # Slotted objects cannot get new attributes easily
            # pylint: disable=attribute-defined-outside-init
            obj.new_attr = "fail"  # type: ignore
        del obj.value
        self.assertFalse(hasattr(obj, "value"))

    def test_freeze_method_basic_and_idempotency(self):
        """Test freeze method and idempotency."""
        obj = SimpleValueFO("data", frozen=False)
        obj.freeze()
        self.assertTrue(obj.is_frozen())
        obj.freeze()
        self.assertTrue(obj.is_frozen())  # Idempotent
        with self.assertRaises(AttributeError):
            obj.value = "no"

    def test_get_all_data_slots(self):
        """Test _get_all_data_slots method."""
        # pylint: disable=protected-access
        self.assertEqual(SimpleValueFO(None)._get_all_data_slots(), {"value"})
        self.assertEqual(PointAnatomyFO(1, 2)._get_all_data_slots(), {"x", "y"})
        self.assertEqual(
            GrandchildWithSlotsFO(1, 2, 3)._get_all_data_slots(), {"x", "y", "z_coord"}
        )
        self.assertEqual(EmptySlotsOnlyFO()._get_all_data_slots(), set())
        # UnslottedChildGetsDictFO inherits only FreezableObject's slots, none are data slots
        self.assertEqual(UnslottedChildGetsDictFO(1, 2)._get_all_data_slots(), set())

    def test_freeze_recursive_fo_members(self):
        """Test freeze on recursive FreezableObject members."""
        inner = SimpleValueFO("in", frozen=False)
        outer = CompositeFO(inner, "str", frozen=False)
        outer.freeze()
        self.assertTrue(outer.is_frozen() and inner.is_frozen())

    def test_freeze_recursive_collections_with_fo(self):
        """Test freeze on collections containing FreezableObjects."""
        f_tuple = SimpleValueFO("ft", frozen=False)
        f_fset = SimpleValueFO("ffs", frozen=False)
        obj = CompositeFO((f_tuple, "el"), frozenset([f_fset, 1]), frozen=False)
        obj.freeze()
        self.assertTrue(obj.is_frozen() and f_tuple.is_frozen() and f_fset.is_frozen())
        # Ensure non-FOs in collections are not affected beyond being part of frozen parent
        self.assertIsInstance(obj.item_a[1], str)  # type: ignore[attr-defined]

    def test_freeze_cyclic_dependencies(self):
        """Test freeze on cyclic dependencies."""
        obj1 = CompositeFO(None, None, frozen=False)
        obj2 = SimpleValueFO(None, frozen=False)
        obj1.item_a = obj2
        obj1.item_b = obj1  # Cycle: obj1.b -> obj1
        obj2.value = obj1  # Cycle: obj2.value -> obj1
        obj1.freeze()  # Should handle cycles and freeze all reachable FOs
        self.assertTrue(obj1.is_frozen() and obj2.is_frozen())
        # Test freeze on already frozen cycle
        obj2.freeze()
        self.assertTrue(obj1.is_frozen() and obj2.is_frozen())

    def test_is_immutable_basics_frozen_status_and_dict(self):
        """Test is_immutable method for frozen and unfrozen objects."""
        self.assertFalse(SimpleValueFO("v", frozen=False).is_immutable(), "Unfrozen not immutable")
        # UnslottedChildGetsDictFO will have __dict__
        dict_obj_f = UnslottedChildGetsDictFO("a", "b", frozen=True)
        self.assertTrue(hasattr(dict_obj_f, "__dict__"))
        self.assertFalse(dict_obj_f.is_immutable(), "Frozen with __dict__ not immutable by rule")
        # SlottedOnlyFO has no __dict__
        no_dict_obj_f = SlottedOnlyFO("v", frozen=True)
        self.assertFalse(hasattr(no_dict_obj_f, "__dict__"))
        self.assertTrue(no_dict_obj_f.is_immutable())

    def test_is_immutable_primitive_and_known_immutable_members(self):
        """Test is_immutable method for known immutable members."""
        self.assertTrue(PointAnatomyFO(1, 2, frozen=True).is_immutable())
        self.assertTrue(SimpleValueFO("str", frozen=True).is_immutable())
        self.assertTrue(SimpleValueFO(None, frozen=True).is_immutable())
        self.assertTrue(SimpleValueFO((1, "t"), frozen=True).is_immutable())
        self.assertTrue(SimpleValueFO(frozenset(["a", 1]), frozen=True).is_immutable())

    def test_is_immutable_known_mutable_member(self):
        """Test is_immutable method for known mutable members."""
        self.assertFalse(SimpleValueFO([1, 2], frozen=True).is_immutable())
        self.assertFalse(SimpleValueFO({"a": 1}, frozen=True).is_immutable())
        self.assertFalse(SimpleValueFO({1}, frozen=True).is_immutable())

    def test_is_immutable_recursive_fo_members(self):
        """Test is_immutable method for recursive FreezableObject members."""
        # Case 1: Inner is immutable (frozen and simple value) - This should be fine
        inner_immutable = SimpleValueFO("inner_val", frozen=True)
        outer_frozen1 = CompositeFO(inner_immutable, "str", frozen=True)
        self.assertTrue(
            outer_frozen1.is_immutable(), "Outer with immutable FO member should be immutable"
        )

        # Case 2: Test is_immutable when outer is marked frozen but its FO member remains unfrozen.
        # This requires bypassing the deep freeze of the outer object's __init__/freeze.
        inner_remains_unfrozen = SimpleValueFO("inner_unfrozen_val", frozen=False)
        # Create outer as mutable first
        outer_for_case2 = CompositeFO(inner_remains_unfrozen, "str", frozen=False)
        # Manually mark outer as frozen WITHOUT calling its full freeze() method,
        # thus not affecting inner_remains_unfrozen's frozen state.
        object.__setattr__(outer_for_case2, "_frozen", True)

        self.assertTrue(outer_for_case2.is_frozen(), "Outer container should be marked frozen")
        self.assertFalse(
            inner_remains_unfrozen.is_frozen(), "Inner FO should remain unfrozen for this test path"
        )
        self.assertFalse(
            outer_for_case2.is_immutable(),
            "Outer (marked frozen) with an actually unfrozen FO member should NOT be immutable",
        )

        # Case 3: Inner FO is frozen but itself contains a mutable type - This logic should be fine
        inner_fo_holds_list = SimpleValueFO([1, 2], frozen=True)
        # outer_frozen3's freeze() will re-freeze inner_fo_holds_list (which is fine/idempotent)
        # and inner_fo_holds_list itself is not immutable due to the list.
        outer_frozen3 = CompositeFO(inner_fo_holds_list, "str", frozen=True)
        self.assertTrue(outer_frozen3.is_frozen())
        self.assertTrue(inner_fo_holds_list.is_frozen())
        self.assertFalse(
            inner_fo_holds_list.is_immutable(), "Inner FO holding list is not immutable"
        )  # Verify this helper assertion
        self.assertFalse(
            outer_frozen3.is_immutable(),
            "Outer with FO member (that is frozen but holds mutable list) should not be immutable",
        )

    def test_is_immutable_tuple_frozenset_recursive(self):
        """Test is_immutable method for tuples and frozensets with recursive members."""
        fo_imm = SimpleValueFO("i", frozen=True)
        fo_mut_val = SimpleValueFO([1], frozen=True)  # Not truly immutable
        # Tuple/frozenset with all immutable elements
        self.assertTrue(SimpleValueFO((fo_imm, "s"), frozen=True).is_immutable())
        self.assertTrue(SimpleValueFO(frozenset([fo_imm, 1]), frozen=True).is_immutable())
        # Tuple/frozenset with a non-immutable FO (due to its value)
        self.assertFalse(SimpleValueFO((fo_mut_val, "s"), frozen=True).is_immutable())
        # Tuple/frozenset with a direct mutable element
        self.assertFalse(SimpleValueFO(([1, 2], "s"), frozen=True).is_immutable())

    def test_is_immutable_unknown_custom_type_member(self):
        """Test is_immutable method for unknown custom types."""
        self.assertFalse(SimpleValueFO(UnknownTypeForTesting(), frozen=True).is_immutable())

    def test_is_immutable_cycles(self):
        """Test is_immutable method for cycles."""
        obj_a = CompositeFO(None, "A", frozen=False)
        obj_b = CompositeFO(None, "B", frozen=False)
        obj_a.item_a = obj_b
        obj_b.item_a = obj_a  # Cycle A <-> B
        obj_a.freeze()  # Freezes both
        self.assertTrue(obj_a.is_immutable() and obj_b.is_immutable())

        obj_c = CompositeFO(None, [1, 2], frozen=False)  # C holds a list
        obj_d = CompositeFO(obj_c, "D", frozen=False)  # D points to C
        obj_c.item_a = obj_d  # Cycle C <-> D
        obj_c.freeze()  # Freezes both C and D
        self.assertFalse(obj_c.is_immutable(), "C has list, so not immutable")
        self.assertFalse(obj_d.is_immutable(), "D contains C (which is not imm), so D not imm")

        # Self-referential tuple/frozenset containing an immutable FO
        _ = SimpleValueFO(None, frozen=True)
        # Note: Python doesn't easily allow direct creation of t = (t,)
        # We test cycles of FOs *within* tuples for is_immutable:
        c_obj1 = SimpleValueFO(None, frozen=False)
        c_obj2 = SimpleValueFO(None, frozen=False)
        c_obj1.value = (c_obj2,)
        c_obj2.value = (c_obj1,)  # (c_obj1 ( (c_obj2 ( (c_obj1 ... ) ) ) ) )
        c_obj1.freeze()  # Freezes both
        self.assertTrue(c_obj1.is_immutable())

    def test_is_immutable_empty_and_unset_slots(self):
        """Test is_immutable method for empty and unset slots."""
        self.assertTrue(EmptySlotsOnlyFO(frozen=True).is_immutable())
        # UnsetAttributeFO: val_a is primitive, val_b is unset
        self.assertTrue(UnsetAttributeFO("a_val", frozen=True).is_immutable())
        # UnsetAttributeFO: val_a is mutable list, val_b is unset
        self.assertFalse(UnsetAttributeFO([1, 2], frozen=True).is_immutable())

    def test_interaction_freeze_then_is_immutable(self):
        """Test interaction of freeze and is_immutable."""
        inner = SimpleValueFO("d", frozen=False)
        outer = CompositeFO((inner, "s"), None, frozen=False)
        outer.freeze()  # Freezes outer and recursively inner
        self.assertTrue(outer.is_immutable())

        outer_list = CompositeFO([SimpleValueFO("d2", frozen=False)], "s2", frozen=False)
        outer_list.freeze()  # Freezes outer_list, but its list member remains a list,
        # and the FO inside the list is *not* frozen by this process.
        self.assertTrue(outer_list.is_frozen())
        self.assertFalse(outer_list.item_a[0].is_frozen())  # type: ignore[attr-defined]
        self.assertFalse(outer_list.is_immutable())

    def test_abstract_methods_notimplemented(self):
        """Test abstract methods for FreezableObject."""
        # pylint: disable=abstract-method
        # pylint disable=abstract-class-instantiated

        # Test for BrokenFO (missing both __eq__ and __hash__)
        class BrokenFO(FreezableObject):
            """Class that does not implement __eq__ or __hash__."""

            __slots__ = ()

        # This part is correct and should pass if FreezableObject is a proper ABC
        with self.assertRaisesRegex(
            TypeError,
            (
                "Can't instantiate abstract class BrokenFO without an "
                "implementation for abstract methods '__eq__', '__hash__'"
            ),
        ):
            # pylint: disable=abstract-class-instantiated
            BrokenFO()  # type: ignore

        # Test for PartiallyBrokenFO (implements __eq__, missing __hash__)
        class PartiallyBrokenFO(FreezableObject):
            """Class that implements __eq__ but not __hash__."""

            __slots__ = ()

            def __eq__(self, other: object) -> bool:
                return True

            # No __hash__ defined here; Python will set it to None

        # 1. Verify that PartiallyBrokenFO can be instantiated
        pb_instance = None
        try:
            # pylint: disable=abstract-class-instantiated
            pb_instance = PartiallyBrokenFO()
        except TypeError:  # pragma: no cover
            self.fail("PartiallyBrokenFO should be instantiable; Python sets __hash__ = None.")

        self.assertIsNotNone(pb_instance, "PartiallyBrokenFO instance should have been created.")

        # 2. Verify that the class's __hash__ attribute is indeed None
        self.assertIsNone(
            PartiallyBrokenFO.__hash__,
            "PartiallyBrokenFO.__hash__ should be implicitly set to None by Python.",
        )

        # 3. Verify that attempting to hash an instance raises TypeError
        with self.assertRaisesRegex(TypeError, "unhashable type: 'PartiallyBrokenFO'"):
            hash(pb_instance)

            def test_deepcopy_mutable(self):
                """Test __deepcopy__ on mutable (unfrozen) FreezableObject."""
                obj = CompositeFO(SimpleValueFO([1, 2]), PointAnatomyFO(1, 2))
                obj_copy = deepcopy(obj)
                self.assertIsInstance(obj_copy, CompositeFO)
                self.assertFalse(obj_copy.is_frozen())
                self.assertIsNot(obj_copy, obj)
                # Deepcopy should also copy members
                self.assertIsNot(obj_copy.item_a, obj.item_a)
                self.assertIsNot(obj_copy.item_b, obj.item_b)
                self.assertEqual(obj_copy.item_a, obj.item_a)
                self.assertEqual(obj_copy.item_b, obj.item_b)
                # Changing copy does not affect original
                obj_copy.item_a.value.append(3)
                self.assertNotEqual(obj_copy.item_a.value, obj.item_a.value)

            def test_deepcopy_frozen_raises(self):
                """Test __deepcopy__ raises TypeError on frozen FreezableObject."""
                obj = CompositeFO(SimpleValueFO("abc"), PointAnatomyFO(1, 2))
                obj.freeze()
                with self.assertRaisesRegex(TypeError, "object is frozen; cannot deepcopy"):
                    deepcopy(obj)

            def test_deepcopy_preserves_slots(self):
                """Test __deepcopy__ preserves slot attributes and does not copy unset slots."""
                obj = UnsetAttributeFO("foo")
                obj_copy = deepcopy(obj)
                self.assertTrue(hasattr(obj_copy, "val_a"))
                self.assertFalse(hasattr(obj_copy, "val_b"))
                self.assertEqual(obj_copy.val_a, "foo")
                # Set val_b and test again
                obj.val_b = "bar"
                obj_copy2 = deepcopy(obj)
                self.assertEqual(obj_copy2.val_b, "bar")
                self.assertEqual(obj_copy2.val_a, "foo")

            def test_deepcopy_handles_nested_freezable_objects(self):
                """Test __deepcopy__ correctly copies nested FreezableObjects."""
                inner = SimpleValueFO("inner")
                outer = CompositeFO(inner, "outer")
                outer_copy = deepcopy(outer)
                self.assertIsInstance(outer_copy.item_a, SimpleValueFO)
                self.assertIsNot(outer_copy.item_a, inner)
                self.assertEqual(outer_copy.item_a.value, "inner")
                self.assertEqual(outer_copy.item_b, "outer")


if __name__ == "__main__":
    unittest.main(verbosity=2)
