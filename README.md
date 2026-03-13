# Nerve Block Atlas

Interactive web-based ultrasound-guided nerve block atlas for anaesthesia residents. Built as a single-page app with responsive portrait/landscape layouts optimised for phone use.

## Features

- **Layered sonoanatomy views** — toggle colour-coded anatomical structures on/off over ultrasound images
- **Multiple view types** — sonoanatomy, diagram, probe position, and reference views per block
- **Responsive layout** — portrait (stacked) and landscape (3-panel) modes
- **Hierarchical navigation** — hamburger menu organised by body region and block
- **Fast loading** — all images compressed to WebP

## Current content

- Brachial Plexus Interscalene (3 sono views, diagram, probe position)
- Upper & Lower Limb Sensory Innervation (6 reference pages)

## Adding new blocks

1. Capture screenshots from the source app using `scripts/screenshot_capture.sh`
2. Process layers: `python3 scripts/process_layers.py` (extracts overlay layers from screenshots)
3. Reprocess if needed: `python3 scripts/reprocess_v2.py` (crops and converts to WebP)
4. Rebuild the viewer: `python3 scripts/build_viewer_v3.py` (injects block data into index.html)

## Hosting

Served as a static site via GitHub Pages. Open `index.html` directly or visit the Pages URL.

## Tech

Single HTML file with inline CSS/JS. No build tools or frameworks required — just a browser.
