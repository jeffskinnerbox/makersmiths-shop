#!/usr/bin/env python3
"""
yaml-to-json.py

Converts a YAML task catalog to JSON. Outputs to stdout by default; use -o to
write to a file. Useful for piping into jq for ad-hoc inspection.

Usage:
    python3 scripts/yaml-to-json.py input/MSL-volunteer-opportunities.yaml | jq -C '.'
    python3 scripts/yaml-to-json.py input/MSL-volunteer-opportunities.yaml -o output/tasks.json
"""
import argparse
import json
import sys

import yaml


def convert_yaml_to_json(input_file, output_file=None, indent=2):
    """Convert a YAML file to JSON and write it to a file or stdout.

    Args:
        input_file: Path to the input YAML file.
        output_file: Path to the output JSON file. If None, prints to stdout.
        indent: JSON indentation level (default: 2).
    """
    with open(input_file, "r") as f:
        data = yaml.safe_load(f)

    json_output = json.dumps(data, indent=indent, default=str)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json_output)
        print(f"JSON written to {output_file}", file=sys.stderr)
    else:
        print(json_output)


def main():
    """Parse CLI args and run the YAML-to-JSON conversion."""
    parser = argparse.ArgumentParser(
        description="Convert a YAML task catalog to JSON."
    )
    parser.add_argument("input", help="Input YAML file path")
    parser.add_argument(
        "-o", "--output", default=None, help="Output JSON file path (default: stdout)"
    )
    args = parser.parse_args()
    convert_yaml_to_json(args.input, args.output)


if __name__ == "__main__":
    main()
