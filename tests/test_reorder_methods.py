"""Unit tests for the reorder_methods script."""

# Import the functions we want to test
from ast import FunctionDef, parse
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from scripts.reorder_methods import FunctionInfo, MethodExtractor, find_python_files, reorder_file


class TestFunctionInfo(TestCase):
    """Test cases for FunctionInfo dataclass."""

    def test_sort_key_init(self) -> None:
        """Test that __init__ gets priority 0."""

        code = "def __init__(self): pass"
        tree = parse(code)
        node = tree.body[0]
        assert isinstance(node, FunctionDef)

        info = FunctionInfo(
            name="__init__", node=node, start_line=1, end_line=1, lines=["def __init__(self): pass"]
        )
        self.assertEqual(info.sort_key, (0, "__init__"))

    def test_sort_key_dunder(self) -> None:
        """Test that dunder methods get priority 1."""

        code = "def __str__(self): pass"
        tree = parse(code)
        node = tree.body[0]
        assert isinstance(node, FunctionDef)

        info = FunctionInfo(
            name="__str__", node=node, start_line=1, end_line=1, lines=["def __str__(self): pass"]
        )
        self.assertEqual(info.sort_key, (1, "__str__"))

    def test_sort_key_private(self) -> None:
        """Test that private methods get priority 2."""

        code = "def _helper(self): pass"
        tree = parse(code)
        node = tree.body[0]
        assert isinstance(node, FunctionDef)

        info = FunctionInfo(
            name="_helper", node=node, start_line=1, end_line=1, lines=["def _helper(self): pass"]
        )
        self.assertEqual(info.sort_key, (2, "_helper"))

    def test_sort_key_public(self) -> None:
        """Test that public methods get priority 3."""

        code = "def public_method(self): pass"
        tree = parse(code)
        node = tree.body[0]
        assert isinstance(node, FunctionDef)

        info = FunctionInfo(
            name="public_method",
            node=node,
            start_line=1,
            end_line=1,
            lines=["def public_method(self): pass"],
        )
        self.assertEqual(info.sort_key, (3, "public_method"))


class TestMethodExtractor(TestCase):
    """Test cases for MethodExtractor."""

    def test_extract_class_methods(self) -> None:
        """Test extracting methods from a class."""
        code = str(
            "class TestClass:\n    def __init__(self):\n        pass\n    def public(self):\n"
            "        pass\n    def _private(self):\n        pass\n"
        )
        lines = code.strip().split("\n")

        tree = parse(code)
        extractor = MethodExtractor(lines)
        extractor.visit(tree)

        self.assertIn("TestClass", extractor.classes)
        self.assertEqual(len(extractor.classes["TestClass"]["methods"]), 3)
        method_names = [m.name for m in extractor.classes["TestClass"]["methods"]]
        self.assertEqual(set(method_names), {"__init__", "public", "_private"})

    def test_extract_module_functions(self) -> None:
        """Test extracting module-level functions."""
        code = str("def function_a():\n    pass\n\ndef function_b():\n    pass\n")
        lines = code.strip().split("\n")

        tree = parse(code)
        extractor = MethodExtractor(lines)
        extractor.visit(tree)

        self.assertEqual(len(extractor.module_functions), 2)
        func_names = [f.name for f in extractor.module_functions]
        self.assertEqual(set(func_names), {"function_a", "function_b"})

    def test_extract_with_decorators(self) -> None:
        """Test that decorators are included with functions."""
        code = str("class TestClass:\n    @property\n    def value(self):\n        return 1\n")
        lines = code.split("\n")

        tree = parse(code)
        extractor = MethodExtractor(lines)
        extractor.visit(tree)

        methods = extractor.classes["TestClass"]["methods"]
        self.assertEqual(len(methods), 1)
        self.assertEqual(methods[0].name, "value")
        # The decorator should be part of the extracted lines
        self.assertIn("@property", "\n".join(methods[0].lines))


