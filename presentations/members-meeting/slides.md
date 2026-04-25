---
# Global Slidev config
theme: default

# Remove the addons block if you're using PNG/SVG images only (Option B/C).
# Requires:  pnpm add slidev-addon-excalidraw
addons:
  - excalidraw

title: "Shop Sergeant — Requirements"
titleTemplate: "%s — Makersmiths"
aspectRatio: 16/9
canvasWidth: 980

drawings:
  enabled: true   # press D during presentation to annotate live
  persist: false
---

# Shop Sergeant

Requirements Overview · Makersmiths

<!-- Speaker notes: introduce the problem — volunteer tracking is manual today -->

---
layout: center
---

<!--
  Option A: direct .excalidraw embedding (requires slidev-addon-excalidraw addon).
  If the addon isn't installed, switch to Option C below.
-->

<Excalidraw filePath="./slide-01.excalidraw" />

<!-- Overview of the current state and goals -->

---
layout: center
---

<Excalidraw filePath="./slide-02.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-03.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-04.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-05.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-06.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-07.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-08.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-09.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-10.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-11.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-12.excalidraw" />

---
layout: center
---

<Excalidraw filePath="./slide-13.excalidraw" />

---
layout: end
---

# Questions?

<!--
  Option C fallback — if the excalidraw addon isn't available, replace each
  <Excalidraw filePath="./slide-NN.excalidraw" /> above with:

      ![](./slide-NN.png)

  PNGs already exist in this directory and work with zero extra tooling.
  They may appear slightly blurry on very large projectors.

  Option B (SVG, sharpest quality):
    1. python3 presentations/scripts/export-diagrams.py \
           --input presentations/requirements/ \
           --output presentations/requirements/assets/ \
           --format svg
    2. Replace each <Excalidraw ...> with:
           <img src="./assets/slide-NN.svg" class="h-full" />
-->
