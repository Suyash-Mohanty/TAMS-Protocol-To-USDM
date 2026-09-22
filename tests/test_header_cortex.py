"""Test header analysis with Cortex vision."""
import json
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

from extraction.header_analyzer import analyze_soa_headers, save_header_structure

# Use existing SoA images from a previous run
SOA_IMAGES_DIR = 'output/NCT05999994_Eli-Lilly-and-Company_J1S-MC-JAAA_b_20260902_122522'
OUTPUT_DIR = 'output/test_cortex_header'

# Find SoA images
image_paths = []
if os.path.exists(SOA_IMAGES_DIR):
    for f in sorted(os.listdir(SOA_IMAGES_DIR)):
        if f.startswith('soa_page_') and f.endswith('.png'):
            image_paths.append(os.path.join(SOA_IMAGES_DIR, f))

print(f"Found {len(image_paths)} SoA images")
print("Running header analysis with Cortex...")

result = analyze_soa_headers(
    image_paths=image_paths,
    model_name="cortex",
)

if result.success:
    print(f"\n✓ Success! Found:")
    print(f"  - {len(result.structure.epochs)} epochs")
    print(f"  - {len(result.structure.encounters)} encounters")
    print(f"  - {len(result.structure.activityGroups)} activity groups")

    # Show activity groups
    print("\n=== Activity Groups ===")
    for g in result.structure.activityGroups:
        print(f"  {g.name}: {len(g.activity_names)} activities")
        if g.activity_names:
            print(f"    Sample: {g.activity_names[:3]}")

    # Save result
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, '4_header_structure.json')
    save_header_structure(result.structure, output_path)
    print(f"\n✓ Saved to: {output_path}")
else:
    print(f"\n✗ Failed: {result.error}")
