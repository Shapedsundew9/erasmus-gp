"""Unit tests for the json_cgraph_to_interfaces helper function.

This module tests the new helper function that extracts JSONCGraph conversion logic
from the CGraph.__init__ method into a standalone, reusable function.
"""

import unittest

from egpcommon.properties import CGraphType
from egppy.genetic_code.c_graph import CGraph, c_graph_type, json_cgraph_to_interfaces
from egppy.genetic_code.c_graph_constants import DstRow, EndPointClass, SrcRow
from egppy.genetic_code.end_point import EndPoint
from egppy.genetic_code.interface import Interface


class TestJsonCGraphToInterfaces(unittest.TestCase):
    """Test the json_cgraph_to_interfaces helper function."""

    def test_primitive_json_cgraph_conversion(self) -> None:
        """Test conversion of a primitive JSONCGraph to interfaces."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(jcg)

        # Check that we get the expected interface keys
        self.assertIn("Ad", interfaces)
        self.assertIn("Od", interfaces)
        self.assertIn("Is", interfaces)
        self.assertIn("As", interfaces)

        # Check destination interfaces
        ad_interface = interfaces["Ad"]
        self.assertIsInstance(ad_interface, Interface)
        self.assertEqual(len(ad_interface), 1)
        self.assertEqual(ad_interface[0].typ.name, "int")
        self.assertEqual(ad_interface[0].refs, [["I", 0]])

        od_interface = interfaces["Od"]
        self.assertIsInstance(od_interface, Interface)
        self.assertEqual(len(od_interface), 1)
        self.assertEqual(od_interface[0].typ.name, "int")
        self.assertEqual(od_interface[0].refs, [["A", 0]])

        # Check source interfaces
        is_interface = interfaces["Is"]
        self.assertIsInstance(is_interface, Interface)
        self.assertEqual(len(is_interface), 1)
        self.assertEqual(is_interface[0].typ.name, "int")
        self.assertEqual(is_interface[0].refs, [["A", 0]])

        as_interface = interfaces["As"]
        self.assertIsInstance(as_interface, Interface)
        self.assertEqual(len(as_interface), 1)
        self.assertEqual(as_interface[0].typ.name, "int")
        self.assertEqual(as_interface[0].refs, [["O", 0]])

    def test_if_then_json_cgraph_conversion(self) -> None:
        """Test conversion of an if-then JSONCGraph to interfaces."""
        jcg = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(jcg)

        # Verify we get all expected interfaces
        self.assertIn("Fd", interfaces)
        self.assertIn("Ad", interfaces)
        self.assertIn("Od", interfaces)
        self.assertIn("Pd", interfaces)
        self.assertIn("Is", interfaces)
        self.assertIn("As", interfaces)

        # Check F interface
        fd_interface = interfaces["Fd"]
        self.assertEqual(len(fd_interface), 1)
        self.assertEqual(fd_interface[0].typ.name, "bool")
        self.assertEqual(fd_interface[0].refs, [["I", 0]])

        # Check source interface has correct endpoints
        is_interface = interfaces["Is"]
        self.assertEqual(len(is_interface), 2)  # I0 and I1
        self.assertEqual(is_interface[0].idx, 0)
        self.assertEqual(is_interface[0].typ.name, "bool")
        self.assertEqual(is_interface[1].idx, 1)
        self.assertEqual(is_interface[1].typ.name, "int")

    def test_standard_json_cgraph_conversion(self) -> None:
        """Test conversion of a standard JSONCGraph to interfaces."""
        jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["A", 0, "int"]],
            DstRow.O: [["B", 0, "int"]],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(jcg)

        # Check interface creation
        self.assertIn("Ad", interfaces)
        self.assertIn("Bd", interfaces)
        self.assertIn("Od", interfaces)
        self.assertIn("Is", interfaces)
        self.assertIn("As", interfaces)
        self.assertIn("Bs", interfaces)

        # Verify connection chain
        od_interface = interfaces["Od"]
        self.assertEqual(od_interface[0].refs, [["B", 0]])

        bd_interface = interfaces["Bd"]
        self.assertEqual(bd_interface[0].refs, [["A", 0]])

        ad_interface = interfaces["Ad"]
        self.assertEqual(ad_interface[0].refs, [["I", 0]])

    def test_empty_json_cgraph_conversion(self) -> None:
        """Test conversion of an empty JSONCGraph to interfaces."""
        jcg = {
            DstRow.O: [],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(jcg)

        # Check that only Od interface is created (empty)
        self.assertIn("Od", interfaces)

        od_interface = interfaces["Od"]
        self.assertEqual(len(od_interface), 0)

        # No source interfaces should be created for empty graph
        self.assertEqual(len([k for k in interfaces.keys() if k.endswith("s")]), 0)

    def test_complex_json_cgraph_conversion(self) -> None:
        """Test conversion of a complex JSONCGraph with multiple endpoint types."""
        jcg = {
            DstRow.A: [["I", 0, "int"], ["I", 1, "str"], ["I", 2, "bool"]],
            DstRow.B: [["A", 0, "int"], ["A", 2, "bool"]],
            DstRow.O: [["B", 0, "int"], ["A", 1, "str"], ["B", 1, "bool"]],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(jcg)

        # Check that source interface I has 3 endpoints
        is_interface = interfaces["Is"]
        self.assertEqual(len(is_interface), 3)

        # Check endpoint types
        types = [ep.typ.name for ep in is_interface.endpoints]
        self.assertEqual(types, ["int", "str", "bool"])

        # Check that A source interface has correct endpoints
        as_interface = interfaces["As"]
        self.assertEqual(len(as_interface), 3)

        # Verify all connections are properly established
        cgraph = CGraph(interfaces)
        self.assertTrue(cgraph.is_stable())

    def test_invalid_json_cgraph_raises_error(self) -> None:
        """Test that invalid JSONCGraph structures raise appropriate errors."""
        # Invalid destination row
        invalid_jcg = {
            "Z": [["I", 0, "int"]],  # Z is not a valid destination row
            DstRow.O: [],
            DstRow.U: [],
        }

        with self.assertRaises(ValueError):
            json_cgraph_to_interfaces(invalid_jcg)

        # Invalid source row in reference
        invalid_jcg2 = {
            DstRow.A: [["X", 0, "int"]],  # X is not a valid source row
            DstRow.O: [],
            DstRow.U: [],
        }

        with self.assertRaises(ValueError):
            json_cgraph_to_interfaces(invalid_jcg2)

    def test_type_consistency_validation(self) -> None:
        """Test that type consistency is enforced across connections."""
        # This should work - same types
        valid_jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["I", 0, "int"]],  # Same source endpoint, same type
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }

        interfaces = json_cgraph_to_interfaces(valid_jcg)
        self.assertIsInstance(interfaces, dict)

        # This should fail - different types for same source endpoint "I",0
        invalid_jcg = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.B: [["I", 0, "str"]],  # Same source endpoint as A, different type
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }

        with self.assertRaises(ValueError):
            json_cgraph_to_interfaces(invalid_jcg)


class TestNewUsagePattern(unittest.TestCase):
    """Demonstrate the new usage pattern for JSONCGraph conversion."""

    def test_recommended_usage_pattern(self) -> None:
        """Demonstrate the recommended way to use the helper function."""
        # Define a JSONCGraph structure
        json_graph = {
            DstRow.F: [["I", 0, "bool"]],
            DstRow.A: [["I", 1, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.P: [["I", 1, "int"]],
            DstRow.U: [],
        }

        # NEW PATTERN: Use helper function first, then create CGraph
        interfaces = json_cgraph_to_interfaces(json_graph)
        cgraph = CGraph(interfaces)

        # Verify it works correctly
        self.assertEqual(c_graph_type(cgraph), CGraphType.IF_THEN)
        self.assertTrue(cgraph.is_stable())

    def test_reusable_interfaces(self) -> None:
        """Demonstrate that interfaces can be reused and modified."""
        json_graph = {
            DstRow.A: [["I", 0, "int"]],
            DstRow.O: [["A", 0, "int"]],
            DstRow.U: [],
        }

        # Convert to interfaces
        interfaces = json_cgraph_to_interfaces(json_graph)

        # Create multiple CGraph instances from the same interfaces
        cgraph1 = CGraph(interfaces.copy())
        cgraph2 = CGraph(interfaces.copy())

        self.assertEqual(cgraph1, cgraph2)

        # Interfaces can be modified before creating CGraph
        modified_interfaces = interfaces.copy()
        # Add a new endpoint to the input interface
        is_interface = modified_interfaces["Is"]
        if hasattr(is_interface, "endpoints") and isinstance(is_interface.endpoints, list):
            new_endpoint = EndPoint(SrcRow.I, 1, EndPointClass.SRC, "str", [])
            is_interface.endpoints.append(new_endpoint)

        # Create CGraph with modified interfaces
        cgraph_modified = CGraph(modified_interfaces)

        # Should have additional input endpoint
        self.assertEqual(len(cgraph_modified["Is"]), 2)


if __name__ == "__main__":
    unittest.main()
