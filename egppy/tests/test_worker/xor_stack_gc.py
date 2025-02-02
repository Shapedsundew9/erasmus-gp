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
from random import choice, random, randrange, seed, shuffle
import tempfile
from collections import Counter

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.gc import GCABC, mermaid_key
from egppy.gc_types.ggc_class_factory import GGCDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM
from egppy.worker.gc_store import GGC_CACHE
from egppy.worker.executor import GCNode, node_graph, line_count, ExecutionContext
from egppy.gc_graph.interface import AnyInterface


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
_logger.setLevel(DEBUG)


# Python int type as an EGP type
INT_T = ["int"]


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
        "gca": sixtyfour_gc,
        "gcb": getrandbits_gc,
        "graph": {
            "A": [],
            "B": [["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "num_codons": 2,
    }
)
GGC_CACHE[random_long_gc["signature"]] = random_long_gc


# Shift right by one GC function. Note that this function needs to
# be defined with the format and naming convention of the GC function
# i.e. inputs are encapsulated in a tuple (even if there is only one)
# and the output is a tuple (even if there is only one). The function
# name must end in an 8 character unsigned hexadecimal value.
def f_ffffffff(i: tuple[int]) -> tuple[int]:
    """Shift right by one."""
    return (i[0] >> 1,)


rshift_1_gc = GGCDict(
    {
        "ancestora": literal_1_gc,
        "ancestorb": rshift_gc,
        "gca": literal_1_gc["signature"],  # Makes the structure of this GC unknown
        "gcb": rshift_gc,
        "graph": {
            "A": [],
            "B": [["I", 0, ["int"]], ["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "num_codons": 2,
        # Pre-defined executable. GC will not be pulled from storage.
        "executable": f_ffffffff,
        "num_lines": 2,
    }
)
GGC_CACHE[rshift_1_gc["signature"]] = rshift_1_gc


rshift_xor_gc = GGCDict(
    {
        "ancestora": rshift_1_gc,
        "ancestorb": xor_gc,
        "gca": rshift_1_gc,
        "gcb": xor_gc,
        "graph": {
            "A": [["I", 1, ["int"]]],
            "B": [["I", 0, ["int"]], ["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc,
        "problem": ACYBERGENESIS_PROBLEM,
        "num_codons": 3,
    }
)
GGC_CACHE[rshift_xor_gc["signature"]] = rshift_xor_gc


# Initialize the gene pool wiht the building blocks
gene_pool: list[GCABC] = [rshift_xor_gc, random_long_gc]


def glue(gca: GCABC, gcb: GCABC) -> GCABC:
    """Glue two GC's together.

    1. Aggregate 0% to 50% of B's destination endpoints with all of A's.
        a. At least one of B's destination endpoints must not be aggregated.
    2. Randomly determine if one input is also a pass-through to output
    3. Randomly shuffle the endpoints.
    4. Randomly connect A's sources to B's unconnected destinations (one to many is allowed)
    5. Randomly connect 0% to 50% of A's sources to outputs
    6. Randomly connect 50% to 100% of B's destinations to outputs
    7. Populate row U with unconnected sources
    """
    # 1
    bdface: AnyInterface = gcb["graph"]["Is"]
    adface: AnyInterface = gca["graph"]["Is"]
    numbi = int(random() / 2.0 * len(bdface))
    numai = len(adface)
    iface = [["I", i, INT_T] for i in range(numbi + numai)]

    # 2
    passthru = False
    if random() < 0.5:
        iface.append(["I", len(iface), INT_T])
        passthru = True

    # 3
    shuffle(iface)
    aface = iface[numbi : numbi + numai]
    oface = [iface[-1]] if passthru else []
    bface = iface[:numbi] if numbi > 0 else []

    # 4
    asface: AnyInterface = gca["graph"]["Od"]
    numab = max(len(bdface) - numbi, 1)
    bface.extend([["A", randrange(len(asface)), INT_T] for _ in range(numab)])
    shuffle(bface)

    # 5
    numao = int(random() / 2.0 * len(asface))
    oface.extend([["A", randrange(len(asface)), INT_T] for _ in range(numao)])

    # 6
    bsface = gcb["graph"]["Od"]
    numbo = max(int((random() / 2.0 + 0.5) * len(bsface)), 1)
    oface.extend([["B", randrange(len(bsface)), INT_T] for _ in range(numbo)])
    shuffle(oface)

    # 7
    all_srcs = aface + bface + oface
    ui: set[int] = set(range(len(iface))) - {ept[1] for ept in all_srcs if ept[0] == "I"}
    ua: set[int] = set(range(len(asface))) - {ept[1] for ept in all_srcs if ept[0] == "A"}
    ub: set[int] = set(range(len(bsface))) - {ept[1] for ept in all_srcs if ept[0] == "B"}
    uface = (
        [["I", i, INT_T] for i in ui]
        + [["A", i, INT_T] for i in ua]
        + [["B", i, INT_T] for i in ub]
    )

    # Basic sanity checks
    assert len(oface) > 0, "No outputs"

    return GGCDict(
        {
            "ancestora": gca["signature"],
            "ancestorb": gcb["signature"],
            "gca": gca,
            "gcb": gcb,
            "graph": {
                "A": aface,
                "B": bface,
                "O": oface,
                "U": uface,
            },
            "pgc": xor_gc["signature"],
            "problem": ACYBERGENESIS_PROBLEM,
            "num_codons": gca["num_codons"] + gcb["num_codons"],
        }
    )


def build_gene_pool(max_num: int = 1024, limit: int = 256, _seed=42) -> None:
    """Randomly generate a pool of genetic codes based on
    the 64 bit random int GC and the XOR codon. A maximum
    of 1024 new GC's will be created or as many as possible
    before the limit of number of input or output endpoints is
    reached 3 times in a row."""
    seed(_seed)
    max_io_len = 0
    num = 2
    while num < max_num and max_io_len < limit:
        gca: GCABC = choice(gene_pool) if random() < 0.75 else choice((xor_gc, random_long_gc))
        gcb: GCABC = choice(gene_pool)
        gca, gcb = (gca, gcb) if random() < 0.5 else (gcb, gca)
        new_gc = glue(gca, gcb)
        if not new_gc["signature"] in GGC_CACHE:
            gene_pool.append(new_gc)
            GGC_CACHE[gene_pool[-1]["signature"]] = gene_pool[-1]
            num = len(gene_pool)
            max_io_len = max(gene_pool[-1]["num_inputs"], gene_pool[-1]["num_outputs"])


if __name__ == "__main__":
    build_gene_pool()
    LINE_LIMIT_X = 3
    LINE_LIMIT_Y = 5
    ec = ExecutionContext()

    # Create a markdown formated file with mermaid diagrams of the GC's in the gene pool
    # A temporary file is created in the default temp directory
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Genetic Codes\n\n")
        f.write(
            "Be aware that GC's may have the same GC graph (structure) but the top level "
            "GC my have a different connectivity resulting in a different signature.\n\n"
        )
        f.write(f"Num GC's: {len(gene_pool)}\n\n")
        f.write(f"Num codons distribution:\n{Counter([gc['num_codons'] for gc in gene_pool])}\n\n")
        f.write("## GC Logical Structure Mermaid Diagrams Key\n\n")
        f.write(mermaid_key())
        f.write("\n\n")
        gcs = tuple(enumerate(gene_pool))
        for idx, gc in gcs[:10]:
            f.write(f"## GC #{idx}\n\n")
            f.write("### Details\n\n")
            f.write(f"- Num codons: {gc['num_codons']}\n")
            f.write(f"- Binary signature: {gc['signature']}\n")
            f.write(f"- Hex signature: {gc['signature'].hex()}\n\n")
            f.write("### Logical Structure\n\n")
            f.write("```mermaid\n")
            f.write(gc.logical_mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Node Graph Structure with Line Limit = {LINE_LIMIT_X}\n\n")
            f.write("```mermaid\n")
            ng = node_graph(ec, gc, LINE_LIMIT_X)
            line_count(ng, LINE_LIMIT_X)
            f.write(ng.mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Node Graph Structure with Line Limit = {LINE_LIMIT_Y}\n\n")
            f.write("```mermaid\n")
            ng = node_graph(ec, gc, LINE_LIMIT_Y)
            line_count(ng, LINE_LIMIT_Y)
            f.write(ng.mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Code Connection Graphs with Line Limit = {LINE_LIMIT_Y}\n\n")
            ntw: list[GCNode] = ng.create_code_graphs()
            for node in ntw:
                f.write("```mermaid\n")
                f.write(node.code_mermaid_chart())
                f.write("\n```\n\n")

    # Dump as JSON so we can take a deeper look at the GC's
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        dump([gc.to_json() for gc in gene_pool], f, sort_keys=True, indent=4)
else:
    # gene_pool is used for testing the exectutor
    build_gene_pool()
    _logger.debug("Loaded %d genetic codes", len(gene_pool))
