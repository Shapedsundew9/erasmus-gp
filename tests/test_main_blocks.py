"""This script dynamically discovers and tests Python modules that contain a
__main__ block. It runs each module as if it were the main program, checking
for successful execution."""

import re
import runpy
import unittest
from os.path import dirname, join
from pathlib import Path

# --- Configuration ---
# Set this constant to the root directory of the package you want to test.
# The script will recursively search for .py files from this location.
# For example, if your code is in a 'src' folder, you'd use Path('./src')
PACKAGE_ROOT = Path(join(dirname(__file__), ".."))

# --- Test Class Definition ---


@unittest.skip("Skipping this entire class because it is for dev helper code.")
class TestMainBlocks(unittest.TestCase):
    """
    A dynamic test suite that discovers and runs the __main__ block
    of Python modules.
    """


# --- Dynamic Test Generation Logic ---


def create_main_test(module_path: Path):
    """
    This is a factory function. It creates and returns a new test method
    that will execute the __main__ block of the given module_path.

    Args:
        module_path: The pathlib.Path object for the Python module to be tested.

    Returns:
        A function that serves as a test method for unittest.
    """

    def test_main(self):
        """
        Dynamically generated test method. Executes the target module's
        __main__ block and checks for successful execution.
        """
        try:
            # runpy.run_path executes the specified file as if it were
            # the main entry point of an application. This correctly sets
            # __name__ to '__main__'.
            runpy.run_path(str(module_path), run_name="__main__")
        except SystemExit as e:
            # It's common for scripts to end with sys.exit().
            # We check that the exit code is 0 or None, which signals success.
            self.assertIn(
                e.code,
                [0, None],
                f"Module '{module_path.name}' exited with non-zero status code: {e.code}",
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            # If any other exception occurs during the module's execution,
            # we fail the test and provide the exception as the reason.
            self.fail(f"Module '{module_path.name}' raised an exception during execution: {e}")

    return test_main


def discover_and_generate_tests():
    """
    Discovers all .py files with a __main__ block in the PACKAGE_ROOT
    and dynamically adds a corresponding test method to the TestMainBlocks class.
    """
    # Regular expression to find 'if __name__ == "__main__"' with variations
    # in spacing and quote types.
    main_pattern = re.compile(r"if\s+__name__\s*==\s*['\"]__main__['\"]:")

    if not PACKAGE_ROOT.is_dir():
        print(
            f"Warning: The specified PACKAGE_ROOT '{PACKAGE_ROOT}' "
            "does not exist. No tests will be generated."
        )
        return

    # Recursively find all .py files in the specified directory
    for py_file in PACKAGE_ROOT.rglob("*.py"):
        # Exclude files or directories that start with "test" to prevent infinite loops
        # or trying to run coverage on test files themselves.
        relative_path = py_file.relative_to(PACKAGE_ROOT)
        if any(
            part.startswith("test")
            or part.startswith(".venv")
            or part.startswith("egpseed")
            or part.startswith("problems")
            for part in relative_path.parts
        ):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            # Check if the file contains the main block pattern
            if main_pattern.search(content):
                # Sanitize the file path to create a valid Python method name
                # Replaces path separators and file extension with underscores
                test_name = "test_main_of_" + str(relative_path).replace("\\", "_").replace(
                    "/", "_"
                ).replace(".", "_")

                # Create the actual test method using our factory
                test_method = create_main_test(py_file)

                # Add the dynamically created test method to our TestCase class
                setattr(TestMainBlocks, test_name, test_method)
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Warning: Could not process file '{py_file}'. Reason: {e}")


# --- Main Execution ---

# Run the discovery and generation process when this module is imported
discover_and_generate_tests()

# This allows the test to be run directly from the command line
if __name__ == "__main__":
    # You can set up a dummy 'src' directory with some files to see this work
    # Example setup:
    # src/
    # ├── app.py  (with a __main__ block)
    # └── utils/
    #     └── helper.py (with a __main__ block)

    # To run: python tests/test_all_main_blocks.py
    unittest.main(verbosity=2)
