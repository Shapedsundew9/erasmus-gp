"""Test the ImportDef class."""

import unittest

from egppy.gc_graph.end_point.import_def import ImportDef


class TestImportDef(unittest.TestCase):
    """Test the ImportDef class."""

    def test_initialization(self) -> None:
        """Test the initialization of ImportDef."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass", "Alias")
        self.assertEqual(import_def.aip, ("egpcommon", "module"))
        self.assertEqual(import_def.name, "MyClass")
        self.assertEqual(import_def.as_name, "Alias")

    def test_initialization_without_as_name(self) -> None:
        """Test the initialization of ImportDef without as_name."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass")
        self.assertEqual(import_def.aip, ("egpcommon", "module"))
        self.assertEqual(import_def.name, "MyClass")
        self.assertEqual(import_def.as_name, "")

    def test_aip_setter(self) -> None:
        """Test the aip setter."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass")
        import_def.aip = ["new", "module"]
        self.assertEqual(import_def.aip, ("new", "module"))

        with self.assertRaises(AssertionError):
            import_def.aip = []

        with self.assertRaises(AssertionError):
            import_def.aip = ["valid", 123]  # type: ignore

    def test_name_setter(self) -> None:
        """Test the name setter."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass")
        import_def.name = "NewClass"
        self.assertEqual(import_def.name, "NewClass")

        with self.assertRaises(AssertionError):
            import_def.name = ""

        with self.assertRaises(AssertionError):
            import_def.name = "a" * 65

    def test_as_name_setter(self) -> None:
        """Test the as_name setter."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass")
        import_def.as_name = "NewAlias"
        self.assertEqual(import_def.as_name, "NewAlias")

        with self.assertRaises(AssertionError):
            import_def.as_name = "a" * 65

    def test_str_representation(self) -> None:
        """Test the string representation of ImportDef."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass", "Alias")
        self.assertEqual(str(import_def), "from egpcommon.module import MyClass as Alias")

        import_def = ImportDef(["egpcommon", "module"], "MyClass")
        self.assertEqual(str(import_def), "from egpcommon.module import MyClass")

    def test_to_json(self) -> None:
        """Test the to_json method."""
        import_def = ImportDef(["egpcommon", "module"], "MyClass", "Alias")
        self.assertEqual(
            import_def.to_json(),
            {
                "aip": ["egpcommon", "module"],
                "name": "MyClass",
                "as_name": "Alias",
            },
        )

    def test_from_json(self) -> None:
        """Test the from_json method."""
        import_def = ImportDef(**ImportDef(["egpcommon", "module"], "MyClass", "Alias").to_json())
        self.assertEqual(import_def.aip, ("egpcommon", "module"))
        self.assertEqual(import_def.name, "MyClass")
        self.assertEqual(import_def.as_name, "Alias")


if __name__ == "__main__":
    unittest.main()
