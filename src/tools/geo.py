"""
Geospatial MCP Tools — 7 Tools fuer Geodaten.
Nutzt OpenStreetMap Nominatim + Overpass API.
"""

import math
from typing import Any

from src.clients.osm import (
    nominatim_search,
    nominatim_reverse,
    nominatim_lookup,
    overpass_nearby,
    overpass_search_pois,
)


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine-Formel: Berechnet Entfernung zwischen zwei Koordinaten in km.
    """
    R = 6371.0  # Erdradius in km

    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def _bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Berechnet die Peilung (Bearing) in Grad von Punkt 1 zu Punkt 2."""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    dlon = math.radians(lon2 - lon1)

    x = math.sin(dlon) * math.cos(lat2_r)
    y = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(dlon)

    bearing_rad = math.atan2(x, y)
    return (math.degrees(bearing_rad) + 360) % 360


def _bearing_to_direction(bearing: float) -> str:
    """Wandelt Bearing in Himmelsrichtung um."""
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing / 45) % 8
    return directions[index]


def _format_element(element: dict[str, Any]) -> dict[str, Any]:
    """Formatiert ein Overpass-Element fuer die Ausgabe."""
    tags = element.get("tags", {})
    # Koordinaten: Bei Way-Elementen center nutzen
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")

    result = {
        "name": tags.get("name", "Unbekannt"),
        "type": element.get("type", "unknown"),
        "lat": lat,
        "lon": lon,
    }

    # Nuetzliche Tags hinzufuegen wenn vorhanden
    useful_tags = [
        "addr:street", "addr:housenumber", "addr:city", "addr:postcode",
        "phone", "website", "opening_hours", "cuisine", "brand",
        "wheelchair", "internet_access",
    ]
    for tag in useful_tags:
        if tag in tags:
            result[tag.replace(":", "_")] = tags[tag]

    return result


async def geocode(query: str) -> dict[str, Any]:
    """
    Adresse oder Ortsname in Koordinaten umwandeln.

    Args:
        query: Adresse oder Ortsname (z.B. "Brandenburger Tor, Berlin")

    Returns:
        Koordinaten, Adressdetails und Typ des Ergebnisses
    """
    results = await nominatim_search(query, limit=5)

    if not results:
        return {"error": f"Keine Ergebnisse fuer '{query}' gefunden."}

    formatted = []
    for r in results:
        entry = {
            "name": r.get("display_name", ""),
            "lat": float(r.get("lat", 0)),
            "lon": float(r.get("lon", 0)),
            "type": r.get("type", "unknown"),
            "class": r.get("class", "unknown"),
            "importance": round(float(r.get("importance", 0)), 4),
        }
        # Adressdetails hinzufuegen
        address = r.get("address", {})
        if address:
            entry["address"] = {
                k: v for k, v in address.items()
                if k not in ("country_code",)
            }
        formatted.append(entry)

    return {
        "query": query,
        "results_count": len(formatted),
        "results": formatted,
    }


async def reverse_geocode(lat: float, lon: float) -> dict[str, Any]:
    """
    Koordinaten in Adresse umwandeln.

    Args:
        lat: Breitengrad (z.B. 48.8566)
        lon: Laengengrad (z.B. 2.3522)

    Returns:
        Adresse und Details zum Standort
    """
    try:
        result = await nominatim_reverse(lat, lon)
    except Exception as e:
        return {"error": f"Reverse Geocoding fehlgeschlagen: {str(e)}"}

    if "error" in result:
        return {"error": result["error"]}

    address = result.get("address", {})
    return {
        "lat": lat,
        "lon": lon,
        "display_name": result.get("display_name", ""),
        "type": result.get("type", "unknown"),
        "class": result.get("class", "unknown"),
        "address": {
            k: v for k, v in address.items()
            if k not in ("country_code",)
        },
    }


