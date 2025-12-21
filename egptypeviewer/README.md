# TypeGraph Explorer

A cyberpunk-styled, interactive graph visualization application for exploring Erasmus GP type definition hierarchies using Dash and Dash Cytoscape.

## Features

- **Interactive Graph Visualization**: Click nodes to expand and explore the type hierarchy
- **Cyberpunk Dark Mode**: Neon accents, dark backgrounds, and stylish glassmorphism effects
- **Node Details Panel**: View full JSON metadata for any selected node
- **Refresh & Reset Controls**: Reload data or reset the view to initial state
- **Containerized Deployment**: Ready-to-use Docker configuration

## Quick Start

### Running Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python egptypeviewer/app.py
   ```

3. Open your browser to [http://localhost:8050](http://localhost:8050)

### Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t egptypeviewer .
   ```

2. Run the container:
   ```bash
   docker run -p 8050:8050 egptypeviewer
   ```

3. Open your browser to [http://localhost:8050](http://localhost:8050)

## Usage

- **Click a node**: Expands the node to show its children types
- **Click Refresh Data**: Reloads the types_def.json file from disk
- **Click Reset View**: Returns to the initial view showing only root nodes
- **Select a node**: View its full JSON metadata in the sidebar

## Project Structure

```
egptypeviewer/
  ├── egptypeviewer/
  │     ├── __init__.py       # Package initialization
  │     ├── app.py            # Main Dash application
  │     └── data_loader.py    # JSON parsing and graph data logic
  ├── assets/
  │     └── styles.css        # Custom dark mode CSS
  ├── Dockerfile              # Container definition
  ├── requirements.txt        # Python dependencies
  ├── pyproject.toml          # Package configuration
  └── README.md               # This file
```

## Design

The application follows a "Cyberpunk/Developer Dark Mode" aesthetic:

- **Dark background**: `#1e1e1e`
- **Neon cyan accents**: `#00bcd4`
- **Purple highlights**: `#9c27b0`
- **Glassmorphism sidebar**: Semi-transparent with blur effects

## Data Source

The application visualizes type definitions from `egppy/egppy/data/types_def.json`. This JSON file contains:

- Type names as keys
- Each type has `uid`, `children`, `parents`, and other metadata
- The root node is `object` (uid: 106) which has no parents

## License

See the main repository LICENSE file.
