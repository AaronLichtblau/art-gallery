#!/usr/bin/env python3
"""
Turn your full-size artwork into web-ready images and a gallery.json manifest.

Usage:
    pip install pillow
    python3 tools/build.py

Put originals in  originals/  (jpg, png, tiff, webp). The script writes
resized WebP files to  images/  at several widths, so visitors download a
small file for the grid and a bigger one only in the lightbox.

Optional metadata: create originals/metadata.json like
    {
      "sunset-study.jpg": {"title": "Sunset Study", "artist": "A. Painter",
                           "year": "2023", "medium": "Oil on canvas",
                           "featured": true}
    }
Anything not listed gets a title made from its filename.
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "originals"
OUT = ROOT / "images"
MANIFEST = ROOT / "gallery.json"

WIDTHS = [480, 960, 1600]   # thumbnail, medium, lightbox
QUALITY = 80                # WebP quality; 78-85 is visually lossless for art
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "work"


def dominant_color(im: Image.Image) -> str:
    tiny = im.convert("RGB").resize((1, 1), Image.LANCZOS)
    r, g, b = tiny.getpixel((0, 0))
    # lighten toward off-white so placeholders feel airy
    r, g, b = (int(c + (255 - c) * 0.55) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def main() -> int:
    if not SRC.exists():
        SRC.mkdir()
        print(f"Created {SRC}. Add your images there and re-run.")
        return 0

    meta = {}
    meta_file = SRC / "metadata.json"
    if meta_file.exists():
        meta = json.loads(meta_file.read_text())

    OUT.mkdir(exist_ok=True)
    files = sorted(p for p in SRC.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        print(f"No images found in {SRC}")

    works = []
    for p in files:
        slug = slugify(p.stem)
        with Image.open(p) as im:
            im = ImageOps.exif_transpose(im)       # respect phone/camera rotation
            w0, h0 = im.size
            if im.mode not in ("RGB", "L"):
                im = im.convert("RGB")
            color = dominant_color(im)

            sizes = []
            for tw in WIDTHS:
                if tw > w0 and sizes:               # never upscale
                    break
                tw = min(tw, w0)
                th = round(h0 * tw / w0)
                dest = OUT / f"{slug}-{tw}.webp"
                if (not dest.exists()) or dest.stat().st_mtime < p.stat().st_mtime:
                    im.resize((tw, th), Image.LANCZOS).save(
                        dest, "WEBP", quality=QUALITY, method=6)
                sizes.append({"src": f"images/{dest.name}", "w": tw})

        m = meta.get(p.name, {})
        works.append({
            "id": slug,
            "title": m.get("title", p.stem.replace("-", " ").replace("_", " ").title()),
            "artist": m.get("artist", ""),
            "year": m.get("year", ""),
            "medium": m.get("medium", ""),
            "alt": m.get("alt", ""),
            "featured": bool(m.get("featured", False)),
            "w": w0,
            "h": h0,
            "color": color,
            "sizes": sizes,
        })
        print(f"  {p.name}  ->  {len(sizes)} sizes")

    MANIFEST.write_text(json.dumps(works, indent=1))
    print(f"Wrote {MANIFEST.name} with {len(works)} works.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
