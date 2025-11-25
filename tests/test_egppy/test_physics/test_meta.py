"""Meta unit tests."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from egpcommon.properties import GCType, PropertiesBD
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.c_graph_constants import DstRow, SrcRow
from egppy.genetic_code.genetic_code import GCABC
from egppy.genetic_code.interface import Interface
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.physics.meta import (
    MetaCodonTypeError,
    MetaCodonValueError,
    meta_type_cast,
    raise_if_not_instance_of,
)
from egppy.physics.runtime_context import RuntimeContext


class TestMetaCodons(unittest.TestCase):
    """Test meta codons."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class method for test setup."""
        cls.gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)

    def test_raise_if_not_instance_of_success(self):
        """Test raise_if_not_instance_of with valid instance."""
        self.assertEqual(raise_if_not_instance_of(1, int), 1)
        self.assertEqual(raise_if_not_instance_of(1.0, float), 1.0)
        self.assertEqual(raise_if_not_instance_of("s", str), "s")
        self.assertEqual(raise_if_not_instance_of(1, object), 1)

    def test_raise_if_not_instance_of_failure(self):
        """Test raise_if_not_instance_of with invalid instance."""
        with self.assertRaises(MetaCodonTypeError):
            raise_if_not_instance_of(1, str)
        with self.assertRaises(MetaCodonTypeError):
            raise_if_not_instance_of("s", int)

    def test_meta_type_cast_simple(self):
        """Test simple meta type cast."""

        rtctxt = RuntimeContext(self.gpi)
        ifa = Interface(["int", "float", "object"], SrcRow.I)
        ifb = Interface(["Integral", "float", "str"], DstRow.O)

        gc = meta_type_cast(rtctxt, ifa, ifb)
        self.assertIsInstance(gc, GCABC)

        # Check Ad (Destination A)
        ad = gc["cgraph"]["Ad"]
        self.assertEqual(len(ad), 2)
        self.assertEqual(ad[0].typ.name, "int")
        self.assertEqual(ad[1].typ.name, "object")

        # Check Od (Destination O)
        od = gc["cgraph"]["Od"]
        self.assertEqual(len(od), 2)
        self.assertEqual(od[0].typ.name, "Integral")
        self.assertEqual(od[1].typ.name, "str")

        self.assertEqual(PropertiesBD(gc["properties"])["gc_type"], GCType.META)

    def test_meta_type_cast_identical_interfaces(self):
        """Test meta type cast with identical interfaces."""
        rtctxt = RuntimeContext(self.gpi)
        ifa = Interface(["int", "float"], SrcRow.I)
        ifb = Interface(["int", "float"], DstRow.O)

        with self.assertRaises(MetaCodonValueError):
            meta_type_cast(rtctxt, ifa, ifb)

    def test_meta_type_cast_existing_gc(self):
        """Test meta type cast when an existing GC is found."""
        # Mock RuntimeContext and GenePoolInterface
        mock_gpi = MagicMock(spec=GenePoolInterface)
        mock_rtctxt = MagicMock(spec=RuntimeContext)
        mock_rtctxt.gpi = mock_gpi

        # Create a dummy existing GC
        existing_gc = MagicMock(spec=GCABC)
        mock_gpi.select_meta.return_value = existing_gc

        ifa = Interface(["int"], SrcRow.I)
        ifb = Interface(["float"], DstRow.O)

        gc = meta_type_cast(mock_rtctxt, ifa, ifb)

        # Verify that select_meta was called
        mock_gpi.select_meta.assert_called_once()

        # Verify that the returned GC is the existing one
        self.assertIs(gc, existing_gc)
