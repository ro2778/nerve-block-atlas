# AnSo Content Extraction — Project Handover

Point a new Claude Code session at this folder and tell it to read `HANDOVER.md`.

## Project Goal

Extract ALL content (images, overlay layers, videos, notes) from the **AnSo** (Anaesthesia Sonoanatomy) Android app, then process those captures into cropped, compressed WebP images. Build an interactive nerve block atlas as a **mobile-first web app / PWA** where toolbar icons and layer toggle buttons are recreated in code, and only the actual image content (ultrasound scans, diagrams, photos) is extracted from the captures.

## User

An anaesthesia professional building a nerve block teaching atlas.

## Current Status (2026-03-24)

### Phase 1: Content Capture — COMPLETE
- All 139 blocks captured via automated adb navigation
- Output: **5,008 PNG screenshots** (3.7 GB), **25 MP4 videos**, **307 text files** (notes)
- Stored in `AnSo_Content/` organised by category > block > view
- **Sensory innervation guides**: 7 blocks recaptured manually (6 simple images + 1 with 3 layers)

### Phase 2: Crop & Extract — v5.1 COMPLETE
- Final algorithm (v5.1) successfully crops all 658 views
- Output: `processed/` directory with cropped WebP base images + transparent overlay layers
- User reviewed and approved all crops

**Algorithm evolution:**
- v1-v3: Simple brightness edge detection, various threshold issues
- v4: Added `%black` jump + gap detection for sidebar boundary
- v4.1-v4.2: Fixed gap detection, added orientation marker detection, layer-based boundaries
- v5.0: Simplified to single robust approach: content-aware scan with `find_content_bbox()`
- v5.1: Fixed narrow ergonomics images (intermediate-brightness pixel detection threshold)

### Phase 3: Web App / PWA Viewer — LIVE at https://ro2778.github.io/nerve-block-atlas/
- `index.html` — Complete single-file PWA viewer (v1.2.2)
- `manifest.json` — Full data manifest (13 categories, 139 blocks, 658 views)
- `pwa-manifest.json` — PWA configuration with Nerve Block Atlas icon

**Viewer features implemented:**
- Dark medical theme matching AnSo app
- **Splash screen** with logo, version number, Open Atlas button, Install Atlas button (Android), iOS install hint
- **Auto-update system**: version.json check on splash screen, "Update Available" button, service worker auto-update via skipWaiting()
- Navigation drawer with categories, favourites (localStorage), search
- **Back navigation** via browser History API (block → submenu → main menu)
- Icon bar with **real extracted AnSo toolbar icons** (sono 1-5, landmark 1-2, ergonomics 1-3, innervation, video, notes) — active/inactive states with grey/white band backgrounds
- Image viewer with base + overlay layer compositing
- Layer controls with **colour-matched dots** (extracted from actual overlay images)
- **Innervation views** with Combine/Compare section headers, home block toggle with inverted visual state
- Show Labels toggle for landmark views with sidebar text key display
- Notes panel with structured sections (Indication, Positioning, Volume, Side Effects, Complications, Ultrasound Tips, Practical Tips)
- Video player with **auto-play** on view selection, cropped videos
- Mirror mode, touch swipe navigation, keyboard shortcuts
- Responsive layout (portrait/landscape)
- **Fullscreen mode** via JS Fullscreen API for installed PWA
- PWA meta tags, service worker, safe area insets, maskable icon (480x480)
- Rotation support (respects device auto-rotate setting)

### Phase 4: Innervation Layer Recapture — COMPLETE
- Recaptured innervation overlays for all 4 nerve categories (~80 blocks)
- New approach: deactivate home block first → capture `base_clean.png` (no layers) → capture each layer individually
- Overlay extraction: solid-colour fill with mask from diff (threshold 3), flat alpha 200
- Metadata captured: `innervation_meta.json` per block with Combine/Compare sections, home block flag
- Duplicate overlays from old captures cleaned up (38 stale files removed from 6 blocks)
- Interpectoral plane recaptured with correct block data

### Phase 5: Sidebar Text Recapture — COMPLETE
- Recaptured ALL 134 landmark sidebar texts by scrolling the right sidebar
- **37 texts updated** with previously missing entries (some had 6→14 entries)
- Key improvements: Lumbar plexus (shamrock) 6→14, Anterior quadratus lumborum 6→13, Cervical plexus (intermediate) 6→11

