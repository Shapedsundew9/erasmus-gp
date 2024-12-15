"""Base class of interface tests."""

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.end_point.types_def import types_db
from egppy.gc_graph.interface.interface_class_factory import ListInterface, TupleInterface

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class InterfaceTestBase(unittest.TestCase):
    """Base class for interface tests.
    FIXME: Not done yet
    """

    # The interface type to test. Define in subclass.
    itype: type[TupleInterface] = TupleInterface

    @classmethod
    def get_test_cls(cls) -> type:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith("TestBase")

    @classmethod
    def get_interface_cls(cls) -> type:
        """Get the Interface class."""
        return cls.itype

    def setUp(self) -> None:
        self.interface_type = self.get_interface_cls()
        self.interface = self.interface_type([types_db["bool"].uid] * 4)

    def test_len(self) -> None:
        """Test the length of the interface."""
        if self.running_in_test_base_class():
            return
        self.assertEqual(len(self.interface), 4)

    def test_iter(self) -> None:
        """Test the iteration of the interface."""
        if self.running_in_test_base_class():
            return
        for idx, ept in enumerate(self.interface):
            self.assertEqual(ept, types_db["bool"].uid)
            self.assertEqual(self.interface[idx], types_db["bool"].uid)

    def test_consistency(self) -> None:
        """Test the consistency of the interface."""
        if self.running_in_test_base_class():
            return
        self.interface.consistency()

    def test_verify(self) -> None:
        """Test the verification of the interface."""
        if self.running_in_test_base_class():
            return
        self.interface.verify()

    def test_verify_assert1(self) -> None:
        """Test when the interface to too long."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            iface = self.interface_type([types_db["bool"].uid] * 257)
            iface.verify()

    def test_verify_assert2(self) -> None:
        """Test when the interface has an invalid type."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            iface = self.interface_type([types_db["egp_invalid"].uid] * 4)
            iface.verify()

    def test_find(self):
        """Test the find method of the interface."""
        if self.running_in_test_base_class():
            return
        idx = self.interface.find(types_db["bool"].uid)
        self.assertEqual(idx, [0, 1, 2, 3])
        iface = self.interface_type(
            [
                types_db["bool"].uid,
                types_db["int"].uid,
                types_db["str"].uid,
                types_db["float"].uid,
            ]
        )
        idx = iface.find(types_db["int"].uid)
        self.assertEqual(idx, [1])


class MutableInterfaceTestBase(InterfaceTestBase):
    """Extends the static interface test cases with dynamic interface tests."""

    itype: type = ListInterface

    def test_setitem(self) -> None:
        """Test setting an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type([types_db["bool"].uid] * 4)
        iface[0] = types_db["int"].uid
        self.assertEqual(iface[0], types_db["int"].uid)

    def test_delitem(self) -> None:
        """Test deleting an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type(
            [
                types_db["bool"].uid,
                types_db["int"].uid,
                types_db["str"].uid,
                types_db["float"].uid,
            ]
        )
        del iface[1]
        self.assertEqual(len(iface), 3)
        self.assertEqual(iface[1], types_db["str"].uid)

    def test_append(self) -> None:
        """Test appending an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type([types_db["bool"].uid] * 4)
        iface.append(types_db["int"].uid)
        self.assertEqual(len(iface), 5)
        self.assertEqual(iface[4], types_db["int"].uid)
