"""Types Definition class for EGP Seed."""

from __future__ import annotations

from collections import Counter
from collections.abc import Container
from itertools import count
from os.path import dirname, join
from typing import Iterator, Iterable

from egpcommon.common import NULL_TUPLE, DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.object_set import ObjectSet
from egpcommon.security import load_signed_json
from egpcommon.validator import Validator

from egppy.c_graph.end_point.import_def import ImportDef, import_def_store

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# End Point Type UID Bitfield Constants
XUID_POS: int = 0
XUID_LEN: int = 16
XUID_MASK: int = ((1 << XUID_LEN) - 1) << XUID_POS
XUID_MAX = (1 << XUID_LEN) - 1
Y_POS: int = 0
Y_LEN: int = 4
Y_MASK: int = ((1 << Y_LEN) - 1) << Y_POS
Y_MAX = (1 << Y_LEN) - 1
X_POS: int = 8
X_LEN: int = 6
X_MASK: int = ((1 << X_LEN) - 1) << X_POS
X_MAX = (1 << X_LEN) - 1
FX_POS: int = 24
FX_LEN: int = 3
FX_MASK: int = ((1 << FX_LEN) - 1) << FX_POS
FX_MAX = (1 << FX_LEN) - 1
IO_POS: int = 27
IO_LEN: int = 1
IO_MASK: int = ((1 << IO_LEN) - 1) << IO_POS
IO_MAX = (1 << IO_LEN) - 1
TT_POS: int = 28
TT_LEN: int = 3
TT_MASK: int = ((1 << TT_LEN) - 1) << TT_POS
TT_MAX = (1 << TT_LEN) - 1
XY_RESERVED_MASK: int = ~(X_MASK | Y_MASK) & 0xFFFF


# XUID counters
# FIXME: Only used for creating the first types database. Once deployed XUIDs cannot change.
XUID_COUNTERS = {tt: count() for tt in range(1 + TT_MAX)}


