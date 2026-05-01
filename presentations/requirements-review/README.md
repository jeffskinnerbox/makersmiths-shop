
### Installing Slidev

```bash
# install slidev
#npm install -g @slidev/cli
npm init slidev

# install cli
npm install -g @swiftlysingh/excalidraw-cli

# test if slidev is working
slidev --version
```

### Do Presentation

```bash
cd ~/src/projects/makersmiths/shop-sergeant/presentations/requirements-review

slidev slides.md
```

### Create a Portable Version of this Presentation
I want something I could put on a thumb drive,
plug the thumb drive into a laptop, and present `slide.md`?
There are two practical options:

1. PDF (simplest):
No browser or server needed — any laptop can open it.

```bash
cd presentations/requirements-review
pnpm export --output shop-sergeant-requirements.pdf
```

Copy the PDF to the thumb drive.
Requires `playwright-chromium` installed.

2. Static site (keeps animations/interactivity)

```bash
  cd presentations/requirements-review
  pnpm build    # outputs to dist/
```

Copy the `dist/` folder to the thumb drive.
On the target laptop, open a terminal in that folder `dist/` and run:
`python3 -m http.server 3030`
Then open `http://localhost:3030` in a browser.
Python 3 is pre-installed on most Macs/Linux machines; Windows may need it installed.

**Recommendation:** Export to PDF for maximum portability — no dependencies, no server, works everywhere.
Use the static site only if you need click animations or the interactive presenter mode.

If you haven't installed playwright yet:

```bash
cd presentations/requirements-review
pnpm add -D playwright-chromium
pnpm exec playwright install chromium
```

```

