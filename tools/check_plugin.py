"""Exercise the public plugin installer against a temporary pets directory."""

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import zipfile


def main():
    root = Path(__file__).resolve().parents[1]
    plugin = root / 'plugins' / 'weird-cats'
    catalog = json.loads((plugin / 'assets' / 'catalog.json').read_text(encoding='utf-8'))
    assert len(catalog['pets']) == 25 and len(catalog['legacy']) == 4
    ids = [item['id'] for item in catalog['pets'] + catalog['legacy']]
    assert len(ids) == len(set(ids))
    script = plugin / 'scripts' / 'install_pet.py'

    with tempfile.TemporaryDirectory(prefix='.install-test-', dir=root) as temporary:
        destination = Path(temporary) / 'pets'
        subprocess.run([sys.executable, str(script), 'all', '--destination', str(destination)],
                       check=True, stdout=subprocess.DEVNULL)
        assert len(list(destination.iterdir())) == 25
        for item in catalog['pets']:
            with zipfile.ZipFile(plugin / 'assets' / 'pets' / item['archive']) as package:
                installed = destination / item['id']
                assert (installed / 'pet.json').read_bytes() == package.read('pet.json')
                assert (installed / 'spritesheet.webp').read_bytes() == package.read('spritesheet.webp')

        subprocess.run([sys.executable, str(script), 'glitch-classic', '--destination', str(destination)],
                       check=True, stdout=subprocess.DEVNULL)
        assert len(list(destination.iterdir())) == 26
        subprocess.run([sys.executable, str(script), 'frog-hat', '--destination', str(destination)],
                       check=True, stdout=subprocess.DEVNULL)
        assert len(list(destination.iterdir())) == 26
    print('PASS: 25 new pets, four original aliases, ZIP integrity, all/single install.')


if __name__ == '__main__':
    main()
