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
from random import choice, randint, random, seed, shuffle
from tempfile import NamedTemporaryFile
from time import time
from typing import Any

from egpcommon.codon_dev_load import find_codon_signature
from egpcommon.common import ACYBERGENESIS_PROBLEM, NULL_SHA256, bin_counts
from egpcommon.egp_log import Logger, egp_logger, enable_debug_logging
from egpcommon.object_deduplicator import deduplicators_info
from egpcommon.properties import BASIC_ORDINARY_PROPERTIES
from egppy.gene_pool.gene_pool_interface import GenePoolInterface
from egppy.genetic_code.egc_class_factory import EGCDict
from egppy.genetic_code.genetic_code import GCABC, mermaid_key
from egppy.genetic_code.ggc_class_factory import GGCDict
from egppy.genetic_code.types_def import types_def_store
from egppy.local_db_config import LOCAL_DB_MANAGER_CONFIG
from egppy.worker.executor.execution_context import ExecutionContext, FunctionInfo, GCNode

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
enable_debug_logging()


# Set the seed for reproducibility
seed(0)


# Python int type as an EGP type
INT_T = "int"
INT_TD = types_def_store[INT_T]

# New GC consistency assessment sample rate
# Slows down the code but is useful for debugging
# Set to 0.0 to disable or a fractional value for random sampling.
CONSISTENCY_SAMPLE = 1.0
gpi = GenePoolInterface(LOCAL_DB_MANAGER_CONFIG)


# Load the primitive codons from the gene pool
# Dictionary mapping signature names to their values
CODON_SIGS: dict[str, bytes] = {}

# Define all codon signatures
_codon_specs = {
    "RSHIFT_SIG": (["Integral"], ["EGPNumber"], ">>"),
    "XOR_SIG": (["Integral"], ["EGPNumber"], "^"),
    "GETRANDBITS_SIG": (["int"], ["int"], "getrandbits"),
    "LITERAL_1_SIG": ([], ["int"], "1"),
    "SIXTYFOUR_SIG": ([], ["int"], "64"),
    "CUSTOM_PGC_SIG": ([], [], "custom"),
    "INT_TO_SIG": (["int"], ["Integral"], "raise_if_not_instance_of(int, Integral)"),
    "TO_INT_SIG": (["EGPNumber"], ["int"], "raise_if_not_instance_of(EGPNumber, int)"),
}


# Dictionary of primitive GCs
# This is empty on initialization and populated on first use
primitive_gcs: dict[str, GCABC] = {}


def find_gc(signature: bytes) -> GCABC:
    """Find a GC in the cache."""
    retval = gpi[signature]
    assert isinstance(retval, GCABC), f"GC with signature {signature.hex()} is not a GCABC object."
    return retval


def resolve_inherited_members(egc: GCABC) -> GCABC:
    """Resolve inherited members from ancestor GCs."""
    assert isinstance(egc, GCABC), "GC must be a GCABC object."
    gca = egc["gca"]
    gcb = egc["gcb"]
    if gca == NULL_SHA256:
        raise ValueError("Cannot resolve inherited members. GC is a codon.")
    gca = find_gc(gca)

    # Populate inherited members as if just GCA is set
    egc["num_codons"] = gca["num_codons"]
    egc["num_codes"] = gca["num_codes"] + 1
    egc["generation"] = gca["generation"] + 1
    egc["code_depth"] = gca["code_depth"] + 1

    # Ad in this GC must be the same as Is in the GCA
    # NOTE: That the TypesDef ObjectSet should ensure they are the same object
    for idx, (a, i) in enumerate(zip(egc["cgraph"]["Ad"], gca["cgraph"]["Is"])):
        if a.typ is not i.typ:
            raise ValueError(
                f"Input types do not match for GCA at position {idx}: "
                f"self['cgraph']['Ad'][{idx}].typ={a.typ!r}, "
                f"gca['cgraph']['Is'][{idx}].typ={i.typ!r}"
            )

    # As in this GC must be the same as Od in the GCA
    for idx, (a, o) in enumerate(zip(egc["cgraph"]["As"], gca["cgraph"]["Od"])):
        if a.typ is not o.typ:
            raise ValueError(
                f"Output types do not match for GCA at position {idx}: "
                f"self['cgraph']['As'][{idx}].typ={a.typ!r}, "
                f"gca['cgraph']['Od'][{idx}].typ={o.typ!r}"
            )

    # If GCB exists modify
    if gcb != NULL_SHA256:
        gcb = find_gc(gcb)
        egc["num_codons"] += gcb["num_codons"]
        egc["num_codes"] += gcb["num_codes"]
        egc["generation"] = max(egc["generation"], gcb["generation"] + 1)
        egc["code_depth"] = max(egc["code_depth"], gcb["code_depth"] + 1)

        # Bd in this GC must be the same as Is in the GCB
        # NOTE: That the TypesDef ObjectSet should ensure they are the same object
        if not all(b.typ is i.typ for b, i in zip(egc["cgraph"]["Bd"], gcb["cgraph"]["Is"])):
            raise ValueError("Input types do not match for GCB")

        # Bs in this GC must be the same as Od in the GCB
        if not all(b.typ is o.typ for b, o in zip(egc["cgraph"]["Bs"], gcb["cgraph"]["Od"])):
            raise ValueError("Output types do not match for GCB")

    return egc


