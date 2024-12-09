"""The Interface End Point Type Definition class."""

from typing import Iterable

from egppy.gc_graph.end_point.end_point_type import (
    ITIDX1_MASK,
    ITIDX1_POS,
    ITIDX2_MASK,
    ITIDX2_POS,
    EndPointType,
)
from egppy.gc_graph.end_point.end_point_type_abc import EndPointTypeABC


class IEPTypeDef:
    """Interface End Point Type Definition class."""

    def __init__(self, epuids: Iterable[int | EndPointTypeABC]) -> None:
        """Initialize the Interface End Point Type Definition."""
        self._epuids: list[int | EndPointTypeABC] = list(epuids)