class TypesDef(Validator, DictTypeAccessor):
    """Type Definition class for EGP Seed. Stores the type UID
    and instanciation information."""

    __slots__ = (
        "_name",
        "_uid",
        "_default",
        "_imports",
        "_inherits",
        "abstract",
        "meta",
        "derived",
        "_max_depth",
        "_min_depth",
    )

    def __init__(
        self,
        name: str,
        xuid: int = -1,
        tt: int = 0,
        io: int = 0,
        fx: int = 0,
        abstract: bool = False,
        meta: bool = False,
        default: str | None = None,
        imports: Iterable[ImportDef] | dict | None = None,
        inherits: Iterable[str | TypesDef] | None = None,
    ) -> None:
        """Initialize Type Definition.

        Args:
            name: Name of the type  definition.
            uid: Unique identifier of the type  definition.
            default: Executable python default instanciation of the type.
            imports: List of import definitions.
        """
        assert (tt == fx == 0 and io == 1) or io == 0, "TT and FX must be 0 if IO is set."
        assert not (abstract and meta), "Type cannot be both abstract and meta."
        assert 0 <= tt <= TT_MAX, "TT must be in range 0 to TT_MAX."
        assert 0 <= io <= IO_MAX, "IO must be in range 0 to IO_MAX."
        assert 0 <= fx <= FX_MAX, "FX must be in range 0 to FX_MAX."

        # FIXME: For creation - remove after deployment
        if xuid == -1:
            # deepcode ignore unguarded~next~call: Infinite counters are fine here.
            xuid = next(XUID_COUNTERS[tt])
        assert 0 <= xuid <= XUID_MAX, "XUID must be in range 0 to XUID_MAX."
        assert (
            xuid & XY_RESERVED_MASK == 0
        ) or io == 0, (
            f"XUID 0x{xuid:04x} reserved bits 0x{XY_RESERVED_MASK:04x} must be 0 if IO is set."
        )

        uid = (xuid << XUID_POS) | (tt << TT_POS) | (io << IO_POS) | (fx << FX_POS)
        setattr(self, "name", name)
        self.abstract = abstract
        self.meta = meta
        setattr(self, "uid", uid)
        setattr(self, "default", default)
        setattr(self, "imports", imports)
        setattr(self, "inherits", inherits)
        self.derived: tuple[TypesDef, ...] = NULL_TUPLE
        self._max_depth: int = -1
        self._min_depth: int = -1

    def __hash__(self) -> int:
        """Return globally unique hash for the object.
        TypeDefs are unique by design and should not be duplicated.
        """
        return id(self)

    @property
    def name(self) -> str:
        """Return name of the type template definition."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set name of the type template definition."""
        self._is_string("name", name)
        self._is_length("name", name, 1, 64)
        self._is_printable_string("name", name)
        self._name = name

    @property
    def uid(self) -> int:
        """Return unique identifier of the type template definition."""
        return self._uid

    @uid.setter
    def uid(self, uid: int) -> None:
        """Set unique identifier of the type template definition."""
        self._is_int("uid", uid)
        self._in_range("uid", uid, 0, 2**31 - 1)
        self._uid = uid

    @property
    def default(self) -> str | None:
        """Return default instanciation of the type template definition."""
        return self._default

    @default.setter
    def default(self, default: str | None) -> None:
        """Set default instanciation of the type template definition."""
        if default is not None:
            self._is_string("default", default)
            self._is_length("default", default, 1, 128)
            self._is_printable_string("default", default)
        self._default = default

    @property
    def imports(self) -> tuple[ImportDef, ...]:
        """Return list of import definitions of the type template definition."""
        return self._imports

    @imports.setter
    def imports(self, imports: list[ImportDef] | dict | None) -> None:
        """Set list of import definitions of the type template definition."""
        if imports is None or not imports:
            self._imports: tuple[ImportDef, ...] = NULL_TUPLE
            return
        # If it is already a tuple no need to copy it. Saves memory.
        if isinstance(imports, tuple) and isinstance(imports[0], ImportDef):
            assert all(
                impt in import_def_store for impt in imports
            ), "ImportDef must be in the import store."
            self._imports = imports
            return
        _imports = []
        for import_def in imports:
            if isinstance(import_def, dict):
                # The import store will ensure that the same import is not duplicated.
                idef = import_def_store.add(ImportDef(**import_def))
                _imports.append(idef)
            elif isinstance(import_def, ImportDef):
                assert import_def in import_def_store, "ImportDef must be in the import store."
                _imports.append(import_def)
            else:
                raise ValueError("Invalid imports definition.")
        self._imports = tuple(_imports)

    @property
    def inherits(self) -> tuple[str, ...] | tuple[TypesDef, ...]:
        """Return list of type names that the type inherits from."""
        return self._inherits

    @inherits.setter
    def inherits(self, inherits: list[str | TypesDef] | None) -> None:
        """Set list of type names or definitions that the type inherits from."""
        if inherits is None or not inherits:
            self._inherits: tuple[str, ...] = NULL_TUPLE
            return
        # If it is already a tuple no need to copy it. Saves memory.
        if isinstance(inherits, tuple) and isinstance(inherits[0], (str, TypesDef)):
            self._inherits = inherits
            return
        _inherits = []
        for inherit in inherits:
            if isinstance(inherit, str):
                self._is_string("inherits", inherit)
                self._is_length("inherits", inherit, 1, 64)
                self._is_printable_string("inherits", inherit)
            _inherits.append(inherit)
        self._inherits = tuple(_inherits)

    def all_derived_types(self) -> set[TypesDef]:
        """Return the set of types that are derived from this type."""
        children = set()
        for derived in self.derived:
            assert isinstance(
                derived, TypesDef
            ), "Derived must be a TypesDef object to search inheritence graph."
            if derived not in children:
                children.add(derived)
                children.update(derived.all_derived_types())
        return children

    def all_inherited_types(self) -> set[TypesDef]:
        """Return the set of all types this type inherits from."""
        parents = set()
        for ancestor in self.inherits:
            assert isinstance(
                ancestor, TypesDef
            ), "Inherits must be a TypesDef object to search inheritence graph."
            if ancestor not in parents:
                parents.add(ancestor)
                parents.update(ancestor.all_inherited_types())
        return parents

    def ept(self) -> tuple[TypesDef, ...]:
        """Return the End Point Type as a tuple of TypesDef objects."""
        return (self,)

    def fx(self) -> int:
        """Return the FX number."""
        return (self.uid & FX_MASK) >> FX_POS

    def inherits_from(self, types_def: TypesDef) -> bool:
        """Return True if the type inherits from the given type."""
        checked = set()
        for ancestor in self.inherits:
            assert isinstance(
                ancestor, TypesDef
            ), "Inherits must be a TypesDef object to search inheritence graph."
            if ancestor not in checked:
                checked.add(ancestor)
                if ancestor == types_def or ancestor.inherits_from(types_def):
                    return True
        return False

    def io(self) -> int:
        """Return the IO number."""
        return (self.uid & IO_MASK) >> IO_POS

    def is_container(self) -> bool:
        """Return True if the type is a container type."""
        return self.tt() > 0

    def max_depth(self) -> int:
        """Return the maximum depth of the type in the inheritance tree."""
        if self._max_depth == -1:
            if not self.inherits:
                self._max_depth = 0
            else:
                self._max_depth = (
                    max(i.max_depth() for i in self.inherits if isinstance(i, TypesDef)) + 1
                )
        return self._max_depth

    def min_depth(self) -> int:
        """Return the minimum depth of the type in the inheritance tree."""
        if self._min_depth == -1:
            if not self.inherits:
                self._min_depth = 0
            else:
                self._min_depth = (
                    min(i.min_depth() for i in self.inherits if isinstance(i, TypesDef)) + 1
                )
        return self._min_depth

    def to_json(self) -> dict:
        """Return Type Definition as a JSON serializable dictionary."""
        return {
            "name": self.name,
            "uid": self.uid,
            "xuid": self.xuid(),
            "fx": self.fx(),
            "io": self.io(),
            "tt": self.tt(),
            "abstract": self.abstract,
            "meta": self.meta,
            "default": self.default,
            "imports": [idef.to_json() for idef in self.imports],
            "inherits": list(self.inherits),
        }

    def tt(self) -> int:
        """Return the Template Type number."""
        return (self.uid & TT_MASK) >> TT_POS

    def xuid(self) -> int:
        """Return the Type XUID."""
        return (self.uid & XUID_MASK) >> XUID_POS


