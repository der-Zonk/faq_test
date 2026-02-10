#!/usr/bin/env python3
"""Scan `data/faq/*.md` and add an `answer` frontmatter block when missing.

This helps fix existing files created without the expected `answer` field.
It will move the file body into `answer: |` inside the YAML frontmatter and
preserve other frontmatter fields.

Usage:
  python scripts/fix_missing_answer.py [--dry-run]
"""

from pathlib import Path
import re
import sys


def split_frontmatter(text: str):
    # Return (fm_text, rest) or (None, text) if no frontmatter
    if text.startswith('---'):
        parts = text.split('---', 2)
        # parts[0] == '' before first '---'
        if len(parts) >= 3:
            fm = parts[1].strip()
            rest = parts[2].lstrip('\n')
            return fm, rest
    return None, text


def has_answer_in_fm(fm: str) -> bool:
    # crude check for 'answer:' key at start of a line
    return re.search(r'^answer\s*:', fm, flags=re.M) is not None


def make_new_content(fm: str, body: str) -> str:
    lines = []
    lines.append('---')
    # keep fm as-is
    if fm:
        lines.append(fm.rstrip())
    # insert answer block
    lines.append('answer: |')
    if body:
        for line in body.splitlines():
            lines.append('  ' + line.rstrip())
    else:
        lines.append('  ')  # empty block
    lines.append('---')
    lines.append('')
    return '\n'.join(lines)


def process_file(path: Path, dry_run=False):
    text = path.read_text(encoding='utf-8')
    fm, rest = split_frontmatter(text)
    if fm is None:
        print(f'SKIP (no frontmatter): {path.name}')
        return False
    if has_answer_in_fm(fm):
        print(f'OK (has answer): {path.name}')
        return False

    # Move rest into answer block
    new_content = make_new_content(fm, rest)
    if dry_run:
        print(f'WILL UPDATE: {path.name}')
        return True
    path.write_text(new_content, encoding='utf-8')
    print(f'Updated: {path.name}')
    return True


def main():
    dry = '--dry-run' in sys.argv
    repo_root = Path(__file__).resolve().parents[1]
    faq_dir = repo_root / 'data' / 'faq'
    if not faq_dir.exists():
        print('data/faq directory not found')
        sys.exit(1)

    md_files = sorted(faq_dir.glob('*.md'))
    updated = 0
    for p in md_files:
        if process_file(p, dry_run=dry):
            updated += 1

    print(f'Done. Files updated: {updated}')


if __name__ == '__main__':
    main()
