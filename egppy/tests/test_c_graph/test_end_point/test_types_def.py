"""Unit tests for the TypesDef class and _to_str_recursive function."""

import unittest
from egppy.c_graph.end_point.import_def import ImportDef, import_def_store

# Absolute import for the functions and classes to test
from egppy.c_graph.end_point.types_def.types_def import (
    TypesDef,
    _to_str_recursive,
    _TUPLE_UID,
    TypesDefBD,
)
from egpcommon.egp_log import Logger, egp_logger, DEBUG  # For logging setup (optional)

# Standard EGP logging pattern (optional, but good practice from example)
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


# Helper class for mocking TypesDef for _to_str_recursive tests
class MockTypesDef:
    """Mocks TypesDef for testing _to_str_recursive."""

    def __init__(self, name: str, uid: int, tt_value: int):
        self.name = name
        self.uid = uid  # Important for _TUPLE_UID check in _to_str_recursive
        self._tt_value = tt_value

    def tt(self) -> int:
        """Returns the mock template type arity."""
        return self._tt_value

    def __repr__(self) -> str:  # For debugging test failures
        return f"MockTypesDef(name='{self.name}', uid={self.uid}, tt_value={self._tt_value})"


class TestToStrRecursive(unittest.TestCase):
    """Unit tests for the _to_str_recursive function."""

    def setUp(self):
        """Set up mock TypesDef instances for testing."""
        # Basic types (UIDs are arbitrary non-_TUPLE_UID for these mocks)
        self.td_int = MockTypesDef(name="int", uid=1001, tt_value=0)
        self.td_str = MockTypesDef(name="str", uid=1002, tt_value=0)
        self.td_bool = MockTypesDef(name="bool", uid=1003, tt_value=0)

        # Template types
        self.td_list_template = MockTypesDef(name="List", uid=2001, tt_value=1)
        self.td_dict_template = MockTypesDef(name="Dict", uid=2002, tt_value=2)
        # Tuple template, using the special _TUPLE_UID from the module
        self.td_tuple_template = MockTypesDef(
            name="Tuple", uid=_TUPLE_UID, tt_value=2
        )  # e.g., Tuple[T1, T2]
        self.td_custom_template = MockTypesDef(name="Custom", uid=2003, tt_value=3)

    def test_single_non_template_type(self):
        """Test with a single type that is not a template (tt=0)."""
        ept = (self.td_int,)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "int")
        self.assertEqual(next_index, 1)

    def test_simple_template_type(self):
        """Test with a simple template type like List[str]."""
        ept = (self.td_list_template, self.td_str)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "List[str]")
        self.assertEqual(next_index, 2)

    def test_nested_template_type(self):
        """Test with a nested template type like Dict[str, List[int]]."""
        ept = (self.td_dict_template, self.td_str, self.td_list_template, self.td_int)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "Dict[str, List[int]]")
        self.assertEqual(next_index, 4)

    def test_tuple_type_two_params(self):
        """Test Tuple type with two parameters, expecting ', ...' suffix."""
        ept = (self.td_tuple_template, self.td_int, self.td_bool)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "Tuple[int, bool, ...]")
        self.assertEqual(next_index, 3)

    def test_tuple_type_one_param(self):
        """Test Tuple type with one parameter."""
        td_tuple_one_param = MockTypesDef(name="Tuple", uid=_TUPLE_UID, tt_value=1)
        ept = (td_tuple_one_param, self.td_str)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "Tuple[str, ...]")
        self.assertEqual(next_index, 2)

    def test_custom_template_three_params(self):
        """Test a custom template with three parameters."""
        ept = (self.td_custom_template, self.td_int, self.td_str, self.td_bool)
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "Custom[int, str, bool]")
        self.assertEqual(next_index, 4)

    def test_ept_longer_than_needed(self):
        """Test that only necessary types from EPT are consumed."""
        ept = (self.td_list_template, self.td_int, self.td_str)  # td_str is extra
        result_str, next_index = _to_str_recursive(ept, 0)  # type: ignore
        self.assertEqual(result_str, "List[int]")
        self.assertEqual(next_index, 2)  # Should only consume up to td_int


