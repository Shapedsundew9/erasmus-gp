"""Base class of connections tests."""

import unittest

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.c_graph.connections.connections_class_factory import (
    NULL_CONNECTIONS,
    ListConnections,
    TupleConnections,
)
from egppy.c_graph.end_point.end_point import DstEndPointRef, SrcEndPointRef
from egppy.c_graph.c_graph_constants import DstRow, SrcRow

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


class ConnectionsTestBase(unittest.TestCase):
    """Base class for connections tests.
    FIXME: Not done yet
    """

    # The connections type to test. Define in subclass.
    ctype: type = TupleConnections

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
    def get_connections_cls(cls) -> type:
        """Get the Connections class."""
        return cls.ctype

    def setUp(self) -> None:
        self.connections_type = self.get_connections_cls()
        self.connections = self.connections_type([[SrcEndPointRef(DstRow.A, i)] for i in range(4)])

    def test_len(self) -> None:
        """Test the length of the connections."""
        if self.running_in_test_base_class():
            return
        self.assertEqual(len(self.connections), 4)

    def test_iter(self) -> None:
        """Test the iteration of the connections."""
        if self.running_in_test_base_class():
            return
        for idx, ept in enumerate(self.connections):
            self.assertEqual(ept, [SrcEndPointRef(DstRow.A, idx)])
            self.assertEqual(self.connections[idx], [SrcEndPointRef(DstRow.A, idx)])

    def test_consistency(self) -> None:
        """Test the consistency of the connections."""
        if self.running_in_test_base_class():
            return
        self.connections.consistency()

    def test_consistency_assert(self) -> None:
        """Test the consistency of the connections."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            conns = TupleConnections(
                [(SrcEndPointRef(DstRow.O, 0), DstEndPointRef(SrcRow.I, 0)) * 4]
            )
            conns.consistency()

    def test_verify(self) -> None:
        """Test the verification of the connections."""
        if self.running_in_test_base_class():
            return
        self.connections.verify()

    def test_verify_assert(self) -> None:
        """Test the verification of the connections."""
        if self.running_in_test_base_class():
            return
        with self.assertRaises(AssertionError):
            # It is legit for the constructor to assert this but not required.
            conns = self.connections_type([[SrcEndPointRef(DstRow.A, 0)] for _ in range(257)])
            conns.verify()

    def test_has_unconnected_eps(self):
        """Test has_unconnected_eps method."""
        if self.running_in_test_base_class():
            return
        self.assertFalse(self.connections.has_unconnected_eps())
        self.connections = self.connections_type([[]])
        self.assertTrue(self.connections.has_unconnected_eps())
        self.connections = NULL_CONNECTIONS
        self.assertFalse(self.connections.has_unconnected_eps())

    def test_get_unconnected_idx(self):
        """Test get_unconnected_idx method."""
        if self.running_in_test_base_class():
            return
        self.assertEqual(self.connections.get_unconnected_idx(), [])
        self.connections = self.connections_type([[]])
        self.assertEqual(self.connections.get_unconnected_idx(), [0])
        self.connections = NULL_CONNECTIONS
        self.assertEqual(self.connections.get_unconnected_idx(), [])


class MutableConnectionsTestBase(ConnectionsTestBase):
    """Extends the static connections test cases with dynamic connections tests."""

    ctype: type = ListConnections

    def test_setitem(self) -> None:
        """Test setting an item in the connections."""
        if self.running_in_test_base_class():
            return
        self.connections[0] = [SrcEndPointRef(DstRow.O, 0)]
        self.assertEqual(self.connections[0], [SrcEndPointRef(DstRow.O, 0)])

    def test_delitem(self) -> None:
        """Test deleting an item in the connections."""
        if self.running_in_test_base_class():
            return
        del self.connections[0]
        self.assertEqual(len(self.connections), 3)
        self.assertEqual(self.connections[0], [SrcEndPointRef(DstRow.A, 1)])
        self.assertEqual(self.connections[1], [SrcEndPointRef(DstRow.A, 2)])
        self.assertEqual(self.connections[2], [SrcEndPointRef(DstRow.A, 3)])
        with self.assertRaises(IndexError):
            _ = self.connections[3]
        with self.assertRaises(IndexError):
            del self.connections[3]

    def test_append(self) -> None:
        """Test appending an item in the connections."""
        if self.running_in_test_base_class():
            return
        self.connections.append([SrcEndPointRef(DstRow.O, 0)])
        self.assertEqual(len(self.connections), 5)
        self.assertEqual(self.connections[4], [SrcEndPointRef(DstRow.O, 0)])
