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
from egppy.worker.executor.context_writer import write_context_to_file
from egppy.worker.executor.execution_context import ExecutionContext

# Constants
PSQL_CDN_PRP_MSK = ([], ["PsqlBigInt"], "properties_codon_mask")
PSQL_PRP_COLUMN = ([], ["PsqlBigInt"], "properties")
PSQL_BITWISE_AND = (["PsqlIntegral"], ["PsqlIntegral"], "&")
PSQL_EQUALS = (["PsqlType"], ["PsqlBool"], "=")
PSQL_0_BIGINT = ([], ["PsqlBigInt"], "0::BIGINT")
PSQL_ORDERBY_RND = ([], ["PsqlFragmentOrderBy"], "ORDER BY RANDOM")
PSQL_WHERE = (["PsqlBool"], ["PsqlFragmentWhere"], "WHERE")
PSQL_2x64_TO_IGRL = (
    ["PsqlBigInt"],
    ["PsqlIntegral"],
    "raise_if_not_both_instances_of(PsqlBigInt, PsqlBigInt, PsqlIntegral)",
)
PSQL_IGRL_TO_64 = (
    ["PsqlIntegral"],
    ["PsqlBigInt"],
    "raise_if_not_instance_of(PsqlIntegral, PsqlBigInt)",
)
GPI_SELECT_GC = (["PsqlFragmentOrderBy", "PsqlFragmentWhere"], ["GGCode"], "select")
SCA_GC = (["GGCode"], ["EGCode"], "sca")
PERFECT_STACK = (["GGCode"], ["EGCode"], "perfect_stack")


# Dictionary of primitive GCs
# This is empty on initialization and populated on first use
primitive_gcs: dict[str, GCABC] = {}


def create_primitive_gcs():
    """Create the primitive genetic codes and store them in the primitive_gcs dict."""
    if primitive_gcs:
        return

    # Initialize the Gene Pool Interface
    gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)

    # Load the primitive genetic code signatures from the gene pool
    primitive_gcs["PSQL_CDN_PRP_MSK"] = gpi[find_codon_signature(*PSQL_CDN_PRP_MSK)]
    primitive_gcs["PSQL_PRP_COLUMN"] = gpi[find_codon_signature(*PSQL_PRP_COLUMN)]
    primitive_gcs["PSQL_BITWISE_AND"] = gpi[find_codon_signature(*PSQL_BITWISE_AND)]
    primitive_gcs["PSQL_EQUALS"] = gpi[find_codon_signature(*PSQL_EQUALS)]
    primitive_gcs["PSQL_0_BIGINT"] = gpi[find_codon_signature(*PSQL_0_BIGINT)]
    primitive_gcs["PSQL_ORDERBY_RND"] = gpi[find_codon_signature(*PSQL_ORDERBY_RND)]
    primitive_gcs["PSQL_WHERE"] = gpi[find_codon_signature(*PSQL_WHERE)]
    primitive_gcs["PSQL_2x64_TO_IGRL"] = gpi[find_codon_signature(*PSQL_2x64_TO_IGRL)]
    primitive_gcs["PSQL_IGRL_TO_64"] = gpi[find_codon_signature(*PSQL_IGRL_TO_64)]
    primitive_gcs["GPI_SELECT_GC"] = gpi[find_codon_signature(*GPI_SELECT_GC)]
    primitive_gcs["SCA_GC"] = gpi[find_codon_signature(*SCA_GC)]
    primitive_gcs["PERFECT_STACK"] = gpi[find_codon_signature(*PERFECT_STACK)]

    # Create an execution context to do the work.
    ec = ExecutionContext(gpi, wmc=True)
    ec.write_executable(primitive_gcs["PERFECT_STACK"])
    big_int_and_gc = ec.execute(
        primitive_gcs["PERFECT_STACK"]["signature"],
        (primitive_gcs["PSQL_2x64_TO_IGRL"], primitive_gcs["PSQL_BITWISE_AND"]),
    )
    write_context_to_file(ec)
    print(f"BigInt AND GC signature: {big_int_and_gc[1].hex()}")


if __name__ == "__main__":
    create_primitive_gcs()
