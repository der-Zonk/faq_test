"""Builds index.json and creates a versioned snapshot + manifest.

This script scans `data/faq/*.md`, produces `index.json` (latest), writes
`versions/<version>.json` and updates `versions.json` manifest.

Version id is either provided via env BUILD_VERSION or derived from datetime+git sha.
"""
import os
import json
import glob
import subprocess
from datetime import datetime


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAQ_DIR = os.path.join(ROOT, 'data', 'faq')
OUT_INDEX = os.path.join(ROOT, 'index.json')
VERSIONS_DIR = os.path.join(ROOT, 'versions')
VERSIONS_MANIFEST = os.path.join(ROOT, 'versions.json')


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or not lines[0].strip().startswith('---'):
        return {}, text
    fm = {}
    i = 1
    while i < len(lines):
        if lines[i].strip() == '---':
            i += 1
            break
        line = lines[i]
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"')
        i += 1
    body = '\n'.join(lines[i:]).strip()
    return fm, body


def get_git_sha_short():
    # Prefer CI-provided GITHUB_SHA
    sha = os.environ.get('GITHUB_SHA')
    if sha:
        return sha[:7]
    try:
        out = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, stderr=subprocess.DEVNULL)
        return out.decode('utf-8').strip()
    except Exception:
        return 'unknown'


def build_index():
    items = []
    for path in sorted(glob.glob(os.path.join(FAQ_DIR, '*.md'))):
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        fm, body = parse_frontmatter(text)
        item = {
            'filename': os.path.basename(path),
            'id': fm.get('id'),
            'question': fm.get('question'),
            'category': fm.get('category'),
            'turn_order': fm.get('turn_order'),
            'date': fm.get('date'),
            'referenced_rules': fm.get('referenced_rules'),
            'change_log': fm.get('change_log'),
            'content': body[:10000]
        }
        items.append(item)

    # ensure versions dir exists
    os.makedirs(VERSIONS_DIR, exist_ok=True)

    # compute version id
    version = os.environ.get('BUILD_VERSION')
    if not version:
        now = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        sha = get_git_sha_short()
        version = f'{now}-{sha}'

    version_file = os.path.join(VERSIONS_DIR, f'{version}.json')

    # write index (latest)
    with open(OUT_INDEX, 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
    print('Wrote', OUT_INDEX)

    # write version snapshot (immutable)
    with open(version_file, 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
    print('Wrote', version_file)

    # update manifest
    manifest = []
    if os.path.exists(VERSIONS_MANIFEST):
        try:
            with open(VERSIONS_MANIFEST, 'r', encoding='utf-8') as fh:
                manifest = json.load(fh)
        except Exception:
            manifest = []

    # add new entry if commit/version not already present
    if not any(entry.get('version') == version for entry in manifest):
        entry = {
            'version': version,
            'date': datetime.utcnow().isoformat() + 'Z',
            'commit': get_git_sha_short(),
            'file': f'versions/{version}.json'
        }
        manifest.insert(0, entry)
        # keep only last 100 entries by default
        manifest = manifest[:100]
        with open(VERSIONS_MANIFEST, 'w', encoding='utf-8') as fh:
            json.dump(manifest, fh, ensure_ascii=False, indent=2)
        print('Updated', VERSIONS_MANIFEST)
    else:
        print('Version already present in manifest')


if __name__ == '__main__':
    build_index()
