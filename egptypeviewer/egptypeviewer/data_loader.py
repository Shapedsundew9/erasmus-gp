"""Data loader module for TypeGraph data processing.

This module provides the TypeGraphData class which handles loading,
indexing, and querying type definition data from a JSON file.
"""

from json import load
from os import environ
from os.path import dirname, exists, join
from typing import Any


class TypeGraphData:
    """Handles loading and processing of type definition graph data.

    Loads type definitions from a JSON file and provides methods to
    query nodes by ID, retrieve root nodes, and access children nodes.

    Attributes:
        filepath: Path to the types_def.json file.
        data: The raw dictionary loaded from JSON (keyed by type name).
        nodes_by_id: Dictionary mapping UID to node data.
    """

    def __init__(self, filepath: str | None = None) -> None:
        """Initialize TypeGraphData with the given JSON file path.

        Args:
            filepath: Path to the types_def.json file. If None, uses
                the TYPES_DEF_PATH environment variable or falls back to
                the default path in egppy/egppy/data/types_def.json.
        """
        if filepath is None:
            # Check for environment variable first
            filepath = environ.get("TYPES_DEF_PATH")

        if filepath is None:
            # Default path relative to this file's package location
            # From egptypeviewer/egptypeviewer/data_loader.py up 3 levels to repo root
            base_dir = dirname(dirname(dirname(__file__)))
            filepath = join(base_dir, "egppy", "egppy", "data", "types_def.json")

        self.filepath: str = filepath
        self.data: dict[str, dict[str, Any]] = {}
        self.nodes_by_id: dict[int, dict[str, Any]] = {}
        self._load_data()

    def _load_data(self) -> None:
        """Load JSON data from file and build lookup indexes."""
        if not exists(self.filepath):
            raise FileNotFoundError(f"Types definition file not found: {self.filepath}")

        with open(self.filepath, "r", encoding="utf-8") as f:
            self.data = load(f)

        # Build ID-based lookup
        self.nodes_by_id = {}
        for name, node_data in self.data.items():
            uid = node_data.get("uid")
            if uid is not None:
                # Add the name to the node data for convenience
                node_with_name = dict(node_data)
                node_with_name["name"] = name
                self.nodes_by_id[uid] = node_with_name

    def reload(self) -> None:
        """Reload the JSON file from disk.

        Useful for refreshing data when the file has been updated.
        """
        self._load_data()

    def get_root_nodes(self) -> list[dict[str, Any]]:
        """Return nodes that have empty parents lists.

        The root node is typically 'object' which has no parents.

        Returns:
            List of node data dictionaries that have no parents.
        """
        roots = []
        for name, node_data in self.data.items():
            parents = node_data.get("parents", [])
            if not parents:
                node_with_name = dict(node_data)
                node_with_name["name"] = name
                roots.append(node_with_name)
        return roots

    def get_node_by_id(self, uid: int) -> dict[str, Any] | None:
        """Get a node by its unique ID.

        Args:
            uid: The unique identifier of the node.

        Returns:
            The node data dictionary or None if not found.
        """
        return self.nodes_by_id.get(uid)

    def get_children(self, uid: int) -> list[dict[str, Any]]:
        """Get the children of a node given its UID.

        Args:
            uid: The unique identifier of the parent node.

        Returns:
            List of child node data dictionaries.
        """
        node = self.nodes_by_id.get(uid)
        if node is None:
            return []

        children_uids = node.get("children", [])
        children = []
        for child_uid in children_uids:
            child_node = self.nodes_by_id.get(child_uid)
            if child_node:
                children.append(child_node)
        return children

    def get_node_by_name(self, name: str) -> dict[str, Any] | None:
        """Get a node by its name.

        Args:
            name: The name of the type.

        Returns:
            The node data dictionary or None if not found.
        """
        node_data = self.data.get(name)
        if node_data is not None:
            node_with_name = dict(node_data)
            node_with_name["name"] = name
            return node_with_name
        return None
