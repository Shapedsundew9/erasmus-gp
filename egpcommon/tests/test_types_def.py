"""Test the TypesDef class."""

import unittest

from egpcommon.import_def import ImportDef
from egpcommon.types_def import TypesDef


class TestTypesDef(unittest.TestCase):
    """Test the TypesDef class."""

    def test_initialization(self) -> None:
        """Test the initialization of TypesDef."""
        imports = [ImportDef(["egpcommon", "module"], "MyClass", "Alias")]
        types_def = TypesDef("TypeName", 1, "DefaultInstance", imports, ["BaseClass"])
        self.assertEqual(types_def.name, "TypeName")
        self.assertEqual(types_def.uid, 1)
        self.assertEqual(types_def.default, "DefaultInstance")
        self.assertEqual(types_def.imports, imports)
        self.assertEqual(types_def.inherits, ["BaseClass"])

    def test_initialization_without_default_and_imports(self) -> None:
        """Test the initialization of TypesDef without default and imports."""
        types_def = TypesDef("TypeName", 1, inherits=["BaseClass"])
        self.assertEqual(types_def.name, "TypeName")
        self.assertIsNone(types_def.default)
        self.assertEqual(types_def.inherits, ["BaseClass"])
        self.assertIsNone(types_def.default)
        self.assertIsNone(types_def.imports)

    def test_name_setter(self) -> None:
        """Test the name setter."""
        types_def = TypesDef("TypeName", 1)
        types_def.name = "NewTypeName"
        self.assertEqual(types_def.name, "NewTypeName")

        with self.assertRaises(AssertionError):
            types_def.name = ""

        with self.assertRaises(AssertionError):
            types_def.name = "a" * 65

    def test_uid_setter(self) -> None:
        """Test the uid setter."""
        types_def = TypesDef("TypeName", 1)
        types_def.uid = 2
        self.assertEqual(types_def.uid, 2)

        with self.assertRaises(AssertionError):
            types_def.uid = "invalid"  # type: ignore

        with self.assertRaises(AssertionError):
            types_def.uid = 2**31

    def test_default_setter(self) -> None:
        """Test the default setter."""
        types_def = TypesDef("TypeName", 1)
        types_def.default = "NewDefaultInstance"
        self.assertEqual(types_def.default, "NewDefaultInstance")

        with self.assertRaises(AssertionError):
            types_def.default = "a" * 129

    def test_imports_setter(self) -> None:
        """Test the imports setter."""
        imports = [ImportDef(["egpcommon", "module"], "MyClass", "Alias")]
        types_def = TypesDef("TypeName", 1)
        types_def.imports = imports
        self.assertEqual(types_def.imports, imports)

        with self.assertRaises(ValueError):
            types_def.imports = [  # type: ignore
                ImportDef(["egpcommon", "module"], "MyClass", "Alias").to_json(),
                "not_a_dict_or_import_def",
            ]

    def test_to_json(self) -> None:
        """Test the to_json method."""
        imports = [ImportDef(["egpcommon", "module"], "MyClass", "Alias")]
        types_def = TypesDef("TypeName", 1, "DefaultInstance", imports)
        self.assertEqual(
            types_def.to_json(),
            {
                "name": "TypeName",
                "uid": 1,
                "default": "DefaultInstance",
                "imports": [
                    {"aip": ["egpcommon", "module"], "name": "MyClass", "as_name": "Alias"}
                ],
                "inherits": None,
            },
        )

    def test_from_json(self) -> None:
        """Test the from_json method."""
        imports = [ImportDef(["egpcommon", "module"], "MyClass", "Alias")]
        types_def = TypesDef(
            **{
                "name": "TypeName",
                "uid": 1,
                "default": "DefaultInstance",
                "imports": [
                    {"aip": ["egpcommon", "module"], "name": "MyClass", "as_name": "Alias"}
                ],
            }
        )
        self.assertEqual(types_def.name, "TypeName")
        self.assertEqual(types_def.uid, 1)
        self.assertEqual(types_def.default, "DefaultInstance")
        self.assertEqual(types_def.imports, imports)
        self.assertIsNone(types_def.inherits)


if __name__ == "__main__":
    unittest.main()
