"""
prompts.py
----------
Prompt templates for Gemma 3 4B-IT.
Keep prompts small, focused, and explicit — small models perform best with clear constraints.
"""


def build_story_prompt(chart: dict, name: str) -> str:
    """Generate the personalized astrology story (3 paragraphs)."""
    p = chart["personal_planets"]
    asc = chart["ascendant"]["sign"] if chart.get("ascendant") else "Unknown"

    return f"""You are a warm, friendly astrologer writing a personalized astrology story.

User details:
- Name: {name}
- Sun sign: {p['Sun']['sign']}
- Moon sign: {p['Moon']['sign']}
- Mercury: {p['Mercury']['sign']}
- Venus: {p['Venus']['sign']}
- Mars: {p['Mars']['sign']}
- Ascendant (Rising): {asc}

Write a warm, personalized astrology story in EXACTLY 3 paragraphs:
1. First paragraph: Core personality based on Sun sign
2. Second paragraph: Emotional nature and values based on Moon and Venus
3. Third paragraph: Life journey, strengths, and challenges

Rules:
- Write in second person ("You are...")
- Warm and encouraging tone
- Maximum 250 words total
- Flowing paragraphs, NO bullet points
- Do NOT mention planet names or astrology jargon
- Start directly with "As a {p['Sun']['sign']}, you..."

Story:"""


def build_quote_prompt(sun_sign: str, date_str: str, tomorrow: bool = False) -> str:
    """Generate a single daily motivational quote tailored to the sun sign."""
    when = "tomorrow" if tomorrow else "today"
    return f"""Generate ONE motivational quote for a {sun_sign} person for {when} ({date_str}).

Rules:
- Maximum 15 words
- Inspiring, positive, actionable
- Should subtly reflect {sun_sign} personality traits
- Do NOT mention astrology, zodiac, or signs in the quote
- Return ONLY the quote text — no quotation marks, no explanation, no prefix

Quote:"""


def build_predictions_prompt(chart: dict, transits: dict) -> str:
    """Generate future predictions across 4 life areas using current transits."""
    p = chart["personal_planets"]
    t = transits["planets"]
    asc = chart["ascendant"]["sign"] if chart.get("ascendant") else "Unknown"

    return f"""You are an astrologer giving life predictions based on current planetary transits.

Person's natal chart:
- Sun: {p['Sun']['sign']}
- Moon: {p['Moon']['sign']}
- Mars: {p['Mars']['sign']}
- Ascendant: {asc}

Current planetary transits ({transits['date']}):
- Jupiter is now in: {t['Jupiter']['sign']}
- Saturn is now in: {t['Saturn']['sign']}

Write predictions in EXACTLY this format with these 4 sections:

CAREER: [2-3 sentence prediction]
LOVE: [2-3 sentence prediction]
FINANCES: [2-3 sentence prediction]
HEALTH: [2-3 sentence prediction]

Rules:
- Be specific and actionable, not generic
- Encouraging tone, even for challenges
- No astrology jargon (no "Jupiter", "Saturn", "house", etc.)
- Each section maximum 40 words
- Output only the 4 sections, nothing else

Predictions:"""
