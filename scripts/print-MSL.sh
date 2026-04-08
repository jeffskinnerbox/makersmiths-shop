#!/bin/bash
set -euo pipefail

# Generate Jinja2 template (you can run once; output is reusable)
scripts/signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Generate HTML sign-up sheet from Jinja2 template + YAML
scripts/signup-sheet.py --template output/signup-sheet-template.html.j2 --yaml input/MSL-volunteer-opportunities.yaml --output output/MSL-signup-sheet.html

# Render HTML sign-up sheet as a PDF file
wkhtmltopdf --orientation Landscape output/MSL-signup-sheet.html output/MSL-signup-sheet.pdf

# View the rendered HTML sign-up sheet as a PDF file
xdg-open output/MSL-signup-sheet.pdf
