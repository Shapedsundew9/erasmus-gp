"""JSON File store implementation."""

from collections.abc import Hashable, MutableMapping
from io import BufferedRandom
from json import dumps, loads
from mmap import ACCESS_WRITE, mmap
from os.path import exists
from tempfile import TemporaryFile
from typing import Any, Iterator

from egpcommon.egp_log import Logger, egp_logger
from egppy.storage.store.storable_obj_abc import StorableObjABC
from egppy.storage.store.store_abc import StoreABC
from egppy.storage.store.store_base import StoreBase

# Standard EGP logging pattern
_logger: Logger = egp_logger(name=__name__)


# Header
_HEADER = b"JSON File Store for T types in EGP\n"


class JSONFileStore(StoreBase, StoreABC):
    """A file based store for StorableObjABC objects using the json() method.

    JSONFileStore is not intended to be quick or efficient in any way. It is intended for
    testing or as a place holder for a StoreABC object when a NullStore is not appropriate.
    By definition it is limited to JSONizable data types.

    Individual JSON objects are stored in the file as separate lines. The file is memory
    mapped and new JSON objects are appended to the end of the file. The JSON objects are
    identified by the key being added into the JSON object as "__key__": key. This allows the
    JSON object to be found by searching for the key in the file.
    """

    def __init__(self, flavor: type[StorableObjABC], file_path: str | None = None) -> None:
        """Constructor for JSONFileStore"""
        if file_path is not None:
            empty_file: bool = not exists(path=file_path)
            self.file: BufferedRandom = open(file=file_path, mode="a+b")
        else:
            self.file = TemporaryFile(suffix=".json")
            empty_file = True
        if empty_file:
            self.file.write(_HEADER)
        self.file.seek(0)
        self.mmap_obj = mmap(fileno=self.file.fileno(), length=0, access=ACCESS_WRITE)
        self.file_size: int = self.mmap_obj.size()
        self.search_str: str = '"__key__": "{key}"'
        super().__init__(flavor=flavor)

    def __contains__(self, key: Hashable) -> bool:
        """Check if an item is in the store."""
        assert isinstance(key, str), f"Key must be a string, not {type(key)} for JSONFileStore."
        search_str: bytes = self.search_str.format(key=key).encode(encoding="utf-8")
        self.mmap_obj.seek(0)
        return self.mmap_obj.find(search_str) != -1

    def __del__(self) -> None:
        """Close the file and flush the mmap object."""
        self.mmap_obj.flush()
        self.mmap_obj.close()
        self.file.close()

    def __delitem__(self, key: Hashable) -> None:
        """Delete an item from the store."""
        assert isinstance(key, str), f"Key must be a string, not {type(key)} for JSONFileStore."
        search_str: bytes = self.search_str.format(key=key).encode(encoding="utf-8")
        self.mmap_obj.seek(0)  # Start from the beginning of the file
        pos: int = self.mmap_obj.find(search_str)
        if pos != -1:
            self.mmap_obj.seek(pos)
            start: int = self.mmap_obj.rfind(b"\n", 0, pos) + 1  # Find the start
            if start == 0:  # If it's the first line, handle it correctly
                start = pos
            end: int = self.mmap_obj.find(b"\n", start) + 1  # Find the end of the line
            if end == 0:  # If it's the last line, handle it correctly
                end = self.file_size
            remaining_data: bytes = self.mmap_obj[end:]
            self.mmap_obj.move(start, end, len(remaining_data))
            self.mmap_obj.resize(self.file_size - (end - start))
            self.file_size = self.mmap_obj.size()

    def __getitem__(self, key: Hashable) -> Any:
        """Get an item from the store."""
        assert isinstance(key, str), f"Key must be a string, not {type(key)} for JSONFileStore."
        search_str: bytes = self.search_str.format(key=key).encode(encoding="utf-8")
        self.mmap_obj.seek(0)  # Start from the beginning of the file
        pos: int = self.mmap_obj.find(search_str)
        if pos == -1:
            raise KeyError(f"Key {key} not found.")
        start = self.mmap_obj.rfind(b"\n", 0, pos) + 1  # Find the start of the line
        self.mmap_obj.seek(start)
        line: bytes = self.mmap_obj.readline()
        data = loads(s=line)
        return self.flavor(data["__value__"])

    def __iter__(self) -> Iterator:
        """Iterate over the store."""
        self.mmap_obj.seek(0)  # Start from the beginning of the file
        self.mmap_obj.readline()  # Skip the header line
        while True:
            line: bytes = self.mmap_obj.readline()
            if not line:
                break
            data = loads(line)
            yield data["__key__"]

    def __len__(self) -> int:
        self.mmap_obj.seek(0)  # Start from the beginning of the file
        count = 0
        while True:
            line: bytes = self.mmap_obj.readline()
            if not line:
                break
            count += 1
        return count - 1  # Subtract 1 for the header line

    def __setitem__(self, key: Hashable, value: StorableObjABC) -> None:
        """Set an item in the store."""
        assert isinstance(key, str), f"Key must be a string, not {type(key)} for JSONFileStore."
        self.append_json_objects(jobjs={key: value})

    def append_json_objects(self, jobjs: MutableMapping[Hashable, StorableObjABC]) -> None:
        """Append JSON objects to the file."""
        jds = [{"__key__": str(k), "__value__": v.to_json()} for k, v in jobjs.items()]
        new_data: bytes = "".join(dumps(obj=v) + "\n" for v in jds).encode(encoding="utf-8")
        self.mmap_obj.resize(self.file_size + len(new_data))
        self.mmap_obj.seek(self.file_size)  # Move to the end of the file
        self.mmap_obj.write(new_data)
        self.file_size = self.mmap_obj.size()
