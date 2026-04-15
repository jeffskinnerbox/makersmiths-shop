#!/usr/bin/env bash
# Convert docs/requirements.md → docs/requirements.pdf
# Usage: bash scripts/requirements-to-pdf.sh [output.pdf]
#
# Notes:
#   --enable-local-file-access: wkhtmltopdf blocks local file reads by default (images drop silently)
#   cd "$DOCS_DIR": pandoc resolves image paths relative to CWD; must be in docs/ for PNGs to embed

set -euo pipefail

DOCS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../docs" && pwd)"
INPUT="$DOCS_DIR/requirements.md"
OUTPUT="${1:-$DOCS_DIR/requirements.pdf}"

cd "$DOCS_DIR"

pandoc \
  --from=gfm \
  --to=pdf \
  --pdf-engine=wkhtmltopdf \
  --pdf-engine-opt="--enable-local-file-access" \
  --pdf-engine-opt="-s" --pdf-engine-opt="Letter" \
  --pdf-engine-opt="--margin-top" --pdf-engine-opt="18mm" \
  --pdf-engine-opt="--margin-bottom" --pdf-engine-opt="18mm" \
  --pdf-engine-opt="--margin-left" --pdf-engine-opt="22mm" \
  --pdf-engine-opt="--margin-right" --pdf-engine-opt="22mm" \
  --metadata title="Shop Sergeant — System Requirements" \
  -o "$OUTPUT" \
  "$INPUT"

echo "PDF written to: $OUTPUT"
