"""Unit tests for mutation primitives."""

import unittest
from unittest.mock import MagicMock
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.mutations.rewire import rewire
from egppy.physics.mutations.delete import delete
from egppy.physics.mutations.iterate import iterate
from egppy.physics.mutations.split import split
from egppy.physics.mutations.insert import insert, InsertionCase
from egppy.physics.mutations.create import create
from egppy.physics.mutations.wrap import wrap, WrapCase
from egppy.physics.mutations.crossover import crossover
from egppy.physics.mutations.dce import dce
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SrcRow, DstRow, EPCls
from egppy.physics.pgc_api import EGCode
from egppy.physics.helpers import empty_egc
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.c_graph import CGraph
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.endpoint import EndPoint
from egppy.genetic_code.types_def_store import types_def_store


class TestMutations(unittest.TestCase):
    """Test the mutation primitives."""

    def setUp(self):
        self.gpi = MagicMock()
        self.rtctxt = RuntimeContext(gpi=self.gpi)
        
        # Create a valid STANDARD graph structure
        # Add a bool input for split tests
        cgraph_dict = {
            SrcIfKey.IS: Interface([
                EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', []),
                EndPoint(SrcRow.I, 1, EPCls.SRC, 'bool', [])
            ], SrcRow.I),
            DstIfKey.AD: Interface([EndPoint(DstRow.A, 0, EPCls.DST, 'int', [])], DstRow.A),
            SrcIfKey.AS: Interface([EndPoint(SrcRow.A, 0, EPCls.SRC, 'int', [])], SrcRow.A),
            DstIfKey.BD: Interface([EndPoint(DstRow.B, 0, EPCls.DST, 'int', [])], DstRow.B),
            SrcIfKey.BS: Interface([EndPoint(SrcRow.B, 0, EPCls.SRC, 'int', [])], SrcRow.B),
            DstIfKey.OD: Interface([EndPoint(DstRow.O, 0, EPCls.DST, 'int', [])], DstRow.O),
        }
        
        self.egc = EGCode({
            "cgraph": CGraph(cgraph_dict),
            "properties": PropertiesBD({"gc_type": GCType.ORDINARY, "graph_type": CGraphType.STANDARD}),
            "pgc": None,
            "creator": None,
            "gca": "0" * 64,
            "gcb": "0" * 64,
            "ancestora": None,
            "ancestorb": None,
            "num_codes": 10,
        })

    def test_rewire_primitive(self):
        """Verify rewire returns a new object and connects endpoints (FR-010, FR-011)."""
        new_egc = rewire(self.rtctxt, self.egc, DstIfKey.AD, 0, SrcIfKey.IS, 0)
        
        self.assertIsNot(self.egc, new_egc)
        self.assertTrue(new_egc["cgraph"][DstIfKey.AD][0].is_connected())
        ref = new_egc["cgraph"][DstIfKey.AD][0].refs[0]
        self.assertEqual(ref.row, SrcRow.I)
        self.assertEqual(ref.idx, 0)

    def test_delete_primitive(self):
        """Test delete mutation primitive."""
        new_egc = delete(self.rtctxt, self.egc, a=True)
        self.assertIsNone(new_egc["gca"])
        self.assertIsNotNone(self.egc["gca"])
        
        new_egc_b = delete(self.rtctxt, self.egc, b=True)
        self.assertIsNone(new_egc_b["gcb"])
        self.assertIsNotNone(self.egc["gcb"])

    def test_iterate_primitive(self):
        """Test iterate mutation primitive."""
        new_egc = iterate(self.rtctxt, self.egc, CGraphType.FOR_LOOP)
        self.assertEqual(PropertiesBD(new_egc["properties"])["graph_type"], CGraphType.FOR_LOOP)

    def test_split_primitive(self):
        """Test split mutation primitive."""
        # Let's make the first one bool for this test
        self.egc["cgraph"][SrcIfKey.IS][0].typ = types_def_store['bool']
        
        new_egc = split(self.rtctxt, self.egc, SrcIfKey.IS)
        self.assertEqual(PropertiesBD(new_egc["properties"])["graph_type"], CGraphType.IF_THEN_ELSE)
        self.assertIn(DstIfKey.FD, new_egc["cgraph"])
        self.assertTrue(new_egc["cgraph"][DstIfKey.FD][0].is_connected())

    def test_create_primitive(self):
        """Test create mutation primitive."""
        empty = empty_egc(self.rtctxt, self.egc["cgraph"][SrcIfKey.IS], self.egc["cgraph"][DstIfKey.OD])
        empty["gca"] = "0" * 64
        empty["gcb"] = "0" * 64
        
        empty["cgraph"][DstIfKey.AD] = Interface([EndPoint(DstRow.A, 0, EPCls.DST, 'int', [])], DstRow.A)
        empty["cgraph"][SrcIfKey.AS] = Interface([EndPoint(SrcRow.A, 0, EPCls.SRC, 'int', [])], SrcRow.A)
        empty["cgraph"][DstIfKey.BD] = Interface([EndPoint(DstRow.B, 0, EPCls.DST, 'int', [])], DstRow.B)
        empty["cgraph"][SrcIfKey.BS] = Interface([EndPoint(SrcRow.B, 0, EPCls.SRC, 'int', [])], SrcRow.B)
        
        props = PropertiesBD(empty["properties"])
        props["graph_type"] = CGraphType.EMPTY
        empty["properties"] = props.to_int()

        new_egc = create(self.rtctxt, empty)
        self.assertIsNot(empty, new_egc)
        self.assertTrue(new_egc["cgraph"][DstIfKey.AD][0].is_connected())

    def test_wrap_primitive(self):
        """Test wrap mutation primitive."""
        new_egc = wrap(self.rtctxt, self.egc, self.egc, WrapCase.STACK)
        self.assertIsNotNone(new_egc)

    def test_insert_primitive(self):
        """Test insert mutation primitive."""
        new_egc = insert(self.rtctxt, self.egc, self.egc, InsertionCase.ABOVE_A)
        self.assertIsNotNone(new_egc)

    def test_crossover_primitive(self):
        """Test crossover mutation primitive."""
        new_egc = crossover(self.rtctxt, self.egc, self.egc, a=True)
        self.assertIsNot(self.egc, new_egc)

    def test_dce_primitive(self):
        """Test DCE mutation primitive."""
        # Setup: Is -> Ad, As -> Od. This makes GCA reachable.
        # GCB is NOT connected to anything that reaches Od.
        self.egc["cgraph"].connect(SrcRow.I, 0, DstRow.A, 0)
        self.egc["cgraph"].connect(SrcRow.A, 0, DstRow.O, 0)
        # GCB (Bd, Bs) remains unconnected
        
        new_egc = dce(self.rtctxt, self.egc)
        self.assertIsNot(self.egc, new_egc)
        self.assertIsNotNone(new_egc["gca"])
        self.assertIsNone(new_egc["gcb"])
        self.assertNotIn(DstIfKey.BD, new_egc["cgraph"])
        self.assertNotIn(SrcIfKey.BS, new_egc["cgraph"])

    def test_graph_size_limit(self):
        """Verify graph size limit enforcement (FR-008)."""
        from egppy.physics.mutations.common import MAX_GRAPH_SIZE
        self.egc["num_codes"] = MAX_GRAPH_SIZE + 1
        
        with self.assertRaises(RuntimeError) as cm:
            rewire(self.rtctxt, self.egc, DstIfKey.AD, 0, SrcIfKey.IS, 0)
        self.assertIn("Graph size limit exceeded", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
