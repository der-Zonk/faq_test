#!/usr/bin/env python3
"""Merge versions.json from gh-pages with newly built manifest.

Usage: python merge_versions.py <old_versions_file> <new_versions_file>
Writes merged result to <new_versions_file>.
"""
import json
import sys

def merge_versions(old_file, new_file):
    # Read current (newly built) manifest
    with open(new_file, 'r', encoding='utf-8') as f:
        new_manifest = json.load(f)

    # Read old manifest from gh-pages
    try:
        with open(old_file, 'r', encoding='utf-8') as f:
            old_manifest = json.load(f)
    except Exception as e:
        print(f"Could not read old manifest: {e}")
        old_manifest = []

    # Get the version id from the new manifest (should be first entry)
    new_version = new_manifest[0]['version'] if new_manifest else None

    # Merge: if new_version not in old_manifest, prepend it; else keep old
    if new_version and not any(e.get('version') == new_version for e in old_manifest):
        merged = new_manifest + old_manifest
    else:
        merged = old_manifest

    # Keep only last 100 versions
    merged = merged[:100]

    # Write merged manifest back to new_file
    with open(new_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    print(f"Merged manifest now has {len(merged)} versions")
    for v in merged[:5]:
        print(f"  - {v.get('version')} ({v.get('date')})")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: merge_versions.py <old_versions.json> <new_versions.json>")
        sys.exit(1)
    merge_versions(sys.argv[1], sys.argv[2])
