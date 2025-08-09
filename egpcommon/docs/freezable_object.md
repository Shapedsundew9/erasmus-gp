# FreezableObject

**Source File:** `freezable_object.py`
**Inherits from:** `collections.abc.Hashable`, `egpcommon.common_obj.CommonObj`

## Overview

The `FreezableObject` class provides a base for objects that can be "frozen." A frozen object becomes immutable, meaning its state cannot be changed after freezing. This characteristic is primarily useful for reducing memory consumption when many duplicate objects are utilized within an application, as immutable objects can be safely shared.

To be considered fully immutable by the `is_immutable()` check, a `FreezableObject` instance must satisfy the following conditions:

1. The object itself must be frozen (i.e., `_frozen` is `True`).
2. The object must not possess a `__dict__` attribute; all its instance data must be managed via `__slots__`.
3. All values stored within its slots must themselves be recursively immutable.

## Key Concepts

### Freezing

Freezing an object via the `freeze()` method transitions it from a mutable state to an immutable state. Once frozen, attempts to modify, add, or delete attributes will result in an `AttributeError`.

### Immutability

The `is_immutable()` method performs a recursive check to determine if an object and all its members are effectively immutable. This involves checking if the object is frozen, uses `__slots__`, and that all slotted members are also immutable (primitive immutable types, other frozen `FreezableObject` instances, or immutable collections like `tuple` and `frozenset` whose elements are also immutable).

### Slots

`FreezableObject` uses `__slots__ = ("_frozen", "__weakref__")` to manage its own internal attributes. Subclasses are expected to also use `__slots__` for all their instance data to meet the immutability criteria.

## Subclassing `FreezableObject`

When creating a class that inherits from `FreezableObject`, developers should adhere to the following guidelines:

1. **Define `__slots__`:** All instance data for the subclass must be declared in `__slots__`. Avoid using `__dict__`.
2. **Implement `__eq__` and `__hash__`:** As `FreezableObject` inherits from `collections.abc.Hashable`, subclasses *must* provide concrete implementations for `__eq__(self, value: object) -> bool` and `__hash__(self) -> int`. These methods are crucial for correct behavior, especially when frozen objects are used in sets or as dictionary keys.
3. **Initialize `FreezableObject`:** In the subclass's `__init__` method, call `super().__init__(frozen=False)` (or `FreezableObject.__init__(self, frozen=False)`) early. This initializes the `_frozen` attribute to `False`, allowing the subclass to set its initial member attributes.
4. **Call `freeze()`:** After all initial setup of the object's members is complete, call the `self.freeze()` method to transition the object to its immutable, frozen state.
5. **Handle Mutable Collections:** If a subclass uses mutable collections (e.g., `list`, `dict`) as part of its state, the subclass designer is responsible for ensuring these are appropriately handled *before* calling the base `freeze()` method. This might involve converting them to their immutable counterparts (e.g., `list` to `tuple`, `dict` to a sequence of items in a `tuple`) and ensuring any `FreezableObject` instances within these collections are also frozen if they are to contribute to the overall immutability as checked by `is_immutable()`. The `freeze()` method itself does not convert mutable collections.

## API Reference

### `__init__(self, frozen: bool = False)`

Initializes a `FreezableObject`.

* **Parameters:**
  * `frozen` (`bool`, optional): If `True`, the object is initialized as already frozen. Defaults to `False`, meaning the object is mutable and can be frozen later by calling `freeze()`.

### `freeze(self, _fo_visited_in_freeze_call: typing.Set[int] | None = None) -> None`

Freezes the object, making it immutable. This method recursively freezes:

1. The object itself (by setting `_frozen = True`).
2. Any direct members (stored in slots) that are instances of `FreezableObject`.
3. Any `FreezableObject` instances found as elements within `tuple` or `frozenset` members.

It handles cyclic references to prevent infinite recursion during the freezing process.

* **Parameters:**
  * `_fo_visited_in_freeze_call` (`typing.Set[int] | None`, optional): This is an internal parameter used to track object IDs during a single top-level `freeze()` operation to manage cycles. Developers should not provide this argument when calling `freeze()`.

### `is_frozen(self) -> bool`

Returns `True` if the object is currently marked as frozen, `False` otherwise.

### `is_immutable(self, _visited_ids: typing.Set[int] | None = None) -> bool`

Recursively verifies if the object and all its members are effectively immutable according to the defined criteria (frozen, no `__dict__`, all slotted members are immutable). It handles cyclic references during the check.

* **Parameters:**
  * `_visited_ids` (`typing.Set[int] | None`, optional): This is an internal parameter used to track object IDs during the recursion to detect cycles. Developers should not provide this argument directly.
* **Returns:** `bool` - `True` if the object and its contents are considered immutable, `False` otherwise.

