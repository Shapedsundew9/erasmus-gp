"""
Primordial boost — initialize simple physical genetic codes.

This module provides helper routines used to "kick start" evolution
by constructing primitive genetic codes and applying basic
selection and mutation operations. It is intended for use during the
early stages of development to save waiting around for chance discoveries.
"""

from egpcommon.codon_dev_load import find_codon_signature
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.worker.executor.context_writer import OutputFileType, write_context_to_file
from egppy.worker.executor.execution_context import ExecutionContext
from egppy.worker.executor.fw_config import FWConfig

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
        "raise_if_not_both_instances_of(PsqlBigInt, PsqlBigInt, PsqlIntegral)",
    ),
    "PSQL_IGRL_TO_64": (
        ["PsqlIntegral"],
        ["PsqlBigInt"],
        "raise_if_not_instance_of(PsqlIntegral, PsqlBigInt)",
    ),
    "PSQL_2x64_TO_TYPE": (
        ["PsqlBigInt"],
        ["PsqlType"],
        "raise_if_not_both_instances_of(PsqlBigInt, PsqlBigInt, PsqlType)",
    ),
    "GPI_SELECT_GC": (["PsqlFragmentOrderBy", "PsqlFragmentWhere"], ["GGCode"], "select"),
    "SCA_GC": (["GGCode"], ["EGCode"], "sca"),
    "PERFECT_STACK": (["GGCode"], ["EGCode"], "perfect_stack"),
    "HARMONY_GC": (["GGCode"], ["EGCode"], "harmony"),
    "CONNECT_ALL": (["EGCode"], ["GGCode"], "connect_all"),
}

# Dictionary of codon GCs
# This is empty on initialization and populated on first use
codons: dict[str, GCABC] = {}


def _harmony_connect(ec: ExecutionContext, gc1: GCABC, gc2: GCABC) -> GCABC:
    """
    Create a harmony between two GCs and connect all outputs.

    Args:
        ec: Execution context to use.
        gc1: First genetic code.
        gc2: Second genetic code.

    Returns:
        Connected genetic code result.
    """
    egc = ec.execute(codons["HARMONY_GC"], (gc1, gc2))
    return ec.execute(codons["CONNECT_ALL"], (egc,))


def _stack_connect(ec: ExecutionContext, gc1: GCABC, gc2: GCABC) -> GCABC:
    """
    Stack two GCs and connect all outputs.

    Args:
        ec: Execution context to use.
        gc1: First genetic code (bottom of stack).
        gc2: Second genetic code (top of stack).

    Returns:
        Connected genetic code result.
    """
    egc = ec.execute(codons["PERFECT_STACK"], (gc1, gc2))
    return ec.execute(codons["CONNECT_ALL"], (egc,))


def create_primitive_gcs():
    """Create the primitive genetic codes and store them in the primitive_gcs dict."""
    if codons:
        return

    # Initialize the Gene Pool Interface
    gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)

    # Load the primitive genetic code signatures from the gene pool
    for name, signature in _GC_SIGNATURES.items():
        codons[name] = gpi[find_codon_signature(*signature)]

    # Create an execution context to do the work.
    ec = ExecutionContext(gpi, wmc=True)

    # Stack codons to create a selector GC
    #   1. Convert the Integral input interface of the bitwise & codon to BigInt
    #   2. Make a harmony from the codon property mask and the properties column codon
    #   3. Stack #2 on #1 to make a filter condition for the WHERE clause
    #   4.

    tmp1_ggc = _harmony_connect(ec, codons["PSQL_CDN_PRP_MSK"], codons["PSQL_PRP_COLUMN"])
    tmp2_ggc = _stack_connect(ec, codons["PSQL_2x64_TO_IGRL"], codons["PSQL_BITWISE_AND"])
    tmp3_ggc = _stack_connect(ec, tmp1_ggc, tmp2_ggc)
    tmp3a_ggc = _stack_connect(ec, tmp3_ggc, codons["PSQL_IGRL_TO_64"])
    tmp3b_ggc = _harmony_connect(ec, tmp3a_ggc, codons["PSQL_0_BIGINT"])
    tmp3c_ggc = _stack_connect(ec, codons["PSQL_2x64_TO_TYPE"], codons["PSQL_EQUALS"])
    tmp3d_ggc = _stack_connect(ec, tmp3b_ggc, tmp3c_ggc)
    tmp4_ggc = _stack_connect(ec, tmp3d_ggc, codons["PSQL_WHERE"])
    tmp5_ggc = _harmony_connect(ec, tmp4_ggc, codons["PSQL_ORDERBY_RND"])
    segc = ec.execute(codons["PERFECT_STACK"], (tmp5_ggc, codons["GPI_SELECT_GC"]))
    sggc = codons["SELECTOR_GC"] = ec.execute(codons["CONNECT_ALL"], (segc,))
    ec.write_executable(sggc)
    fwconfig = FWConfig(hints=True, lean=False, inline_sigs=True)
    write_context_to_file(ec, "primitive_gcs.md", fwconfig=fwconfig, oft=OutputFileType.MARKDOWN)
    print(f"Primitive genetic codes created: {ec.execute(sggc, tuple())}")


if __name__ == "__main__":
    create_primitive_gcs()
