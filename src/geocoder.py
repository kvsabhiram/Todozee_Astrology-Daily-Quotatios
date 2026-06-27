"""
geocoder.py
-----------
Resolves a place name to (latitude, longitude, timezone).
Uses a local cache for popular cities, falls back to Nominatim for everything else.
"""

from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

# Popular cities cached locally for speed (no network call needed)
CITY_CACHE = {
    # India
    'mumbai': (19.0760, 72.8777),
    'delhi': (28.7041, 77.1025),
    'bangalore': (12.9716, 77.5946),
    'bengaluru': (12.9716, 77.5946),
    'hyderabad': (17.3850, 78.4867),
    'chennai': (13.0827, 80.2707),
    'kolkata': (22.5726, 88.3639),
    'pune': (18.5204, 73.8567),
    'ahmedabad': (23.0225, 72.5714),
    'jaipur': (26.9124, 75.7873),
    'lucknow': (26.8467, 80.9462),
    'chandigarh': (30.7333, 76.7794),
    'indore': (22.7196, 75.8577),
    'bhopal': (23.2599, 77.4126),
    'nagpur': (21.1458, 79.0882),
    'surat': (21.1702, 72.8311),
    'visakhapatnam': (17.6868, 83.2185),
    'kochi': (9.9312, 76.2673),
    'coimbatore': (11.0168, 76.9558),
    'vadodara': (22.3072, 73.1812),
    'goa': (15.2993, 74.1240),
    'warangal': (17.9689, 79.5941),
    'tirupati': (13.6288, 79.4192),
    'bhubaneswar': (20.2961, 85.8245),

    # USA
    'new york': (40.7128, -74.0060),
    'los angeles': (34.0522, -118.2437),
    'chicago': (41.8781, -87.6298),
    'san francisco': (37.7749, -122.4194),
    'boston': (42.3601, -71.0589),
    'miami': (25.7617, -80.1918),

    # UK / Europe
    'london': (51.5074, -0.1278),
    'paris': (48.8566, 2.3522),
    'berlin': (52.5200, 13.4050),
    'madrid': (40.4168, -3.7038),
    'rome': (41.9028, 12.4964),

    # Asia
    'tokyo': (35.6762, 139.6503),
    'singapore': (1.3521, 103.8198),
    'dubai': (25.2048, 55.2708),
    'bangkok': (13.7563, 100.5018),
}

_tf = TimezoneFinder()
_geolocator = Nominatim(user_agent="astrology_backend_v1")


def get_timezone(lat: float, lon: float) -> str:
    """Return IANA timezone string for given coordinates, e.g. 'Asia/Kolkata'."""
    tz = _tf.timezone_at(lat=lat, lng=lon)
    return tz or "UTC"


def resolve_place(place: str) -> dict:
    """
    Resolve a place name to coordinates + timezone.
    Returns:
        {
            "success": True,
            "latitude": ...,
            "longitude": ...,
            "timezone": "Asia/Kolkata",
            "source": "cache" | "nominatim"
        }
    or
        {"success": False, "error": "..."}
    """
    if not place:
        return {"success": False, "error": "No place provided"}

    key = place.lower().strip()

    # 1. Check local cache first
    if key in CITY_CACHE:
        lat, lon = CITY_CACHE[key]
        return {
            "success": True,
            "latitude": lat,
            "longitude": lon,
            "timezone": get_timezone(lat, lon),
            "source": "cache",
        }

    # 2. Fall back to Nominatim
    try:
        location = _geolocator.geocode(place, timeout=10)
        if location:
            lat = location.latitude
            lon = location.longitude
            return {
                "success": True,
                "latitude": lat,
                "longitude": lon,
                "timezone": get_timezone(lat, lon),
                "source": "nominatim",
                "matched_name": location.address,
            }
    except Exception as e:
        return {"success": False, "error": f"Geocoding error: {e}"}

    return {"success": False, "error": f"Could not find location: {place}"}
