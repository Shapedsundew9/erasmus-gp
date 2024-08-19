"""The problem module contains the classes and functions for the problem object."""
from datetime import datetime
from hashlib import sha256
from re import Pattern, compile as regex_compile
from egppy.common.common import EGP_EPOCH, Validator, DictTypeAccessor


# The beginning
ACYBERGENESIS_PROBLEM = sha256(b"Acybergenesis Problem").digest()


class ProblemConfig(Validator, DictTypeAccessor):
    """Configuration for the problem in EGP.
    
    Must set from the JSON or internal types and validate the values.
    Getting the values returns the internal types.
    The to_json() method returns the JSON types.
    """

    git_repo_regex_str: str = r"[a-zA-Z0-9_\\.-]{1,256}"
    git_repo_regex: Pattern[str] = regex_compile(git_repo_regex_str)

    def __init__(self,
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
        setattr(self, "git_hash", git_hash)
        setattr(self, "git_repo", git_repo)
        setattr(self, "git_url", git_url)
        setattr(self, "ordered_interface_hash", ordered_interface_hash)
        setattr(self, "unordered_interface_hash", unordered_interface_hash)
        setattr(self, "description", description)
        setattr(self, "ff_code_file", ff_code_file)
        setattr(self, "last_verified_live", last_verified_live)
        setattr(self, "name", name)
        setattr(self, "requirements_file_name", requirements_file_name)
        setattr(self, "root_path", root_path)

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
        assert value is not None, "git_hash must be a string"
        if isinstance(value, bytes) and len(value) == 20:
            value = b'0' * 12 + value
        elif isinstance(value, str) and len(value) == 40:
            value = "0" * 24 + value
        if isinstance(value, str):
            value = bytes.fromhex(value)
        self._is_sha256("git_hash", value)
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
        self._is_regex("git_repo", value, self.git_repo_regex)
        self._git_repo = value

    @property
    def git_url(self) -> str:
        """Get the git url."""
        return self._git_url

    @git_url.setter
    def git_url(self, value: str) -> None:
        """The Git base URL *NOT* including the repo name.
        URL/git_repo.git must be a valid git repo url."""
        self._is_url("git_url", value)
        self._is_length("git_url", value, 0, 256)
        self._git_url = value

    @property
    def ordered_interface_hash(self) -> bytes:
        """Get the ordered interface hash."""
        return self._ordered_interface_hash

    @ordered_interface_hash.setter
    def ordered_interface_hash(self, value: bytes | str) -> None:
        """The hash of the ordered interface."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        self._is_hash8("ordered_interface_hash", value)
        self._ordered_interface_hash = value

    @property
    def unordered_interface_hash(self) -> bytes:
        """Get the unordered interface hash."""
        return self._unordered_interface_hash

    @unordered_interface_hash.setter
    def unordered_interface_hash(self, value: bytes | str) -> None:
        """The hash of the unordered interface."""
        if isinstance(value, str):
            value = bytes.fromhex(value)
        self._is_hash8("unordered_interface_hash", value)
        self._unordered_interface_hash = value

    @property
    def description(self) -> str:
        """Get the description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """User defined arbitary string. Not used by Erasmus."""
        self._is_printable_string("description", value)
        self._is_length("description", value, 0, 1024)
        self._description = value

    @property
    def ff_code_file(self) -> str:
        """Get the fitness function code file."""
        return self._ff_code_file

    @ff_code_file.setter
    def ff_code_file(self, value: str) -> None:
        """The name of the fitness function code file."""
        self._is_filename("ff_code_file", value)
        self._ff_code_file = value

    @property
    def last_verified_live(self) -> datetime:
        """Get the last verified live."""
        return self._last_verified_live

    @last_verified_live.setter
    def last_verified_live(self, value: datetime | str) -> None:
        """The last verified live timestamp."""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        self._is_historical_datetime("last_verified_live", value)
        self._last_verified_live = value

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """User defined name for the problem. Not used by Erasmus."""
        self._is_printable_string("name", value)
        self._is_length("name", value, 0, 64)
        self._name = value

    @property
    def requirements_file_name(self) -> str:
        """Get the requirements file name."""
        return self._requirements_file_name

    @requirements_file_name.setter
    def requirements_file_name(self, value: str) -> None:
        """The name of the requirements file."""
        self._is_filename("requirements_file_name", value)
        self._requirements_file_name = value

    @property
    def root_path(self) -> str:
        """Get the root path."""
        return self._root_path

    @root_path.setter
    def root_path(self, value: str) -> None:
        """The root path of the problem."""
        self._is_path("root_path", value)
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
