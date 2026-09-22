# Weird Cats × Codex Pets

The Weird Cats Codex plugin now includes 25 experimental laptop companions, plus the four original pets. Each has sixteen cursor directions, interaction reactions, task signals, and a Codex Pet v2 package. The website gallery still shows the original four.

## Meet the first four

| Pet | Source | Technical ID |
| --- | --- | --- |
| Smoke | WC 04 | `weird-cats-04-page-mascot` |
| Lucky | WC 07 | `weird-cats-07-page-mascot` |
| Glitch | WC 09 | `weird-cats-09-page-mascot` |
| Beanie | WC 10 | `weird-cats-10-page-mascot` |

Open the gallery, click a character, and choose **Install** inside its speech bubble. The detail page provides two copyable commands: a one-time plugin setup and the short character command, such as `$weird-cats smoke`. Every package contains exactly `pet.json` and `spritesheet.webp`.

After Codex installs the package, open **Settings → Pets**, select **Refresh**, and choose the new custom pet.

## Plugin setup

Add this repository as a Codex marketplace and install the collection once:

```sh
codex plugin marketplace add nett0eth/weird-cats-codex-pets
codex plugin add weird-cats@weird-cats
```

Install all new companions with `$weird-cats all`, or choose one by name, such as `$weird-cats frog-hat`, `$weird-cats ash`, `$weird-cats prism`, `$weird-cats spectrum`, or `$weird-cats glitch`. The full list is in [`plugins/weird-cats/assets/catalog.json`](plugins/weird-cats/assets/catalog.json). The original four remain available as `$weird-cats smoke-classic`, `$weird-cats lucky-classic`, `$weird-cats glitch-classic`, and `$weird-cats beanie-classic`.

These 25 packages are for testing in Codex. Their head movements use the Page Mascot directional poses, their working state shows a laptop, and greeting/hover poses have no hearts. The Codex pet format does not currently send a separate user-typing event, so looking down while the user types is demonstrated only in the local preview.

## Package format

- Codex Pet v2
- Atlas: `1536 × 2288` WebP
- Grid: 8 columns × 11 rows
- Manifest marker: `"spriteVersionNumber": 2`

## Add a future Weird Cat

The website gallery has its own four-pet catalog. To add another character to the experimental Codex plugin, add its validated package to `plugins/weird-cats/assets/pets/` and an entry to `plugins/weird-cats/assets/catalog.json`. The importer at `tools/import_laptop_collection.py` performs both steps from the tested local collection.

## Local preview

Serve the repository root with any static HTTP server and open `index.html`. Fetching `pets.json` requires HTTP rather than opening the file directly.
