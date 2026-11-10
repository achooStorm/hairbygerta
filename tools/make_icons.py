#!/usr/bin/env python3
"""Rebuild the browser icons of hairbygerta.com from the salon logo.

Source (the only input, a licensed file):
    images/logo.jpg                  black artwork on a white background

Output (all four are made from the logo and nothing else):
    favicon.ico                      one file holding a 32 px and a 48 px image
    images/favicon.png               64 x 64
    images/apple-touch-icon.png      180 x 180, opaque, for phone home screens (iPhone)
    images/icon-192.png              192 x 192, opaque, for phone home screens (Android)

How to run it (needs Pillow, nothing else):
    python tools/make_icons.py                 write the three files
    python tools/make_icons.py --check         write nothing, exit 1 if a file
                                               on disk differs from a fresh build
    python tools/make_icons.py --report FILE   also write a JSON list with the
                                               size, byte count and SHA-256 of
                                               each file

Every path is worked out from the place of this script, so it can be started
from any folder. The output holds no dates and no random values: the same
logo and the same Pillow version always give the same bytes.

What it does to the artwork: finds the box around the ink, scales that box
to fit the icon with a small margin, centres it on the page background colour
and, for the small sizes only, darkens and sharpens the thin strokes a little
so the logo still reads at 32 px.
"""

import argparse
import hashlib
import io
import json
import struct
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageFilter
except ImportError:
    sys.exit("make_icons: this script needs Pillow (python -m pip install Pillow)")

ROOT = Path(__file__).resolve().parent.parent
LOGO = "images/logo.jpg"

BACKGROUND = (0xFE, 0xFE, 0xFD)  # the page background, #fefefd

# pixel size: (margin in px above and below the artwork,
#              ink gamma, above 1 makes grey strokes darker,
#              sharpening in percent, 0 is off)
RENDER = {
    32: (1, 1.5, 80),
    48: (2, 1.35, 60),
    64: (3, 1.25, 40),
    180: (14, 1.0, 0),
    192: (15, 1.0, 0),
}

# output file: (container, the pixel sizes it holds)
ICONS = {
    "favicon.ico": ("ico", (32, 48)),
    "images/favicon.png": ("png", (64,)),
    "images/apple-touch-icon.png": ("png", (180,)),
    "images/icon-192.png": ("png", (192,)),
}

WHITE_POINT = 244  # JPEG haze at or above this value counts as pure white
INK_LIMIT = 200  # anything darker than this belongs to the artwork


def load_artwork():
    """Return the logo with a clean white background and the box around its ink."""
    logo = Image.open(ROOT / LOGO).convert("RGB")
    lut = [255 if v >= WHITE_POINT else round(v * 255 / WHITE_POINT) for v in range(256)]
    logo = logo.point(lut * 3)
    box = logo.convert("L").point(lambda v: 255 if v < INK_LIMIT else 0).getbbox()
    if box is None:
        sys.exit("make_icons: no artwork found in " + LOGO)
    return logo, box


def render(logo, box, size):
    """One opaque RGB icon of size x size px with the artwork centred."""
    margin, gamma, sharpen = RENDER[size]
    room = size - 2 * margin
    box_w, box_h = box[2] - box[0], box[3] - box[1]
    scale = min(room / box_w, room / box_h)
    art_w, art_h = max(1, round(box_w * scale)), max(1, round(box_h * scale))
    art = logo.resize((art_w, art_h), Image.Resampling.LANCZOS, box=box)
    if sharpen:
        art = art.filter(ImageFilter.UnsharpMask(radius=0.6, percent=sharpen, threshold=0))
    if gamma != 1.0:
        lut = [round(255 * (v / 255) ** gamma) for v in range(256)]
        art = art.point(lut * 3)
    icon = Image.new("RGB", (size, size), (255, 255, 255))
    icon.paste(art, ((size - art_w) // 2, (size - art_h) // 2))
    # multiply turns white into the background colour and leaves black black
    return ImageChops.multiply(icon, Image.new("RGB", (size, size), BACKGROUND))


def png_bytes(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def ico_bytes(images):
    """An .ico file with one PNG-compressed 32-bit image per entry, smallest first."""
    blobs = [png_bytes(image.convert("RGBA")) for image in images]
    head = struct.pack("<HHH", 0, 1, len(images))
    offset = len(head) + 16 * len(images)
    for image, blob in zip(images, blobs):
        width, height = image.size
        head += struct.pack("<BBBBHHII", width % 256, height % 256, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    return head + b"".join(blobs)


def build():
    """Return {relative file name: (bytes, sizes)} for every icon."""
    logo, box = load_artwork()
    made = {}
    for name, (container, sizes) in ICONS.items():
        images = [render(logo, box, size) for size in sorted(sizes)]
        for image in images:
            if image.mode != "RGB" or image.getpixel((0, 0)) != BACKGROUND:
                sys.exit("make_icons: " + name + " did not come out opaque on the background colour")
        data = ico_bytes(images) if container == "ico" else png_bytes(images[0])
        made[name] = (data, sorted(sizes))
    return made


def main():
    parser = argparse.ArgumentParser(description="Rebuild the site icons from images/logo.jpg.")
    parser.add_argument("--check", action="store_true",
                        help="write nothing, exit 1 if a file on disk differs from a fresh build")
    parser.add_argument("--report", metavar="FILE",
                        help="also write a JSON list describing the icon files")
    args = parser.parse_args()

    made = build()
    report, stale = [], []
    for name, (data, sizes) in made.items():
        target = ROOT / name
        if args.check:
            if not target.is_file() or target.read_bytes() != data:
                stale.append(name)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        entry = {
            "file": name,
            "sizes": ["%dx%d" % (size, size) for size in sizes],
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "derived_from": LOGO,
            "status": "allowed-derivative",
        }
        report.append(entry)
        print("%-28s %-12s %6d bytes  sha256 %s"
              % (name, ",".join(entry["sizes"]), entry["bytes"], entry["sha256"]))

    if args.report:
        with open(args.report, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
    if stale:
        print("differs from a fresh build: " + ", ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
