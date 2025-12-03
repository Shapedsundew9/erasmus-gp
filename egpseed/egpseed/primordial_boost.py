"""
Primordial boost — initialize simple physical genetic codes.

This module provides helper routines to "bootstrap" evolution by constructing
primitive genetic codes that mirror pre-defined Python implementations.

There is a circular dependency problem when starting evolution in EGP. To construct
genetic codes, you need mutations, which are themselves genetic codes. For
example, a simple stacking mutation takes one codon and stacks it on another.
This requires finding codons with compatible interfaces (a selector), performing
the stacking operation (a mutation), and creating a wrapper genetic code. In nature,
this evolutionary bootstrap took eons through random combinations of primitives.
However, we don't have that luxury.

Primordial boost leverages Python implementations of fundamental physcial genetic
codes (mutations & selectors) like perfect_stack() and harmony(). These functions
are then used as mutations to create EGP GC implementations of
primitive functions including themselves (!), effectively "seeding" the
evolutionary process.

This module is intended for use during early development stages to avoid waiting
for chance discoveries.
"""

from egpcommon.codon_dev_load import find_codon_signature
from egpcommon.common import SHAPEDSUNDEW9_UUID
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.physics.runtime_context import RuntimeContext
from egppy.worker.executor.context_writer import OutputFileType, write_context_to_file
from egppy.worker.executor.execution_context import ExecutionContext
from egppy.worker.executor.fw_config import FWConfig
from egpseed.primordial_python import harmony_py, perfect_stack_py

# Primitive GC signature definitions
# Maps GC names to their (input_types, output_types, name) signatures
_GC_SIGNATURES: dict[str, tuple] = {
    "PSQL_CDN_PRP_MSK": ([], ["PsqlBigInt"], "properties_codon_mask"),
    "PSQL_PRP_COLUMN": ([], ["PsqlBigInt"], "properties"),
    "PSQL_BITWISE_AND": (["PsqlIntegral"], ["PsqlIntegral"], "&"),
    "PSQL_EQUALS": (["PsqlType"], ["PsqlBool"], "="),
    "PSQL_0_BIGINT": ([], ["PsqlBigInt"], "0::BIGINT"),
    "PSQL_ORDERBY_RND": ([], ["PsqlFragmentOrderBy"], "ORDER BY RANDOM"),
    "PSQL_WHERE": (["PsqlBool"], ["PsqlFragmentWhere"], "WHERE"),
    "PSQL_2x64_TO_IGRL": (
        ["PsqlBigInt"],
        ["PsqlIntegral"],
        "raise_if_not_instance_of(ix, tx)",
    ),
    "PSQL_IGRL_TO_64": (
        ["PsqlIntegral"],
        ["PsqlBigInt"],
        "raise_if_not_instance_of(i0, t0)",
    ),
    "PSQL_2x64_TO_TYPE": (
        ["PsqlBigInt"],
        ["PsqlType"],
        "raise_if_not_instance_of(ix, tx)",
    ),
    "GPI_SELECT_GC": (["PsqlFragmentOrderBy", "PsqlFragmentWhere"], ["GGCode"], "select"),
    "CONNECT_ALL": (["EGCode"], ["GGCode"], "connect_all"),
    "CUSTOM_PGC": ([], [], "custom"),
}

# Dictionary of codon GCs
# This is empty on initialization and populated on first use
codons: dict[str, GCABC] = {}


def _harmony_connect(ec: ExecutionContext, rtctxt: RuntimeContext, gc1: GCABC, gc2: GCABC) -> GCABC:
    """
    Create a harmony between two GCs and connect all outputs.

    Args:
        ec: Execution context to use.
        rtctxt: Runtime context to use.
        gc1: First genetic code.
        gc2: Second genetic code.

    Returns:
        Connected genetic code result.
    """
    egc = harmony_py(rtctxt, gc1, gc2)
    return ec.execute(codons["CONNECT_ALL"], (egc,))


def _stack_connect(ec: ExecutionContext, rtctxt: RuntimeContext, gc1: GCABC, gc2: GCABC) -> GCABC:
    """
    Stack two GCs and connect all outputs.

    Args:
        ec: Execution context to use.
        rtctxt: Runtime context to use.
        gc1: First genetic code (bottom of stack).
        gc2: Second genetic code (top of stack).

    Returns:
        Connected genetic code result.
    """
    egc = perfect_stack_py(rtctxt, gc1, gc2)
    return ec.execute(codons["CONNECT_ALL"], (egc,))


def load_codons(gpi: GenePoolInterface) -> None:
    """Loadf the codons that will be used and store them in the codons dict."""
    if codons:
        return

    # Load the primitive genetic code signatures from the gene pool
    for name, signature in _GC_SIGNATURES.items():
        codons[name] = gpi[find_codon_signature(*signature)]


def nrtc(ec: ExecutionContext) -> RuntimeContext:
    """Create a default runtime context for primordial boost operations."""
    return RuntimeContext(ec.gpi, creator=SHAPEDSUNDEW9_UUID)


