"""Reorder methods script.

This script recursively traverses a directory tree, identifies Python source files (.py),
and reorganizes the order of function and class method definitions according to a specific
visibility and naming hierarchy.

## **Sorting Logic**

### **Class Scope (Methods)**

1. **Constructor:** __init__ is always first.
2. **Dunder Methods:** Methods starting and ending with __ (excluding __init__),
     sorted alphabetically (e.g., __repr__, __str__).
3. **Private Methods:** Methods starting with a single _ (e.g., _internal_calc), sorted
    alphabetically.
4. **Public Methods:** All other methods (e.g., calculate_total), sorted alphabetically.

### **Module Scope (Functions)**

1. **Standalone Functions:** All top-level functions sorted alphabetically.

## **Preservation Requirements**

The script preserves:
- Decorators
- Leading comments
- Docstrings
- Type hints
- Indentation
- Asynchronous functions

Usage:
    python reorder_methods.py [--path PATH] [--dry-run] [--verbose]

Examples:
    python reorder_methods.py --path ./egppy
    python reorder_methods.py --path . --dry-run
    python reorder_methods.py --path ./egpcommon --verbose
"""

from argparse import ArgumentParser, Namespace
from ast import AsyncFunctionDef, ClassDef, FunctionDef, NodeVisitor, parse
from dataclasses import dataclass, field
from pathlib import Path
from sys import exit as sys_exit
from typing import Any


@dataclass
class FunctionInfo:
    """Information about a function or method definition."""

    name: str
    node: FunctionDef | AsyncFunctionDef
    start_line: int  # 1-indexed, inclusive (first decorator or comment)
    end_line: int  # 1-indexed, inclusive (last line of function body)
    lines: list[str]  # Complete lines including decorators and comments
    sort_key: tuple[int, str] = field(init=False)

    def __post_init__(self) -> None:
        """Calculate the sort key based on method type."""
        self.sort_key = self._calculate_sort_key()

    def _calculate_sort_key(self) -> tuple[int, str]:
        """Calculate sort key: (priority, alphabetical_name).

        Priority:
            0: __init__
            1: Dunder methods (excluding __init__)
            2: Private methods (starting with _ but not dunder)
            3: Public methods
        """
        if self.name == "__init__":
            return (0, self.name)
        if self.name.startswith("__") and self.name.endswith("__"):
            return (1, self.name)
        if self.name.startswith("_"):
            return (2, self.name)
        return (3, self.name)


class MethodExtractor(NodeVisitor):
    """Extract function and class method definitions from AST."""

    def __init__(self, source_lines: list[str]) -> None:
        """Initialize the extractor.

        Args:
            source_lines: List of source code lines (without trailing newlines).
        """
        self.source_lines = source_lines
        self.module_functions: list[FunctionInfo] = []
        self.classes: dict[str, dict[str, Any]] = {}
        self.current_class: str | None = None

    def _visit_function(self, node: FunctionDef | AsyncFunctionDef) -> None:
        """Process a function or async function definition.

        Args:
            node: The function AST node.
        """
        # Determine start line (accounting for decorators)
        start_line = node.lineno
        if node.decorator_list:
            start_line = node.decorator_list[0].lineno

        # Look for leading comments (lines immediately before decorators or function)
        comment_start = start_line
        for i in range(start_line - 2, -1, -1):  # -2 because lines are 1-indexed
            line = self.source_lines[i].strip()
            if line.startswith("#"):
                comment_start = i + 1  # Convert back to 1-indexed
            elif line:  # Non-empty, non-comment line
                break
            # Empty lines are skipped

        start_line = comment_start
        end_line = node.end_lineno or node.lineno

        # Extract the complete lines
        lines = self.source_lines[start_line - 1 : end_line]

        func_info = FunctionInfo(
            name=node.name,
            node=node,
            start_line=start_line,
            end_line=end_line,
            lines=lines,
        )

        if self.current_class:
            self.classes[self.current_class]["methods"].append(func_info)
        else:
            self.module_functions.append(func_info)

    def visit_AsyncFunctionDef(  # pylint: disable=invalid-name
        self, node: AsyncFunctionDef
    ) -> None:
        """Visit an async function definition.

        Args:
            node: The AsyncFunctionDef AST node.
        """
        self._visit_function(node)

    def visit_ClassDef(self, node: ClassDef) -> None:  # pylint: disable=invalid-name
        """Visit a class definition.

        Args:
            node: The ClassDef AST node.
        """
        self.current_class = node.name
        self.classes[node.name] = {
            "node": node,
            "methods": [],
            "start_line": node.lineno,
            "end_line": node.end_lineno or node.lineno,
        }
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: FunctionDef) -> None:  # pylint: disable=invalid-name
        """Visit a function definition.

        Args:
            node: The FunctionDef AST node.
        """
        self._visit_function(node)


