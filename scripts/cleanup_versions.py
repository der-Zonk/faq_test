#!/usr/bin/env python3
"""Remove duplicate entries from versions.json."""
import json
import sys

def cleanup_versions(file_path):
    # Read current manifest
    with open(file_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    print(f"Original manifest has {len(manifest)} entries")
    
    # Remove duplicates based on version field, keeping first occurrence
    seen = set()
    cleaned = []
    for entry in manifest:
        version = entry.get('version')
        if version and version not in seen:
            seen.add(version)
            cleaned.append(entry)
        else:
            print(f"Removing duplicate: {version}")
    
    print(f"Cleaned manifest has {len(cleaned)} entries")
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    
    print(f"Cleaned {file_path}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: cleanup_versions.py <versions.json>")
        sys.exit(1)
    cleanup_versions(sys.argv[1])
