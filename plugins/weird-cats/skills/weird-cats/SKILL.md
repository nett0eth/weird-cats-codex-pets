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
2. Extract it into a fresh temporary directory.
3. Verify the archive contains exactly `pet.json` and `spritesheet.webp`. Verify the manifest has `spriteVersionNumber` equal to `2` and that `spritesheetPath` is `spritesheet.webp`.
4. Install the validated directory through the Codex custom-pet installation flow. Preserve the `id` and `displayName` from `pet.json`.
5. Refresh the Codex Pets list and select the newly installed cat.
6. Report the installed display name in one sentence.

Do not replace another custom pet whose manifest has a different `id`. If a pet with the same `id` exists, update it with the bundled version.
