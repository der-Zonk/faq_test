# FAQ Categories Configuration

This file defines the allowed categories for FAQ entries.

## Allowed Categories

The following categories are currently configured:

- **Combat** - Combat phase rules, combat resolution
- **Movement** - Movement phase, march, charge, wheel
- **Magic** - Magic phase, spells, wizards
- **Shooting** - Shooting phase, ranged attacks
- **Morale** - Panic, psychology, leadership tests
- **Characters** - Character rules, mounts, challenges
- **Monsters** - Monster rules, special abilities
- **War Machines** - Warmachines, crew, shooting
- **Terrain** - Terrain types, effects
- **Deployment** - Deployment rules, scenarios
- **Special Rules** - Universal special rules
- **Army Lists** - Army list composition, restrictions
- **General** - General game rules, miscellaneous

## How to Add/Remove Categories

1. Edit `config.json`
2. Update the `allowed_categories` array
3. Update this documentation
4. Commit and push changes

Note: The webapp form automatically populates category options from `index.json` (GitHub Pages), so no manual updates to the form are needed.

## Validation

Categories are validated in CI by `scripts/validate_faq.py`. PRs with invalid categories will be rejected.
