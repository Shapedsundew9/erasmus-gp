"""FreezableObject class.
A FreezableObject is a object that can be frozen. A frozen object is immutable and cannot
be changed. This is used to reduce memory consumption when a lot of duplicate objects are
used in a program."""

import types
from abc import ABCMeta, abstractmethod
from copy import copy, deepcopy
from collections.abc import Hashable
from typing import Self, Any, Set as TypingSet  # Using TypingSet for type hint for clarity
from egpcommon.common_obj import CommonObj
from egpcommon.object_set import ObjectSet
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Define tuples of known types for efficient checking.
# These can be expanded if other specific types need to be categorized.
_KNOWN_IMMUTABLE_TYPES_TUPLE = (
    int,
    float,
    complex,
    str,
    bytes,
    bool,
    type(None),  # Basic immutable types
    range,
    tuple,
    frozenset,  # Immutable collections
    type(Ellipsis),  # Ellipsis object
    types.FunctionType,
    types.BuiltinFunctionType,  # Function types
    types.MethodType,
    types.WrapperDescriptorType,  # Method types
    types.MethodDescriptorType,
    types.ClassMethodDescriptorType,
    types.GetSetDescriptorType,  # Descriptor types
    type,  # Class objects (types) themselves
)

_KNOWN_MUTABLE_TYPES_TUPLE = (
    list,
    dict,
    set,
    bytearray,
    # Consider adding collections.deque, collections.defaultdict, etc., if they might appear
)


