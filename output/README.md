
# README.md

## How To Use Your Tools
In Ubuntu, you can convert an HTML file to a landscape PDF using several command-line tools.
`wkhtmltopdf` is often the most direct method,
while `pandoc` offers more flexibility if you have a LaTeX engine installed.

## Install Your Tools

```bash
sudo apt update
sudo apt install wkhtmltopdf pandoc
```

## Using Your Tools

```bash
# Step 1: Generate Jinja2 template (run once; output is reusable)
scripts/generate-signup-sheet-template.py --output output/signup-sheet-template.html.j2

# Step 2: Generate HTML sign-up sheet from Jinja2 template + YAML
scripts/signup-sheet.py --template output/signup-sheet-template.html.j2 --yaml input/metalshop-volunteer-opportunities.yaml --output output/metalshop-signup-sheet.html
scripts/signup-sheet.py --template output/signup-sheet-template.html.j2 --yaml input/MSL-volunteer-opportunities.yaml --output output/MSL-signup-sheet.html

# view the rendered HTML sign-up sheet in your browser
file:///home/jeff/src/projects/makersmiths/shop-sergeant/output/metalshop-signup-sheet.html
file:///home/jeff/src/projects/makersmiths/shop-sergeant/output/MSL-signup-sheet.html

# view the rendered HTML sign-up sheet as a PDF file
wkhtmltopdf --orientation Landscape output/metalshop-signup-sheet.html output/metalshop-signup-sheet.pdf
wkhtmltopdf --orientation Landscape output/MSL-signup-sheet.html output/MSL-signup-sheet.pdf

#NOTE: This needs more work
# Convert HTML → Word doc
pandoc output/metalshop-signup-sheet.html --reference-doc=input/custom-reference.docx -o output/metalshop-signup-sheet.docx
pandoc output/MSL-signup-sheet.html --reference-doc=input/custom-reference.docx -o output/MSL-signup-sheet.docx

#NOTE: This needs more work
# Convert YAML task list to Markdown
scripts/parse-opp-tasks.py input/metalshop-volunteer-opportunities.yaml output/metalshop-task-list.md
scripts/parse-tasks.py input/MSL-volunteer-opportunities.yaml output/MSL-task-list.md

#NOTE: This needs more work
# Convert YAML → JSON
scripts/yaml-to-json.py input/MSL-volunteer-opportunities.yaml | jq -C '.'

#NOTE: what about the creation of metalshop-task-list.docx
```
