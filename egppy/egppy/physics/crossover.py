"""The crossover module implements crossover operations for genetic codes."""

from egppy.genetic_code.genetic_code import GCABC
from egppy.physics.pgc_api import EGCode
from egppy.physics.runtime_context import RuntimeContext


def crossover(rtctxt: RuntimeContext, psite1: GCABC, psite2: GCABC, a: bool) -> EGCode:
    """Crossover GCA (if a is True) or GCB (if a is False) from psite2 into psite1.

    Args:
        rtctxt: The runtime context containing the gene pool and other necessary information.
        psite1: The first parent GC which is, or is a sub-GC of, rtctxt.root_gc.
        psite2: The second parent GC which is, or is a sub-GC of, rtctxt.other_gc.
        a: If True, crossover GCA from psite2 into psite1 GCA. If False, crossover GCB from
           psite2 into psite1 GCB.
    Returns:
        The modified psite1 (rgc) with the specified crossover applied. rgc is a newly created EGCode
        the same as psite1 except with the specified crossover applied. psite1 is not modified.
    """
