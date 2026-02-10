#!/usr/bin/env python3
"""Convert a CSV of FAQs into individual markdown files matching the repo schema.

Usage:
  python scripts/csv_to_md.py /path/to/faqs.csv

CSV columns expected (header row):
  ID,Turn Order,Category,Question,Ruling,Date,Referenced Rules,Change Log

Output:
  Writes files to data/faq/ named like: 001-slugified-question.md
  Each file will contain YAML frontmatter with fields:
    turn_order, category, question, referenced_rules, change_log
  And the CSV 'Ruling' content as the markdown body.

This script is conservative: it will not overwrite existing files unless --force is used.
"""

import csv
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def slugify(text: str) -> str:
    text = text.strip().lower()
    # replace non-alnum with hyphen
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:60]


def write_md(out_dir: Path, row: dict, force=False):
    try:
        id_raw = row.get('ID') or row.get('Id') or row.get('id')
        idx = int(id_raw)
    except Exception:
        # fallback to timestamp if no numeric id
        idx = int(datetime.utcnow().timestamp())

    question = (row.get('Question') or row.get('question') or '').strip()
    slug = slugify(question) or f'faq-{idx}'
    fname = f"{idx:03d}-{slug}.md"
    target = out_dir / fname

    if target.exists() and not force:
        print(f"Skipping existing: {target}")
        return target

    # Build frontmatter
    fm_lines = ["---"]
    turn_order = row.get('Turn Order') or row.get('turn_order') or ''
    if turn_order:
        fm_lines.append(f'turn_order: "{turn_order}"')
    category = (row.get('Category') or row.get('category') or '').strip()
    if category:
        fm_lines.append(f'category: "{category}"')
    # Escape double-quotes inside the question for safe YAML inline string
    escaped_question = question.replace('"', '\\"')
    fm_lines.append(f'question: "{escaped_question}"')

    referenced = (row.get('Referenced Rules') or row.get('Referenced Rules'.lower()) or '').strip()
    if referenced:
        fm_lines.append('referenced_rules: |')
        for line in referenced.splitlines():
            fm_lines.append('  ' + line.rstrip())

    change_log = (row.get('Change Log') or row.get('Change Log'.lower()) or '').strip()
    if change_log:
        fm_lines.append('change_log: |')
        for line in change_log.splitlines():
            fm_lines.append('  ' + line.rstrip())

    # Close frontmatter and add the ruling as `answer` block scalar so the
    # validator (which expects an `answer` field) finds it.
    fm_lines.append('')
    ruling = (row.get('Ruling') or row.get('ruling') or '').strip()
    if ruling:
        fm_lines.append('answer: |')
        for line in ruling.splitlines():
            fm_lines.append('  ' + line.rstrip())
    fm_lines.append('---')
    fm_lines.append('')

    # In previous versions we wrote the ruling as the markdown body. The
    # validator expects an `answer` field in frontmatter, so we store it
    # there. For compatibility, we also leave no duplicate body content.
    content = '\n'.join(fm_lines) + '\n'

    out_dir.mkdir(parents=True, exist_ok=True)
    with target.open('w', encoding='utf-8') as fh:
        fh.write(content)

    print(f'Wrote: {target}')
    return target


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/csv_to_md.py /path/to/faqs.csv [--force]')
        sys.exit(2)

    csv_path = Path(sys.argv[1])
    force = '--force' in sys.argv
    if not csv_path.exists():
        print(f'CSV not found: {csv_path}')
        sys.exit(3)

    # Determine repo root by walking up until we find data/faq or scripts folder
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / 'data' / 'faq'

    with csv_path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            write_md(out_dir, row, force=force)


if __name__ == '__main__':
    main()
