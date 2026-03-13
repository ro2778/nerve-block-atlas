# Nerve Block Atlas Viewer — Session Handover

This document provides all context needed for a new Cowork/Claude session to continue this project. Point the new session at this folder and tell it to read HANDOVER.md.

## Project Goal

Build an interactive nerve block atlas as a mobile-first web app for hospital anaesthesia residents. The atlas replicates the functionality of the AnSo iPad app (which has no export capability) by extracting overlay layers from sequential screenshots and presenting them in a web viewer with toggle controls.

## Current Status

- **Completed**: Brachial Plexus Interscalene (folder 2) — all 5 views processed as WebP images and working in the lightweight HTML viewer (Sono 1, 2, 3, Diagram with label toggle, Probe Position).
- **Remaining**: 20 more nerve block folders to process (folders 1, 3–21). Additional app sections not yet captured: Lower Limb Nerves, Head Neck and Trunk Nerves, Vascular Access, Airway and Gastric Antrum, Lumbar Spine.
- **Future**: Convert to a Next.js PWA with navigation, search, and offline support once all blocks are processed.

## Architecture

The project uses a **separate-files approach** — images are stored as individual WebP files and loaded on demand by a lightweight HTML viewer. This replaced an earlier base64-embedded approach that produced a 113 MB HTML file for a single nerve block.

**Why WebP?** The overlay layers are mostly transparent (often >95% transparent pixels). PNG stores these as ~1 MB each; WebP compresses them to 10–30 KB. For the Brachial Plexus Interscalene block: PNG total was 85 MB, WebP total is 7.1 MB. At 100 nerve blocks, that's the difference between ~8.5 GB (impractical) and ~710 MB (manageable, fits on a phone as a PWA).

**Image format details:**
- Base images: lossy WebP, quality 90 (photos/ultrasound — no visible quality loss)
- Overlay layers: lossless WebP (preserves sharp alpha edges for accurate structure outlines)

## Dependencies

- **Python 3** with `numpy` and `Pillow` (PIL). These are the only dependencies for processing.
- **scipy is NOT available** in the Cowork environment — use PIL's `ImageFilter.BoxBlur` if smoothing is needed.
- No Node.js or build tools required. The viewer is a single HTML file served by any static HTTP server.

## Project Folder Structure

```
nerve_block_atlas/
├── HANDOVER.md                  ← You are here
├── METHODS.md                   ← Detailed capture & processing methods
├── index.html                   ← Lightweight viewer (23 KB, loads images on demand)
├── scripts/
│   ├── process_layers.py        ← Core module: load, crop, diff, extract overlays → WebP
│   ├── reprocess_v2.py          ← Config for Brachial Plexus Interscalene (all 5 views)
│   ├── build_viewer_v3.py       ← Builds index.html from processed/ metadata
│   └── screenshot_capture.sh    ← macOS bash script for capturing from QuickTime mirror
├── ScreenCaptures/              ← Raw screenshots from iPad app
│   ├── 1/                       ← Folder per nerve block
│   ├── 2/                       ← Brachial Plexus Interscalene (73 + 1 images)
│   ├── 3/ ... 21/               ← Remaining nerve blocks (not yet processed)
│   └── ...
└── processed/
    └── brachial_plexus_interscalene/
        ├── metadata.json        ← View definitions, layer filenames, coverage %
        ├── sonoanatomy_1/       ← base.webp + 24 layer WebPs
        ├── sonoanatomy_2/       ← base.webp + 20 layer WebPs
        ├── sonoanatomy_3/       ← base.webp + 18 layer WebPs
        ├── diagram/             ← base.webp + layer_01_labels.webp
        └── probe_position/      ← base.webp (static, no overlays)
```

## How the Scripts Work

All scripts use **relative paths** from the project root. Run them from anywhere — they resolve paths from their own location.

**`scripts/process_layers.py`** — Core processing module. Key functions:
- `crop_to_ultrasound(arr, crop_box)` — Crops to content area using `(left, top, right, bottom)` tuple
- `extract_overlay(base, overlay, threshold=15)` — Pixel diffs base vs overlay, outputs transparent RGBA array
- `process_nerve_block(folder, output_dir, image_ranges, block_name)` — Main entry point. Saves base images as lossy WebP (q=90) and overlays as lossless WebP. Generates `metadata.json`.

**`scripts/reprocess_v2.py`** — Configuration for Brachial Plexus Interscalene. Defines all 5 views: image indices, overlay names, per-view crop_box tuples, and view types (layers/static). Run: `python3 scripts/reprocess_v2.py`

**`scripts/build_viewer_v3.py`** — Scans `processed/` for all `metadata.json` files, builds a single `index.html` that references images via relative paths. The viewer auto-discovers all processed blocks. Run: `python3 scripts/build_viewer_v3.py`

**`scripts/screenshot_capture.sh`** — macOS script for capturing screenshots from QuickTime Player mirroring the iPhone. Controls: ENTER to pause/resume, q to quit. Saves to `ScreenCaptures/` with sequential numbering.

## Local Testing

```bash
cd <project_root>
python3 -m http.server 8080
```

Open `http://localhost:8080` on your computer. To test on a phone, find your Mac's local IP (System Settings → Wi-Fi → Details → IP Address) and open `http://<your-ip>:8080` — both devices must be on the same Wi-Fi network.

## Image Index Mapping (Folder 2)

