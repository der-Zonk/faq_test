# FAQ Data Repository

This repository stores the FAQ Markdown source files and a CI workflow that validates and builds a machine-readable index (index.json).

## Structure
- `data/faq/*.md` — individual FAQ entries (YAML frontmatter + Markdown body)
  - **Filename format**: `{ID}-{slug}.md` (e.g., `001-combat-question.md`)
  - **ID is extracted from filename**, not from frontmatter
- `scripts/build_index.py` — generates index.json from markdown files
- `scripts/validate_faq.py` — validates frontmatter (duplicate IDs, required fields, valid categories)
- `config.json` — allowed categories configuration
- `.github/workflows/build-index.yml` — GitHub Action to validate and build index.json

## FAQ Entry Format

### Filename
Files must follow the pattern: `{numeric-id}-{slug}.md`
- Example: `001-skirmisher-retreat.md`
- The ID is automatically extracted from the filename

### Frontmatter (YAML)
```yaml
---
question: "Your question here"
category: "Combat"  # Must be from allowed list in config.json
turn_order: "TBD"   # Optional
referenced_rules: |  # Optional, multiline supported
  See rulebook page 42.
---
```

**Auto-generated fields** (not in frontmatter):
- `id` — extracted from filename
- `date` — last commit date of the file
- `change_log` — list of commit messages for the file

## Usage (local)
1. Add / edit Markdown files under `data/faq/`.
2. Run validator and builder locally:
   ```bash
   python scripts/validate_faq.py
   python scripts/build_index.py
   ```

## CI Workflow
- **On PR**: Validates all FAQ entries
- **On merge to main**: Builds index.json and deploys to GitHub Pages
- **Checks**: Duplicate IDs, required fields, valid categories, filename format
