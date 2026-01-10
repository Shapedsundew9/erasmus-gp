"""
Docstring for egppy.genetic_code.types_def_store
"""

from collections.abc import Iterable, Iterator
from functools import reduce
from json import dumps, loads
from os.path import dirname, join
from re import findall
from typing import Any

from egpcommon.common import EGP_DEV_PROFILE, EGP_PROFILE
from egpcommon.egp_log import Logger, egp_logger
from egpcommon.object_deduplicator import format_deduplicator_info
from egpcommon.security import InvalidSignatureError, load_signature_data, verify_signed_file
from egpcommon.type_string_parser import TypeNode, TypeStringParser
from egpdb.configuration import ColumnSchema
from egpdb.table import RowIter, Table, TableConfig
from egppy.genetic_code.types_def import TypesDef
from egppy.local_db_config import LOCAL_DB_CONFIG

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# SQL
_TABLE_NAME = "types_def"
_MAX_UID_SQL = "SELECT MAX({uid}) FROM {" + _TABLE_NAME + "}"
_TYPE_SELECT_SQL = "WHERE name = {id} or alias = {id}"
_TEMPLATE_TYPE_PATTERN = r"-\S*\d"
_TYPES_DEF_FILE_FOLDER = join(dirname(__file__), "..", "data")
_TYPES_DEF_FILE = "types_def.json"

# Initialize the database connection
DB_STORE_TABLE_CONFIG = TableConfig(
    database=LOCAL_DB_CONFIG,
    table=_TABLE_NAME,
    schema={
        "uid": ColumnSchema(db_type="int4", primary_key=True),
        "name": ColumnSchema(db_type="VARCHAR", index="btree"),
        "alias": ColumnSchema(db_type="VARCHAR", index="btree", nullable=True),
        "default": ColumnSchema(db_type="VARCHAR", nullable=True),
        "depth": ColumnSchema(db_type="int4"),
        "abstract": ColumnSchema(db_type="bool"),
        "imports": ColumnSchema(db_type="VARCHAR"),
        "parents": ColumnSchema(db_type="INT4[]"),
        "children": ColumnSchema(db_type="INT4[]"),
        "template": ColumnSchema(db_type="VARCHAR", nullable=True),
        "tt": ColumnSchema(db_type="int4"),
    },
    data_file_folder=_TYPES_DEF_FILE_FOLDER,
    data_files=[_TYPES_DEF_FILE],
    delete_table=False,
    create_db=True,
    create_table=True,
    conversions=(("imports", dumps, loads),),
)
DB_SOURCES_TABLE_CONFIG = TableConfig(
    database=LOCAL_DB_CONFIG,
    table="types_def_sources",
    schema={
        "source_path": ColumnSchema(db_type="VARCHAR", nullable=False),
        "creator_uuid": ColumnSchema(db_type="VARCHAR", nullable=False),
        "timestamp": ColumnSchema(db_type="VARCHAR", nullable=False),
        "file_hash": ColumnSchema(db_type="VARCHAR", nullable=False),
        "signature": ColumnSchema(db_type="VARCHAR", nullable=False),
        "algorithm": ColumnSchema(db_type="VARCHAR", nullable=False),
    },
    delete_table=False,
    create_db=True,
    create_table=True,
)


# The object type UID
OBJECT_UID: int = 0


# Helper function to get the highest type
def highest_type(types_iter: Iterable[str]) -> str:
    """Get the highest input type from a list of input types.

    The highest type is determined by the type depth in the types definition store.
    The type with the greatest depth (furthest from object) is considered the highest type.

    Arguments:
        types_iter: Iterable of input type names.
    Returns:
        The highest input type name.
    """
    tds = [td for td in (types_def_store[typ] for typ in types_iter)]
    tds.sort(key=lambda td: td.depth, reverse=True)
    return tds[0].name


