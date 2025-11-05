"""
Unit tests for the CGraphABC abstract base class.

This test module ensures that the abstract base class properly defines
the interface contract and that concrete implementations must provide
all required methods.
"""

import unittest
from abc import ABCMeta

from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph import CGraph
from egppy.genetic_code.c_graph_abc import CGraphABC


class IncompleteImplementation(CGraphABC):
    """Incomplete implementation for testing that abstract methods are enforced."""

    pass


class TestCGraphABC(unittest.TestCase):
    """Test cases for the CGraphABC abstract base class."""

    def test_cgraph_abc_is_abstract(self) -> None:
        """Test that CGraphABC cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            # pylint: disable=abstract-class-instantiated
            CGraphABC({})  # type: ignore

    def test_incomplete_implementation_raises_error(self) -> None:
        """Test that incomplete implementations cannot be instantiated."""
        with self.assertRaises(TypeError):
            # pylint: disable=abstract-class-instantiated
            IncompleteImplementation({})  # type: ignore

    def test_cgraph_implements_abc(self) -> None:
        """Test that CGraph properly implements the abstract base class."""
        # Create a simple empty graph with required interface
        from egppy.genetic_code.c_graph_constants import DstRow
        from egppy.genetic_code.interface import Interface

        graph = CGraph(
            {
                "Od": Interface([], row=DstRow.O),  # Empty output interface
            }
        )
        self.assertIsInstance(graph, CGraphABC)

    def test_abc_defines_required_methods(self) -> None:
        """Test that all required abstract methods are defined in the ABC."""
        abstract_methods = CGraphABC.__abstractmethods__

        expected_methods = {
            "__contains__",
            "__iter__",
            "__len__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "is_stable",
            "graph_type",
            "to_json",
            "connect_all",
            "stabilize",
            "copy",
            "__eq__",
            "__hash__",
            "__repr__",
        }

        self.assertEqual(abstract_methods, expected_methods)

    def test_cgraph_inherits_from_abc(self) -> None:
        """Test that CGraph properly inherits from CGraphABC."""
        self.assertTrue(issubclass(CGraph, CGraphABC))

    def test_abc_has_correct_metaclass(self) -> None:
        """Test that CGraphABC uses ABCMeta metaclass."""
        self.assertIsInstance(CGraphABC, ABCMeta)

    def test_concrete_implementation_methods_exist(self) -> None:
        """Test that CGraph implements all required abstract methods."""
        from egppy.genetic_code.c_graph_constants import DstRow
        from egppy.genetic_code.interface import Interface

        graph = CGraph(
            {
                "Od": Interface([], row=DstRow.O),  # Empty output interface
            }
        )

        # Test that all methods exist and are callable
        required_methods = [
            "__contains__",
            "__iter__",
            "__len__",
            "__getitem__",
            "__setitem__",
            "__delitem__",
            "is_stable",
            "graph_type",
            "to_json",
            "connect_all",
            "stabilize",
            "copy",
            "__eq__",
            "__hash__",
            "__repr__",
            "consistency",
            "verify",
        ]

        for method_name in required_methods:
            self.assertTrue(hasattr(graph, method_name), f"CGraph should have method {method_name}")
            self.assertTrue(
                callable(getattr(graph, method_name)),
                f"CGraph method {method_name} should be callable",
            )

    def test_abc_method_signatures(self) -> None:
        """Test that the abstract methods have correct signatures."""
        # Create a minimal valid graph with required interfaces
        from egppy.genetic_code.c_graph_constants import DstRow
        from egppy.genetic_code.interface import Interface

        # Create a simple empty graph
        graph = CGraph(
            {
                "Od": Interface([], row=DstRow.O),  # Empty output interface
            }
        )

        # Test method return types through actual calls
        self.assertIsInstance(graph.is_stable(), bool)
        self.assertIsInstance(graph.graph_type(), CGraphType)
        self.assertIsInstance(graph.to_json(), dict)
        self.assertIsInstance(graph.copy(), CGraphABC)
        self.assertIsInstance(len(graph), int)
        self.assertIsInstance(repr(graph), str)


if __name__ == "__main__":
    unittest.main()
