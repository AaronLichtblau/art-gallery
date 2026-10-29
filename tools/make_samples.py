#!/usr/bin/env python3
"""Generate placeholder 'paintings' so you can preview the layout.
Delete the samples (originals/sample-*) once you add real artwork."""
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent.parent / "originals"
OUT.mkdir(exist_ok=True)
random.seed(7)

SIZES = [  # (w, h)
    (1600, 1200), (1200, 1600), (2400, 1000), (1400, 1400), (1000, 1800),
    (1800, 1200), (1500, 1500), (2200, 1100), (1200, 1500), (1600, 1000),
    (1100, 1700), (1800, 1800), (1500, 1100), (1000, 1000), (2000, 1200),
    (1200, 1800),
]
PALETTES = [
    [(236, 200, 140), (200, 90, 70), (60, 70, 110)],
    [(180, 205, 190), (70, 110, 100), (240, 232, 210)],
    [(240, 170, 160), (130, 90, 140), (250, 235, 215)],
    [(30, 50, 90), (240, 190, 70), (210, 220, 235)],
    [(120, 150, 90), (230, 215, 160), (70, 60, 50)],
]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


for n, (w, h) in enumerate(SIZES, 1):
    pal = PALETTES[n % len(PALETTES)]
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        c = lerp(pal[0], pal[2], y / h)
        for x in range(0, w):
            px[x, y] = c
    d = ImageDraw.Draw(im, "RGBA")
    for _ in range(14):
        cx, cy = random.randint(0, w), random.randint(0, h)
        r = random.randint(min(w, h) // 8, min(w, h) // 2)
        col = random.choice(pal) + (random.randint(60, 150),)
        if random.random() < .5:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        else:
            d.rectangle([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=col)
    im = im.filter(ImageFilter.GaussianBlur(10))
    im.save(OUT / f"sample-{n:02d}.jpg", quality=88)

print(f"Wrote {len(SIZES)} sample images to {OUT}")
