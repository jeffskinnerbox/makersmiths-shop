#!/usr/bin/env python3
"""
export-diagrams.py

Converts .excalidraw files to SVG or PNG by loading the official Excalidraw
library in a headless Chromium browser (via Playwright) and calling its built-in
export functions.

How it works:
  1. Builds a minimal in-memory HTML page that loads the Excalidraw UMD bundle
     from unpkg CDN.
  2. Playwright opens the page in headless Chromium.
  3. For each .excalidraw file, the script injects the JSON data into the page
     and calls ExcalidrawLib.exportToSvg() or ExcalidrawLib.exportToBlob().
  4. The resulting SVG string or PNG bytes are written to the output directory.

Requirements (run once):
  pip install playwright
  python3 -m playwright install chromium

  Internet access is required the first run to download the Excalidraw bundle
  from unpkg.com.  Playwright's Chromium caches the assets after that.

Usage:
  # Export all .excalidraw files in a directory to SVG (default)
  python3 export-diagrams.py --input diagrams/

  # Export to a specific output directory
  python3 export-diagrams.py --input diagrams/ --output assets/

  # Export a single file to PNG
  python3 export-diagrams.py --input diagrams/slide-01.excalidraw --format png

  # Export everything to PNG with dark-mode background
  python3 export-diagrams.py --input diagrams/ --format png --dark
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# The HTML page loaded by Playwright.
# It pulls the Excalidraw UMD bundle from unpkg, which exposes ExcalidrawLib
# as a global.  The bundle includes exportToSvg and exportToBlob utilities.
# React must be loaded first because the Excalidraw bundle depends on it.
_EXPORT_PAGE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>body {{ margin: 0; background: white; }}</style>
  <!-- React 18 UMD (required by Excalidraw bundle) -->
  <script crossorigin
    src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin
    src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <!-- Excalidraw UMD bundle — exposes ExcalidrawLib global -->
  <script
    src="https://unpkg.com/@excalidraw/excalidraw/dist/excalidraw.production.min.js">
  </script>
</head>
<body>
<script>
  // Expose a single async function that Playwright can call via page.evaluate().
  // data    — parsed .excalidraw JSON object
  // format  — "svg" | "png"
  // dark    — boolean, use dark background
  window.exportDiagram = async function(data, format, dark) {
    const {{ exportToSvg, exportToBlob }} = ExcalidrawLib;

    const opts = {{
      elements: data.elements || [],
      appState: {{
        exportWithDarkMode: dark,
        exportBackground: true,
        // Preserve the stored viewBackground from the .excalidraw file if present
        viewBackgroundColor: (data.appState || {{}}).viewBackgroundColor || '#ffffff',
      }},
      files: data.files || {{}},
    }};

    if (format === 'svg') {{
      const svgElement = await exportToSvg(opts);
      return svgElement.outerHTML;
    }} else {{
      const blob = await exportToBlob({{
        ...opts,
        mimeType: 'image/png',
        quality: 1,
      }});
      // Convert Blob → Uint8Array → plain Array so it survives the JS→Python bridge
      const buffer = await blob.arrayBuffer();
      return Array.from(new Uint8Array(buffer));
    }}
  }};

  // Signal to Playwright that the page is ready
  window.__excalidrawReady = true;
</script>
</body>
</html>
"""


def collect_input_files(inputs: list[str]) -> list[Path]:
    """Expand a list of file paths and directories into .excalidraw paths."""
    files = []
    for inp in inputs:
        p = Path(inp)
        if p.is_dir():
            files.extend(sorted(p.glob("**/*.excalidraw")))
        elif p.suffix == ".excalidraw" and p.exists():
            files.append(p)
        else:
            print(f"  [WARN] skipping {inp}: not a .excalidraw file or directory",
                  file=sys.stderr)
    return files


async def export_all(
    input_files: list[Path],
    output_dir: Path | None,
    fmt: str,
    dark: bool,
) -> None:
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        sys.exit(
            "playwright is not installed.\n"
            "Run:  pip install playwright && python3 -m playwright install chromium"
        )

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()

        # Load the export page (content, not a file URL, so no CORS issues)
        await page.set_content(_EXPORT_PAGE)

        # Wait until the Excalidraw bundle has initialised
        await page.wait_for_function("window.__excalidrawReady === true", timeout=30_000)

        for src in input_files:
            # Determine output path
            dest_dir = output_dir if output_dir else src.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / f"{src.stem}.{fmt}"

            # Read and parse the .excalidraw JSON
            try:
                data = json.loads(src.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                print(f"  [ERR ] {src}: {exc}", file=sys.stderr)
                continue

            # Call the in-page export function via Playwright's JS bridge
            result = await page.evaluate(
                "(args) => window.exportDiagram(args.data, args.format, args.dark)",
                {"data": data, "format": fmt, "dark": dark},
            )

            if fmt == "svg":
                dest.write_text(result, encoding="utf-8")
            else:
                dest.write_bytes(bytes(result))

            print(f"  {src}  →  {dest}")

        await browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input", "-i",
        nargs="+",
        required=True,
        metavar="PATH",
        help=".excalidraw file(s) or director(ies) to export",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="DIR",
        help="output directory (default: same directory as each input file)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["svg", "png"],
        default="svg",
        help="output format (default: svg)",
    )
    parser.add_argument(
        "--dark",
        action="store_true",
        help="export with dark background",
    )
    args = parser.parse_args()

    input_files = collect_input_files(args.input)
    if not input_files:
        sys.exit("No .excalidraw files found.")

    output_dir = Path(args.output) if args.output else None

    print(f"Exporting {len(input_files)} file(s) to {args.format.upper()}...")
    asyncio.run(export_all(input_files, output_dir, args.format, args.dark))
    print("Done.")


if __name__ == "__main__":
    main()
