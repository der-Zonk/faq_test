"""Simple validator for FAQ entries.

Checks for duplicate IDs, missing required fields, and valid categories.
"""
import os
import glob
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FAQ_DIR = os.path.join(ROOT, 'data', 'faq')
CONFIG_FILE = os.path.join(ROOT, 'config.json')


def load_config():
    """Load allowed categories from config.json."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as fh:
            config = json.load(fh)
            return config.get('allowed_categories', [])
    except Exception as e:
        print(f'WARNING: Could not load config.json: {e}')
        return []


def parse_frontmatter(text):
    """Parse YAML-like frontmatter with support for multiline blocks (|)."""
    lines = text.splitlines()
    if not lines or not lines[0].strip().startswith('---'):
        return {}
    
    fm = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        
        # End of frontmatter block
        if line.strip() == '---':
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
    
    return fm


def validate():
    ids = {}
    errors = 0
    allowed_categories = load_config()
    
    if not allowed_categories:
        print('WARNING: No allowed categories configured in config.json')
    else:
        print(f'Allowed categories: {", ".join(allowed_categories)}')
    
    for path in sorted(glob.glob(os.path.join(FAQ_DIR, '*.md'))):
        with open(path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        fm = parse_frontmatter(text)
        fname = os.path.basename(path)
        
        # Extract ID from filename (e.g., "001-question.md" -> "001")
        file_id = fname.split('-')[0] if '-' in fname else fname.replace('.md', '')
        
        # Check filename format (should start with ID)
        if not file_id or not file_id[0].isdigit():
            print(f'ERROR {fname}: filename should start with numeric ID (e.g., "001-question.md")')
            errors += 1
            continue
        
        # Check required fields (id is extracted from filename, not frontmatter)
        if not fm.get('question'):
            print(f'ERROR {fname}: missing question field')
            errors += 1
            continue
            continue
        
        # Check duplicate IDs (from filenames)
        if file_id in ids:
            print(f'ERROR {fname}: duplicate id {file_id} (also in {ids[file_id]})')
            errors += 1
        else:
            ids[file_id] = fname
        
        # Check category validity
        category = fm.get('category')
        if not category:
            print(f'ERROR {fname}: missing category field')
            errors += 1
        elif allowed_categories and category not in allowed_categories:
            print(f'ERROR {fname}: invalid category "{category}". Allowed: {", ".join(allowed_categories)}')
            errors += 1
    
    if errors:
        print(f'\nValidation failed: {errors} errors')
        return 2
    print('\nValidation passed')
    return 0


if __name__ == '__main__':
    raise SystemExit(validate())
