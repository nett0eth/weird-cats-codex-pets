# Weird Cats × Codex Pets

The first public Weird Cats drop for Codex: six animated pixel companions with sixteen cursor directions, interaction reactions, and Codex Pet v2 packages.

## Meet the first six

| Pet | Source | Technical ID |
| --- | --- | --- |
| Weirdo | WC 18 · Original | `weird-cats-18-page-mascot` |
| Smoke | WC 04 | `weird-cats-04-page-mascot` |
| Lucky | WC 07 | `weird-cats-07-page-mascot` |
| Glitch | WC 09 | `weird-cats-09-page-mascot` |
| Beanie | WC 10 | `weird-cats-10-page-mascot` |
| Frog Hat | Special | `weird-cats-frog-hat-page-mascot` |

Open the gallery, choose a character, and use the installation command on its detail page. Every package contains exactly `pet.json` and `spritesheet.webp`.

## Install manually

1. Download one ZIP from the [v1.0.0 release](https://github.com/nett0eth/weird-cats-codex-pets/releases/tag/v1.0.0).
2. Extract it to `$HOME/.codex/pets/<technical-id>/`.
3. Open **Settings → Pets** in the ChatGPT desktop app.
4. Select **Refresh**, then choose the new custom pet.

The official OpenAI Pets guide describes the Settings → Pets, Refresh, and custom-pet selection flow: <https://learn.chatgpt.com/docs/pets>.

## Package format

- Codex Pet v2
- Atlas: `1536 × 2288` WebP
- Grid: 8 columns × 11 rows
- Manifest marker: `"spriteVersionNumber": 2`

## Add a future Weird Cat

The gallery is data driven. Add the new package under `packages/<technical-id>/`, put the display atlas in `assets/`, add one object to `pets.json`, and attach the installable ZIP to the next GitHub release. `gallery.js` and `pet.js` render the new entry without hard-coded card markup.

## Local preview

Serve the repository root with any static HTTP server and open `index.html`. Fetching `pets.json` requires HTTP rather than opening the file directly.
