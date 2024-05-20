"""Universal Genetic Code Class Factory.

A Universal Genetic Code, UGC, is the 'bucket' genetic code object. It is most practically
used for testing or as a placeholder but can be used in less resource intensive applications
for simplicity. The UGC allows any values to be stored in the genetic code object and can
by considered to be a dict[str, Any] object with the additional constraints of the GCABC.
"""
from typing import Type, Callable, Any
from logging import Logger, NullHandler, getLogger, DEBUG
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.dirty_dict_base_gc import DirtyDictBaseGC
from egppy.gc_types.dict_base_gc import DictBaseGC
from egppy.gc_types.gc_illegal import GCIllegal


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


def ugc_class_factory(cls: Type[GCABC]) -> Type[GCABC]:
    """Create a genetic code object.

    Wraps the cls methods and adds derived methods to create a genetic code object.
    The cls must be a subclass of GCABC.

    Args:
        cls: The genetic code base class to wrap.

    Returns:
        A genetic code object.
    """
    if not issubclass(cls, GCABC):
        raise ValueError("cls must be a subclass of GCABC")

    def __init__(self, *args, **kwargs) -> None:
        """Constructor for GC."""
        gcabc: GCABC | dict[str, Any] = args[0] if args else kwargs
        super(cls, self).__init__(gcabc)  # type: ignore

    cls_name: str = cls.__name__.replace("Base", "U")
    cls_methods: dict[str, Callable] = {
        '__init__': __init__,
    }
    return type(cls_name, (GCIllegal, DictBaseGC,), cls_methods)


DirtyDictUGC: Type[GCABC] = ugc_class_factory(cls=DirtyDictBaseGC)
DictUGC: Type[GCABC] = ugc_class_factory(cls=DictBaseGC)
