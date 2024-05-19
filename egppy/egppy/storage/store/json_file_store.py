"""JSON File store implementation."""
from io import BufferedRandom
from typing import Any, Iterator
from collections.abc import MutableMapping
from mmap import mmap, ACCESS_WRITE
from json import loads, dumps
from os.path import getsize
from egppy.storage.store.store_abc import StoreABC
from egppy.types.gc_abc import GCABC


class JsonFileStore(StoreABC):
    """A file based store for JSON objects."""
    def __init__(self, file_path: str, search_str: str = '"signature": "{key}"') -> None:
        self.file_path: str = file_path
        self.file: BufferedRandom = open(file=file_path, mode='a+b')
        self.file_size: int = getsize(filename=file_path)
        self.mmap_obj = mmap(fileno=self.file.fileno(), length=0, access=ACCESS_WRITE)
        self.search_str: str = search_str

    def __del__(self) -> None:
        """Close the file and flush the mmap object."""
        self.mmap_obj.flush()
        self.mmap_obj.close()
        self.file.close()

    def __delitem__(self, key: Any) -> None:
        """Delete an item from the store."""
        search_str: bytes = self.search_str.format(key=key).encode(encoding='utf-8')
        self.mmap_obj.seek(pos=0)  # Start from the beginning of the file
        pos: int = self.mmap_obj.find(sub=search_str)
        if pos != -1:
            self.mmap_obj.seek(pos=pos)
            start: int = self.mmap_obj.rfind(sub=b'\n', start=0, stop=pos) + 1  # Find the start
            if start == 0:  # If it's the first line, handle it correctly
                start = pos
            end: int = self.mmap_obj.find(sub=b'\n', start=start) + 1  # Find the end of the line
            if end == 0:  # If it's the last line, handle it correctly
                end = self.file_size
            remaining_data: bytes = self.mmap_obj[end:]
            self.mmap_obj.move(dest=start, src=end, count=len(remaining_data))
            self.mmap_obj.resize(newsize=self.file_size - (end - start))
            self.file_size = self.mmap_obj.size()

    def __getitem__(self, key) -> GCABC:
        """Get an item from the store."""
        search_str: bytes = self.search_str.format(key=key).encode(encoding='utf-8')
        self.mmap_obj.seek(pos=0)  # Start from the beginning of the file
        pos: int = self.mmap_obj.find(sub=search_str)
        if pos != -1:
            raise KeyError(f"Key {key} not found.")
        self.mmap_obj.seek(pos=pos)
        line: bytes = self.mmap_obj.readline()
        return loads(s=line)

    def __iter__(self) -> Iterator:
        """Iterate over the store."""
        self.mmap_obj.seek(pos=0)  # Start from the beginning of the file
        while True:
            line: bytes = self.mmap_obj.readline()
            if not line:
                break
            yield loads(line)

    def __len__(self) -> int:
        self.mmap_obj.seek(pos=0)  # Start from the beginning of the file
        count = 0
        while True:
            line: bytes = self.mmap_obj.readline()
            if not line:
                break
            count += 1
        return count

    def __setitem__(self, key: Any, value: GCABC) -> None:
        """Set an item in the store."""
        del self[key]  # Remove the item if it exists
        self.append_json_objects(jobjs=[value])

    def append_json_objects(self, jobjs) -> None:
        """Append JSON objects to the file."""
        new_data: bytes = ''.join(dumps(obj=obj) + '\n' for obj in jobjs).encode(encoding='utf-8')
        self.mmap_obj.resize(newsize=self.file_size + len(new_data))
        self.mmap_obj.seek(pos=self.file_size)  # Move to the end of the file
        self.mmap_obj.write(bytes=new_data)
        self.file_size = self.mmap_obj.size()

    def update(  # type: ignore pylint: disable=arguments-differ
            self, m: MutableMapping[Any, GCABC]) -> None:
        """Update the store. This is more efficient that setting items one at a time."""
        for key in m:
            del self[key]
        self.append_json_objects(jobjs=m.values())
