# geospatial-mcp-server

**Geospatial data for AI agents** — geocoding, reverse geocoding, POI search, routing, and area statistics via OpenStreetMap.

[![PyPI version](https://badge.fury.io/py/geospatial-mcp-server.svg)](https://pypi.org/project/geospatial-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **100% free, no API key required.** Uses OpenStreetMap Nominatim + Overpass API.

## Quick Start

```bash
pip install geospatial-mcp-server
```

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

## What Can You Do?

**Ask your AI agent things like:**
- *"What are the coordinates of the Eiffel Tower?"*
- *"Find all hospitals within 2km of Times Square"*
- *"What's at latitude 48.8566, longitude 2.3522?"*
- *"How far is it from Berlin to Munich?"*
- *"Show me the population and area of Tokyo"*

## 7 Tools

| Tool | What it does |
|------|-------------|
| `geocode` | Convert address/place name to coordinates |
| `reverse_geocode` | Convert coordinates to address |
| `search_nearby` | Find POIs nearby (restaurants, hospitals, schools, etc.) |
| `get_route_info` | Distance and bearing between two points |
| `get_area_stats` | Population, area, and type info for a place |
| `find_boundaries` | Administrative boundaries of a place |
| `search_pois` | Search points of interest by keyword in an area |

## Related Servers

- [openmeteo-mcp-server](https://pypi.org/project/openmeteo-mcp-server/) — Weather and climate data
- [climate-risk-mcp-server](https://pypi.org/project/climate-risk-mcp-server/) — Climate TRACE, NOAA, ESG data

## License

MIT
