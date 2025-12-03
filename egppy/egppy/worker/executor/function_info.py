"""
FunctionInfo class for the function information in the execution context.
This class is used to store the information about the executable function for the GC.
"""

from dataclasses import dataclass
from typing import Callable, Sequence

from egppy.genetic_code.ggc_class_factory import GCABC, NULL_GC


# For GC's with no executable (yet)
def NULL_EXECUTABLE(_: tuple) -> tuple:  # pylint: disable=invalid-name
    """The Null Exectuable. Should never be executed."""
    raise RuntimeError("NULL_EXECUTABLE should never be executed.")


@dataclass(slots=True)
class FunctionInfo:
    """The information for a function in the execution context."""

    executable: Callable
    global_index: int
    line_count: int
    # TODO: This keeps the GCABC hanging around. It should not. Should be pulled from
    # the GPI everytime it is accessed to reduce memory usage.
    gc: GCABC

    def name(self) -> str:
        """Return the function name."""
        return f"f_{self.global_index:x}"

    def call_str(self, ivns: Sequence[str]) -> str:
        """Return the function call string using the map of input variable names."""
        if len(ivns):
            return f"{self.name()}(({', '.join(f'{ivn}' for ivn in ivns)},))"
        return f"{self.name()}()"


NULL_FUNCTION_MAP: FunctionInfo = FunctionInfo(NULL_EXECUTABLE, -1, 0, NULL_GC)
# The NULL_FUNCTION_MAP is used to indicate that the function is not set.