### Remaining Work

1. **Info page** — Credit AnSo app per their educational/non-commercial use terms
2. **Search refinement** — Better extraction of surgical terms from indications for "Find Block by Surgery" feature
3. **Video crop refinement** — Current crops are functional but could be tighter
4. **Innervation pixel quality** — Diff-based overlay approach loses some subtle pixels vs AnSo's native vector rendering. Acceptable but not pixel-perfect.

## Deployment

**GitHub Pages**: https://ro2778.github.io/nerve-block-atlas/
**Repository**: https://github.com/ro2778/nerve-block-atlas

### Version Update Process
1. Make code/data changes
2. Bump `APP_VERSION` in `index.html` and `version` in `version.json`
3. `git add -A && git commit && git push origin main`
4. GitHub Pages auto-deploys (1-2 min delay)
5. Installed PWAs auto-update via service worker, or splash screen shows "Update Available" button

## File Structure

```
AnSo capture/
├── index.html                 # PWA viewer (single file, all CSS/JS inline)
├── manifest.json              # Data manifest (categories, blocks, views, layers, notes)
├── pwa-manifest.json          # PWA configuration
├── version.json               # Version info for auto-update system
├── sw.js                      # Service worker for PWA caching
├── icon-192.png               # PWA icon
├── icon-512.png               # PWA icon (large)
├── icon-maskable-512.png      # Maskable icon for Android adaptive icons
├── nerve block atlas icon.jpg # Source icon image
│
├── AnSo_Content/              # Raw captured data (3.7 GB) — DO NOT DELETE
│   ├── <Category>/
│   │   └── <Block>/
│   │       ├── <View>/
│   │       │   ├── base.png
│   │       │   ├── base_clean.png      # (innervation only) no layers active
│   │       │   ├── base_home.png       # (innervation only) home block active
│   │       │   ├── layer_01_<name>.png
│   │       │   ├── sidebar_text.txt
│   │       │   └── innervation_meta.json  # (innervation only) section info
│   │       ├── <Block>_notes/
│   │       │   ├── notes_text.txt
│   │       │   └── notes_page_*.png
│   │       └── metadata.json
│   └── ... (13 categories, 139 blocks)
│
├── processed/                 # Cropped WebP output (~356 MB)
│   ├── <Category>/<Block>/<View>/
│   │   ├── base.webp          # Cropped base image (q95 lossy)
│   │   ├── overlay_*.webp     # Transparent overlays (lossless)
│   │   ├── crop_info.json     # Crop coordinates
│   │   └── block_info.json    # View/layer metadata
│   ├── <Category>/<Block>/video/
│   │   └── loop.mp4           # Cropped video
│   └── review.html            # Visual review page
│
├── icons/                     # Extracted toolbar icons
│   ├── toolbar_captures/      # Raw screenshots from phone
│   ├── sonoanatomy_[1-5]_[active|inactive].png
│   ├── landmark_[1-2]_[active|inactive].png
│   ├── ergonomics_[1-3]_[active|inactive].png
│   ├── innervation_[active|inactive].png
│   ├── video_[active|inactive].png
│   └── notes_[active|inactive].png
│
├── scripts/
│   ├── capture_all.py              # ADB automation (Phase 1) — reference only
│   ├── crop_and_extract.py         # Image processing (Phase 2)
│   ├── build_manifest.py           # Manifest generator (extracts overlay colours)
│   ├── recapture_landmark_keys.py  # Sidebar text recapture script
│   └── recapture_innervation.py    # Innervation layer recapture script
│
├── anso_app_structure.json    # All 139 blocks by category (source of truth)
├── HANDOVER.md                # THIS FILE
└── apk_extract/               # Extracted APK (no bundled images, Flutter+Firebase app)
```

## Key Scripts

### `scripts/crop_and_extract.py` — Image processing (Phase 2)

Detects content boundaries in raw screenshots, crops to content area, extracts transparent overlay layers.

**Usage:**
```bash
python3 scripts/crop_and_extract.py                    # process all
python3 scripts/crop_and_extract.py --block "Veins"    # process specific block
python3 scripts/crop_and_extract.py --review-only      # regenerate review HTML only
```

