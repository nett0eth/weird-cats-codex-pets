"""Rebuild Frog Hat with clean cell edges and a safe neutral frame."""
from collections import deque
from pathlib import Path
import shutil
import zipfile

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parent / "codex-pets" / "collection-01"
PET_ID = "weird-cats-frog-hat-page-mascot"
CELL = (192, 208)
RENDER = (184, 184)
OFFSET = (4, 12)
MAP = [
    ["D4", "R0", "D4", "D4", "R0", "D4"],
    ["D5", "D5", "D2", "D5", "D5", "D8", "D5", "D5"],
    ["D3", "D3", "D0", "D3", "D3", "D6", "D3", "D3"],
    ["R1", "R2", "R8", "R1"],
    ["D4", "R3", "R2", "R8", "D4"],
    ["R3", "R7", "R7", "R6", "R6", "R7", "R6", "D4"],
    ["D4", "R0", "D4", "R6", "R0", "D4"],
    ["D4", "R2", "R8", "R4", "R2", "R8"],
    ["D4", "R3", "R4", "R7", "R2", "D4"],
    ["D1", "D2", "D2", "D5", "D5", "D5", "D8", "D8"],
    ["D7", "D6", "D6", "D3", "D3", "D0", "D0", "D0"],
]


def split_cell(sheet: Image.Image, index: int) -> Image.Image:
    size = sheet.width // 3
    x = (index % 3) * size
    y = (index // 3) * size
    return sheet.crop((x, y, x + size, y + size))


def remove_foreign_edge_fragments(cell: Image.Image) -> Image.Image:
    """Remove small alpha islands crossing a generated 3x3 cell boundary."""
    image = cell.copy().convert("RGBA")
    alpha = image.getchannel("A")
    width, height = image.size
    occupied = alpha.load()
    seen = bytearray(width * height)
    components = []

    for start_y in range(height):
        for start_x in range(width):
            key = start_y * width + start_x
            if seen[key] or occupied[start_x, start_y] < 12:
                continue
            queue = deque([(start_x, start_y)])
            seen[key] = 1
            points = []
            touches_edge = False
            while queue:
                x, y = queue.popleft()
                points.append((x, y))
                touches_edge = touches_edge or x < 3 or y < 3 or x >= width - 3 or y >= height - 3
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                    if 0 <= nx < width and 0 <= ny < height:
                        nkey = ny * width + nx
                        if not seen[nkey] and occupied[nx, ny] >= 12:
                            seen[nkey] = 1
                            queue.append((nx, ny))
            components.append((points, touches_edge))

    largest = max((len(points) for points, _ in components), default=0)
    pixels = image.load()
    for points, touches_edge in components:
        if touches_edge and len(points) < largest * 0.12:
            for x, y in points:
                pixels[x, y] = (0, 0, 0, 0)
    return image


def render_cell(sheet: Image.Image, index: int) -> Image.Image:
    source = remove_foreign_edge_fragments(split_cell(sheet, index))
    source = source.resize(RENDER, Image.Resampling.NEAREST)
    output = Image.new("RGBA", CELL)
    output.paste(source, OFFSET, source)
    return output


def render_original_neutral() -> Image.Image:
    source_path = SOURCE_ROOT / "artwork" / "weird-cats-frog-hat" / "source" / "normalized.png"
    source = Image.open(source_path).convert("RGBA")
    scale = min(RENDER[0] / source.width, RENDER[1] / source.height)
    size = (round(source.width * scale), round(source.height * scale))
    source = source.resize(size, Image.Resampling.NEAREST)
    output = Image.new("RGBA", CELL)
    position = ((CELL[0] - source.width) // 2, (CELL[1] - source.height) // 2)
    output.paste(source, position, source)
    return output


def main() -> None:
    source_dir = SOURCE_ROOT / "artwork" / PET_ID / "source"
    directions = Image.open(source_dir / "directions-clean.png").convert("RGBA")
    reactions = Image.open(source_dir / "reactions-clean.png").convert("RGBA")
    atlas = Image.new("RGBA", (1536, 2288))

    for row, tokens in enumerate(MAP):
        for column, token in enumerate(tokens):
            sheet = directions if token[0] == "D" else reactions
            frame = render_cell(sheet, int(token[1:]))
            if token == "D4":
                frame = render_original_neutral()
            atlas.paste(frame, (column * CELL[0], row * CELL[1]), frame)

    neutral = render_original_neutral()
    atlas.paste(neutral, (6 * CELL[0], 0), neutral)

    package = ROOT / "packages" / PET_ID
    sprite_path = package / "spritesheet.webp"
    atlas.save(sprite_path, lossless=True, exact=True, method=6)
    shutil.copy2(sprite_path, ROOT / "assets" / "frog-hat.webp")
    neutral.save(ROOT / "assets" / "art" / "frog-hat-clean.png")

    archive_path = ROOT / "downloads" / f"{PET_ID}-v2.zip"
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(package / "pet.json", "pet.json")
        archive.write(sprite_path, "spritesheet.webp")
    print(f"Rebuilt {sprite_path.name} with clean edge cells and safe eye margins.")


if __name__ == "__main__":
    main()
