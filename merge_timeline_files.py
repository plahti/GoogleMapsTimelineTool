#!/usr/bin/python3

import json
import sys
import os
import argparse
import logging

# Lokitusasetukset
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_time(json_obj):
    try:
        return json_obj['startTime']
    except KeyError:
        logging.warning("Missing 'startTime' in one of the entries.")
        return None

def merge_json_files(files):
    all_semantic_segments = []
    for filename in files:
        if not os.path.isfile(filename):
            logging.error(f"File not found: {filename}")
            continue

        logging.info(f"Processing file: {filename}")
        try:
            with open(filename) as f:
                data = json.load(f)
            
            semantic_segments = data.get("semanticSegments", [])
            if not isinstance(semantic_segments, list):
                logging.warning(f"Warning: 'semanticSegments' in {filename} is not a list.")
                semantic_segments = []
            
            logging.info(f"From file {filename}, got {len(semantic_segments)} segments")
            all_semantic_segments.extend(semantic_segments)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error reading {filename}: {e}")
            continue

    return all_semantic_segments

def main():
    parser = argparse.ArgumentParser(description="Merge multiple JSON files containing semantic segments.")
    parser.add_argument("files", nargs='+', help="Paths to the JSON files to merge.")
    args = parser.parse_args()

    all_semantic_segments = merge_json_files(args.files)
    # lajitellaan varmuuden vuoksi
    all_semantic_segments.sort(key=extract_time, reverse=False)

    if not all_semantic_segments:
        logging.error("No valid segments were found.")
        sys.exit(1)

    mergedjson = {"semanticSegments": all_semantic_segments}
    merged_file = 'merged.json'

    with open(merged_file, 'w') as f:
        json.dump(mergedjson, f, indent=4)
    logging.info(f"Saved result to {merged_file}")

if __name__ == "__main__":
    main()

# eof