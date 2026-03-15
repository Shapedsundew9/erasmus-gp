"""Unit tests for structural optimizations."""

import unittest
from unittest.mock import MagicMock
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.pgc_api import EGCode
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SrcRow, DstRow, EPCls
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.c_graph import CGraph
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.endpoint import EndPoint
from egppy.physics.optimization import dead_code_elimination, unused_parameter_removal


class TestOptimization(unittest.TestCase):
    """Test the optimization functions."""

    def setUp(self):
        self.gpi = MagicMock()
        self.rtctxt = RuntimeContext(gpi=self.gpi)
        
        cgraph_dict = {
            SrcIfKey.IS: Interface([
                EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', []),
                EndPoint(SrcRow.I, 1, EPCls.SRC, 'int', [])
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
            "gca": "0" * 64,
            "gcb": "0" * 64,
        })

    def test_dce(self):
        """Verify DCE removes unreachable sub-GCs."""
        # Is[0] -> Ad, As[0] -> Od[0]. GCB is dead.
        self.egc["cgraph"].connect(SrcRow.I, 0, DstRow.A, 0)
        self.egc["cgraph"].connect(SrcRow.A, 0, DstRow.O, 0)
        
        new_egc = dead_code_elimination(self.rtctxt, self.egc)
        self.assertIsNone(new_egc["gcb"])
        self.assertIsNotNone(new_egc["gca"])
        self.assertNotIn(DstIfKey.BD, new_egc["cgraph"])

    def test_upr(self):
        """Verify UPR removes unused input parameters."""
        # Is[0] -> Ad, As[0] -> Od[0]. Is[1] is unused.
        self.egc["cgraph"].connect(SrcRow.I, 0, DstRow.A, 0)
        self.egc["cgraph"].connect(SrcRow.A, 0, DstRow.O, 0)
        
        new_egc = unused_parameter_removal(self.rtctxt, self.egc)
        self.assertEqual(len(new_egc["cgraph"][SrcIfKey.IS]), 1)
        self.assertEqual(new_egc["cgraph"][SrcIfKey.IS][0].idx, 0)


if __name__ == "__main__":
    unittest.main()
