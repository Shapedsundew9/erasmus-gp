"""The problem module contains the classes and functions for the problem object."""

from datetime import datetime
from re import Pattern
from re import compile as regex_compile

from egpcommon.common import EGP_EPOCH, DictTypeAccessor
from egpcommon.common_obj import CommonObj
from egpcommon.validator import Validator


class ProblemConfig(Validator, DictTypeAccessor, CommonObj):
    """Configuration for the problem in EGP.

    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    git_repo_regex_str: str = (
        r"[a-zA-Z0-9_\.-]{1,256}"  # Alphanumeric characters, underscores, dots, and hyphens
    )
    git_repo_regex: Pattern = regex_compile(git_repo_regex_str)

    def __init__(
        self,
        git_hash: bytes | str,
        git_repo: str,
        git_url: str,
        ordered_interface_hash: bytes | str,
        unordered_interface_hash: bytes | str,
        description: str = "",
        ff_code_file: str = "fitness_function.py",
        last_verified_live: datetime | str = EGP_EPOCH,
        name: str = "",
        requirements_file_name: str = "",
        root_path: str = ".",
    ) -> None:
        """Initialize the class."""
        # TODO: Add codon limit for a solution.
        # TODO: Add an execution time limit for a solution.
        # TODO: Add a global loop count limit
        # NOTE: "limits" are actually soft - it is more of a pressure threshold.
        # After the "limit" an evolutionary pressure is applied to get under it - increasing
        # the pressure the further over the limit a solution is.
        self._set_git_attributes(git_hash, git_repo, git_url)
        self._set_interface_hashes(ordered_interface_hash, unordered_interface_hash)
        self._set_optional_attributes(
            description, ff_code_file, last_verified_live, name, requirements_file_name, root_path
        )

    def _set_git_attributes(self, git_hash: bytes | str, git_repo: str, git_url: str) -> None:
        """Set git-related attributes."""
        setattr(self, "git_hash", git_hash)
        setattr(self, "git_repo", git_repo)
        setattr(self, "git_url", git_url)

    def _set_interface_hashes(
        self, ordered_interface_hash: bytes | str, unordered_interface_hash: bytes | str
    ) -> None:
        """Set interface hashes."""
        setattr(self, "ordered_interface_hash", ordered_interface_hash)
        setattr(self, "unordered_interface_hash", unordered_interface_hash)

    def _set_optional_attributes(
        self,
        description: str,
        ff_code_file: str,
        last_verified_live: datetime | str,
        name: str,
        requirements_file_name: str,
        root_path: str,
    ) -> None:
        """Set optional attributes."""
        setattr(self, "description", description)
        setattr(self, "ff_code_file", ff_code_file)
        setattr(self, "last_verified_live", last_verified_live)
        setattr(self, "name", name)
        setattr(self, "requirements_file_name", requirements_file_name)
        setattr(self, "root_path", root_path)

    @property
    def description(self) -> str:
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """User defined arbitrary string. Not used by Erasmus for any
        internal processing or logic."""
        if not self._is_printable_string("description", value):
            raise ValueError(
                "description must be a printable string, but contains non-printable characters"
            )
        if not self._is_length("description", value, 0, 1024):
            raise ValueError(
                f"description must be between 0 and 1024 characters, but is {len(value)} characters"
            )
        self._description = value

    @property
    def ff_code_file(self) -> str:
        """Get the fitness function code file."""
        return self._ff_code_file

    @ff_code_file.setter
    def ff_code_file(self, value: str) -> None:
        """The name of the fitness function code file."""
        if not self._is_filename("ff_code_file", value):
            raise ValueError(f"ff_code_file must be a valid filename, but is {value}")
        self._ff_code_file = value

    @property
    def git_hash(self) -> bytes:
        """Get the git hash."""
        return self._git_hash

    @git_hash.setter
    def git_hash(self, value: bytes | str) -> None:
        """The git hash of the last verified commit.
        NOTE: Older git hashes may be 160 bit SHA1. These are extended
        to 256 bit SHA256 by prefixing zeros.
        """
        if value is None:
            raise ValueError("git_hash must be a bytes or string")
        if isinstance(value, bytes) and len(value) == 20:
            value = b"0" * 12 + value
        elif isinstance(value, str) and len(value) == 40:
            value = "0" * 24 + value
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if not self._is_sha256("git_hash", value):
            raise ValueError(f"git_hash must be a SHA256 hash, but is {value}")
        self._git_hash = value

    @property
    def git_repo(self) -> str:
        """Get the git repo."""
        return self._git_repo

    @git_repo.setter
    def git_repo(self, value: str) -> None:
        """URL/git_repo.git must be a valid git repo url.
        i.e. the git repo name without the 'URL/' and '.git' parts.
        """
        if not self._is_regex("git_repo", value, self.git_repo_regex):
            raise ValueError(
                f"git_repo must match the pattern {self.git_repo_regex_str}, but is {value}"
            )
        self._git_repo = value

    @property
    def git_url(self) -> str:
        """Get the git url."""
        return self._git_url

    @git_url.setter
    def git_url(self, value: str) -> None:
        """The Git base URL *NOT* including the repo name.
        URL/git_repo.git must be a valid git repo url."""
        if not self._is_url("git_url", value):
            raise ValueError(f"git_url must be a valid URL, but is {value}")
        if not self._is_length("git_url", value, 0, 256):
            raise ValueError(
                f"git_url must be between 0 and 256 characters, but is {len(value)} characters"
            )
        self._git_url = value

    @property
    def last_verified_live(self) -> datetime:
        """Get the last verified live."""
        return self._last_verified_live

    @last_verified_live.setter
    def last_verified_live(self, value: datetime | str) -> None:
        """The last verified live timestamp."""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if not self._is_historical_datetime("last_verified_live", value):
            raise ValueError(
                f"last_verified_live must be a historical datetime (not in the future), but is {value}"
            )
        self._last_verified_live = value

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """User defined name for the problem. This field is not utilized by the Erasmus system."""
        if not self._is_printable_string("name", value):
            raise ValueError(
                "name must be a printable string, but contains non-printable characters"
            )
        self._name = value

    @property
    def ordered_interface_hash(self) -> bytes:
        """Get the ordered interface hash."""
        return self._ordered_interface_hash

    @ordered_interface_hash.setter
    def ordered_interface_hash(self, value: bytes | str) -> None:
        """The hash of the ordered interface."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if not self._is_hash8("ordered_interface_hash", value):
            raise ValueError(
                "ordered_interface_hash must be an 8-byte hash, but is "
                f"{len(value) if isinstance(value, bytes) else type(value)}"
            )
        self._ordered_interface_hash = value

    @property
    def requirements_file_name(self) -> str:
        """Get the requirements file name."""
        return self._requirements_file_name

    @requirements_file_name.setter
    def requirements_file_name(self, value: str) -> None:
        """The name of the requirements file."""
        if not self._is_filename("requirements_file_name", value):
            raise ValueError(f"requirements_file_name must be a valid filename, but is {value}")
        self._requirements_file_name = value

    @property
    def root_path(self) -> str:
        """Get the root path."""
        return self._root_path

    @root_path.setter
    def root_path(self, value: str) -> None:
        """The root path of the problem."""
        if not self._is_path("root_path", value):
            raise ValueError(f"root_path must be a valid path, but is {value}")
        self._root_path = value

    def to_json(self) -> dict:
        """Return the configuration as a dictionary."""
        return {
            "git_hash": self.git_hash.hex(),
            "git_repo": self.git_repo,
            "git_url": self.git_url,
            "ordered_interface_hash": self.ordered_interface_hash.hex(),
            "unordered_interface_hash": self.unordered_interface_hash.hex(),
            "description": self.description,
            "ff_code_file": self.ff_code_file,
            "last_verified_live": self.last_verified_live.isoformat(),
            "name": self.name,
            "requirements_file_name": self.requirements_file_name,
            "root_path": self.root_path,
        }

    @property
    def unordered_interface_hash(self) -> bytes:
        """Get the unordered interface hash."""
        return self._unordered_interface_hash

    @unordered_interface_hash.setter
    def unordered_interface_hash(self, value: bytes | str) -> None:
        """The hash of the unordered interface."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        if not self._is_hash8("unordered_interface_hash", value):
            raise ValueError(
                "unordered_interface_hash must be an 8-byte hash, but is "
                f"{len(value) if isinstance(value, bytes) else type(value)}"
            )
        self._unordered_interface_hash = value
