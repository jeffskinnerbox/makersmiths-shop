
# README.md

| Skills | Discription |
|:----------------:|:----------------: |
| excalidraw | |
| python-refactor | <https://mcpmarket.com/tools/skills/python-refactor> |
| python-simplifer | <https://mcpmarket.com/tools/skills/python-code-simplifier> |


## Installing SliDev
To install Slidev, you need the following prerequisite packages and environment setup:

### Core Requirements
* **Node.js:** You need Node.js >= 18.0 (v20.12.0 or higher is recommended for the latest features).
* **Package Manager:** You will need one of the following to manage dependencies:
  * **`npm`** (comes bundled with Node.js)
  * **`pnpm`** (highly recommended by the Slidev team for speed and efficiency)
  * **`yarn`** or **`bun`**

### Recommended Setup (Linux/Ubuntu)
If you are setting this up on a Linux system (like Ubuntu 24.04), it is best to avoid using `sudo apt install nodejs`,
as the version in the default repositories is often outdated. Instead, use a version manager:
* **nvm (Node Version Manager):** This allows you to install the specific version required.

  ```bash
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
  nvm install --lts
  ```

* **pnpm:** If you prefer pnpm, you can install it via npm:

    ```bash
    npm install -g pnpm
    ```

### Optional but Helpful Tools
* **Git:** Essential if you plan to version control your slides or use templates from GitHub.
* **Playwright/Chromium:** If you intend to export your slides to PDF or PNG,
    you will need to install Playwright to handle the rendering:

    ```bash
    npx playwright install chromium
    ```

### Quick Start Command
   Once Node.js is ready, you don't need to manually download a "SilDev" package.
   You can bootstrap a project directly:

   ```bash
   npm init slidev@latest
   ```

  This command will prompt you for a project name and automatically install all the necessary sub-dependencies
  (like Vite, Vue 3, and UnoCSS) into that folder.

### Slidev Skill for Claude Code
Since you are likely using the Claude Code CLI, the most streamlined way is to install it as a plugin/skill directly from a marketplace.
1. **Add the Marketplace:**
   If you haven't already, add the Anthropic/community marketplace:
   `/plugin marketplace add anthropics/claude-code`
1. **Install the Slidev Skill:**
   Search for and install the specific Slidev skill (often named `slidev-presentation-maker` or similar):
   `/plugin install slidev-presentation-maker@anthropics-claude-code`
1. **Reload Plugins:**
   Apply the changes to your current session:
   `/reload-plugins`

* [Slidev](https://sli.dev/)
* [GitHub: slidevjs/slidev](https://github.com/slidevjs/slidev/tree/main)

## Excalidraw
Generate architecture diagrams as `.excalidraw` files from codebase analysis,
with optional PNG and SVG export.

* [Excalidraw](https://excalidraw.com/)
* [Custom Claude Code Skill: Auto-Generating / Updating Architecture Diagrams with Excalidraw](https://yeefei.beehiiv.com/p/custom-claude-code-skill-auto-generating-updating-architecture-diagrams-with-excalidraw)
* [Excalidraw - Architecture Diagram Generator](https://github.com/ooiyeefei/ccc/tree/main/skills/excalidraw)

* [excalidraw-diagram](https://github.com/coleam00/excalidraw-diagram-skill/tree/main)
* [Build BEAUTIFUL Diagrams with Claude Code (Full Workflow)](https://www.youtube.com/watch?v=m3fqyXZ4k4I)
