#!/usr/bin/env python3
"""
redraws the link preview images in themes/nfo/assets

  og.png       og-art.txt (braille stars) with logo.txt in the middle
  og-post.png  og-post-art.txt (braille crosshair + stars), hugo draws the
               post title on top of it (see layouts/_partials/og-image.html)

run it after changing logo.txt or either art file:  python3 og.py
needs pillow and the font at assets/fonts/og.ttf
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parent
assets = root / "themes/nfo/assets"
font = root / "assets/fonts/og.ttf"

W, H = 1200, 630
SIZE = 12      # logo font px, 12 makes a ~170 col logo about 1000px wide
ART_SIZE = 10  # art font px, braille at 10 fills 1200x630 with about 240x62 cells
ART_LH = 1.013 # braille line height, keeps the dot rows evenly spaced across lines
SS = 4         # draw 4x and scale down so the grid stays exact


def art_layer(name):
    """a braille art file on a black 1200x630"""
    f = ImageFont.truetype(str(font), ART_SIZE * SS)
    cw = f.getlength("M")
    ch = ART_SIZE * SS * ART_LH
    top = f.getbbox("█")[1]
    big = Image.new("L", (W * SS, H * SS), 0)
    d = ImageDraw.Draw(big)
    for y, line in enumerate((assets / name).read_text(encoding="utf-8").split("\n")):
        for x, c in enumerate(line):
            if c not in " ⠀":
                d.text((round(x * cw), round(y * ch - top)), c, font=f, fill=255)
    return big.resize((W, H), Image.Resampling.LANCZOS)


def logo_layer():
    lines = (assets / "logo.txt").read_text(encoding="utf-8").rstrip("\n").split("\n")
    cols = max(len(l) for l in lines)
    f = ImageFont.truetype(str(font), SIZE * SS)
    pad = 4 * SS
    big = Image.new("L", (int(cols * f.getlength("M")) + 2 * pad, len(lines) * SIZE * SS + 2 * pad), 0)
    d = ImageDraw.Draw(big)
    for i, line in enumerate(lines):
        d.text((pad, pad + i * SIZE * SS), line, font=f, fill=255)
    logo = big.resize((big.width // SS, big.height // SS), Image.Resampling.LANCZOS)
    return logo.crop(logo.getbbox()), cols


og = art_layer("og-art.txt")
logo, cols = logo_layer()
og.paste(logo, ((W - logo.width) // 2, (H - logo.height) // 2), logo)
og.save(assets / "og.png", optimize=True)

art_layer("og-post-art.txt").save(assets / "og-post.png", optimize=True)

print(f"og.png: {cols} col logo, {logo.width}x{logo.height}px")