class TypesDefStore:
    """Types Definition Database.

    The TDDB is a double dictionary that maps type names to TypesDef objects
    and type UIDs to TypesDef objects. It is implemented as a cache of the
    full types database which is a local postgres database.

    The expectation is that the types used at runtime will be small enough
    to fit in memory (but the user should look for frequent GC cache evictions
    in the logs and adjust the cache size accordingly) as EGP should use a tight
    subset for a population.

    New compound types can be created during evolution requiring the store and
    database to be updated. Since types have to be globally unique a cloud service
    call is required to create a new type.
    """

    _db_store: Table | None = None
    _db_sources: Table | None = None
    _db_lock_id: int = hash("TypesDefStoreLock")
    _cache: dict[int | str, TypesDef] = {}
    _cache_order: list[int | str] = []
    _cache_maxsize: int = 1024
    _cache_hits: int = 0
    _cache_misses: int = 0

    _ancestors_cache: dict[int, frozenset[TypesDef]] = {}
    _ancestors_cache_order: list[int] = []
    _ancestors_cache_maxsize: int = 128
    _ancestors_cache_hits: int = 0
    _ancestors_cache_misses: int = 0

    _descendants_cache: dict[int, frozenset[TypesDef]] = {}
    _descendants_cache_order: list[int] = []
    _descendants_cache_maxsize: int = 128
    _descendants_cache_hits: int = 0
    _descendants_cache_misses: int = 0

    def __contains__(self, key: int | str) -> bool:
        """Check if the key is in the store."""
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        try:
            self[key]  # This will populate the cache if the key exists.
        except KeyError:
            return False
        return True

    def __copy__(self):
        """Called by copy.copy()"""
        return self

    def __deepcopy__(self, memo):
        """
        Called by copy.deepcopy().
        'memo' is a dictionary used to track recursion loops.
        """
        # Since we are returning self, we don't need to use memo,
        # but the signature requires it.
        return self

    def __getitem__(self, key: int | str) -> TypesDef:
        """Get a object from the dict."""
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        assert TypesDefStore._db_store is not None, "DB store must be initialized."

        # Check cache first
        if key in TypesDefStore._cache:
            TypesDefStore._cache_hits += 1
            return TypesDefStore._cache[key]

        TypesDefStore._cache_misses += 1

        if isinstance(key, int):
            td = TypesDefStore._db_store.get(key, {})
            if not td:
                raise KeyError(f"Type not found with UID: {key}")
        elif isinstance(key, str):
            tds = tuple(TypesDefStore._db_store.select(_TYPE_SELECT_SQL, literals={"id": key}))
            td = tds[0] if len(tds) == 1 else {}
        else:
            raise TypeError(f"Invalid key type: {type(key)}")
        if not td:
            # TODO: Go to an external service to find or create the type definition.
            # NOTE: Other types will be affected by any new type through parents/children.
            # For now if it is a new compund container type then we can create it locally.
            assert isinstance(key, str), "Key must be a string to create new type."
            root_tn: TypeNode = TypeStringParser.parse(key)
            if not root_tn.args:
                # It is not a container and we do not know what it is.
                raise KeyError(f"Type not found with name: {key}")
            # Recursively unpack the contained type definitions (ignoring ellipsis)
            arg_strs = [str(arg) for arg in root_tn.args if arg.name != "..."]
            ctds = [self[arg_str] for arg_str in arg_strs]
            # Now we have a parent container in root_tn and known contained types
            # to make a new type definition.
            base_type = self[root_tn.name]  # This is the alias e.g. list, dict, tuple, etc.

            # Imports are deduplicated when the TypesDef is created.
            imports = [i for ctd in ctds for i in ctd.imports]

            # Parent types are likely needed to be created too. However, they are templated
            # where r'-.*[0-9]' is used to indicate a template parameter for a specific type.
            assert (
                base_type.template is not None
            ), f"Base type {base_type.name} must be a template type."

            # Must have 1 parent otherwise why do we have a template?
            assert (
                len(base_type.template) > 1
            ), f"Base type {base_type.name} must have at least 1 parent."
            type_templates = findall(_TEMPLATE_TYPE_PATTERN, base_type.template[0])

            # For types the number of templates
            assert len(type_templates) <= len(ctds), (
                f"Template parameters ({type_templates}) is greater than the "
                f"number of contained types ({ctds}) for type {key}."
            )

            # Create a mapping of template to contained type definition
            # and use that to update the templated parent types to make a list of parents.
            trans_table = dict(zip(type_templates, arg_strs))
            parents = [
                reduce(lambda acc, tpl: acc.replace(*tpl), trans_table.items(), parent)
                for parent in base_type.template[1:]
            ]

            # Get the parent TypesDef objects - this will create them if they do not exist.
            # TypeDefs need the parent UIDs
            ptds = [self[parent] for parent in parents]
            td = {
                "name": str(root_tn),  # Ensure consistent formatting
                "alias": None,  # Never will be a base template by definition
                "uid": self.next_xuid(),
                "default": base_type.default,
                "depth": base_type.depth,
                "abstract": base_type.abstract,
                "imports": imports,
                "parents": [p.uid for p in ptds],
                "children": [],  # Children may be possible but not created by default.
                "template": None,
                "tt": base_type.tt,
            }

            # Add to the database & read it back out again to ensure consistency
            TypesDefStore._db_store.insert((TypesDef(**td).to_json(),))
            td = next(TypesDefStore._db_store.select(_TYPE_SELECT_SQL, literals={"id": key}))

        # Create a frozen TypesDef object but do not put it in the object_store as
        # we will cache it here.
        ntd = TypesDef(**td)

        # Cache the result with LRU eviction
        TypesDefStore._cache[key] = ntd
        TypesDefStore._cache_order.append(key)

        # LRU eviction if cache is full
        if len(TypesDefStore._cache_order) > TypesDefStore._cache_maxsize:
            evict_key = TypesDefStore._cache_order.pop(0)
            del TypesDefStore._cache[evict_key]

        return ntd

    def _initialize_db_store(self) -> None:
        """Initialize the database store if it has not been initialized yet.
        This is done lazily to avoid import overheads when not used.
        """
        # TODO: There is a race condition here for multi-threaded use.
        # This should be protected by a lock in the database.
        TypesDefStore._db_sources = Table(config=DB_SOURCES_TABLE_CONFIG)
        DB_STORE_TABLE_CONFIG.delete_table = self._should_reload_table()
        if DB_STORE_TABLE_CONFIG.delete_table:
            # Delete sources and recreate them with the latest data files.
            DB_SOURCES_TABLE_CONFIG.delete_table = True
            TypesDefStore._db_sources = Table(config=DB_SOURCES_TABLE_CONFIG)
            for name in DB_STORE_TABLE_CONFIG.data_files:
                filename = join(DB_STORE_TABLE_CONFIG.data_file_folder, name)
                if not verify_signed_file(filename):
                    raise InvalidSignatureError(
                        f"Signature verification failed for file: {filename}"
                    )
                sig_data = load_signature_data(filename + ".sig")
                sig_data["source_path"] = filename
                TypesDefStore._db_sources.insert((sig_data,))
        # The table configuration will either create & populate with the latest data
        # or load the existing table.
        TypesDefStore._db_store = Table(config=DB_STORE_TABLE_CONFIG)

    def _should_reload_table(self) -> bool:
        """Determine if the types_def table should be reloaded."""
        db_sources = TypesDefStore._db_sources
        assert db_sources is not None, "DB sources must be initialized."
        folder = DB_STORE_TABLE_CONFIG.data_file_folder
        num_entries = len(db_sources)
        num_files = len(DB_STORE_TABLE_CONFIG.data_files)
        if EGP_PROFILE == EGP_DEV_PROFILE and num_entries >= num_files:
            sources: RowIter = db_sources.select()
            hashes: set[bytes] = {row["file_hash"] for row in sources}
            for filename in DB_STORE_TABLE_CONFIG.data_files:
                data = load_signature_data(join(folder, filename + ".sig"))
                file_hash = data["file_hash"]
                if file_hash not in hashes:
                    return True
                hashes.remove(file_hash)
            return bool(hashes)
        TypesDefStore._db_sources = db_sources
        return num_entries < num_files

    def ancestors(self, key: str | int | TypesDef) -> frozenset[TypesDef]:
        """Returns the specified type definition and all its ancestor type
        definitions in depth order.

        Ancestors are defined as the parents, grandparents, etc., of the given type,
        including the type itself. The search starts from the provided key
        (which can be a name, UID, or TypesDef instance) and traverses up the parent hierarchy.
        Results are cached for performance.

        Args:
            key (str | int | TypesDef): The identifier (name, UID, or TypesDef instance)
            of the type definition to start from.

        Returns:
            frozenset[TypesDef]: A frozenset containing the type definition and all its
            ancestors, in depth order.

        Raises:
            KeyError: If the provided key does not correspond to a valid type definition.
        """
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        td = self[key] if not isinstance(key, TypesDef) else key

        if td.uid in TypesDefStore._ancestors_cache:
            TypesDefStore._ancestors_cache_hits += 1
            return TypesDefStore._ancestors_cache[td.uid]

        TypesDefStore._ancestors_cache_misses += 1

        stack: set[TypesDef] = {td}
        ancestors: set[TypesDef] = set()
        while stack:
            parent: TypesDef = stack.pop()
            if parent not in ancestors:
                ancestors.add(parent)
                stack.update(self[p] for p in parent.parents)

        result = frozenset(ancestors)
        TypesDefStore._ancestors_cache[td.uid] = result
        TypesDefStore._ancestors_cache_order.append(td.uid)

        if len(TypesDefStore._ancestors_cache_order) > TypesDefStore._ancestors_cache_maxsize:
            evict_key = TypesDefStore._ancestors_cache_order.pop(0)
            del TypesDefStore._ancestors_cache[evict_key]

        return result

    def descendants(self, key: str | int | TypesDef) -> frozenset[TypesDef]:
        """Returns the specified type definition and all its descendant type
        definitions in depth order.

        Descendants are defined as the children, grandchildren, etc., of the given type,
        including the type itself. The search starts from the provided key
        (which can be a name, UID, or TypesDef instance) and traverses down the child hierarchy.
        Results are cached for performance.

        Args:
            key (str | int | TypesDef): The identifier (name, UID, or TypesDef instance)
            of the type definition to start from.

        Returns:
            frozenset[TypesDef]: A frozenset containing the type definition and all its
            descendants, in depth order.

        Raises:
            KeyError: If the provided key does not correspond to a valid type definition.
        """
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        td = self[key] if not isinstance(key, TypesDef) else key

        if td.uid in TypesDefStore._descendants_cache:
            TypesDefStore._descendants_cache_hits += 1
            return TypesDefStore._descendants_cache[td.uid]

        TypesDefStore._descendants_cache_misses += 1

        stack: set[TypesDef] = {td}
        descendants: set[TypesDef] = set()
        while stack:
            child: TypesDef = stack.pop()
            if child not in descendants:
                descendants.add(child)
                stack.update(self[c] for c in child.children)

        result = frozenset(descendants)
        TypesDefStore._descendants_cache[td.uid] = result
        TypesDefStore._descendants_cache_order.append(td.uid)

        if len(TypesDefStore._descendants_cache_order) > TypesDefStore._descendants_cache_maxsize:
            evict_key = TypesDefStore._descendants_cache_order.pop(0)
            del TypesDefStore._descendants_cache[evict_key]

        return result

    def export(self) -> dict[str, Any]:
        """Export the types definition store to the data files."""
        if TypesDefStore._db_store is None:
            raise RuntimeError("DB store must be initialized before it can be exported.")
        rows: RowIter = TypesDefStore._db_store.select()
        return {td["name"]: td for td in rows}

    def get(self, base_key: str) -> tuple[TypesDef, ...]:
        """Get a tuple of TypesDef objects by base key. e.g. All "Pair" types."""
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        assert TypesDefStore._db_store is not None, "DB store must be initialized."
        tds = TypesDefStore._db_store.select(
            "WHERE name LIKE {id}", literals={"id": f"{base_key}%"}
        )
        return tuple(TypesDef(**td) for td in tds)

    def info(self) -> str:
        """Print cache hit and miss statistics."""
        info_str = "\n".join(
            (
                format_deduplicator_info(
                    "TypesDefStore",
                    0.649,
                    TypesDefStore._cache_hits,
                    TypesDefStore._cache_misses,
                    len(TypesDefStore._cache),
                    TypesDefStore._cache_maxsize,
                ),
                format_deduplicator_info(
                    "Ancestors",
                    0.649,
                    TypesDefStore._ancestors_cache_hits,
                    TypesDefStore._ancestors_cache_misses,
                    len(TypesDefStore._ancestors_cache),
                    TypesDefStore._ancestors_cache_maxsize,
                ),
                format_deduplicator_info(
                    "Descendants",
                    0.649,
                    TypesDefStore._descendants_cache_hits,
                    TypesDefStore._descendants_cache_misses,
                    len(TypesDefStore._descendants_cache),
                    TypesDefStore._descendants_cache_maxsize,
                ),
            )
        )
        _logger.info(info_str)
        return info_str

    def next_xuid(self) -> int:
        """Get the next X unique ID for a type."""
        # TODO: This is temporary until we have a cloud service to allocate UIDs.
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        assert TypesDefStore._db_store is not None, "DB store must be initialized."
        retval = next(TypesDefStore._db_store.raw.arbitrary_sql(_MAX_UID_SQL))
        assert retval, "No UIDs available for this Template Type."
        max_uid = retval[0]
        assert isinstance(max_uid, int), "Max UID must be an integer."
        if max_uid & 0xFFFF == 0xFFFF:
            raise OverflowError("No more UIDs available for this Template Type.")
        return (max_uid & 0xFFFF) + 1

    def values(self) -> Iterator[TypesDef]:
        """Iterate through all the types in the store."""
        if TypesDefStore._db_store is None:
            self._initialize_db_store()
        assert TypesDefStore._db_store is not None, "DB store must be initialized."
        for td in TypesDefStore._db_store.select():
            yield TypesDef(**td)


# Create the TypesDefStore object
types_def_store = TypesDefStore()