class FreezableObject(Hashable, CommonObj, metaclass=ABCMeta):
    """
    FreezableObject class.

    A FreezableObject is an object that can be frozen. A frozen object is immutable and cannot
    be changed. This is used to reduce memory consumption when a lot of duplicate objects are
    used in a program.

    To be considered fully immutable by the `is_immutable` check, a FreezableObject instance
    must:
    1. Be frozen (self._frozen is True).
    2. Not have a `__dict__` attribute (i.e., all its instance data must be in `__slots__`).
    3. All values stored in its slots must themselves be immutable according to the recursive check.

    When creating a FreezableObject subclass, ensure that:
    - All instance data is defined in `__slots__`.
    - The `__eq__` and `__hash__` methods are implemented to ensure proper equality and hashing.
    - The FreezableObject.__init__() is called immediately with frozen=False to allow members
      to be initialized.
    - The `freeze()` method is called to freeze the object and its members after all
      initialization is complete.
    """

    __slots__ = ("_frozen", "__weakref__")
    object_store: ObjectSet  # pylint: disable=declare-non-slot

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """
        This hook is called when a class inherits from FreezableObject.
        'cls' is the new subclass being created.
        """
        # Call the parent's __init_subclass__ to be cooperative
        super().__init_subclass__(**kwargs)

        # Create the ObjectSet instance, labeled with the new class's name
        # Attach the store as a CLASS ATTRIBUTE to the new subclass
        cls.object_store = ObjectSet(name=cls.__name__)

    def __init__(self, frozen: bool = False) -> None:
        """
        Initialize a FreezableObject object.

        Args:
            frozen (bool): If True, the object is initialized as frozen.
                           If False, it's mutable and can be frozen later via `freeze()`.
        """
        # Using object.__setattr__ bypasses our overridden __setattr__,
        # which is necessary as _frozen controls writability itself.
        self._frozen: bool = frozen
        super().__init__()

    def __copy__(self) -> Self:
        """Return a shallow copy of the object. Shallow copy is not allowed
        for frozen objects. Derived classes may override this method with an
        implementation that creates an unfrozen copy."""
        if self.is_frozen():
            raise TypeError(f"'{type(self).__name__}' object is frozen; cannot copy")
        return copy(self)

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        """Return a deep copy of the object. Deep copy is not allowed for frozen objects.
        Derived classes may override this method with an implementation that creates
        an unfrozen copy."""
        if self.is_frozen():
            raise TypeError(f"'{type(self).__name__}' object is frozen; cannot deepcopy")
        return deepcopy(self, memo)

    def __delattr__(self, name: str) -> None:
        """Delete an attribute. Raises AttributeError if the object is frozen."""
        # hasattr check ensures _frozen exists, useful during early __init__ of complex objects.
        if hasattr(self, "_frozen") and self._frozen:
            raise AttributeError(
                f"'{type(self).__name__}' object is frozen; cannot delete attribute '{name}'"
            )
        super().__delattr__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set an attribute. Raises AttributeError if frozen, unless setting '_frozen' itself."""
        # Allow internal modification of _frozen (e.g., by freeze() or __init__).
        if name == "_frozen":
            object.__setattr__(self, name, value)
            return

        if hasattr(self, "_frozen") and self._frozen:
            raise AttributeError(
                f"'{type(self).__name__}' object is frozen; cannot set attribute '{name}'"
            )
        object.__setattr__(self, name, value)

    @abstractmethod
    def __eq__(self, value: object) -> bool:
        """Derived classes must implement equality checking."""
        raise NotImplementedError(f"{type(self).__name__}.__eq__ must be overridden")

    @abstractmethod
    def __hash__(self) -> int:
        """Derived classes must implement hashing."""
        raise NotImplementedError(f"{type(self).__name__}.__hash__ must be overridden")

    def _get_all_data_slots(self) -> TypingSet[str]:
        """
        Helper to get all unique slot names from this class and its superclasses
        that are intended for member data. Excludes FreezableObject's own internal
        slots like `_frozen` and `__weakref__`.
        """
        all_slots: TypingSet[str] = set()
        for cls in type(self).__mro__:  # Iterate through Method Resolution Order
            if hasattr(cls, "__slots__"):
                slots_attr = cls.__slots__
                if isinstance(slots_attr, str):  # __slots__ can be a single string
                    all_slots.add(slots_attr)
                else:  # Or an iterable of strings
                    all_slots.update(slots_attr)

        # Exclude internal slots of the FreezableObject base class itself.
        all_slots.discard("_frozen")
        all_slots.discard("__weakref__")
        return all_slots

    @staticmethod
    def _is_value_recursively_immutable(value: Any, _visited_ids: TypingSet[int]) -> bool:
        """
        Static helper method to determine if an arbitrary value is recursively immutable.
        This method is called by `is_immutable` to check members.

        Args:
            value: The value to check.
            _visited_ids: Set of object IDs currently in the recursion stack.

        Returns:
            bool: True if the value is considered recursively immutable, False otherwise.
        """
        # If the value's ID is already in _visited_ids, it's part of a cycle.
        # Assume immutable for this path, similar to how `is_immutable` handles `self`.
        # This check is crucial for collections that might contain themselves or other
        # objects already higher up in the recursion stack.
        if id(value) in _visited_ids:
            # Exclude common interned immutables like None, True, False, small ints
            # which might share IDs frequently but don't form "problematic" cycles.
            # For complex objects or collections, this means a true cycle.
            if not isinstance(
                value, (type(None), bool, int)
            ):  # Add other simple interned types if needed
                return True

        if isinstance(value, FreezableObject):
            # Delegate to the FreezableObject's own is_immutable method.
            # This will correctly use and manage _visited_ids.
            return value.is_immutable(_visited_ids)

        # Check for immutable collections (tuple, frozenset)
        # Their elements must also be recursively immutable.
        if isinstance(value, (tuple, frozenset)):
            _visited_ids.add(id(value))  # Add this collection to visited stack before iterating
            try:
                for item in value:
                    if not FreezableObject._is_value_recursively_immutable(item, _visited_ids):
                        return False  # An element is mutable.
                return True  # All elements are immutable.
            finally:
                _visited_ids.remove(id(value))  # Remove from stack after checking elements.

        # Check against the tuple of known, simple immutable types.
        # (tuple and frozenset are handled above for element checking, but being in this
        # tuple ensures empty ones or those already checked pass here too).
        if isinstance(value, _KNOWN_IMMUTABLE_TYPES_TUPLE):
            return True

        # Check against the tuple of known mutable types.
        if isinstance(value, _KNOWN_MUTABLE_TYPES_TUPLE):
            return False  # Value is an instance of a known mutable type.

        # Default for unknown types:
        # For any other type of object not covered above (e.g., custom classes
        # not inheriting from FreezableObject, or other non-standard types),
        # assume it's mutable for safety. This is the most conservative approach.
        return False

    @staticmethod
    def _recursively_freeze_member_value(
        value: Any, store: bool, _fo_visited_in_freeze_call: TypingSet[int]
    ) -> None:
        """
        Static helper to recursively process a value for freezing.
        - If 'value' is a FreezableObject, its 'freeze' method is called.
        - If 'value' is a tuple or frozenset, its elements are recursively processed by this helper.
        Other types (lists, dicts, primitives, non-FreezableObject custom objects) are
        ignored by this helper.

        Args:
            value: The value to process.
            _fo_visited_in_freeze_call: A set of FreezableObject IDs that have already
                                       had their freeze process initiated during the
                                       current top-level freeze operation. This is passed
                                       to nested FreezableObject.freeze() calls.
        """
        if isinstance(value, FreezableObject):
            # If the value is a FreezableObject, call its freeze method.
            # The freeze method itself will use _fo_visited_in_freeze_call to handle cycles.
            # pylint: disable=protected-access
            value._freeze(store, _fo_visited_in_freeze_call)
        elif isinstance(value, (tuple, frozenset)):
            # If the value is a tuple or frozenset, iterate through its elements
            # and recursively call this helper for each element.
            # This does not add the tuple/frozenset ID to _fo_visited_in_freeze_call,
            # as that set is specifically for tracking FreezableObject instances.
            for item in value:
                FreezableObject._recursively_freeze_member_value(
                    item, store, _fo_visited_in_freeze_call)
        # Any other types of values are not processed further by this freezing logic.
        # For example, lists or dicts are not modified, nor are their contents inspected here.

    def consistency(self) -> bool:
        """
        Check the consistency of the object.

        This method checks if the object is frozen and if all its members are
        recursively immutable. It returns True if both conditions are met, False otherwise.
        """
        return (self.is_frozen() and self.is_immutable()) or not self.is_frozen()

    def freeze(self, store: bool = True) -> Self:
        """
        Freeze the object, making it immutable.

        This method is the entry point for freezing the object. It initializes the
        internal state and calls the recursive _freeze method to process all members.

        Args:
            store (bool): If True, the object is stored in the FreezableObject store.
                This is used to avoid duplicates. Default is True.

        Returns:
            Self: The frozen version of this object.
        """
        return self._freeze(store)

    def _freeze(self, store: bool = True,
               _fo_visited_in_freeze_call: TypingSet[int] | None = None) -> Self:
        """
        Freezes the object, making it immutable.
        This method recursively freezes:
        1. The object itself.
        2. Any direct members (in slots) that are FreezableObject instances.
        3. Any FreezableObject instances found as elements within tuple or frozenset members.

        It does NOT convert mutable collections (e.g., list to tuple).
        Subclass designers should ensure mutable collections are handled (e.g., converted
        to immutable counterparts and their FreezableObject elements frozen if necessary)
        appropriately *before* calling this base freeze() method if such collections are
        part of their state and need to contribute to the overall immutability as checked
        by `is_immutable()`.

        Args:
            store (bool): If True, the object is stored in the FreezableObject store.
                This is used to avoid duplicates. Default is True.
            _fo_visited_in_freeze_call (set[int], optional): Used internally to track
                FreezableObject IDs during a single top-level freeze operation to prevent
                infinite recursion in case of cyclic references. Callers should not
                provide this argument.
        Returns:
            Self: This method returns an immutable version of itself. Note that the object
            may not be the same object as self if store = True so the caller should execute
            _FreezableInstance = FreezableInstance.freeze()_ to ensure
            the object is frozen and immutable.
        """
        # Initialize the visited set for the top-level call.
        if _fo_visited_in_freeze_call is None:
            _fo_visited_in_freeze_call = set()

        # If this FreezableObject instance is already in the visited set for this
        # specific top-level freeze() call, it means we're in a cycle. Stop here for this path.
        if id(self) in _fo_visited_in_freeze_call:
            return self

        # If the object is already marked as frozen, its members should have been
        # handled during the call that originally froze it.
        # Add to visited set to prevent re-processing if encountered again via a
        # different path in the current (potentially ongoing) top-level freeze operation.
        if self.is_frozen():
            _fo_visited_in_freeze_call.add(id(self))
            return self

        # Mark this FreezableObject as visited for the current freeze operation *before*
        # processing members to handle cycles correctly.
        _fo_visited_in_freeze_call.add(id(self))

        # Recursively process members before freezing self
        for slot_name in self._get_all_data_slots():
            try:
                member_value = getattr(self, slot_name)
                # Delegate to the static helper to process the member's value
                FreezableObject._recursively_freeze_member_value(
                    member_value, store, _fo_visited_in_freeze_call
                )
            except AttributeError:
                # Slot defined but attribute not set on this instance. This is fine.
                pass

        # Finally, freeze this object itself by setting the internal _frozen flag.
        object.__setattr__(self, "_frozen", True)
        # The ID remains in _fo_visited_in_freeze_call for the duration of the top-level call
        # to signify it has been processed.

        # Return the object itself, or add it to the store if requested.
        return self.object_store.add(self) if store else self

    def is_frozen(self) -> bool:
        """Returns True if the object is marked as frozen, False otherwise."""
        return self._frozen

    def is_immutable(self, _visited_ids: TypingSet[int] | None = None) -> bool:
        """
        Recursively verifies if the object and all its members are effectively immutable
        according to the defined criteria.

        Args:
            _visited_ids (set[int], optional): Used internally to track object IDs
                currently in the recursion stack to detect cycles. Callers should
                not provide this argument directly.

        Returns:
            bool: True if the object and its contents are considered immutable, False otherwise.
        """
        # Initialize _visited_ids for the top-level call.
        # This set tracks objects currently being processed in the recursion stack.
        if _visited_ids is None:
            _visited_ids = set()

        # If this object's ID is already in _visited_ids, we've encountered a cycle.
        # Assume immutability for this path; the cycle's true immutability depends on
        # its non-cyclic parts.
        if id(self) in _visited_ids:
            return True

        _visited_ids.add(id(self))  # Mark this object as currently being visited.

        try:
            # Condition 1: Must be frozen.
            if not self.is_frozen():
                return False

            # Condition 2: Must not have a __dict__ (all members slotted).
            if hasattr(self, "__dict__"):
                return False  # Violates the "all members slotted" rule for immutability.

            # Condition 3: All data members in slots must be recursively immutable.
            for slot_name in self._get_all_data_slots():
                try:
                    member_value = getattr(self, slot_name)
                except AttributeError:
                    # If a slot is defined but the attribute isn't set on this instance,
                    # it doesn't contribute to mutability. So, continue.
                    continue

                # Recursively check the immutability of the member's value.
                if not FreezableObject._is_value_recursively_immutable(member_value, _visited_ids):
                    return False  # Found a mutable member.

            # If all checks pass, the object is considered immutable.
            return True
        finally:
            # Important: Remove from _visited_ids after checking this object and its children,
            # regardless of the outcome, to correctly handle non-cyclic shared objects.
            _visited_ids.remove(id(self))
