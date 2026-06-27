#!/usr/bin/env python3
"""
Advanced Astrology Predictor using Swiss Ephemeris and Flatlib
Provides accurate astronomical calculations and detailed astrological predictions

Installation required:
pip install pyswisseph flatlib
"""

import swisseph as swe
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib import const
from datetime import datetime

class AdvancedAstrologyPredictor:
    def __init__(self):
        # Set ephemeris path (optional - uses default if not set)
        # swe.set_ephe_path('/path/to/ephemeris/files')
        
        # City coordinates database
        self.city_coordinates = {
            # India
            'mumbai': (19.0760, 72.8777),
            'delhi': (28.7041, 77.1025),
            'bangalore': (12.9716, 77.5946),
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
            
            # USA
            'new york': (40.7128, -74.0060),
            'los angeles': (34.0522, -118.2437),
            'chicago': (41.8781, -87.6298),
            'houston': (29.7604, -95.3698),
            'phoenix': (33.4484, -112.0740),
            'philadelphia': (39.9526, -75.1652),
            'san francisco': (37.7749, -122.4194),
            'seattle': (47.6062, -122.3321),
            'miami': (25.7617, -80.1918),
            'boston': (42.3601, -71.0589),
            'washington dc': (38.9072, -77.0369),
            'atlanta': (33.7490, -84.3880),
            'dallas': (32.7767, -96.7970),
            'las vegas': (36.1699, -115.1398),
            
            # UK
            'london': (51.5074, -0.1278),
            'manchester': (53.4808, -2.2426),
            'birmingham': (52.4862, -1.8904),
            'liverpool': (53.4084, -2.9916),
            'edinburgh': (55.9533, -3.1883),
            'glasgow': (55.8642, -4.2518),
            
            # Europe
            'paris': (48.8566, 2.3522),
            'berlin': (52.5200, 13.4050),
            'madrid': (40.4168, -3.7038),
            'rome': (41.9028, 12.4964),
            'amsterdam': (52.3676, 4.9041),
            'brussels': (50.8503, 4.3517),
            'vienna': (48.2082, 16.3738),
            'zurich': (47.3769, 8.5417),
            'barcelona': (41.3851, 2.1734),
            'milan': (45.4642, 9.1900),
            'athens': (37.9838, 23.7275),
            'lisbon': (38.7223, -9.1393),
            
            # Asia
            'tokyo': (35.6762, 139.6503),
            'beijing': (39.9042, 116.4074),
            'shanghai': (31.2304, 121.4737),
            'seoul': (37.5665, 126.9780),
            'bangkok': (13.7563, 100.5018),
            'singapore': (1.3521, 103.8198),
            'hong kong': (22.3193, 114.1694),
            'dubai': (25.2048, 55.2708),
            'kuala lumpur': (3.1390, 101.6869),
            'jakarta': (6.2088, 106.8456),
            'manila': (14.5995, 120.9842),
            'taipei': (25.0330, 121.5654),
            'istanbul': (41.0082, 28.9784),
            'riyadh': (24.7136, 46.6753),
            'tehran': (35.6892, 51.3890),
            'karachi': (24.8607, 67.0011),
            'dhaka': (23.8103, 90.4125),
            'kabul': (34.5553, 69.2075),
            'colombo': (6.9271, 79.8612),
            
            # Australia & NZ
            'sydney': (-33.8688, 151.2093),
            'melbourne': (-37.8136, 144.9631),
            'brisbane': (-27.4698, 153.0251),
            'perth': (-31.9505, 115.8605),
            'auckland': (-36.8485, 174.7633),
            'wellington': (-41.2865, 174.7762),
            
            # Middle East
            'jerusalem': (31.7683, 35.2137),
            'tel aviv': (32.0853, 34.7818),
            'cairo': (30.0444, 31.2357),
            'doha': (25.2854, 51.5310),
            'abu dhabi': (24.4539, 54.3773),
            'muscat': (23.5880, 58.3829),
            'baghdad': (33.3152, 44.3661),
            
            # Africa
            'johannesburg': (-26.2041, 28.0473),
            'cape town': (-33.9249, 18.4241),
            'nairobi': (-1.2864, 36.8172),
            'lagos': (6.5244, 3.3792),
            'accra': (5.6037, -0.1870),
            'casablanca': (33.5731, -7.5898),
            
            # South America
            'sao paulo': (-23.5505, -46.6333),
            'rio de janeiro': (-22.9068, -43.1729),
            'buenos aires': (-34.6037, -58.3816),
            'lima': (-12.0464, -77.0428),
            'bogota': (4.7110, -74.0721),
            'santiago': (-33.4489, -70.6693),
            'caracas': (10.4806, -66.9036),
            
            # Canada
            'toronto': (43.6532, -79.3832),
            'vancouver': (49.2827, -123.1207),
            'montreal': (45.5017, -73.5673),
            'calgary': (51.0447, -114.0719),
            'ottawa': (45.4215, -75.6972),
        }
        
        self.planet_names = {
            swe.SUN: 'Sun',
            swe.MOON: 'Moon',
            swe.MERCURY: 'Mercury',
            swe.VENUS: 'Venus',
            swe.MARS: 'Mars',
            swe.JUPITER: 'Jupiter',
            swe.SATURN: 'Saturn',
            swe.URANUS: 'Uranus',
            swe.NEPTUNE: 'Neptune',
            swe.PLUTO: 'Pluto'
        }
        
        self.zodiac_signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        self.house_meanings = {
            1: "Self, Identity, Physical Appearance, Life Approach",
            2: "Money, Possessions, Values, Self-Worth",
            3: "Communication, Siblings, Short Trips, Learning",
            4: "Home, Family, Roots, Inner Foundation",
            5: "Creativity, Romance, Children, Self-Expression",
            6: "Health, Work, Daily Routines, Service",
            7: "Partnerships, Marriage, One-on-One Relationships",
            8: "Transformation, Shared Resources, Intimacy, Death/Rebirth",
            9: "Higher Learning, Travel, Philosophy, Expansion",
            10: "Career, Public Image, Ambitions, Authority",
            11: "Friends, Groups, Hopes, Humanitarian Causes",
            12: "Spirituality, Subconscious, Karma, Hidden Matters"
        }
        
        self.planet_meanings = {
            'Sun': "Core identity, ego, vitality, life purpose",
            'Moon': "Emotions, instincts, subconscious, nurturing",
            'Mercury': "Communication, thinking, logic, mental processes",
            'Venus': "Love, beauty, values, relationships, pleasure",
            'Mars': "Action, energy, desire, assertion, courage",
            'Jupiter': "Growth, expansion, luck, wisdom, optimism",
            'Saturn': "Discipline, responsibility, limitations, structure",
            'Uranus': "Innovation, rebellion, sudden changes, uniqueness",
            'Neptune': "Dreams, spirituality, illusion, compassion",
            'Pluto': "Transformation, power, regeneration, deep change"
        }

    def get_city_coordinates(self, city_name):
        """Get coordinates for a city name"""
        city_lower = city_name.lower().strip()
        if city_lower in self.city_coordinates:
            return self.city_coordinates[city_lower]
        return None

    def get_julian_day(self, year, month, day, hour, minute):
        """Convert date and time to Julian Day"""
        time = hour + minute / 60.0
        return swe.julday(year, month, day, time)

    def get_zodiac_sign(self, longitude):
        """Convert ecliptic longitude to zodiac sign"""
        sign_num = int(longitude / 30)
        degree = longitude % 30
        return self.zodiac_signs[sign_num], degree

    def calculate_planets_swiss(self, jd):
        """Calculate planetary positions using Swiss Ephemeris"""
        planets = {}
        
        for planet_id, planet_name in self.planet_names.items():
            # Calculate position (returns longitude, latitude, distance, speed in long, speed in lat, speed in dist)
            position = swe.calc_ut(jd, planet_id)[0]
            longitude = position[0]
            
            sign, degree = self.get_zodiac_sign(longitude)
            
            planets[planet_name] = {
                'longitude': longitude,
                'sign': sign,
                'degree': degree,
                'position': f"{int(degree)}°{int((degree % 1) * 60)}' {sign}"
            }
        
        return planets

    def calculate_houses_swiss(self, jd, lat, lon):
        """Calculate house cusps using Swiss Ephemeris"""
        # Using Placidus house system (most common)
        houses_data = swe.houses(jd, lat, lon, b'P')
        house_cusps = houses_data[0]
        ascendant = houses_data[1][0]  # Ascendant
        mc = houses_data[1][1]  # Midheaven
        
        houses = {}
        for i in range(12):
            sign, degree = self.get_zodiac_sign(house_cusps[i])
            houses[i+1] = {
                'cusp': house_cusps[i],
                'sign': sign,
                'degree': degree,
                'meaning': self.house_meanings[i+1]
            }
        
        asc_sign, asc_degree = self.get_zodiac_sign(ascendant)
        mc_sign, mc_degree = self.get_zodiac_sign(mc)
        
        return houses, {
            'ascendant': ascendant,
            'asc_sign': asc_sign,
            'asc_degree': asc_degree,
            'midheaven': mc,
            'mc_sign': mc_sign,
            'mc_degree': mc_degree
        }

    def create_flatlib_chart(self, year, month, day, hour, minute, lat, lon):
        """Create birth chart using Flatlib"""
        try:
            # Create datetime object
            date = Datetime(f'{year}/{month}/{day}', f'{hour}:{minute}', '+00:00')
            
            # Create geographic position
            pos = GeoPos(lat, lon)
            
            # Create chart
            chart = Chart(date, pos)
            
            return chart
        except Exception as e:
            print(f"Error creating Flatlib chart: {e}")
            return None

    def analyze_flatlib_chart(self, chart):
        """Analyze chart using Flatlib"""
        if not chart:
            return None
        
        analysis = {
            'sun': None,
            'moon': None,
            'ascendant': None,
            'aspects': []
        }
        
        try:
            # Get Sun
            sun = chart.get(const.SUN)
            analysis['sun'] = {
                'sign': sun.sign,
                'house': sun.house,
                'longitude': sun.lon
            }
            
            # Get Moon
            moon = chart.get(const.MOON)
            analysis['moon'] = {
                'sign': moon.sign,
                'house': moon.house,
                'longitude': moon.lon
            }
            
            # Get Ascendant
            asc = chart.get(const.ASC)
            analysis['ascendant'] = {
                'sign': asc.sign,
                'longitude': asc.lon
            }
            
            # Get aspects
            sun_aspects = chart.aspects(const.SUN)
            for aspect in sun_aspects:
                analysis['aspects'].append({
                    'planet1': 'Sun',
                    'planet2': aspect.id2,
                    'type': aspect.type,
                    'orb': aspect.orb
                })
        
        except Exception as e:
            print(f"Error analyzing chart: {e}")
        
        return analysis

    def get_personality_prediction(self, sun_sign, moon_sign, asc_sign):
        """Generate personality insights"""
        predictions = f"""
PERSONALITY PROFILE:

☀️ SUN IN {sun_sign.upper()}:
   Your core essence and life purpose. This is who you are at your deepest level.
   The Sun represents your conscious self, vitality, and creative power.

🌙 MOON IN {moon_sign.upper()}:
   Your emotional nature and subconscious patterns. How you instinctively react.
   The Moon governs your feelings, needs, and what makes you feel secure.

⬆️ ASCENDANT IN {asc_sign.upper()}:
   Your outer personality and how others perceive you initially.
   The Rising sign shapes your approach to life and physical appearance.
"""
        return predictions

    def get_planetary_predictions(self, planets):
        """Generate predictions based on planetary positions"""
        predictions = "\nPLANETARY INFLUENCES:\n"
        
        for planet, data in planets.items():
            sign = data['sign']
            predictions += f"\n{planet} in {sign}:\n"
            predictions += f"   Position: {data['position']}\n"
            predictions += f"   Influence: {self.planet_meanings.get(planet, 'Cosmic influence')}\n"
            
            # Add specific interpretations
            if planet == 'Sun':
                predictions += self.get_sun_interpretation(sign)
            elif planet == 'Moon':
                predictions += self.get_moon_interpretation(sign)
            elif planet == 'Mercury':
                predictions += self.get_mercury_interpretation(sign)
            elif planet == 'Venus':
                predictions += self.get_venus_interpretation(sign)
            elif planet == 'Mars':
                predictions += self.get_mars_interpretation(sign)
        
        return predictions

    def get_sun_interpretation(self, sign):
        interpretations = {
            'Aries': "   Bold, pioneering spirit. Natural leader with courage and initiative.\n",
            'Taurus': "   Stable, practical nature. Values security and sensual pleasures.\n",
            'Gemini': "   Versatile communicator. Quick-witted and intellectually curious.\n",
            'Cancer': "   Nurturing and intuitive. Deep emotional sensitivity and loyalty.\n",
            'Leo': "   Creative and generous. Natural magnetism and leadership ability.\n",
            'Virgo': "   Analytical and helpful. Attention to detail and service-oriented.\n",
            'Libra': "   Diplomatic and balanced. Seeks harmony in relationships.\n",
            'Scorpio': "   Intense and transformative. Deep investigative nature.\n",
            'Sagittarius': "   Optimistic and adventurous. Seeks truth and expansion.\n",
            'Capricorn': "   Ambitious and disciplined. Strong sense of responsibility.\n",
            'Aquarius': "   Innovative and humanitarian. Independent thinker.\n",
            'Pisces': "   Compassionate and imaginative. Deeply spiritual nature.\n"
        }
        return interpretations.get(sign, "")

    def get_moon_interpretation(self, sign):
        interpretations = {
            'Aries': "   Emotional reactions are quick and direct. Need for independence.\n",
            'Taurus': "   Emotional security through stability. Sensual comfort seeking.\n",
            'Gemini': "   Emotional expression through communication. Variety needed.\n",
            'Cancer': "   Deeply nurturing emotions. Strong intuitive feelings.\n",
            'Leo': "   Warm, generous emotions. Need for appreciation and recognition.\n",
            'Virgo': "   Practical emotional responses. Helpful and analytical feelings.\n",
            'Libra': "   Emotional balance and harmony important. Partnership-oriented.\n",
            'Scorpio': "   Intense, deep emotions. Transformative emotional experiences.\n",
            'Sagittarius': "   Optimistic emotional nature. Freedom in feelings important.\n",
            'Capricorn': "   Controlled emotions. Security through achievement.\n",
            'Aquarius': "   Detached yet humanitarian feelings. Independent emotions.\n",
            'Pisces': "   Highly empathetic and compassionate. Spiritual emotional nature.\n"
        }
        return interpretations.get(sign, "")

    def get_mercury_interpretation(self, sign):
        interpretations = {
            'Aries': "   Quick, direct thinking. Impulsive communication style.\n",
            'Taurus': "   Practical, deliberate thinking. Steady communication.\n",
            'Gemini': "   Versatile mind. Excellent communication and wit.\n",
            'Cancer': "   Intuitive thinking. Emotional communication style.\n",
            'Leo': "   Creative, confident thinking. Dramatic expression.\n",
            'Virgo': "   Analytical mind. Precise, detailed communication.\n",
            'Libra': "   Balanced thinking. Diplomatic communication.\n",
            'Scorpio': "   Deep, investigative mind. Intense communication.\n",
            'Sagittarius': "   Philosophical thinking. Honest, direct communication.\n",
            'Capricorn': "   Structured thinking. Serious, authoritative communication.\n",
            'Aquarius': "   Original thinking. Innovative communication.\n",
            'Pisces': "   Imaginative mind. Artistic, intuitive communication.\n"
        }
        return interpretations.get(sign, "")

    def get_venus_interpretation(self, sign):
        interpretations = {
            'Aries': "   Passionate, direct in love. Enjoys the chase.\n",
            'Taurus': "   Sensual, loyal in love. Values stability and comfort.\n",
            'Gemini': "   Mental connection important. Variety in relationships.\n",
            'Cancer': "   Nurturing, emotional in love. Family-oriented values.\n",
            'Leo': "   Romantic, generous in love. Enjoys grand gestures.\n",
            'Virgo': "   Practical expression of love. Service-oriented affection.\n",
            'Libra': "   Harmonious relationships. Values partnership and balance.\n",
            'Scorpio': "   Intense, passionate love. Deep emotional bonds.\n",
            'Sagittarius': "   Freedom in relationships. Adventurous love style.\n",
            'Capricorn': "   Serious approach to love. Traditional values.\n",
            'Aquarius': "   Unconventional relationships. Friendship-based love.\n",
            'Pisces': "   Romantic, compassionate love. Spiritual connections.\n"
        }
        return interpretations.get(sign, "")

    def get_mars_interpretation(self, sign):
        interpretations = {
            'Aries': "   Direct, assertive action. Quick to anger, quick to forgive.\n",
            'Taurus': "   Steady, persistent action. Patient but stubborn when provoked.\n",
            'Gemini': "   Mental action. Energy scattered across multiple interests.\n",
            'Cancer': "   Protective action. Indirect approach to conflict.\n",
            'Leo': "   Confident, dramatic action. Pride drives ambition.\n",
            'Virgo': "   Precise, efficient action. Practical application of energy.\n",
            'Libra': "   Diplomatic action. Avoids direct confrontation.\n",
            'Scorpio': "   Intense, focused action. Strategic and powerful.\n",
            'Sagittarius': "   Enthusiastic action. Direct and philosophical approach.\n",
            'Capricorn': "   Disciplined action. Ambitious and goal-oriented.\n",
            'Aquarius': "   Innovative action. Fights for humanitarian causes.\n",
            'Pisces': "   Intuitive action. Spiritual motivation for action.\n"
        }
        return interpretations.get(sign, "")

    def get_house_predictions(self, houses):
        """Generate predictions based on house placements"""
        predictions = "\nHOUSE SYSTEM ANALYSIS:\n"
        
        for house_num, house_data in houses.items():
            predictions += f"\n{house_num}th House in {house_data['sign']}:\n"
            predictions += f"   {house_data['meaning']}\n"
            predictions += f"   This area of life is influenced by {house_data['sign']} energy.\n"
        
        return predictions

    def get_future_predictions(self, planets, houses):
        """Generate future predictions based on current transits and natal chart"""
        predictions = """
FUTURE PREDICTIONS:

📅 UPCOMING INFLUENCES:

CAREER & SUCCESS:
   Your professional path is guided by your 10th house and planetary positions.
   Jupiter's position indicates areas of growth and expansion.
   Saturn shows where discipline and hard work will pay off.

💕 LOVE & RELATIONSHIPS:
   Venus and your 7th house reveal relationship patterns.
   Current and upcoming aspects suggest romantic opportunities.
   Your Moon sign shows emotional needs in partnerships.

💰 FINANCES:
   2nd and 8th houses govern wealth and shared resources.
   Jupiter aspects can bring financial opportunities.
   Saturn aspects require careful financial planning.

🏥 HEALTH & WELLNESS:
   6th house and Mars position indicate health matters.
   Maintain balance in the areas ruled by your signs.
   Pay attention to body parts associated with your Sun sign.

🌟 SPIRITUAL GROWTH:
   9th and 12th houses show spiritual development.
   Neptune and Pluto aspects indicate deep transformation.
   Your higher purpose is revealed through your chart.
"""
        return predictions

    def display_complete_reading(self, planets, houses, angles, flatlib_analysis):
        """Display complete astrological reading"""
        print("\n" + "="*80)
        print("✨ YOUR COMPLETE ASTROLOGICAL BIRTH CHART ✨".center(80))
        print("="*80)
        
        # Display angles (Ascendant, MC)
        print(f"\n🎯 CHART ANGLES:")
        print(f"   Ascendant (Rising Sign): {int(angles['asc_degree'])}° {angles['asc_sign']}")
        print(f"   Midheaven (MC): {int(angles['mc_degree'])}° {angles['mc_sign']}")
        
        # Display personality profile
        print(self.get_personality_prediction(
            planets['Sun']['sign'],
            planets['Moon']['sign'],
            angles['asc_sign']
        ))
        
        # Display planetary positions and predictions
        print(self.get_planetary_predictions(planets))
        
        # Display house information
        print(self.get_house_predictions(houses))
        
        # Display Flatlib analysis if available
        if flatlib_analysis:
            print("\n🔮 FLATLIB ANALYSIS:")
            if flatlib_analysis.get('aspects'):
                print("\n   MAJOR ASPECTS:")
                for aspect in flatlib_analysis['aspects'][:5]:  # Show first 5 aspects
                    print(f"   {aspect['planet1']} {aspect['type']} {aspect['planet2']}")
        
        # Display future predictions
        print(self.get_future_predictions(planets, houses))
        
        print("\n" + "="*80)
        print("✨ Remember: Astrology guides, but you create your destiny! ✨".center(80))
        print("="*80 + "\n")