def _should_skip_directory(path: Path) -> bool:
    """Check if a directory should be skipped during file search.

    Args:
        path: Directory path to check.

    Returns:
        True if the directory should be skipped, False otherwise.
    """
    name = path.name

    # Skip hidden directories (starting with .)
    if name.startswith("."):
        return True

    # Skip common virtual environment directories
    venv_names = {
        "venv",
        ".venv",
        "env",
        "ENV",
        "env.bak",
        "venv.bak",
        "__pypackages__",
        ".pixi",
    }
    if name in venv_names:
        return True

    # Skip build and cache directories
    build_cache_names = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".pytype",
        ".tox",
        ".nox",
        "build",
        "dist",
        ".eggs",
    }
    if name in build_cache_names:
        return True

    # Skip .egg-info directories
    if name.endswith(".egg-info"):
        return True

    return False


def find_python_files(root_path: Path) -> list[Path]:
    """Recursively find all Python files in the given path.

    Excludes hidden directories (starting with '.'), virtual environments,
    and build/cache directories.

    Args:
        root_path: Root directory or file path to search.

    Returns:
        List of Path objects for Python files.
    """
    if root_path.is_file():
        return [root_path] if root_path.suffix == ".py" else []

    python_files = []
    for py_file in root_path.rglob("*.py"):
        # Check if any parent directory should be skipped
        skip = False
        # Use parts of the relative path for efficient checking
        relative_path = py_file.relative_to(root_path)
        for part in relative_path.parts[:-1]:  # Exclude the file name itself
            if _should_skip_directory(Path(part)):
                skip = True
                break
        if not skip:
            python_files.append(py_file)

    return sorted(python_files)


def main() -> None:
    """Main entry point for the reorder methods script."""
    args = parse_arguments()

    try:
        root_path = Path(args.path).resolve()

        if not root_path.exists():
            print(f"Error: Path does not exist: {root_path}")
            sys_exit(1)

        # Find all Python files
        python_files = find_python_files(root_path)

        if not python_files:
            print(f"No Python files found in {root_path}")
            sys_exit(0)

        if args.verbose:
            print(f"Found {len(python_files)} Python file(s)")

        # Process each file
        modified_count = 0
        for file_path in python_files:
            if args.verbose:
                print(f"\nProcessing: {file_path}")

            if reorder_file(file_path, dry_run=args.dry_run, verbose=args.verbose):
                modified_count += 1

        # Summary
        if args.dry_run:
            print(f"\nDry run complete. {modified_count} file(s) would be modified.")
        else:
            print(f"\nComplete. {modified_count} file(s) modified.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys_exit(130)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error: {e}")
        sys_exit(1)


