#!/usr/bin/env python3
import yaml
import json
import sys


def convert_yaml_to_json(input_file, output_file=None, indent=2):
    """Convert a YAML file to JSON format."""
    with open(input_file, "r") as f:
        data = yaml.safe_load(f)

    json_output = json.dumps(data, indent=indent, default=str)

    if output_file:
        with open(output_file, "w") as f:
            f.write(json_output)
        print(f"JSON written to {output_file}")
    else:
        print(json_output)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/yaml-to-json.py <input.yaml> [output.json]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_yaml_to_json(input_file, output_file)


if __name__ == "__main__":
    main()
