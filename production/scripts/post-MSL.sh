#!/bin/bash

# prevents scripts from "marching forward" blindly after a critical failure
set -euo pipefail

# Generate Jinja2 template (you can run once; output is reusable)
scripts/generate-signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Generate HTML sign-up sheet from Jinja2 template + YAML
scripts/signup-sheet.py --template output/signup-sheet-template.html.j2 --yaml input/MSL-volunteer-opportunities.yaml --output output/MSL-signup-sheet.html

# View the rendered HTML sign-up sheet in your browser
google-chrome file:///home/jeff/src/projects/makersmiths/shop-sergeant/output/MSL-signup-sheet.html

# NOTE: Replace the above with a command that directs the HTML file to a website