class TypesDB(Container):
    """Types Database.

    Used to look up TypesDefs by name or uid.
    Immutable once initialized.
    """

    def __init__(self, types_filename: str) -> None:
        """Initialize Types Database."""
        self._types_filename = types_filename
        data = load_signed_json(types_filename)
        assert isinstance(data, dict), "Types Database must be a dictionary."
        self._name_key: dict[str, TypesDef] = {k: TypesDef(name=k, **v) for k, v in data.items()}

        # Generate the abstract type fixed versions
        for types_def in tuple(td for td in self._name_key.values() if td.abstract or td.meta):
            for fx in range(1, FX_MAX + 1):
                if fx != types_def.fx():
                    name = f"{types_def.name}{fx}"
                    self._name_key[name] = TypesDef(
                        name=name,
                        xuid=types_def.xuid(),
                        tt=types_def.tt(),
                        io=types_def.io(),
                        fx=fx,
                        abstract=types_def.abstract,
                        meta=types_def.meta,
                        default=types_def.default,
                        imports=types_def.imports,
                        inherits=types_def.inherits,
                    )

        # Generate the output wildcard meta-types
        for x in range(X_MAX + 1):
            for y in range(Y_MAX + 1):
                name = f"egp_wc_{x}_{y}"
                self._name_key[name] = TypesDef(
                    name=name,
                    xuid=(x << X_POS) | (y << Y_POS),
                    tt=0,
                    io=1,
                    fx=0,
                    abstract=False,
                    meta=True,
                )

        # Replace type names in inherits with TypesDef objects
        # The object set ensures that the same object is used for the same inheritence list.
        # There are many duplicates in the types database.
        inherits_set = ObjectSet("Inherit")
        derived_dict = {}
        for types_def in self._name_key.values():
            inherits = []
            for inherit in types_def.inherits:
                if isinstance(inherit, str):
                    inherits.append(self._name_key[inherit])
                else:
                    inherits.append(inherit)
                derived_dict.setdefault(inherits[-1].uid, []).append(types_def)
            types_def.inherits = inherits_set.add(tuple(inherits))

        # Create the derived set of types for each type (reverse link to inherits)
        for types_def in self._name_key.values():
            types_def.derived = inherits_set.add(tuple(derived_dict.get(types_def.uid, [])))

        # Create the uid_key dict with the new TypesDef objects
        self._uid_key = {v.uid: v for v in self._name_key.values()}

    def __contains__(self, key) -> bool:
        """Return True if the key is in the types database."""
        if isinstance(key, str):
            return key in self._name_key
        if isinstance(key, int):
            return key in self._uid_key
        if isinstance(key, TypesDef):
            return key in self._name_key.values()
        raise ValueError("Invalid key type.")

    def __getitem__(self, key: str | int | TypesDef) -> TypesDef:
        """Return Types Definition by name or uid."""
        if isinstance(key, str):
            return self._name_key[key]
        if isinstance(key, int):
            return self._uid_key[key]
        if isinstance(key, TypesDef):
            return key
        raise ValueError("Invalid key type.")

    def __iter__(self) -> Iterator[TypesDef]:
        """Return an iterator over the types database."""
        return iter(self._name_key.values())

    def __len__(self) -> int:
        """Return the number of types in the types database."""
        return len(self._name_key)

    def get(self, key: str | int | TypesDef, default: str = "object") -> TypesDef:
        """Return Types Definition by name or uid or the default type.
        If the default type does not exist either return 'object' type.
        """
        default = "object" if default not in self else default
        return self[key] if key in self else self[default]

    def inheritance_chart(self, concrete: bool = True) -> str:
        """Return a string representation of the inheritance chart
        in Mermaid charts graph diagram format.

        The chart graphically shows how each object inherits from each other
        all the way back to 'object'.
        """
        # Build the graph.

        chart: list[str] = []
        if concrete:
            flter = (v for v in self._name_key.values() if not v.fx())
        else:
            flter = (v for v in self._name_key.values() if not v.fx() and (v.meta or v.abstract))
        for node in sorted(flter, key=lambda x: x.min_depth()):
            for edge in node.inherits:
                assert isinstance(edge, TypesDef), "Inherits must be a TypesDef object."
                chart.append(f"  {edge.name} --> {node.name}")
        chart.insert(0, "flowchart TD")
        return "\n".join(chart)

    def keys(self) -> list[str]:
        """Return the keys of the types database."""
        return list(self._name_key.keys())

    def to_json(self) -> dict:
        """Return Types Database as a JSON serializable dictionary."""
        return {name: types_def.to_json() for name, types_def in self._name_key.items()}

    def validate(self):
        """Validate the types database."""
        if len(self._name_key) != len(self._uid_key):
            counts = Counter([types_def.uid for types_def in self._name_key.values()])
            for uid, _count in ((k, v) for k, v in counts.items() if v > 1):
                _logger.error("Type UID %d is not unique. There are %d occurances.", uid, _count)
                for types_def in (td for td in self._name_key.values() if td.uid == uid):
                    _logger.error("\t\tType='%s' uid=%d", types_def.name, types_def.uid)
            raise ValueError("Type UIDs are not unique. See logs.")

    def values(self) -> list[TypesDef]:
        """Return the values of the types database."""
        return list(self._name_key.values())


types_db = TypesDB(join(dirname(__file__), "..", "..", "data", "types.json"))
types_db.validate()


if __name__ == "__main__":
    # Output the inheritence chart.
    print("```mermaid")
    print(types_db.inheritance_chart(False))
    print("```")
