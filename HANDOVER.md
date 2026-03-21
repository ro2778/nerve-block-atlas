# AnSo Content Extraction — Project Handover

Point a new Claude Code session at this folder and tell it to read `HANDOVER.md`.

## Project Goal

Extract ALL content (images, overlay layers, videos, notes) from the **AnSo** (Anaesthesia Sonoanatomy) Android app, then process those captures into cropped, compressed WebP images. Build an interactive nerve block atlas as a **mobile-first web app / PWA** where toolbar icons and layer toggle buttons are recreated in code, and only the actual image content (ultrasound scans, diagrams, photos) is extracted from the captures.

## User

An anaesthesia professional building a nerve block teaching atlas.

## Current Status (2026-03-21, evening)

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

### Phase 3: Web App / PWA Viewer — FUNCTIONAL, NEEDS POLISH
- `index.html` — Complete single-file PWA viewer
- `manifest.json` — Full data manifest (13 categories, 139 blocks, 658 views)
- `pwa-manifest.json` — PWA configuration with Nerve Block Atlas icon

**Viewer features implemented:**
- Dark medical theme matching AnSo app
- Navigation drawer with categories, favourites (localStorage), search
- Icon bar with **real extracted AnSo toolbar icons** (sono 1-5, landmark 1-2, ergonomics 1-3, innervation, video, notes) — active/inactive states with grey/white band backgrounds
- Image viewer with base + overlay layer compositing
- Layer controls with **colour-matched dots** (extracted from actual overlay images)
- Show Labels toggle for landmark views with sidebar text key display
- Notes panel with structured sections
- Video player
- Mirror mode, touch swipe navigation, keyboard shortcuts
- Responsive layout (portrait/landscape)
- PWA meta tags, service worker registration, safe area insets

### Phase 4: Remaining Work

1. **Video cropping** — Raw MP4s are full-screen recordings (2424x1080) that need cropping to the content area, similar to how images were cropped. Requires ffmpeg.

2. **Push to GitHub** — User mentioned previously hosting on GitHub Pages. Need to set up repo and push.

3. **Sensory innervation guides viewer** — These 7 blocks have a different UI pattern (single image with optional layers, no toolbar). The viewer handles them but they could use testing.

4. **Minor polish items:**
   - Some landmark sidebar text entries may still be incomplete for the last few categories (Airway, Lung signs, Echo) — the recapture script was stopped early but most were already correct
   - Innervation view "related blocks comparison" feature not implemented (shows other blocks' innervation for comparison)

## File Structure

```
AnSo capture/
├── index.html                 # PWA viewer (single file, all CSS/JS inline)
├── manifest.json              # Data manifest (categories, blocks, views, layers, notes)
├── pwa-manifest.json          # PWA configuration
├── icon-192.png               # PWA icon (Nerve Block Atlas)
├── icon-512.png               # PWA icon (large)
├── nerve block atlas icon.jpg # Source icon image
│
├── AnSo_Content/              # Raw captured data (3.7 GB) — DO NOT DELETE
│   ├── <Category>/
│   │   └── <Block>/
│   │       ├── <View>/
│   │       │   ├── base.png
│   │       │   ├── layer_01_<name>.png
│   │       │   └── sidebar_text.txt
│   │       ├── <Block>_notes/
│   │       │   ├── notes_text.txt
│   │       │   └── notes_page_*.png
│   │       └── metadata.json
│   └── ... (13 categories, 139 blocks)
│
├── processed/                 # Cropped WebP output
│   ├── <Category>/<Block>/<View>/
│   │   ├── base.webp          # Cropped base image (q95 lossy)
│   │   ├── overlay_*.webp     # Transparent overlays (lossless)
│   │   └── block_info.json    # View/layer metadata
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
│   └── recapture_landmark_keys.py  # Sidebar text recapture script
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

### `scripts/build_manifest.py` — Manifest generator

Reads `anso_app_structure.json` + `processed/` + `AnSo_Content/` to build `manifest.json`. Also extracts dominant colour from each overlay image for layer dot colour matching.

**Usage:**
```bash
python3 scripts/build_manifest.py
```

Output: 13 categories, 139 blocks, 658 views, 3,992 layers with colours, 101 notes, 206 sidebar texts, 24 videos.

### `scripts/recapture_landmark_keys.py` — Sidebar text recapture

Navigates AnSo app via adb, scrolls the right sidebar on each landmark view to capture complete abbreviation keys. Found and updated **37 landmark texts** that were previously truncated.

### Toolbar Icon Extraction

Icons were extracted by navigating to `Paediatric Plan A blocks > Penile nerves` (which has the most toolbar icons: 5 sono + 3 landmark + 3 ergonomics + innervation + notes). Each icon was captured in both active (white band bg) and inactive (grey band bg) states from raw toolbar screenshots. The video icon was captured separately from `Basic Sonoanatomy > Arteries`.

Icons are full band crops (not transparent) — dark grey icon lines on grey/white backgrounds. Embedded in `index.html` as base64 data URIs in the `APP_ICONS` object.

## AnSo App Structure

Each block has multiple **views** (left toolbar icons change the view):
- **Sonoanatomy views** (1-8): Ultrasound images with toggleable overlay layers
- **Landmark/pattern view** (1-3): Anatomy diagram with probe placement + abbreviation key
- **Ergonomics view** (1-3): Photo of hand/probe positioning
- **Innervation view**: Dermatome/nerve distribution diagram
- **Video view**: MP4 loop of scanning technique
- **Notes view**: Clinical notes (indications, positioning, volume, side effects, complications, tips)

**Sensory innervation guides** have a unique layout: single image view with optional layer buttons (no toolbar).

## Image Processing Details

- **Content boundaries:** Detected via brightness edge detection with sidebar exclusion
- **Overlay extraction:** `diff = abs(base - layer)`, threshold=12
- **WebP compression:** Base images q95 lossy, overlays lossless (transparency)
- **Layer colours:** Dominant non-white/non-black colour extracted from each overlay via numpy pixel analysis
- **Screen layout:** Landscape 2424x1080, toolbar x=173-310, title y=0-110, sidebar x>=1978

## Technical Environment

- **macOS Tahoe 26.0, MacBook Pro M5**
- **Python 3** with `Pillow` and `numpy`
- **Google Pixel 10** connected via USB with adb debugging
- **ADB** installed via Homebrew

## Quick Start for New Session

1. Read this file
2. Start the viewer: `cd "/Users/richardobyrne/Documents/Claude Projects/AnSo capture" && python3 -m http.server 8080`
3. Open `http://localhost:8080` to review the app
4. Key files to edit: `index.html` (viewer), `scripts/build_manifest.py` (data), `scripts/crop_and_extract.py` (image processing)
5. After changes: rebuild manifest with `python3 scripts/build_manifest.py`
