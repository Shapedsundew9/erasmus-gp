"""Visualize type relationships as an interactive graph using PyVis."""

import json
import os

from pyvis.network import Network


def create_interactive_graph(json_file_path, output_file):
    """Create an interactive graph visualization from a JSON file."""
    # 1. Load the JSON data
    if not os.path.exists(json_file_path):
        print(f"Error: File '{json_file_path}' not found.")
        return

    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. Initialize the PyVis Network
    net = Network(
        height="90vh",
        width="100%",
        bgcolor="#222222",
        select_menu=True,
        cdn_resources="remote",
    )

    print(f"Processing {len(data)} types...")

    # 3. Process Nodes
    for type_name, attributes in data.items():
        uid = attributes.get("uid")
        is_abstract = attributes.get("abstract", False)

        # Format imports: comma-separated list
        imports_list = [i.get("name") for i in attributes.get("imports", [])]
        if len(imports_list) > 5:
            import_str = ", ".join(imports_list[:5]) + f", ... (+{len(imports_list)-5} more)"
        else:
            import_str = ", ".join(imports_list) if imports_list else "None"

        # PLAIN TEXT TOOLTIP
        # We use \n for line breaks. Vis.js renders this natively.
        title_text = (
            f"Name: {type_name}\n"
            f"UID: {uid}\n"
            f"Abstract: {is_abstract}\n"
            f"Depth: {attributes.get('depth')}\n"
            f"Default: {attributes.get('default')}\n"
            f"Imports: {import_str}"
        )

        # Visual styling
        color = "#ff6b6b" if is_abstract else "#4d96f7"
        shape = "dot"
        size = 25 if is_abstract else 15

        net.add_node(
            n_id=uid, label=type_name, title=title_text, color=color, shape=shape, size=size
        )

    # 4. Process Edges
    edge_count = 0
    for type_name, attributes in data.items():
        child_uid = attributes.get("uid")
        parents = attributes.get("parents", [])

        for parent_uid in parents:
            # Connect Parent -> Child
            net.add_edge(
                parent_uid, child_uid, color="rgba(200,200,200,0.5)", arrowStrikethrough=False
            )
            edge_count += 1

    print(f"Added {edge_count} relationships.")

    # 5. Configure Physics and Interaction
    options = {
        "nodes": {"font": {"size": 16, "face": "tahoma", "color": "#ffffff"}, "borderWidth": 2},
        "edges": {
            "color": {"inherit": True},
            "smooth": {"type": "continuous", "forceDirection": "none"},
            "arrows": {"to": {"enabled": True, "scaleFactor": 0.5}},
        },
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -50,
                "centralGravity": 0.005,
                "springLength": 100,
                "springConstant": 0.18,
            },
            "maxVelocity": 146,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"enabled": True, "iterations": 150},
        },
        "interaction": {
            "hover": True,
            "multiselect": True,
            "navigationButtons": True,
            "keyboard": True,
            "tooltipDelay": 200,
        },
    }
    net.set_options(json.dumps(options))

    # 6. Save
    print(f"Generating {output_file}...")
    net.write_html(output_file, notebook=False)
    print("Done! Open the HTML file in your browser.")


if __name__ == "__main__":
    create_interactive_graph(
        "/workspaces/erasmus-gp/egppy/egppy/data/types_def.json",
        "/workspaces/erasmus-gp/types_graph.html",
    )