async def search_nearby(
    lat: float,
    lon: float,
    category: str,
    radius_m: int = 1000,
) -> dict[str, Any]:
    """
    POIs in der Naehe suchen (Restaurants, Krankenhaeuser, Schulen, etc.).

    Args:
        lat: Breitengrad des Mittelpunkts
        lon: Laengengrad des Mittelpunkts
        category: Kategorie (restaurant, hospital, school, pharmacy, supermarket, hotel, park, bank, fuel, etc.)
        radius_m: Suchradius in Metern (Standard: 1000, Max: 10000)

    Returns:
        Liste der gefundenen POIs mit Name, Koordinaten und Details
    """
    # Radius begrenzen
    radius_m = min(max(radius_m, 100), 10000)

    try:
        elements = await overpass_nearby(lat, lon, category, radius_m)
    except Exception as e:
        return {"error": f"Overpass-Abfrage fehlgeschlagen: {str(e)}"}

    # Ergebnisse formatieren und Entfernung berechnen
    pois = []
    for el in elements:
        formatted = _format_element(el)
        if formatted["lat"] and formatted["lon"]:
            formatted["distance_m"] = round(
                _haversine(lat, lon, formatted["lat"], formatted["lon"]) * 1000
            )
        pois.append(formatted)

    # Nach Entfernung sortieren
    pois.sort(key=lambda x: x.get("distance_m", 99999))

    return {
        "center": {"lat": lat, "lon": lon},
        "category": category,
        "radius_m": radius_m,
        "results_count": len(pois),
        "results": pois[:50],  # Max 50 Ergebnisse
    }


async def get_route_info(origin: str, destination: str) -> dict[str, Any]:
    """
    Entfernung und Richtung zwischen zwei Orten berechnen.

    Args:
        origin: Startort (z.B. "Berlin")
        destination: Zielort (z.B. "Muenchen")

    Returns:
        Luftlinie-Entfernung in km, Richtung und Koordinaten beider Punkte
    """
    # Beide Orte geocoden
    origin_result = await nominatim_lookup(origin)
    if not origin_result:
        return {"error": f"Startort '{origin}' nicht gefunden."}

    dest_result = await nominatim_lookup(destination)
    if not dest_result:
        return {"error": f"Zielort '{destination}' nicht gefunden."}

    lat1 = float(origin_result["lat"])
    lon1 = float(origin_result["lon"])
    lat2 = float(dest_result["lat"])
    lon2 = float(dest_result["lon"])

    distance_km = _haversine(lat1, lon1, lat2, lon2)
    bearing_deg = _bearing(lat1, lon1, lat2, lon2)
    direction = _bearing_to_direction(bearing_deg)

    return {
        "origin": {
            "name": origin_result.get("display_name", origin),
            "lat": lat1,
            "lon": lon1,
        },
        "destination": {
            "name": dest_result.get("display_name", destination),
            "lat": lat2,
            "lon": lon2,
        },
        "distance_km": round(distance_km, 2),
        "distance_miles": round(distance_km * 0.621371, 2),
        "bearing_degrees": round(bearing_deg, 1),
        "direction": direction,
        "note": "Luftlinie (Haversine). Tatsaechliche Strecke kann laenger sein.",
    }


async def get_area_stats(place_name: str) -> dict[str, Any]:
    """
    Statistiken ueber einen Ort abrufen (Bevoelkerung, Flaeche, Typ).

    Args:
        place_name: Name des Ortes (z.B. "Berlin", "Tokyo", "New York")

    Returns:
        Bevoelkerung, Flaeche, Verwaltungstyp und weitere Infos
    """
    result = await nominatim_lookup(place_name)
    if not result:
        return {"error": f"Ort '{place_name}' nicht gefunden."}

    address = result.get("address", {})
    extratags = result.get("extratags", {})

    stats: dict[str, Any] = {
        "name": result.get("display_name", place_name),
        "lat": float(result.get("lat", 0)),
        "lon": float(result.get("lon", 0)),
        "type": result.get("type", "unknown"),
        "class": result.get("class", "unknown"),
        "importance": round(float(result.get("importance", 0)), 4),
    }

    # Bounding Box wenn vorhanden
    bbox = result.get("boundingbox")
    if bbox and len(bbox) == 4:
        stats["bounding_box"] = {
            "south": float(bbox[0]),
            "north": float(bbox[1]),
            "west": float(bbox[2]),
            "east": float(bbox[3]),
        }
        # Ungefaehre Flaeche aus Bounding Box berechnen
        height_km = _haversine(float(bbox[0]), float(bbox[2]), float(bbox[1]), float(bbox[2]))
        width_km = _haversine(float(bbox[0]), float(bbox[2]), float(bbox[0]), float(bbox[3]))
        stats["approx_area_km2"] = round(height_km * width_km, 2)

    # Extratags auswerten (Population, Wikipedia, etc.)
    if extratags:
        if "population" in extratags:
            try:
                stats["population"] = int(extratags["population"])
            except (ValueError, TypeError):
                stats["population"] = extratags["population"]
        if "wikipedia" in extratags:
            stats["wikipedia"] = extratags["wikipedia"]
        if "wikidata" in extratags:
            stats["wikidata"] = extratags["wikidata"]
        if "website" in extratags:
            stats["website"] = extratags["website"]
        if "capital" in extratags:
            stats["capital"] = extratags["capital"]
        if "timezone" in extratags:
            stats["timezone"] = extratags["timezone"]

    # Adress-Hierarchie
    if address:
        stats["address"] = {
            k: v for k, v in address.items()
            if k not in ("country_code",)
        }

    return stats


