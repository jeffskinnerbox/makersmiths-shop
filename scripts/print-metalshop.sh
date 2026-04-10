#!/bin/bash

# prevents scripts from "marching forward" blindly after a critical failure
set -euo pipefail

# Generate Jinja2 template (you can run once; output is reusable)
scripts/generate-signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Generate HTML sign-up sheet from Jinja2 template + YAML
scripts/signup-sheet.py --template output/signup-sheet-template.html.j2 --yaml input/metalshop-volunteer-opportunities.yaml --output output/metalshop-signup-sheet.html

# Render HTML sign-up sheet as a PDF file
wkhtmltopdf --orientation Landscape output/metalshop-signup-sheet.html output/metalshop-signup-sheet.pdf

# View the rendered HTML sign-up sheet as a PDF file
xdg-open output/metalshop-signup-sheet.pdf

# NOTE: Replace the above with a command that directs the PDF file to a printer
