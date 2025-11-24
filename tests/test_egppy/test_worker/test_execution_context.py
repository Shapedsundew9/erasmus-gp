"""Unit tests for the executor function."""

import unittest
from random import choice, getrandbits, randint, seed

from egpcommon.common import ACYBERGENESIS_PROBLEM, random_int_tuple_generator
from egpcommon.egp_log import Logger, egp_logger, enable_debug_logging
from egpcommon.properties import BASIC_ORDINARY_PROPERTIES, CGraphType, GCType, PropertiesBD
from egppy.genetic_code.genetic_code import NULL_SIGNATURE
from egppy.genetic_code.ggc_class_factory import GCABC
from egppy.worker.executor.context_writer import (
    FWC4FILE,
    OutputFileType,
    write_context_to_file,
    write_function_to_file,
)
from egppy.worker.executor.execution_context import ExecutionContext, FunctionInfo
from egppy.worker.executor.gc_node import GCNode

from .xor_stack_gc import (
    CODON_SIGS,
    INT_T,
    create_gc_matrix,
    expand_gc_matrix,
    f_7fffffff,
    gpi,
    inherit_members,
    primitive_gcs,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
enable_debug_logging()


# Constants
NUM_LINES: tuple[int, ...] = (3, 5, 7, 8, 11, 16, 39, 100, 32767)


class TestExecutor(unittest.TestCase):
    """Unit tests for the executor function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class method for test setup."""
        cls.gpi = gpi
        cls.gcm: dict[int, dict[int, list[GCABC]]] = expand_gc_matrix(create_gc_matrix(8), 10)
        cls.gene_pool: list[GCABC] = [
            gc for ni in cls.gcm.values() for rs in ni.values() for gc in rs
        ]

    def setUp(self) -> None:
        super().setUp()
        # 2 different execution contexts
        self.ec1 = ExecutionContext(self.gpi, 3)
        self.ec2 = ExecutionContext(self.gpi, 50, wmc=True)  # Write the meta-codons
        # Hack in pre-defined function
        self.ec1.function_map[primitive_gcs["rshift_1"]["signature"]] = FunctionInfo(
            f_7fffffff, 0x7FFFFFFF, 2, primitive_gcs["rshift_1"]
        )
        self.ec2.function_map[primitive_gcs["rshift_1"]["signature"]] = FunctionInfo(
            f_7fffffff, 0x7FFFFFFF, 2, primitive_gcs["rshift_1"]
        )
        self.ec1.namespace["f_7fffffff"] = f_7fffffff
        self.ec2.namespace["f_7fffffff"] = f_7fffffff

    def test_write_single_codon_ec1(self) -> None:
        """Test writing a single codon to the execution context."""
        node = self.ec1.write_executable(CODON_SIGS["SIXTYFOUR_SIG"])
        self.assertIsInstance(node, GCNode)

    def test_run_single_codon_ec1(self) -> None:
        """Test writing a single codon to the execution context."""
        self.assertEqual(self.ec1.execute(CODON_SIGS["SIXTYFOUR_SIG"], tuple()), 64)

    def test_write_function_ec1_basic(self) -> None:
        """Test the write_function function."""
        node = self.ec1.write_executable(primitive_gcs["one_to_two"])
        self.assertIsInstance(node, GCNode)
        assert isinstance(node, GCNode), "node is not a GCNode"
        ftext = self.ec1.function_def(node, FWC4FILE)
        self.assertIsInstance(ftext, str)
        expected = (
            "def f_1(i: tuple[int]) -> tuple[int, int]:\n"
            '\t"""Signature: 9cdb994a05ee0630d4d79747c9b62ac4ba22545e3085aa3645aed30d13615057\n'
            "\tCreated: 2025-03-29 22:05:08.489847+00:00\n"
            "\tLicense: MIT\n"
            "\tCreator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f\n"
            "\tGeneration: 7\n"
            '\t"""\n'
            "\to1 = f_0()\n"
            "\tt0 = f_7fffffff((o1,))\n"
            "\to0 = i[0] ^ t0\n"
            "\treturn o0, o1"
        )
        self.assertEqual(ftext, expected)

    def test_write_function_ec2_basic(self) -> None:
        """Test the write_function function."""
        node = self.ec2.write_executable(primitive_gcs["one_to_two"])
        self.assertIsInstance(node, GCNode)
        assert isinstance(node, GCNode), "node is not a GCNode"
        ftext = self.ec2.function_def(node, FWC4FILE)
        self.assertIsInstance(ftext, str)
        expected = (
            "def f_0(i: tuple[int]) -> tuple[int, int]:\n"
            '\t"""Signature: 9cdb994a05ee0630d4d79747c9b62ac4ba22545e3085aa3645aed30d13615057\n'
            "\tCreated: 2025-03-29 22:05:08.489847+00:00\n"
            "\tLicense: MIT\n"
            "\tCreator: 1f8f45ca-0ce8-11f0-a067-73ab69491a6f\n"
            "\tGeneration: 7\n"
            '\t"""\n'
            "\tt0 = 64\n"
            "\to1 = getrandbits(t0)\n"
            "\tt3 = f_7fffffff((o1,))\n"
            "\tt2 = raise_if_not_instance_of(t3, Integral)\n"
            "\tt4 = raise_if_not_instance_of(i[0], Integral)\n"
            "\tt1 = t4 ^ t2\n"
            "\to0 = raise_if_not_instance_of(t1, int)\n"
            "\treturn o0, o1"
        )
        self.assertEqual(ftext, expected)

    def test_execute_basic(self) -> None:
        """Test the execute function."""
        self.ec1.write_executable(primitive_gcs["one_to_two"])
        write_context_to_file(self.ec1)
        self.ec2.write_executable(primitive_gcs["one_to_two"])
        write_context_to_file(self.ec2)
        seed(0)
        r1 = self.ec1.execute(primitive_gcs["one_to_two"]["signature"], (0x12345678,))
        seed(0)
        r2 = self.ec2.execute(primitive_gcs["one_to_two"]["signature"], (0x12345678,))
        self.assertIsInstance(r1, tuple)
        self.assertIsInstance(r2, tuple)
        self.assertEqual(r1, r2)

    def test_execute_advanced_single(self) -> None:
        """This test case is used to reproduce single instances from the matrix test case below."""
        ec1 = ExecutionContext(self.gpi, 3)
        ec2 = ExecutionContext(self.gpi, 5)
        gci = 0
        idx = 0
        ec1.write_executable(self.gene_pool[gci])
        ec2.write_executable(self.gene_pool[gci])

        seed(idx)
        r1 = ec1.execute(self.gene_pool[gci]["signature"], tuple(getrandbits(64) for _ in range(2)))
        write_context_to_file(ec1)

        seed(idx)
        r2 = ec2.execute(self.gene_pool[gci]["signature"], tuple(getrandbits(64) for _ in range(2)))
        write_context_to_file(ec2)

        self.assertEqual(r1, r2)

    def test_execute_advanced_matrix(self) -> None:
        """This is a complex test that uses the XOR stack
        to generate multiple different execution contexts
        and validate they all produce the same result."""
        seed(1)
        the_one_hundred: tuple[int, ...] = random_int_tuple_generator(100, len(self.gene_pool))
        # For debug: 1st 100 are the smallest code trees
        # the_one_hundred = tuple(range(100))
        baseline: dict[int, list[int]] = {num_lines: [] for num_lines in NUM_LINES}

        for num_lines in NUM_LINES:
            # Create a new execution context
            ec = ExecutionContext(self.gpi, num_lines)
            # Add the functions to the execution context
            for idx, gci in enumerate(the_one_hundred):
                ec.write_executable(self.gene_pool[gci])
                seed(idx)
                # Execute the function
                gc: GCABC = self.gene_pool[gci]
                result = ec.execute(
                    gc["signature"], tuple(getrandbits(64) for _ in range(len(gc["inputs"])))
                )
                baseline[num_lines].append(result)
                if num_lines != NUM_LINES[0]:
                    # Check the result against the previous execution context
                    self.assertEqual(result, baseline[NUM_LINES[0]][idx])

    def test_write_gene_pool_ec1(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        seed(1)
        the_one_hundred: tuple[int, ...] = random_int_tuple_generator(100, len(self.gene_pool))
        for idx in the_one_hundred:
            _logger.debug("Writing gc %d", idx)
            gc = self.gene_pool[idx]
            self.ec1.write_executable(gc)
        write_context_to_file(self.ec1)

    def test_write_gene_pool_ec2(self) -> None:
        """Test the functions execute.
        This is a placeholder test for now as it is deep and complex."""
        seed(1)
        the_one_hundred: tuple[int, ...] = random_int_tuple_generator(100, len(self.gene_pool))
        for idx in the_one_hundred:
            _logger.debug("Writing gc %d", idx)
            gc = self.gene_pool[idx]
            self.ec2.write_executable(gc)
        write_context_to_file(self.ec2)

    def test_if_then_simple(self) -> None:
        """Test IF_THEN generation."""
        # Create a simple IF_THEN GC

        # Pick a GCA (path "if True") that takes 3 inputs and produces 3 outputs
        gca = choice(self.gcm[3][3])

        # Now create an IF_THEN GC that uses GCA as the "then" branch. The "else"
        # branch is NULL_SIGNATURE which has no function just connects inputs to
        # outputs in pass_through_order.
        pass_through_order = (1, 2, 0)
        ggc = inherit_members(
            {
                "ancestora": gca,
                "ancestorb": NULL_SIGNATURE,
                "gca": gca,
                "gcb": NULL_SIGNATURE,
                "cgraph": {
                    "F": [["I", 3, "bool"]],  # Condition
                    "A": [["I", i, INT_T] for i in range(len(gca["inputs"]))],
                    "O": [["A", i, INT_T] for i in range(len(gca["outputs"]))],
                    "P": [["I", i, INT_T] for i in pass_through_order],
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": BASIC_ORDINARY_PROPERTIES,
                "num_codons": gca["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        # write_function_to_file(self.ec2, ggc, "temp.md", oft=OutputFileType.MARKDOWN)

    def test_if_then_execution(self) -> None:
        """Test IF_THEN execution."""
        # Create a simple IF_THEN GC

        # Set the seed for reproducibility of random choices and then
        # generate 3 random integers that will be used as inputs
        seed(42)
        a, b, c = tuple(getrandbits(64) for _ in range(3))

        # Pick a GCA (path "if True") that takes 3 inputs and produces 3 outputs
        # Execute GCA with inputs a, b, c to get outputs. This is our result
        # to compare against when the condition is True.
        gca = choice(self.gcm[3][3])
        seed(43)
        r_true_expected = self.ec2.execute(gca, (a, b, c))

        # Now create an IF_THEN GC that uses GCA as the "then" branch. The "else"
        # branch is NULL_SIGNATURE which has no function just connects inputs to
        # outputs in pass_through_order.
        pass_through_order = (1, 2, 0)
        r_false_expected = tuple((a, b, c)[i] for i in pass_through_order)
        ggc = inherit_members(
            {
                "ancestora": gca,
                "ancestorb": NULL_SIGNATURE,
                "gca": gca,
                "gcb": NULL_SIGNATURE,
                "cgraph": {
                    "F": [["I", 3, "bool"]],  # Condition
                    "A": [["I", i, INT_T] for i in range(len(gca["inputs"]))],
                    "O": [["A", i, INT_T] for i in range(len(gca["outputs"]))],
                    "P": [["I", i, INT_T] for i in pass_through_order],
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": BASIC_ORDINARY_PROPERTIES,
                "num_codons": gca["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        # write_context_to_file(self.ec2, "temp.md", oft=OutputFileType.MARKDOWN)

        # Execute the IF_THEN GC with condition True. Need the same seed
        # to ensure any random choices in GCA are the same.
        seed(43)
        r_true = self.ec2.execute(ggc, (a, b, c, True))
        self.assertEqual(r_true, r_true_expected)
        # Execute the IF_THEN GC with condition False
        r_false = self.ec2.execute(ggc, (a, b, c, False))
        self.assertEqual(r_false, r_false_expected)

        # Do it again with ec1 (different line limit)
        # self.ec1.write_executable(ggc)
        # write_context_to_file(self.ec1, "temp.md", oft=OutputFileType.MARKDOWN)
        seed(43)
        r_true = self.ec1.execute(ggc, (a, b, c, True))
        self.assertEqual(r_true, r_true_expected)
        r_false = self.ec1.execute(ggc, (a, b, c, False))
        self.assertEqual(r_false, r_false_expected)

    def test_if_then_else_simple(self) -> None:
        """Test IF_THEN_ELSE generation."""
        # Create a simple IF_THEN_ELSE GC

        # Pick a GCA (path "if True") that takes 3 inputs and produces 3 outputs
        # Execute GCA with inputs a, b, c to get outputs. This is our result
        # to compare against when the condition is True.
        idx = randint(0, len(self.gcm[3][3]) - 1)
        gca = self.gcm[3][3][idx]

        # Pick a GCB (path "if False") that takes 3 inputs and produces 3 outputs
        # that is guaranteed to be different from GCA.
        # Execute GCB with inputs a, b, c to get outputs. This is our result
        # to compare against when the condition is False.
        gcb = self.gcm[3][3][(idx + 1) % len(self.gcm[3][3])]

        # Now create an IF_THEN_ELSE GC that uses GCA as the "then" branch
        # and GCB as the "else" branch.
        ggc = inherit_members(
            {
                "ancestora": gca,
                "ancestorb": gcb,
                "gca": gca,
                "gcb": gcb,
                "cgraph": {
                    "F": [["I", 3, "bool"]],  # Condition
                    "A": [["I", i, INT_T] for i in range(len(gca["inputs"]))],
                    "B": [["I", i, INT_T] for i in range(len(gcb["inputs"]))],
                    "O": [["A", i, INT_T] for i in range(len(gca["outputs"]))],
                    "P": [["B", i, INT_T] for i in range(len(gcb["outputs"]))],
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": BASIC_ORDINARY_PROPERTIES,
                "num_codons": gca["num_codons"] + gcb["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        # write_function_to_file(self.ec2, ggc, "temp.md", oft=OutputFileType.MARKDOWN)

    def test_if_then_else_execution(self) -> None:
        """Test IF_THEN_ELSE execution."""
        # Create a simple IF_THEN_ELSE GC

        # Set the seed for reproducibility of random choices and then
        # generate 3 random integers that will be used as inputs
        seed(42)
        a, b, c = tuple(getrandbits(64) for _ in range(3))

        # Pick a GCA (path "if True") that takes 3 inputs and produces 3 outputs
        # Execute GCA with inputs a, b, c to get outputs. This is our result
        # to compare against when the condition is True.
        idx = randint(0, len(self.gcm[3][3]) - 1)
        gca = self.gcm[3][3][idx]
        seed(43)
        r_true_expected = self.ec2.execute(gca, (a, b, c))

        # Pick a GCB (path "if False") that takes 3 inputs and produces 3 outputs
        # that is guaranteed to be different from GCA.
        # Execute GCB with inputs a, b, c to get outputs. This is our result
        # to compare against when the condition is False.
        gcb = self.gcm[3][3][(idx + 1) % len(self.gcm[3][3])]
        seed(44)
        r_false_expected = self.ec2.execute(gcb, (a, b, c))

        # Now create an IF_THEN_ELSE GC that uses GCA as the "then" branch
        # and GCB as the "else" branch.
        ggc = inherit_members(
            {
                "ancestora": gca,
                "ancestorb": gcb,
                "gca": gca,
                "gcb": gcb,
                "cgraph": {
                    "F": [["I", 3, "bool"]],  # Condition
                    "A": [["I", i, INT_T] for i in range(len(gca["inputs"]))],
                    "B": [["I", i, INT_T] for i in range(len(gcb["inputs"]))],
                    "O": [["A", i, INT_T] for i in range(len(gca["outputs"]))],
                    "P": [["B", i, INT_T] for i in range(len(gcb["outputs"]))],
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": BASIC_ORDINARY_PROPERTIES,
                "num_codons": gca["num_codons"] + gcb["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        # write_context_to_file(self.ec2, "temp.md", oft=OutputFileType.MARKDOWN)

        # Execute the IF_THEN_ELSE GC with condition True. Need the same seed
        # to ensure any random choices in GCA are the same.
        seed(43)
        r_true = self.ec2.execute(ggc, (a, b, c, True))
        self.assertEqual(r_true, r_true_expected)

        # Execute the IF_THEN_ELSE GC with condition False. Need the same seed
        # to ensure any random choices in GCB are the same.
        seed(44)
        r_false = self.ec2.execute(ggc, (a, b, c, False))
        self.assertEqual(r_false, r_false_expected)

        # Do it again with ec1 (different line limit)
        # self.ec1.write_executable(ggc)
        # write_context_to_file(self.ec1, "temp.md", oft=OutputFileType.MARKDOWN)
        seed(43)
        r_true = self.ec1.execute(ggc, (a, b, c, True))
        self.assertEqual(r_true, r_true_expected)
        seed(44)
        r_false = self.ec1.execute(ggc, (a, b, c, False))
        self.assertEqual(r_false, r_false_expected)

    def test_for_loop_simple(self) -> None:
        """Test FOR_LOOP generation and execution."""
        # Create a simple FOR_LOOP GC
        # Iterate over a tuple of integers and accumulate them using rshift_xor.
        # L: Tuple of ints (Iterable)
        # S: Initial state (int)
        # A: Body (takes state and item, returns new state)
        # T: Next state (from A)
        # O: Final state (from A)

        # rshift_xor takes 2 inputs.
        # We need to map L item and S state to rshift_xor inputs.
        # rshift_xor inputs: 0->GCB(xor) input 0, 1->GCA(rshift_1) input 0.
        # Let's say S -> Input 0, L item -> Input 1.

        body_gc = primitive_gcs["rshift_xor"]

        # Properties for FOR_LOOP
        props = PropertiesBD(
            {"gc_type": GCType.ORDINARY, "graph_type": CGraphType.FOR_LOOP}
        ).to_int()

        ggc = inherit_members(
            {
                "ancestora": body_gc,
                "ancestorb": NULL_SIGNATURE,
                "gca": body_gc,
                "gcb": NULL_SIGNATURE,
                "cgraph": {
                    "L": [["I", 0, "tuple"]],  # Iterable input
                    "S": [["I", 1, INT_T]],  # Initial State
                    "A": [["S", 0, INT_T], ["L", 0, INT_T]],  # Body inputs: State, Item
                    "T": [["A", 0, INT_T]],  # Next State
                    "O": [["A", 0, INT_T]],  # Output
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": props,
                "num_codons": body_gc["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        # write_function_to_file(self.ec2, ggc, "temp.md", oft=OutputFileType.MARKDOWN)

        # Execute
        # Inputs: (Iterable, Initial State)
        iterable = (1, 2, 3)
        initial_state = 0
        # Expected result:
        # Iter 1: state=0, item=1 -> rshift_xor(0, 1) = 0 ^ (1 >> 1) = 0 ^ 0 = 0
        # Iter 2: state=0, item=2 -> rshift_xor(0, 2) = 0 ^ (2 >> 1) = 0 ^ 1 = 1
        # Iter 3: state=1, item=3 -> rshift_xor(1, 3) = 1 ^ (3 >> 1) = 1 ^ 1 = 0

        s = initial_state
        for i in iterable:
            # rshift_xor(s, i) = s ^ (i >> 1)
            s = s ^ (i >> 1)
        expected = s

        result = self.ec2.execute(ggc, (iterable, initial_state))
        self.assertEqual(result, expected)

    def test_while_loop_simple(self) -> None:
        """Test WHILE_LOOP generation and execution."""
        # Create a simple WHILE_LOOP GC
        # W: Initial Condition (bool)
        # S: Initial State (int)
        # A: Body (takes State, returns Next State, Next Condition)
        # X: Next Condition
        # T: Next State
        # O: Output (State)

        # Use rshift_1 as body.
        # rshift_1 takes 1 input, returns 1 output (input >> 1).
        # We map T -> A0, X -> A0.
        # Loop terminates when s >> 1 is 0.

        body_gc = primitive_gcs["rshift_1"]

        # Properties for WHILE_LOOP
        props = PropertiesBD(
            {"gc_type": GCType.ORDINARY, "graph_type": CGraphType.WHILE_LOOP}
        ).to_int()

        ggc = inherit_members(
            {
                "ancestora": body_gc,
                "ancestorb": NULL_SIGNATURE,
                "gca": body_gc,
                "gcb": NULL_SIGNATURE,
                "cgraph": {
                    "W": [["I", 0, "bool"]],  # Initial Condition
                    "S": [["I", 1, INT_T]],  # Initial State
                    "A": [["S", 0, INT_T]],  # Body inputs: State
                    "T": [["A", 0, INT_T]],  # Next State
                    "X": [["A", 0, INT_T]],  # Next Condition (Same as state)
                    "O": [["A", 0, INT_T]],  # Output
                },
                "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                "problem": ACYBERGENESIS_PROBLEM,
                "properties": props,
                "num_codons": body_gc["num_codons"],
            },
            True,
        )
        self.ec2.write_executable(ggc)
        write_function_to_file(self.ec2, ggc, "temp.md", oft=OutputFileType.MARKDOWN)

        initial_state = 16
        initial_cond = True

        # Expected:
        # 16 -> 8 (True)
        # 8 -> 4 (True)
        # 4 -> 2 (True)
        # 2 -> 1 (True)
        # 1 -> 0 (False) -> Loop terminates.
        # Output should be 0.

        result = self.ec2.execute(ggc, (initial_cond, initial_state))
        self.assertEqual(result, 0)
