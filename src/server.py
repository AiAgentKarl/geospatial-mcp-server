"""
Geospatial MCP Server — Geodaten fuer AI Agents.
Geocoding, POI-Suche, Routing und Gebietsstatistiken via OpenStreetMap.
"""

from mcp.server.fastmcp import FastMCP

from src.tools.geo import (
    geocode,
    reverse_geocode,
    search_nearby,
    get_route_info,
    get_area_stats,
    find_boundaries,
    search_pois,
)

# FastMCP Server erstellen
mcp = FastMCP(
    "geospatial-mcp-server",
    instructions=(
        "Geospatial data server for AI agents. "
        "Provides geocoding, reverse geocoding, nearby POI search, "
        "distance calculation, area statistics, boundary lookup, "
        "and keyword-based POI search. "
        "All data comes from OpenStreetMap (Nominatim + Overpass API). "
        "No API key required."
    ),
)


# --- Tools registrieren ---

@mcp.tool()
async def geocode_tool(query: str) -> dict:
    """Convert an address or place name to geographic coordinates.

    Args:
        query: Address or place name (e.g. "Eiffel Tower, Paris", "1600 Pennsylvania Ave, Washington DC")

    Returns:
        Coordinates, address details and result type
    """
    return await geocode(query)


@mcp.tool()
async def reverse_geocode_tool(lat: float, lon: float) -> dict:
    """Convert geographic coordinates to an address.

    Args:
        lat: Latitude (e.g. 48.8566)
        lon: Longitude (e.g. 2.3522)

    Returns:
        Address and location details
    """
    return await reverse_geocode(lat, lon)


@mcp.tool()
async def search_nearby_tool(
    lat: float,
    lon: float,
    category: str,
    radius_m: int = 1000,
) -> dict:
    """Find points of interest nearby (restaurants, hospitals, schools, etc.).

    Args:
        lat: Center latitude
        lon: Center longitude
        category: POI category — one of: restaurant, cafe, bar, fast_food, hospital, pharmacy, doctor, school, university, kindergarten, bank, atm, fuel, parking, supermarket, bakery, hotel, museum, park, playground, police, fire_station, post_office, library, cinema, theatre, gym, swimming_pool, bus_stop, train_station, subway, charging_station
        radius_m: Search radius in meters (default: 1000, max: 10000)

    Returns:
        List of nearby POIs with name, coordinates, distance
    """
    return await search_nearby(lat, lon, category, radius_m)


@mcp.tool()
async def get_route_info_tool(origin: str, destination: str) -> dict:
    """Calculate distance and direction between two places (straight line).

    Args:
        origin: Starting place (e.g. "Berlin")
        destination: Target place (e.g. "Munich")

    Returns:
        Distance in km/miles, bearing, direction, coordinates of both points
    """
    return await get_route_info(origin, destination)


@mcp.tool()
async def get_area_stats_tool(place_name: str) -> dict:
    """Get statistics about a place (population, area, type).

    Args:
        place_name: Name of the place (e.g. "Berlin", "Tokyo", "New York")

    Returns:
        Population, area, administrative type, Wikipedia link and more
    """
    return await get_area_stats(place_name)


@mcp.tool()
async def find_boundaries_tool(place_name: str) -> dict:
    """Find administrative boundaries of a place.

    Args:
        place_name: Name of the place (e.g. "Bavaria", "California", "Paris")

    Returns:
        Boundary info with bounding box and administrative hierarchy
    """
    return await find_boundaries(place_name)


@mcp.tool()
async def search_pois_tool(
    query: str,
    lat: float,
    lon: float,
    radius_m: int = 5000,
) -> dict:
    """Search points of interest by keyword in an area.

    Args:
        query: Search keyword (e.g. "Starbucks", "Museum", "Train Station")
        lat: Center latitude
        lon: Center longitude
        radius_m: Search radius in meters (default: 5000, max: 25000)

    Returns:
        List of matching POIs with name, coordinates, distance
    """
    return await search_pois(query, lat, lon, radius_m)


def main():
    """Server starten."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
