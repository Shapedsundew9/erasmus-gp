"""Genetic Code Class Factory"""
from typing import Type, Callable, Any
from egppy.gc_types.gc_abc import GCABC
from egppy.gc_types.dict_base_gc import DictBaseGC
from egppy.gc_types.null_gc import NULL_GC


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

    cls_name: str = cls.__name__.replace("Base", "E")
    cls_methods: dict[str, Callable] = {
        '__init__': __init__,
    }
    return type(cls_name, (DictBaseGC,), cls_methods)


DictEGC: Type[GCABC] = egc_class_factory(cls=DictBaseGC)
