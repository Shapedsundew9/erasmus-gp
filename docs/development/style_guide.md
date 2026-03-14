# Eramsus Style

These conventions are to be used throughout the application.

## Mermaid Charts

A subtle dark theme for Mermaid diagrams balances readability with a sophisticated color palette. The key is using desaturated (muted) background fill colors paired with borders that are only slightly lighter than the fill. This creates a soft, tactile depth rather than a harsh contrast.

**Matte Slate & Muted Jewels**: This theme uses a deep slate-gray foundation. The classification colors are inspired by gemstone hues, but heavily desaturated to maintain a calm, authoritative, and corporate-friendly aesthetic.

Why this works:

* **Low-Contrast Borders:** The stroke color is simply a slightly lighter shade of the fill color. This avoids the stark, harsh lines that make diagrams look like retro neon signs.
* **Desaturated Core:** Even the "Gold" and "Purple" have a high amount of gray mixed into them, making them suitable for long periods of viewing.
Warm/Cool Balance: You have cool blues and greens alongside warmer mauves and golds, giving you plenty of logical classification pairs (e.g., using green for success paths and gold for exceptions).

### Erasmus Semantic Mapping

To maintain visual consistency across the documentation, use the following mapping of theme colors to Erasmus-specific objects:

| Object Type | Class | Description |
| :--- | :--- | :--- |
| **TGC** (Target GC) | `dataBlue` | The existing genetic code being modified or evaluated. |
| **IGC** (Insertion GC) | `dataGreen` | The new genetic code being inserted or added. |
| **RGC** (Resultant GC) | `dataTeal` | The final product of an evolutionary operation. |
| **FGC** (Fetal GC) | `dataGold` | A secondary or temporary GC created during a process. |
| **Codon** | `dataPurple` | Functional primitives (terminal nodes in the GC tree). |
| **GCA / GCB** | `dataNavy` | Sub-genetic codes (Left/Right children) within a composite. |
| **AGC** (Abstract GC) | `dataPlum` | Abstract templates used for evolutionary tracking. |
| **Interface (I/O)** | `dataOlive` | Input/Output interfaces and connectivity nodes. |
| **Warning / Error** | `dataRed` | Exceptions, invalid states, or pruned branches. |

#### Standard Template

Copy and paste this header into every new Mermaid chart to ensure the theme is applied correctly:

```mermaid
%%{init: { 'theme': 'dark', 'themeVariables': { 'lineColor': '#6c7a89', 'textColor': '#edf2f4', 'mainBkg': '#2b2d42', 'primaryBorderColor': '#4a4e69' }}}%%
graph TD
    %% Base/Default (Dark Slate)
    classDef default fill:#2b2d42,stroke:#4a4e69,stroke-width:2px,color:#edf2f4
    
    %% CORE CLASSIFICATIONS
    classDef dataBlue fill:#3a506b,stroke:#5c6b73,stroke-width:2px,color:#ffffff
    classDef dataGreen fill:#425c52,stroke:#5d7a6f,stroke-width:2px,color:#ffffff
    classDef dataGold fill:#6e6246,stroke:#8f8160,stroke-width:2px,color:#ffffff
    classDef dataRed fill:#6e4646,stroke:#8f6060,stroke-width:2px,color:#ffffff
    
    %% EXTENDED CLASSIFICATIONS
    classDef dataPurple fill:#594a5c,stroke:#7b687f,stroke-width:2px,color:#ffffff
    classDef dataTeal fill:#3b5e60,stroke:#5b7a7c,stroke-width:2px,color:#ffffff
    classDef dataPlum fill:#4a3b52,stroke:#685b70,stroke-width:2px,color:#ffffff
    classDef dataOlive fill:#525c42,stroke:#6f7a5d,stroke-width:2px,color:#ffffff
    classDef dataNavy fill:#2c3e50,stroke:#4a5c6e,stroke-width:2px,color:#ffffff

    %% ZONES
    classDef zonePrimary fill:#1f2130,stroke:#3a3e59,stroke-width:2px,stroke-dasharray: 5 5
    classDef zoneExternal fill:#221f2e,stroke:#4a3b52,stroke-width:2px,stroke-dasharray: 5 5

    %% Example usage:
    %% NodeA[TGC: Target]:::dataBlue
    %% NodeB[IGC: Insert]:::dataGreen
```
