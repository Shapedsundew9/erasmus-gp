"""The selectors module."""

from egpcommon.properties import CODON_MASK
from egppy.genetic_code.ggc_dict import GGCDict
from egppy.genetic_code.types_def_store import types_def_store
from egppy.physics.runtime_context import RuntimeContext


def _expand_types_ancestors(types: list[int]) -> list[int]:
    """Expand type UIDs to include all ancestor UIDs.

    For each type UID in the input, finds all ancestors in the type hierarchy
    and returns a deduplicated sorted list of all UIDs (including the originals).

    Note:
        Covers direct inheritance only.
        TODO: Add covariance expansion for generic/templated types (e.g.,
        list[int] compatible with list[Integral]).

    Args:
        types: List of TypesDef UIDs to expand.

    Returns:
        Sorted deduplicated list of ancestor type UIDs.
    """
    expanded: set[int] = set()
    for type_uid in types:
        for td in types_def_store.ancestors(type_uid):
            expanded.add(td.uid)
    return sorted(expanded)


def _expand_types_descendants(types: list[int]) -> list[int]:
    """Expand type UIDs to include all descendant UIDs.

    For each type UID in the input, finds all descendants in the type hierarchy
    and returns a deduplicated sorted list of all UIDs (including the originals).

    Note:
        Covers direct inheritance only.
        TODO: Add covariance expansion for generic/templated types (e.g.,
        list[Integral] producing list[int] descendants).

    Args:
        types: List of TypesDef UIDs to expand.

    Returns:
        Sorted deduplicated list of descendant type UIDs.
    """
    expanded: set[int] = set()
    for type_uid in types:
        for td in types_def_store.descendants(type_uid):
            expanded.add(td.uid)
    return sorted(expanded)


