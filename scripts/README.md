# README.md


## Ready For Friendly Testing
* **`generate-signup-sheet-template.py`** - This script generates a [Jinja2 HTML template][01] for the volunteer opportunities sign-up sheet.
  This template captures the layout of a sign-up sheet, and it is what needs modification to change the sign-up sheet layout.
  If you have an agreed to layout, you can run run this script once and the template will be reusable in the future.
* **`signup-sheet.py`** - This script generates a HTML file formatted as a volunteer opportunities sign-up sheet.
  To do this, it uses the Jinja2 HTML template + YAML formatted volunteer opportunities file (eg. `MSL-volunteer-opportunities.yaml`)
  and combines them to create a HTML file ready to be printed or web posted.
* **`signup_sheet_builder.py`** - This is a core library. It is imported by:
  * `scripts/signup-sheet.py` (the CLI entry point) — `imports load_yaml, extract_locations, attach_qr_codes, render_sheet`
  * `tests/test_signup_sheet_builder.py` — test suite for the library
  It provides all the business logic for sign-up sheet generation:

  | Function | Purpose |
  |:--------:|:--------:|
  | load_yaml() | Loads YAML from file path or stdin |
  | detect_format() | Detects which root key format the YAML uses |
  | extract_locations() | Parses shop/area/location/task hierarchy from YAML |
  | attach_qr_codes() | Generates QR codes and attaches them to tasks |
  | render_sheet() | Renders the Jinja2 HTML template with location/task data |

## Requires Further Development
* **`post-metalshop.sh` and `post-MSL.sh`** - These scripts will create a HTML formatted "Volunteer Opportunities"
  file suitable for posting on a website.  Currently, the posting is on your local browser.
* **`print-metalshop.sh` and `print-MSL.sh`** - These scripts will create a PDF formatted "Volunteer Opportunities"
  file suitable for 8.5 x 11-inch paper paper printing. Currently, the print is in a window on your local machine.

**NOTE:** Need to create a tool for MSWord document via (or using the PDF version)
`pandoc -f gfm output/MSL-volunteer-opportunities.md -o output/MSL-volunteer-opportunities.docx --reference-doc docs/custom-reference.docx`

## Utility Scripts
* **`clean-up.sh`** - This utility script remove old files so that refreshed version of
  volunteer opportunities sign-up sheet can be created.
  Currently only backup files (e.g. `*.bak*`) and the `@/output` directory is touched.

## Deprecated Utility Scripts
* **`parse-opp-tasks.py` and `parse-tasks.py`** - These are utility script that converse a volunteer opportunities file
  (eg. `MSL-volunteer-opportunities.yaml`) to a Markdown file,
  formatted somewhat like the target volunteer opportunities file to be used in production.
  Initially used for debugging, and there is no plan to use this script in production.
* **`yaml-to-json.py`** - This is a utility script that converse a volunteer opportunities file (eg. `MSL-volunteer-opportunities.yaml`)
  to a JSON file.  Initially used for debugging, and there is no plan to use this script in production.

----

## `md2html.sh` Script
Gemini Prompts:
1. I'm using lazyvim and it can format a Markdown file into HTML within my browser.  What tools is it using to do this?
1. I like the quality of the HTLM created by this lazyvim process. Can you analyze the tools lazyvim is using and create for me a bash script that will give me the same output as the lazyvim process?

The reason you like the quality of that HTML is that markdown-preview.nvim doesn't just use a generic parser; it uses Markdown-it along with a specific CSS stylesheet designed to mimic the "GitHub" or "Gfm" (GitHub Flavored Markdown) look.

To replicate this in a standalone Bash script, we can use pandoc (the Swiss Army knife of document conversion) combined with a custom CSS file to get that same polished, professional styling.

The Logic
The LazyVim process relies on a Node.js server. For a simple script, we'll swap that for pandoc.

Parser: We'll use pandoc with the GitHub Flavored Markdown extension (gfm).

Styling: We'll pull a high-quality GitHub-style CSS (like the one used by Sindre Sorhus) and embed it directly into the HTML so the file is "standalone" and looks great even offline.

```bash
#!/bin/bash

# --- Check for dependencies ---
if ! command -v pandoc &> /dev/null; then
    echo "Error: 'pandoc' is not installed. Install it with: sudo apt install pandoc"
    exit 1
fi

# --- Variables ---
INPUT_FILE="$1"
OUTPUT_FILE="${INPUT_FILE%.*}.html"
CSS_URL="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown.min.css"
TEMP_CSS="/tmp/github-markdown.css"

# Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Usage: ./md2html.sh <filename.md>"
    exit 1
fi

# --- Action ---
echo "Fetching GitHub styling..."
curl -s "$CSS_URL" -o "$TEMP_CSS"

echo "Converting $INPUT_FILE to $OUTPUT_FILE..."

# Pandoc Command Breakdown:
# -s: Standalone (creates a full HTML doc, not just a snippet)
# --metadata title: Sets the tab title to the filename
# -f gfm: From GitHub Flavored Markdown
# -t html: To HTML
# -H: Includes the CSS in the <head> within a <style> block
# --body-prefix/suffix: Wraps the content in the 'markdown-body' class required by the CSS
pandoc "$INPUT_FILE" \
    -s \
    --metadata title="$(basename "$INPUT_FILE")" \
    -f gfm \
    -t html \
    -H "$TEMP_CSS" \
    --body-prefix='<article class="markdown-body" style="padding: 45px; max-width: 980px; margin: 0 auto;">' \
    --body-suffix='</article>' \
    -o "$OUTPUT_FILE"

echo "Done! Opening in browser..."
# Use 'xdg-open' for Linux/Ubuntu systems
xdg-open "$OUTPUT_FILE"
```

How to use it:
1. Make it executable: chmod +x md2html.sh
1. Run it on a markdown file: ./md2html.sh your_notes.md

Why this works:
* The CSS Class: The github-markdown-css library requires the content to be wrapped in a class called .markdown-body. The script uses Pandoc's --body-prefix to inject that <article> tag automatically.

* The Math/Code Quality: pandoc is extremely reliable for rendering code blocks and math (if you have LaTeX in your notes), which matches the high-end feel of the LazyVim preview.

* Portability: By using -H (header include), the CSS is baked into the HTML file. You can email that .html file to anyone, and it will look exactly the same on their machine.

Since you're comfortable with Ubuntu 24.04 and Tmux, you could even alias this in your .bashrc so you can convert files on the fly without leaving your terminal session.

## Convert requirements.md to PDF

```bash
cd ~/src/projects/makersmiths/shop-sergeant/docs

# create the html version of requirements.md
./scripts/md2html.sh requirements.md

# create the pdf version of requirements.md
#wkhtmltopdf --enable-local-file-access requirements.html requirements.pdf
google-chrome --headless --disable-gpu --print-to-pdf=requirements.pdf requirements.html

# display & inspect your pdf file
xdg-open requirements.pdf
```


[01]:https://jinja.palletsprojects.com/en/stable/templates/

