"""This module dynamically creates a hierarchy of parallel exceptions
to prevent cross-contamination between different parallel sets.
It allows for the creation of custom exception hierarchies with a specified prefix,
while ensuring that previously created hierarchies are ignored during discovery."""

import sys
import time
from collections import deque


def create_parallel_exceptions(prefix="Mutation", module_name=None, verbose=False):
    """
    Dynamically creates a parallel exception hierarchy with a configurable prefix.

    This version prevents cross-contamination between different parallel sets
    by "tagging" custom hierarchies and ignoring them during discovery.

    Args:
        prefix (str): The prefix for the parallel exception names (e.g., "Mutation").
        module_name (str, optional): The name for the new module.
                                     Defaults to f"{prefix.lower()}_exceptions".
        verbose (bool): If True, prints progress and timing information.

    Returns:
        A new module object containing the parallel exception hierarchy.
    """
    if module_name is None:
        module_name = f"{prefix.lower()}_exceptions"

    if module_name in sys.modules:
        if verbose:
            print(f"Module '{module_name}' already exists. Returning cached version.")
        return sys.modules[module_name]

    start_time = time.monotonic()

    # --- Phase 1: Discover all non-parallel exceptions ---
    # We gather a static list of all exceptions first, explicitly ignoring
    # any hierarchies we've created in previous calls.
    all_original_exceptions = []
    queue = deque([BaseException])
    visited = {BaseException}

    while queue:
        exc_class = queue.popleft()
        all_original_exceptions.append(exc_class)

        for subclass in exc_class.__subclasses__():
            # THE FIX: Skip any class that is part of a previously created parallel hierarchy.
            if subclass not in visited and not hasattr(subclass, "_is_parallel_hierarchy"):
                visited.add(subclass)
                queue.append(subclass)

    if verbose:
        print(f"Discovered {len(all_original_exceptions)} original exception classes to process.")

    # --- Phase 2: Create the parallel hierarchy ---
    new_module = type(sys)(module_name)
    sys.modules[module_name] = new_module

    base_exc_name = f"{prefix}Exception"

    class ParallelBaseException(Exception):
        # This "tag" is used to identify our custom hierarchies.
        _is_parallel_hierarchy = True

        """Base class for dynamically generated parallel exceptions."""

        def __init__(self, *args, original_exception=None, **kwargs):
            self.original_exception = original_exception
            self.metadata = kwargs.pop("metadata", {})
            super().__init__(*args)

    ParallelBaseException.__name__ = base_exc_name
    setattr(new_module, base_exc_name, ParallelBaseException)

    _exception_map = {}

    # This loop is now safe as it iterates over the clean, static list.
    for original_exc in all_original_exceptions:
        if not issubclass(original_exc, BaseException):
            continue

        base_classes = []
        for base in original_exc.__bases__:
            # Ignore non-exception base classes (like 'object')
            if issubclass(base, BaseException):
                parallel_base = _exception_map.get(base)
                if parallel_base:
                    base_classes.append(parallel_base)

        if not base_classes:
            base_classes.append(ParallelBaseException)

        new_exc_name = f"{prefix}{original_exc.__name__}"
        new_exc = type(new_exc_name, tuple(base_classes), {})
        setattr(new_module, new_exc_name, new_exc)
        _exception_map[original_exc] = new_exc

    def get_parallel_equivalent(original_exc_type):
        """Returns the parallel equivalent of a standard exception type."""
        return _exception_map.get(original_exc_type)

    setattr(new_module, "get_parallel_equivalent", get_parallel_equivalent)

    end_time = time.monotonic()
    if verbose:
        duration = end_time - start_time
        print(f"✅ Created module '{module_name}' in {duration:.4f} seconds.")

    return new_module


# --- Example Usage ---
if __name__ == "__main__":  # pragma: no cover
    print("--- First call ---")
    mutation_exceptions = create_parallel_exceptions(prefix="Mutation", verbose=True)

    print("\n--- Second call ---")
    validation_exceptions = create_parallel_exceptions(prefix="Validation", verbose=True)

    print("\n--- Demonstration ---")
    try:
        int("foo")
    except Exception as e:  # pylint: disable=broad-exception-caught
        mutation_exc_class = mutation_exceptions.get_parallel_equivalent(type(e))
        if mutation_exc_class:
            raise mutation_exc_class(
                f"Mutation failed: {e}", original_exception=e, metadata={"generation": 42}
            ) from e
        else:
            raise
    except mutation_exceptions.MutationValueError as mve:
        print("Caught a specific 'Mutation' context error:")
        print(f"  - {mve}")
        print(f"  - Metadata: {mve.metadata}")