class TestTypesDef(unittest.TestCase):
    """Unit tests for the TypesDef class."""

    @classmethod
    def setUpClass(cls):
        """Set up TypesDef instances for testing."""
        cls.td_bytes = TypesDef(name="Bytes", uid=0, ept=(0,))

        # Template TypesDef instances with UIDs structured to yield specific tt() values
        cls.td_collection_template = TypesDef(
            name="Collection", uid={"tt": 1, "xuid": 9}, ept=(9,), abstract=True
        )
        cls.td_mapping_template = TypesDef(
            name="Mapping", uid={"tt": 2, "xuid": 68}, ept=(68,), abstract=True
        )

        # For testing 'imports' property
        cls.imp_typing_list = ImportDef(
            aip=("typing",), name="List", as_name="TypingList", frozen=True
        )
        import_def_store.add(cls.imp_typing_list)  # Ensure ImportDef is in the global store

        cls.td_with_imports = TypesDef(
            name="MyList", uid=3000, ept=(3000,), imports=(cls.imp_typing_list,)
        )

        # For testing methods deriving info from UID bitdict (x, y, fx, io, xuid)
        uid_input_type = {"tt": 1, "ttsp": {"io": 1, "iosp": {"x": 123, "y": 456}}}
        cls.td_input_type = TypesDef(name="InputXY", uid=uid_input_type, ept=(100,))

        uid_output_type = {"tt": 1, "ttsp": {"io": 0, "iosp": {"fx": 7, "xuid": 789}}}
        cls.td_output_type = TypesDef(name="OutputFX", uid=uid_output_type, ept=(101,))

    def test_creation_and_basic_properties(self):
        """Test basic instantiation and default property values."""
        self.assertEqual(self.td_bytes.name, "Bytes")
        self.assertEqual(self.td_bytes.uid, 0)
        self.assertEqual(self.td_bytes.ept, (0,))
        self.assertFalse(self.td_bytes.abstract)
        self.assertIsNone(self.td_bytes.default)
        self.assertEqual(self.td_bytes.imports, tuple())
        self.assertEqual(self.td_bytes.parents, tuple())
        self.assertEqual(self.td_bytes.children, tuple())

        self.assertEqual(self.td_collection_template.name, "Collection")
        expected_uid_coll_template = TypesDefBD({"tt": 1, "xuid": 9}).to_int()
        self.assertEqual(self.td_collection_template.uid, expected_uid_coll_template)
        self.assertEqual(self.td_collection_template.ept, (9,))
        self.assertTrue(self.td_collection_template.abstract)

    def test_tt_method(self):
        """Test the tt() method for different UID structures."""
        self.assertEqual(self.td_bytes.tt(), 0)  # Simple UID 0 -> tt=0
        self.assertEqual(self.td_collection_template.tt(), 1)  # UID dict {"tt": 1, ...}
        self.assertEqual(self.td_mapping_template.tt(), 2)  # UID dict {"tt": 2, ...}

    def test_imports_property(self):
        """Test the 'imports' property."""
        self.assertEqual(len(self.td_with_imports.imports), 1)
        self.assertIn(self.imp_typing_list, self.td_with_imports.imports)

    def test_to_json_method(self):
        """Test JSON serialization."""
        json_bytes = self.td_bytes.to_json()
        self.assertEqual(json_bytes["name"], "Bytes")
        self.assertEqual(json_bytes["uid"], 0)
        self.assertEqual(json_bytes["ept"], [0])  # EPT is list in JSON
        self.assertFalse(json_bytes["abstract"])
        self.assertIsNone(json_bytes["default"])
        self.assertEqual(json_bytes["imports"], [])
        self.assertEqual(json_bytes["parents"], [])
        self.assertEqual(json_bytes["children"], [])

        json_template = self.td_collection_template.to_json()
        self.assertEqual(json_template["name"], "Collection")
        expected_uid_coll_template = TypesDefBD({"tt": 1, "xuid": 9}).to_int()
        self.assertEqual(json_template["uid"], expected_uid_coll_template)
        self.assertEqual(json_template["ept"], [9])
        self.assertTrue(json_template["abstract"])

    def test_bitdict_derived_properties_for_tt0_type(self):
        """Test bitdict-derived properties for a type with tt=0."""
        self.assertIsNone(self.td_bytes.io())
        self.assertIsNone(self.td_bytes.x())
        self.assertIsNone(self.td_bytes.y())
        self.assertIsNone(self.td_bytes.fx())
        self.assertIsNone(self.td_bytes.xuid())

    def test_bitdict_derived_properties_for_input_type(self):
        """Test bitdict-derived properties for an input type (io=1)."""
        self.assertEqual(self.td_input_type.tt(), 1)
        self.assertEqual(self.td_input_type.io(), 1)
        self.assertEqual(self.td_input_type.x(), 123)
        self.assertEqual(self.td_input_type.y(), 456)
        self.assertIsNone(self.td_input_type.fx())
        self.assertIsNone(self.td_input_type.xuid())

    def test_bitdict_derived_properties_for_output_type(self):
        """Test bitdict-derived properties for an output/fx type (io=0)."""
        self.assertEqual(self.td_output_type.tt(), 1)
        self.assertEqual(self.td_output_type.io(), 0)
        self.assertIsNone(self.td_output_type.x())
        self.assertIsNone(self.td_output_type.y())
        self.assertEqual(self.td_output_type.fx(), 7)
        self.assertEqual(self.td_output_type.xuid(), 789)


if __name__ == "__main__":
    unittest.main()
