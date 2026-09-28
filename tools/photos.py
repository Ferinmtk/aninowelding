#!/usr/bin/env python3
"""Turn the client's original photos into fast web images + gallery.json.

    python3 tools/photos.py

Reads photos-original/, writes assets/img/gallery/<id>-800.webp (thumb) and
<id>-1600.webp (lightbox), plus gallery.json which build.py renders.
Strips EXIF (phone photos can carry GPS location). Needs ImageMagick (`magick`).

To add a photo: drop it in photos-original/, add a line to PHOTOS, re-run.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "photos-original"
OUT = ROOT / "assets" / "img" / "gallery"

# Crop that removes the "Samsung Galaxy A05" watermark in the bottom-left corner.
NO_WATERMARK = "100%x93%+0+0"
NO_WATERMARK_WIDE = "100%x87%+0+0"  # landscape shots: watermark sits higher

# (file, category, caption, crop geometry or None). Order = gallery order.
PHOTOS = [
    ("p08.jpg", "roofing", "Gazebo shade with decorative cut-steel panels", NO_WATERMARK),
    ("p04.jpg", "gates", "Black steel gate with lattice top panels", None),
    ("p01.jpg", "doors", "Double steel main door with side panels", NO_WATERMARK),
    ("p11.jpg", "windows", "Window grills fitted on a multi-storey building", NO_WATERMARK),
    ("p03.jpg", "doors", "Steel door with timber-look inserts", NO_WATERMARK),
    ("p18.jpg", "gates", "Grey steel gate with vertical bars", NO_WATERMARK_WIDE),
    ("p06.jpg", "roofing", "Steel roof structure under construction", NO_WATERMARK_WIDE),
    ("p14.jpg", "grills", "Full-height window grill with opening sashes", "100%x88%+0+180"),
    ("p05.jpg", "gates", "Steel gate with grid panel design", NO_WATERMARK_WIDE),
    ("p02.jpg", "doors", "Single steel door with brass-look accents", NO_WATERMARK),
    ("p16.jpg", "windows", "Steel window with security grill, fitted", None),
    ("p09.jpg", "gates", "Modern slatted steel gate", "543x655+0+62"),
    ("p13.jpg", "doors", "Steel pedestrian door with frame", NO_WATERMARK),
    ("p15.jpg", "windows", "Steel window frame with bars", NO_WATERMARK),
    ("p17.jpg", "grills", "Steel window grill, ready for fitting", NO_WATERMARK),
    ("p07.jpg", "windows", "Steel window frame in the workshop", None),
    # Cropped out of a phone screenshot, so lower quality.
    ("p10.jpg", "doors", "Double steel door with louvred panels", "945x1190+0+492"),
]


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout.strip()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    items = []
    for fname, cat, caption, crop in PHOTOS:
        src = SRC / fname
        if not src.exists():
            print(f"  skip {fname} (missing)")
            continue
        pid = src.stem
        base = ["magick", str(src), "-auto-orient"]
        if crop:
            base += ["-crop", crop, "+repage"]
        base += ["-strip"]
        thumb = OUT / f"{pid}-800.webp"
        full = OUT / f"{pid}-1600.webp"
        run(*base, "-resize", "800x800>", "-quality", "72", str(thumb))
        run(*base, "-resize", "1600x1600>", "-quality", "78", str(full))
        tw, th = run("magick", "identify", "-format", "%w %h", str(thumb)).split()
        items.append({
            "id": pid,
            "category": cat,
            "caption": caption,
            "thumb": f"assets/img/gallery/{thumb.name}",
            "full": f"assets/img/gallery/{full.name}",
            "tw": int(tw),
            "th": int(th),
        })
        kb = (thumb.stat().st_size + full.stat().st_size) // 1024
        print(f"  {fname:8} → {cat:8} {tw}x{th}  ({kb} KB total)")
    (OUT / "gallery.json").write_text(json.dumps(items, indent=2))
    print(f"Wrote {len(items)} photos to {OUT.relative_to(ROOT)}/gallery.json")


if __name__ == "__main__":
    main()
