from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "art" / "ui"
OUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = Path(r"C:\Windows\Fonts\consolab.ttf")
FONT = ImageFont.truetype(str(FONT_PATH), 12)
FONT_LARGE = ImageFont.truetype(str(FONT_PATH), 18)


def neon_text(lines, colors, name, *, padding=8, line_gap=3, scale=3, large=False):
    font = FONT_LARGE if large else FONT
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    boxes = [probe.textbbox((0, 0), line, font=font, stroke_width=1) for line in lines]
    widths = [box[2] - box[0] for box in boxes]
    heights = [box[3] - box[1] for box in boxes]
    width = max(widths) + padding * 2
    height = sum(heights) + line_gap * (len(lines) - 1) + padding * 2
    crisp = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(crisp)
    y = padding
    for line, color, text_width, text_height in zip(lines, colors, widths, heights):
        x = (width - text_width) // 2
        draw.text((x, y), line, font=font, fill=color, stroke_width=1, stroke_fill=(15, 1, 22, 255))
        y += text_height + line_gap

    crisp = crisp.resize((width * scale, height * scale), Image.Resampling.NEAREST)
    alpha = crisp.getchannel("A")
    glow = Image.new("RGBA", crisp.size, colors[-1])
    glow.putalpha(alpha.filter(ImageFilter.GaussianBlur(scale * 2.2)))
    out = Image.alpha_composite(glow, crisp)
    out.save(OUT / name, optimize=True)


CYAN = (31, 235, 255, 255)
PINK = (255, 48, 196, 255)
WHITE = (255, 239, 252, 255)
YELLOW = (255, 232, 70, 255)

neon_text(["SELECT YOUR", "WEIRD CAT"], [CYAN, PINK], "title-select-weird-cat.png", padding=10, line_gap=5, scale=3, large=True)
neon_text(["CODEX PETS / DROP 01"], [CYAN], "menu-drop.png", padding=6, scale=3)
neon_text(["GITHUB >"], [WHITE], "menu-github.png", padding=6, scale=3)
neon_text(["< ALL CATS"], [WHITE], "menu-all-cats.png", padding=6, scale=3)
neon_text(["INSTALL >"], [YELLOW], "action-install.png", padding=5, scale=3)
neon_text(["INSTALL"], [PINK], "title-install.png", padding=7, scale=3, large=True)
neon_text(["1 / SETUP ONCE"], [CYAN], "title-setup-once.png", padding=5, scale=3)
neon_text(["2 / CALL YOUR CAT"], [PINK], "title-call-cat.png", padding=5, scale=3)
neon_text(["COPY COMMAND"], [WHITE], "action-copy-command.png", padding=5, scale=3)
neon_text(["COPIED !"], [YELLOW], "action-copied.png", padding=5, scale=3)

for pet in ("SMOKE", "LUCKY", "GLITCH", "BEANIE"):
    neon_text([pet], [WHITE], f"name-{pet.lower()}.png", padding=4, scale=3)

for number in range(1, 5):
    neon_text([f"SIGNAL 0{number}"], [PINK], f"signal-{number}.png", padding=3, scale=3)

quotes = {
    "smoke": ["TAKE ME HOME.", "I KNOW A GUY."],
    "lucky": ["CLICK INSTALL.", "TRUST THE COIN."],
    "glitch": ["ADOPT ME BEFORE", "I DESYNC."],
    "beanie": ["YOUR CURSOR LOOKS", "COLD. LET ME IN."],
}
for pet, lines in quotes.items():
    neon_text(lines, [WHITE] * len(lines), f"quote-{pet}.png", padding=5, line_gap=2, scale=3)
