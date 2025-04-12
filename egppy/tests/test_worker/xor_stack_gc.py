"""Creates genetic codes for low level testsing.

Prior to having a functional eveolution pipeline the genetic codes for unit level testing are
created here. The genetic codes are not functionaly complex (a stack of XORs and random ints)
but they are complex enough to test the executor. The properties of the created GC's are:
    - Executable
    - Reproducible - that they can be reliably recreated
    - Deterministic - that they always produce the same output from the same input
    - Have a minimum of 2 codons
    - Have a maximum of 256 inputs (can create more but should be a negative test)
    - Have a maximum of 256 outputs (can create more but should be a negative test)
    - Random - lots of variety
    - Sensitive - errors in construction will cause validation / consistency errors
The implementation chosen is a stack of XORs and random ints. The stack is created by randomly
by stacking the primitive codons. XORs are chosen because they are simple and have a clear
relationship between inputs and outputs. The random ints are chosen because they are simple,
deterministic with a seed and require correct order execution to produce the correct output.
"""

from json import dump
from random import choice, random, randint, seed, shuffle
from tempfile import NamedTemporaryFile
from time import time

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger, enable_debug_logging
from egpcommon.common import bin_counts
from egpcommon.properties import BASIC_ORDINARY_PROPERTIES

from egppy.gc_types.gc import GCABC, mermaid_key
from egppy.gc_types.ggc_class_factory import GGCDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM
from egppy.worker.gc_store import GGC_CACHE
from egppy.worker.executor.execution_context import FunctionInfo, GCNode, ExecutionContext


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
enable_debug_logging()


# Set the seed for reproducibility
seed(0)


# Python int type as an EGP type
INT_T = ["int"]

# New GC consistency assessment sample rate
# Slows down the code but is useful for debugging
# Set to 0.0 to disable or a fractional value for random sampling.
CONSISTENCY_SAMPLE = 1.0

# Right shift codon
rshift_gc = GGC_CACHE[
    bytes.fromhex("3ba3b63560abc42aa8088d5655a53d973c50fa0d3edacdfc801053b7a26e6923")
]
# Literal 1 codon
literal_1_gc = GGC_CACHE[
    bytes.fromhex("ebba2a300e27e8b73a8e4c2807ad43273534ad9ae385e9a21cc1e7d9c3d8abd0")
]
# This is the Integral type XOR but it does not matter for this
# b'\x00\xaf\x97\xc8\x88\xef\x12\xa4V\xda\xad\x80!\xf2\x1cpLBY\xa6\xe9TiY\x83\xb3\xf9=I\xdd\x82\x90'
xor_gc = GGC_CACHE[
    bytes.fromhex("00af97c888ef12a456daad8021f21c704c4259a6e954695983b3f93d49dd8290")
]
# b'e\x864d\xea\xc5\x14!a>pS)\xddv\xfczs\xfb\xdbI\xbe\xa1\x18f!\xc5\xd2\xe00\xd5<'
getrandbits_gc = GGC_CACHE[
    bytes.fromhex("65863464eac51421613e705329dd76fc7a73fbdb49bea1186621c5d2e030d53c")
]
# b'\xb3Y\x86s\x01J\x84\xbc\xca\xa4!\xa8\xebx\xe4\x10\x9b\x07\x8f,s\x98\xefO:\xec\x1e\x1d\xef\x8cu.'
sixtyfour_gc = GGC_CACHE[
    bytes.fromhex("b3598673014a84bccaa421a8eb78e4109b078f2c7398ef4f3aec1e1def8c752e")
]
# b'R\xb6j\xfd\x16\xa3\x10!\x91|\x90pdI7iW"\x044d+\xfc2\xc2`\xbf\x94~\x7f\xd8i'
custom_pgc = GGC_CACHE[
    bytes.fromhex("52b66afd16a31021917c90706449376957220434642bfc32c260bf947e7fd869")
]

