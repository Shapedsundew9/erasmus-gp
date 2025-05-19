# ObjectDict

The `ObjectDict` class provides a dictionary-like collection that stores unique objects, aiming to reduce memory consumption when many duplicate objects might otherwise exist. It achieves this by using a `WeakValueDictionary` internally, which allows objects to be garbage-collected if they are no longer referenced elsewhere, and by ensuring that only one instance of an object (for a given key) is stored.

It is part of the `egpcommon` library and inherits from `egpcommon.common_obj.CommonObj`, providing base `verify()` and `consistency()` methods, and `collections.abc.Collection`.

## Overview

`ObjectDict` is designed for scenarios where you need to access unique objects using a key, but want to avoid storing multiple identical copies of these objects in memory. When an object is added, if an object for that key already exists, the existing object is returned and no new object is stored. This is particularly useful for large datasets or applications with many repeating data structures.

A key feature is its use of `weakref.WeakValueDictionary`. This means the `ObjectDict` holds weak references to the *values* it stores. If an object (value) stored in the `ObjectDict` has no other strong references pointing to it from elsewhere in the application, it can be automatically removed by Python's garbage collector.

**Important Note on `__setitem__`**: The `ObjectDict` does not implement the `__setitem__` method (i.e., `my_dict[key] = value`). This is a deliberate design choice to prevent accidental overwriting of existing unique objects. The `add()` method must be used to insert objects.

## Getting Started

Here's a simple example of how to use `ObjectDict`:

```python
from egpcommon.object_dict import ObjectDict
from egpcommon.freezable_object import FreezableObject # Assuming a concrete implementation

# Create a sample FreezableObject (must be frozen to be added)
class MyData(FreezableObject):
    __slots__ = ('_value',)
    def __init__(self, value, frozen=False):
        super().__init__(frozen=frozen)
        self._value = value
        if not frozen: # Typically freeze after all attributes are set
            self.freeze()

    def __eq__(self, other):
        if not isinstance(other, MyData):
            return NotImplemented
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return f"MyData({self._value}, frozen={self.is_frozen()})"

# Initialize an ObjectDict
data_store = ObjectDict(name="MyUniqueData")

# Create some objects
obj1 = MyData("apple", frozen=True)
obj2 = MyData("banana", frozen=True)
obj3_duplicate_of_obj1_by_key_and_value = MyData("apple", frozen=True)

# Add objects
# added_obj1 will be obj1
added_obj1 = data_store.add(key="fruit1", obj=obj1)
print(f"Added {added_obj1}, Is it the same as obj1? {added_obj1 is obj1}")

# added_obj2 will be obj2
added_obj2 = data_store.add(key="fruit2", obj=obj2)
print(f"Added {added_obj2}, Is it the same as obj2? {added_obj2 is obj2}")

# Try to add an object with the same key "fruit1"
# existing_obj will be obj1, not obj3_duplicate_of_obj1_by_key_and_value
existing_obj = data_store.add(key="fruit1", obj=obj3_duplicate_of_obj1_by_key_and_value)
print(f"Attempted to add with duplicate key: {existing_obj}")
print(f"Is it the same as obj1? {existing_obj is obj1}")
print(f"Is it the same as obj3? {existing_obj is obj3_duplicate_of_obj1_by_key_and_value}")

print(f"Number of unique objects: {len(data_store)}") # Output: 2
data_store.info()

# Accessing an object
retrieved_obj = data_store["fruit1"]
print(f"Retrieved: {retrieved_obj}")

# Check for key existence
print(f"Contains key 'fruit1': {'fruit1' in data_store}") # True
print(f"Contains key 'fruit3': {'fruit3' in data_store}") # False
```

## API Reference

### `__init__(self, name: str)`

Initializes an `ObjectDict` instance.

* **Parameters:**
  * `name` (`str`): A name for the `ObjectDict`, primarily used for identification in logging and information messages.

-----

### `add(self, key: Hashable, obj: Any) -> Any`

Adds an object to the dictionary, associated with the given key.

If the key already exists in the dictionary, this method does **not** overwrite the existing object. Instead, it returns the object already associated with that key. If the key does not exist, the new object is added, and then this new object is returned.

**Constraint for `FreezableObject` instances:** If the `obj` being added is an instance of `FreezableObject` (or its subclasses), it **must** be in a frozen state. An `AssertionError` will be raised if a `FreezableObject` that is not frozen is passed. This ensures the immutability of objects managed by `ObjectDict`, which is crucial for consistency, especially since their hash values are used.

* **Parameters:**
  * `key` (`Hashable`): The hashable key under which to store the object.
  * `obj` (`Any`): The object to store.
