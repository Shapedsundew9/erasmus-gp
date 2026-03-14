"""Unit tests for egpcommon.common_obj and egpcommon.common_obj_abc.

Tests verify the CommonObj/CommonObjABC relationship and validate that
CommonObj is a concrete implementation of the CommonObjABC interface.
"""

from unittest import TestCase

from egpcommon.common_obj import CommonObj
from egpcommon.common_obj_abc import CommonObjABC


class TestCommonObjABCRelationship(TestCase):
    """Tests for the CommonObj and CommonObjABC relationship."""

    def test_common_obj_inherits_from_abc(self) -> None:
        """CommonObj is a subclass of CommonObjABC."""
        self.assertTrue(issubclass(CommonObj, CommonObjABC))

    def test_common_obj_instance_is_abc_instance(self) -> None:
        """CommonObj instances satisfy isinstance checks for CommonObjABC."""
        obj = CommonObj()
        self.assertIsInstance(obj, CommonObjABC)

    def test_common_obj_is_concrete(self) -> None:
        """CommonObj can be instantiated (it is not abstract)."""
        obj = CommonObj()
        self.assertIsNotNone(obj)

    def test_common_obj_abc_is_abstract(self) -> None:
        """CommonObjABC cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            CommonObjABC()  # type: ignore[abstract]

    def test_common_obj_abc_has_slots(self) -> None:
        """CommonObjABC defines __slots__ to maintain the slots chain."""
        self.assertTrue(hasattr(CommonObjABC, "__slots__"))
        self.assertEqual(CommonObjABC.__slots__, ())

    def test_consistency_and_verify_callable(self) -> None:
        """CommonObj provides concrete consistency() and verify() methods."""
        obj = CommonObj()
        # Both methods should be callable without raising
        obj.consistency()
        obj.verify()
