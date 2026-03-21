"""
OpenStreetMap API Client — Nominatim + Overpass
Nutzt httpx fuer async HTTP-Anfragen.
"""

import httpx
from typing import Any


# Nominatim verlangt einen User-Agent Header
USER_AGENT = "GeospatialMCPServer/0.1.0"
NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Timeout fuer alle Anfragen (Overpass kann langsam sein)
TIMEOUT = httpx.Timeout(30.0, connect=10.0)


def _get_headers() -> dict[str, str]:
    """Standard-Headers fuer Nominatim (User-Agent ist Pflicht)."""
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }


async def nominatim_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """
    Geocoding: Adresse/Ortsname -> Koordinaten.
    Nutzt Nominatim /search Endpoint.
    """
    params = {
        "q": query,
        "format": "json",
        "limit": limit,
        "addressdetails": 1,
        "extratags": 1,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{NOMINATIM_BASE}/search",
            params=params,
            headers=_get_headers(),
        )
        response.raise_for_status()
        return response.json()


async def nominatim_reverse(lat: float, lon: float) -> dict[str, Any]:
    """
    Reverse Geocoding: Koordinaten -> Adresse.
    Nutzt Nominatim /reverse Endpoint.
    """
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "extratags": 1,
    }
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(
            f"{NOMINATIM_BASE}/reverse",
            params=params,
            headers=_get_headers(),
        )
        response.raise_for_status()
        return response.json()


async def nominatim_lookup(query: str) -> dict[str, Any] | None:
    """
    Einzelnen Ort suchen und Details zurueckgeben.
    Gibt das erste Ergebnis zurueck oder None.
    """
    results = await nominatim_search(query, limit=1)
    if results:
        return results[0]
    return None


async def overpass_query(query: str) -> dict[str, Any]:
    """
    Overpass API Abfrage ausfuehren.
    Erwartet eine vollstaendige Overpass QL Query.
    """
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(
            OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        return response.json()


async def overpass_nearby(
    lat: float,
    lon: float,
    category: str,
    radius_m: int = 1000,
) -> list[dict[str, Any]]:
    """
    POIs in der Naehe suchen via Overpass.
    Unterstuetzte Kategorien werden auf OSM-Tags gemappt.
    """
    # Kategorie auf OSM-Tags mappen
    tag_mapping = {
        "restaurant": '"amenity"="restaurant"',
        "cafe": '"amenity"="cafe"',
        "bar": '"amenity"="bar"',
        "fast_food": '"amenity"="fast_food"',
        "hospital": '"amenity"="hospital"',
        "pharmacy": '"amenity"="pharmacy"',
        "doctor": '"amenity"="doctors"',
        "school": '"amenity"="school"',
        "university": '"amenity"="university"',
        "kindergarten": '"amenity"="kindergarten"',
        "bank": '"amenity"="bank"',
        "atm": '"amenity"="atm"',
        "fuel": '"amenity"="fuel"',
        "parking": '"amenity"="parking"',
        "supermarket": '"shop"="supermarket"',
        "bakery": '"shop"="bakery"',
        "hotel": '"tourism"="hotel"',
        "museum": '"tourism"="museum"',
        "park": '"leisure"="park"',
        "playground": '"leisure"="playground"',
        "police": '"amenity"="police"',
        "fire_station": '"amenity"="fire_station"',
        "post_office": '"amenity"="post_office"',
        "library": '"amenity"="library"',
        "cinema": '"amenity"="cinema"',
        "theatre": '"amenity"="theatre"',
        "gym": '"leisure"="fitness_centre"',
        "swimming_pool": '"leisure"="swimming_pool"',
        "bus_stop": '"highway"="bus_stop"',
        "train_station": '"railway"="station"',
        "subway": '"railway"="subway_entrance"',
        "charging_station": '"amenity"="charging_station"',
    }

    # Wenn Kategorie bekannt, nutze spezifischen Tag
    osm_filter = tag_mapping.get(category.lower())
    if not osm_filter:
        # Fallback: Suche nach Name oder beliebigem Amenity-Tag
        osm_filter = f'"amenity"="{category}"'

    query = f"""
    [out:json][timeout:25];
    (
      node[{osm_filter}](around:{radius_m},{lat},{lon});
      way[{osm_filter}](around:{radius_m},{lat},{lon});
    );
    out center body;
    """

    result = await overpass_query(query)
    return result.get("elements", [])


async def overpass_search_pois(
    keyword: str,
    lat: float,
    lon: float,
    radius_m: int = 5000,
) -> list[dict[str, Any]]:
    """
    POIs nach Freitext-Keyword suchen via Overpass.
    Sucht in name-Tags innerhalb des Radius.
    """
    query = f"""
    [out:json][timeout:25];
    (
      node["name"~"{keyword}",i](around:{radius_m},{lat},{lon});
      way["name"~"{keyword}",i](around:{radius_m},{lat},{lon});
    );
    out center body;
    """

    result = await overpass_query(query)
    return result.get("elements", [])