* **Returns:**
  * `Any`: The object that is now associated with the key in the dictionary. This will be the passed `obj` if the key was new, or the existing object if the key was already present.
* **Raises:**
  * `AssertionError`: If `obj` is a `FreezableObject` and `obj.is_frozen()` is `False`.

-----

### `__getitem__(self, key: Any) -> Any`

Retrieves the object associated with the given key.

* **Parameters:**
  * `key` (`Any`): The key of the object to retrieve.
* **Returns:**
  * `Any`: The object associated with the key.
* **Raises:**
  * `KeyError`: If the key is not found in the dictionary.

-----

### `__len__(self) -> int`

Returns the number of unique objects currently stored in the dictionary.

* **Returns:**
  * `int`: The count of key-object pairs.

-----

### `__contains__(self, key: Any) -> bool`

Checks if the given `key` is present in the `ObjectDict`.
Note that this method checks for the existence of a *key*, not whether a specific object *instance* (value) is present if you don't know its key.

* **Parameters:**
  * `key` (`Any`): The key to check for.
* **Returns:**
  * `bool`: `True` if the key exists in the dictionary, `False` otherwise.

-----

### `__iter__(self) -> Iterator[Any]`

Returns an iterator over the keys in the `ObjectDict`.

* **Returns:**
  * `Iterator[Any]`: An iterator yielding the keys.

-----

### `clear(self) -> None`

Removes all objects from the `ObjectDict`. The internal counters for added objects and duplicate attempts are also reset.

-----

### `info(self) -> str`

Logs and returns a string containing information about the `ObjectDict`, including its name, the current number of objects, the total number of objects successfully added, and the number of duplicate addition attempts.

* **Returns:**
  * `str`: An information string.

-----

### `remove(self, key: Hashable) -> None`

Removes the object associated with the given key from the `ObjectDict`.

* **Parameters:**
  * `key` (`Hashable`): The key of the object to remove.
* **Raises:**
  * `KeyError`: If the key is not found in the dictionary.

-----

### `verify(self) -> bool`

Performs a verification check on the `ObjectDict` object. This method prints information about the dictionary using `info()` and then calls the `verify()` method of its superclass, `CommonObj`. The base `CommonObj.verify()` method is used to check data for validity (e.g., correct value ranges, types) and raises a `ValueError` if the object is not valid.

* **Returns:**
  * `bool`: `True` if verification passes.
* **Raises:**
  * `ValueError`: If the object's data is found to be invalid by the `CommonObj.verify()` checks.

-----

### `consistency(self) -> bool`

Inherited from `egpcommon.common_obj.CommonObj`.
Checks the semantic consistency of the `ObjectDict`. While `verify()` checks individual values, `consistency()` checks relationships between values. It raises a `RuntimeError` if the object is not consistent. For `ObjectDict` itself, the base implementation from `CommonObj` is used, which by default returns `True` unless overridden with more specific checks.

* **Returns:**
  * `bool`: `True` if the consistency check passes.
* **Raises:**
  * `RuntimeError`: If the object is found to be inconsistent.

## Important Considerations

* **Memory Management via `WeakValueDictionary`:** The underlying `WeakValueDictionary` allows values to be garbage collected when they are no longer referenced elsewhere. This is automatic and helps manage memory efficiently. However, it means that a value might disappear from the dictionary if all other strong references to it are removed.
* **Immutability of `FreezableObject`s:** When storing instances of `FreezableObject`, they *must* be frozen. This is critical because dictionary keys (and in this case, the managed objects that dictate uniqueness often via their hash) should be immutable. If a `FreezableObject` were mutable, its hash could change after being added, corrupting the dictionary's internal state.
* **Thread Safety:** The provided code does not show any explicit mechanisms for thread safety. If an `ObjectDict` instance is accessed and modified by multiple threads concurrently, external locking mechanisms may be necessary.

## Related Classes

### ObjectSet

The `egpcommon.object_set.ObjectSet` class inherits from `ObjectDict`. It specializes `ObjectDict` to behave like a set of unique objects. It achieves this by overriding the `add` method:

```python
# In ObjectSet:
def add(self, obj: Any) -> Any: # type: ignore
    """Add a object to the set."""
    return super().add(obj, obj) # obj is used as both key and value
```

In an `ObjectSet`, the object itself is used as the key. This means methods like `__contains__(self, obj)` in an `ObjectSet` instance will effectively check for the presence of the `obj` itself within the set. Like `ObjectDict`, objects added to an `ObjectSet` that are instances of `FreezableObject` must be frozen.