def random_codon_selector(rtctxt: RuntimeContext) -> GGCDict:
    """Select a random codon from the gene pool.

    This function uses the runtime context to access the gene pool interface
    and select a random codon genetic code.

    Args:
        rtctxt: The runtime context.
    Returns:
        GGCDict: A random codon genetic code.
    """
    ggc = rtctxt.gpi.select_gc(
        "{codon_mask} & {properties} = {zero}",
        literals={"codon_mask": CODON_MASK, "zero": 0},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_pgc_selector(rtctxt: RuntimeContext) -> GGCDict:
    """Select a random PGC (mutation) from the gene pool.

    This function uses the runtime context to access the gene pool interface
    and select a random PGC (mutation) genetic code.

    Args:
        rtctxt: The runtime context.
    Returns:
        GGCDict: A random PGC (mutation) genetic code.
    """
    # Any GC returning an EGCode output type is a valid mutation candidate.
    ggc = rtctxt.gpi.select_gc(
        "{output_types} @> ARRAY[{eg_code_td}]::INT[]",
        literals={"eg_code_td": types_def_store["EGCode"].uid},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Exact Type Match (= operator) ---
# GC types must exactly equal the requested types (same types, order, and length).


def random_exact_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC with exactly matching input and output types.

    Args:
        rtctxt: The runtime context.
        input_types: Required input type UIDs (exact match).
        output_types: Required output type UIDs (exact match).

    Returns:
        A random GC whose input_types and output_types exactly equal the given arrays.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} = {itypes}::INT[] AND {output_types} = {otypes}::INT[]",
        literals={"itypes": input_types, "otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_exact_input_selector(rtctxt: RuntimeContext, input_types: list[int]) -> GGCDict:
    """Select a random GC with exactly matching input types.

    Args:
        rtctxt: The runtime context.
        input_types: Required input type UIDs (exact match).

    Returns:
        A random GC whose input_types exactly equals the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} = {itypes}::INT[]",
        literals={"itypes": input_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_exact_output_selector(rtctxt: RuntimeContext, output_types: list[int]) -> GGCDict:
    """Select a random GC with exactly matching output types.

    Args:
        rtctxt: The runtime context.
        output_types: Required output type UIDs (exact match).

    Returns:
        A random GC whose output_types exactly equals the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{output_types} = {otypes}::INT[]",
        literals={"otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Subset Match (<@ operator) ---
# GC types are contained within (subset of) the requested types.


def random_subset_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC whose input and output types are subsets of the given types.

    Args:
        rtctxt: The runtime context.
        input_types: Allowed input type UIDs (GC inputs must be a subset).
        output_types: Allowed output type UIDs (GC outputs must be a subset).

    Returns:
        A random GC whose types are subsets of the given arrays.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} <@ {itypes}::INT[] AND {output_types} <@ {otypes}::INT[]",
        literals={"itypes": input_types, "otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_subset_input_selector(rtctxt: RuntimeContext, input_types: list[int]) -> GGCDict:
    """Select a random GC whose input types are a subset of the given types.

    Args:
        rtctxt: The runtime context.
        input_types: Allowed input type UIDs (GC inputs must be a subset).

    Returns:
        A random GC whose input_types is a subset of the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} <@ {itypes}::INT[]",
        literals={"itypes": input_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_subset_output_selector(rtctxt: RuntimeContext, output_types: list[int]) -> GGCDict:
    """Select a random GC whose output types are a subset of the given types.

    Args:
        rtctxt: The runtime context.
        output_types: Allowed output type UIDs (GC outputs must be a subset).

    Returns:
        A random GC whose output_types is a subset of the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{output_types} <@ {otypes}::INT[]",
        literals={"otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Superset Match (@> operator) ---
# GC types contain (are a superset of) all the requested types.


def random_superset_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC whose input and output types are supersets of the given types.

    Args:
        rtctxt: The runtime context.
        input_types: Required input type UIDs (GC inputs must contain all).
        output_types: Required output type UIDs (GC outputs must contain all).

    Returns:
        A random GC whose types are supersets of the given arrays.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} @> {itypes}::INT[] AND {output_types} @> {otypes}::INT[]",
        literals={"itypes": input_types, "otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_superset_input_selector(rtctxt: RuntimeContext, input_types: list[int]) -> GGCDict:
    """Select a random GC whose input types are a superset of the given types.

    Args:
        rtctxt: The runtime context.
        input_types: Required input type UIDs (GC inputs must contain all).

    Returns:
        A random GC whose input_types is a superset of the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} @> {itypes}::INT[]",
        literals={"itypes": input_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_superset_output_selector(rtctxt: RuntimeContext, output_types: list[int]) -> GGCDict:
    """Select a random GC whose output types are a superset of the given types.

    Args:
        rtctxt: The runtime context.
        output_types: Required output type UIDs (GC outputs must contain all).

    Returns:
        A random GC whose output_types is a superset of the given array.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{output_types} @> {otypes}::INT[]",
        literals={"otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Overlap Match (&& operator) ---
# GC types share at least one type in common with the requested types.


def random_overlap_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC whose input and output types overlap with the given types.

    At least one input type and at least one output type must be in common.

    Args:
        rtctxt: The runtime context.
        input_types: Input type UIDs to overlap with.
        output_types: Output type UIDs to overlap with.

    Returns:
        A random GC with overlapping input and output types.

    Raises:
        KeyError: If no matching GC is found.
    """
    ggc = rtctxt.gpi.select_gc(
        "{input_types} && {itypes}::INT[] AND {output_types} && {otypes}::INT[]",
        literals={"itypes": input_types, "otypes": output_types},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Compatible Type Match (ancestor/descendant expansion + && operator) ---
# Types are expanded via inheritance hierarchy before querying.
# Input types are expanded to ancestors (a GC expecting an ancestor type can accept our data).
# Output types are expanded to descendants (a GC producing a descendant type satisfies our need).


def random_compatible_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC with type-compatible inputs and outputs.

    Input types are expanded to include ancestors (upcast-compatible) and output
    types are expanded to include descendants. The GC must overlap with both
    expanded sets.

    Args:
        rtctxt: The runtime context.
        input_types: Input type UIDs to match (expanded via ancestors).
        output_types: Output type UIDs to match (expanded via descendants).

    Returns:
        A random GC with type-compatible inputs and outputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_inputs = _expand_types_ancestors(input_types)
    expanded_outputs = _expand_types_descendants(output_types)
    ggc = rtctxt.gpi.select_gc(
        "{input_types} && {itypes}::INT[] AND {output_types} && {otypes}::INT[]",
        literals={"itypes": expanded_inputs, "otypes": expanded_outputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_compatible_input_selector(rtctxt: RuntimeContext, input_types: list[int]) -> GGCDict:
    """Select a random GC with type-compatible inputs.

    Input types are expanded to include all ancestor types (upcast-compatible).
    The GC must have at least one input type in the expanded set.

    Args:
        rtctxt: The runtime context.
        input_types: Input type UIDs to match (expanded via ancestors).

    Returns:
        A random GC with type-compatible inputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_inputs = _expand_types_ancestors(input_types)
    ggc = rtctxt.gpi.select_gc(
        "{input_types} && {itypes}::INT[]",
        literals={"itypes": expanded_inputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_compatible_output_selector(rtctxt: RuntimeContext, output_types: list[int]) -> GGCDict:
    """Select a random GC with type-compatible outputs.

    Output types are expanded to include all descendant types. The GC must
    have at least one output type in the expanded set.

    Args:
        rtctxt: The runtime context.
        output_types: Output type UIDs to match (expanded via descendants).

    Returns:
        A random GC with type-compatible outputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_outputs = _expand_types_descendants(output_types)
    ggc = rtctxt.gpi.select_gc(
        "{output_types} && {otypes}::INT[]",
        literals={"otypes": expanded_outputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


# --- Downcast-Compatible Type Match (reverse expansion + && operator) ---
# The reverse of compatible matching: input types are expanded via descendants
# (a GC expecting a more specific type) and output types via ancestors (a GC
# producing a more general type). This enables downcasting which may cause
# runtime errors if the actual object type does not match.


def random_downcast_io_selector(
    rtctxt: RuntimeContext, input_types: list[int], output_types: list[int]
) -> GGCDict:
    """Select a random GC with downcast-compatible inputs and outputs.

    Input types are expanded to include descendants (downcast) and output types
    are expanded to include ancestors. The GC must overlap with both expanded sets.

    Warning:
        Downcasting is not type-safe and may cause runtime errors if the actual
        object type does not match the expected specific type.

    Args:
        rtctxt: The runtime context.
        input_types: Input type UIDs to match (expanded via descendants).
        output_types: Output type UIDs to match (expanded via ancestors).

    Returns:
        A random GC with downcast-compatible inputs and outputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_inputs = _expand_types_descendants(input_types)
    expanded_outputs = _expand_types_ancestors(output_types)
    ggc = rtctxt.gpi.select_gc(
        "{input_types} && {itypes}::INT[] AND {output_types} && {otypes}::INT[]",
        literals={"itypes": expanded_inputs, "otypes": expanded_outputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_downcast_input_selector(rtctxt: RuntimeContext, input_types: list[int]) -> GGCDict:
    """Select a random GC with downcast-compatible inputs.

    Input types are expanded to include all descendant types (downcast).
    The GC must have at least one input type in the expanded set.

    Warning:
        Downcasting is not type-safe and may cause runtime errors.

    Args:
        rtctxt: The runtime context.
        input_types: Input type UIDs to match (expanded via descendants).

    Returns:
        A random GC with downcast-compatible inputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_inputs = _expand_types_descendants(input_types)
    ggc = rtctxt.gpi.select_gc(
        "{input_types} && {itypes}::INT[]",
        literals={"itypes": expanded_inputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc


def random_downcast_output_selector(rtctxt: RuntimeContext, output_types: list[int]) -> GGCDict:
    """Select a random GC with downcast-compatible outputs.

    Output types are expanded to include all ancestor types (downcast).
    The GC must have at least one output type in the expanded set.

    Warning:
        Downcasting is not type-safe and may cause runtime errors.

    Args:
        rtctxt: The runtime context.
        output_types: Output type UIDs to match (expanded via ancestors).

    Returns:
        A random GC with downcast-compatible outputs.

    Raises:
        KeyError: If no matching GC is found.
    """
    expanded_outputs = _expand_types_ancestors(output_types)
    ggc = rtctxt.gpi.select_gc(
        "{output_types} && {otypes}::INT[]",
        literals={"otypes": expanded_outputs},
        order_by="ORDER BY RANDOM()",
    )
    return GGCDict(ggc) if not isinstance(ggc, GGCDict) else ggc
