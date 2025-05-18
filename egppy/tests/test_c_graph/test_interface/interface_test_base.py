"""Base class of interface tests."""

import unittest
from typing import Callable

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.end_point.types_def.types_def import ept_db
from egppy.c_graph.interface import interface, mutable_interface

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
    itype: Callable = interface

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
    def get_interface_cls(cls) -> Callable:
        """Get the Interface class."""
        return cls.itype

    def setUp(self) -> None:
        self.interface_type = self.get_interface_cls()
        self.interface = self.interface_type([ept_db["bool"].uid] * 4)

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
            self.assertEqual(ept[0], ept_db["bool"])
            self.assertEqual(self.interface[idx][0], ept_db["bool"])

    def test_verify_assert1(self) -> None:
        """Test when the interface to too long."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            _ = self.interface_type([ept_db["bool"].uid] * 257)


class MutableInterfaceTestBase(InterfaceTestBase):
    """Extends the static interface test cases with dynamic interface tests."""

    itype: Callable = mutable_interface

    def test_setitem(self) -> None:
        """Test setting an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type([ept_db["bool"].uid] * 4)
        iface[0] = ept_db["int"].uid
        self.assertEqual(iface[0], ept_db["int"].uid)

    def test_delitem(self) -> None:
        """Test deleting an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type(
            [
                ept_db["bool"].uid,
                ept_db["int"].uid,
                ept_db["str"].uid,
                ept_db["float"].uid,
            ]
        )
        del iface[1]
        self.assertEqual(len(iface), 3)
        self.assertEqual(iface[1][0].uid, ept_db["str"].uid)

    def test_append(self) -> None:
        """Test appending an endpoint type."""
        if self.running_in_test_base_class():
            return
        iface = self.interface_type([ept_db["bool"].uid] * 4)
        iface.append((ept_db["int"],))
        self.assertEqual(len(iface), 5)
        self.assertEqual(iface[4][0].uid, ept_db["int"].uid)
