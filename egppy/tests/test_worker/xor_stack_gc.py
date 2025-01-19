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

from random import choice, random, randrange, seed, shuffle
import tempfile

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.gc import GCABC
from egppy.gc_types.ggc_class_factory import GGCDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM
from egppy.worker.gc_store import GGC_CACHE
from egppy.gc_graph.interface import AnyInterface


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)
_logger.setLevel(DEBUG)


# Python int type as an EGP type
INT_T = ["int"]


# This is the Integral type XOR but it does not matter for this
xor_gc = GGC_CACHE[
    bytes.fromhex("00af97c888ef12a456daad8021f21c704c4259a6e954695983b3f93d49dd8290")
]
getrandbits_gc = GGC_CACHE[
    bytes.fromhex("65863464eac51421613e705329dd76fc7a73fbdb49bea1186621c5d2e030d53c")
]
sixtyfour_gc = GGC_CACHE[
    bytes.fromhex("b3598673014a84bccaa421a8eb78e4109b078f2c7398ef4f3aec1e1def8c752e")
]
custom_pgc = GGC_CACHE[
    bytes.fromhex("52b66afd16a31021917c90706449376957220434642bfc32c260bf947e7fd869")
]
random_long_gc = GGCDict(
    {
        "ancestora": sixtyfour_gc["signature"],
        "ancestorb": getrandbits_gc["signature"],
        "gca": sixtyfour_gc["signature"],
        "gcb": getrandbits_gc["signature"],
        "graph": {
            "A": [],
            "B": [["A", 0, ["int"]]],
            "O": [["B", 0, ["int"]]],
        },
        "pgc": custom_pgc["signature"],
        "problem": ACYBERGENESIS_PROBLEM,
    }
)
gene_pool: list[GCABC] = [xor_gc, random_long_gc]


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
        }
    )


def build_gene_pool(max_num: int = 1024, limit: int = 256) -> None:
    """Randomly generate a pool of genetic codes based on
    the 64 bit random int GC and the XOR codon. A maximum
    of 1024 new GC's will be created or as many as possible
    before the limit of number of input or output endpoints is
    reached 3 times in a row."""
    max_io_len = 0
    num = 2
    while num < max_num and max_io_len < limit:
        gca: GCABC = choice(gene_pool) if random() < 0.5 else choice((xor_gc, random_long_gc))
        gcb: GCABC = choice(gene_pool) if random() < 0.5 else choice((xor_gc, random_long_gc))
        gene_pool.append(glue(gca, gcb))
        num = len(gene_pool)
        max_io_len = max(gene_pool[-1]["num_inputs"], gene_pool[-1]["num_outputs"])


if __name__ == "__main__":
    seed(0)
    build_gene_pool()

    # Create a markdown formated file with mermaid diagrams of the GC's in the gene pool
    # A temporary file is created in the default temp directory
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Genetic Codes\n\n")
        for gc in gene_pool[:10] + gene_pool[-10:]:
            f.write(f"## GC {gc['signature'].hex()}\n\n")
            f.write("```mermaid\n")
            f.write(gc.logical_mermaid_chart())
            f.write("\n```\n\n")
