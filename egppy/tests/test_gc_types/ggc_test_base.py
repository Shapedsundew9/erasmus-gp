"""Tests for the GGC* class."""

from __future__ import annotations

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.ggc_class_factory import GGCDict, GGCMixin, GGCType

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class GGCTestBase(unittest.TestCase):
    """
    Test base class for GGC classes.

    """

    # The GGC class to test. Override this in subclasses.
    ugc_type: type[GGCType] = GGCDict

    @classmethod
    def get_test_cls(cls) -> type[unittest.TestCase]:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith("TestBase")

    @classmethod
    def get_cls(cls) -> type[GGCType]:
        """Get the GGC class."""
        return cls.ugc_type

    def setUp(self) -> None:
        self.type: type[GGCType] = self.get_cls()
        self.ggc: GGCType = self.type({})
        self.ggc1: GGCType = self.type({})
        self.ggc2: GGCType = self.type({})

    def test_set_item(self) -> None:
        """
        Test the set_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.assertEqual(first=self.ggc["key"], second="value")

    def test_get_item(self) -> None:
        """
        Test the get_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.assertEqual(first=self.ggc["key"], second="value")

    def test_del_item(self) -> None:
        """
        Test the del_item method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        del self.ggc["key"]
        self.assertNotIn(member="key", container=self.ggc)

    def test_contains(self) -> None:
        """
        Test the contains method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.assertIn(member="key", container=self.ggc)

    def test_len(self) -> None:
        """
        Test the len method.
        """
        if self.running_in_test_base_class():
            return
        self.assertEqual(first=len(self.ggc), second=len(GGCMixin.GC_KEY_TYPES))

    def test_iter(self) -> None:
        """
        Test the iter method.
        """
        if self.running_in_test_base_class():
            return
        keys = list(self.ggc)
        self.assertEqual(first=keys, second=list(GGCMixin.GC_KEY_TYPES.keys()))

    def test_clear(self) -> None:
        """
        Test the clear method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.ggc.clear()
        self.assertEqual(first=len(self.ggc), second=0)

    def test_dirty(self) -> None:
        """
        Test the dirty method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc.clean()
        self.ggc.dirty()
        self.assertTrue(expr=self.ggc.is_dirty())

    def test_is_dirty(self) -> None:
        """
        Test the is_dirty method.
        For a DirtyDict*GC object, is_dirty() should return True until clean() is called
        and updating the object *may* not update the dirty flag.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key1"] = "value1"
        self.assertTrue(expr=self.ggc.is_dirty())

    def test_clean(self) -> None:
        """
        Test the clean method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.assertTrue(expr=self.ggc.is_dirty())
        self.ggc.clean()
        self.assertFalse(expr=self.ggc.is_dirty())

    def test_pop(self) -> None:
        """
        Test the pop method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        value = self.ggc.pop("key")
        self.assertEqual(first=value, second="value")

    def test_popitem(self) -> None:
        """
        Test the popitem method.
        """
        if self.running_in_test_base_class():
            return
        key, _ = self.ggc.popitem()
        self.assertEqual(first=key, second=tuple(GGCMixin.GC_KEY_TYPES.keys())[-1])

    def test_keys(self) -> None:
        """
        Test the keys method.
        """
        if self.running_in_test_base_class():
            return
        keys = self.ggc.keys()
        self.assertEqual(first=list(keys), second=list(GGCMixin.GC_KEY_TYPES.keys()))

    def test_items(self) -> None:
        """
        Test the items method.
        """
        if self.running_in_test_base_class():
            return
        items = self.ggc.items()
        self.assertEqual(first=len(items), second=len(GGCMixin.GC_KEY_TYPES))
        # TBD

    def test_values(self) -> None:
        """
        Test the values method.
        """
        if self.running_in_test_base_class():
            return
        values = self.ggc.values()
        self.assertEqual(first=len(values), second=len(GGCMixin.GC_KEY_TYPES))
        # TBD

    def test_eq(self) -> None:
        """
        Test the __eq__ method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc1 = self.type({})
        self.ggc2 = self.type({})
        self.assertEqual(first=self.ggc1, second=self.ggc2)

    def test_ne(self) -> None:
        """
        Test the __ne__ method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc1 = self.type({})
        self.ggc2 = self.type({"signature": "1" * 64})
        self.assertNotEqual(first=self.ggc1, second=self.ggc2)

    def test_get(self) -> None:
        """
        Test the get method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        value = self.ggc.get("key", None)  # pylint: disable=assignment-from-no-return
        self.assertEqual(first=value, second="value")

    def test_setdefault(self) -> None:
        """
        Test the setdefault method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key"] = "value"
        self.ggc.clean()
        value = self.ggc.setdefault("key", "default")  # pylint: disable=assignment-from-no-return
        self.assertEqual(first=value, second="value")
        self.assertFalse(expr=self.ggc.is_dirty())

        value = self.ggc.setdefault(  # pylint: disable=assignment-from-no-return
            "new_key", "default"
        )
        self.assertEqual(first=value, second="default")
        self.assertTrue(expr=self.ggc.is_dirty())

    def test_update(self) -> None:
        """
        Test the update method.
        """
        if self.running_in_test_base_class():
            return
        self.ggc["key1"] = "value1"
        self.ggc.update({"key2": "value2", "key3": "value3"})
        self.assertEqual(first=self.ggc["key2"], second="value2")
        self.assertEqual(first=self.ggc["key3"], second="value3")
        self.assertTrue(expr=self.ggc.is_dirty())
