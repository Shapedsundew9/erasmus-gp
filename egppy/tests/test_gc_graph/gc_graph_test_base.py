"""Base test module for GC Graph classes."""

import unittest
from itertools import count, permutations, product
from json import dump, load
from os.path import dirname, exists, join
from random import choice, randint
from typing import cast

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_graph.ep_type import INVALID_EP_TYPE_VALUE, ep_type_lookup
from egppy.gc_graph.gc_graph_class_factory import FrozenGCGraph, MutableGCGraph
from egppy.gc_graph.typing import (
    DESTINATION_ROWS,
    SOURCE_ROWS,
    VALID_ROW_SOURCES,
    DestinationRow,
    EndPointType,
    EPClsPostfix,
    Row,
    SourceRow,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


_FOUR_EP_TYPES: tuple[EndPointType, ...] = (
    ep_type_lookup["n2v"]["bool"],
    ep_type_lookup["n2v"]["int"],
    ep_type_lookup["n2v"]["float"],
    ep_type_lookup["n2v"]["str"],
)
_TYPE_COMBINATIONS: tuple[tuple[EndPointType, ...], ...] = tuple(
    product(_FOUR_EP_TYPES, _FOUR_EP_TYPES + (INVALID_EP_TYPE_VALUE,))
)


def next_idx(
    src_next_idx: dict[SourceRow, count],
    src_positions: dict[str, list[int]],
    row: SourceRow,
    typa: EndPointType,
) -> int:
    """Get the next index for a source endpoint."""
    if row != "U":
        key = f"{row}{typa}"
        src_positions.setdefault(key, [])
        if len(src_positions[key]) < 2:
            # deepcode ignore unguarded~next~call/test: Infinite counter
            src_positions[key].append(next(src_next_idx[row]))
            return src_positions[key][-1]
        return src_positions[key][randint(0, 1)]
    # deepcode ignore unguarded~next~call/test: Infinite counter
    return next(src_next_idx[row])


def generate_valid_json_gc_graphs() -> list[dict[str, list[list]]]:
    """Generate all possible valid JSON GC Graphs with short rows."""
    filename = join(dirname(__file__), "..", "data", "valid_json_gc_graphs.json")
    if not exists(filename):
        jgcg_list = []
        for structure in ("ABO", "ABOU"):  # JSON GC graphs that are standard graphs
            for row_order in permutations(structure):  # Different orders of assignment
                jgcg_list.append(jgcg := {})
                src_next_idx = {row: count() for row in SOURCE_ROWS}
                src_positions = {}
                for row in row_order:
                    # Row only appears in JSON format GCG's for unconnected
                    # sources so has the same connectivity as row O in standard graphs
                    dst_row = DestinationRow.O if row == "U" else cast(Row, row)
                    for src in VALID_ROW_SOURCES[False][dst_row]:
                        if row == "U":
                            typ = ep_type_lookup["n2v"]["complex"]
                            idx = next_idx(src_next_idx, src_positions, src, typ)
                            jgcg.setdefault(row, []).append([src, idx, typ])
                        else:
                            for typ in _FOUR_EP_TYPES:
                                idx = next_idx(src_next_idx, src_positions, src, typ)
                                jgcg.setdefault(row, []).append([src, idx, typ])
                if "U" in jgcg:
                    jgcg["U"] = sorted(jgcg["U"], key=lambda x: x[0] + f"{x[1]:03d}")

        # Write the JSON GC Graphs to a file
        with open(filename, "w", encoding="ascii") as f:
            dump(jgcg_list, f, indent=4, sort_keys=True)
    else:
        # Read the JSON GC Graphs from a file
        with open(filename, "r", encoding="ascii") as f:
            jgcg_list = load(f)
    return jgcg_list


class GCGraphTestBase(unittest.TestCase):
    """Base class for GC Graph tests.
    FIXME: Not done yet
    """

    # The connections type to test. Define in subclass.
    gcgtype: type[FrozenGCGraph] = FrozenGCGraph
    jgcg_list: list[dict[str, list[list]]] = generate_valid_json_gc_graphs()

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
    def get_gcg_cls(cls) -> type:
        """Get the Connections class."""
        return cls.gcgtype

    def setUp(self) -> None:
        self.gcg_type = self.get_gcg_cls()

    def test_valid_graphs(self) -> None:
        """Test the validity of the graphs."""
        if self.running_in_test_base_class():
            return
        for idx, jgcg in enumerate(self.jgcg_list):
            with self.subTest(idx=idx):
                gcg = self.gcg_type(jgcg)
                gcg.verify()
                gcg.consistency()
                self.assertEqual(gcg.to_json(), jgcg)

    def test_create_from_self(self):
        """Test creating a graph from itself."""
        if self.running_in_test_base_class():
            return
        gcg1 = self.gcg_type(self.jgcg_list[0])
        gcg2 = self.gcg_type(gcg1)
        self.assertEqual(gcg1, gcg2)

    def test_is_stable(self):
        """Test the is_stable method."""
        if self.running_in_test_base_class():
            return
        gcg = self.gcg_type(self.jgcg_list[0])
        self.assertTrue(gcg.is_stable())


class MutableGCGraphTestBase(GCGraphTestBase):
    """Extends the static graph test cases with dynamic graph tests."""

    gcgtype: type = MutableGCGraph

    def test_equal_to_static(self) -> None:
        """Test building a graph from endpoints."""
        if self.running_in_test_base_class():
            return
        sgcg = FrozenGCGraph(self.jgcg_list[0])
        dgcg = self.gcg_type(sgcg)
        self.assertEqual(sgcg, dgcg)

    def test_del_all_endpoints(self) -> None:
        """Test deleting and setting endpoints."""
        if self.running_in_test_base_class():
            return
        jgcg = self.jgcg_list[0]
        gcg = self.gcg_type(jgcg)
        for ep in reversed(tuple(gcg.epkeys())):
            del gcg[ep]
        self.assertEqual(gcg.to_json(), {r: [] for r in jgcg})  # Empty graph
        for ikey in gcg.ikeys():
            self.assertEqual(len(gcg[ikey]), 0)

    def test_del_interface(self) -> None:
        """Test deleting interfaces."""
        if self.running_in_test_base_class():
            return
        jgcg = self.jgcg_list[0]
        gcg = self.gcg_type(jgcg)
        for ikey in gcg.ikeys():
            del gcg[ikey]
            self.assertNotIn(ikey, gcg)

    def test_del_connections(self) -> None:
        """Test deleting connections."""
        if self.running_in_test_base_class():
            return
        jgcg = self.jgcg_list[0]
        gcg = self.gcg_type(jgcg)
        for ikey in gcg.ikeys():
            del gcg[ikey + "c"]
            self.assertNotIn(ikey + "c", gcg)

    def test_pop_endpoints(self) -> None:
        """Test popping endpoints."""
        if self.running_in_test_base_class():
            return
        jgcg = self.jgcg_list[0]
        gcg = self.gcg_type(jgcg)
        sgcg = FrozenGCGraph(jgcg)
        for ikey in gcg.ikeys():
            del gcg[ikey[0] + "---" + ikey[1]]
            self.assertEqual(len(gcg[ikey]) + 1, len(sgcg[ikey]))
            for idx, ept in enumerate(gcg[ikey]):
                self.assertEqual(ept, sgcg[ikey][idx])

    def test_append_endpoints(self) -> None:
        """Test appending endpoints."""
        if self.running_in_test_base_class():
            return
        jgcg = self.jgcg_list[0]
        gcg = self.gcg_type(jgcg)
        sgcg = FrozenGCGraph(jgcg)
        for ikey in gcg.ikeys():
            gcg[ikey[0] + "+++" + ikey[1]] = sgcg[ikey[0] + "000" + ikey[1]]
            self.assertEqual(len(gcg[ikey]), len(sgcg[ikey]) + 1)
            self.assertEqual(gcg[ikey][-1], sgcg[ikey][0])
            self.assertEqual(tuple(gcg[ikey + "c"][-1]), tuple(sgcg[ikey + "c"][0]))
            ep1 = gcg[ikey[0] + f"{len(gcg[ikey]) - 1:03d}" + ikey[1]]
            ep2 = sgcg[ikey[0] + "000" + ikey[1]]
            self.assertEqual(ep1.get_cls(), ep2.get_cls())
            self.assertEqual(ep1.get_refs(), ep2.get_refs())
            self.assertEqual(ep1.get_typ(), ep2.get_typ())
            self.assertEqual(ep1.get_row(), ep2.get_row())

    def test_is_stable2(self):
        """Test the is_stable method."""
        if self.running_in_test_base_class():
            return
        for jgcg in self.jgcg_list:
            gcg = self.gcg_type(jgcg)
            # The maximum number of endpoints to remove
            count = randint(1, 4)
            # Find a destination row that has 1 or more endpoints
            for drow in DESTINATION_ROWS:
                if drow in gcg and len(gcg[drow + EPClsPostfix.DST]) > 0:
                    # Choose a random endpoint in the row
                    idx = randint(0, len(gcg[drow + EPClsPostfix.DST]) - 1)
                    ref = gcg[drow + EPClsPostfix.DST + "c"][idx][0]
                    # Its a destination so only has one reference which we remove
                    gcg[drow + EPClsPostfix.DST + "c"][0] = []
                    # Need to find the reference in the source row reference list and remove it
                    gcg[ref.get_row() + EPClsPostfix.SRC + "c"][ref.get_idx()].remove((drow, idx))
                    break
            # Check that the graph is not stable
            self.assertFalse(gcg.is_stable())
