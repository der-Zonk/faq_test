"""Simple build_index.py

Reads markdown files from ../data/faq/*.md and emits index.json with minimal fields.
This script is intentionally dependency-free and uses a naive frontmatter parser.
"""
import os
import json
import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAQ_DIR = os.path.join(ROOT, 'data', 'faq')
OUT = os.path.join(ROOT, 'index.json')


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
            'content': body[:1000]
        }
        items.append(item)
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
    print('Wrote', OUT)


if __name__ == '__main__':
    build_index()