def get_birth_information():
    """Collect detailed birth information from user"""
    print("="*80)
    print("🌟 ADVANCED ASTROLOGY READING WITH SWISS EPHEMERIS & FLATLIB 🌟".center(80))
    print("="*80)
    print("\nFor accurate calculations, I need your complete birth information.\n")
    
    predictor = AdvancedAstrologyPredictor()
    
    while True:
        try:
            # Birth date
            print("📅 BIRTH DATE:")
            year = int(input("   Year (e.g., 1990): "))
            month = int(input("   Month (1-12): "))
            day = int(input("   Day (1-31): "))
            
            # Birth time
            print("\n🕐 BIRTH TIME (24-hour format):")
            hour = int(input("   Hour (0-23): "))
            minute = int(input("   Minute (0-59): "))
            
            # Birth location
            print("\n🌍 BIRTH LOCATION:")
            print("   You can enter either:")
            print("   1. City name (e.g., 'Pune', 'Mumbai', 'New York')")
            print("   2. Coordinates (Latitude and Longitude)")
            
            location_input = input("\n   Enter city name or 'coordinates': ").strip()
            
            if location_input.lower() == 'coordinates':
                latitude = float(input("   Latitude (e.g., 18.5204 for Pune): "))
                longitude = float(input("   Longitude (e.g., 73.8567 for Pune): "))
            else:
                # Try to find city
                coords = predictor.get_city_coordinates(location_input)
                if coords:
                    latitude, longitude = coords
                    print(f"   ✅ Found {location_input.title()}: {latitude}, {longitude}")
                else:
                    print(f"   ❌ City '{location_input}' not found in database.")
                    print("   Available cities include: Mumbai, Delhi, Pune, Bangalore, London, Paris, New York, etc.")
                    print("   Please enter coordinates manually:")
                    latitude = float(input("   Latitude: "))
                    longitude = float(input("   Longitude: "))
            
            # Validate
            datetime(year, month, day, hour, minute)
            
            if -90 <= latitude <= 90 and -180 <= longitude <= 180:
                return year, month, day, hour, minute, latitude, longitude
            else:
                print("❌ Invalid coordinates! Latitude: -90 to 90, Longitude: -180 to 180")
        
        except ValueError as e:
            print(f"❌ Invalid input: {e}. Please try again.")


