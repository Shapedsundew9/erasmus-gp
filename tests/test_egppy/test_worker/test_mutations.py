"""Unit tests for the executor function."""

import unittest
from functools import partial
from itertools import product
from random import getrandbits, seed

from egpcommon.common import ACYBERGENESIS_PROBLEM
from egpcommon.egp_log import DEBUG, TRACE, Logger, egp_logger
from egppy.genetic_code.c_graph_constants import DstIfKey, SrcIfKey
from egppy.physics.helpers import empty_egc, literal_codon
from egppy.physics.insertion import InsertionCase, insert
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext
from egppy.physics.stabilization import stabilize_gc
from egppy.physics.wrap import WrapCase, wrap
from egppy.worker.executor.ec_logger import gc_mermaid_cg
from egppy.worker.executor.execution_context import ExecutionContext
from tests.test_egppy.test_worker.xor_stack_gc import (
    BASIC_ORDINARY_PROPERTIES,
    CODON_SIGS,
    INT_TD,
    create_primitive_gcs,
    gpi,
    inherit_members,
    primitive_gcs,
)

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Constants
NUM_TEST_FUNCS = 10
assert NUM_TEST_FUNCS > 4, "Need at least 4 test functions to test all wrap and insert cases."


class TestExecutor(unittest.TestCase):
    """Unit tests for the executor function."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class method for test setup."""
        cls.gpi = gpi
        cls.ec = ExecutionContext(cls.gpi, 50)
        create_primitive_gcs()

        # Create a set of random 64-bit integers for testing and
        # add them as literal codons to the primitive GCs
        seed(42)
        cls.c64 = tuple(getrandbits(64) for _ in range(NUM_TEST_FUNCS))
        cls.funcs = [partial(lambda x, c: (x >> 1) ^ c, c=i) for i in cls.c64]
        cls.rtctxt = RuntimeContext(gpi)
        primitive_gcs.update(
            {
                f"constant_{i}": gpi.add(literal_codon(cls.rtctxt, c, INT_TD))
                for i, c in enumerate(cls.c64)
            }
        )

        # Make a shift-xor function for each integer and add to the primitive GCs
        # in the execution context
        for i in range(len(cls.c64)):
            primitive_gcs[f"rsx_{i}"] = inherit_members(
                {
                    "ancestorb": primitive_gcs["rshift_xor"],
                    "ancestora": primitive_gcs[f"constant_{i}"],
                    "gcb": primitive_gcs["rshift_xor"],
                    "gca": primitive_gcs[f"constant_{i}"],
                    "cgraph": {
                        "A": [],
                        "B": [
                            ["A", 0, INT_TD.name],
                            ["I", 0, INT_TD.name],
                        ],
                        "O": [["B", 0, INT_TD.name]],
                    },
                    "pgc": gpi[CODON_SIGS["CUSTOM_PGC_SIG"]],
                    "problem": ACYBERGENESIS_PROBLEM,
                    "properties": BASIC_ORDINARY_PROPERTIES,
                }
            )
            cls.ec.write_executable(primitive_gcs[f"rsx_{i}"])

    def test_insertion_golden_reference(self):
        """To test the wrapping and inserting functionality we use a golden reference
        model approach. This test case validates the golden reference model behaves as
        expected. It is really a convinience for developing the actual tests.

        The model used is a stack of XOR operations. The stack is initialised with a set of
        random 64-bit integers. The model then applies a sequence of shift-XOR operations, each
        time using one of the initial integers. The final results are collected and checked
        for uniqueness.

        The test ensures that the combination of operations produces unique results for
        each unique combination of operations and inputs. This provides a framework for
        testing that wrapping and insertion of genetic codes behaves as expected.
        """
        result_set = set()
        for func_combo in product(self.funcs[:4], repeat=4):
            for input_value in self.c64:
                result = input_value
                for func in func_combo:
                    result = func(result)
                self.assertNotIn(result, result_set)
                result_set.add(result)

    def test_functional_equivalence(self):
        """Test the golden reference functions and the primitive genetic code
        implementations are functionally equivalent.
        """
        for i, func in enumerate(self.funcs):
            gc = primitive_gcs[f"rsx_{i}"]
            # Execute the genetic code
            gc_result = self.ec.execute(gc, (0xFFFFFFFFFFFFFFFF,))

            # Compute the golden reference result
            golden_result = func(0xFFFFFFFFFFFFFFFF)

            # Assert equivalence
            self.assertEqual(
                gc_result,
                golden_result,
                f"Genetic code result {gc_result} does not match "
                f"golden reference {golden_result} for input {0xFFFFFFFFFFFFFFFF}",
            )

    def test_wrap(self):
        """Test the set of wrapping functions with direct connections."""
        for fnum in range(len(self.funcs) >> 1):
            f1num = fnum * 2
            f2num = fnum * 2 + 1
            igc = primitive_gcs[f"rsx_{f1num}"]
            tgc = primitive_gcs[f"rsx_{f2num}"]
            ifunc = self.funcs[f1num]
            tfunc = self.funcs[f2num]
            ival = getrandbits(64)

            # Add empty egc as wrapper
            rgc = empty_egc(self.rtctxt, igc["cgraph"][SrcIfKey.IS], tgc["cgraph"][DstIfKey.OD])

            for wc in WrapCase:
                match wc:
                    case WrapCase.STACK:
                        rgc = wrap(self.rtctxt, igc, tgc, wc)
                        stabilized_rgc = stabilize_gc(self.rtctxt, rgc)
                        # Execute the wrapped genetic code
                        rgc_result = self.ec.execute(stabilized_rgc, (ival,))
                        # Compute the golden reference result
                        golden_result = ifunc(tfunc(ival))
                    case WrapCase.ISTACK:
                        rgc = wrap(self.rtctxt, igc, tgc, wc)
                        stabilized_rgc = stabilize_gc(self.rtctxt, rgc)
                        # Execute the wrapped genetic code
                        rgc_result = self.ec.execute(stabilized_rgc, (ival,))
                        # Compute the golden reference result
                        golden_result = tfunc(ifunc(ival))
                    case WrapCase.WRAP:
                        rgc = wrap(self.rtctxt, igc, tgc, wc, rgc)
                        stabilized_rgc = stabilize_gc(self.rtctxt, rgc)
                        # Execute the wrapped genetic code
                        rgc_result = self.ec.execute(stabilized_rgc, (ival,))
                        # Compute the golden reference result
                        golden_result = ifunc(tfunc(ival))
                    case WrapCase.IWRAP:
                        rgc = wrap(self.rtctxt, igc, tgc, wc, rgc)
                        stabilized_rgc = stabilize_gc(self.rtctxt, rgc)
                        # Execute the wrapped genetic code
                        rgc_result = self.ec.execute(stabilized_rgc, (ival,))
                        # Compute the golden reference result
                        golden_result = tfunc(ifunc(ival))
                    case WrapCase.HARMONY:
                        rgc_result = golden_result = 0
                    case _:
                        self.fail(f"Unknown wrap case: {wc}")

                # Assert equivalence
                self.assertEqual(
                    rgc_result,
                    golden_result,
                    f"Wrapped genetic code result {rgc_result} does not match "
                    f"golden reference {golden_result} for input {ival} "
                    f"with wrap case {wc.name}",
                )

    def test_insert(self):
        """Test the set of insert functions with direct connections."""
        # Create a parent EGCode to insert into.
        # This will become the tgc (target genetic code) for the insertions.
        tgc1 = primitive_gcs["rsx_0"]
        igc1 = primitive_gcs["rsx_1"]
        rgc = wrap(self.rtctxt, igc1, tgc1, WrapCase.STACK)
        tgc = stabilize_gc(self.rtctxt, rgc)
        if _logger.isEnabledFor(TRACE):
            # Mermaid graph creation is expensive so we only do it if trace logging is enabled.
            _logger.log(
                TRACE, "Initial tgc created for insertion tests:\n%s", gc_mermaid_cg(self.gpi, tgc)
            )

        # Golden reference is a sequence of calls to the functions in the correct order.
        tfunc = (self.funcs[0], self.funcs[1])

        # Make sure the result of the tgc matches the golden reference before insertion
        tgc_result = self.ec.execute(tgc, (0xFFFFFFFFFFFFFFFF,))
        golden_result = tfunc[1](tfunc[0](0xFFFFFFFFFFFFFFFF))
        self.assertEqual(
            tgc_result,
            golden_result,
            f"Pre-insertion tgc result {tgc_result} does not match "
            f"golden reference {golden_result} for input {0xFFFFFFFFFFFFFFFF}",
        )

        # Test each insertion case
        # TODO: Need to implement this test when stablization and insertion are fully implemented.
        for fnum in range(2, len(self.funcs)):
            igc = primitive_gcs[f"rsx_{fnum}"]
            ifunc = self.funcs[fnum]
            ival = getrandbits(64)

            for ic in InsertionCase:
                pass


if __name__ == "__main__":
    unittest.main()
