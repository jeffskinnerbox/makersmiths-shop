
```bash
# Step 1 - generate template (same)
python3 scripts/generate-signup-sheet2-template.py --output output/signup-sheet2-template.html.j2

# Step 2 - use signup-sheet2.py, not signup-sheet.py
python3 scripts/signup-sheet2.py --template output/signup-sheet2-template.html.j2 --yaml input/metalshop-volunteer-opportunities.yaml --output output/metalshop-signup-sheet2.html

# Step 3 - PDF (same)
wkhtmltopdf --orientation Landscape output/metalshop-signup-sheet2.html output/metalshop-signup-sheet2.pdf
```


- signup-sheet.py → v1 template (signup-sheet-template.html.j2)
- signup-sheet2.py → v2 template (signup-sheet2-template.html.j2)
