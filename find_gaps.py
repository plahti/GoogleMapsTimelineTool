#!/usr/bin/python3

import json
import argparse
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def parse_time(timestamp: str) -> datetime:
    """Yrittää jäsentää aikaleiman. Katkaisee sekunnin osiin asti."""
    try:
        return datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise ValueError(f"Virheellinen aikaleima: {timestamp}")


def extract_time(segment: Dict[str, Any]) -> Optional[str]:
    return segment.get("startTime")


def process_timestamps(timestamps: List[str], label: str, min_gap: timedelta, last_time: Optional[datetime]) -> tuple[int, Optional[datetime], timedelta]:
    """Käy läpi aikaleimat ja etsii niistä aukkoja."""
    gap_count = 0
    total_gap_duration = timedelta(0)
    for t in timestamps:
        try:
            current_time = parse_time(t)
        except ValueError as e:
            print(e)
            continue

        if last_time:
            gap = current_time - last_time
            if gap >= min_gap:
                print(f"Gap detected ({label}): {last_time.strftime('%d.%m.%Y %H:%M')} - {current_time.strftime('%d.%m.%Y %H:%M')}  Gap: {gap}")
                gap_count += 1
                total_gap_duration += gap

        last_time = current_time

    return gap_count, last_time, total_gap_duration


def find_gaps(file_path: str, min_gap_hours: float) -> None:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    min_gap = timedelta(hours=min_gap_hours)
    total_gaps = 0
    total_gap_duration = timedelta(0)
    all_times = []

    last_time: Optional[datetime] = None

    # semanticSegments
    semantic_segments = data.get("semanticSegments", [])
    semantic_segments = sorted(
        (s for s in semantic_segments if extract_time(s)),
        key=lambda s: extract_time(s)
    )
    segment_times = [s["startTime"] for s in semantic_segments]
    gaps, last_time, gap_duration = process_timestamps(segment_times, "semanticSegments", min_gap, last_time)
    total_gaps += gaps
    total_gap_duration += gap_duration
    all_times.extend(segment_times)

    # timelinePath
    for timeline in data.get("timelinePath", []):
        gaps, last_time, gap_duration = process_timestamps(timeline.get("timestamps", []), "timelinePath", min_gap, last_time)
        total_gaps += gaps
        total_gap_duration += gap_duration
        all_times.extend(timeline.get("timestamps", []))

    # Pienin ja suurin aikaväli
    if all_times:
        min_time = parse_time(min(all_times, key=parse_time))
        max_time = parse_time(max(all_times, key=parse_time))
        total_duration = max_time - min_time
        print(f"\nAineiston kokonaispituus: {total_duration.days} päivää")
    
    # Kaikkien aukkojen kokonaishinta
    print(f"\nKaikkien aukkojen yhteenlaskettu kokonaispituus: {total_gap_duration.days} päivää, yhteensä aukkoja löytyi {total_gaps} kpl")


def main():
    parser = argparse.ArgumentParser(description="Etsi aikavälejä, joissa on aukkoja.")
    parser.add_argument("json_file", help="JSON-tiedoston polku")
    parser.add_argument("min_gap_hours", type=float, help="Minimiaukon pituus tunteina")
    args = parser.parse_args()

    try:
        find_gaps(args.json_file, args.min_gap_hours)
    except FileNotFoundError:
        print(f"Tiedostoa ei löytynyt: {args.json_file}")
    except json.JSONDecodeError:
        print("Virhe JSON-tiedoston jäsentämisessä.")
    except Exception as e:
        print(f"Odottamaton virhe: {e}")


if __name__ == "__main__":
    main()

# eof