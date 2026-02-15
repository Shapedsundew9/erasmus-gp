"""Unit tests for the egppy.genetic_code.types_def module.

Tests cover the TypesDef class initialization, validation, comparison
operators, hashing, repr/str, to_json serialization, and iteration.
"""

import unittest
from array import array

from egppy.genetic_code.types_def import TypesDef


class TestTypesDefInit(unittest.TestCase):
    """Test TypesDef construction and attribute assignment."""

    def _make_simple(self, **kwargs) -> TypesDef:
        """Create a minimal TypesDef with sensible defaults."""
        defaults = {
            "name": "TestType",
            "uid": 100,
        }
        defaults.update(kwargs)
        return TypesDef(**defaults)

    def test_minimal_init(self) -> None:
        """TypesDef can be created with just name and uid."""
        td = self._make_simple()
        self.assertEqual(td.name, "TestType")
        self.assertEqual(td.uid, 100)
        self.assertFalse(td.abstract)
        self.assertIsNone(td.default)
        self.assertEqual(td.depth, 0)
        self.assertEqual(len(td.imports), 0)
        self.assertEqual(len(td.parents), 0)
        self.assertEqual(len(td.children), 0)
        self.assertIsNone(td.alias)

    def test_abstract_flag(self) -> None:
        """TypesDef abstract flag is stored correctly."""
        td = self._make_simple(abstract=True)
        self.assertTrue(td.abstract)

    def test_default_value(self) -> None:
        """TypesDef default string is stored correctly."""
        td = self._make_simple(default="int()")
        self.assertEqual(td.default, "int()")

    def test_depth(self) -> None:
        """TypesDef depth is stored correctly."""
        td = self._make_simple(depth=3)
        self.assertEqual(td.depth, 3)

    def test_alias(self) -> None:
        """TypesDef alias is stored correctly."""
        td = self._make_simple(alias="MyAlias")
        self.assertEqual(td.alias, "MyAlias")

    def test_parents_from_ints(self) -> None:
        """Parents can be provided as a list of int uids."""
        td = self._make_simple(parents=[1, 2, 3])
        self.assertEqual(list(td.parents), [1, 2, 3])
        self.assertIsInstance(td.parents, array)

    def test_children_from_ints(self) -> None:
        """Children can be provided as a list of int uids."""
        td = self._make_simple(children=[10, 20])
        self.assertEqual(list(td.children), [10, 20])

    def test_subtypes_from_ints(self) -> None:
        """Subtypes can be provided as a list of int uids."""
        td = self._make_simple(subtypes=[5, 6])
        self.assertEqual(list(td.subtypes), [5, 6])

    def test_parents_from_typedef(self) -> None:
        """Parents can be provided as TypesDef instances."""
        parent = self._make_simple(name="Parent", uid=1)
        td = self._make_simple(parents=[parent])
        self.assertEqual(list(td.parents), [1])


class TestTypesDefComparison(unittest.TestCase):
    """Test comparison operators on TypesDef."""

    def setUp(self) -> None:
        """Create TypesDef instances with different UIDs for comparison tests."""
        self.td_a = TypesDef(name="A", uid=10)
        self.td_b = TypesDef(name="B", uid=20)
        self.td_a2 = TypesDef(name="A2", uid=10)

    def test_eq_same_uid(self) -> None:
        """TypesDef objects with the same UID are equal."""
        self.assertEqual(self.td_a, self.td_a2)

    def test_eq_different_uid(self) -> None:
        """TypesDef objects with different UIDs are not equal."""
        self.assertNotEqual(self.td_a, self.td_b)

    def test_ne(self) -> None:
        """TypesDef __ne__ returns True for different UIDs."""
        self.assertTrue(self.td_a != self.td_b)

    def test_lt(self) -> None:
        """TypesDef __lt__ compares UIDs."""
        self.assertTrue(self.td_a < self.td_b)
        self.assertFalse(self.td_b < self.td_a)

    def test_le(self) -> None:
        """TypesDef __le__ compares UIDs."""
        self.assertTrue(self.td_a <= self.td_a2)
        self.assertTrue(self.td_a <= self.td_b)

    def test_gt(self) -> None:
        """TypesDef __gt__ compares UIDs."""
        self.assertTrue(self.td_b > self.td_a)

    def test_ge(self) -> None:
        """TypesDef __ge__ compares UIDs."""
        self.assertTrue(self.td_b >= self.td_a)
        self.assertTrue(self.td_a >= self.td_a2)

    def test_comparison_with_non_typedef(self) -> None:
        """Comparisons with non-TypesDef return NotImplemented."""
        self.assertNotEqual(self.td_a, 10)
        self.assertEqual(self.td_a.__lt__(42), NotImplemented)
        self.assertEqual(self.td_a.__gt__("x"), NotImplemented)


