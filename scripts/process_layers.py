#!/usr/bin/env python3
"""
Process nerve block screenshots to extract overlay layers.
Takes a folder of sequential captures and produces:
- Cropped base images (WebP, lossy)
- Individual overlay layers as transparent WebP (lossless for alpha accuracy)
- Metadata JSON mapping layers to anatomical structure names

Output format: WebP for ~98% size reduction vs PNG.
Base images use lossy q=90 (photos/ultrasound). Overlays use lossless (preserves sharp alpha edges).
"""

import os
import json
import sys
import numpy as np
from PIL import Image

# Default crop constants (used as fallback)
CROP_LEFT = 259
CROP_TOP = 311
CROP_RIGHT = 2220
CROP_BOTTOM = 1865

# Right sidebar region for detecting which menu item is highlighted
SIDEBAR_LEFT = 2040
SIDEBAR_TOP = 130

# Diff threshold for detecting overlay changes
DIFF_THRESHOLD = 15

def load_image(path):
    """Load image as numpy array (RGB only)."""
    return np.array(Image.open(path).convert('RGB'))

def extract_overlay(base_arr, overlay_arr, threshold=DIFF_THRESHOLD):
    """
    Extract the overlay difference between base and overlay images.
    Returns an RGBA image where the overlay pixels are opaque and everything else is transparent.
    """
    diff = np.abs(base_arr.astype(int) - overlay_arr.astype(int))
    diff_mag = np.max(diff, axis=2)

    # Create mask of significantly changed pixels
    mask = diff_mag > threshold

    # Create RGBA output - overlay pixels with alpha
    h, w = overlay_arr.shape[:2]
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[:, :, :3] = overlay_arr
    result[:, :, 3] = mask.astype(np.uint8) * 255

    return result

def crop_to_ultrasound(arr, crop_box=None):
    """Crop array to just the ultrasound viewing area.
    crop_box: optional (left, top, right, bottom) tuple for per-view crops.
    """
    if crop_box:
        l, t, r, b = crop_box
        return arr[t:b, l:r]
    return arr[CROP_TOP:CROP_BOTTOM, CROP_LEFT:CROP_RIGHT]

def detect_highlighted_menu_item(base_arr, overlay_arr):
    """
    Detect which menu item is highlighted by looking at the right sidebar.
    Returns the approximate y-position of the highlighted item.
    """
    sidebar_base = base_arr[SIDEBAR_TOP:, SIDEBAR_LEFT:, :]
    sidebar_overlay = overlay_arr[SIDEBAR_TOP:, SIDEBAR_LEFT:, :]

    diff = np.abs(sidebar_base.astype(int) - sidebar_overlay.astype(int))
    diff_mag = np.max(diff, axis=2)

    # Find rows with significant changes in the sidebar
    changed_rows = np.any(diff_mag > 20, axis=1)
    if np.any(changed_rows):
        indices = np.where(changed_rows)[0]
        # Return the center of the changed region
        return (indices[0] + indices[-1]) // 2 + SIDEBAR_TOP
    return None

def process_nerve_block(folder_path, output_dir, image_ranges, block_name=None):
    """
    Process a nerve block folder.

    image_ranges: list of dicts, each with:
        - 'name': name of the view (e.g., 'Sonoanatomy 1')
        - 'type': 'layers' (default) or 'static'
        - 'base_index': index of the clean base image (int or str for special filenames)
        - 'overlay_indices': list of indices for overlay images
        - 'overlay_names': list of names for each overlay
        - 'crop_box': optional (left, top, right, bottom) per-view crop
    block_name: human-readable name (e.g. 'Brachial Plexus Interscalene')
    """
    os.makedirs(output_dir, exist_ok=True)

    metadata = {
        'block_id': os.path.basename(output_dir),
        'block_name': block_name if block_name else os.path.basename(output_dir).replace('_', ' ').title(),
        'source_folder': folder_path,
        'views': []
    }

    for view in image_ranges:
        view_name = view['name']
        view_dir = os.path.join(output_dir, view_name.lower().replace(' ', '_'))
        os.makedirs(view_dir, exist_ok=True)

        # Load and crop base image
        crop_box = view.get('crop_box', None)
        base_idx = view['base_index']
        if isinstance(base_idx, str):
            base_path = os.path.join(folder_path, f"capture_{base_idx}.png")
        else:
            base_path = os.path.join(folder_path, f"capture_{base_idx:04d}.png")
        base_full = load_image(base_path)
        base_cropped = crop_to_ultrasound(base_full, crop_box)

        # Save base image as lossy WebP (good for photos/ultrasound)
        base_out = os.path.join(view_dir, 'base.webp')
        Image.fromarray(base_cropped).save(base_out, format='WEBP', quality=90, method=6)
        base_kb = os.path.getsize(base_out) / 1024
        print(f"  Saved base: {view_name} ({base_kb:.0f} KB)")

        view_meta = {
            'name': view_name,
            'type': view.get('type', 'layers'),
            'base': 'base.webp',
            'layers': []
        }

        # Skip overlay processing for static views
        if view.get('type') == 'static':
            metadata['views'].append(view_meta)
            continue

        # Process each overlay
        for i, (idx, name) in enumerate(zip(view['overlay_indices'], view['overlay_names'])):
            overlay_path = os.path.join(folder_path, f"capture_{idx:04d}.png")
            if not os.path.exists(overlay_path):
                print(f"  WARNING: Missing image {overlay_path}")
                continue

            overlay_full = load_image(overlay_path)

            # Extract overlay for the ultrasound area only
            base_crop = crop_to_ultrasound(base_full, crop_box)
            overlay_crop = crop_to_ultrasound(overlay_full, crop_box)

            layer = extract_overlay(base_crop, overlay_crop)

            # Count non-transparent pixels
            non_transparent = np.sum(layer[:, :, 3] > 0)
            total_pixels = layer.shape[0] * layer.shape[1]
            coverage = non_transparent / total_pixels * 100

            # Save layer as lossless WebP (preserves sharp alpha edges)
            layer_filename = f"layer_{i+1:02d}_{name.lower().replace(' ', '_').replace('/', '_')}.webp"
            layer_path = os.path.join(view_dir, layer_filename)
            Image.fromarray(layer).save(layer_path, format='WEBP', lossless=True, method=6)
            layer_kb = os.path.getsize(layer_path) / 1024

            view_meta['layers'].append({
                'filename': layer_filename,
                'name': name,
                'coverage_pct': round(coverage, 2),
                'source_image': f"capture_{idx:04d}.png"
            })

            print(f"  Layer {i+1}: {name} ({coverage:.1f}% coverage, {layer_kb:.0f} KB)")

        metadata['views'].append(view_meta)

    # Save metadata
    meta_path = os.path.join(output_dir, 'metadata.json')
    with open(meta_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Print size summary
    total_bytes = 0
    for root, dirs, files in os.walk(output_dir):
        for fname in files:
            if fname.endswith('.webp'):
                total_bytes += os.path.getsize(os.path.join(root, fname))
    print(f"\nMetadata saved to {meta_path}")
    print(f"Total WebP output: {total_bytes / 1024:.0f} KB ({total_bytes / 1024 / 1024:.1f} MB)")
    return metadata

if __name__ == '__main__':
    print("Layer extraction module loaded. Use process_nerve_block() to process a folder.")
