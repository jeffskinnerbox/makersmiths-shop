#!/bin/bash

INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.*}.html"
# Ensure this points to where you saved the template.html above
TEMPLATE_PATH="$(dirname "$0")/template.html"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Usage: ./md2html.sh <filename.md>"
  exit 1
fi

if [[ ! -f "$TEMPLATE_PATH" ]]; then
  echo "Error: template.html not found at $TEMPLATE_PATH"
  exit 1
fi

echo "Converting $INPUT_FILE using template..."

# --template: Uses our custom HTML wrapper
# --standalone: Required to use templates
pandoc "$INPUT_FILE" \
  --standalone \
  --template="$TEMPLATE_PATH" \
  -f gfm \
  -t html \
  -o "$OUTPUT_FILE"

if [[ -f "$OUTPUT_FILE" ]]; then
  echo "Success! Created $OUTPUT_FILE"
  # xdg-open "$OUTPUT_FILE" # Uncomment to auto-open
else
  echo "Error: Conversion failed."
fi
