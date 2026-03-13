# Nerve Block Atlas Viewer — Methods

## Part 1: Screenshot Capture Method

### 1.1 Background

The AnSo (Anaesthesia Sonoanatomy) iPad app provides interactive ultrasound anatomy views with colour-coded anatomical structure overlays that can be toggled on and off. The app has no export or share functionality, so the content must be captured via sequential screenshots and then reconstructed programmatically.

### 1.2 App Structure Per Nerve Block

Each nerve block in AnSo has five views accessible from the left sidebar:

1. **Sonoanatomy 1, 2, 3** — Three ultrasound cross-section views at different anatomical levels. Each has a right sidebar with toggleable colour-coded overlays for individual anatomical structures (e.g. "C5 Nerve Root", "Anterior Scalene", "Internal Jugular Vein").
2. **Diagram** — An anatomical line drawing. By default shown unlabelled; a single toggle in the right sidebar shows/hides abbreviation labels (e.g. SCM, IJV, CA, N, AS, MS).
3. **Probe Position (Ergonomics)** — A photograph showing correct probe placement on the patient. No overlays or toggles.

### 1.3 Capture Procedure

Screenshots are captured sequentially using the iPhone's built-in accessibility feature (e.g. AssistiveTouch or Back Tap mapped to screenshot). The captures must follow a strict order.

**For each Sonoanatomy view (1, 2, 3):**

1. Navigate to the view. Ensure all overlays are OFF.
2. Capture the **base image** (clean ultrasound, no overlays).
3. Toggle ON the first overlay in the right sidebar. Capture a screenshot.
4. Toggle OFF the first overlay. Toggle ON the next overlay. Capture.
5. Repeat for every overlay in the sidebar, always returning to the clean base between each.

**Critical rule:** Each overlay screenshot must show exactly ONE overlay active against the clean base. The processing script computes the pixel difference between each overlay image and the base to extract just that overlay's contribution.

**For the Diagram view:**

1. Navigate to the Diagram view with labels hidden (the default state).
2. Capture the base image (unlabelled diagram).
3. Toggle labels ON. Capture the labelled version.

**For the Probe Position view:**

Capture a single screenshot. There are no overlays.

### 1.4 File Naming Convention

Screenshots are saved to a numbered folder (one per nerve block) under `ScreenCaptures/`. The iPhone names them sequentially as `capture_0001.png`, `capture_0002.png`, etc. The numbering reflects capture order.

For supplementary captures (e.g. a missing base diagram captured later), name the file to sort near its related images, e.g. `capture_00072_base.png` for a diagram base associated with `capture_0072.png`.

### 1.5 Image Specifications

All screenshots from the iPad app are **3024 × 1964 pixels** (landscape). The app layout consists of a fixed frame:

| Zone | Position | Notes |
|------|----------|-------|
| Left sidebar icons | x = 0–172 | Grey/white view selector icons, pixel-identical across views |
| Sidebar–content gap | x = 173–185 | Always black (zero brightness) |
| Title bar | y = 165–310 | Shows nerve block name and current view title |
| Title–content gap | y ≈ 311–395 | Black gap (variable height per view) |
| Right sidebar | x ≈ 2275+ | Overlay toggle buttons. Absent on Probe Position view |
| Main content area | Variable | Different size in each view (see crop boundaries) |

---

## Part 2: Image Processing Pipeline

### 2.1 Overview

The processing pipeline takes the raw sequential screenshots and produces cropped, transparent PNG overlay layers that can be composited in a web viewer. The core technique is **pixel differencing**: for each overlay screenshot, the script computes the absolute difference from the base image and extracts pixels that exceed a brightness threshold.

### 2.2 Processing Scripts

**`process_layers.py` — Core Processing Module**

Provides the reusable functions:

- `load_image(path)` — Loads a PNG as a NumPy RGB array.
- `crop_to_ultrasound(arr, crop_box)` — Crops an image array to the specified content area. Accepts an optional `(left, top, right, bottom)` tuple for per-view crop coordinates.
- `extract_overlay(base, overlay, threshold=15)` — Computes the per-pixel absolute difference between base and overlay arrays. Pixels where the maximum channel difference exceeds the threshold (default 15) are kept; all other pixels become fully transparent. Returns an RGBA array.
- `process_nerve_block(folder, output_dir, image_ranges)` — Main entry point. Takes a list of view definitions (each specifying base image index, overlay indices, overlay names, and crop_box) and produces cropped PNGs and `metadata.json`.

**`reprocess_v2.py` — View Configuration**

Defines the specific image mappings for each nerve block. For the Brachial Plexus Interscalene block, it maps capture file indices to view names and overlay names, with per-view crop coordinates. Running this script invokes `process_nerve_block()` to produce all outputs.

**`build_viewer_v3.py` — HTML Viewer Builder**

Reads the processed outputs (base PNGs + overlay PNGs + metadata.json), Base64-encodes all images, and generates a single self-contained HTML file. The viewer uses CSS opacity toggling with absolute-positioned overlay images stacked on top of the base.

