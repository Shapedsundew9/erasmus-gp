"""Erasmus GP Type Definition Graph Viewer - Main Dash Application.

A cyberpunk-styled, interactive graph visualization application using
Dash and Dash Cytoscape to explore type definition hierarchies.
"""

from json import dumps

import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import Dash, Input, Output, State, callback, dcc, html, no_update
from data_loader import TypeGraphData

# Initialize the data loader
data_loader = TypeGraphData()

# --- Cytoscape Stylesheet (Cyberpunk/Dark Mode) ---
CYTOSCAPE_STYLESHEET = [
    # Default node styling
    {
        "selector": "node",
        "style": {
            "background-color": "#222",
            "border-color": "#00bcd4",
            "border-width": "2px",
            "content": "data(label)",
            "color": "#fff",
            "text-valign": "center",
            "text-halign": "center",
            "shape": "round-rectangle",
            "width": "label",
            "height": "label",
            "padding": "10px",
            "font-size": "12px",
            "text-wrap": "wrap",
            "text-max-width": "150px",
        },
    },
    # Selected node styling
    {
        "selector": "node:selected",
        "style": {
            "background-color": "#00bcd4",
            "color": "#000",
            "border-color": "#9c27b0",
            "border-width": "3px",
        },
    },
    # Hovered node styling
    {
        "selector": "node:active",
        "style": {
            "overlay-color": "#00bcd4",
            "overlay-opacity": 0.3,
        },
    },
    # Abstract node styling (different border color)
    {
        "selector": "node[?abstract]",
        "style": {
            "border-color": "#9c27b0",
            "border-style": "dashed",
        },
    },
    # Root node styling
    {
        "selector": "node[?isRoot]",
        "style": {
            "background-color": "#1a1a2e",
            "border-color": "#e94560",
            "border-width": "3px",
        },
    },
    # Edge styling
    {
        "selector": "edge",
        "style": {
            "width": 2,
            "line-color": "#555",
            "target-arrow-color": "#555",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 1.2,
        },
    },
    # Selected edge styling
    {
        "selector": "edge:selected",
        "style": {
            "line-color": "#00bcd4",
            "target-arrow-color": "#00bcd4",
        },
    },
]


def create_node_element(node_data: dict, is_root: bool = False) -> dict:
    """Create a Cytoscape node element from node data.

    Args:
        node_data: Dictionary containing node information.
        is_root: Whether this is a root node.

    Returns:
        A Cytoscape-formatted node element dictionary.
    """
    uid = node_data.get("uid")
    name = node_data.get("name", f"uid_{uid}")
    abstract = node_data.get("abstract", False)
    has_children = bool(node_data.get("children", []))

    return {
        "data": {
            "id": str(uid),
            "label": name,
            "abstract": abstract,
            "isRoot": is_root,
            "hasChildren": has_children,
        }
    }


def create_edge_element(parent_uid: int, child_uid: int) -> dict:
    """Create a Cytoscape edge element.

    Args:
        parent_uid: UID of the parent node.
        child_uid: UID of the child node.

    Returns:
        A Cytoscape-formatted edge element dictionary.
    """
    return {
        "data": {
            "id": f"edge_{parent_uid}_{child_uid}",
            "source": str(parent_uid),
            "target": str(child_uid),
        }
    }


def get_initial_elements() -> list[dict]:
    """Get initial graph elements (root nodes only).

    Returns:
        List of Cytoscape elements containing only root nodes.
    """
    elements = []
    roots = data_loader.get_root_nodes()
    for root_node in roots:
        elements.append(create_node_element(root_node, is_root=True))
    return elements


def get_root_selector() -> str:
    """Get the CSS selector for root nodes in breadthfirst layout.

    Returns:
        CSS selector string for root nodes, or empty string if no roots.
    """
    roots = data_loader.get_root_nodes()
    if roots:
        return "#" + str(roots[0]["uid"])
    return ""


# Initialize the Dash app with Bootstrap CYBORG theme (dark mode)
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
)

