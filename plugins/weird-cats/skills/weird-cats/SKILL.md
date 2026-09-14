---
name: weird-cats
description: Install Smoke, Lucky, Glitch, or Beanie from the Weird Cats collection as the user's Codex Pet. Use when the user invokes $weird-cats with a cat name or asks to install a Weird Cat.
---

# Weird Cats

Install one bundled Weird Cat as a custom Codex Pet.

## Commands

- `$weird-cats smoke`
- `$weird-cats lucky`
- `$weird-cats glitch`
- `$weird-cats beanie`

Match names case-insensitively. If the invocation does not name one of these four cats, ask the user to choose one.

## Installation

1. Resolve the selected archive relative to this file at `../../assets/pets/`:
   - Smoke: `weird-cats-04-page-mascot-v2.zip`
   - Lucky: `weird-cats-07-page-mascot-v2.zip`
   - Glitch: `weird-cats-09-page-mascot-v2.zip`
   - Beanie: `weird-cats-10-page-mascot-v2.zip`
2. Run `../../scripts/install_pet.py <name>` with the bundled Python runtime. The script validates the archive and stages the pet under `${CODEX_HOME}/pets/<pet-id>` (or `~/.codex/pets/<pet-id>` when `CODEX_HOME` is unset).
3. Open Codex **Settings → Pets**, refresh the list, and select the newly installed cat when UI control is available. Otherwise, tell the user to refresh and select it.
4. Report the installed display name in one sentence.

Do not replace another custom pet whose manifest has a different `id`. If a pet with the same `id` exists, update it with the bundled version.