class TestTypesDefHash(unittest.TestCase):
    """Test TypesDef hashing."""

    def test_hash_equals_uid(self) -> None:
        """TypesDef hash is the UID."""
        td = TypesDef(name="H", uid=42)
        self.assertEqual(hash(td), 42)

    def test_hash_consistency(self) -> None:
        """Two TypesDef with the same UID have the same hash."""
        td1 = TypesDef(name="H1", uid=99)
        td2 = TypesDef(name="H2", uid=99)
        self.assertEqual(hash(td1), hash(td2))

    def test_usable_in_set(self) -> None:
        """TypesDef objects with the same UID de-duplicate in a set."""
        td1 = TypesDef(name="S1", uid=7)
        td2 = TypesDef(name="S2", uid=7)
        self.assertEqual(len({td1, td2}), 1)


class TestTypesDefStringRepresentations(unittest.TestCase):
    """Test __repr__ and __str__."""

    def test_str_returns_name(self) -> None:
        """str(TypesDef) returns the type name."""
        td = TypesDef(name="MyType", uid=1)
        self.assertEqual(str(td), "MyType")

    def test_repr_contains_name_and_uid(self) -> None:
        """repr(TypesDef) includes name and uid."""
        td = TypesDef(name="MyType", uid=1)
        r = repr(td)
        self.assertIn("MyType", r)
        self.assertIn("uid=1", r)
        self.assertTrue(r.startswith("TypesDef("))


class TestTypesDefToJson(unittest.TestCase):
    """Test to_json serialization."""

    def test_to_json_keys(self) -> None:
        """to_json returns the expected keys."""
        td = TypesDef(name="J", uid=50)
        j = td.to_json()
        expected_keys = {
            "abstract",
            "alias",
            "children",
            "default",
            "depth",
            "imports",
            "name",
            "parents",
            "subtypes",
            "template",
            "tt",
            "uid",
        }
        self.assertEqual(set(j.keys()), expected_keys)

    def test_to_json_values(self) -> None:
        """to_json returns correct values for a simple TypesDef."""
        td = TypesDef(name="J", uid=50, abstract=True, depth=2)
        j = td.to_json()
        self.assertEqual(j["name"], "J")
        self.assertEqual(j["uid"], 50)
        self.assertTrue(j["abstract"])
        self.assertEqual(j["depth"], 2)


class TestTypesDefIteration(unittest.TestCase):
    """Test __iter__ and __len__."""

    def test_len(self) -> None:
        """len(TypesDef) returns 7."""
        td = TypesDef(name="L", uid=1)
        self.assertEqual(len(td), 7)

    def test_iter_yields_json_values(self) -> None:
        """Iterating over TypesDef yields to_json() values."""
        td = TypesDef(name="I", uid=1)
        values = list(td)
        json_values = list(td.to_json().values())
        self.assertEqual(values, json_values)


class TestTypesDefValidation(unittest.TestCase):
    """Test validation of invalid inputs."""

    def test_invalid_parents_type(self) -> None:
        """Non-int, non-TypesDef parents raise ValueError."""
        with self.assertRaises(ValueError):
            TypesDef(name="P", uid=1, parents=["invalid"])  # type: ignore[list-item]

    def test_invalid_children_type(self) -> None:
        """Non-int, non-TypesDef children raise ValueError."""
        with self.assertRaises(ValueError):
            TypesDef(name="C", uid=1, children=[3.14])  # type: ignore[list-item]

    def test_invalid_subtypes_type(self) -> None:
        """Non-int, non-TypesDef subtypes raise ValueError."""
        with self.assertRaises(ValueError):
            TypesDef(name="S", uid=1, subtypes=[None])  # type: ignore[list-item]


if __name__ == "__main__":
    unittest.main()
