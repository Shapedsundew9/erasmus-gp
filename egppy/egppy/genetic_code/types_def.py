"""Types Definition class and store for EGP types."""

from __future__ import annotations

from array import array
from json import loads
from typing import Any, Final, Generator, Iterable

from bitdict import BitDictABC, bitdict_factory

from egpcommon.common import NULL_TUPLE
from egpcommon.egp_log import DEBUG, Logger, egp_logger
from egpcommon.validator import Validator
from egppy.genetic_code.import_def import ImportDef
from egppy.genetic_code.types_def_bit_dict import TYPESDEF_CONFIG

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# The BitDict format of the EGP type UID
TypesDefBD: type[BitDictABC] = bitdict_factory(
    TYPESDEF_CONFIG,
    name="TypesDefBD",
    title="Type Definition BitDict",
)


class TypesDef(Validator):
    """The Type Definition class stores all the information in order
    to define a type in the EGP system.

    TypesDef objects are final and immutable so that they can be
    cached and reused. Also see the types_def_db.py module.
    """

    __slots__: tuple[str, ...] = (
        "name",
        "alias",
        "default",
        "depth",
        "abstract",
        "imports",
        "parents",
        "children",
        "uid",
        "template",
        "tt",
    )

    def __init__(
        self,
        name: str,
        uid: int | dict[str, Any],
        alias: str | None = None,
        abstract: bool = False,
        default: str | None = None,
        depth: int | None = None,
        imports: Iterable[ImportDef] | dict = NULL_TUPLE,
        parents: Iterable[int | TypesDef] = NULL_TUPLE,
        children: Iterable[int | TypesDef] = NULL_TUPLE,
        template: Iterable[str] | str | None = None,
        tt: int = 0,
    ) -> None:
        """Initialize Type Definition.

        Args:
            name: Name of the type definition.
            uid: Unique identifier of the type definition.
            abstract: True if the type is abstract.
            default: Executable python default instantiation of the type.
            depth: Depth of the type in the inheritance hierarchy. object = 0.
            imports: List of import definitions need to instantiate the type.
            parents: List of type uids or definitions that the type inherits from.
            children: List of type uids or definitions that the type has as children.
            alias: Alias name of the type definition (only for container types).
            template: Template mapping for templated (container) types.
        """
        # Always set frozen to False
        # because we want to be able to set the attributes during initialization.
        self.name: Final[str] = self._name(name)
        self.default: Final[str | None] = self._default(default)
        self.depth: Final[int] = self._depth(depth if depth is not None else 0)
        self.abstract: Final[bool] = self._abstract(abstract)
        self.imports: Final[tuple[ImportDef, ...]] = self._imports(imports)
        self.parents: Final[array[int]] = self._parents(parents)
        self.children: Final[array[int]] = self._children(children)
        self.uid: Final[int] = self._uid(uid)
        self.alias: Final[str | None] = self._alias(alias)
        self.template: Final[list[str] | None] = self._template(template)
        self.tt: Final[int] = self._tt(tt)

    def _alias(self, alias: str | None) -> str | None:
        """Validate the alias of the type definition."""
        if alias is None:
            return None
        self._is_string("alias", alias)
        self._is_length("alias", alias, 1, 64)
        self._is_printable_string("alias", alias)
        return alias

    def _template(self, template: Iterable[str] | None) -> list[str] | None:
        """Validate the template of the type definition."""
        if template is None:
            return None
        if isinstance(template, str):
            template = loads(template)
        return template if isinstance(template, (list, type(None))) else list(template)

    def _tt(self, tt: int) -> int:
        """Validate the Template Type number of the type definition."""
        self._is_int("tt", tt)
        self._in_range("tt", tt, 0, 7)
        return tt

    def __eq__(self, value: object) -> bool:
        """Return True if the value is equal to this object."""
        if isinstance(value, TypesDef):
            return self.uid == value.uid
        return False

    def __ge__(self, other: object) -> bool:
        """Return True if this object's UID is greater than or equal to the other object's UID."""
        if not isinstance(other, TypesDef):
            return NotImplemented
        return self.uid >= other.uid

    def __gt__(self, other: object) -> bool:
        """Return True if this object's UID is greater than the other object's UID."""
        if not isinstance(other, TypesDef):
            return NotImplemented
        return self.uid > other.uid

    def __hash__(self) -> int:
        """Return globally unique hash for the object.
        TypeDefs are unique by design and should not be duplicated.
        """
        return self.uid

    def __iter__(self) -> Generator[Any, Any, None]:
        """
        Allows iteration over the *values* of public instance variables.
        This is define by the to_json() method.
        """
        for value in self.to_json().values():
            yield value

    def __le__(self, other: object) -> bool:
        """Return True if this object's UID is less than or equal to the other object's UID."""
        if not isinstance(other, TypesDef):
            return NotImplemented
        return self.uid <= other.uid

    def __len__(self) -> int:
        """Return the number of publicly exposed variables."""
        return 7

    def __lt__(self, other: object) -> bool:
        """Return True if this object's UID is less than the other object's UID."""
        if not isinstance(other, TypesDef):
            return NotImplemented
        return self.uid < other.uid

    def __ne__(self, value: object) -> bool:
        """Return True if the value is not equal to this object."""
        if not isinstance(value, TypesDef):
            return NotImplemented
        return self.uid != value.uid

    def __repr__(self) -> str:
        """Return the string representation of the type definition."""
        return (
            f"TypesDef(name={self.name!r}, uid={self.uid}, "
            f"abstract={self.abstract}, default={self.default!r}, "
            f"imports={self.imports!r}, parents={self.parents!r}, "
            f"children={self.children!r})"
        )

    def __str__(self) -> str:
        """Return the string representation of the type definition."""
        return self.name

    def _abstract(self, abstract: bool) -> bool:
        """Validate the abstract flag of the type definition."""
        self._is_bool("abstract", abstract)
        return abstract

    def _children(self, children: Iterable[int | TypesDef]) -> array[int]:
        """Mash the children definitions into an array of type uids.
        Names are used to look up the type in the types database on an as needed basis.
        This allows TypesDef objects to be independently cached.
        """
        # If it is already an array no need to copy it. Saves memory.
        # TODO: For Any and tuple there are a lot of children
        # these need to be special cased to save memory.
        if isinstance(children, array) and children.typecode == "i":
            return children
        child_list: list[int] = []
        for child in children:
            if isinstance(child, int):
                child_list.append(child)
            elif isinstance(child, TypesDef):
                child_list.append(child.uid)
            else:
                raise ValueError("Invalid children definition.")
        return array("i", child_list)

    def _default(self, default: str | None) -> str | None:
        """Validate the default instantiation of the type definition."""
        if default is None:
            return None
        self._is_string("default", default)
        self._is_length("default", default, 1, 64)
        self._is_printable_string("default", default)
        return default

    def _depth(self, depth: int) -> int:
        """Validate the depth of the type definition."""
        self._is_int("depth", depth)
        self._in_range("depth", depth, 0, 1024)
        return depth

    def _imports(self, imports: Iterable[ImportDef] | dict) -> tuple[ImportDef, ...]:
        """Mash the import definitions into a tuple of ImportDef objects
        and ensure they are in the ImportDef store."""
        import_list: set[ImportDef] = set()
        for import_def in imports:
            if isinstance(import_def, dict):
                # The import store will ensure that the same import is not duplicated.
                import_list.add(ImportDef(**import_def).freeze())
            elif isinstance(import_def, ImportDef):
                import_list.add(import_def)
            else:
                raise ValueError("Invalid imports definition.")
        return tuple(import_list)

    def _name(self, name: str) -> str:
        """Validate the name of the type definition."""
        if _logger.isEnabledFor(level=DEBUG):
            self._is_string("name", name)
            self._is_length("name", name, 1, 64)
            self._is_printable_string("name", name)
        return name

    def _parents(self, parents: Iterable[int | TypesDef]) -> array[int]:
        """Mash the inheritance definitions into an array of type uids.
        Names are used to look up the type in the types database on an as needed basis.
        This allows TypesDef objects to be independently cached.
        """
        # If it is already an array no need to copy it. Saves memory.
        if isinstance(parents, array) and parents.typecode == "i":
            return parents
        parent_list: list[int] = []
        for parent in parents:
            if isinstance(parent, int):
                parent_list.append(parent)
            elif isinstance(parent, TypesDef):
                parent_list.append(parent.uid)
            else:
                raise ValueError("Invalid parents definition.")
        return array("i", parent_list)

    def _uid(self, uid: int | dict[str, Any]) -> int:
        """Validate the UID of the type definition."""
        if isinstance(uid, int):
            if _logger.isEnabledFor(level=DEBUG):
                self._is_int("uid", uid)
                self._in_range("uid", uid, -(2**31), 2**31 - 1)
            return uid
        elif isinstance(uid, dict):
            # The BitDict will handle the validation.
            return TypesDefBD(uid).to_int()
        else:
            raise ValueError("Invalid UID definition.")

    def bd(self) -> BitDictABC:
        """Return the BitDict object."""
        return TypesDefBD(self.uid)

    def to_json(self) -> dict:
        """Return Type Definition as a JSON serializable dictionary."""
        return {
            "abstract": self.abstract,
            "alias": self.alias,
            "children": list(self.children),
            "default": self.default,
            "depth": self.depth,
            "imports": [idef.to_json() for idef in self.imports],
            "name": self.name,
            "parents": list(self.parents),
            "template": self.template,
            "tt": self.tt,
            "uid": self.uid,
        }

    def xuid(self) -> int:
        """Return the XUID of the type definition."""
        bd = self.bd()
        retval = bd["xuid"]
        assert isinstance(retval, int), "XUID must be an integer."
        return retval
