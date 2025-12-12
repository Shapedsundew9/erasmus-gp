"""Store Base class module."""

from egpcommon.common_obj import CommonObj
from egpcommon.common_obj_abc import CommonObjABC
from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.store.storable_obj_abc import StorableObjABC

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


class StoreBase(CommonObj, CommonObjABC):
    """Store Base class has methods generic to all store classes."""

    def __init__(
        self, flavor: type[StorableObjABC], load_flavor: type[StorableObjABC] | None = None
    ) -> None:
        """All stores must have a flavor and optionally a load flavor.
        The flavor is the type of object that the store stores.
        The load flavor is the type of object that the store loads.
        If the load flavor is not provided, it defaults to the flavor.
        Args:
            flavor (type[StorableObjABC]): The type of object that the store stores.
            load_flavor (type[StorableObjABC] | None, optional): The type of object that
            the store loads. Defaults to None.
        """
        self.flavor: type[StorableObjABC] = flavor
        self.load_flavor: type[StorableObjABC] = load_flavor if load_flavor is not None else flavor
