"""Copy the tested laptop pet archives into the Codex plugin catalog.

Usage: python tools/import_laptop_collection.py PATH_TO_LAPTOP_PRODUCTION
"""

from pathlib import Path
import argparse
import json
import shutil
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    entries = json.loads((source / 'production.json').read_text(encoding='utf-8'))
    if len(entries) != 25:
        raise SystemExit('Expected exactly 25 tested laptop pets.')

    plugin = Path(__file__).resolve().parents[1] / 'plugins' / 'weird-cats'
    destination = plugin / 'assets' / 'pets'
    destination.mkdir(parents=True, exist_ok=True)
    catalog = []
    for entry in entries:
        name = entry['name'].lower().replace(' ', '-')
        archive_name = Path(entry['download']).name
        archive = source / entry['download']
        with zipfile.ZipFile(archive) as package:
            if set(package.namelist()) != {'pet.json', 'spritesheet.webp'} or package.testzip():
                raise SystemExit(f'Invalid archive: {archive}')
            manifest = json.loads(package.read('pet.json'))
            if manifest['id'] != entry['id'] or manifest['spriteVersionNumber'] != 2:
                raise SystemExit(f'Invalid manifest: {archive}')
        shutil.copy2(archive, destination / archive_name)
        catalog.append({'name': name, 'displayName': entry['name'], 'id': entry['id'],
                        'archive': archive_name})

    legacy = [
        {'name': name + '-classic', 'displayName': name.title() + ' (original)',
         'id': f'weird-cats-{number}-page-mascot',
         'archive': f'weird-cats-{number}-page-mascot-v2.zip'}
        for name, number in (('smoke', '04'), ('lucky', '07'), ('glitch', '09'), ('beanie', '10'))
    ]
    for item in legacy:
        if not (destination / item['archive']).is_file():
            raise SystemExit(f'Missing original package: {item["archive"]}')
    payload = {'version': 1, 'pets': catalog, 'legacy': legacy}
    (plugin / 'assets' / 'catalog.json').write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Imported {len(catalog)} test pets; preserved {len(legacy)} originals.')


if __name__ == '__main__':
    main()