class TestFindPythonFiles(TestCase):
    """Test cases for find_python_files."""

    def test_find_single_file(self) -> None:
        """Test finding a single Python file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# test")

            files = find_python_files(test_file)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0], test_file)

    def test_find_directory(self) -> None:
        """Test finding Python files in a directory."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test1.py").write_text("# test1")
            (tmppath / "test2.py").write_text("# test2")
            (tmppath / "test.txt").write_text("# not python")

            files = find_python_files(tmppath)
            self.assertEqual(len(files), 2)
            self.assertTrue(all(f.suffix == ".py" for f in files))

    def test_exclude_hidden_directories(self) -> None:
        """Test that hidden directories are excluded."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "visible.py").write_text("# visible")

            # Create hidden directory with Python file
            hidden_dir = tmppath / ".hidden"
            hidden_dir.mkdir()
            (hidden_dir / "hidden.py").write_text("# hidden")

            files = find_python_files(tmppath)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].name, "visible.py")

    def test_exclude_venv_directories(self) -> None:
        """Test that virtual environment directories are excluded."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "main.py").write_text("# main")

            # Create various venv directories with Python files
            for venv_name in ["venv", ".venv", "env", "ENV"]:
                venv_dir = tmppath / venv_name
                venv_dir.mkdir()
                (venv_dir / "lib.py").write_text("# lib")

            files = find_python_files(tmppath)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].name, "main.py")

    def test_exclude_cache_directories(self) -> None:
        """Test that cache and build directories are excluded."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "source.py").write_text("# source")

            # Create cache directories with Python files
            for cache_name in ["__pycache__", ".pytest_cache", ".mypy_cache"]:
                cache_dir = tmppath / cache_name
                cache_dir.mkdir()
                (cache_dir / "cached.py").write_text("# cached")

            files = find_python_files(tmppath)
            self.assertEqual(len(files), 1)
            self.assertEqual(files[0].name, "source.py")

    def test_nested_exclusion(self) -> None:
        """Test that exclusion works for nested directories."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "root.py").write_text("# root")

            # Create nested structure: src/venv/lib.py
            src_dir = tmppath / "src"
            src_dir.mkdir()
            (src_dir / "app.py").write_text("# app")

            venv_dir = src_dir / "venv"
            venv_dir.mkdir()
            (venv_dir / "lib.py").write_text("# lib")

            files = find_python_files(tmppath)
            self.assertEqual(len(files), 2)
            file_names = {f.name for f in files}
            self.assertEqual(file_names, {"root.py", "app.py"})


class TestReorderFile(TestCase):
    """Test cases for reorder_file."""

    def test_reorder_class_methods(self) -> None:
        """Test reordering methods in a class."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "class TestClass:\n"
                "    def public(self):\n"
                "        pass\n"
                "\n"
                "    def _private(self):\n"
                "        pass\n"
                "\n"
                "    def __init__(self):\n"
                "        pass\n"
            )

            result = reorder_file(test_file, dry_run=False, verbose=False)
            self.assertTrue(result)

            content = test_file.read_text()
            # Check that __init__ comes before _private which comes before public
            init_pos = content.find("def __init__")
            private_pos = content.find("def _private")
            public_pos = content.find("def public")

            self.assertLess(init_pos, private_pos)
            self.assertLess(private_pos, public_pos)

    def test_reorder_module_functions(self) -> None:
        """Test reordering module-level functions."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("def zebra():\n    pass\n\ndef apple():\n    pass\n")

            result = reorder_file(test_file, dry_run=False, verbose=False)
            self.assertTrue(result)

            content = test_file.read_text()
            # Check that apple comes before zebra
            apple_pos = content.find("def apple")
            zebra_pos = content.find("def zebra")

            self.assertLess(apple_pos, zebra_pos)

    def test_no_reorder_needed(self) -> None:
        """Test that files already in order are not modified."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "class TestClass:\n    def __init__(self):\n        "
                "pass\n\n    def public(self):\n        pass\n"
            )

            result = reorder_file(test_file, dry_run=False, verbose=False)
            self.assertFalse(result)

    def test_preserve_decorators(self) -> None:
        """Test that decorators are preserved with their functions."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                "class TestClass:\n    @property\n    def value(self):\n        "
                "pass\n\n    def __init__(self):\n        pass\n"
            )

            result = reorder_file(test_file, dry_run=False, verbose=False)
            self.assertTrue(result)

            content = test_file.read_text()
            # Check that @property is still before def value
            self.assertIn("@property\n    def value", content)
            # Check that __init__ comes first
            init_pos = content.find("def __init__")
            value_pos = content.find("def value")
            self.assertLess(init_pos, value_pos)


if __name__ == "__main__":
    import unittest

    unittest.main()
