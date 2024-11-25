"""Types Definition class for EGP Seed."""

from egpcommon.common import DictTypeAccessor
from egpcommon.import_def import ImportDef
from egpcommon.security import load_signed_json
from egpcommon.validator import Validator


class TypesDef(Validator, DictTypeAccessor):
    """Type Definition class for EGP Seed."""

    def __init__(
        self,
        name: str,
        uid: int,
        default: str | None = None,
        imports: list[ImportDef] | dict | None = None,
        inherits: list[str] | None = None,
    ) -> None:
        """Initialize Type Definition.

        Args:
            name (str): Name of the type  definition.
            uid (int): Unique identifier of the type  definition.
            default (str, optional): Default instanciation of the type. Defaults to None.
            imports (list[ImportDef], optional): List of import definitions. Defaults to None.
        """
        setattr(self, "name", name)
        setattr(self, "uid", uid)
        setattr(self, "default", default)
        setattr(self, "imports", imports)
        setattr(self, "inherits", inherits)

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
        self._in_range("uid", uid, -(2**31), 2**31 - 1)
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
    def imports(self) -> list[ImportDef] | None:
        """Return list of import definitions of the type template definition."""
        return self._imports

    @imports.setter
    def imports(self, imports: list[ImportDef] | dict | None) -> None:
        """Set list of import definitions of the type template definition."""
        if imports is None:
            _imports: list[ImportDef] | None = None
        else:
            _imports = []
            self._is_list("imports", imports)
            for import_def in imports:
                if isinstance(import_def, dict):
                    _imports.append(ImportDef(**import_def))
                elif isinstance(import_def, ImportDef):
                    _imports.append(import_def)
                else:
                    raise ValueError("Invalid imports definition.")
        self._imports = _imports

    @property
    def inherits(self) -> list[str] | None:
        """Return list of type names that the type inherits from."""
        return self._inherits

    @inherits.setter
    def inherits(self, inherits: list[str] | None) -> None:
        """Set list of type names that the type inherits from."""
        if inherits is None:
            _inherits: list[str] | None = None
        else:
            _inherits = []
            self._is_list("inherits", inherits)
            for inherit in inherits:
                self._is_string("inherits", inherit)
                self._is_length("inherits", inherit, 1, 64)
                self._is_printable_string("inherits", inherit)
                _inherits.append(inherit)
        self._inherits = _inherits

    def to_json(self) -> dict:
        """Return Type Definition as a JSON serializable dictionary."""
        return {
            "name": self.name,
            "uid": self.uid,
            "default": self.default,
            "imports": None if self.imports is None else [idef.to_json() for idef in self.imports],
            "inherits": self.inherits,
        }


class TypesDB:
    """Types Database class for EGP Seed."""

    def __init__(self, types_filename: str) -> None:
        """Initialize Types Database."""
        self._types_filename = types_filename
        with open(types_filename, "r", encoding="ascii") as types_file:
            data = load_signed_json(types_file)
        assert isinstance(data, dict), "Types Database must be a dictionary."
        self._name_key: dict[str, TypesDef] = {k: TypesDef(name=k, **v) for k, v in data.items()}
        self._uid_key: dict[int, TypesDef] = {v.uid: v for v in self._name_key.values()}

    def __getitem__(self, key: str | int) -> TypesDef:
        """Return Types Definition by name or uid."""
        if isinstance(key, str):
            return self._name_key[key]
        if isinstance(key, int):
            return self._uid_key[key]
        raise ValueError("Invalid key type.")

    def to_json(self) -> dict:
        """Return Types Database as a JSON serializable dictionary."""
        return {name: types_def.to_json() for name, types_def in self._name_key.items()}

    def validate(self):
        """Validate the types database."""
        assert len(self._name_key) == len(self._uid_key), "Name and UID keys must be unique."
