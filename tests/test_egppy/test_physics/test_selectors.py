"""Unit tests for the egppy.physics.selectors module.

Tests cover all selector functions using the default gene pool database
populated with codons from codons.json. The gene pool contains ~673 codons
with various input/output type combinations.

Type hierarchy used in tests:
    object (uid=0)
        Hashable (uid=56)
            Number (uid=88)
                Complex (uid=18)
                    Real (uid=125)
                        Rational (uid=124)
                            Integral (uid=58)
                                int (uid=167)
                                bool (uid=158)
                        float (uid=165)
            str (uid=172)
        PsqlType (uid=119)
            PsqlIntegral (uid=107)
                PsqlBigInt (uid=93)

Note:
    GGCDict objects returned by selectors do not preserve the raw DB columns
    ``input_types`` and ``output_types``. To verify types, each test wraps the
    returned GGCDict in a ``GPGCView`` which derives these fields from the
    C-graph (the source of truth for type information).
"""

import unittest

from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.genetic_code.gpg_view import GPGCView
from egppy.genetic_code.types_def_store import types_def_store
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.selectors import (
    _expand_types_ancestors,
    _expand_types_descendants,
    random_codon_selector,
    random_compatible_input_selector,
    random_compatible_io_selector,
    random_compatible_output_selector,
    random_downcast_input_selector,
    random_downcast_io_selector,
    random_downcast_output_selector,
    random_exact_input_selector,
    random_exact_io_selector,
    random_exact_output_selector,
    random_overlap_io_selector,
    random_pgc_selector,
    random_subset_input_selector,
    random_subset_io_selector,
    random_subset_output_selector,
    random_superset_input_selector,
    random_superset_io_selector,
    random_superset_output_selector,
)


def _uid(name: str) -> int:
    """Get the UID for a type name."""
    return types_def_store[name].uid


class TestSelectorsSetup(unittest.TestCase):
    """Test fixture providing a RuntimeContext connected to the default gene pool."""

    gpi: GenePoolInterface
    rtctxt: RuntimeContext

    @classmethod
    def setUpClass(cls) -> None:
        """Create a GenePoolInterface and RuntimeContext for all tests."""
        cls.gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)
        cls.rtctxt = RuntimeContext(gpi=cls.gpi)


class TestExpandHelpers(TestSelectorsSetup):
    """Tests for _expand_types_ancestors and _expand_types_descendants."""

    def test_expand_ancestors_int(self) -> None:
        """Expanding int should include int and all its ancestors up to object."""
        int_uid = _uid("int")
        result = _expand_types_ancestors([int_uid])
        self.assertIn(int_uid, result)
        self.assertIn(_uid("Integral"), result)
        self.assertIn(_uid("Rational"), result)
        self.assertIn(_uid("Real"), result)
        self.assertIn(_uid("Complex"), result)
        self.assertIn(_uid("Number"), result)
        self.assertIn(_uid("Hashable"), result)
        self.assertIn(_uid("object"), result)

    def test_expand_ancestors_deduplicates(self) -> None:
        """Expanding two types with shared ancestors should deduplicate."""
        result_both = _expand_types_ancestors([_uid("int"), _uid("float")])
        result_int = _expand_types_ancestors([_uid("int")])
        result_float = _expand_types_ancestors([_uid("float")])
        expected = sorted(set(result_int) | set(result_float))
        self.assertEqual(result_both, expected)

    def test_expand_ancestors_empty(self) -> None:
        """Expanding an empty list should return an empty list."""
        self.assertEqual(_expand_types_ancestors([]), [])

    def test_expand_ancestors_sorted(self) -> None:
        """Result should be sorted."""
        result = _expand_types_ancestors([_uid("int"), _uid("str")])
        self.assertEqual(result, sorted(result))

    def test_expand_descendants_integral(self) -> None:
        """Expanding Integral should include Integral, int, and bool."""
        integral_uid = _uid("Integral")
        result = _expand_types_descendants([integral_uid])
        self.assertIn(integral_uid, result)
        self.assertIn(_uid("int"), result)
        self.assertIn(_uid("bool"), result)

    def test_expand_descendants_object(self) -> None:
        """Expanding object should include many types (it is the root)."""
        result = _expand_types_descendants([_uid("object")])
        self.assertIn(_uid("object"), result)
        self.assertIn(_uid("int"), result)
        self.assertIn(_uid("str"), result)
        self.assertGreater(len(result), 10)

    def test_expand_descendants_empty(self) -> None:
        """Expanding an empty list should return an empty list."""
        self.assertEqual(_expand_types_descendants([]), [])

    def test_expand_descendants_sorted(self) -> None:
        """Result should be sorted."""
        result = _expand_types_descendants([_uid("Number")])
        self.assertEqual(result, sorted(result))

    def test_expand_descendants_leaf_type(self) -> None:
        """Expanding a leaf type (bool) should return only itself."""
        bool_uid = _uid("bool")
        result = _expand_types_descendants([bool_uid])
        self.assertEqual(result, [bool_uid])


