"""Methods for meta codons.

Meta codons are used to manipulate the implementation of the genetic code
functions. They have no effect on the genetic code function but are used
to instrument for profiling or monitoring purposes, or to provide manipulation
of EGP's type management system.
"""

from typing import Any

from egpcommon.egpcommon.parallel_exceptions import create_parallel_exceptions

# Create a module with parallel exceptions for meta codons
MetaCodonExceptionModule = create_parallel_exceptions(
    prefix="MetaCodon", module_name="egppy.worker.executor.meta_codons"
)

# Find some common exceptions in the module
MetaCodonError = MetaCodonExceptionModule.get_parallel_equivalent(Exception)
MetaCodonValueError = MetaCodonExceptionModule.get_parallel_equivalent(ValueError)
MetaCodonTypeError = MetaCodonExceptionModule.get_parallel_equivalent(TypeError)


def raise_if_not_instance_of(obj: Any, t: type) -> None:
    """Raise an error if the object is not an instance of the given types."""
    if not isinstance(obj, t):
        raise MetaCodonTypeError(f"Expected {t}, got {type(obj)} instead.")


if __name__ == "__main__":  # pragma: no cover
    # Example usage of the meta codon exceptions
    try:
        raise_if_not_instance_of(42, str)
    except MetaCodonTypeError as e:
        print(f"Caught a meta codon type error: {e}")
    else:
        print("No error raised, object is of the correct type.")
    finally:
        print("Meta codon example execution completed.")