def build_custom_gcs() -> ExecutionContext:
    """Manually create genetic codes that have the same function as the python code
    equivilents in egpseed/egpseed/primordial_python.py. The GC's are persisted in the
    Gene Pool for later use. Re-using existing GC's or sub-GC's is preferred to creating
    new ones, so the creation order does matter."""

    # TODO: Need to name these GC's in the meta data so they can be found later.
    # Tidying up the meta data structure needs to be part of that.

    # Create an execution context to do the work.
    gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)
    load_codons(gpi)
    ec = ExecutionContext(gpi, wmc=True)

    # Genetic code creation (in order)
    # NOTE: It is essential that each of these functions GC's are proven to be functionally
    # equivalent to their python counterparts. This can be done by writing test cases that
    # compare the output of the python function to the output of the GC function for
    # a variety of inputs. Since random selection of a GC from the gene pool cannot be
    # guaranteed to select the same GC each time, the tests should focus on the functional
    # equivalence rather than exact GC identity or mock the database queries verify the SQL
    # generated by the GC's and then return the GC that was selected by the python version.
    # Python versions make use of the RuntimeContext.debug_data member to store intermediate
    # results.

    # The random codon selector GC build is heavily commented as an example of how to
    # build these primordial boost GC's.
    random_codon_selector_gc(ec)

    # Return the execution context for inspection if needed.
    return ec


def random_codon_selector_gc(ec: ExecutionContext) -> None:
    """Build a genetic code with the functional equivilence of random_codon_selector_py()."""

    # Can reuse the RuntimeContext for all operations the data is the same for each operation
    # and no debug data is collected.
    rtctxt = nrtc(ec)

    # A GC is built up in stages, each stage creating
    # a temporary GC that is used in the next stage. The final GC is written
    # to the execution context which adds it to the Gene Pool and makes it available
    # for later execution.

    # All GC's (which includes all codons) are stored in the Gene Pool Postgres database so that
    # they can be queried at runtime on any criteria. The GC table is initially populated
    # with the codons defined in egppy/egppy/data/codons.json and
    # egppy/egppy/data/meta_codons.json which can be inspected to find suitable codons to use.
    # The codons dict defined at the top of this module is populated with
    # commonly used codons and can be extended with more as needed by adding to the
    # _GC_SIGNATURES dict.

    # The random codon selector GC is built up in stages as follows:
    # 1. Get the properties codon mask (PSQL_CDN_PRP_MSK) and the properties column (PSQL_PRP_COLUMN)
    #    codons and package them into a harmony GC (tmp1_ggc).
    # 2. Get the PSQL_2x64_TO_IGRL codon which type casts a BIGINT to an Integral and the
    #    PSQL_BITWISE_AND codon which performs a bitwise AND operation on two Integrals and
    #    stack them to create a GC that takes 2x BIGINT and does a bitwise and on it to return an
    #    Integral(tmp2_ggc).
    # 3. Stack tmp1_ggc and tmp2_ggc to create a GC that takes the properties codon mask
    #    and properties column, does a bitwise AND on them and returns an Integral (tmp3_ggc).
    # 4. Take the Integral output of tmp3_ggc and type cast it back to a BIGINT using the
    #    PSQL_IGRL_TO_64 codon (tmp3a_ggc).
    # 5. Create a GC that returns the constant BIGINT 0 using the PSQL_0_BIGINT codon (tmp3b_ggc).
    # 6. Get the PSQL_2x64_TO_TYPE codon which type casts a BIGINT to a Type and the
    #    PSQL_EQUALS codon which compares two Types for equality and stack them to create a GC
    #    that takes 2x BIGINT and compares them for equality to return a Bool (tmp3c_ggc).
    # 7. Stack tmp3b_ggc and tmp3c_ggc to create a GC that compares the BIGINT 0 with the
    #    BIGINT output of tmp3a_ggc for equality to return a Bool (tmp3d_ggc).
    # 8. Stack tmp3d_ggc with the PSQL_WHERE codon to create a GC that takes a Bool (result of
    #    the expression) and returns a PSQL WHERE fragment that can be used in a PSQL query
    #    (tmp4_ggc).
    # 9. Create a harmony GC that combines tmp4_ggc with the PSQL_ORDERBY_RND codon to create a
    #    GC that provides both the WHERE fragment and ORDER BY RANDOM fragment (tmp5_ggc).
    # 10. Finally, stack tmp5_ggc with the GPI_SELECT_GC codon to create the final GC that
    #     selects a random codon from the gene pool based on the properties codon mask
    #     and properties column (sggc).
    # 11. Write the final GC to the execution context which adds it to the Gene Pool.
    tmp1_ggc = _harmony_connect(ec, rtctxt, codons["PSQL_CDN_PRP_MSK"], codons["PSQL_PRP_COLUMN"])
    tmp2_ggc = _stack_connect(ec, rtctxt, codons["PSQL_2x64_TO_IGRL"], codons["PSQL_BITWISE_AND"])
    tmp3_ggc = _stack_connect(ec, rtctxt, tmp1_ggc, tmp2_ggc)
    tmp3a_ggc = _stack_connect(ec, rtctxt, tmp3_ggc, codons["PSQL_IGRL_TO_64"])
    tmp3b_ggc = _harmony_connect(ec, rtctxt, tmp3a_ggc, codons["PSQL_0_BIGINT"])
    tmp3c_ggc = _stack_connect(ec, rtctxt, codons["PSQL_2x64_TO_TYPE"], codons["PSQL_EQUALS"])
    tmp3d_ggc = _stack_connect(ec, rtctxt, tmp3b_ggc, tmp3c_ggc)
    tmp4_ggc = _stack_connect(ec, rtctxt, tmp3d_ggc, codons["PSQL_WHERE"])
    tmp5_ggc = _harmony_connect(ec, rtctxt, tmp4_ggc, codons["PSQL_ORDERBY_RND"])
    sggc = _stack_connect(ec, rtctxt, tmp5_ggc, codons["GPI_SELECT_GC"])
    ec.write_executable(sggc)


if __name__ == "__main__":
    ectxt: ExecutionContext = build_custom_gcs()
    fwconfig = FWConfig(hints=True, lean=False, inline_sigs=True)
    write_context_to_file(ectxt, "temp.md", fwconfig=fwconfig, oft=OutputFileType.MARKDOWN)
