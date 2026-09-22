"""Install a bundled Weird Cat as a Codex Pet."""

import argparse
import json
import os
import re
import zipfile
from pathlib import Path


def load_catalog(plugin_root):
    catalog = json.loads((plugin_root / 'assets' / 'catalog.json').read_text(encoding='utf-8'))
    entries = catalog['pets'] + catalog['legacy']
    by_name = {item['name']: item for item in entries}
    if len(catalog['pets']) != 25 or len(by_name) != len(entries):
        raise SystemExit('Invalid Weird Cats catalog.')
    return catalog, by_name


def install(item, plugin_root, destination):
    pet_id = item['id']
    archive_name = item['archive']
    if not re.fullmatch(r'weird-cats-[a-z0-9-]+', pet_id):
        raise SystemExit(f'Invalid pet ID: {pet_id}')
    if Path(archive_name).name != archive_name or not archive_name.endswith('.zip'):
        raise SystemExit(f'Invalid archive name: {archive_name}')
    archive = plugin_root / 'assets' / 'pets' / archive_name
    with zipfile.ZipFile(archive) as package:
        if set(package.namelist()) != {'pet.json', 'spritesheet.webp'} or package.testzip():
            raise SystemExit(f'Invalid package contents: {archive_name}')
        manifest_bytes = package.read('pet.json')
        sprite_bytes = package.read('spritesheet.webp')

    manifest = json.loads(manifest_bytes)
    if (manifest.get('id') != pet_id or manifest.get('spriteVersionNumber') != 2
            or manifest.get('spritesheetPath') != 'spritesheet.webp'):
        raise SystemExit(f'Invalid pet manifest: {archive_name}')
    if not sprite_bytes.startswith(b'RIFF') or b'WEBP' not in sprite_bytes[:16]:
        raise SystemExit(f'Invalid WebP spritesheet: {archive_name}')

    target = destination / pet_id
    if target.exists():
        manifest_file = target / 'pet.json'
        if manifest_file.is_file():
            existing = json.loads(manifest_file.read_text(encoding='utf-8'))
            if existing.get('id') != pet_id:
                raise SystemExit(f'Refusing to replace another pet: {target}')
    target.mkdir(parents=True, exist_ok=True)
    for filename, content in (('pet.json', manifest_bytes), ('spritesheet.webp', sprite_bytes)):
        temporary = target / (filename + '.tmp')
        temporary.write_bytes(content)
        os.replace(temporary, target / filename)
    print(f"Installed {manifest['displayName']} at {target}")


def main():
    plugin_root = Path(__file__).resolve().parents[1]
    catalog, by_name = load_catalog(plugin_root)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('cat', choices=['all', *sorted(by_name)])
    parser.add_argument('--destination', type=Path,
                        help='Optional test folder; defaults to CODEX_HOME/pets.')
    args = parser.parse_args()
    destination = args.destination or Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'pets'
    selected = catalog['pets'] if args.cat == 'all' else [by_name[args.cat]]
    for item in selected:
        install(item, plugin_root, destination)


if __name__ == '__main__':
    main()
