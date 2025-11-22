"""Function write configuration class."""

from dataclasses import dataclass


@dataclass(slots=True)
class FWConfig:
    """Configuration class for function writing.
    By default the configuration is for lean & optimised code.
    """

    # Enable type hinting in function definitions
    hints: bool = False
    # Enable debug (relatively light)
    debug: bool = False
    # Enable deep debug (very heavy)
    deep_debug: bool = False
    # Inline signature comments for each line (least significant 32 bits of the signature)
    inline_sigs: bool = False
    # Enable lean mode to remove all comments, docstrings and pretty spacing.
    # This saves memory in the execution_context.
    lean: bool = True

    # The following attributes add a comment at the top of the function
    # with the specified information (if lean is False).
    # The SHA256 signature of the Genetic Code (GC)
    signature: bool = True
    # The date & time the GC was created (UTC)
    created: bool = True
    # The GC license summary
    license: bool = True
    # The UUID & short name of the creator
    creator: bool = True
    # The generation of the GC
    generation: bool = True
    # The version of the GC
    version: bool = True
    # Write out the optimisations performed on the function (defined below)
    optimisations: bool = False

    # The following attributes enable / disable code optimisations.
    # Constant evaluation: Any constant expressions in the function are evaluated
    # prior to write time and the code is replaced with the result.
    const_eval: bool = True
    # Result cache: Any function calls that are deterministic and do not have side effects
    # are cached. If the function is called with the same arguments, the cached
    # result is returned instead of calling the function again.
    # NOTE: This optimization is only applied if the GC property `consider_cache` is True.
    result_cache: bool = True
    # Common subexpression elimination: Any common subexpressions (that are
    # deterministic & do not have side effects) are evaluated once and the result
    # is used in place of the subexpression.
    cse: bool = True
    # Simplification uses symbolic regression to simplify the code.
    simplification: bool = True
    # Note that dead code elimination is always performed.


FWCONFIG_DEFAULT = FWConfig()
