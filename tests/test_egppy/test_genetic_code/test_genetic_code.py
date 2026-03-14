"""Unit tests for GCABC protocol conformance.

Tests verify that GCABC inherits from MutableMapping and that
the mapping protocol methods (get, setdefault, keys, values, items)
are provided by the MutableMapping mixin rather than declared as abstract.
"""

from collections.abc import MutableMapping
from unittest import TestCase

from egppy.genetic_code.egc_dict import EGCDict
from egppy.genetic_code.genetic_code import GCABC


class TestGCABCProtocolConformance(TestCase):
    """Tests for GCABC MutableMapping protocol conformance."""

    def test_gcabc_inherits_from_mutable_mapping(self) -> None:
        """GCABC is a subclass of MutableMapping."""
        self.assertTrue(issubclass(GCABC, MutableMapping))

    def test_concrete_gc_is_mutable_mapping_instance(self) -> None:
        """Concrete GC instances satisfy isinstance for MutableMapping."""
        gc = EGCDict()
        self.assertIsInstance(gc, MutableMapping)

    def test_mixin_methods_not_abstract(self) -> None:
        """get and setdefault are provided by MutableMapping, not abstract on GCABC."""
        mixin_methods = {"get", "setdefault", "keys", "values", "items", "pop",
                         "popitem", "clear", "update", "__contains__", "__eq__"}
        for method_name in mixin_methods:
            self.assertNotIn(
                method_name,
                GCABC.__abstractmethods__,
                f"{method_name} should not be abstract (provided by MutableMapping)",
            )

    def test_required_abstract_methods_still_present(self) -> None:
        """The five required MutableMapping methods remain abstract on GCABC."""
        required = {"__getitem__", "__setitem__", "__delitem__", "__iter__", "__len__"}
        for method_name in required:
            self.assertIn(
                method_name,
                GCABC.__abstractmethods__,
                f"{method_name} should be abstract (required by MutableMapping)",
            )

    def test_concrete_gc_get_method(self) -> None:
        """Concrete GC instances have a working get() method."""
        gc = EGCDict()
        # get() with default returns None for missing keys
        result = gc.get("nonexistent_key", "default_val")
        self.assertEqual(result, "default_val")
