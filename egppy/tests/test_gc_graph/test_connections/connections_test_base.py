"""Base class of connections tests."""
import unittest
from egppy.gc_graph.connections.connections_class_factory import ListConnections, TupleConnections
from egppy.gc_graph.end_point.end_point import SrcEndPointRef, DstEndPointRef
from egppy.gc_graph.egp_typing import DestinationRow, SourceRow
from egppy.common.egp_log import egp_logger, DEBUG, VERIFY, CONSISTENCY, Logger


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
    ctype: type= TupleConnections

    @classmethod
    def get_test_cls(cls) -> type:
        """Get the TestCase class."""
        return cls

    @classmethod
    def running_in_test_base_class(cls) -> bool:
        """Pass the test if the Test class class is the Test Base class."""
        # Alternative is to skip:
        # raise unittest.SkipTest('Base class test not run')
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_connections_cls(cls) -> type:
        """Get the Connections class."""
        return cls.ctype

    def setUp(self) -> None:
        self.connections_type = self.get_connections_cls()
        self.connections = self.connections_type([[
            SrcEndPointRef(DestinationRow.A, i)] for i in range(4)])

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
            self.assertEqual(ept, [SrcEndPointRef(DestinationRow.A, idx)])
            self.assertEqual(self.connections[idx], [SrcEndPointRef(DestinationRow.A, idx)])

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
            conns = TupleConnections([[SrcEndPointRef(DestinationRow.O, 0),
                                       DstEndPointRef(SourceRow.I, 0)] * 4])
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
            conns = self.connections_type([[
                SrcEndPointRef(DestinationRow.A, 0)] for _ in range(257)])
            conns.verify()


class MutableConnectionsTestBase(ConnectionsTestBase):
    """Extends the static connections test cases with dynamic connections tests."""
    ctype: type = ListConnections

    def test_setitem(self) -> None:
        """Test setting an item in the connections."""
        if self.running_in_test_base_class():
            return
        self.connections[0] = [SrcEndPointRef(DestinationRow.O, 0)]
        self.assertEqual(self.connections[0], [SrcEndPointRef(DestinationRow.O, 0)])

    def test_delitem(self) -> None:
        """Test deleting an item in the connections."""
        if self.running_in_test_base_class():
            return
        del self.connections[0]
        self.assertEqual(len(self.connections), 3)
        self.assertEqual(self.connections[0], [SrcEndPointRef(DestinationRow.A, 1)])
        self.assertEqual(self.connections[1], [SrcEndPointRef(DestinationRow.A, 2)])
        self.assertEqual(self.connections[2], [SrcEndPointRef(DestinationRow.A, 3)])
        with self.assertRaises(IndexError):
            _ = self.connections[3]
        with self.assertRaises(IndexError):
            del self.connections[3]

    def test_append(self) -> None:
        """Test appending an item in the connections."""
        if self.running_in_test_base_class():
            return
        self.connections.append([SrcEndPointRef(DestinationRow.O, 0)])
        self.assertEqual(len(self.connections), 5)
        self.assertEqual(self.connections[4], [SrcEndPointRef(DestinationRow.O, 0)])
