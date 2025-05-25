"""Types Definition class and store for EGP types."""

from __future__ import annotations

from json import dumps, loads
from os.path import dirname, join
from typing import Any, Final, Generator, Iterable

from bitdict import BitDictABC, bitdict_factory
from egpcommon.common import EGP_DEV_PROFILE, EGP_PROFILE, NULL_TUPLE
from egpcommon.egp_log import CONSISTENCY, DEBUG, VERIFY, Logger, egp_logger
from egpcommon.freezable_object import FreezableObject
from egpcommon.object_dict import ObjectDict
from egpcommon.validator import Validator
from egpdb.configuration import ColumnSchema
from egpdb.table import Table, TableConfig

from egppy.c_graph.end_point.import_def import ImportDef, import_def_store
from egppy.c_graph.end_point.types_def.types_def_bit_dict import TYPESDEF_CONFIG
from egppy.local_db_config import LOCAL_DB_CONFIG


# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)
_LOG_DEBUG: bool = _logger.isEnabledFor(level=DEBUG)
_LOG_VERIFY: bool = _logger.isEnabledFor(level=VERIFY)
_LOG_CONSISTENCY: bool = _logger.isEnabledFor(level=CONSISTENCY)


# Initialize the database connection
DB_STORE = Table(
    config=TableConfig(
        database=LOCAL_DB_CONFIG,
        table="types_def",
        schema={
            "uid": ColumnSchema(db_type="int4", primary_key=True),
            "name": ColumnSchema(db_type="VARCHAR", index="btree"),
            "default": ColumnSchema(db_type="VARCHAR", nullable=True),
            "abstract": ColumnSchema(db_type="bool"),
            "ept": ColumnSchema(db_type="INT4[]"),
            "imports": ColumnSchema(db_type="VARCHAR"),
            "parents": ColumnSchema(db_type="VARCHAR"),
            "children": ColumnSchema(db_type="VARCHAR"),
        },
        data_file_folder=join(dirname(__file__), "..", "..", "..", "data"),
        data_files=["types_def.json"],
        delete_table=EGP_PROFILE == EGP_DEV_PROFILE,
        create_db=True,
        create_table=True,
        conversions=(
            ("imports", dumps, loads),
            ("parents", dumps, loads),
            ("children", dumps, loads),
        ),
    ),
)

# The generic tuple type UID
_TUPLE_UID: int = 268435471


# The BitDict format of the EGP type UID
TypesDefBD: type[BitDictABC] = bitdict_factory(
    TYPESDEF_CONFIG,
    name="TypesDefBD",
    title="Type Definition BitDict",
)


