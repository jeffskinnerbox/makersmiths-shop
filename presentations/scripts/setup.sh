#!/usr/bin/env bash
# setup.sh
#
# Installs all prerequisites for the Slidev + Excalidraw presentation workflow.
#
# What this installs:
#   - Node.js >= 18 (checked, not installed — install it yourself if missing)
#   - pnpm (fast Node package manager, recommended by Slidev)
#   - @slidev/cli (the Slidev command-line tool, installed globally)
#   - playwright-chromium (headless browser used by Slidev's PDF export
#     and by export-diagrams.py for rendering Excalidraw)
#   - Python playwright (used by export-diagrams.py)
#
# Run once per machine:
#   bash presentations/scripts/setup.sh

set -euo pipefail

# ── helpers ──────────────────────────────────────────────────────────────────
info()  { echo "  [INFO]  $*"; }
ok()    { echo "  [ OK ]  $*"; }
err()   { echo "  [ERR ]  $*" >&2; exit 1; }

# ── 1. Node.js ────────────────────────────────────────────────────────────────
info "Checking Node.js..."
if ! command -v node &>/dev/null; then
    err "Node.js not found. Install Node.js >= 18 from https://nodejs.org/en/download/ \
then re-run this script."
fi

NODE_VERSION=$(node -e "process.stdout.write(process.versions.node)")
NODE_MAJOR=$(echo "$NODE_VERSION" | cut -d. -f1)
if [[ "$NODE_MAJOR" -lt 18 ]]; then
    err "Node.js $NODE_VERSION is too old. Slidev requires >= 18. \
Update via https://nodejs.org/en/download/ or nvm."
fi
ok "Node.js $NODE_VERSION"

# ── 2. pnpm ───────────────────────────────────────────────────────────────────
info "Checking pnpm..."
if ! command -v pnpm &>/dev/null; then
    info "Installing pnpm globally via npm..."
    npm install -g pnpm
fi
PNPM_VERSION=$(pnpm --version)
ok "pnpm $PNPM_VERSION"

# ── 3. Slidev CLI ─────────────────────────────────────────────────────────────
info "Installing @slidev/cli globally..."
pnpm add -g @slidev/cli
SLIDEV_VERSION=$(slidev --version 2>/dev/null | head -1 || echo "installed")
ok "Slidev $SLIDEV_VERSION"

# ── 4. playwright-chromium (for PDF export and diagram export) ────────────────
# Installed globally so it's available in any deck project and to the Python
# export-diagrams.py script.
info "Installing playwright-chromium globally..."
pnpm add -g playwright-chromium

# Download the Chromium browser binary (needed before first use)
info "Downloading Chromium browser binary..."
pnpm exec playwright install chromium
ok "playwright-chromium ready"

# ── 5. Python playwright (for export-diagrams.py) ─────────────────────────────
info "Installing Python playwright..."
if ! command -v python3 &>/dev/null; then
    err "python3 not found. Install Python 3.9+ then re-run."
fi

python3 -m pip install --quiet playwright
# Install the Chromium browser for the Python playwright bindings
python3 -m playwright install chromium
ok "Python playwright ready"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "Setup complete. Next steps:"
echo "  bash presentations/scripts/new-deck.sh <deck-name>"
echo "  cd presentations/<deck-name>"
echo "  pnpm dev"
