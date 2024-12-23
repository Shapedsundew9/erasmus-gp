"""Types Definition class for EGP Seed."""

from __future__ import annotations

from collections import Counter
from collections.abc import Container
from os.path import dirname, join

from egpcommon.common import NULL_TUPLE, DictTypeAccessor
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.security import load_signed_json
from egpcommon.validator import Validator

from egppy.gc_graph.end_point.import_def import ImportDef

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# End Point Type UID Bitfield Constants
XUID_POS: int = 0
XUID_LEN: int = 16
XUID_MASK: int = ((1 << XUID_LEN - 1) - 1) << XUID_POS
TT_POS: int = 28
TT_LEN: int = 3
TT_MASK: int = ((1 << TT_LEN - 1) - 1) << TT_POS


class TypesDef(Validator, DictTypeAccessor):
    """Type Definition class for EGP Seed. Stores the type UID
    and instanciation information."""

    def __init__(
        self,
        name: str,
        uid: int,
        default: str | None = None,
        imports: list[ImportDef] | dict | None = None,
        inherits: list[str | TypesDef] | None = None,
    ) -> None:
        """Initialize Type Definition.

        Args:
            name: Name of the type  definition.
            uid: Unique identifier of the type  definition.
            default: Executable python default instanciation of the type.
            imports: List of import definitions.
        """
        setattr(self, "name", name)
        setattr(self, "uid", uid)
        setattr(self, "default", default)
        setattr(self, "imports", imports)
        setattr(self, "inherits", inherits)

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
        assert (
            uid & TT_MASK
        ) & XUID_MASK == 0, f"Invalid Type UID. Reserved bits are set: {uid:08x}"
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
        return tuple(self._imports) if self._imports is not None else NULL_TUPLE

    @imports.setter
    def imports(self, imports: list[ImportDef] | dict | None) -> None:
        """Set list of import definitions of the type template definition."""
        if imports is None:
            self._imports: tuple[ImportDef, ...] = NULL_TUPLE
            return
        _imports = []
        self._is_list("imports", imports)
        for import_def in imports:
            if isinstance(import_def, dict):
                _imports.append(ImportDef(**import_def))
            elif isinstance(import_def, ImportDef):
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
        if inherits is None:
            self._inherits: tuple[str, ...] = NULL_TUPLE
            return
        _inherits = []
        self._is_list("inherits", inherits)
        for inherit in inherits:
            if isinstance(inherit, str):
                self._is_string("inherits", inherit)
                self._is_length("inherits", inherit, 1, 64)
                self._is_printable_string("inherits", inherit)
            _inherits.append(inherit)
        self._inherits = tuple(_inherits)

    def ept(self) -> EndPointType:
        """Return the End Point Type as a tuple of TypesDef objects."""
        return (self,)

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

    def is_container(self) -> bool:
        """Return True if the type is a container type."""
        return self.tt() > 0

    def to_json(self) -> dict:
        """Return Type Definition as a JSON serializable dictionary."""
        return {
            "name": self.name,
            "uid": self.uid,
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


# The End Point Type type definition is recursive
EndPointType = tuple[TypesDef | tuple[TypesDef, ...] | tuple, ...]


class TypesDB(Container):
    """Types Database.

    Used to look up TypesDefs by name or uid.
    Immutable once initialized.
    """

    def __init__(self, types_filename: str) -> None:
        """Initialize Types Database."""
        self._types_filename = types_filename
        with open(types_filename, "r", encoding="ascii") as types_file:
            data = load_signed_json(types_file)
        assert isinstance(data, dict), "Types Database must be a dictionary."
        self._name_key: dict[str, TypesDef] = {k: TypesDef(name=k, **v) for k, v in data.items()}
        self._uid_key: dict[int, TypesDef] = {v.uid: v for v in self._name_key.values()}

        # Replace type names in inherits with TypesDef objects
        for types_def in self._name_key.values():
            inherits = []
            for inherit in types_def.inherits:
                if isinstance(inherit, str):
                    inherits.append(self._name_key[inherit])
                else:
                    inherits.append(inherit)
            types_def.inherits = inherits

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

    def to_json(self) -> dict:
        """Return Types Database as a JSON serializable dictionary."""
        return {name: types_def.to_json() for name, types_def in self._name_key.items()}

    def validate(self):
        """Validate the types database."""
        if len(self._name_key) != len(self._uid_key):
            counts = Counter([types_def.uid for types_def in self._name_key.values()])
            for uid, count in ((k, v) for k, v in counts.items() if v > 1):
                _logger.error("Type UID %d is not unique. There are %d occurances.", uid, count)
                for types_def in (td for td in self._name_key.values() if td.uid == uid):
                    _logger.error("\t\tType='%s' uid=%d", types_def.name, types_def.uid)
            raise ValueError("Type UID's are not unique. See logs.")


types_db = TypesDB(join(dirname(__file__), "..", "..", "data", "types.json"))
types_db.validate()
