"""
Test suite for the TypesDef and TypesDefStore classes in the
egppy.c_graph.end_point.types_def module.
"""

import unittest
from unittest.mock import patch
from array import array

# It's good practice to keep imports relative if these files are part of the same package
# For this example, I'll assume they can be imported directly or you'll adjust the sys.path
# For a real project, ensure your PYTHONPATH is set up correctly or use relative imports.
from egppy.c_graph.end_point.types_def.types_def import TypesDef, TypesDefStore
from egppy.c_graph.end_point.import_def import ImportDef, import_def_store


# pylint: disable=protected-access
class TestTypesDef(unittest.TestCase):
    """Test suite for the TypesDef class."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # Clear import_def_store for consistent tests
        import_def_store.clear()
        self.test_import = ImportDef(aip=["math"], name="sqrt")
        self.test_import.freeze()  # Freeze the import to ensure it's immutable
        import_def_store.add(self.test_import)

    def test_types_def_creation_minimal(self):
        """Test minimal creation of a TypesDef object."""
        td = TypesDef(name="MinimalType", uid=1)
        self.assertEqual(td.name, "MinimalType")
        self.assertEqual(td.uid, 1)
        self.assertFalse(td.abstract)
        self.assertIsNone(td.default)
        self.assertEqual(td.imports, tuple())
        self.assertEqual(td.parents, array("i"))
        self.assertEqual(td.children, array("i"))

    def test_types_def_creation_full(self):
        """Test full creation of a TypesDef object with all parameters."""
        td = TypesDef(
            name="FullType",
            uid={"tt": 1, "xuid": 123},
            abstract=True,
            default="FullType()",
            imports=[self.test_import],
            parents=[
                10,
                TypesDef(name="ParentType", uid=10),
            ],  # ParentType needs to exist or be mocked if store is used
            children=[20],
        )
        self.assertEqual(td.name, "FullType")
        # uid will be calculated by TypesDefBD, let's assume a mock or a known value if calculable
        # For now, just check it's an int
        self.assertIsInstance(td.uid, int)
        self.assertTrue(td.abstract)
        self.assertEqual(td.default, "FullType()")
        self.assertEqual(td.imports, (self.test_import,))
        self.assertEqual(td.parents, array("i", [10, 10]))  # uid of ParentType is 10
        self.assertEqual(td.children, array("i", [20]))

    def test_types_def_uid_dict(self):
        """Test TypesDef creation with a dictionary UID and tt/xuid methods."""
        # This UID corresponds to tt=0, xuid=1
        # Based on a hypothetical TYPESDEF_CONFIG where tt is 1 bit and xuid is 31 bits
        # You'll need to adjust this if your bitdict config is different
        uid_val = 1  # Example, replace with actual calculation if needed
        td = TypesDef(name="BitDictUid", uid={"tt": 0, "xuid": 1})
        self.assertEqual(td.uid, uid_val)
        self.assertEqual(td.tt(), 0)
        self.assertEqual(td.xuid(), 1)

    def test_types_def_comparison(self):
        """Test comparison operators for TypesDef objects."""
        td1 = TypesDef(name="Type1", uid=1)
        td2 = TypesDef(name="Type2", uid=2)
        td1_again = TypesDef(name="Type1Again", uid=1)

        self.assertEqual(td1, td1_again)
        self.assertNotEqual(td1, td2)
        self.assertTrue(td1 < td2)
        self.assertTrue(td1 <= td2)
        self.assertTrue(td1 <= td1_again)
        self.assertTrue(td2 > td1)
        self.assertTrue(td2 >= td1)
        self.assertTrue(td2 >= td1_again)

    def test_types_def_hash(self):
        """Test hashing of TypesDef objects."""
        td1 = TypesDef(name="Type1", uid=1)
        td1_again = TypesDef(name="Type1Again", uid=1)
        self.assertEqual(hash(td1), hash(td1_again))
        self.assertEqual(hash(td1), 1)

    def test_types_def_to_json(self):
        """Test the to_json method of TypesDef."""
        td = TypesDef(
            name="JsonType",
            uid=5,
            abstract=True,
            default="JsonType()",
            imports=[self.test_import],
            parents=[1],
            children=[2],
        )
        expected_json = {
            "name": "JsonType",
            "uid": 5,
            "abstract": True,
            "default": "JsonType()",
            "imports": [self.test_import.to_json()],
            "parents": [1],
            "children": [2],
        }
        self.assertEqual(td.to_json(), expected_json)

    def test_invalid_name(self):
        """Test TypesDef creation with invalid names."""
        with self.assertRaises(AssertionError):
            TypesDef(name="", uid=1)  # Empty name
        with self.assertRaises(AssertionError):
            TypesDef(name="a" * 65, uid=1)  # Too long

    def test_invalid_uid(self):
        """Test TypesDef creation with invalid UIDs."""
        with self.assertRaises(ValueError):
            TypesDef(name="Test", uid="not_an_int_or_dict")  # type: ignore
        with self.assertRaises(AssertionError):  # Assuming 32-bit signed int range
            TypesDef(name="Test", uid=2**31)
        with self.assertRaises(AssertionError):  # Assuming 32-bit signed int range
            TypesDef(name="Test", uid=-(2**31) - 1)

    def test_invalid_imports(self):
        """Test TypesDef creation with invalid import types."""
        with self.assertRaises(ValueError):
            TypesDef(name="Test", uid=1, imports=[123])  # type: ignore

    def test_invalid_parents_children(self):
        """Test TypesDef creation with invalid parent/child types."""
        with self.assertRaises(ValueError):
            TypesDef(name="Test", uid=1, parents=["not_int_or_typedef"])  # type: ignore
        with self.assertRaises(ValueError):
            TypesDef(name="Test", uid=1, children=["not_int_or_typedef"])  # type: ignore


class TestTypesDefStore(unittest.TestCase):
    """Test suite for the TypesDefStore class."""

    def setUp(self):
        """Set up test fixtures and mock dependencies."""
        # It's crucial to mock DB_STORE for store tests
        self.db_store_patcher = patch(
            "egppy.c_graph.end_point.types_def.types_def.DB_STORE", autospec=True
        )
        self.mock_db_store = self.db_store_patcher.start()
        self.addCleanup(self.db_store_patcher.stop)

        # Clear import_def_store for consistent tests
        import_def_store.clear()
        self.test_import_def = ImportDef(aip=["test", "module"], name="TestClass")
        self.test_import_def.freeze()  # Freeze the import to ensure it's immutable
        import_def_store.add(self.test_import_def)

        self.types_def_store = TypesDefStore()
        # Clear internal cache of the store for each test
        self.types_def_store._objects.clear()
        self.types_def_store._cache_hit = 0
        self.types_def_store._cache_miss = 0

    def test_getitem_int_cache_miss_and_hit(self):
        """Test __getitem__ with an integer key, covering cache miss and hit scenarios."""
        mock_type_data = {
            "name": "MyIntType",
            "uid": 100,
            "abstract": False,
            "default": None,
            "imports": [],
            "parents": [],
            "children": [],
        }
        self.mock_db_store.get.return_value = mock_type_data

        # Cache miss
        td_obj = self.types_def_store[100]
        self.assertIsInstance(td_obj, TypesDef)
        self.assertEqual(td_obj.name, "MyIntType")
        self.assertEqual(td_obj.uid, 100)
        self.mock_db_store.get.assert_called_once_with(100, {})
        self.assertEqual(self.types_def_store._cache_miss, 1)
        self.assertEqual(self.types_def_store._cache_hit, 0)

        # Cache hit
        td_obj_cached = self.types_def_store[100]
        self.assertIs(td_obj, td_obj_cached)  # Should be the same object
        self.mock_db_store.get.assert_called_once()  # Not called again
        self.assertEqual(self.types_def_store._cache_miss, 1)
        self.assertEqual(self.types_def_store._cache_hit, 1)

        # Check if also stored by name
        td_obj_name_cached = self.types_def_store["MyIntType"]
        self.assertIs(td_obj, td_obj_name_cached)
        self.assertEqual(self.types_def_store._cache_hit, 2)

    def test_getitem_str_cache_miss_and_hit(self):
        """Test __getitem__ with a string key, covering cache miss and hit scenarios."""
        mock_type_data = {
            "name": "MyStrType",
            "uid": 200,
            "abstract": True,
            "default": "MyStrType()",
            "imports": [{"aip": ["test", "module"], "name": "TestClass"}],  # Will be converted
            "parents": [1],
            "children": [2],
        }
        self.mock_db_store.select.return_value = (mock_type_data,)

        # Cache miss
        td_obj = self.types_def_store["MyStrType"]
        self.assertIsInstance(td_obj, TypesDef)
        self.assertEqual(td_obj.name, "MyStrType")
        self.assertEqual(td_obj.uid, 200)
        self.assertTrue(td_obj.abstract)
        self.assertEqual(td_obj.default, "MyStrType()")
        self.assertEqual(len(td_obj.imports), 1)
        self.assertEqual(td_obj.imports[0].aip, ("test", "module"))
        self.mock_db_store.select.assert_called_once_with(
            "WHERE name = {id}", literals={"id": "MyStrType"}
        )
        self.assertEqual(self.types_def_store._cache_miss, 1)
        self.assertEqual(self.types_def_store._cache_hit, 0)

        # Cache hit
        td_obj_cached = self.types_def_store["MyStrType"]
        self.assertIs(td_obj, td_obj_cached)
        self.mock_db_store.select.assert_called_once()  # Not called again
        self.assertEqual(self.types_def_store._cache_miss, 1)
        self.assertEqual(self.types_def_store._cache_hit, 1)

        # Check if also stored by UID
        td_obj_uid_cached = self.types_def_store[200]
        self.assertIs(td_obj, td_obj_uid_cached)
        self.assertEqual(self.types_def_store._cache_hit, 2)

    def test_getitem_key_not_found_int(self):
        """Test __getitem__ with an integer key that is not found in the store."""
        self.mock_db_store.get.return_value = {}  # Simulate DB returning no data
        with self.assertRaises(KeyError):
            # pylint: disable=pointless-statement
            self.types_def_store[999]
        self.assertEqual(self.types_def_store._cache_miss, 1)

    def test_getitem_key_not_found_str(self):
        """Test __getitem__ with a string key that is not found in the store."""
        self.mock_db_store.select.return_value = tuple()  # Simulate DB returning no data
        with self.assertRaises(KeyError):
            # pylint: disable=pointless-statement
            self.types_def_store["NonExistentType"]
        self.assertEqual(self.types_def_store._cache_miss, 1)

    def test_getitem_invalid_key_type(self):
        """Test __getitem__ with an invalid key type."""
        with self.assertRaises(TypeError):
            # pylint: disable=pointless-statement
            self.types_def_store[123.45]
        self.assertEqual(self.types_def_store._cache_miss, 1)  # Still counts as a miss attempt


if __name__ == "__main__":
    unittest.main()
