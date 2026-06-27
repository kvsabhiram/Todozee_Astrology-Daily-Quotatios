"""
astrology_engine.py
-------------------
Core astrology calculations using Swiss Ephemeris only.
(Flatlib removed — its pyswisseph dependency conflicts with modern versions.)
Aspects are computed directly from planetary longitudes.

No text interpretations here — only raw chart data.
Text/story generation is handled by the LLM (see llm_client.py).
"""

import swisseph as swe
from datetime import datetime, timedelta
import pytz


ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Personal planets (the 5 we care about for personality/story)
PERSONAL_PLANETS = {
    swe.SUN: "Sun",
    swe.MOON: "Moon",
    swe.MERCURY: "Mercury",
    swe.VENUS: "Venus",
    swe.MARS: "Mars",
}

# Outer planets (used for transits / future predictions)
OUTER_PLANETS = {
    swe.JUPITER: "Jupiter",
    swe.SATURN: "Saturn",
    swe.URANUS: "Uranus",
    swe.NEPTUNE: "Neptune",
    swe.PLUTO: "Pluto",
}

# Major aspects and their target angles (degrees of separation)
ASPECT_TYPES = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Opposition": 180,
}
DEFAULT_ORB = 6.0  # degrees of allowable deviation

# Simple date-range fallback for sun sign (when no place/time given)
SUN_SIGN_DATE_RANGES = [
    ((3, 21), (4, 19), "Aries"),
    ((4, 20), (5, 20), "Taurus"),
    ((5, 21), (6, 20), "Gemini"),
    ((6, 21), (7, 22), "Cancer"),
    ((7, 23), (8, 22), "Leo"),
    ((8, 23), (9, 22), "Virgo"),
    ((9, 23), (10, 22), "Libra"),
    ((10, 23), (11, 21), "Scorpio"),
    ((11, 22), (12, 21), "Sagittarius"),
    ((12, 22), (12, 31), "Capricorn"),
    ((1, 1), (1, 19), "Capricorn"),
    ((1, 20), (2, 18), "Aquarius"),
    ((2, 19), (3, 20), "Pisces"),
]


def get_sun_sign_from_date(month: int, day: int) -> str:
    """Fast fallback: returns sun sign from DOB only, no ephemeris needed."""
    for (sm, sd), (em, ed), sign in SUN_SIGN_DATE_RANGES:
        if (month, day) >= (sm, sd) and (month, day) <= (em, ed):
            return sign
    return "Capricorn"


def zodiac_from_longitude(longitude: float) -> tuple:
    """Convert ecliptic longitude (0-360°) to (sign, degree_within_sign)."""
    longitude = longitude % 360
    sign_idx = int(longitude / 30)
    degree = longitude % 30
    return ZODIAC_SIGNS[sign_idx], degree


def local_to_utc(year, month, day, hour, minute, tz_name):
    """Convert local birth datetime to UTC using the birth-place timezone."""
    tz = pytz.timezone(tz_name)
    local_dt = tz.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.UTC)
    return utc_dt


def julian_day_from_utc(utc_dt: datetime) -> float:
    """Convert a UTC datetime to Julian Day for Swiss Ephemeris."""
    hour_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    return swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_decimal)


def calculate_planets(jd: float, planet_map: dict) -> dict:
    """
    Calculate positions for the given planets at Julian Day `jd`.
    Returns: {planet_name: {"sign": ..., "degree": ..., "longitude": ...}}
    """
    result = {}
    for planet_id, planet_name in planet_map.items():
        position = swe.calc_ut(jd, planet_id)[0]
        longitude = position[0]
        sign, degree = zodiac_from_longitude(longitude)
        result[planet_name] = {
            "sign": sign,
            "degree": round(degree, 2),
            "longitude": round(longitude, 4),
        }
    return result


