"""Test the TypesDef class."""

import unittest
from os.path import dirname, join

from egppy.c_graph.end_point.import_def import ImportDef, import_def_store
from egppy.c_graph.end_point.types_def.types_def import EPTDB, TypesDef


class TestTypesDef(unittest.TestCase):
    """Test the TypesDef class."""

    def test_types_def(self) -> None:
        """Test the TypesDef class."""
        types_def = TypesDef(
            name="type1",
            xuid=1,
            default="default_value",
            imports=[import_def_store.add(ImportDef(aip=["module1"], name="func1"))],
            inherits=["parent_type"],
        )
        self.assertEqual(types_def.name, "type1")
        self.assertEqual(types_def.uid, 1)
        self.assertEqual(types_def.default, "default_value")
        self.assertEqual(len(types_def.imports), 1)
        self.assertEqual(types_def.inherits, ("parent_type",))
        self.assertEqual(types_def.ept(), (types_def,))
        self.assertFalse(types_def.is_container())
        self.assertEqual(types_def.xuid(), 1)
        self.assertEqual(types_def.tt(), 0)

        types_def_json = {
            "name": "type1",
            "uid": 1,
            "xuid": 1,
            "fx": 0,
            "io": 0,
            "tt": 0,
            "abstract": False,
            "meta": False,
            "default": "default_value",
            "imports": [{"aip": ["module1"], "name": "func1", "as_name": ""}],
            "inherits": ["parent_type"],
        }

        self.assertEqual(types_def.to_json(), types_def_json)


class TestTypesDB(unittest.TestCase):
    """Test the TypesDB class."""

    def test_types_db(self):
        """Test the TypesDB class."""
        test_types_db_path = join(dirname(__file__), "test_types.json")

        with open(test_types_db_path, "w", encoding="utf-8") as f:
            f.write(
                """
                {
                  "int": {
                    "xuid": 1,
                    "default": "0",
                    "imports": [],
                    "inherits": []
                  },
                  "float": {
                    "xuid": 2,
                    "default": "0.0",
                    "imports": [],
                    "inherits": []
                  },
                  "str": {
                    "xuid": 4,
                    "default": "''",
                    "imports": [],
                    "inherits": []
                  },
                   "list[int]": {
                    "xuid": 4,
                    "tt": 1,
                    "default": "[]",
                    "imports": [],
                    "inherits": []
                  }
                }
                """
            )

        _types_db = EPTDB(test_types_db_path)
        self.assertIn("int", _types_db)
        self.assertIn(1, _types_db)
        self.assertIn(_types_db["int"], _types_db)
        self.assertEqual(_types_db["int"].name, "int")
        self.assertEqual(_types_db[1].name, "int")
        self.assertEqual(_types_db[_types_db["int"]].name, "int")
        self.assertTrue(isinstance(_types_db["list[int]"].ept(), tuple))


if __name__ == "__main__":
    unittest.main()
