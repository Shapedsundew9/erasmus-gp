"""Integration tests for mutation sequences and stabilization."""

import unittest
from unittest.mock import MagicMock
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.pgc_api import EGCode
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SrcRow, DstRow, EPCls
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.c_graph import CGraph
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.endpoint import EndPoint
from egppy.physics.mutations.insert import insert, InsertionCase
from egppy.physics.mutations.rewire import rewire
from egppy.physics.stabilization import sfss


class TestIntegration(unittest.TestCase):
    """Test chained mutations and stabilization."""

    def setUp(self):
        self.gpi = MagicMock()
        self.rtctxt = RuntimeContext(gpi=self.gpi)
        
        # Base GC: standard I -> O
        cgraph_dict = {
            SrcIfKey.IS: Interface([EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', [])], SrcRow.I),
            DstIfKey.AD: Interface([EndPoint(DstRow.A, 0, EPCls.DST, 'int', [])], DstRow.A),
            SrcIfKey.AS: Interface([EndPoint(SrcRow.A, 0, EPCls.SRC, 'int', [])], SrcRow.A),
            DstIfKey.BD: Interface([EndPoint(DstRow.B, 0, EPCls.DST, 'int', [])], DstRow.B),
            SrcIfKey.BS: Interface([EndPoint(SrcRow.B, 0, EPCls.SRC, 'int', [])], SrcRow.B),
            DstIfKey.OD: Interface([EndPoint(DstRow.O, 0, EPCls.DST, 'int', [])], DstRow.O),
        }
        
        self.egc = EGCode({
            "cgraph": CGraph(cgraph_dict),
            "properties": PropertiesBD({"gc_type": GCType.ORDINARY, "graph_type": CGraphType.STANDARD}),
            "gca": MagicMock(spec=EGCode),
            "gcb": MagicMock(spec=EGCode),
        })
        
        # Setup sub-GCs
        for key in ["gca", "gcb"]:
            self.egc[key]["cgraph"] = CGraph({
                SrcIfKey.IS: Interface([EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', [])], SrcRow.I),
                DstIfKey.OD: Interface([EndPoint(DstRow.O, 0, EPCls.DST, 'int', [])], DstRow.O),
                "properties": PropertiesBD({"gc_type": GCType.ORDINARY, "graph_type": CGraphType.STANDARD}),
            })
            self.egc[key]["properties"] = self.egc[key]["cgraph"]["properties"]
            self.gpi[self.egc[key]["signature"]] = self.egc[key]

    def test_mutation_chain_and_stabilization(self):
        """Verify that a sequence of mutations can be stabilized."""
        # 1. Start with unstable/unconnected graph
        self.assertFalse(self.egc["cgraph"].is_stable())
        
        # 2. Insert a new GC
        # (This will trigger insertion connection process)
        new_egc = insert(self.rtctxt, self.egc, self.egc, InsertionCase.ABOVE_A)
        
        # 3. Manually disconnect something to make it unstable if process stabilized it
        new_egc["cgraph"][DstIfKey.OD][0].clr_refs()
        self.assertFalse(new_egc["cgraph"].is_stable())
        
        # 4. Stabilize
        stabilized = sfss(self.rtctxt, new_egc)
        self.assertTrue(stabilized["cgraph"].is_stable())


if __name__ == "__main__":
    unittest.main()
