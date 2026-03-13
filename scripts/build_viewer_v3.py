#!/usr/bin/env python3
"""
Build the Nerve Block Atlas viewer by injecting processed block data
into the HTML template (index.html).

The script:
1. Scans processed/*/metadata.json for available blocks
2. Fixes up image paths to be relative from project root
3. Replaces the BLOCKS JSON in index.html with the discovered data

Output: Updated index.html in project root
Usage: python3 scripts/build_viewer_v3.py
Then:  cd <project_root> && python3 -m http.server 8080
"""

import os
import json
import glob
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, 'processed')
HTML_PATH = os.path.join(PROJECT_ROOT, 'index.html')

# Discover all processed blocks
blocks = []
for meta_path in sorted(glob.glob(os.path.join(PROCESSED_DIR, '*/metadata.json'))):
    with open(meta_path) as f:
        meta = json.load(f)
    block_dir = os.path.basename(os.path.dirname(meta_path))
    # Fix up paths to be relative from project root
    for view in meta['views']:
        view_dir = view['name'].lower().replace(' ', '_')
        view['base'] = f"processed/{block_dir}/{view_dir}/{view['base']}"
        for layer in view['layers']:
            layer['filename'] = f"processed/{block_dir}/{view_dir}/{layer['filename']}"
    blocks.append(meta)
    print(f"  Found: {meta.get('block_name', block_dir)} ({len(meta['views'])} views)")

if not blocks:
    print("No processed blocks found. Run a processing script first.")
    exit(1)

# Read existing HTML
with open(HTML_PATH, 'r') as f:
    html = f.read()

# Replace the BLOCKS JSON assignment
blocks_json = json.dumps(blocks, separators=(',', ':'))
# Match: const BLOCKS = [...]; (the JSON array on one line)
pattern = r'(const BLOCKS = )\[.*?\];'
replacement = f'\\1{blocks_json};'
new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)

if count == 0:
    print("ERROR: Could not find 'const BLOCKS = [...]' in index.html")
    print("Make sure index.html contains the BLOCKS declaration.")
    exit(1)

with open(HTML_PATH, 'w') as f:
    f.write(new_html)

file_size = os.path.getsize(HTML_PATH) / 1024
print(f"\nViewer updated: {HTML_PATH}")
print(f"File size: {file_size:.1f} KB")
print(f"Blocks: {len(blocks)}")
for b in blocks:
    print(f"  - {b.get('block_name', b['block_id'])} ({len(b['views'])} views)")
print(f"\nTo test locally:")
print(f"  cd {PROJECT_ROOT}")
print(f"  python3 -m http.server 8080")
print(f"  Open http://localhost:8080")
