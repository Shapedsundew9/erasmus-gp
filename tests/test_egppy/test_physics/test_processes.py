"""Unit tests for connection processes."""

import unittest
from unittest.mock import MagicMock
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.pgc_api import EGCode
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey, SrcRow, DstRow, EPCls
from egppy.genetic_code.interface import Interface
from egppy.genetic_code.c_graph import CGraph
from egpcommon.properties import CGraphType, GCType, PropertiesBD
from egppy.genetic_code.endpoint import EndPoint
from egppy.physics.processes import (
    create_connection_process,
    wrap_connection_process,
    insert_connection_process,
    crossover_connection_process,
)


class TestProcesses(unittest.TestCase):
    """Test the connection processes."""

    def setUp(self):
        self.gpi = MagicMock()
        self.rtctxt = RuntimeContext(gpi=self.gpi)
        
        # Standard graph structure
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
        # Mock interfaces for sub-GCs to avoid crashes in crossover process
        self.egc["gca"]["cgraph"] = CGraph({
            SrcIfKey.IS: Interface([EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', [])], SrcRow.I),
            DstIfKey.OD: Interface([EndPoint(DstRow.O, 0, EPCls.DST, 'int', [])], DstRow.O),
        })
        self.egc["gcb"]["cgraph"] = CGraph({
            SrcIfKey.IS: Interface([EndPoint(SrcRow.I, 0, EPCls.SRC, 'int', [])], SrcRow.I),
            DstIfKey.OD: Interface([EndPoint(DstRow.O, 0, EPCls.DST, 'int', [])], DstRow.O),
        })

    def test_create_process(self):
        """Verify create process establishes primary connections."""
        new_egc = create_connection_process(self.egc)
        self.assertTrue(new_egc["cgraph"][DstIfKey.AD][0].is_connected())
        self.assertTrue(new_egc["cgraph"][DstIfKey.BD][0].is_connected())
        self.assertTrue(new_egc["cgraph"][DstIfKey.OD][0].is_connected())

    def test_insert_process_overwrite(self):
        """Verify insertion process re-routes (overwrites) non-primary connections."""
        # Setup: Od connected to Is (non-primary, primary for Od is Bs)
        self.egc["cgraph"].connect(SrcRow.I, 0, DstRow.O, 0)
        
        new_egc = insert_connection_process(self.egc)
        # Should now be connected to Bs[0]
        ref = new_egc["cgraph"][DstIfKey.OD][0].refs[0]
        self.assertEqual(ref.row, SrcRow.B)

    def test_wrap_process(self):
        """Verify wrap process only connects if unconnected."""
        # Setup: Ad already connected
        self.egc["cgraph"].connect(SrcRow.I, 0, DstRow.A, 0)
        
        new_egc = wrap_connection_process(self.egc)
        self.assertTrue(new_egc["cgraph"][DstIfKey.AD][0].is_connected())
        # Other primary connections should still be attempted if unconnected
        self.assertTrue(new_egc["cgraph"][DstIfKey.BD][0].is_connected())


if __name__ == "__main__":
    unittest.main()
