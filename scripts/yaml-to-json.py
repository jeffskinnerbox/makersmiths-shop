#!/usr/bin/env python3
import argparse
import json
import sys

import yaml


def convert_yaml_to_json(input_file, output_file=None, indent=2):
    """Convert a YAML file to JSON format."""
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
