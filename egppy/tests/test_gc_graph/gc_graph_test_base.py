"""Base test module for GC Graph classes."""
import unittest
from itertools import product, permutations, count
from random import randint
from typing import cast
from json import dump, load
from os.path import join, dirname, exists
from egppy.gc_graph.gc_graph_class_factory import StaticGCGraph
from egppy.gc_graph.ep_type import ep_type_lookup, INVALID_EP_TYPE_VALUE
from egppy.gc_graph.egp_typing import (DestinationRow, EndPointType, Row, 
    VALID_ROW_SOURCES, SOURCE_ROWS, SourceRow)


_FOUR_EP_TYPES: tuple[EndPointType, ...] = (ep_type_lookup['n2v']['bool'],
    ep_type_lookup['n2v']['int'],
    ep_type_lookup['n2v']['float'],
    ep_type_lookup['n2v']['str']
)
_TYPE_COMBINATIONS: tuple[tuple[EndPointType, ...], ...] = tuple(product(
    _FOUR_EP_TYPES, _FOUR_EP_TYPES + (INVALID_EP_TYPE_VALUE,)))


def next_idx(src_next_idx: dict[SourceRow, count], src_positions: dict[str, list[int]],
    row: SourceRow, typa: EndPointType) -> int:
    """Get the next index for a source endpoint."""
    # HERE & NEEDS FIXING
    if row != 'U':
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
    filename = join(dirname(__file__), '..', 'data', 'valid_json_gc_graphs.json')
    if not exists(filename):
        jgcg_list = []
        for structure in ('ABO', 'ABOU'):  # JSON GC graphs that are standard graphs
            for row_order in permutations(structure):  # Different orders of assignment
                jgcg_list.append(jgcg := {})
                src_next_idx = {row: count() for row in SOURCE_ROWS}
                src_positions = {}
                for row in row_order:
                    # Row only appears in JSON format GCG's for unconnected
                    # sources so has the same connectivity as row O in standard graphs
                    dst_row = DestinationRow.O if row == 'U' else cast(Row, row)
                    for src in VALID_ROW_SOURCES[False][dst_row]:
                        for typ in _FOUR_EP_TYPES:
                            idx = next_idx(src_next_idx, src_positions, src, typ)
                            jgcg.setdefault(row, []).append([src, idx, typ])

        # Write the JSON GC Graphs to a file
        with open(filename, 'w', encoding="ascii") as f:
            dump(jgcg_list, f, indent=4, sort_keys=True)
    else:
        # Read the JSON GC Graphs from a file
        with open(filename, 'r', encoding="ascii") as f:
            jgcg_list = load(f)
    return jgcg_list


class GCGraphTestBase(unittest.TestCase):
    """Base class for GC Graph tests.
    FIXME: Not done yet
    """

    # The connections type to test. Define in subclass.
    itype: type[StaticGCGraph] = StaticGCGraph
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
        return cls.get_test_cls().__name__.endswith('TestBase')

    @classmethod
    def get_gcg_cls(cls) -> type:
        """Get the Connections class."""
        return cls.itype

    def setUp(self) -> None:
        self.gcg_type = self.get_gcg_cls()
        cls = self.get_test_cls()
        self.gcg = self.gcg_type(cls.jgcg_list[0])

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
