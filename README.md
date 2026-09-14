# Weird Cats × Codex Pets

The first public Weird Cats drop for Codex: four animated pixel companions with sixteen cursor directions, interaction reactions, and Codex Pet v2 packages.

## Meet the first four

| Pet | Source | Technical ID |
| --- | --- | --- |
| Smoke | WC 04 | `weird-cats-04-page-mascot` |
| Lucky | WC 07 | `weird-cats-07-page-mascot` |
| Glitch | WC 09 | `weird-cats-09-page-mascot` |
| Beanie | WC 10 | `weird-cats-10-page-mascot` |

Open the gallery, click a character, and choose **Install** inside its speech bubble. The detail page provides one short command to copy into Codex, such as `$weird-cats smoke`. Every package contains exactly `pet.json` and `spritesheet.webp`.

After Codex installs the package, open **Settings → Pets**, select **Refresh**, and choose the new custom pet.

## Plugin setup

Add this repository as a Codex marketplace and install the collection once:

```sh
codex plugin marketplace add nett0eth/weird-cats-codex-pets
codex plugin add weird-cats@weird-cats
```

Then install any companion from the Codex composer with `$weird-cats smoke`, `$weird-cats lucky`, `$weird-cats glitch`, or `$weird-cats beanie`.

## Package format

- Codex Pet v2
- Atlas: `1536 × 2288` WebP
- Grid: 8 columns × 11 rows
- Manifest marker: `"spriteVersionNumber": 2`

## Add a future Weird Cat

The gallery is data driven. Add the new package under `packages/<technical-id>/`, put the display atlas in `assets/`, add one object to `pets.json`, and attach the installable package to the next GitHub release. `gallery.js` and `pet.js` render the new entry without hard-coded card markup.

## Local preview

Serve the repository root with any static HTTP server and open `index.html`. Fetching `pets.json` requires HTTP rather than opening the file directly.