def parse_arguments() -> Namespace:
    """Parse command line arguments.

    Returns:
        Namespace: Parsed arguments containing path, dry_run, and verbose flags.
    """
    parser = ArgumentParser(
        description="Reorder methods and functions in Python source files.",
        epilog="This tool reorganizes class methods and module functions according to "
        "visibility and naming conventions.",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to directory or file to process (default: current directory)",
        metavar="PATH",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    return parser.parse_args()


def reorder_file(  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    file_path: Path, dry_run: bool = False, verbose: bool = False
) -> bool:
    """Reorder methods and functions in a Python file.

    Args:
        file_path: Path to the Python file.
        dry_run: If True, don't modify the file.
        verbose: If True, print verbose output.

    Returns:
        True if file was modified (or would be in dry-run), False otherwise.
    """
    try:  # pylint: disable=too-many-nested-blocks
        source = file_path.read_text(encoding="utf-8")
        original_lines = source.splitlines()

        # Parse the AST
        tree = parse(source, filename=str(file_path))

        # Extract functions and methods
        extractor = MethodExtractor(original_lines)
        extractor.visit(tree)

        # Check if any reordering is needed
        modified = False

        # Check module functions
        module_funcs_need_reorder = False
        if extractor.module_functions:
            current_func_order = [f.name for f in extractor.module_functions]
            sorted_func_order = [
                f.name for f in sorted(extractor.module_functions, key=lambda f: f.name)
            ]
            module_funcs_need_reorder = current_func_order != sorted_func_order

        # Check classes
        classes_need_reorder = {}
        for class_name, class_info in extractor.classes.items():
            if not class_info["methods"]:
                continue

            current_order = [m.name for m in class_info["methods"]]
            sorted_order = [m.name for m in sorted(class_info["methods"], key=lambda m: m.sort_key)]

            if current_order != sorted_order:
                classes_need_reorder[class_name] = True
                modified = True
                if verbose:
                    print(f"  Class {class_name}: {current_order} -> {sorted_order}")

        if module_funcs_need_reorder:
            modified = True
            if verbose:
                current_func_order = [f.name for f in extractor.module_functions]
                sorted_func_order = [
                    f.name for f in sorted(extractor.module_functions, key=lambda f: f.name)
                ]
                print(f"  Module functions: {current_func_order} -> {sorted_func_order}")

        if not modified:
            if verbose:
                print(f"No changes needed: {file_path}")
            return False

        # Build the new file
        new_lines: list[str] = []
        skip_until_line: int = -1

        for line_idx, line in enumerate(original_lines):
            line_num = line_idx + 1  # 1-indexed

            # Skip lines we've already handled
            if line_num <= skip_until_line:
                continue

            # Check if we're at the start of a class that needs reordering
            class_to_reorder = None
            for class_name, needs_reorder in classes_need_reorder.items():
                if needs_reorder:
                    class_info = extractor.classes[class_name]
                    if line_num == class_info["start_line"]:
                        class_to_reorder = class_info
                        break

            if class_to_reorder:
                # Add class header (everything before first method)
                first_method_start = min(m.start_line for m in class_to_reorder["methods"])

                # Add lines from class start to first method
                for i in range(class_to_reorder["start_line"] - 1, first_method_start - 1):
                    new_lines.append(original_lines[i])

                # Add sorted methods with blank lines between them
                sorted_methods = sorted(class_to_reorder["methods"], key=lambda m: m.sort_key)
                for idx, method in enumerate(sorted_methods):
                    # Add blank line before method (except first)
                    if idx > 0:
                        new_lines.append("")
                    new_lines.extend(method.lines)

                # Skip to end of class
                skip_until_line = class_to_reorder["end_line"]
                continue

            # Check if we're at the start of module functions that need reordering
            if module_funcs_need_reorder and extractor.module_functions:
                # Check if this is the first module function
                first_module_func = min(extractor.module_functions, key=lambda f: f.start_line)
                if line_num == first_module_func.start_line:
                    # Sort and add all module functions
                    sorted_funcs = sorted(extractor.module_functions, key=lambda f: f.name)
                    for idx, func in enumerate(sorted_funcs):
                        if idx > 0:
                            new_lines.append("")
                            new_lines.append("")
                        new_lines.extend(func.lines)

                    # Skip all the original function lines
                    last_func_line = max(f.end_line for f in extractor.module_functions)
                    skip_until_line = last_func_line
                    module_funcs_need_reorder = False  # Only do this once
                    continue

            # Otherwise, keep the line as-is
            new_lines.append(line)

        # Write the result
        new_content = "\n".join(new_lines) + "\n" if new_lines else ""

        if dry_run:
            print(f"Would modify: {file_path}")
        else:
            file_path.write_text(new_content, encoding="utf-8")
            if verbose:
                print(f"Modified: {file_path}")

        return True

    except SyntaxError as e:
        print(f"Syntax error in {file_path}: {e}")
        return False
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error processing {file_path}: {e}")
        raise


if __name__ == "__main__":
    main()