| Images | View | Type | Overlays |
|--------|------|------|----------|
| 1–5 | Main Menu | App menu (not usable) | — |
| 6 | Sonoanatomy 1 | Base | — |
| 7–30 | Sonoanatomy 1 | Overlays | 24 layers |
| 31 | Sonoanatomy 2 | Base | — |
| 32–51 | Sonoanatomy 2 | Overlays | 20 layers |
| 52 | Sonoanatomy 3 | Base | — |
| 53–70 | Sonoanatomy 3 | Overlays | 18 layers |
| 71 | Sonoanatomy 3 | Last overlay state | — |
| 72 | Diagram | Labelled version | — |
| 00072_base | Diagram | Unlabelled base (supplementary capture) | — |
| 73 | Probe Position | Static photo | — |

## Key Technical Parameters

- **Diff threshold**: 15 (max channel difference). Rejects compression noise, retains overlay edges.
- **Left sidebar**: x = 0–172. Always exclude from content crop.
- **Sidebar–content gap**: x = 173–185. Always black.
- **Title bar**: y = 165–310. Pixel-identical between base and overlay; excluded from crop.
- **Right sidebar**: x ≥ 2275 typically. Contains toggle buttons. Absent on Probe Position.
- **App frame**: All images are 3024 × 1964 px. The title bar and left sidebar are pixel-identical across views within a nerve block.

## Per-View Crop Boundaries (Brachial Plexus Interscalene)

| View | crop_box (L, T, R, B) | Notes |
|------|----------------------|-------|
| Sonoanatomy 1 | (259, 311, 2220, 1865) | Ant./Post. labels define boundaries |
| Sonoanatomy 2 | (190, 445, 2262, 1713) | Content starts lower; left edge extends further |
| Sonoanatomy 3 | (229, 309, 2204, 1866) | Ant./Post. labels extend beyond scan area |
| Diagram | (186, 396, 2275, 1778) | Drawing only, title bar excluded |
| Probe Position | (573, 311, 2908, 1864) | No right sidebar; photo offset right |

## Known Issues and Gotchas

1. **Each sonoanatomy view has DIFFERENT crop boundaries.** The ultrasound image size varies per view. Never assume one crop fits all.
2. **Sono 2's "Colour All" overlay bleeds into the right sidebar.** This is an artefact from the original app, not a processing error.
3. **Ant./Post. orientation labels** in some views extend beyond the ultrasound scan into black space. Crop boundaries must be widened to include them.
4. **Images 2–5 in the Brachial Plexus folder are the Main Menu** captured with a dim screen during app loading. They are not Diagram captures.
5. **The diagram's unlabelled base was not captured in the original session.** It was added later as `capture_00072_base.png`. Future nerve blocks should capture both diagram states in sequence.
6. **scipy is not available** in the Cowork environment. Use PIL's `ImageFilter.BoxBlur` instead of `scipy.ndimage.uniform_filter` if smoothing is needed.
7. **`base_index` can be a string** for special filenames (e.g. `'00072_base'` for the supplementary diagram capture). The processing script handles both int and str.

## Processing a New Nerve Block

To process a new folder (e.g. folder 3):

1. Examine the first few images to identify the base image for each view (the one with no overlays active).
2. Count the overlays per view by looking at the capture sequence.
3. Identify overlay names by examining the right sidebar text in each overlay screenshot.
4. Run crop boundary detection on each view's base image (column/row coverage analysis — see METHODS.md for the algorithm).
5. Create a config script (like `scripts/reprocess_v2.py`) with the image ranges, overlay names, `crop_box` tuples, and view types. Include all 5 views (Sono 1/2/3, Diagram, Probe Position) in a single script.
6. Run the script to generate WebP outputs in `processed/<block_name>/`.
7. Run `python3 scripts/build_viewer_v3.py` to rebuild `index.html` — it auto-discovers all blocks in `processed/`.
8. Visually verify each view: `python3 -m http.server 8080` then open `http://localhost:8080`.

## Overlay Name Lists (Folder 2 Reference)

### Sonoanatomy 1 (24 overlays)
Colour All, Needle Path, LA, C5 Nerve Root, C6 Nerve Root, C7 Nerve Root, Carotid Artery, Internal Jugular Vein, Anterior Scalene, Middle Scalene, Sternocleidomastoid, C7 Vertebrae, Vertebral Artery, Vertebral Vein, Phrenic Nerve, Transverse Cervical Artery, Vagus Nerve, Longus Colli, Platysma, Omohyoid, Longissimus Cervicis, Posterior Scalene, Cervical Sympathetic Chain, Thyroid

### Sonoanatomy 2 (20 overlays)
Colour All, Needle Path, LA, C5 Nerve Root, C6 Nerve Root Divided, C7 Nerve Root, Anterior Scalene, Middle Scalene, Carotid Artery, Internal Jugular Vein, C7 Transverse Process, Vertebral Artery and Vein, Phrenic Nerve, Sternocleidomastoid, Platysma, Longus Colli, Vagus Nerve, Cervical Sympathetics, Deep Cervical Muscles, Levator Scapulae

### Sonoanatomy 3 (18 overlays)
Colour All, Needle Path, LA, C5 Nerve Root, C6 Nerve Root, C7 Nerve Root, Anterior Scalene, Middle Scalene, Carotid Artery, Internal Jugular Vein, C7 Vertebrae, Vertebral Artery and Vein, Phrenic Nerve, Sternocleidomastoid, Platysma, Longus Colli, Vagus Nerve, Longissimus Cervicis

### Diagram (1 overlay)
Labels (abbreviations: N, SCM, AS, MS, IJV, CA)
