"""Function write configuration class."""

from dataclasses import dataclass


@dataclass
class FWConfig:
    """Configuration class for function writing."""

    # Enable type hinting in function definitions
    hints: bool = True

    # The following attributes add a comment at the top of the function
    # with the specified information.
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
    # Common subexpression elimination: Any common subexpressions (that are
    # deterministic & do not have side effects) are evaluated once and the result
    # is used in place of the subexpression.
    cse: bool = True
    # Simplification uses symbolic regression to simplify the code.
    simplification: bool = True
    # Note that dead code elimination is always performed.


FWCONFIG_DEFAULT = FWConfig()
