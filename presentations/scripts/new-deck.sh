#!/usr/bin/env bash
# new-deck.sh
#
# Bootstraps a new Slidev presentation project inside the presentations/ directory.
#
# Creates:
#   presentations/<name>/
#     slides.md          Slide content — edit this
#     package.json       Slidev + excalidraw addon deps
#     .gitignore
#     diagrams/          Put your .excalidraw source files here
#     assets/            Put exported SVG/PNG files here (output of export-diagrams.py)
#
# The generated slides.md includes examples of all three embedding options
# (addon, SVG, PNG) so you can pick and delete what you don't need.
#
# Usage:
#   bash presentations/scripts/new-deck.sh my-talk
#   bash presentations/scripts/new-deck.sh "shop-sergeant-overview"

set -euo pipefail

DECK_NAME="${1:-}"
if [[ -z "$DECK_NAME" ]]; then
    echo "Usage: $0 <deck-name>"
    echo "  Example: $0 my-talk"
    exit 1
fi

# Resolve presentations/ relative to the repo root (parent of this script's dir)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESENTATIONS_DIR="$(dirname "$SCRIPT_DIR")"
DECK_DIR="$PRESENTATIONS_DIR/$DECK_NAME"

if [[ -d "$DECK_DIR" ]]; then
    echo "Directory $DECK_DIR already exists. Aborting."
    exit 1
fi

echo "Creating deck: $DECK_DIR"
mkdir -p "$DECK_DIR/diagrams"
mkdir -p "$DECK_DIR/assets"

# ── package.json ──────────────────────────────────────────────────────────────
# Includes:
#   @slidev/cli      — the Slidev build/dev/export CLI
#   @slidev/theme-default — baseline theme (swap for another if desired)
#   slidev-addon-excalidraw — Option A: direct .excalidraw embedding
#   playwright-chromium  — required by `slidev export` for PDF/PNG output
cat > "$DECK_DIR/package.json" << 'PKGJSON'
{
  "name": "DECK_NAME_PLACEHOLDER",
  "private": true,
  "scripts": {
    "dev":    "slidev slides.md --open",
    "build":  "slidev build slides.md",
    "export": "slidev export slides.md"
  },
  "dependencies": {
    "@slidev/cli": "latest",
    "@slidev/theme-default": "latest",
    "slidev-addon-excalidraw": "latest"
  },
  "devDependencies": {
    "playwright-chromium": "latest"
  }
}
PKGJSON

# Patch in the actual deck name
sed -i "s/DECK_NAME_PLACEHOLDER/$DECK_NAME/g" "$DECK_DIR/package.json"

# ── .gitignore ────────────────────────────────────────────────────────────────
cat > "$DECK_DIR/.gitignore" << 'GITIGNORE'
node_modules/
dist/
.slidev/
GITIGNORE

# ── slides.md ─────────────────────────────────────────────────────────────────
# The first YAML block is the global presentation config.
# Each slide is separated by `---`.
# Speaker notes go in HTML comments <!-- like this --> at the bottom of a slide.
cat > "$DECK_DIR/slides.md" << 'SLIDESMD'
---
# Global presentation config
theme: default

# Remove the addons line if you are NOT using Option A (direct .excalidraw embedding).
# Requires:  pnpm add slidev-addon-excalidraw
addons:
  - excalidraw

title: "My Presentation"
titleTemplate: "%s — Slidev"
aspectRatio: 16/9
canvasWidth: 980

# Enable live drawing/annotation during presentation (press D)
drawings:
  enabled: true
  persist: false
---

# My Presentation

Subtitle · Date · Author

<!-- Speaker notes: visible only in presenter view (localhost:3030/presenter) -->
Opening remarks go here.

---
layout: center
---

# Option A — Direct Excalidraw embedding

Uses the `slidev-addon-excalidraw` addon. No export step needed.
Edit the .excalidraw file, reload the slide.

<Excalidraw filePath="./diagrams/example.excalidraw" />

<!-- Make sure diagrams/example.excalidraw exists before using this slide -->

---
layout: center
---

# Option B — SVG export (recommended for PDF/PPTX)

Export first:  python3 presentations/scripts/export-diagrams.py --input diagrams/ --output assets/

<img src="./assets/example.svg" class="h-4/5 mx-auto" />

---
layout: center
---

# Option C — PNG (zero setup, works right now)

Directly reference any PNG. Good for quick prototyping.

![](./assets/example.png)

---

# Slide with two columns

<div class="grid grid-cols-2 gap-4">
<div>

## Left column

- Bullet point one
- Bullet point two

</div>
<div>

<img src="./assets/example.svg" class="h-full" />

</div>
</div>

---
layout: end
---

# Questions?

contact@example.com
SLIDESMD

# ── Install dependencies ───────────────────────────────────────────────────────
echo "Installing npm dependencies (pnpm install)..."
cd "$DECK_DIR"
pnpm install --silent

echo ""
echo "Deck created: $DECK_DIR"
echo ""
echo "Next steps:"
echo "  1. Add .excalidraw files to  $DECK_DIR/diagrams/"
echo "  2. Edit slides:              $DECK_DIR/slides.md"
echo "  3. Start dev server:         cd $DECK_DIR && pnpm dev"
echo "  4. Presenter view:           http://localhost:3030/presenter"
echo "  5. Export to PDF:            cd $DECK_DIR && pnpm export"