class TypesDef(FreezableObject, Validator):
    """The Type Definition class stores all the information in order
    to define a type in the EGP system.

    TypesDef objects are final and immutable so that they can be
    cached and reused. Also see the types_def_db.py module.
    """

    __slots__: tuple[str, ...] = (
        "__name",
        "__ept",
        "__default",
        "__abstract",
        "__imports",
        "__parents",
        "__children",
        "__uid",
    )

    def __init__(
        self,
        name: str,
        uid: int | dict[str, Any],
        ept: Iterable[int],
        abstract: bool = False,
        default: str | None = None,
        imports: Iterable[ImportDef] | dict = NULL_TUPLE,
        parents: Iterable[str | TypesDef] = NULL_TUPLE,
        children: Iterable[str | TypesDef] = NULL_TUPLE,
    ) -> None:
        """Initialize Type Definition.

        Args:
            name: Name of the type definition.
            uid: Unique identifier of the type definition.
            ept: The End Point Type - a list of integers defining the type.
            abstract: True if the type is abstract.
            default: Executable python default instantiation of the type.
            imports: List of import definitions need to instantiate the type.
            parents: List of type names or definitions that the type inherits from.
            children: List of type names or definitions that the type has as children.
        """
        # Always set frozen to False
        # because we want to be able to set the attributes during initialization.
        super().__init__(frozen=False)
        self.__name: Final[str] = self._name(name)
        self.__ept: Final[tuple[int, ...]] = self._ept(ept)
        self.__default: Final[str | None] = self._default(default)
        self.__abstract: Final[bool] = self._abstract(abstract)
        self.__imports: Final[tuple[ImportDef, ...]] = self._imports(imports)
        self.__parents: Final[tuple[str, ...]] = self._parents(parents)
        self.__children: Final[tuple[str, ...]] = self._children(children)
        self.__uid: Final[int] = self._uid(uid)
        self.freeze()

    def __eq__(self, value: object) -> bool:
        """Return True if the value is equal to this object."""
        if isinstance(value, TypesDef):
            return self.__uid == value.uid
        return False

    def __hash__(self) -> int:
        """Return globally unique hash for the object.
        TypeDefs are unique by design and should not be duplicated.
        """
        return self.__uid

    def __iter__(self) -> Generator[Any, Any, None]:
        """
        Allows iteration over the *values* of public instance variables.
        This is define by the to_json() method.
        """
        for value in (
            self.__name,
            self.uid,
            self.__ept,
            self.__default,
            self.__imports,
            self.__parents,
            self.__children,
        ):
            yield value

    def __len__(self) -> int:
        """Return the number of publicly exposed variables."""
        return 7

    def _abstract(self, abstract: bool) -> bool:
        """Validate the abstract flag of the type definition."""
        self._is_bool("abstract", abstract)
        return abstract

    def _children(self, children: Iterable[str | TypesDef]) -> tuple[str, ...]:
        """Mash the children definitions into a tuple of type names.
        Names are used to look up the type in the types database on an as needed basis.
        This allows TypesDef objects to be independently cached.
        """
        # If it is already a tuple no need to copy it. Saves memory.
        if isinstance(children, tuple) and all(isinstance(i, str) for i in children):
            return children  # type: ignore
        child_list: list[str] = []
        for child in children:
            if isinstance(child, str):
                child_list.append(child)
            elif isinstance(child, TypesDef):
                child_list.append(child.name)
            else:
                raise ValueError("Invalid children definition.")
        return tuple(child_list)

    def _default(self, default: str | None) -> str | None:
        """Validate the default instantiation of the type definition."""
        if default is None:
            return None
        self._is_string("default", default)
        self._is_length("default", default, 1, 64)
        self._is_printable_string("default", default)
        return default

    def _ept(self, ept: Iterable[int]) -> tuple[int, ...]:
        """Validate the EPT of the type definition."""
        self._is_sequence("ept", ept)
        ept = tuple(ept)
        assert 9 > len(ept) > 0, "The EPT must have between 1 and 8 elements."
        assert all(isinstance(x, int) for x in ept), "All elements of EPT must be integers."
        return ept

    def _imports(self, imports: Iterable[ImportDef] | dict) -> tuple[ImportDef, ...]:
        """Mash the import definitions into a tuple of ImportDef objects
        and ensure they are in the ImportDef store."""
        # If it is already a tuple no need to copy it. Saves memory.
        if isinstance(imports, tuple) and all(isinstance(i, ImportDef) for i in imports):
            assert all(
                impt in import_def_store for impt in imports
            ), "ImportDef must be in the import store."
            return imports
        import_list: list[ImportDef] = []
        for import_def in imports:
            if isinstance(import_def, dict):
                # The import store will ensure that the same import is not duplicated.
                idef = import_def_store.add(ImportDef(**import_def))
                import_list.append(idef)
            elif isinstance(import_def, ImportDef):
                assert import_def in import_def_store, "ImportDef must be in the import store."
                import_list.append(import_def)
            else:
                raise ValueError("Invalid imports definition.")
        return tuple(import_list)

    def _name(self, name: str) -> str:
        """Validate the name of the type definition."""
        self._is_string("name", name)
        self._is_length("name", name, 1, 64)
        self._is_printable_string("name", name)
        return name

    def _parents(self, parents: Iterable[str | TypesDef]) -> tuple[str, ...]:
        """Mash the inheritance definitions into a tuple of type names.
        Names are used to look up the type in the types database on an as needed basis.
        This allows TypesDef objects to be independently cached.
        """
        # If it is already a tuple no need to copy it. Saves memory.
        if isinstance(parents, tuple) and all(isinstance(i, str) for i in parents):
            return parents  # type: ignore
        parent_list: list[str] = []
        for parent in parents:
            if isinstance(parent, str):
                parent_list.append(parent)
            elif isinstance(parent, TypesDef):
                parent_list.append(parent.name)
            else:
                raise ValueError("Invalid parents definition.")
        return tuple(parent_list)

    def _uid(self, uid: int | dict[str, Any]) -> int:
        """Validate the UID of the type definition."""
        if isinstance(uid, int):
            self._is_int("uid", uid)
            self._in_range("uid", uid, -(2**31), 2**31 - 1)
            return uid
        elif isinstance(uid, dict):
            # The BitDict will handle the validation.
            return TypesDefBD(uid).to_int()
        else:
            raise ValueError("Invalid UID definition.")

    @property
    def abstract(self) -> bool:
        """Return True if the type is abstract."""
        return self.__abstract

    @property
    def bd(self) -> BitDictABC:
        """Return the BitDict object."""
        return TypesDefBD(self.__uid)

    @property
    def children(self) -> tuple[str, ...]:
        """Return the children of the type definition."""
        return self.__children

    @property
    def default(self) -> str | None:
        """Return the default instantiation of the type."""
        return self.__default

    @property
    def ept(self) -> tuple[int, ...]:
        """Return the EPT of the type definition."""
        return self.__ept

    @property
    def imports(self) -> tuple[ImportDef, ...]:
        """Return the imports of the type definition."""
        return self.__imports

    @property
    def name(self) -> str:
        """Return the name of the type definition."""
        return self.__name

    @property
    def parents(self) -> tuple[str, ...]:
        """Return the parents of the type definition."""
        return self.__parents

    @property
    def uid(self) -> int:
        """Return the UID of the type definition."""
        return self.bd.to_int()

    def fx(self) -> int | None:
        """Return the FX number."""
        bd = self.bd
        if not bd["tt"]:
            return None
        ttsp = bd["ttsp"]
        assert isinstance(ttsp, BitDictABC), "ttsp must be a BitDictABC"
        io = ttsp["io"]
        assert isinstance(io, int), "IO must be an integer."
        if io:
            return None
        iosp = ttsp["iosp"]
        assert isinstance(iosp, BitDictABC), "iosp must be a BitDictABC"
        retval = iosp["fx"]
        assert isinstance(retval, int), "FX must be an integer."
        return retval

    def io(self) -> int | None:
        """Return the IO number."""
        bd = self.bd
        if not bd["tt"]:
            return None
        ttsp = bd["ttsp"]
        assert isinstance(ttsp, BitDictABC), "ttsp must be a BitDictABC"
        retval = ttsp["io"]
        assert isinstance(retval, int), "IO must be an integer."
        return retval

    def to_json(self) -> dict:
        """Return Type Definition as a JSON serializable dictionary."""
        return {
            "abstract": self.__abstract,
            "children": list(self.__children),
            "default": self.__default,
            "ept": list(self.__ept),
            "imports": [idef.to_json() for idef in self.__imports],
            "name": self.__name,
            "parents": list(self.__parents),
            "uid": self.uid,
        }

    def tt(self) -> int:
        """Return the Template Type number."""
        bd = self.bd
        retval = bd["tt"]
        assert isinstance(retval, int), "TT must be an integer."
        return retval

    def x(self) -> int | None:
        """Return the X number."""
        bd = self.bd
        if not bd["tt"]:
            return None
        ttsp = bd["ttsp"]
        assert isinstance(ttsp, BitDictABC), "ttsp must be a BitDictABC"
        io = ttsp["io"]
        assert isinstance(io, int), "IO must be an integer."
        if not io:
            return None
        iosp = ttsp["iosp"]
        assert isinstance(iosp, BitDictABC), "iosp must be a BitDictABC"
        retval = iosp["x"]
        assert isinstance(retval, int), "X must be an integer."
        return retval

    def xuid(self) -> int | None:
        """Return the XUID of the type definition."""
        bd = self.bd
        if not bd["tt"]:
            return None
        ttsp = bd["ttsp"]
        assert isinstance(ttsp, BitDictABC), "ttsp must be a BitDictABC"
        io = ttsp["io"]
        assert isinstance(io, int), "IO must be an integer."
        if io:
            return None
        iosp = ttsp["iosp"]
        assert isinstance(iosp, BitDictABC), "iosp must be a BitDictABC"
        retval = iosp["xuid"]
        assert isinstance(retval, int), "XUID must be an integer."
        return retval

    def y(self) -> int | None:
        """Return the Y number."""
        bd = self.bd
        if not bd["tt"]:
            return None
        ttsp = bd["ttsp"]
        assert isinstance(ttsp, BitDictABC), "ttsp must be a BitDictABC"
        io = ttsp["io"]
        assert isinstance(io, int), "IO must be an integer."
        if not io:
            return None
        iosp = ttsp["iosp"]
        assert isinstance(iosp, BitDictABC), "iosp must be a BitDictABC"
        retval = iosp["y"]
        assert isinstance(retval, int), "Y must be an integer."
        return retval


