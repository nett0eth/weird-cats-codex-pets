import argparse
import json
import os
import zipfile
from pathlib import Path


ARCHIVES = {
    "smoke": "weird-cats-04-page-mascot-v2.zip",
    "lucky": "weird-cats-07-page-mascot-v2.zip",
    "glitch": "weird-cats-09-page-mascot-v2.zip",
    "beanie": "weird-cats-10-page-mascot-v2.zip",
}


def main():
    parser = argparse.ArgumentParser(description="Install a bundled Weird Cat as a Codex Pet.")
    parser.add_argument("cat", choices=sorted(ARCHIVES))
    args = parser.parse_args()

    plugin_root = Path(__file__).resolve().parents[1]
    archive = plugin_root / "assets" / "pets" / ARCHIVES[args.cat]
    with zipfile.ZipFile(archive) as package:
        if set(package.namelist()) != {"pet.json", "spritesheet.webp"}:
            raise SystemExit("Invalid pet package contents.")
        manifest_bytes = package.read("pet.json")
        sprite_bytes = package.read("spritesheet.webp")

    manifest = json.loads(manifest_bytes)
    if manifest.get("spriteVersionNumber") != 2:
        raise SystemExit("Unsupported sprite version.")
    if manifest.get("spritesheetPath") != "spritesheet.webp":
        raise SystemExit("Invalid spritesheet path.")
    if not sprite_bytes.startswith(b"RIFF") or b"WEBP" not in sprite_bytes[:16]:
        raise SystemExit("Invalid WebP spritesheet.")

    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    destination = codex_root / "pets" / manifest["id"]
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "pet.json").write_bytes(manifest_bytes)
    (destination / "spritesheet.webp").write_bytes(sprite_bytes)
    print(f"Installed {manifest['displayName']} at {destination}")


if __name__ == "__main__":
    main()
