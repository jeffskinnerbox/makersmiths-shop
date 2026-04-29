# Slidev + Excalidraw Presentation Workflow

Slidev is a Markdown-based, browser-rendered presentation framework — you write slides in plain
Markdown and run them with a local dev server. Excalidraw produces hand-drawn-style diagrams and
slide artwork. The two tools compose well, but there are three distinct ways to connect them, each
with real trade-offs. See [Choosing an Option](#choosing-an-option) to pick the right one before
you start.



To create PNG files exactly as displayed via Excalidraw, use the following:

```bash
# create PNG files exactly as displayed via Excalidraw
for file in ./diagrams/*.excalidraw; do
  excalidraw-cli convert "$file" --output "./assets/$(basename "${file%.*}.png")" --format png
done
```

To create PNG files with a transparent background, use the following:

```bash
#!/bin/bash

# Ensure the output directory exists
mkdir -p ./assets

# Loop through all .excalidraw files in the diagrams folder
for file in ./diagrams/*.excalidraw; do
  # Skip if no files are found
  [ -e "$file" ] || continue

  filename=$(basename "${file%.*}")

  echo "Converting $filename to transparent PNG..."

  # Using the 'convert' command with '--backgroundColor transparent'
  excalidraw-cli convert "$file" \
    --output "./assets/${filename}.png" \
    --format png \
    --background-color transparent
done

echo "Done! Transparent PNGs are in ./assets"
```


---

## Table of Contents

1. [Tools Overview](#tools-overview)
2. [Installation](#installation)
3. [Project Structure](#project-structure)
4. [Decks in This Repo](#decks-in-this-repo)
5. [Integrating Excalidraw with Slidev](#integrating-excalidraw-with-slidev)
   - [Option A — Runtime Addon](#option-a--runtime-addon-slidev-addon-excalidraw)
   - [Option B — SVG / PNG Static Export](#option-b--svg--png-static-export--selected)
   - [Option C — Use Existing PNGs Directly](#option-c--use-existing-pngs-directly)
   - [Choosing an Option](#choosing-an-option)
6. [Running a Presentation](#running-a-presentation)
7. [Slide Anatomy](#slide-anatomy)
8. [Presenter Mode & Zoom](#presenter-mode--zoom)
9. [Exporting Slides](#exporting-slides)
10. [Keyboard Shortcuts](#keyboard-shortcuts)
11. [Claude Code Integration](#claude-code-integration)
12. [Portability Tips](#portability-tips)
13. [References](#references)

---

## Tools Overview

### Slidev

Slidev ([sli.dev][01]) is a developer-focused presentation framework built on Vite and Vue 3.
Slides live in a single `slides.md` file — you write Markdown, and Slidev renders a live-reloading
browser presentation. It supports custom layouts, Vue components, speaker notes, and exports to PDF,
PNG, and PPTX.

Useful introductions: [Technical presentations with Slidev][02] and
["Slidev for Tech Talks" (PUGS Meetup)][03].

### Excalidraw

Excalidraw ([excalidraw.com][04]) is an open-source, collaborative whiteboard that produces
hand-drawn-style diagrams. It runs as a [Progressive Web App (PWA)][05] — meaning it can install
itself to your desktop and run fully offline, saving `.excalidraw` JSON files locally. You can also
[run it locally via Docker][06] if you need a permanently self-hosted instance.

Excalidraw exports SVG and PNG, and SVGs can carry an embedded copy of the source scene (so the
`.excalidraw` is recoverable from the SVG). See the [Excalidraw developer docs][07] and the
[Excalidraw Libraries][08] for reusable shape packs.

---

## Installation

### Prerequisites
To install Slidev, you need the following prerequisite packages and environment setup:

- **Node.js:** You need Node.js >= 18.0 (v20.12.0 or higher is recommended for the latest features).
- **Package Manager:** You will need one of the following to manage dependencies:
  - **`npm`** (comes bundled with Node.js)
  - **`pnpm`** (highly recommended by the Slidev team for speed and efficiency)
  - **`yarn`** or **`bun`**
- **Playwright / Chromium** — needed only if you plan to export slides to PDF or PNG

On Ubuntu, avoid `apt install nodejs` — the packaged version is usually outdated. Use **nvm**
instead:

```bash
# install nvm, then use it to get the latest LTS Node
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
nvm install --lts

# install pnpm globally
npm install -g pnpm

# install Playwright's Chromium (needed for PDF/PNG export)
npx playwright install chromium
```

### Excalidraw (Desktop / PWA)
On Ubuntu, Excalidraw can be installed through three primary "app" methods:
as a Progressive Web App (PWA), via an unofficial Desktop Client, or as a Docker container.
PWA is the recommended method by the Excalidraw developers.
To do this install, you do the following:

- At the top left corner of the Ubuntu Desktop, there is the **Activities** button.
  Click on it and it will bring up the **Search Bar**.
- Type in it "Excalidraw" and it will find Excalidraw as a PWA.
- Click Install. This adds Excalidraw to your Ubuntu application menu with its own icon,
  allowing it to run in a standalone window.
- Works fully offline, saves `.excalidraw` JSON files locally
- Ubuntu will automatically update Excalidraw for you

Alternatively, open [excalidraw.com][04] in any browser and use it there.

### Creating a New Presentation Repository

If you are starting a new deck in its own repo (not inside this monorepo):

```bash
mkdir -p ~/tmp/my-talk && cd ~/tmp/my-talk

# initialise local git repo
git init
touch README.md
cp ~/.dotfiles/checker-files/.gitignore .
cp ~/.dotfiles/checker-files/.markdownlint-cli2.jsonc .
git add --all && git commit -m "Initial commit"
git branch -M main

# create and push to GitHub
gh repo create my-talk --public --source=. --remote=origin --push
```

Breakdown of the `gh` Flags:
- `my-new-repo`: The name you want for the repository on GitHub.
- `--public`: Sets visibility (use `--private` if you prefer).
- `--source=.`: Tells the CLI to use the current directory (`.`) as the source for the repository.
- `--remote=origin`: Automatically adds the GitHub URL as a "remote" named origin.
- `--push`: Immediately pushes your local commits to the new GitHub repository.

Useful Optional `gh` Flags:
- `-d "My description"`: Adds a short bio/description to your repo.
- `--homepage "url"`: Adds a website link to the repo header.
- `--license "mit"`: Automatically adds a specific license file.
- `--gitignore "Python"`: Automatically adds a `.gitignore` template for a specific language.

If you want to delete your remote GitHub repository, you can use the following command:
`gh repo delete <repository-name>` or `gh repo delete`
if you are already inside the local folder for that repository.

### Bootstrapping Slidev Inside a Deck Directory
Once Node.js is already setup, you don't need to manually download a "SilDev" package.
One command can bring a working Slidev presentation development directory
and a Slidev template presentation `slides.md`.
You can bootstrap a project directly with this command:

```bash
cd presentations/my-talk
npm init slidev@latest   # prompts for a project name; installs all deps
pnpm dev                 # starts the live-reload server
```

The `npm install` will install all Slidev dependencies for its latest version.
The command will prompt you for a project name (e.g. `my-talk`)
and automatically install all the necessary sub-dependencies
(like Vite, Vue 3, and UnoCSS) into that folder.

After a few moments, `npm run dev` to start a live reload webserver that shows the presentation in your browser.
By editing`slides.md`, you change the presentation and its immediately visible in your browser.

---

## Project Structure

Each deck is a self-contained Slidev project:

```text
presentations/
└── <deck-name>/
    ├── slides.md           # all slide content (edit this)
    ├── package.json        # Slidev + addon deps
    ├── diagrams/           # .excalidraw source files (versioned)
    └── assets/             # exported SVG/PNG (re-generated by export script)
```

Helper scripts:

| Script | Purpose |
|--------|---------|
| `scripts/../setup.sh` | Install Node.js, pnpm, Slidev, Playwright |
| `scripts/../new-deck.sh <name>` | Bootstrap a new Slidev + Excalidraw deck |
| `scripts/../export-diagrams.py` | Export `.excalidraw` → SVG or PNG via headless browser |

---

## Decks in This Repo

| Directory | Description |
|-----------|-------------|
| `members-meeting/` | Members meeting overview |
| `requirements-review/` | Shop Sergeant requirements walkthrough |

Each deck: run `pnpm install` (first time only), then `pnpm dev`. See
[Running a Presentation](#running-a-presentation).

---

## Integrating Excalidraw with Slidev

Three approaches exist for embedding Excalidraw diagrams in Slidev slides.
All three are summarized below with their trade-offs.
**This project uses [Option B](#option-b--svg--png-static-export--selected)** — SVGs exported via `excalidraw-brute-export-cli` are used directly in slides.
See [Choosing an Option](#choosing-an-option) for the decision rationale.

---

### Option A — Runtime Addon (`slidev-addon-excalidraw`)

**How it works:** The community addon ([haydenull/slidev-addon-excalidraw][09]) provides a
`<Excalidraw>` Vue component. Slidev renders it in-browser using the Excalidraw export library
fetched from the `esm.sh` CDN. The `.excalidraw` file is served as a Vite static asset and
rendered at presentation time — no pre-export step needed.

**Pros:**
- No export step — edit the diagram, reload the slide
- Preserves the Excalidraw hand-drawn aesthetic exactly (correct fonts, colors, line style)
- Works directly with Python-generated `.excalidraw` files from `generate_slides.py`
- `darkMode` and `background` are controllable per-slide via component props

**Cons:**
- Community addon (not official Slidev); may lag behind Slidev releases and break on version bumps
- PDF export of Excalidraw-rendered slides is inconsistent — slides using the component may not
  render correctly when running `pnpm export`
- Requires an internet connection for CDN fonts (`esm.sh`) unless you self-host them (extra setup)
- `.excalidraw` files **must** live inside `public/` — Vite cannot serve files outside that root,
  which forces a copy/sync step separate from your version-controlled `diagrams/` directory
- Addon pins Excalidraw at v0.18.0; newer file formats may not render correctly

> For Option A setup details, see [`excalidraw-to-slidev.md`](./excalidraw-to-slidev.md).

---

### Option B — SVG / PNG Static Export *(selected)*

**How it works:** Export `.excalidraw` files to SVG or PNG ahead of time using a CLI tool or the
Excalidraw web app, then embed them in slides as ordinary Markdown images or `<img>` tags. Slidev
handles them like any other static asset — no addon, no runtime rendering.

**Pros:**
- No addon dependency; works with any Slidev version, now and in the future
- SVG is vector — looks crisp at any screen size or projector resolution
- PDF / PPTX export via `pnpm export` works reliably (no runtime rendering surprises)
- SVG exported with "Embed scene" preserves the Excalidraw source inside the file (recoverable)
- Full offline support — no CDN, no internet required at presentation time
- Simpler project structure — no `public/` directory duplication needed

**Cons:**
- Must re-run the export script each time a diagram changes (extra step vs Option A)
- First export requires internet access (headless browser loads Excalidraw from CDN to render)
- `excalidraw-to-svg` (no-Chromium variant) does not reproduce the hand-drawn font (`FG_Virgil`)
  — use `excalidraw-brute-export-cli` when font fidelity matters

#### Setup

No addon configuration is needed. Remove `addons: [excalidraw]` from `slides.md` if present.
The only tools required are an export CLI and the existing Slidev setup.

Install the export CLI (one-time, global):

```bash
npm install -g excalidraw-brute-export-cli
```

Or, for a lighter alternative that skips Chromium (but loses hand-drawn fonts):

```bash
npm install -g excalidraw-to-svg
```

#### Exporting Diagrams

**Manual (Excalidraw web app):**

Open [excalidraw.com][04], load the `.excalidraw` file, then `Export image → SVG` and check
**"Embed scene"** so the source is recoverable from the SVG later.

**Automated — `excalidraw-brute-export-cli` (headless Firefox, full font fidelity):**

One-time setup (install tool + Playwright Firefox browser):

```bash
npm install -g excalidraw-brute-export-cli
npx playwright install firefox
```

```bash
# export a single file
excalidraw-brute-export-cli \
  --input  diagrams/pipeline-overview.excalidraw \
  --format svg \
  --scale  2 \
  --embed-scene true \
  --output assets/pipeline-overview.svg

# batch-export all .excalidraw files in diagrams/ to assets/
for f in diagrams/*.excalidraw; do
  base=$(basename "$f" .excalidraw)
  excalidraw-brute-export-cli --input "$f" --format svg --scale 2 --embed-scene true --output "assets/${base}.svg" --quiet
  echo "exported: $base"
done
```

Required flags: `--scale` (1, 2, or 3; use 2 for presentation quality) and `--format`. The `--embed-scene` flag saves the source scene inside the SVG so it can be re-opened in Excalidraw later. Note: despite the README for the tool saying "Chromium", the current version (0.2.0) uses Playwright Firefox — install `firefox`, not `chromium`.

See [excalidraw-brute-export-cli][10] for the full option list.

**Automated — `excalidraw-to-svg` (Node only, no Chromium):**

```bash
# export a single file (output directory must exist)
excalidraw-to-svg ./diagrams/pipeline-overview.excalidraw ./assets
```

> **Note:** `excalidraw-to-svg` falls back to system fonts — the Excalidraw hand-drawn style
> (`FG_Virgil`) will not appear. Prefer `excalidraw-brute-export-cli` for visual fidelity.
> See [excalidraw-to-svg][11].

**Using the project export script:**

```bash
python3 presentations/scripts/export-diagrams.py \
    --input  diagrams/ \
    --output assets/ \
    --format svg
```

#### Slide Syntax

Basic Markdown image (Slidev sizes it to fit the slide):

```markdown
---
layout: center
---

# Pipeline Overview

![Pipeline Overview](./assets/pipeline-overview.svg)
```

With explicit sizing via an inline HTML tag and UnoCSS classes:

```markdown
---
layout: center
---

# Pipeline Overview

<img src="./assets/pipeline-overview.svg" class="w-[800px] mx-auto" />
```

Full-slide diagram (no title, diagram fills the frame):

```markdown
---
layout: center
---

<img src="./assets/pipeline-overview.svg" class="h-full" />
```

---

### Option C — Use Existing PNGs Directly

**How it works:** Reference PNG files already exported from the Excalidraw desktop app (or
produced by `generate_slides.py`) directly in Markdown. No tooling, no export step — just point
at the file.

**Pros:**
- Zero setup — works immediately if PNGs already exist in `assets/`
- No dependencies whatsoever
- Suitable for a quick one-off presentation where diagram quality is not critical

**Cons:**
- Raster images look blurry when the slide canvas is larger than the PNG resolution (common on
  high-DPI projectors or when zoomed)
- No round-trip back to Excalidraw source unless the original `.excalidraw` file was also kept
- Not suitable for PDF export where crisp vector output is expected

> Option C requires no setup. Embed PNGs exactly as shown in the [Slide Anatomy](#slide-anatomy)
> section using standard Markdown image syntax.

---

### Choosing an Option

| Factor | Option A (Addon) | Option B (SVG export) | Option C (PNG) |
|--------|------------------|-----------------------|----------------|
| Setup effort | High (`public/` copy, CDN fonts) | Medium (export CLI) | Zero |
| Edit → preview cycle | Instant (save → reload) | Edit → re-export | Edit → re-export |
| Offline support | No (CDN fonts), unless self-hosted | Yes | Yes |
| PDF export fidelity | Inconsistent | Reliable | Reliable but raster |
| Visual quality | Exact Excalidraw look | Vector-perfect | Raster (may blur) |
| Addon version risk | Yes (community addon) | None | None |
| Font fidelity | Native (CDN or self-hosted) | Full (brute-export-cli) | Baked into PNG |

**Why Option B was chosen for this project:**

Option A's appeal is zero re-export friction during editing, but two hard constraints ruled it out:
(1) PDF export is unreliable with the `<Excalidraw>` component, and these decks will be shared as
PDFs; (2) the `public/` directory duplication creates a second copy of every diagram to keep in
sync, which is error-prone. Option C is adequate for quick demos but produces blurry output on
projectors. Option B (SVG via `excalidraw-brute-export-cli`) gives vector-perfect output, reliable
PDF export, full offline support, and no addon maintenance risk — at the cost of one extra export
command when a diagram changes.

```text
diagrams/slide-NN.excalidraw
         │
         ▼  excalidraw-brute-export-cli (or export-diagrams.py)
assets/slide-NN.svg
         │
         ▼  <img src="./assets/slide-NN.svg" /> in slides.md
         │
         ├── pnpm dev    (live preview at http://localhost:3030)
         ├── pnpm build  (static HTML site → dist/)
         └── pnpm export (PDF / PPTX for sharing)
```

---

## Running a Presentation

Run all commands from inside the deck's directory:

```bash
cd presentations/members-meeting   # or requirements-review

pnpm install        # first time only — installs all deps
pnpm dev            # live-reload dev server → http://localhost:3030
pnpm build          # build static site → dist/
pnpm export         # export to PDF (requires playwright-chromium)
```

---

## Slide Anatomy

Slides are separated by `---`. The first block is the global config; subsequent blocks are
individual slides:

```markdown
---
theme: default
title: My Presentation
aspectRatio: 16/9
---

# Title Slide

Subtitle or opening content

---
layout: center
---

# Diagram Slide (Option B — SVG)

<img src="./assets/slide-01.svg" class="h-4/5 mx-auto" />

---
layout: center
---

# Diagram Slide (Option C — PNG fallback)

![](./assets/slide-01.png)

---

# Slide with Speaker Notes

Audience-visible content here.

<!-- Speaker notes (only shown in presenter view): -->
These are my notes.
```

See the [Slidev Layouts Guide][12] for all built-in layout options.

---

## Presenter Mode & Zoom

Slidev has a built-in presenter view with speaker notes:

```bash
# start with remote access (generates a QR code for audience to follow along)
pnpm dev --remote

# presenter URL (open in a separate browser tab):
# http://localhost:3030/presenter
```

**Using with Zoom:**
1. Run `pnpm dev` to start the server.
2. Open the presenter view (`/presenter`) on your local monitor.
3. Share `http://localhost:3030` (the clean audience view) to Zoom, or share your whole screen and
   keep the presenter view on a second monitor.

---

## Exporting Slides

```bash
# Export to PDF (requires playwright-chromium)
pnpm export

# Export to PNG (one image per slide)
pnpm export -- --format png

# Export to PPTX (opens in PowerPoint / LibreOffice Impress)
pnpm export -- --format pptx

# Build a static HTML site (self-contained; open dist/index.html offline)
pnpm build
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `F` | Fullscreen |
| `O` | Slide overview |
| `D` | Toggle drawing mode (annotate live, doesn't touch source) |
| `B` | Blackout |
| `G` | Go to slide number |

---

## Claude Code Integration

Claude Code can generate `.excalidraw` JSON directly (the file format is well-documented), write
or update `slides.md`, and run the export pipeline via Bash. The net result: describe a diagram or
slide structure, and Claude Code produces the files — zero manual assembly.

Relevant Claude Code skills and resources:

| Skill / Resource | Link |
|-----------------|------|
| `excalidraw` skill | (installed locally) |
| `python-refactor` skill | [mcpmarket.com][13] |
| `python-simplifier` skill | [mcpmarket.com][14] |
| Custom Excalidraw diagram skill | [ooiyeefei/ccc][15] |
| `excalidraw-diagram` skill | [coleam00/excalidraw-diagram-skill][16] |

Video walkthroughs:
- [Claude Code + Excalidraw MCP: AI Draws Diagrams in Real-Time][17]
- [Build BEAUTIFUL Diagrams with Claude + Excalidraw (Full Workflow)][18]
- [Build BEAUTIFUL Diagrams with Claude Code][19]
- [Claude Code + Karpathy Slides Changed Presentations (MARP System)][20]
- [Custom Claude Code Skill: Auto-Generating Architecture Diagrams with Excalidraw][21]

---

## Portability Tips

- Keep everything in one git repo: `.excalidraw` source files, exported SVGs, and `slides.md`.
- Add a shell script or Makefile that re-exports SVGs and launches Slidev — one command to go from
  zero to presenting.
- `pnpm build` produces a static HTML bundle (`dist/`) — open `dist/index.html` in any browser as
  a fallback if your dev environment has issues.
- For air-gapped / offline use, run `pnpm build` ahead of the presentation; no internet needed at
  runtime when using Option B SVGs.

---

[01]: https://sli.dev/
[02]: https://www.wimdeblauwe.com/blog/2024/11/05/technical-presentations-with-slidev/
[03]: https://www.youtube.com/watch?v=gsWCVPsoClw
[04]: https://excalidraw.com/
[05]: https://topflightapps.com/ideas/native-vs-progressive-web-app/
[06]: https://docs.excalidraw.com/docs/introduction/development
[07]: https://docs.excalidraw.com/
[08]: https://libraries.excalidraw.com/
[09]: https://github.com/haydenull/slidev-addon-excalidraw
[10]: https://github.com/realazthat/excalidraw-brute-export-cli
[11]: https://github.com/JRJurman/excalidraw-to-svg
[12]: https://sli.dev/guide/layout
[13]: https://mcpmarket.com/tools/skills/python-refactor
[14]: https://mcpmarket.com/tools/skills/python-code-simplifier
[15]: https://github.com/ooiyeefei/ccc/tree/main/skills/excalidraw
[16]: https://github.com/coleam00/excalidraw-diagram-skill/tree/main
[17]: https://www.youtube.com/watch?v=ufW78Amq5qA
[18]: https://www.youtube.com/watch?v=Gf-yFsbxgyo
[19]: https://www.youtube.com/watch?v=m3fqyXZ4k4I
[20]: https://www.youtube.com/watch?v=RBcc_ezfh1s
[21]: https://yeefei.beehiiv.com/p/custom-claude-code-skill-auto-generating-updating-architecture-diagrams-with-excalidraw