**Key details:**
- Handles two app layouts: old (TITLE_BOTTOM=110) and new (TITLE_BOTTOM=173, detected via grey status bar)
- Nav bar white line detection for new captures (y=1044-1055)
- Innervation overlays: solid-colour fill with diff mask (threshold 3, alpha 200)
- Uses `base_clean.png` for display base and diff reference on innervation views

### `scripts/build_manifest.py` — Manifest generator

Reads `anso_app_structure.json` + `processed/` + `AnSo_Content/` to build `manifest.json`. Also extracts dominant colour from each overlay image for layer dot colour matching. Reads `innervation_meta.json` for Combine/Compare section labels and home block identification.

**Usage:**
```bash
python3 scripts/build_manifest.py
```

Output: 13 categories, 139 blocks, 658 views, layers with colours, 101 notes, 207 sidebar texts, 24 videos.

### `scripts/recapture_innervation.py` — Innervation layer recapture

Navigates AnSo app via adb, captures clean base (home block off) + each layer individually with Combine/Compare section detection. Auto-scrolls sidebar to find all layers (slow swipe x=2200, 2000ms).

**Key features:**
- Deactivates home block first for clean base
- Detects Combine/Compare section headers in sidebar
- Auto-scrolls sidebar with slow swipe (2000ms duration)
- Manual scroll prompt system (bell chime + 5s wait) as fallback
- Saves `innervation_meta.json` with section labels and home block flag

### Toolbar Icon Extraction

Icons were extracted by navigating to `Paediatric Plan A blocks > Penile nerves` (which has the most toolbar icons: 5 sono + 3 landmark + 3 ergonomics + innervation + notes). Each icon was captured in both active (white band bg) and inactive (grey band bg) states from raw toolbar screenshots. The video icon was captured separately from `Basic Sonoanatomy > Arteries`.

Icons are full band crops (not transparent) — dark grey icon lines on grey/white backgrounds. Embedded in `index.html` as base64 data URIs in the `APP_ICONS` object.

## AnSo App Structure

Each block has multiple **views** (left toolbar icons change the view):
- **Sonoanatomy views** (1-8): Ultrasound images with toggleable overlay layers
- **Landmark/pattern view** (1-3): Anatomy diagram with probe placement + abbreviation key
- **Ergonomics view** (1-3): Photo of hand/probe positioning
- **Innervation view**: Dermatome/nerve distribution diagram with Combine (related blocks) and Compare (similar blocks) sections
- **Video view**: MP4 loop of scanning technique
- **Notes view**: Clinical notes (indications, positioning, volume, side effects, complications, tips)

**Sensory innervation guides** have a unique layout: single image view with optional layer buttons (no toolbar).

## Image Processing Details

- **Content boundaries:** Detected via brightness edge detection with sidebar exclusion
- **Overlay extraction (sono/landmark):** `diff = abs(base - layer)`, threshold=12
- **Overlay extraction (innervation):** Solid-colour fill + diff mask, threshold=3, flat alpha=200
- **WebP compression:** Base images q95 lossy, overlays lossless (transparency)
- **Layer colours:** Dominant non-white/non-black colour extracted from each overlay via numpy pixel analysis
- **Screen layout:** Landscape 2424x1080, toolbar x=173-310, title y=0-110 (old) or y=0-173 (new), sidebar x>=1978
- **Nav bar:** White gesture line at y=1044-1055 in new captures, detected and excluded from crop

## Technical Environment

- **macOS Tahoe 26.0, MacBook Pro M5**
- **Python 3** with `Pillow` and `numpy`
- **Google Pixel 10** connected via USB with adb debugging
- **ADB** installed via Homebrew
- **ffmpeg** for video cropping

## Quick Start for New Session

1. Read this file
2. Start the viewer: `cd "/Users/richardobyrne/Documents/Claude Projects/AnSo capture" && python3 -m http.server 8080`
3. Open `http://localhost:8080` to review the app
4. Key files to edit: `index.html` (viewer), `scripts/build_manifest.py` (data), `scripts/crop_and_extract.py` (image processing)
5. After changes: rebuild manifest with `python3 scripts/build_manifest.py`
6. To deploy: bump version in `index.html` + `version.json`, commit and push to GitHub

## Content Usage

AnSo app permits use of their images for **educational and non-commercial purposes**. An info/credits page should be added to the viewer acknowledging this.