def calculate_houses_and_angles(jd: float, lat: float, lon: float) -> dict:
    """
    Calculate house cusps + Ascendant + Midheaven using Placidus system.
    Requires birth location (will raise if lat/lon missing).
    """
    houses_data = swe.houses(jd, lat, lon, b"P")
    cusps = houses_data[0]
    ascendant_lon = houses_data[1][0]
    midheaven_lon = houses_data[1][1]

    asc_sign, asc_deg = zodiac_from_longitude(ascendant_lon)
    mc_sign, mc_deg = zodiac_from_longitude(midheaven_lon)

    houses = {}
    for i in range(12):
        sign, deg = zodiac_from_longitude(cusps[i])
        houses[i + 1] = {"sign": sign, "degree": round(deg, 2)}

    return {
        "ascendant": {"sign": asc_sign, "degree": round(asc_deg, 2)},
        "midheaven": {"sign": mc_sign, "degree": round(mc_deg, 2)},
        "houses": houses,
    }


def compute_aspects(all_planets: dict, orb: float = DEFAULT_ORB) -> list:
    """
    Compute major aspects between every pair of planets using their longitudes.
    Pure math — no external library needed.
    Returns list of {planet1, planet2, type, orb_deg}.
    """
    names = list(all_planets.keys())
    aspects = []

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            p1, p2 = names[i], names[j]
            lon1 = all_planets[p1]["longitude"]
            lon2 = all_planets[p2]["longitude"]

            # Angular separation (always 0-180)
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff

            # Check against each aspect type
            for asp_name, target_angle in ASPECT_TYPES.items():
                deviation = abs(diff - target_angle)
                if deviation <= orb:
                    aspects.append({
                        "planet1": p1,
                        "planet2": p2,
                        "type": asp_name,
                        "orb_deg": round(deviation, 2),
                    })
                    break  # one aspect per pair max

    # Sort by tightest orb first, keep top 10
    aspects.sort(key=lambda a: a["orb_deg"])
    return aspects[:10]


def compute_natal_chart(year, month, day, hour, minute, lat=None, lon=None, tz_name=None) -> dict:
    """
    Compute the full natal chart.
    If lat/lon/tz_name are None → returns sun-sign-only data (no houses/ascendant).
    """
    has_location = lat is not None and lon is not None and tz_name is not None

    if has_location:
        utc_dt = local_to_utc(year, month, day, hour, minute, tz_name)
    else:
        # Assume UTC if no location (best effort)
        utc_dt = datetime(year, month, day, hour, minute, tzinfo=pytz.UTC)

    jd = julian_day_from_utc(utc_dt)

    personal = calculate_planets(jd, PERSONAL_PLANETS)
    outer = calculate_planets(jd, OUTER_PLANETS)

    chart = {
        "personal_planets": personal,
        "outer_planets": outer,
        "birth_utc": utc_dt.isoformat(),
        "julian_day": jd,
        "has_location": has_location,
    }

    chart["sun_sign"] = personal["Sun"]["sign"]
    chart["moon_sign"] = personal["Moon"]["sign"]

    if has_location:
        angles = calculate_houses_and_angles(jd, lat, lon)
        chart["ascendant"] = angles["ascendant"]
        chart["midheaven"] = angles["midheaven"]
        chart["houses"] = angles["houses"]

        # Aspects across all planets (Swiss Ephemeris based, no Flatlib)
        combined = {**personal, **outer}
        chart["aspects"] = compute_aspects(combined)
    else:
        chart["ascendant"] = None
        chart["midheaven"] = None
        chart["houses"] = None
        chart["aspects"] = []

    return chart


def compute_current_transits() -> dict:
    """Get today's outer-planet positions (for future predictions)."""
    now_utc = datetime.utcnow()
    jd_now = julian_day_from_utc(now_utc)
    return {
        "date": now_utc.strftime("%Y-%m-%d"),
        "planets": calculate_planets(jd_now, OUTER_PLANETS),
    }