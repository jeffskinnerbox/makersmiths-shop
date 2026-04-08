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



[01]:https://jinja.palletsprojects.com/en/stable/templates/

