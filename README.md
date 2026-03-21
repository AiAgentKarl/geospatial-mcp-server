# geospatial-mcp-server

<!-- mcp-name: geospatial-mcp-server -->

MCP Server for geospatial data — gives AI agents access to geocoding, reverse geocoding, POI search, routing info, and area statistics via OpenStreetMap.

**100% free, no API key required.** Uses OpenStreetMap Nominatim + Overpass API.

## Tools

| Tool | Description |
|------|-------------|
| `geocode` | Convert address/place name to coordinates |
| `reverse_geocode` | Convert coordinates to address |
| `search_nearby` | Find POIs nearby (restaurants, hospitals, schools, etc.) |
| `get_route_info` | Distance and bearing between two points |
| `get_area_stats` | Population, area, type info for a place |
| `find_boundaries` | Administrative boundaries of a place |
| `search_pois` | Search points of interest by keyword in an area |

## Installation

```bash
pip install geospatial-mcp-server
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "geospatial": {
      "command": "geospatial-server"
    }
  }
}
```

Or with uvx (no install needed):

```json
{
  "mcpServers": {
    "geospatial": {
      "command": "uvx",
      "args": ["geospatial-mcp-server"]
    }
  }
}
```

## Examples

- "Where is the Eiffel Tower?" → `geocode("Eiffel Tower, Paris")`
- "What's at 48.8566, 2.3522?" → `reverse_geocode(48.8566, 2.3522)`
- "Find restaurants near me" → `search_nearby(48.8566, 2.3522, "restaurant")`
- "How far is Berlin from Munich?" → `get_route_info("Berlin", "Munich")`
- "Tell me about Tokyo" → `get_area_stats("Tokyo")`

## Data Sources

- [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) — Geocoding & reverse geocoding
- [Overpass API](https://overpass-api.de/) — POI search & spatial queries

## License

MIT
