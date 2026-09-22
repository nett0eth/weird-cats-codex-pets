---
name: weird-cats
description: Install any of 25 experimental Weird Cats laptop mascots as the user's Codex Pet. Use when the user invokes $weird-cats with a cat name or asks to install Weird Cats.
---

# Weird Cats

Install one or all bundled Weird Cats as custom Codex Pets. The new collection is experimental; the four original pets remain available with `-classic` names.

## Commands

- `$weird-cats all` installs all 25 new mascots.
- `$weird-cats frog-hat`, `$weird-cats ash`, `$weird-cats prism`, `$weird-cats spectrum`, and `$weird-cats glitch` install individual new mascots.
- `$weird-cats smoke-classic`, `$weird-cats lucky-classic`, `$weird-cats glitch-classic`, and `$weird-cats beanie-classic` install the four original versions.

Match names case-insensitively and replace spaces with hyphens. Read the full set of names from `../../assets/catalog.json`. If the name is missing, show the available names and ask the user to choose one.

## Installation

1. Run `../../scripts/install_pet.py <name>` with Python, using the name from the catalog or `all`. The script validates each bundled archive under `../../assets/pets/` and installs it under `${CODEX_HOME}/pets/<pet-id>` (or `~/.codex/pets/<pet-id>` when `CODEX_HOME` is unset).
2. Open Codex **Settings → Pets**, refresh the list, and select the newly installed cat when UI control is available. Otherwise, tell the user to refresh and select it.
3. Report the installed display name, or the number installed for `all`.

Do not replace another custom pet whose manifest has a different `id`. If a pet with the same `id` exists, update it with the bundled version.