async def find_boundaries(place_name: str) -> dict[str, Any]:
    """
    Administrative Grenzen eines Ortes finden.

    Args:
        place_name: Name des Ortes (z.B. "Bayern", "California", "Paris")

    Returns:
        Verwaltungsgrenzen mit Bounding Box und Hierarchie
    """
    # Nominatim-Suche mit Polygon-Bounding-Box
    results = await nominatim_search(place_name, limit=3)

    if not results:
        return {"error": f"Keine Grenzen fuer '{place_name}' gefunden."}

    # Beste Ergebnisse filtern (bevorzugt administrative Grenzen)
    boundaries = []
    for r in results:
        entry: dict[str, Any] = {
            "name": r.get("display_name", ""),
            "type": r.get("type", "unknown"),
            "class": r.get("class", "unknown"),
            "osm_type": r.get("osm_type", ""),
            "osm_id": r.get("osm_id", ""),
            "lat": float(r.get("lat", 0)),
            "lon": float(r.get("lon", 0)),
        }

        # Bounding Box
        bbox = r.get("boundingbox")
        if bbox and len(bbox) == 4:
            entry["bounding_box"] = {
                "south": float(bbox[0]),
                "north": float(bbox[1]),
                "west": float(bbox[2]),
                "east": float(bbox[3]),
            }

        # Adress-Hierarchie zeigt administrative Ebenen
        address = r.get("address", {})
        if address:
            entry["admin_hierarchy"] = {
                k: v for k, v in address.items()
                if k not in ("country_code",)
            }

        # Extratags fuer weitere Details
        extratags = r.get("extratags", {})
        if extratags:
            admin_level = extratags.get("admin_level") or extratags.get("linked_place")
            if admin_level:
                entry["admin_level"] = admin_level
            if "border_type" in extratags:
                entry["border_type"] = extratags["border_type"]

        boundaries.append(entry)

    return {
        "query": place_name,
        "results_count": len(boundaries),
        "boundaries": boundaries,
    }


async def search_pois(
    query: str,
    lat: float,
    lon: float,
    radius_m: int = 5000,
) -> dict[str, Any]:
    """
    Points of Interest nach Freitext-Keyword in einem Gebiet suchen.

    Args:
        query: Suchbegriff (z.B. "Starbucks", "Museum", "Bahnhof")
        lat: Breitengrad des Mittelpunkts
        lon: Laengengrad des Mittelpunkts
        radius_m: Suchradius in Metern (Standard: 5000, Max: 25000)

    Returns:
        Liste der gefundenen POIs mit Name, Koordinaten und Entfernung
    """
    # Radius begrenzen
    radius_m = min(max(radius_m, 100), 25000)

    try:
        elements = await overpass_search_pois(query, lat, lon, radius_m)
    except Exception as e:
        return {"error": f"POI-Suche fehlgeschlagen: {str(e)}"}

    # Ergebnisse formatieren
    pois = []
    for el in elements:
        formatted = _format_element(el)
        if formatted["lat"] and formatted["lon"]:
            formatted["distance_m"] = round(
                _haversine(lat, lon, formatted["lat"], formatted["lon"]) * 1000
            )
        pois.append(formatted)

    # Nach Entfernung sortieren
    pois.sort(key=lambda x: x.get("distance_m", 99999))

    return {
        "query": query,
        "center": {"lat": lat, "lon": lon},
        "radius_m": radius_m,
        "results_count": len(pois),
        "results": pois[:50],  # Max 50 Ergebnisse
    }
