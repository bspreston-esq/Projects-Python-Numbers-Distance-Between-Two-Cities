#!/usr/bin/env python3
"""Great-circle distance between two cities, in the unit you choose."""
import argparse
import json
import math
import urllib.parse
import urllib.request

EARTH_RADIUS_KM = 6371.0088
UNITS = {"km": 1.0, "mi": 1.609344, "nmi": 1.852}

# A small offline gazetteer; extend it or use --geocode for anything else.
CITIES = {
    "new york": (40.7128, -74.0060), "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298), "houston": (29.7604, -95.3698),
    "toronto": (43.6532, -79.3832), "vancouver": (49.2827, -123.1207),
    "mexico city": (19.4326, -99.1332), "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522), "berlin": (52.5200, 13.4050),
    "madrid": (40.4168, -3.7038), "rome": (41.9028, 12.4964),
    "amsterdam": (52.3676, 4.9041), "dublin": (53.3498, -6.2603),
    "moscow": (55.7558, 37.6173), "istanbul": (41.0082, 28.9784),
    "cairo": (30.0444, 31.2357), "lagos": (6.5244, 3.3792),
    "nairobi": (-1.2921, 36.8219), "cape town": (-33.9249, 18.4241),
    "dubai": (25.2048, 55.2708), "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090), "singapore": (1.3521, 103.8198),
    "hong kong": (22.3193, 114.1694), "tokyo": (35.6762, 139.6503),
    "seoul": (37.5665, 126.9780), "beijing": (39.9042, 116.4074),
    "sydney": (-33.8688, 151.2093), "melbourne": (-37.8136, 144.9631),
    "auckland": (-36.8509, 174.7645), "sao paulo": (-23.5505, -46.6333),
    "buenos aires": (-34.6037, -58.3816), "lima": (-12.0464, -77.0428),
    "bogota": (4.7110, -74.0721), "honolulu": (21.3069, -157.8583),
}

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))

def geocode(city: str):
    """Look a city up through OpenStreetMap Nominatim (requires network)."""
    query = urllib.parse.urlencode({"q": city, "format": "json", "limit": 1})
    request = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{query}",
        headers={"User-Agent": "distance-between-two-cities/1.0"})
    with urllib.request.urlopen(request, timeout=10) as response:
        data = json.load(response)
    if not data:
        raise ValueError(f"could not geocode '{city}'")
    return float(data[0]["lat"]), float(data[0]["lon"])

def coordinates(city: str, allow_network: bool):
    key = city.strip().lower()
    if key in CITIES:
        return CITIES[key]
    if allow_network:
        return geocode(city)
    raise ValueError(f"'{city}' is not in the offline gazetteer; pass --geocode to look it up online")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from", dest="origin")
    parser.add_argument("--to", dest="destination")
    parser.add_argument("--unit", choices=sorted(UNITS), default="km")
    parser.add_argument("--geocode", action="store_true", help="allow online lookup for unknown cities")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo:
        for a, b in (("new york", "london"), ("tokyo", "sydney"), ("paris", "berlin")):
            (lat1, lon1), (lat2, lon2) = CITIES[a], CITIES[b]
            km = haversine(lat1, lon1, lat2, lon2)
            print(f"{a.title()} -> {b.title()}: {km:,.0f} km / {km/UNITS['mi']:,.0f} mi")
        return

    origin = args.origin or input("From city: ").strip()
    destination = args.destination or input("To city: ").strip()
    try:
        (lat1, lon1) = coordinates(origin, args.geocode)
        (lat2, lon2) = coordinates(destination, args.geocode)
        km = haversine(lat1, lon1, lat2, lon2)
        print(f"{origin.title()} -> {destination.title()}: {km / UNITS[args.unit]:,.1f} {args.unit}")
    except (ValueError, OSError) as exc:
        print(f"Error: {exc}")

if __name__ == "__main__":
    main()
