#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from typing import Any, cast


def analyze_har(har_file_path: str) -> None:
    try:
        har_data = cast(dict[str, Any], json.loads(Path(har_file_path).read_text(encoding='utf-8')))
    except FileNotFoundError:
        print(f"Error: File not found at {har_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {har_file_path}")
        return

    log_data = har_data.get('log')
    if not isinstance(log_data, dict):
        print(f"Error: HAR file missing log data at {har_file_path}")
        return

    entries = log_data.get('entries')
    if not isinstance(entries, list):
        print(f"Error: HAR file missing request entries at {har_file_path}")
        return

    valid_entries = [entry for entry in entries if isinstance(entry, dict)]
    sorted_entries = sorted(valid_entries, key=get_entry_time, reverse=True)

    print("Slowest requests:")
    for entry in sorted_entries[:10]:
        request_data = entry.get('request')
        timings = entry.get('timings')
        if not isinstance(request_data, dict) or not isinstance(timings, dict):
            continue

        request_url = request_data.get('url')
        total_time = entry.get('time')
        if not isinstance(request_url, str) or not isinstance(total_time, int | float):
            continue

        print(f"\nURL: {request_url}")
        print(f"  Total time: {total_time:.2f} ms")
        print("  Timings: ")
        for timing_name, timing_value in timings.items():
            if isinstance(timing_value, int | float) and timing_value != -1:
                print(f"    {timing_name}: {timing_value:.2f} ms")


def get_entry_time(entry: dict[Any, Any]) -> float:
    entry_time = entry.get('time')
    return float(entry_time) if isinstance(entry_time, int | float) else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a HAR file and print the slowest requests."
    )
    parser.add_argument("har_file", help="path to the HAR file to analyze")
    args = parser.parse_args()

    analyze_har(args.har_file)


if __name__ == '__main__':
    main()
