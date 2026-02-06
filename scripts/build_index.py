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
    """Parse YAML-like frontmatter with support for multiline blocks (|)."""
    lines = text.splitlines()
    if not lines or not lines[0].strip().startswith('---'):
        return {}, text
    
    fm = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        
        # End of frontmatter block
        if line.strip() == '---':
            i += 1
            break
        
        # Skip empty lines or lines without colons
        if ':' not in line:
            i += 1
            continue
        
        # Parse key: value
        k, v = line.split(':', 1)
        k = k.strip()
        v = v.strip()
        
        # Check for multiline block indicator
        if v == '|':
            # Collect multiline block (lines starting with 2 spaces)
            i += 1
            block_lines = []
            while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
                block_lines.append(lines[i][2:] if lines[i].startswith('  ') else '')
                i += 1
            fm[k] = '\n'.join(block_lines).strip()
            # Don't increment i - it's already at the next line
            continue
        
        # Handle quoted values
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        
        fm[k] = v
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


def get_file_last_commit_date(filepath):
    """Get the date of the last commit that modified this file."""
    try:
        # git log -1 --format=%cI <file> returns ISO 8601 date of last commit
        out = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cI', '--', filepath],
            cwd=ROOT,
            stderr=subprocess.DEVNULL
        )
        iso_date = out.decode('utf-8').strip()
        if iso_date:
            # Parse ISO date and return as YYYY-MM-DD
            return iso_date.split('T')[0]
    except Exception:
        pass
    # Fallback: use current date
    return datetime.utcnow().strftime('%Y-%m-%d')


def get_file_last_commit_author(filepath):
    """Get the author name of the last commit that modified this file."""
    try:
        # git log -1 --format=%an <file> returns author name of last commit
        out = subprocess.check_output(
            ['git', 'log', '-1', '--format=%an', '--', filepath],
            cwd=ROOT,
            stderr=subprocess.DEVNULL
        )
        author = out.decode('utf-8').strip()
        return author if author else 'Unknown'
    except Exception:
        return 'Unknown'


def get_file_commit_history(filepath, max_commits=10):
    """Get the commit history (messages) for a file.
    Returns a list of commit messages (most recent first).
    """
    try:
        # git log --format=%s -- <file> returns commit subjects (one per line)
        out = subprocess.check_output(
            ['git', 'log', f'-{max_commits}', '--format=%s', '--', filepath],
            cwd=ROOT,
            stderr=subprocess.DEVNULL
        )
        messages = out.decode('utf-8').strip().split('\n')
        # Filter out empty lines
        return [msg for msg in messages if msg.strip()]
    except Exception:
        return []


def build_index():
    items = []
    for path in sorted(glob.glob(os.path.join(FAQ_DIR, '*.md'))):
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        fm, body = parse_frontmatter(text)
        
        # Extract ID from filename (e.g., "001-question.md" -> "001")
        filename = os.path.basename(path)
        file_id = filename.split('-')[0] if '-' in filename else filename.replace('.md', '')
        
        # Get last commit date for this file (auto-generated)
        last_modified = get_file_last_commit_date(path)
        
        # Get last commit author for this file (auto-generated)
        last_author = get_file_last_commit_author(path)
        
        # Get commit history for this file (auto-generated changelog)
        commit_history = get_file_commit_history(path, max_commits=10)
        
        item = {
            'filename': filename,
            'id': file_id,  # Extract from filename instead of frontmatter
            'question': fm.get('question'),
            'category': fm.get('category'),
            'turn_order': fm.get('turn_order'),
            'date': last_modified,  # Use git commit date instead of frontmatter
            'author': last_author,  # Last commit author
            'referenced_rules': fm.get('referenced_rules'),
            'change_log': commit_history,  # List of commit messages
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
