"""Simple validator for FAQ entries.

Checks for duplicate IDs and missing required fields.
"""
import os
import glob

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAQ_DIR = os.path.join(ROOT, 'data', 'faq')


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or not lines[0].strip().startswith('---'):
        return {}
    fm = {}
    i = 1
    while i < len(lines):
        if lines[i].strip() == '---':
            break
        line = lines[i]
        if ':' in line:
            k, v = line.split(':', 1)
            fm[k.strip()] = v.strip().strip('"')
        i += 1
    return fm


def validate():
    ids = {}
    errors = 0
    for path in sorted(glob.glob(os.path.join(FAQ_DIR, '*.md'))):
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        fm = parse_frontmatter(text)
        fname = os.path.basename(path)
        if not fm.get('id') or not fm.get('question'):
            print(f'ERROR {fname}: missing id or question')
            errors += 1
            continue
        if fm['id'] in ids:
            print(f'ERROR {fname}: duplicate id {fm["id"]} (also in {ids[fm["id"]]})')
            errors += 1
        else:
            ids[fm['id']] = fname
    if errors:
        print(f'Validation failed: {errors} errors')
        return 2
    print('Validation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(validate())
