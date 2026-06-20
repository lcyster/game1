#!/usr/bin/env python3

import json
import sys

def analyze_har(har_file_path):
    """Analyzes a HAR file and prints a summary of the slowest requests."""
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {har_file_path}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {har_file_path}")
        return

    entries = har_data['log']['entries']

    sorted_entries = sorted(entries, key=lambda x: x['time'], reverse=True)

    print("Slowest requests:")
    for entry in sorted_entries[:10]:
        url = entry['request']['url']
        time = entry['time']
        timings = entry['timings']
        print(f"\nURL: {url}")
        print(f"  Total time: {time:.2f} ms")
        print(f"  Timings: ")
        for k, v in timings.items():
            if v != -1:
                print(f"    {k}: {v:.2f} ms")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: har_analyzer.py <path_to_har_file>")
        sys.exit(1)

    analyze_har(sys.argv[1])