def _to_str_recursive(ept: tuple[TypesDef, ...], current_index: int) -> tuple[str, int]:
    """Recursively convert the EPT to a string representation."""
    td: TypesDef = ept[current_index]
    current_index += 1
    tt: int = td.tt()
    if not tt:
        return td.name, current_index

    parts: list[str] = []
    for _ in range(tt):
        part_str, current_index = _to_str_recursive(ept, current_index)
        parts.append(part_str)

    ext = ", ..." if td.uid == _TUPLE_UID else ""
    return f"{td.name}[{', '.join(parts)}{ext}]", current_index


def to_str(ept: tuple[TypesDef, ...]) -> str:
    """Convert the EPT to a string representation."""
    assert len(ept) > 0, "The EPT must have at least one type."
    assert isinstance(ept[0], TypesDef), f"Expected TypesDef but found {type(ept[0])}"
    result, _ = _to_str_recursive(ept, 0)
    return result


class TypesDefStore(ObjectDict):
    """Types Definition Database.

    The TDDB is a double dictionary that maps type names to TypesDef objects
    and type UIDs to TypesDef objects. It is implemented as a cache of the
    full types database which is a local postgres database.

    The expectation is that the types used at runtime will be small enough
    to fit in memory (but the user should look for frequent cache evictions
    in the logs and adjust the cache size accordingly) as EGP should use a tight
    subset for a population.

    New compound types can be created during evolution requiring the  cache and
    database to be updated. Since types have to be globally unique a cloud service
    call is required to create a new type.

    Initialization follow the following steps:
        1. Load the pre-defined types from the local JSON file.
        2. Generate the abstract type fixed versions.
        3. Generate the output wildcard meta-types.
        4. Push the types to the database.
        5. Initialise the empty cache.
    """

    def __init__(self) -> None:
        """Initialize the TypesDefStore."""
        super().__init__("TypesDefStore")
        self._cache_hit: int = 0
        self._cache_miss: int = 0

    def __getitem__(self, key: Any) -> Any:
        """Get a object from the dict."""
        if key in self._objects:
            self._cache_hit += 1
            return self._objects[key]
        self._cache_miss += 1
        if isinstance(key, int):
            td = DB_STORE.get(key, {})
        elif isinstance(key, str):
            tds = tuple(DB_STORE.select("WHERE name = {id}", literals={"id": key}))
            td = tds[0] if len(tds) == 1 else {}
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
        if not td:
            raise KeyError(f"Object not found with key: {key}")

        # Create the TypesDef object
        ntd = TypesDef(**td)
        self._objects[ntd.name] = ntd
        self._objects[ntd.uid] = ntd
        return ntd

    def info(self) -> str:
        """Print cache hit and miss statistics."""
        info_str = (
            f"TypesDefStore Cache hits: {self._cache_hit}\n"
            f"TypesDefStore Cache misses: {self._cache_miss}\n"
            f"{super().info()}"
        )
        _logger.info(info_str)
        return info_str


# Create the TypesDefStore object
types_def_store = TypesDefStore()


# Important check
assert types_def_store["tuple"].uid == _TUPLE_UID, "Tuple UID is used as a constant."
