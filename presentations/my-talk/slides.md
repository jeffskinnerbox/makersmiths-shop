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

<contact@example.com>