### 2.3 Crop Boundary Detection

This is the most critical part of the pipeline. Each view in the AnSo app has a **different content area size** within the same 3024 × 1964 frame. The crop must precisely isolate the content, excluding the left sidebar icons, title bar, and right sidebar toggles.

**Per-View Crop Boundaries (Brachial Plexus Interscalene):**

| View | Left | Top | Right | Bottom | Content Size |
|------|------|-----|-------|--------|-------------|
| Sonoanatomy 1 | 259 | 311 | 2220 | 1865 | 1961 × 1554 |
| Sonoanatomy 2 | 190 | 445 | 2262 | 1713 | 2072 × 1268 |
| Sonoanatomy 3 | 229 | 309 | 2204 | 1866 | 1975 × 1557 |
| Diagram | 186 | 396 | 2275 | 1778 | 2089 × 1382 |
| Probe Position | 573 | 311 | 2908 | 1864 | 2335 × 1553 |

**Detection Method:**

1. Convert image to brightness array: `max(R, G, B)` per pixel.
2. Compute **column coverage**: for each column x, what percentage of rows have brightness > 25.
3. Compute **row coverage**: for each row y (within the main content x-range), what percentage of columns have brightness > 25.
4. **Left boundary**: Find the gap between left sidebar (x ≤ 172) and content start. The left sidebar always drops to 0% coverage at x ≈ 173, then content jumps to high coverage. The first column with ≥ 90% coverage after x = 173 is the left boundary.
5. **Right boundary**: Find where column coverage drops from high (>90%) to low (<50%), indicating the start of the right sidebar or end of content.
6. **Top boundary**: Find the first row with >90% coverage after the title bar gap (y > 310).
7. **Bottom boundary**: Find the last row with >90% coverage.

**Special Cases and Priority Rules:**

- **Ant./Post. labels**: In Sonoanatomy views 1 and 3, the anatomical orientation labels "Ant." and "Post." extend beyond the ultrasound scan area into black space. The crop boundary must be widened to include these labels, as they define the left, right, and top boundaries.
- **Sono 2 offset**: Sonoanatomy 2 has a significantly different layout — the ultrasound image starts lower (y = 445 vs ≈ 310) and the left edge extends further left (x = 190). The "Colour All" overlay in Sono 2 also bleeds into the right sidebar (an artefact of the original app).
- **Probe Position**: This view has no right sidebar. The photograph extends from x = 573 to x = 2908 (much wider than other views). The area between the left sidebar and the photo (x = 173–572) is black.
- **Scale bar**: Sonoanatomy views have a thin horizontal scale bar at approximately y = 290–310 with brightness ≈ 180, spanning x ≈ 200–2199. This sits within the title bar zone and is excluded by the crop.

### 2.4 Overlay Extraction Algorithm

For each overlay image against the base:

```
diff = abs(base_pixel - overlay_pixel)    # per channel
max_diff = max(diff_R, diff_G, diff_B)
if max_diff > 15: keep overlay pixel (alpha = 255)
else: transparent (alpha = 0)
```

The threshold of 15 was determined empirically to reject JPEG compression noise while retaining subtle overlay edges. The output is a transparent PNG where only the overlay's contribution is visible.

### 2.5 Output Format

Images are saved as **WebP** instead of PNG for dramatic size reduction (~98% smaller).

- **Base images**: lossy WebP, quality 90. These are ultrasound scans and photographs where minor lossy artefacts are invisible.
- **Overlay layers**: lossless WebP. These have sharp alpha edges (binary transparency from the diff threshold) that must be preserved exactly.

Size comparison for one nerve block (Brachial Plexus Interscalene, 68 images):

| Format | Total size | Notes |
|--------|-----------|-------|
| PNG | 85 MB | Original approach |
| WebP lossless (all) | 11 MB | Safe but larger |
| WebP mixed (lossy bases + lossless overlays) | **7.1 MB** | Current approach |
| Projected 100 blocks (WebP mixed) | ~710 MB | Feasible for a PWA |

### 2.6 Viewer Architecture

The viewer is a lightweight `index.html` file (~23 KB) with no external dependencies. It loads images on demand from the `processed/` folder via relative paths. The build script (`build_viewer_v3.py`) scans all `metadata.json` files in `processed/` and generates the HTML with the block/view/layer data inlined as JSON — but the **image data itself is not embedded**. Images are fetched by the browser as standard HTTP requests when a view is opened.

The UI is mobile-first (stacked layout: image on top, controls below on phones; side-by-side on tablets/desktop). It uses CSS absolute positioning to stack transparent overlay images on top of the base. Each overlay's visibility is toggled by switching between `opacity: 0` and `opacity: 1`.

Anatomical structures are colour-coded in the layer list: yellow for nerves, red for arteries/muscles, blue for veins, grey for bone, green for local anaesthetic, white for needle path, and a gradient for "Colour All."

To serve locally: `python3 -m http.server 8080` from the project root. For phone testing, use the Mac's local IP address on the same Wi-Fi network.
