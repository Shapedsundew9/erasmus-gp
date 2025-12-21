# Python Method Reorder Script

## Overview

The `reorder_methods.py` script is a command-line utility that automatically reorganizes the order of functions and class methods in Python source files according to a consistent hierarchy based on visibility and naming conventions.

## Features

- **Automatic Method Sorting**: Reorders class methods by type:
  1. Constructor (`__init__`)
  2. Dunder methods (alphabetically)
  3. Private methods (alphabetically)
  4. Public methods (alphabetically)

- **Function Sorting**: Reorders module-level functions alphabetically

- **Preservation**: Maintains all code semantics:
  - Decorators stay with their functions
  - Leading comments move with their functions
  - Docstrings remain inside functions
  - Type hints are preserved
  - Indentation is maintained
  - Async functions are handled correctly

## Usage

```bash
# Reorder a single file
python scripts/reorder_methods.py --path path/to/file.py

# Reorder all files in a directory (recursive)
python scripts/reorder_methods.py --path path/to/directory

# Dry run (show what would change without modifying files)
python scripts/reorder_methods.py --path path/to/directory --dry-run

# Verbose output
python scripts/reorder_methods.py --path path/to/directory --verbose
```

## Examples

### Before

```python
class MyClass:
    def public_method(self):
        pass

    def _private_method(self):
        pass

    def __str__(self):
        return "MyClass"

    def __init__(self):
        self.value = 0
```

### After

```python
class MyClass:
    def __init__(self):
        self.value = 0

    def __str__(self):
        return "MyClass"

    def _private_method(self):
        pass

    def public_method(self):
        pass
```

## Sorting Rules

### Class Methods

Methods are sorted in the following order:

1. **Constructor**: `__init__` always comes first
2. **Dunder Methods**: Methods like `__str__`, `__repr__`, etc. (alphabetically)
3. **Private Methods**: Methods starting with `_` (alphabetically)
4. **Public Methods**: All other methods (alphabetically)

### Module Functions

All top-level functions are sorted alphabetically by name.

## Command-Line Options

- `--path PATH`: Path to file or directory to process (default: current directory)
- `--dry-run`: Show what would be changed without modifying files
- `--verbose`, `-v`: Enable verbose output showing all changes

## Testing

Run the test suite:

```bash
python tests/test_reorder_methods.py
```

## Exit Codes

- `0`: Success
- `1`: Error occurred
- `130`: Cancelled by user (Ctrl+C)

## Notes

- The script uses Python's AST (Abstract Syntax Tree) module for parsing
- Files with syntax errors are skipped
- Only `.py` files are processed
- Empty lines are added between methods for readability