### `consistency(self) -> bool`

Inherited from `CommonObj` and overridden. Checks the consistency of the `FreezableObject`.
This method specifically verifies that if an object `is_frozen()`, it must also satisfy `is_immutable()`. If it's not frozen, this check implicitly passes regarding its frozen state.

* **Returns:** `bool` - `True` if the consistency check passes.
* **Note:** The base `CommonObj.consistency()` notes that such checks can significantly slow down code.

### `verify(self) -> bool`

Inherited from `CommonObj`. The `FreezableObject` class does not override `verify()` directly, so the behavior is as defined in `CommonObj`. This method is used to check the object's data for validity (e.g., correct value ranges, lengths, types).

* **Returns:** `bool` - `True` if the verification passes.
* **Raises:** `ValueError` if the object is not valid.

### Magic Methods

#### `__copy__(self) -> Self`

Returns a shallow copy of the object.

* **Raises:** `TypeError` if the object `is_frozen()`. Subclasses may override this to provide custom unfrozen copy behavior.

#### `__deepcopy__(self, memo: dict[int, Any]) -> Self`

Returns a deep copy of the object.

* **Parameters:**
  * `memo` (`dict`): The memoization dictionary used by `deepcopy`.
* **Raises:** `TypeError` if the object `is_frozen()`. Subclasses may override this to provide custom unfrozen deep copy behavior.

#### `__delattr__(self, name: str) -> None`

Called for attribute deletion.

* **Parameters:**
  * `name` (`str`): The name of the attribute to delete.
* **Raises:** `AttributeError` if the object `is_frozen()`.

#### `__setattr__(self, name: str, value: Any) -> None`

Called for attribute assignment.

* **Parameters:**
  * `name` (`str`): The name of the attribute to set.
  * `value` (`Any`): The value to assign to the attribute.
* **Raises:** `AttributeError` if the object `is_frozen()` and the attribute being set is not `_frozen` itself. (The `_frozen` attribute can be set internally by `__init__` and `freeze`.)

#### `__eq__(self, value: object) -> bool`

**Abstract Method.** Subclasses *must* implement this method to define equality.

* **Raises:** `NotImplementedError` if not overridden by a subclass.

#### `__hash__(self) -> int`

**Abstract Method.** Subclasses *must* implement this method to allow the object to be hashable (e.g., for use in sets or as dictionary keys). The hash value should be consistent with the `__eq__` implementation: if `a == b` is true, then `hash(a) == hash(b)` must also be true.

* **Raises:** `NotImplementedError` if not overridden by a subclass.

### Internal Helper Methods

The class also contains the following static and internal helper methods, which are primarily for internal use by `freeze()` and `is_immutable()` and are not typically called directly by users of the class:

* `_get_all_data_slots(self) -> typing.Set[str]`: Retrieves all unique slot names intended for member data from the class and its superclasses (excluding `_frozen` and `__weakref__`).
* `_is_value_recursively_immutable(value: Any, _visited_ids: typing.Set[int]) -> bool`: A static helper to determine if an arbitrary value is recursively immutable.
* `_recursively_freeze_member_value(value: Any, _fo_visited_in_freeze_call: typing.Set[int]) -> None`: A static helper to recursively process a value for freezing, calling `freeze()` on nested `FreezableObject` instances.

## Example (Conceptual Subclass)

```python
from freezable_object import FreezableObject #
from typing import Tuple

class MyImmutableData(FreezableObject):
    __slots__ = ('_id', '_name', '_values')

    def __init__(self, id_val: int, name_val: str, values_list: list[int]):
        super().__init__(frozen=False) # Initialize as mutable
        self._id = id_val
        self._name = name_val
        # Convert mutable list to immutable tuple before freezing
        self._values: Tuple[int, ...] = tuple(values_list) #

        # Freeze the object after all members are set
        self.freeze() #

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MyImmutableData):
            return NotImplemented
        return (self._id == other._id and
                self._name == other._name and
                self._values == other._values)

    def __hash__(self) -> int:
        return hash((self._id, self._name, self._values))

    # verify() and consistency() could be overridden if specific checks
    # beyond what FreezableObject provides are needed.

# Usage
data1 = MyImmutableData(1, "TestData", [10, 20, 30])
print(f"Is data1 frozen? {data1.is_frozen()}") # True
print(f"Is data1 immutable? {data1.is_immutable()}") # True

try:
    data1._name = "NewName" # This will raise AttributeError
except AttributeError as e:
    print(e)

# To create a modifiable version, you would typically implement a
# dedicated method if needed, e.g., an 'unfreeze_copy()' or similar,
# or simply create a new instance.
# shallow_copy = copy(data1) # This will raise TypeError as data1 is frozen
```
