"""Embryonic Genetic Code Class Factory

An Embryonic Genetic Code, EGC, is the 'working' genetic code object. It is most practically
used with the DictBaseGC class for performance but theoretically can be used with any genetic
code class. As a working genetic code object, it only contains the essentials of what make a
genetic code object avoiding all the derived data.
"""
from typing import Type, Callable, Any
from logging import Logger, NullHandler, getLogger, DEBUG
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.dirty_dict_base_gc import DirtyDictBaseGC
from egppy.gc_types.dict_base_gc import DictBaseGC
from egppy.gc_types.null_gc import NULL_GC
from egppy.gc_types.gc_illegal import GCIllegal


# Standard EGP logging pattern
_logger: Logger = getLogger(name=__name__)
_logger.addHandler(hdlr=NullHandler())
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)


def egc_class_factory(cls: Type[GCABC]) -> Type[GCABC]:
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
        super(cls, self).__init__(
            graph=gcabc.get('graph', {}),  # type: ignore
            gca=gcabc.get('gca', NULL_GC),  # type: ignore
            gcb=gcabc.get('gcb', NULL_GC),  # type: ignore
            ancestora=gcabc.get('ancestora', NULL_GC),  # type: ignore
            ancestorb=gcabc.get('ancestorb', NULL_GC),  # type: ignore
            pgc=gcabc.get('pgc', NULL_GC)  # type: ignore
        )
        self.dirty()

    cls_name: str = cls.__name__.replace("Base", "E")
    cls_methods: dict[str, Callable] = {
        '__init__': __init__,
    }
    return type(cls_name, (GCIllegal, cls), cls_methods)


DirtyDictEGC: Type[GCABC] = egc_class_factory(cls=DirtyDictBaseGC)
DictEGC: Type[GCABC] = egc_class_factory(cls=DictBaseGC)