class TestExistingSelectors(TestSelectorsSetup):
    """Tests for the original random_codon_selector and random_pgc_selector."""

    def test_random_codon_selector(self) -> None:
        """random_codon_selector should return a GGCDict that is a codon."""
        ggc = random_codon_selector(self.rtctxt)
        self.assertIsInstance(ggc, GGCDict)
        self.assertTrue(ggc.is_codon())

    def test_random_pgc_selector(self) -> None:
        """random_pgc_selector should return a GGCDict with EGCode in output_types."""
        ggc = random_pgc_selector(self.rtctxt)
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        eg_code_uid = _uid("EGCode")
        self.assertIn(eg_code_uid, view["output_types"])


class TestExactSelectors(TestSelectorsSetup):
    """Tests for exact match selectors (= operator)."""

    def test_exact_io_selector(self) -> None:
        """Select a GC with exact input and output types matching [Integral], [Integral].

        Codons with input_types=[Integral] output_types=[Integral] exist (e.g. ^, >>).
        """
        integral_uid = _uid("Integral")
        ggc = random_exact_io_selector(self.rtctxt, [integral_uid], [integral_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertEqual(list(view["input_types"]), [integral_uid])
        self.assertEqual(list(view["output_types"]), [integral_uid])

    def test_exact_input_selector(self) -> None:
        """Select a GC with exact input types matching [int]."""
        int_uid = _uid("int")
        ggc = random_exact_input_selector(self.rtctxt, [int_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertEqual(list(view["input_types"]), [int_uid])

    def test_exact_output_selector(self) -> None:
        """Select a GC with exact output types matching [int]."""
        int_uid = _uid("int")
        ggc = random_exact_output_selector(self.rtctxt, [int_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertEqual(list(view["output_types"]), [int_uid])

    def test_exact_io_no_match_raises(self) -> None:
        """exact_io_selector raises KeyError when no GC matches impossible types."""
        impossible = [_uid("int"), _uid("str"), _uid("float"), _uid("bool")]
        with self.assertRaises(KeyError):
            random_exact_io_selector(self.rtctxt, impossible, impossible)

    def test_exact_output_empty_types(self) -> None:
        """Select a GC with empty output types (codons with output_types=[])."""
        ggc = random_exact_output_selector(self.rtctxt, [])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertEqual(list(view["output_types"]), [])


class TestSubsetSelectors(TestSelectorsSetup):
    """Tests for subset match selectors (<@ operator).

    GC types must be contained within the requested types.
    """

    def test_subset_io_selector(self) -> None:
        """A GC with input/output types that are subsets of {int, Integral}."""
        int_uid = _uid("int")
        integral_uid = _uid("Integral")
        type_set = [int_uid, integral_uid]
        ggc = random_subset_io_selector(self.rtctxt, type_set, type_set)
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        for t in view["input_types"]:
            self.assertIn(t, type_set)
        for t in view["output_types"]:
            self.assertIn(t, type_set)

    def test_subset_input_selector(self) -> None:
        """A GC whose input types are a subset of {int, Integral, str}."""
        type_set = [_uid("int"), _uid("Integral"), _uid("str")]
        ggc = random_subset_input_selector(self.rtctxt, type_set)
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        for t in view["input_types"]:
            self.assertIn(t, type_set)

    def test_subset_output_selector(self) -> None:
        """A GC whose output types are a subset of {int, bool, Integral}."""
        type_set = [_uid("int"), _uid("bool"), _uid("Integral")]
        ggc = random_subset_output_selector(self.rtctxt, type_set)
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        for t in view["output_types"]:
            self.assertIn(t, type_set)


class TestSupersetSelectors(TestSelectorsSetup):
    """Tests for superset match selectors (@> operator).

    GC types must contain all of the requested types.
    """

    def test_superset_io_selector(self) -> None:
        """A GC whose types contain at least [Integral] in both directions."""
        integral_uid = _uid("Integral")
        ggc = random_superset_io_selector(self.rtctxt, [integral_uid], [integral_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertIn(integral_uid, list(view["input_types"]))
        self.assertIn(integral_uid, list(view["output_types"]))

    def test_superset_input_selector(self) -> None:
        """A GC whose input types contain at least [Integral]."""
        integral_uid = _uid("Integral")
        ggc = random_superset_input_selector(self.rtctxt, [integral_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertIn(integral_uid, list(view["input_types"]))

    def test_superset_output_selector(self) -> None:
        """A GC whose output types contain at least [int]."""
        int_uid = _uid("int")
        ggc = random_superset_output_selector(self.rtctxt, [int_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertIn(int_uid, list(view["output_types"]))


class TestOverlapSelector(TestSelectorsSetup):
    """Tests for overlap match selector (&& operator).

    GC must share at least one type in common on each side.
    """

    def test_overlap_io_selector(self) -> None:
        """A GC with at least one common input and output type."""
        int_uid = _uid("int")
        integral_uid = _uid("Integral")
        requested = {int_uid, integral_uid}
        ggc = random_overlap_io_selector(self.rtctxt, list(requested), list(requested))
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        self.assertTrue(set(view["input_types"]) & requested)
        self.assertTrue(set(view["output_types"]) & requested)


class TestCompatibleSelectors(TestSelectorsSetup):
    """Tests for compatible type selectors (ancestor/descendant expansion + &&).

    Input types expanded via ancestors, output types via descendants.
    """

    def test_compatible_io_selector(self) -> None:
        """Select a GC compatible with int inputs and Integral outputs.

        int's ancestors include Integral, so a GC with Integral inputs matches.
        Integral's descendants include int, so a GC with int outputs matches.
        """
        int_uid = _uid("int")
        integral_uid = _uid("Integral")
        ggc = random_compatible_io_selector(self.rtctxt, [int_uid], [integral_uid])
        self.assertIsInstance(ggc, GGCDict)

    def test_compatible_input_selector(self) -> None:
        """Select a GC with inputs compatible with int.

        Should find GCs expecting Integral, Number, etc. (ancestors of int).
        """
        int_uid = _uid("int")
        ggc = random_compatible_input_selector(self.rtctxt, [int_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_ancestors([int_uid]))
        self.assertTrue(set(view["input_types"]) & expanded)

    def test_compatible_output_selector(self) -> None:
        """Select a GC with outputs compatible with Number.

        Number's descendants include Complex, Real, Rational, Integral, int, bool, float.
        GCs outputting any of those types should match.
        """
        number_uid = _uid("Number")
        ggc = random_compatible_output_selector(self.rtctxt, [number_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_descendants([number_uid]))
        self.assertTrue(set(view["output_types"]) & expanded)

    def test_compatible_input_broader_than_exact(self) -> None:
        """Compatible input search for bool should find more than exact search.

        bool has many ancestors (Integral, Rational, Real, Complex, Number, Hashable, object).
        Compatible search should find codons expecting Integral, Number, etc.
        """
        bool_uid = _uid("bool")
        ggc = random_compatible_input_selector(self.rtctxt, [bool_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_ancestors([bool_uid]))
        self.assertTrue(set(view["input_types"]) & expanded)


class TestDowncastSelectors(TestSelectorsSetup):
    """Tests for downcast-compatible selectors (reverse expansion + &&).

    Input types expanded via descendants, output types via ancestors.
    """

    def test_downcast_io_selector(self) -> None:
        """Select a GC with downcast-compatible Integral inputs and int outputs.

        Integral descendants: {Integral, int, bool} -> matches GC with int inputs.
        int ancestors: {int, Integral, ..., object} -> matches GC with Integral outputs.
        """
        integral_uid = _uid("Integral")
        int_uid = _uid("int")
        ggc = random_downcast_io_selector(self.rtctxt, [integral_uid], [int_uid])
        self.assertIsInstance(ggc, GGCDict)

    def test_downcast_input_selector(self) -> None:
        """Select a GC with downcast-compatible Integral inputs.

        Integral's descendants are {Integral, int, bool}, so GCs expecting
        int or bool should also match.
        """
        integral_uid = _uid("Integral")
        ggc = random_downcast_input_selector(self.rtctxt, [integral_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_descendants([integral_uid]))
        self.assertTrue(set(view["input_types"]) & expanded)

    def test_downcast_output_selector(self) -> None:
        """Select a GC with downcast-compatible int outputs.

        int's ancestors include Integral, Rational, ..., object. GCs producing
        any of those types should match.
        """
        int_uid = _uid("int")
        ggc = random_downcast_output_selector(self.rtctxt, [int_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_ancestors([int_uid]))
        self.assertTrue(set(view["output_types"]) & expanded)

    def test_downcast_input_broader_than_exact(self) -> None:
        """Downcast input for Number should find GCs expecting Number's descendants.

        Number descendants include Complex, Real, Rational, Integral, int, bool, float.
        """
        number_uid = _uid("Number")
        ggc = random_downcast_input_selector(self.rtctxt, [number_uid])
        self.assertIsInstance(ggc, GGCDict)
        view = GPGCView(ggc)
        expanded = set(_expand_types_descendants([number_uid]))
        self.assertTrue(set(view["input_types"]) & expanded)


if __name__ == "__main__":
    unittest.main()
