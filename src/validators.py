"""
validators.py
-------------
Validates all user inputs before processing.
Returns a list of error messages (empty list = all valid).
"""

from datetime import datetime


def validate_name(name: str) -> list:
    errors = []
    if not name or not name.strip():
        errors.append("Name is required")
        return errors

    name = name.strip()
    if len(name) < 2:
        errors.append("Name must be at least 2 characters")
    if len(name) > 100:
        errors.append("Name must be less than 100 characters")

    # Allow letters, spaces, hyphens, apostrophes, dots (for names like O'Brien, J.K., Mary-Jane)
    allowed = lambda c: c.isalpha() or c.isspace() or c in "-'."
    if not all(allowed(c) for c in name):
        errors.append("Name contains invalid characters")

    return errors


def validate_dob(dob: str) -> list:
    """Expect format YYYY-MM-DD"""
    errors = []
    if not dob:
        errors.append("Date of birth is required")
        return errors

    try:
        birth_date = datetime.strptime(dob, "%Y-%m-%d")
    except ValueError:
        errors.append("Date of birth must be in YYYY-MM-DD format")
        return errors

    today = datetime.now()
    if birth_date > today:
        errors.append("Date of birth cannot be in the future")
    if birth_date.year < 1900:
        errors.append("Date of birth must be 1900 or later")

    age_years = (today - birth_date).days / 365.25
    if age_years > 120:
        errors.append("Invalid date of birth (age exceeds 120 years)")

    return errors


def validate_tob(tob: str) -> list:
    """Expect format HH:MM (24-hour)"""
    errors = []
    if not tob:
        errors.append("Time of birth is required")
        return errors

    try:
        t = datetime.strptime(tob, "%H:%M")
        if not (0 <= t.hour <= 23):
            errors.append("Hour must be between 0 and 23")
        if not (0 <= t.minute <= 59):
            errors.append("Minute must be between 0 and 59")
    except ValueError:
        errors.append("Time of birth must be in HH:MM (24-hour) format")

    return errors


def validate_place(place) -> list:
    """Place is optional. If provided, must be a valid string."""
    errors = []
    if place is None or place == "":
        return errors  # optional

    if not isinstance(place, str):
        errors.append("Place must be a text value")
        return errors

    place = place.strip()
    if len(place) < 2:
        errors.append("Place name must be at least 2 characters")
    if len(place) > 100:
        errors.append("Place name must be less than 100 characters")

    return errors


def validate_inputs(name: str, dob: str, tob: str, place: str = None) -> list:
    """Run all validators and return a combined list of errors."""
    errors = []
    errors.extend(validate_name(name))
    errors.extend(validate_dob(dob))
    errors.extend(validate_tob(tob))
    errors.extend(validate_place(place))
    return errors
