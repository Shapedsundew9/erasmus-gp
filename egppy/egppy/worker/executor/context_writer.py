"""File writer for execution contexts.

This capability is not part of the ExecutionContext class as it requires
a regeneration of the node & code graphs that make the code (even) more
complex. This is a rare and one off operation and so it is better to keep this
in a separate module to avoid cluttering the ExecutionContext class.

The EC being written is not modified in any way. Its configuration
is copied into a new temporary EC and the code is generated from that. A bypass has
been added to the EC.create_code_graphs() method to avoid creating all the executable
functions which would not ben needed & use a lot of memory. With little
persistence needed the pretty file can be created in a streaming-like fashion.

Note that this does have some consequences: The variable and function numbers will
be different. This is because the execution context may (will like have) evolved
over time and the global index counter will reflect that.
"""

from datetime import datetime
from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from tempfile import NamedTemporaryFile

from egpcommon.egp_logo import header_lines
from isort import code as isort_imports

from egppy.worker.executor.execution_context import ExecutionContext

# Header
# from pyfiglet import figlet_format
# print(figlet_format("EGP Exec Context"))
HEADER: str = """
 _____ ____ ____    _____                  ____            _            _   
| ____/ ___|  _ \\  | ____|_  _____  ___   / ___|___  _ __ | |_ _____  _| |_
|  _|| |  _| |_) | |  _| \\ \\/ / _ \\/ __| | |   / _ \\| '_ \\| __/ _ \\ \\/ / __|
| |__| |_| |  __/  | |___ >  <  __/ (__  | |__| (_) | | | | ||  __/>  <| |_
|_____\\____|_|     |_____/_/\\_\\___|\\___|  \\____\\___/|_| |_|\\__\\___/_/\\_\\__|
"""


def write_context_to_file(ec: ExecutionContext, filepath: str = "") -> None:
    """Write the execution context to a file.
    The file is nicely formatted and contains everything needed to execute GC
    functions. It also includes license information and a signature of authenticity.

    Args
    ----
        ec: ExecutionContext: The execution context to write.
        filepath: str: The file to write to. If empty, a temporary file is created.
    """
    format_file_with_black(_context_writer(ec, filepath))


def _context_writer(ec: ExecutionContext, filepath: str | Path) -> str:
    """Write the execution context using a specified writer."""

    _filepath = filepath if filepath else NamedTemporaryFile(suffix=".py", delete=False).name
    with open(_filepath, mode="w", encoding="utf-8") as f:
        # File name
        filename = f.name

        # First write out the module header
        f.write(f'"""EGP Execution Context generated on {datetime.now().isoformat()}"""\n')
        f.write(HEADER.replace("\n", "\n# ") + "\n#")
        f.write("\n# ".join(header_lines(attr="bw")))
        f.write("\n")

        # Now the imports
        f.write(isort_imports("\n".join(str(impt) for impt in ec.imports)))
        f.write("\n\n")

        # Finally the function definitions
        nec = ExecutionContext(ec.line_limit())
        for func in ec.function_map.values():
            for node in nec.create_graphs(func.gc, False)[1]:
                # Write the function definition
                f.write(nec.function_def(node, False))
                f.write("\n")
    return filename


def format_file_with_black(filepath: str | Path) -> None:
    """
    Formats a Python file using the 'black' formatter and saves the result safely.

    Args:
        filepath: Path (string or pathlib.Path) to the Python file to format.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If 'black' is not installed or found in PATH, if 'black'
                      fails during formatting (e.g., due to syntax errors in
                      the input file), or if there's an issue writing the
                      output file.
        OSError: If the directory structure for the output file cannot be created.

    Security Note:
        This function uses subprocess.run() without shell=True, which is generally
        safe from shell injection vulnerabilities when arguments are passed as a list.
    """
    input_path = Path(filepath)

    # 1. Check if 'black' executable is available
    black_executable = which("black")
    if not black_executable or black_executable is None:
        raise RuntimeError(
            "The 'black' executable was not found in your system's PATH. "
            "Please ensure black is installed (e.g., 'pip install black') "
            "and accessible in your environment."
        )

    # 2. Check if the input file exists
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # 3. Prepare the command to run black
    #    We run black with '--quiet' to suppress status messages on stderr
    #    and provide the input file path. Black will print the formatted
    #    code to standard output when run this way without modifying the file.
    command: list[str] = [black_executable, "--quiet", str(input_path)]

    # 4. Run black as a subprocess
    try:
        # Run the command, capture stdout/stderr, decode as text (UTF-8 common for code)
        # check=False prevents raising CalledProcessError automatically on non-zero exit
        process: CompletedProcess[str] = run(
            command,
            capture_output=True,
            text=True,
            check=False,  # We will check the return code manually
            encoding="utf-8",  # Specify encoding for text mode
        )

        # 5. Check if black encountered an error
        if process.returncode != 0:
            # Black failed (e.g., syntax error in input file, internal black error)
            error_message = (
                f"Black formatting failed for {input_path} "
                f"(exit code {process.returncode}).\n"
                f"Potential issues include syntax errors in the input file.\n"
                f"Black's stderr:\n{process.stderr}"
            )
            raise RuntimeError(error_message)

    except FileNotFoundError as exc:
        # This specific error could occur if the black_executable path
        # becomes invalid between the shutil.which check and subprocess.run
        raise RuntimeError(
            f"Failed to execute black. Ensure '{black_executable}' is valid."
        ) from exc
    except Exception as e:
        # Catch other potential subprocess errors
        raise RuntimeError(f"An unexpected error occurred while running black: {e}") from e
