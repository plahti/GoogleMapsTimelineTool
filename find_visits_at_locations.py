#!/usr/bin/python3

import json
import sys
from datetime import datetime, timedelta
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from functools import lru_cache


def parse_time(timestamp):
    """Parse ISO8601 timestamp (up to seconds) into a datetime object."""
    return datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")


def is_within_radius(lat1, lon1, lat2, lon2, max_distance):
    """Return True if the two coordinates are within max_distance meters."""
    return geodesic((lat1, lon1), (lat2, lon2)).meters <= max_distance


def format_duration(duration):
    """Format a timedelta duration as 'd h m' string."""
    days, remainder = divmod(duration.days, 1)
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = remainder // 60
    return f"{days:2} d {hours:2} h {minutes:02} m"


def get_weekday_short(date):
    """Return short Finnish weekday name for a datetime object."""
    weekdays = ['ma', 'ti', 'ke', 'to', 'pe', 'la', 'su']
    return weekdays[date.weekday()]


def get_language_from_country_code(country_code):
    """Map country code to primary language code, or return the input if not found."""
    country_to_language = {
        'fi': 'fi',
        'se': 'sv',
        'no': 'nb',
        'dk': 'da',
        'de': 'de',
        'fr': 'fr',
        'ru': 'ru',
        'us': 'en',
        'gb': 'en',
    }
    return country_to_language.get(country_code.lower(), country_code)

  # Välimuisti geolokaatiokutsuille


@lru_cache(maxsize=100)  # Välimuisti geolokaatiokutsuille
def get_language(lat, lon):
    """Guess the primary local language based on coordinates using reverse geocoding."""
    geolocator = Nominatim(user_agent="language_checker")
    location = geolocator.reverse((lat, lon), language='en', timeout=10)

    if location:
        address = location.raw.get('address', {})
        country = address.get('country', '')

        # Tarkistetaan, onko maata löytynyt ja palautetaan kieli
        if country:
            # Nominatim palauttaa kielen 'address' osassa, jos se on saatavilla
            country = address.get('country_code', 'Unknown')
            language = get_language_from_country_code(country)
            return language

    return "Unknown"


@lru_cache(maxsize=100)  # Välimuisti geolokaatiokutsuille
def get_address(lat, lon):
    """Reverse geocode coordinates to a human-readable address, preferring local language."""
    geolocator = Nominatim(user_agent="visit_locator")
    lang = get_language(lat, lon)
    languages = [lang, 'en']

    for lang in languages:
        try:
            location = geolocator.reverse(
                (lat, lon), language=lang, timeout=10)
            if location:
                address = location.raw.get('address', {})
                street = address.get('road', 'Unknown street')
                house_number = address.get('house_number', 'N/A')
                city = address.get('city', address.get('town', 'Unknown city'))
                neighborhood = address.get(
                    'neighborhood', 'Unknown neighborhood')

                # Palautetaan löydetty osoite
                address_parts = []

                if street != 'Unknown street':
                    address_parts.append(
                        f"{street} {house_number}" if house_number != 'N/A' else street)

                if neighborhood != 'Unknown neighborhood':
                    address_parts.append(neighborhood)

                if city != 'Unknown city':
                    address_parts.append(city)

                if not address_parts:
                    island = address.get('island', 'Unknown island')
                    if island != 'Unknown island':
                        return f"{island}"
                    return ""

                return ", ".join(address_parts)
        except GeocoderTimedOut:
            continue  # Jos palvelu ei vastaa, kokeillaan seuraavaa kieltä

    # Jos ei löytynyt mitään kaikilla kielillä, palautetaan ""
    return ""


def process_visits(file_path, ref_lat, ref_lon, max_distance):
    """Parse semanticSegments from JSON file and print visits within a radius."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    semantic_segments = data.get("semanticSegments", [])
    visits = []

    for segment in semantic_segments:
        start_time = parse_time(segment["startTime"])
        end_time = parse_time(segment["endTime"])
        duration = end_time - start_time

        if duration < timedelta(minutes=5):
            continue  # Skip short visits

        if "visit" in segment:
            place = segment["visit"]["topCandidate"]["placeLocation"]["latLng"]
            lat, lon = map(float, place.replace("°", "").split(", "))

            if not is_within_radius(ref_lat, ref_lon, lat, lon, max_distance):
                continue

            if visits and (start_time - visits[-1][1]) <= timedelta(hours=24):
                # Yhdistetään käynnit
                visits[-1] = (visits[-1][0], end_time,
                              visits[-1][2] + [(lat, lon)])
            else:
                visits.append((start_time, end_time, [(lat, lon)]))

    for start_time, end_time, coords in visits:
        avg_lat = sum(lat for lat, lon in coords) / len(coords)
        avg_lon = sum(lon for lat, lon in coords) / len(coords)
        address = get_address(avg_lat, avg_lon)

        formatted_start = f"{get_weekday_short(start_time)} {start_time.strftime('%d.%m.%Y %H:%M')}"
        formatted_end = f"{get_weekday_short(end_time)} {end_time.strftime('%d.%m.%Y %H:%M')}"

        duration = end_time - start_time
        print(
            f"{formatted_start} - {formatted_end}  {format_duration(duration)}  {address}")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python3 find_visits_at_locations.py <data.json> <latitude> <longitude> <distance>")
        sys.exit(1)

    json_file = sys.argv[1]
    latitude = float(sys.argv[2])
    longitude = float(sys.argv[3])
    distance = float(sys.argv[4])

    process_visits(json_file, latitude, longitude, distance)

# eof