# random_long_gc signature:
# b'\xd1d\xb9=\x0b\xbeB\x97Go\xea<\x9c\xd6\xbc-\xa4\x8cn\xcc|C\xe8\xa7\x03Z\x15\xfa\xb2\xf3\x1c\n'
# 'd164b93d0bbe4297476fea3c9cd6bc2da48c6ecc7c43e8a7035a15fab2f31c0a'
random_long_gc = GGCDict(
    {
        "ancestora": sixtyfour_gc,
        "ancestorb": getrandbits_gc,
        "created": "2025-03-29 22:05:08.489847+00:00",
        "gca": sixtyfour_gc,
        "gcb": getrandbits_gc,
        "graph": {
            "A": [],
            "B": [["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "properties": BASIC_ORDINARY_PROPERTIES,
    }
)
random_long_gc.consistency()
GGC_CACHE[random_long_gc["signature"]] = random_long_gc


# Shift right by one GC function. Note that this function needs to
# be defined with the format and naming convention of the GC function
# i.e. inputs are encapsulated in a tuple (even if there is only one)
# and the output is a tuple (even if there is only one). The function
# name must end in an 8 character unsigned hexadecimal value.
def f_7fffffff(i: tuple[int]) -> int:
    """Shift right by one."""
    return i[0] >> 1


# rshift_1_gc signature:
# b'\x94\xedS\xe0/Kr*\x14\xcf\xb7\xe8"d\xa1\x98\xf11\xfa\xfe\xb6\xc6\xc7w)\x1e\xac*\xfb\xads\xd9'
# 94ed53e02f4b722a14cfb7e82264a198f131fafeb6c6c777291eac2afbad73d9
rshift_1_gc = GGCDict(
    {
        "ancestora": literal_1_gc,
        "ancestorb": rshift_gc,
        "created": "2025-03-29 22:05:08.489847+00:00",
        "code_depth": 2,
        "gca": literal_1_gc["signature"],  # Makes the structure of this GC unknown
        "gcb": rshift_gc,
        "generation": 2,
        "graph": {
            "A": [],
            "B": [["I", 0, ["int"]], ["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "num_codes": 3,
        "num_codons": 2,
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "properties": BASIC_ORDINARY_PROPERTIES,
    }
)
rshift_1_gc.consistency()
GGC_CACHE[rshift_1_gc["signature"]] = rshift_1_gc

# rshift_xor_gc signature:
# b'\x17\x01\x9dk\xb5\xc6\x90G\xd1\xce\xee\xbaO@<>\xec\xab=\x8e\xdaefV:\x83\xbc\x16Wy\xcfa'
# 17019d6bb5c69047d1ceeeba4f403c3eecab3d8eda6566563a83bc165779cf61
rshift_xor_gc = GGCDict(
    {
        "ancestora": rshift_1_gc,
        "ancestorb": xor_gc,
        "created": "2025-03-29 22:05:08.489847+00:00",
        "gca": rshift_1_gc,
        "gcb": xor_gc,
        "graph": {
            "A": [["I", 1, ["int"]]],
            "B": [["I", 0, ["int"]], ["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "properties": BASIC_ORDINARY_PROPERTIES,
    }
)
rshift_xor_gc.consistency()
GGC_CACHE[rshift_xor_gc["signature"]] = rshift_xor_gc

# one_to_two signature:
# b'\xc3\xef\xa5\xf3N\x034<\xd6\xef\xd9o\xedh\xe60\x9eH\
# xfd\x9b}8\x8f\x12\x85\x1b\x04\xc2T\x83\xe8\x85'
# c3efa5f34e03343cd6efd96fed68e6309e48fd9b7d388f12851b04c25483e885
one_to_two = GGCDict(
    {
        "ancestora": random_long_gc,
        "ancestorb": rshift_xor_gc,
        "created": "2025-03-29 22:05:08.489847+00:00",
        "gca": random_long_gc,
        "gcb": rshift_xor_gc,
        "graph": {
            "A": [],
            "B": [["I", 0, ["int"]], ["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]], ["A", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "properties": BASIC_ORDINARY_PROPERTIES,
    }
)
one_to_two.consistency()
GGC_CACHE[one_to_two["signature"]] = one_to_two
two_to_one = rshift_xor_gc


def randomrange(a: int, num: int = 0) -> list[int]:
    """Return a randomly ordered range between a and b."""
    rr = list(range(a))
    if num > 0 and num < a:
        rr = rr[:num]
    if num > 0 and num > a:
        rr.extend(rr * (num // a) + rr[: num % a])
    shuffle(rr)
    assert len(rr) == num or num == 0, f"len(rr) = {len(rr)} != num = {num}"
    return rr


def expand_gc_outputs(gc1: GCABC, gc2: GCABC) -> GCABC:
    """Expand the GC.

    Create a new GC where GCA = gc1 and GCB = gc2.
    The inputs to the new GC are the same as the inputs to gc and
    are connected directly to the inputs of GCA & GCB. The outputs
    of the new GC are the concatenation of the outputs of GCA & GCB.
    """
    gca: GCABC = gc1
    gcb: GCABC = gc2
    gcx = GGCDict(
        {
            "ancestora": gca,
            "ancestorb": gcb,
            "gca": gca,
            "gcb": gcb,
            "graph": {
                "A": [["I", i, INT_T] for i in randomrange(gca["num_inputs"])],
                "B": [["I", i, INT_T] for i in randomrange(gca["num_inputs"], gcb["num_inputs"])],
                "O": [["A", i, INT_T] for i in randomrange(gca["num_outputs"])]
                + [["B", i, INT_T] for i in randomrange(gcb["num_outputs"])],
            },
            "pgc": custom_pgc,
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gca["num_codons"] + gcb["num_codons"],
        }
    )
    if random() < CONSISTENCY_SAMPLE:
        gcx.consistency()
    return gcx


def append_gcs(gc1: GCABC, gc2: GCABC) -> GCABC:
    """Create a new GC with # of input & outputs = gc1 + gc2.

    Create a GC where GCA = gc1 and GCB = gc2.
    The inputs to the GC are the concatenation of the inputs to gc.
    The outputs of the GC are the concatenation of the outputs GCA & GCB.
    """
    gca: GCABC = gc1
    gcb: GCABC = gc2
    gcx = GGCDict(
        {
            "ancestora": gca,
            "ancestorb": gcb,
            "gca": gca,
            "gcb": gcb,
            "graph": {
                "A": [["I", i, INT_T] for i in randomrange(gca["num_inputs"])],
                "B": [["I", i + gca["num_inputs"], INT_T] for i in randomrange(gcb["num_inputs"])],
                "O": [["A", i, INT_T] for i in randomrange(gca["num_outputs"])]
                + [["B", i, INT_T] for i in randomrange(gcb["num_outputs"])],
            },
            "pgc": custom_pgc,
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gca["num_codons"] + gcb["num_codons"],
        }
    )
    if random() < CONSISTENCY_SAMPLE:
        gcx.consistency()
    return gcx


def expand_gc_inputs(gc1: GCABC, gc2: GCABC, narrow_gc: GCABC) -> GCABC:
    """Expand the GC.

    Append gc2 to gc1 as per append_gcs then stack it on the narrow to
    reduce the number of outputs back to the original number of outputs.

    This asserts that the number of inputs to the narrow GC is
    # gc1 outputs + # gc2 outputs and the number of outputs is
    # gc1 outputs.
    Connections on each interface are randomly assigned.
    """
    assert (
        gc1["num_outputs"] + gc2["num_outputs"] == narrow_gc["num_inputs"]
    ), "gc1 + gc2 outputs != narrow_gc # inputs."
    assert gc1["num_outputs"] == narrow_gc["num_outputs"], "gc1 outputs != narrow_gc outputs."
    gca: GCABC = append_gcs(gc1, gc2)
    gcb: GCABC = narrow_gc
    return stack_gcs(gca, gcb)


def stack_gcs(gc1: GCABC, gc2: GCABC) -> GCABC:
    """Stack two GC's gc1 on top of gc2.

    Create a new GC where GCA = gc1 and GCB = gc2.
    The inputs to the new GC are those of GCA.
    The outputs of the new GC are those of GCB.
    It is assumed that GCA has the same number of outputs as GCB has inputs.
    GCA's outputs are randomly connected to GCB's inputs.
    """
    assert gc1["num_outputs"] == gc2["num_inputs"], "gc1 # outputs != gc2 # inputs"
    gcx = GGCDict(
        {
            "ancestora": gc1,
            "ancestorb": gc2,
            "gca": gc1,
            "gcb": gc2,
            "graph": {
                "A": [["I", i, INT_T] for i in randomrange(gc1["num_inputs"])],
                "B": [["A", i, INT_T] for i in randomrange(gc2["num_inputs"])],
                "O": [["B", i, INT_T] for i in randomrange(gc2["num_outputs"])],
            },
            "pgc": custom_pgc,
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gc1["num_codons"] + gc2["num_codons"],
        }
    )
    if random() < CONSISTENCY_SAMPLE:
        gcx.consistency()
    return gcx


def create_gc_matrix(max_epc: int) -> dict[int, dict[int, list[GCABC]]]:
    """Create a matrix of GC's.

    Create a matrix of GC's where the maxim number of inputs and outputs
    is determined by max_epc. The matrix is a dictionary of
    dictionaries where the key is the number of inputs and the value
    is a dictionary of the number of outputs and a set of GC's.

    GC's will be created for all combinations of inputs and outputs
    1 to max_epc.

    max_epc must be >= 2

    matrix[#inputs][#outputs] = {GC1, GC2, ...}
    """
    assert max_epc >= 2, "max_epc < 2"
    max_epc = max_epc + 1
    _gcm: dict[int, dict[int, list[GCABC]]] = {
        1: {1: [stack_gcs(one_to_two, two_to_one)], 2: [one_to_two]},
        2: {1: [two_to_one]},
    }

    # Create GC's with 1 input
    for no in range(3, max_epc):
        _gcm[1][no] = [expand_gc_outputs(_gcm[1][no - 1][0], _gcm[1][1][0])]

    # Create GC's with 1 output
    for num_inputs in range(2, max_epc):
        _gcm.setdefault(num_inputs, {})[1] = [
            # Previous GC with 1 output, +1 input & +1 output, then narrow to 1 output
            expand_gc_inputs(_gcm[num_inputs - 1][1][0], _gcm[1][1][0], _gcm[2][1][0])
        ]

    # Create GC's with >2 inputs or outputs
    for num_inputs in range(2, max_epc):
        for num_outputs in range(2, max_epc):
            target_set: list[GCABC] = _gcm.setdefault(num_inputs, {}).setdefault(num_outputs, [])
            if target_set:
                continue
            num_a = randint(1, num_inputs - 1)
            num_b = num_inputs - num_a

            # Randomly choose a GCA with the right number of inputs and less than maximum
            # allowed outputs so that there is the possibility of finding an output
            # solution that meets the constraint.
            gca = choice([gc for no in _gcm[num_a] for gc in _gcm[num_a][no] if no < num_outputs])
            gcb = choice(tuple(_gcm[num_b][num_outputs - gca["num_outputs"]]))
            ngc = append_gcs(gca, gcb)
            target_set.append(ngc)
            GGC_CACHE[ngc["signature"]] = ngc
            assert ngc["num_inputs"] == num_inputs, f"ngx # inputs != {num_inputs}"
            assert ngc["num_outputs"] == num_outputs, f"ngx # outputs != {num_outputs}"
    return _gcm


def expand_gc_matrix(
    matrix: dict[int, dict[int, list[GCABC]]], limit: int
) -> dict[int, dict[int, list[GCABC]]]:
    """Expand the GC matrix with randomly constructed GC's until every ratio has limit GC's.
    Assumes that the passed GCM has at least one GC for every ratio of inputs to outputs.
    The GC's get more complex as the number of GC's for a ratio increases.
    """
    # Makesure the matrix is properly formed.
    # Use create_gc_matrix() to create a matrix.
    assert len(matrix) > 0, "gcm is empty."
    assert all(len(matrix) == len(row) for row in matrix.values()), "gcm is missing sets."
    assert all(len(s) for row in matrix.values() for s in row.values()), "gcm has empty sets."

    # The most endpoints an input or output interface can have
    max_xputs = max(matrix)
    for num_inputs in matrix:
        for num_outputs in matrix[num_inputs]:
            while len(matrix[num_inputs][num_outputs]) < limit:
                if random() < 0.5 and not (num_inputs == 1 or num_outputs == 1):
                    # Append GCs to make a new one
                    # Split the inputs and outputs to define two GC's that can be appended
                    # to make one of the size required.
                    num_ia = randint(1, num_inputs - 1)
                    num_ib = num_inputs - num_ia
                    num_oa = randint(1, num_outputs - 1)
                    num_ob = num_outputs - num_oa
                    gca = choice(matrix[num_ia][num_oa])
                    gcb = choice(matrix[num_ib][num_ob])
                    ngc = append_gcs(gca, gcb)
                else:
                    # Stack GCs to make a new one
                    # Randomly choose two GC's to stack. The number of outputs of the first
                    # GC must be the same as the number of inputs of the second GC. The
                    # number of inputs of the new GC is the number of inputs of the first GC
                    # and the number of outputs is the number of outputs of the second GC.
                    num_ia = randint(1, max_xputs)
                    gca = choice(matrix[num_inputs][num_ia])
                    gcb = choice(matrix[num_ia][num_outputs])
                    ngc = stack_gcs(gca, gcb)
                matrix[num_inputs][num_outputs].append(ngc)
                GGC_CACHE[ngc["signature"]] = ngc
    return matrix


if __name__ == "__main__":
    # Seed the random number generator for reproducibility
    start = time()
    gcm: dict[int, dict[int, list[GCABC]]] = expand_gc_matrix(create_gc_matrix(8), 10)
    print(f"GCM Elapsed time: {time() - start:.2f} seconds")
    gene_pool: list[GCABC] = [gc for ni in gcm.values() for rs in ni.values() for gc in rs]

    # Codon bin size for the histogram of generated GC sizes
    CBS = 40

    # 2 different execution contexts
    ec1 = ExecutionContext(3)
    ec2 = ExecutionContext(50)
    # Hack in pre-defined function
    ec1.function_map[rshift_1_gc["signature"]] = FunctionInfo(
        f_7fffffff, 0x7FFFFFFF, 2, rshift_1_gc
    )
    ec2.function_map[rshift_1_gc["signature"]] = FunctionInfo(
        f_7fffffff, 0x7FFFFFFF, 2, rshift_1_gc
    )

    # Create a markdown formatted file with mermaid diagrams of the GC's in the gene pool
    # A temporary file is created in the default temp directory
    with NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Genetic Codes\n\n")
        f.write(
            "Be aware that GC's may have the same Connection Graph (structure) but the top level "
            "GC may have a different connectivity resulting in a different signature.\n\n"
        )
        f.write(f"Num GC's: {len(gene_pool)}\n\n")
        f.write("```mermaid\n")
        f.write("---\n")
        f.write("config:\n")
        f.write("  xyChart:\n")
        f.write("    width: 1400\n")
        f.write("---\n")
        f.write("xychart-beta\n")
        f.write('  title "Codon Count Distribution"\n')
        codon_bin_counts = bin_counts([gc["num_codons"] for gc in gene_pool], CBS)
        f.write(f'  x-axis "Codon Count Bins" {[x * CBS for x in range(len(codon_bin_counts))]}\n')
        f.write('  y-axis "GC Count"\n')
        f.write(f"  bar {codon_bin_counts}\n")
        f.write("```\n\n")
        f.write("## GC Logical Structure Mermaid Diagrams Key\n\n")
        f.write(mermaid_key())
        f.write("\n\n")
        gcs = tuple(enumerate(gene_pool))
        global_idx_set1 = set()
        global_idx_set2 = set()
        for idx, gpgc in gcs[:10]:
            f.write(f"## GC #{idx}\n\n")
            f.write("### Details\n\n")
            f.write(f"- Num codons: {gpgc['num_codons']}\n")
            f.write(f"- Binary signature: {gpgc['signature']}\n")
            f.write(f"- Hex signature: {gpgc['signature'].hex()}\n\n")
            f.write("### Logical Structure\n\n")
            f.write("```mermaid\n")
            f.write(gpgc.logical_mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Node Graph Structure with Line Limit = {ec1.line_limit()}\n\n")
            f.write("```mermaid\n")
            ng = ec1.node_graph(gpgc)
            ng.line_count(ec1.line_limit())
            f.write(ng.mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Code Connection Graphs with Line Limit = {ec1.line_limit()}\n")
            ntw: list[GCNode] = ec1.create_code_graphs(ng)
            for node in ntw:
                if node.function_info.global_index not in global_idx_set1:
                    f.write("\n```mermaid\n")
                    f.write(node.code_mermaid_chart())
                    f.write("\n```\n")
                    global_idx_set1.add(node.function_info.global_index)
                else:
                    f.write(f"Duplicate global index: {node.function_info.global_index}\n")
            f.write(f"### GC Node Graph Structure with Line Limit = {ec2.line_limit()}\n\n")
            f.write("```mermaid\n")
            ng = ec2.node_graph(gpgc)
            ng.line_count(ec2.line_limit())
            f.write(ng.mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Code Connection Graphs with Line Limit = {ec2.line_limit()}\n")
            ntw: list[GCNode] = ec2.create_code_graphs(ng)
            for node in ntw:
                if node.function_info.global_index not in global_idx_set2:
                    f.write("\n```mermaid\n")
                    f.write(node.code_mermaid_chart())
                    f.write("\n```\n")
                    global_idx_set2.add(node.function_info.global_index)
                else:
                    f.write(f"Duplicate global index: {node.function_info.global_index}\n")
            f.write("\n")

    # Dump as JSON so we can take a deeper look at the GC's
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        dump([gc.to_json() for gc in gene_pool], f, sort_keys=True, indent=4)
