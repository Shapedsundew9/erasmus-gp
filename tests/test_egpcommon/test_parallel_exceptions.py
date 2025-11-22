"""Unit tests for the create_parallel_exceptions factory function."""

import sys
import unittest
from io import StringIO
from unittest.mock import patch

# Assuming the function is in a file named parallel_exceptions.py
from egpcommon.parallel_exceptions import create_parallel_exceptions


class TestParallelExceptions(unittest.TestCase):
    """
    Comprehensive unit tests for the create_parallel_exceptions factory function.
    """

    def setUp(self):
        """
        Clean up sys.modules before each test to ensure isolation.
        This prevents caching from affecting test outcomes.
        """
        # List of modules created by our tests
        self.modules_to_delete = [
            "mutation_exceptions",
            "validation_exceptions",
            "custom_module_name",
        ]
        for mod_name in self.modules_to_delete:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

    def test_basic_creation_and_structure(self):
        """
        Tests if the basic hierarchy is created correctly with default names.
        """
        mod = create_parallel_exceptions(prefix="Mutation")

        # Test module creation
        self.assertIn("mutation_exceptions", sys.modules)
        self.assertEqual(mod.__name__, "mutation_exceptions")

        # Test existence of key exception classes
        self.assertTrue(hasattr(mod, "MutationException"))
        self.assertTrue(hasattr(mod, "MutationValueError"))
        self.assertTrue(hasattr(mod, "MutationKeyError"))

        # Test the custom base exception
        self.assertTrue(issubclass(mod.MutationException, Exception))
        # pylint: disable=protected-access
        self.assertTrue(mod.MutationException._is_parallel_hierarchy)

    def test_inheritance_chain(self):
        """
        Verifies that the created exceptions have the correct inheritance hierarchy.
        """
        mod = create_parallel_exceptions(prefix="Mutation")

        # CORRECTED: ZeroDivisionError is a subclass of ArithmeticError.
        # This correctly tests that our parallel hierarchy mirrors the real one.
        self.assertTrue(issubclass(mod.MutationZeroDivisionError, mod.MutationArithmeticError))

        # And the entire chain should lead back to our custom base exception
        self.assertTrue(issubclass(mod.MutationZeroDivisionError, mod.MutationException))

        # And ultimately to Python's base Exception
        self.assertTrue(issubclass(mod.MutationZeroDivisionError, Exception))

    def test_get_parallel_equivalent(self):
        """
        Tests the get_parallel_equivalent helper function.
        """
        mod = create_parallel_exceptions(prefix="Mutation")

        # Test with a standard exception
        self.assertIs(mod.get_parallel_equivalent(ValueError), mod.MutationValueError)
        self.assertIs(mod.get_parallel_equivalent(KeyError), mod.MutationKeyError)

        # Test with a non-exception type
        self.assertIsNone(mod.get_parallel_equivalent(int))

        # Test with an exception that has no direct parallel (should not happen with full traversal)
        class MyCustomError(Exception):
            """A custom error for testing purposes."""

        self.assertIsNone(mod.get_parallel_equivalent(MyCustomError))

    def test_exception_instantiation_and_usage(self):
        """
        Tests raising, catching, and inspecting an instance of a parallel exception.
        """
        mod = create_parallel_exceptions(prefix="Mutation")
        original_error = ValueError("Original error message")
        metadata = {"gen": 1, "fitness": 0.5}

        try:
            raise mod.MutationValueError(
                "Parallel error", original_exception=original_error, metadata=metadata
            )
        except mod.MutationValueError as e:
            self.assertEqual(str(e), "Parallel error")
            self.assertIs(e.original_exception, original_error)
            self.assertEqual(e.metadata, metadata)
            self.assertTrue(isinstance(e, mod.MutationException))

    def test_isolation_between_hierarchies(self):
        """
        Crucial test: Ensures creating a second hierarchy does not affect or copy the first.
        """
        # Create the first set
        mod1 = create_parallel_exceptions(prefix="Mutation")

        # Check its contents
        self.assertTrue(hasattr(mod1, "MutationValueError"))
        self.assertFalse(hasattr(mod1, "ValidationValueError"))

        # Create the second set
        mod2 = create_parallel_exceptions(prefix="Validation")

        # Check its contents
        self.assertTrue(hasattr(mod2, "ValidationValueError"))
        self.assertFalse(hasattr(mod2, "MutationValueError"))

        # Ensure the classes are distinct types
        self.assertNotEqual(mod1.MutationException, mod2.ValidationException)

    def test_caching_behavior(self):
        """
        Tests that a second call with the same prefix returns the cached module.
        """
        mod1 = create_parallel_exceptions(prefix="Mutation")
        mod2 = create_parallel_exceptions(prefix="Mutation")
        self.assertIs(
            mod1, mod2, "Function should return the same module object on subsequent calls"
        )

    def test_custom_module_name(self):
        """
        Tests the ability to provide a custom module name.
        """
        mod = create_parallel_exceptions(prefix="Mutation", module_name="custom_module_name")
        self.assertIn("custom_module_name", sys.modules)
        self.assertEqual(mod.__name__, "custom_module_name")

    def test_verbose_output(self):
        """
        Tests that the verbose flag produces output.
        """
        # Redirect stdout to capture the print statements from the function
        with patch("sys.stdout", new=StringIO()) as fake_out:
            create_parallel_exceptions(prefix="TestVerbose", verbose=True)
            output = fake_out.getvalue().strip()

            # Check for expected output patterns
            self.assertIn("Discovered", output)
            self.assertIn("original exception classes", output)
            self.assertIn("Created module", output)
            self.assertIn("seconds", output)

    def test_exception_conversion_and_catching(self):
        """
        Tests the full workflow of catching a standard exception,
        converting it to a parallel exception, and catching the parallel exception.
        This test ensures the example usage pattern works correctly.
        """
        mod = create_parallel_exceptions(prefix="Mutation")

        # Track that the exception was caught
        caught = False
        metadata_value = None

        try:
            try:
                # Raise a standard Python exception
                int("foo")
            except Exception as e:  # pylint: disable=broad-exception-caught
                # Convert to parallel exception
                mutation_exc_class = mod.get_parallel_equivalent(type(e))
                if mutation_exc_class:
                    raise mutation_exc_class(
                        f"Mutation failed: {e}",
                        original_exception=e,
                        metadata={"generation": 42},
                    ) from e
                else:
                    raise
        except mod.MutationValueError as mve:
            # This except clause should catch the parallel exception
            caught = True
            metadata_value = mve.metadata.get("generation")
            self.assertIsInstance(mve, mod.MutationValueError)
            self.assertIsInstance(mve, mod.MutationException)
            self.assertIsNotNone(mve.original_exception)
            self.assertIsInstance(mve.original_exception, ValueError)

        # Ensure the exception was actually caught
        self.assertTrue(caught, "The parallel exception should have been caught")
        self.assertEqual(metadata_value, 42, "Metadata should be preserved")

    def test_exception_not_caught_by_wrong_hierarchy(self):
        """
        Tests that a parallel exception from one hierarchy is not caught
        by an except clause for a different hierarchy.
        """
        mutation_mod = create_parallel_exceptions(prefix="Mutation")
        validation_mod = create_parallel_exceptions(prefix="Validation")

        with self.assertRaises(mutation_mod.MutationValueError):
            try:
                try:
                    raise ValueError("test")
                except ValueError as e:
                    mutation_exc = mutation_mod.get_parallel_equivalent(ValueError)
                    raise mutation_exc("Mutation error", original_exception=e) from e
            except validation_mod.ValidationValueError:
                # This should NOT catch the MutationValueError
                self.fail("ValidationValueError should not catch MutationValueError")

    def test_base_exception_catches_all_parallel_exceptions(self):
        """
        Tests that the base parallel exception class catches all exceptions
        in its hierarchy.
        """
        mod = create_parallel_exceptions(prefix="Mutation")

        caught = False
        try:
            try:
                raise KeyError("test")
            except KeyError as e:
                mutation_exc = mod.get_parallel_equivalent(KeyError)
                raise mutation_exc("Mutation error", original_exception=e) from e
        except mod.MutationException:
            # The base class should catch all parallel exceptions
            caught = True

        self.assertTrue(caught, "Base parallel exception should catch all parallel exceptions")


if __name__ == "__main__":
    unittest.main()
