"""Base class of connections tests."""
import unittest
from egppy.gc_graph.connections.connections_class_factory import TupleConnections
from egppy.gc_graph.end_point.builtin_end_point import BuiltinSrcEndPointRef, BuiltinDstEndPointRef
from egppy.gc_graph.egp_typing import DestinationRow, SourceRow


class ConnectionsTestBase(unittest.TestCase):
    """Base class for connections tests.
    FIXME: Not done yet
    """

    # The connections type to test. Define in subclass.
    ctype: type[TupleConnections] = TupleConnections

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
            BuiltinSrcEndPointRef(DestinationRow.A, i)] for i in range(4)])

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
            self.assertEqual(ept, [BuiltinSrcEndPointRef(DestinationRow.A, idx)])
            self.assertEqual(self.connections[idx], [BuiltinSrcEndPointRef(DestinationRow.A, idx)])

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
            conns = TupleConnections([[BuiltinSrcEndPointRef(DestinationRow.O, 0),
                                       BuiltinDstEndPointRef(SourceRow.I, 0)] * 4])
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
                BuiltinSrcEndPointRef(DestinationRow.A, 0)] for _ in range(257)])
            conns.verify()

if __name__ == '__main__':
    unittest.main()