def main():
    """Main function"""
    # Get birth information
    year, month, day, hour, minute, lat, lon = get_birth_information()
    
    print("\n⏳ Calculating your celestial blueprint using Swiss Ephemeris...\n")
    
    # Initialize predictor
    predictor = AdvancedAstrologyPredictor()
    
    # Calculate using Swiss Ephemeris
    jd = predictor.get_julian_day(year, month, day, hour, minute)
    planets = predictor.calculate_planets_swiss(jd)
    houses, angles = predictor.calculate_houses_swiss(jd, lat, lon)
    
    # Create Flatlib chart
    print("⏳ Creating advanced chart analysis with Flatlib...\n")
    flatlib_chart = predictor.create_flatlib_chart(year, month, day, hour, minute, lat, lon)
    flatlib_analysis = predictor.analyze_flatlib_chart(flatlib_chart)
    
    # Display complete reading
    predictor.display_complete_reading(planets, houses, angles, flatlib_analysis)
    
    # Save chart data option
    save = input("Would you like to save your birth chart data? (yes/no): ").lower()
    if save == 'yes':
        filename = f"birth_chart_{year}_{month}_{day}.txt"
        with open(filename, 'w') as f:
            f.write(f"Birth Chart for {month}/{day}/{year} at {hour}:{minute}\n")
            f.write(f"Location: {lat}, {lon}\n\n")
            f.write(f"Planets:\n")
            for planet, data in planets.items():
                f.write(f"{planet}: {data['position']}\n")
            f.write(f"\nAscendant: {angles['asc_sign']}\n")
            f.write(f"Midheaven: {angles['mc_sign']}\n")
        print(f"\n✅ Chart saved to {filename}")


if __name__ == "__main__":
    main()