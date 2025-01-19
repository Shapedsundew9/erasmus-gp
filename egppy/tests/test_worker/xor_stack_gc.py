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

from random import randint, seed

from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger

from egppy.gc_types.ggc_class_factory import GGCDict
from egppy.problems.configuration import ACYBERGENESIS_PROBLEM
from egppy.worker.gc_store import GGC_CACHE

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)

_logger.setLevel(DEBUG)

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