app.title = "TypeGraph Explorer"

# --- Layout ---
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                # Sidebar (Left, 25% width)
                dbc.Col(
                    [
                        # Title with neon styling
                        html.H2(
                            "TypeGraph Explorer",
                            className="text-center mb-4",
                            style={
                                "color": "#00bcd4",
                                "textShadow": "0 0 10px #00bcd4",
                                "fontWeight": "bold",
                            },
                        ),
                        html.Hr(style={"borderColor": "#555"}),
                        # Controls section
                        html.Div(
                            [
                                html.H5("Controls", style={"color": "#9c27b0"}),
                                dbc.Button(
                                    "🔄 Refresh Data",
                                    id="refresh-btn",
                                    color="info",
                                    outline=True,
                                    className="w-100 mb-2",
                                ),
                                dbc.Button(
                                    "🔙 Reset View",
                                    id="reset-btn",
                                    color="secondary",
                                    outline=True,
                                    className="w-100 mb-3",
                                ),
                            ],
                            className="mb-4",
                        ),
                        html.Hr(style={"borderColor": "#555"}),
                        # Legend
                        html.Div(
                            [
                                html.H5("Legend", style={"color": "#9c27b0"}),
                                html.Div(
                                    [
                                        html.Span(
                                            "●",
                                            style={
                                                "color": "#e94560",
                                                "fontSize": "20px",
                                                "marginRight": "8px",
                                            },
                                        ),
                                        html.Span(
                                            "Root Node",
                                            style={"color": "#aaa"},
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "◯",
                                            style={
                                                "color": "#9c27b0",
                                                "fontSize": "18px",
                                                "marginRight": "8px",
                                            },
                                        ),
                                        html.Span(
                                            "Abstract Type",
                                            style={"color": "#aaa"},
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "●",
                                            style={
                                                "color": "#00bcd4",
                                                "fontSize": "20px",
                                                "marginRight": "8px",
                                            },
                                        ),
                                        html.Span(
                                            "Concrete Type",
                                            style={"color": "#aaa"},
                                        ),
                                    ],
                                    className="mb-2",
                                ),
                            ],
                            className="mb-4",
                        ),
                        html.Hr(style={"borderColor": "#555"}),
                        # Node Details Panel
                        html.Div(
                            [
                                html.H5("Node Details", style={"color": "#9c27b0"}),
                                html.Div(
                                    id="node-details",
                                    style={
                                        "backgroundColor": "#1a1a2e",
                                        "borderRadius": "8px",
                                        "padding": "15px",
                                        "border": "1px solid #333",
                                        "minHeight": "200px",
                                        "maxHeight": "400px",
                                        "overflow": "auto",
                                    },
                                    children=[
                                        html.P(
                                            "Click a node to view details",
                                            style={"color": "#666", "fontStyle": "italic"},
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                    width=3,
                    style={
                        "backgroundColor": "rgba(30, 30, 46, 0.95)",
                        "padding": "20px",
                        "borderRight": "1px solid #333",
                        "height": "100vh",
                        "overflowY": "auto",
                    },
                ),
                # Main Graph Area (Right, 75% width)
                dbc.Col(
                    [
                        cyto.Cytoscape(
                            id="cytoscape-graph",
                            elements=get_initial_elements(),
                            stylesheet=CYTOSCAPE_STYLESHEET,
                            layout={
                                "name": "breadthfirst",
                                "directed": True,
                                "roots": get_root_selector(),
                                "spacingFactor": 1.5,
                            },
                            style={"width": "100%", "height": "100vh"},
                            responsive=True,
                            minZoom=0.1,
                            maxZoom=3,
                            boxSelectionEnabled=True,
                        ),
                    ],
                    width=9,
                    style={"padding": "0"},
                ),
            ],
            className="g-0",
        ),
        # Store for expanded nodes tracking
        dcc.Store(id="expanded-nodes", data=[]),
    ],
    fluid=True,
    style={"padding": "0", "margin": "0", "backgroundColor": "#1e1e1e"},
)


# --- Callbacks ---


@callback(
    Output("cytoscape-graph", "elements"),
    Output("expanded-nodes", "data"),
    Input("cytoscape-graph", "tapNodeData"),
    State("cytoscape-graph", "elements"),
    State("expanded-nodes", "data"),
    prevent_initial_call=True,
)
def expand_node(tap_data, current_elements, expanded_nodes):
    """Expand a node to show its children when clicked.

    Args:
        tap_data: Data from the tapped node.
        current_elements: Current graph elements.
        expanded_nodes: List of already expanded node IDs.

    Returns:
        Updated elements and expanded nodes list.
    """
    if tap_data is None:
        return no_update, no_update

    node_id = tap_data.get("id")
    if node_id is None:
        return no_update, no_update

    # Check if node is already expanded
    if node_id in expanded_nodes:
        return no_update, no_update

    # Get children for this node
    uid = int(node_id)
    children = data_loader.get_children(uid)

    if not children:
        # No children to add, but mark as expanded to avoid future lookups
        expanded_nodes.append(node_id)
        return no_update, expanded_nodes

    # Get existing node and edge IDs
    existing_ids = set()
    for element in current_elements:
        elem_id = element.get("data", {}).get("id")
        if elem_id:
            existing_ids.add(elem_id)

    # Add new nodes and edges
    new_elements = list(current_elements)
    for child in children:
        child_id = str(child.get("uid"))

        # Add node if it doesn't exist
        if child_id not in existing_ids:
            new_elements.append(create_node_element(child))
            existing_ids.add(child_id)

        # Add edge if it doesn't exist
        edge_id = f"edge_{node_id}_{child_id}"
        if edge_id not in existing_ids:
            new_elements.append(create_edge_element(uid, child.get("uid")))
            existing_ids.add(edge_id)

    expanded_nodes.append(node_id)
    return new_elements, expanded_nodes


@callback(
    Output("node-details", "children"),
    Input("cytoscape-graph", "tapNodeData"),
)
def display_node_details(tap_data):
    """Display details of the selected node.

    Args:
        tap_data: Data from the tapped node.

    Returns:
        HTML content showing node details.
    """
    if tap_data is None:
        return html.P(
            "Click a node to view details",
            style={"color": "#666", "fontStyle": "italic"},
        )

    node_id = tap_data.get("id")
    if node_id is None:
        return html.P("No node selected", style={"color": "#666"})

    # Get full node data
    uid = int(node_id)
    node_data = data_loader.get_node_by_id(uid)

    if node_data is None:
        return html.P(f"Node {node_id} not found", style={"color": "#e94560"})

    # Format the node data as pretty JSON
    formatted_json = dumps(node_data, indent=2, default=str)

    return dcc.Markdown(
        f"```json\n{formatted_json}\n```",
        style={"color": "#00bcd4", "fontSize": "12px"},
    )


@callback(
    Output("cytoscape-graph", "elements", allow_duplicate=True),
    Output("expanded-nodes", "data", allow_duplicate=True),
    Input("refresh-btn", "n_clicks"),
    prevent_initial_call=True,
)
def refresh_data(n_clicks):
    """Refresh data from the JSON file and reset the graph.

    Args:
        n_clicks: Number of times the button was clicked.

    Returns:
        Reset elements and cleared expanded nodes list.
    """
    if n_clicks is None:
        return no_update, no_update

    data_loader.reload()
    return get_initial_elements(), []


@callback(
    Output("cytoscape-graph", "elements", allow_duplicate=True),
    Output("expanded-nodes", "data", allow_duplicate=True),
    Input("reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def reset_view(n_clicks):
    """Reset the graph view to show only root nodes.

    Args:
        n_clicks: Number of times the button was clicked.

    Returns:
        Initial elements and cleared expanded nodes list.
    """
    if n_clicks is None:
        return no_update, no_update

    return get_initial_elements(), []


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050, use_reloader=False)
