#!/usr/bin/env python3
"""
draws the braille art for the link previews into themes/nfo/assets

  og-art.txt       stars, for og.png (the logo goes on top)
  og-post-art.txt  crosshair sigil + stars, for og-post.png (hugo adds the title)

shapes are drawn as a big black and white picture first, then turned into
braille, 2x4 dots per character. run python3 og.py after this to redraw the pngs.
needs pillow and numpy
"""
import math, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parent
assets = root / "themes/nfo/assets"

W, H = 1200, 630
HR = 3                       # the picture is drawn 3x bigger than the og image
PX, LH = 10, 1.013           # braille font px and line height, same as og.py
LX0, LY0, LX1, LY1 = 88, 214, 1112, 416  # where the logo / post title goes, kept empty


# ------------------------------------------------------------------ drawing
def bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    return (u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3,
            u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3)


class Pen:
    def __init__(self):
        self.im = Image.new("L", (W * HR, H * HR), 0)
        self.d = ImageDraw.Draw(self.im)

    def thorn(self, p, w, kind="tip", power=1.0, n=240, minw=0.0):
        """curve that tapers to a point (tip) or to points at both ends (blade)"""
        pts = [bez(p, i / n) for i in range(n + 1)]
        L, R = [], []
        for i, (x, y) in enumerate(pts):
            t = i / n
            a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l = math.hypot(dx, dy) or 1
            nx, ny = -dy / l, dx / l
            ww = w * ((1 - t) ** power if kind == "tip" else math.sin(math.pi * t) ** power) + minw
            L.append((x + nx * ww, y + ny * ww)); R.append((x - nx * ww, y - ny * ww))
        self.d.polygon([(x * HR, y * HR) for x, y in L + R[::-1]], fill=255)

    def line(self, pts, w=1.0):
        self.d.line([(x * HR, y * HR) for x, y in pts], fill=255, width=max(1, int(w * HR)))

    def ring(self, cx, cy, r, w):
        pts = [(cx + r * math.cos(t / 40 * 2 * math.pi), cy + r * math.sin(t / 40 * 2 * math.pi)) for t in range(41)]
        self.line(pts, w)

    def seg(self, a, b, w):
        """straight spike from a to b"""
        (x0, y0), (x1, y1) = a, b
        self.thorn([(x0, y0), (x0 + (x1 - x0) / 3, y0 + (y1 - y0) / 3),
                    (x0 + 2 * (x1 - x0) / 3, y0 + 2 * (y1 - y0) / 3), (x1, y1)], w, "tip", 0.9, minw=0.5)

    def star(self, cx, cy, r):
        """4 point sparkle, long up and down"""
        w = max(1.4, r * 0.11)
        for dx, dy, rr in ((0, -1, r), (0, 1, r), (1, 0, r * 0.55), (-1, 0, r * 0.55)):
            self.thorn([(cx, cy), (cx + dx * rr * .3, cy + dy * rr * .3),
                        (cx + dx * rr * .6, cy + dy * rr * .6), (cx + dx * rr, cy + dy * rr)], w, "tip", 1.6)

    def dust(self, seed, n=26, avoid=()):
        """tiny stars, a dot or two each, the bigger ones get a sparkle"""
        rnd = random.Random(seed)
        k = 0
        while k < n:
            x, y = rnd.uniform(8, 1192), rnd.uniform(8, 622)
            if LX0 - 10 < x < LX1 + 10 and LY0 - 10 < y < LY1 + 10:
                continue
            if any(a <= x <= c and b <= y <= d for a, b, c, d in avoid):
                continue
            r = rnd.choice([1.3, 1.3, 1.8, 2.4])
            self.d.ellipse(((x - r) * HR, (y - r) * HR, (x + r) * HR, (y + r) * HR), fill=255)
            if r > 2:
                self.star(x, y, rnd.choice([7, 9]))
            k += 1


# ------------------------------------------------------------------ the two pieces
def stars():
    p = Pen()
    p.star(710, 80, 18)
    p.star(60, 40, 9)
    p.star(1130, 560, 12)
    p.dust(13, n=30)
    return p


def crosshair():
    """rough ring with a cross through it and one long thorny arm, top left"""
    p = Pen()
    cx, cy = 190, 120
    rnd = random.Random(7)
    p.ring(cx, cy, 52, 4.2)
    for a0, a1 in ((20, 150), (200, 320)):  # broken inner ring
        p.line([(cx + 30 * math.cos(math.radians(a)), cy + 30 * math.sin(math.radians(a))) for a in range(a0, a1 + 1, 6)], 3.2)
    for k in range(16):  # rough barbs on the ring
        a = rnd.uniform(0, 2 * math.pi)
        r0 = 52 + rnd.choice([-1, 1]) * 2
        L = rnd.choice([6, 9, 12]) * rnd.choice([-1, 1])
        p.seg((cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * (r0 + L), cy + math.sin(a) * (r0 + L)), 1.8)
    p.line([(cx, 6), (cx, 206)], 3.4)
    p.line([(cx - 80, cy), (cx + 360, cy)], 3.0)
    p.thorn([(cx + 360, cy), (cx + 400, cy), (cx + 440, cy), (cx + 470, cy)], 2.4, "tip", 1)
    for x in range(cx + 80, cx + 340, 37):  # thorns along the long arm
        p.seg((x, cy), (x + rnd.choice([-6, 6]), cy + rnd.choice([-1, 1]) * rnd.choice([8, 12])), 1.8)
    p.star(cx + 520, cy - 40, 18)
    p.star(60, 40, 9)
    p.dust(13, n=22, avoid=[(60, 0, 700, 215)])
    return p


# ------------------------------------------------------------------ braille
def braille(p):
    a = np.asarray(p.im, dtype=np.float32) / 255
    a[LY0 * HR:LY1 * HR, LX0 * HR:LX1 * HR] = 0
    cols, rows = int(W / (PX / 2)) + 1, int(H / (PX * LH)) + 1
    im = Image.fromarray((a * 255).astype(np.uint8))
    g = np.asarray(im.resize((cols * 2, rows * 4), Image.Resampling.BOX), dtype=np.float32) / 255
    bits = [(0, 0, 0x01), (1, 0, 0x02), (2, 0, 0x04), (0, 1, 0x08), (1, 1, 0x10), (2, 1, 0x20), (3, 0, 0x40), (3, 1, 0x80)]
    lines = []
    for y in range(rows):
        row = ""
        for x in range(cols):
            v = sum(b for dy, dx, b in bits if g[y * 4 + dy, x * 2 + dx] > 0.28)
            row += chr(0x2800 + v) if v else " "
        lines.append(row.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"


(assets / "og-art.txt").write_text(braille(stars()), encoding="utf-8")
(assets / "og-post-art.txt").write_text(braille(crosshair()), encoding="utf-8")
print("wrote og-art.txt and og-post-art.txt, now run python3 og.py")
