FAQ Data Repository (scaffold)

This repository stores the FAQ Markdown source files and a CI workflow that validates and builds a machine-readable index (index.json).

Structure
- data/faq/*.md           — individual FAQ entries (YAML frontmatter + Markdown body)
- scripts/build_index.py  — generates index.json from markdown files
- scripts/validate_faq.py — validates frontmatter (duplicate IDs, required fields)
- .github/workflows/build-index.yml — GitHub Action to validate and build index.json

Usage (local)
1. Add / edit Markdown files under `data/faq/`.
2. Run validator and builder locally:
   python scripts/validate_faq.py
   python scripts/build_index.py

CI: The workflow will run on PRs to validate and on merges to main to generate `index.json`.
