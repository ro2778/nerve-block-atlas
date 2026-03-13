#!/usr/bin/env python3
"""
Configuration and runner for Brachial Plexus Interscalene (folder 2).
Processes all 5 views: Sonoanatomy 1/2/3, Diagram, Probe Position.
Outputs WebP images to processed/brachial_plexus_interscalene/
"""

import sys
import os

# Resolve paths relative to project root (one level up from scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts'))
from process_layers import process_nerve_block

folder = os.path.join(PROJECT_ROOT, 'ScreenCaptures', '2')
output = os.path.join(PROJECT_ROOT, 'processed', 'brachial_plexus_interscalene')

image_ranges = [
    {
        'name': 'Sonoanatomy 1',
        'type': 'layers',
        'base_index': 6,
        'overlay_indices': list(range(7, 31)),
        'overlay_names': [
            'Colour All', 'Needle Path', 'LA',
            'C5 Nerve Root', 'C6 Nerve Root', 'C7 Nerve Root',
            'Carotid Artery', 'Internal Jugular Vein',
            'Anterior Scalene', 'Middle Scalene', 'Sternocleidomastoid',
            'C7 Vertebrae', 'Vertebral Artery', 'Vertebral Vein',
            'Phrenic Nerve', 'Transverse Cervical Artery', 'Vagus Nerve',
            'Longus Colli', 'Platysma', 'Omohyoid',
            'Longissimus Cervicis', 'Posterior Scalene',
            'Cervical Sympathetic Chain', 'Thyroid'
        ],
        'crop_box': (259, 311, 2220, 1865),
    },
    {
        'name': 'Sonoanatomy 2',
        'type': 'layers',
        'base_index': 31,
        'overlay_indices': list(range(32, 52)),
        'overlay_names': [
            'Colour All', 'Needle Path', 'LA',
            'C5 Nerve Root', 'C6 Nerve Root Divided', 'C7 Nerve Root',
            'Anterior Scalene', 'Middle Scalene',
            'Carotid Artery', 'Internal Jugular Vein',
            'C7 Transverse Process', 'Vertebral Artery and Vein',
            'Phrenic Nerve', 'Sternocleidomastoid', 'Platysma',
            'Longus Colli', 'Vagus Nerve', 'Cervical Sympathetics',
            'Deep Cervical Muscles', 'Levator Scapulae'
        ],
        'crop_box': (190, 445, 2262, 1713),
    },
    {
        'name': 'Sonoanatomy 3',
        'type': 'layers',
        'base_index': 52,
        'overlay_indices': list(range(53, 71)),
        'overlay_names': [
            'Colour All', 'Needle Path', 'LA',
            'C5 Nerve Root', 'C6 Nerve Root', 'C7 Nerve Root',
            'Anterior Scalene', 'Middle Scalene',
            'Carotid Artery', 'Internal Jugular Vein',
            'C7 Vertebrae', 'Vertebral Artery and Vein',
            'Phrenic Nerve', 'Sternocleidomastoid', 'Platysma',
            'Longus Colli', 'Vagus Nerve', 'Longissimus Cervicis'
        ],
        'crop_box': (229, 309, 2204, 1866),
    },
    {
        'name': 'Diagram',
        'type': 'layers',
        'base_index': '00072_base',  # Supplementary capture (unlabelled)
        'overlay_indices': [72],
        'overlay_names': ['Labels'],
        'crop_box': (186, 396, 2275, 1778),
    },
    {
        'name': 'Probe Position',
        'type': 'static',
        'base_index': 73,
        'overlay_indices': [],
        'overlay_names': [],
        'crop_box': (573, 311, 2908, 1864),
    },
]

print("Processing Brachial Plexus Interscalene (folder 2)")
print("=" * 50)
for v in image_ranges:
    n_overlays = len(v['overlay_names'])
    label = f"{n_overlays} overlays" if n_overlays else "static"
    print(f"  {v['name']}: crop={v['crop_box']}, {label}")
print()

metadata = process_nerve_block(
    folder, output, image_ranges,
    block_name='Brachial Plexus Interscalene'
)

print("\nDone! Summary:")
for view in metadata['views']:
    print(f"  {view['name']}: {len(view['layers'])} layers")