def inherit_members(gc: dict[str, Any], check: bool = True) -> GGCDict:
    """Create a EGC, inherit members from its sub-GCs and create a new GGC."""
    egc = EGCDict(gc)
    ggc = GGCDict(resolve_inherited_members(egc))
    if check:
        try:
            ggc.verify()
        except (ValueError, RuntimeError) as e:
            raise ValueError(f"GC with signature {ggc['signature'].hex()} is not valid.") from e
    gpi[ggc["signature"]] = ggc
    return ggc


def cast_to_int_at_input_idx(mc: GGCDict, gc: GGCDict, idx: int) -> GGCDict:
    """Cast the input at the given index to 'int'.
    This is done by stacking a meta codon that does the right conversion
    as GCA and wiring through the inputs and outputs directly
    to ensure the interface remains in the same order.

    Args
    ----
    mc: The meta codon to use for the cast.
    gc: The original GC to cast.
    idx: The index of the input in gc to cast.
    """
    mcot = mc["cgraph"]["Od"][0].typ.name
    return inherit_members(
        {
            "ancestora": gc,
            "ancestorb": mc,
            "created": "2025-03-29 22:05:08.489847+00:00",
            "gca": mc,
            "gcb": gc,
            "cgraph": {
                "A": [["I", idx, mc["cgraph"]["Is"][0].typ.name]],
                "B": [
                    ["I", ep.idx, ep.typ.name] if ep.idx != idx else ["A", 0, mcot]
                    for ep in gc["cgraph"]["Is"]
                ],
                "O": [["B", ep.idx, ep.typ.name] for ep in gc["cgraph"]["Od"]],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )


def cast_to_int_at_output_idx(mc: GGCDict, gc: GGCDict, idx: int) -> GGCDict:
    """Cast the output at the given index to 'int'.
    This is done by stacking a meta codon that does the right conversion
    as GCB and wiring through the inputs and outputs directly
    to ensure the interface remains in the same order.

    Args
    ----
    mc: The meta codon to use for the cast.
    gc: The original GC to cast.
    idx: The index of the output in gc to cast.
    """
    mcot = mc["cgraph"]["Od"][0].typ.name
    return inherit_members(
        {
            "ancestora": gc,
            "ancestorb": mc,
            "created": "2025-03-29 22:05:08.489847+00:00",
            "gca": gc,
            "gcb": mc,
            "cgraph": {
                "A": [["I", ep.idx, ep.typ.name] for ep in gc["cgraph"]["Is"]],
                "B": [["A", idx, gc["cgraph"]["Od"][idx].typ.name]],
                "O": [
                    ["A", ep.idx, ep.typ.name] if ep.idx != idx else ["B", 0, mcot]
                    for ep in gc["cgraph"]["Od"]
                ],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )


def cast_interfaces_to_int(gc: GGCDict) -> GGCDict:
    """Cast the interfaces of the GC to 'int'.
    The functional GC's have interfaces defined by the most generic type (usually 'Integral').
    Since EGP requires typing to be explicit each interface needs to be 'cast' to 'int' using
    meta codons.
    """

    int_to: dict[str, GGCDict] = {"Integral": gpi[CODON_SIGS["INT_TO_SIG"]]}
    to_int: dict[str, GGCDict] = {"EGPNumber": gpi[CODON_SIGS["TO_INT_SIG"]]}

    # Find all the endpoint in the input interface that are not 'int'
    while iepl := [iep for iep in gc["cgraph"]["Is"] if iep.typ != INT_TD]:
        # We will only process the first endpoint in the iepl list
        # Find the appropriate meta codon to cast the first endpoint to 'int'
        meta_codon = int_to.get(iepl[0].typ.name)
        if meta_codon is None:
            raise ValueError(f"No meta-codon found to cast {iepl[0].typ.name} to int.")
        # Create an new GC with that endpoint cast. This GC will be evaluated to see
        # if all its inputs are 'int' in the next iteration
        gc = cast_to_int_at_input_idx(meta_codon, gc, iepl[0].idx)

    # Now do the same with the outputs
    while oepl := [oep for oep in gc["cgraph"]["Od"] if oep.typ != INT_TD]:
        # We will only process the first endpoint in the oepl list
        # Find the appropriate meta codon to cast the first endpoint to 'int'
        meta_codon = to_int.get(oepl[0].typ.name)
        if meta_codon is None:
            raise ValueError(f"No meta-codon found to cast {oepl[0].typ.name} to int.")
        # Create an new GC with that endpoint cast. This GC will be evaluated to see
        # if all its outputs are 'int' in the next iteration
        gc = cast_to_int_at_output_idx(meta_codon, gc, oepl[0].idx)

    # The original GC with the input & output types converted to 'int'
    return gc


# Shift right by one GC function. Note that this function needs to
# be defined with the format and naming convention of the GC function
# i.e. inputs are encapsulated in a tuple (even if there is only one)
# and the output is a tuple (even if there is only one). The function
# name must end in an 8 character unsigned hexadecimal value.
def f_7fffffff(i: tuple[int]) -> int:
    """Shift right by one."""
    return i[0] >> 1


def create_primitive_gcs() -> None:
    """Create the primitive GC's used in the tests."""
    if primitive_gcs:
        return  # Already created

    # Load and validate all codon signatures
    for cname, (input_types, output_types, codon_name) in _codon_specs.items():
        csig = find_codon_signature(input_types, output_types, codon_name)
        assert csig is not None, f"{cname} codon signature not found"
        CODON_SIGS[cname] = csig

    # Right shift and xor need interfaces casting
    rshift_gc = cast_interfaces_to_int(gpi[CODON_SIGS["RSHIFT_SIG"]])
    xor_gc = cast_interfaces_to_int(gpi[CODON_SIGS["XOR_SIG"]])

    # random_long_gc signature:
    random_long_gc = inherit_members(
        {
            "ancestora": gpi[CODON_SIGS["SIXTYFOUR_SIG"]],
            "ancestorb": gpi[CODON_SIGS["GETRANDBITS_SIG"]],
            "created": "2025-03-29 22:05:08.489847+00:00",
            "gca": gpi[CODON_SIGS["SIXTYFOUR_SIG"]],
            "gcb": gpi[CODON_SIGS["GETRANDBITS_SIG"]],
            "cgraph": {
                "A": [],
                "B": [["A", 0, INT_T]],
                "O": [["B", 0, INT_T]],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )

    # rshift_1_gc signature:
    rshift_1_gc = inherit_members(
        {
            "ancestora": gpi[CODON_SIGS["LITERAL_1_SIG"]],
            "ancestorb": rshift_gc,
            "created": "2025-03-29 22:05:08.489847+00:00",
            "code_depth": 2,
            "gca": gpi[CODON_SIGS["LITERAL_1_SIG"]][
                "signature"
            ],  # Makes the structure of this GC unknown
            "gcb": rshift_gc,
            "generation": 2,
            "cgraph": {
                "A": [],
                "B": [["I", 0, INT_T], ["A", 0, INT_T]],
                "O": [["B", 0, INT_T]],
                "U": [],
            },
            "num_codes": 3,
            "num_codons": 2,
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )

    # rshift_xor_gc signature:
    rshift_xor_gc = inherit_members(
        {
            "ancestora": rshift_1_gc,
            "ancestorb": xor_gc,
            "created": "2025-03-29 22:05:08.489847+00:00",
            "gca": rshift_1_gc,
            "gcb": xor_gc,
            "cgraph": {
                "A": [["I", 1, INT_T]],
                "B": [["I", 0, INT_T], ["A", 0, INT_T]],
                "O": [["B", 0, INT_T]],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )

    # one_to_two signature:
    one_to_two = inherit_members(
        {
            "ancestora": random_long_gc,
            "ancestorb": rshift_xor_gc,
            "created": "2025-03-29 22:05:08.489847+00:00",
            "gca": random_long_gc,
            "gcb": rshift_xor_gc,
            "cgraph": {
                "A": [],
                "B": [["I", 0, INT_T], ["A", 0, INT_T]],
                "O": [["B", 0, INT_T], ["A", 0, INT_T]],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
        }
    )
    two_to_one = rshift_xor_gc

    # Populate the primitive GC dictionary
    primitive_gcs["random_long"] = random_long_gc
    primitive_gcs["rshift_1"] = rshift_1_gc
    primitive_gcs["rshift_xor"] = rshift_xor_gc
    primitive_gcs["one_to_two"] = one_to_two
    primitive_gcs["two_to_one"] = two_to_one


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
    return inherit_members(
        {
            "ancestora": gca,
            "ancestorb": gcb,
            "gca": gca,
            "gcb": gcb,
            "cgraph": {
                "A": [["I", i, INT_T] for i in randomrange(len(gca["inputs"]))],
                "B": [["I", i, INT_T] for i in randomrange(len(gca["inputs"]), len(gcb["inputs"]))],
                "O": [["A", i, INT_T] for i in randomrange(len(gca["outputs"]))]
                + [["B", i, INT_T] for i in randomrange(len(gcb["outputs"]))],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gca["num_codons"] + gcb["num_codons"],
        },
        random() < CONSISTENCY_SAMPLE,
    )


def append_gcs(gc1: GCABC, gc2: GCABC) -> GCABC:
    """Create a new GC with # of input & outputs = gc1 + gc2.

    Create a GC where GCA = gc1 and GCB = gc2.
    The inputs to the GC are the concatenation of the inputs to gc.
    The outputs of the GC are the concatenation of the outputs GCA & GCB.
    """
    gca: GCABC = gc1
    gcb: GCABC = gc2
    return inherit_members(
        {
            "ancestora": gca,
            "ancestorb": gcb,
            "gca": gca,
            "gcb": gcb,
            "cgraph": {
                "A": [["I", i, INT_T] for i in randomrange(len(gca["inputs"]))],
                "B": [
                    ["I", i + len(gca["inputs"]), INT_T] for i in randomrange(len(gcb["inputs"]))
                ],
                "O": [["A", i, INT_T] for i in randomrange(len(gca["outputs"]))]
                + [["B", i, INT_T] for i in randomrange(len(gcb["outputs"]))],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gca["num_codons"] + gcb["num_codons"],
        },
        random() < CONSISTENCY_SAMPLE,
    )


def expand_gc_inputs(gc1: GCABC, gc2: GCABC, narrow_gc: GCABC) -> GCABC:
    """Expand the GC.

    Append gc2 to gc1 as per append_gcs then stack it on the narrow to
    reduce the number of outputs back to the original number of outputs.

    This asserts that the number of inputs to the narrow GC is
    # gc1 outputs + # gc2 outputs and the number of outputs is
    # gc1 outputs.
    Connections on each interface are randomly assigned.
    """
    assert len(gc1["outputs"]) + len(gc2["outputs"]) == len(
        narrow_gc["inputs"]
    ), "gc1 + gc2 outputs != narrow_gc # inputs."
    assert len(gc1["outputs"]) == len(narrow_gc["outputs"]), "gc1 outputs != narrow_gc outputs."
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
    assert len(gc1["outputs"]) == len(gc2["inputs"]), "gc1 # outputs != gc2 # inputs"
    return inherit_members(
        {
            "ancestora": gc1,
            "ancestorb": gc2,
            "gca": gc1,
            "gcb": gc2,
            "cgraph": {
                "A": [["I", i, INT_T] for i in randomrange(len(gc1["inputs"]))],
                "B": [["A", i, INT_T] for i in randomrange(len(gc2["inputs"]))],
                "O": [["B", i, INT_T] for i in randomrange(len(gc2["outputs"]))],
                "U": [],
            },
            "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
            "problem": ACYBERGENESIS_PROBLEM,
            "properties": BASIC_ORDINARY_PROPERTIES,
            "num_codons": gc1["num_codons"] + gc2["num_codons"],
        },
        random() < CONSISTENCY_SAMPLE,
    )


def create_gc_matrix(max_epc: int) -> dict[int, dict[int, list[GCABC]]]:
    """Create a matrix of GC's.

    Create a matrix of GC's where the maximum number of inputs and outputs
    is determined by max_epc. The matrix is a dictionary of
    dictionaries where the key is the number of inputs and the value
    is a dictionary of the number of outputs and a set of GC's.

    GC's will be created for all combinations of inputs and outputs
    1 to max_epc.

    max_epc must be >= 2

    matrix[#inputs][#outputs] = {GC1, GC2, ...}
    """
    assert max_epc >= 2, "max_epc < 2"
    create_primitive_gcs()
    max_epc = max_epc + 1
    _gcm: dict[int, dict[int, list[GCABC]]] = {
        1: {
            1: [stack_gcs(primitive_gcs["one_to_two"], primitive_gcs["two_to_one"])],
            2: [primitive_gcs["one_to_two"]],
        },
        2: {1: [primitive_gcs["two_to_one"]]},
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
            gcb = choice(tuple(_gcm[num_b][num_outputs - len(gca["outputs"])]))
            ngc = append_gcs(gca, gcb)
            target_set.append(ngc)
            assert len(ngc["inputs"]) == num_inputs, f"ngx # inputs != {num_inputs}"
            assert len(ngc["outputs"]) == num_outputs, f"ngx # outputs != {num_outputs}"
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
    ec1 = ExecutionContext(gpi, 3)
    ec2 = ExecutionContext(gpi, 50, wmc=True)  # Write the meta codons
    # Hack in pre-defined function
    ec1.function_map[primitive_gcs["rshift_1"]["signature"]] = FunctionInfo(
        f_7fffffff, 0x7FFFFFFF, 2, primitive_gcs["rshift_1"]
    )
    ec2.function_map[primitive_gcs["rshift_1"]["signature"]] = FunctionInfo(
        f_7fffffff, 0x7FFFFFFF, 2, primitive_gcs["rshift_1"]
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
        for indx, gpgc in gcs[:10]:
            f.write(f"## GC #{indx}\n\n")
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
                if node.finfo.global_index not in global_idx_set1:
                    f.write("\n```mermaid\n")
                    f.write(node.code_mermaid_chart())
                    f.write("\n```\n")
                    global_idx_set1.add(node.finfo.global_index)
                else:
                    f.write(f"Duplicate global index: {node.finfo.global_index}\n")
            f.write(f"\n### GC Node Graph Structure with Line Limit = {ec2.line_limit()}\n\n")
            f.write("```mermaid\n")
            ng = ec2.node_graph(gpgc)
            ng.line_count(ec2.line_limit())
            f.write(ng.mermaid_chart())
            f.write("\n```\n\n")
            f.write(f"### GC Code Connection Graphs with Line Limit = {ec2.line_limit()}\n")
            ntw: list[GCNode] = ec2.create_code_graphs(ng)
            for node in ntw:
                if node.finfo.global_index not in global_idx_set2:
                    f.write("\n```mermaid\n")
                    f.write(node.code_mermaid_chart())
                    f.write("\n```\n")
                    global_idx_set2.add(node.finfo.global_index)
                else:
                    f.write(f"Duplicate global index: {node.finfo.global_index}\n")
            f.write("\n")

    # Dump as JSON so we can take a deeper look at the GC's
    with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        dump([gc.to_json() for gc in gene_pool], f, sort_keys=True, indent=4)

    # Deduplicator info
    print(f"GC markdown and JSON files created.\n\n{deduplicators_info()}")
