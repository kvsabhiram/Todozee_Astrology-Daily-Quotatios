"""
orchestrator.py
---------------
Ties everything together:
    validate → geocode → compute chart → call Gemma → return report
"""

from datetime import datetime, timedelta

from validators import validate_inputs
from geocoder import resolve_place
from astrology_engine import (
    compute_natal_chart,
    compute_current_transits,
    get_sun_sign_from_date,
)
from prompts import build_story_prompt, build_quote_prompt, build_predictions_prompt
from llm_client import call_gemma


def generate_full_report(name: str, dob: str, tob: str, place: str = None) -> dict:
    """
    Main entry point.
    Inputs:
        name  — full name (str)
        dob   — YYYY-MM-DD
        tob   — HH:MM (24-hour)
        place — city name (optional)
    Returns a dict with success flag, errors (if any), and the full report.
    """

    # 1. Validate inputs
    errors = validate_inputs(name, dob, tob, place)
    if errors:
        return {"success": False, "errors": errors}

    # Parse date/time
    dt = datetime.strptime(f"{dob} {tob}", "%Y-%m-%d %H:%M")
    year, month, day = dt.year, dt.month, dt.day
    hour, minute = dt.hour, dt.minute

    # 2. Resolve place (optional)
    lat, lon, tz_name, place_info = None, None, None, None
    if place:
        place_info = resolve_place(place)
        if place_info.get("success"):
            lat = place_info["latitude"]
            lon = place_info["longitude"]
            tz_name = place_info["timezone"]
        else:
            # Place was given but couldn't be resolved — return error
            return {
                "success": False,
                "errors": [place_info.get("error", "Could not resolve place")],
            }

    # 3. Compute natal chart
    try:
        chart = compute_natal_chart(year, month, day, hour, minute, lat, lon, tz_name)
    except Exception as e:
        return {"success": False, "errors": [f"Chart calculation failed: {e}"]}

    # 4. Current transits (for predictions)
    transits = compute_current_transits()

    # 5. Generate text via Gemma
    today_str = datetime.utcnow().strftime("%Y-%m-%d")
    tomorrow_str = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    sun_sign = chart["sun_sign"]

    try:
        story = call_gemma(build_story_prompt(chart, name), max_tokens=400)
        predictions = call_gemma(build_predictions_prompt(chart, transits), max_tokens=350)
        quote_today = call_gemma(
            build_quote_prompt(sun_sign, today_str, tomorrow=False),
            max_tokens=60,
            temperature=0.8,
        )
    except RuntimeError as e:
        return {"success": False, "errors": [str(e)]}

    # 6. Assemble response
    return {
        "success": True,
        "name": name,
        "zodiac": sun_sign,
        "moon_sign": chart["moon_sign"],
        "ascendant": chart["ascendant"]["sign"] if chart["ascendant"] else None,
        "has_location": chart["has_location"],
        "place_info": place_info if place else None,
        "story": story,
        "predictions": predictions,
        "quote_today": quote_today,
        "date": today_str,
    }


def get_daily_quote(sun_sign: str, tomorrow: bool = False) -> dict:
    """Lightweight endpoint — just generate today's or tomorrow's quote."""
    if sun_sign not in [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]:
        return {"success": False, "errors": ["Invalid zodiac sign"]}

    target_date = datetime.utcnow() + (timedelta(days=1) if tomorrow else timedelta(0))
    date_str = target_date.strftime("%Y-%m-%d")

    try:
        quote = call_gemma(
            build_quote_prompt(sun_sign, date_str, tomorrow=tomorrow),
            max_tokens=60,
            temperature=0.8,
        )
    except RuntimeError as e:
        return {"success": False, "errors": [str(e)]}

    return {
        "success": True,
        "zodiac": sun_sign,
        "date": date_str,
        "quote": quote,
    }


def get_quick_sun_sign(dob: str) -> dict:
    """Ultra-fast endpoint — sun sign from DOB only, no ephemeris, no LLM."""
    try:
        dt = datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        return {"success": False, "errors": ["Date must be YYYY-MM-DD"]}

    sign = get_sun_sign_from_date(dt.month, dt.day)
    return {"success": True, "zodiac": sign}
