#!/usr/bin/env python3
"""Make the share image of hairbygerta.com: the picture a link preview shows (Facebook, Instagram, WhatsApp,
iMessage, Google and the rest), named by og:image on every page.

    python tools/make_share_image.py           write images/share.jpg and record it in image-manifest.json
    python tools/make_share_image.py --check   write nothing, exit 1 when images/share.jpg is not what the
                                               manifest records

It needs Pillow (the Python setup in hairbygerta-env has it). Every path is worked out from where this
script is, so it can be started from any folder.

What it makes: 1200 x 630 px, the size link previews ask for. The owner's photo g13 on the left and g12 on
the right, each at full height, and between them on the beige of the site the logo, the business name, the
role and the place, in the two fonts of the site (folder fonts). The manifest records the box of each photo,
of the logo and of each line of text ("parts").

It uses only files that may be published: images/logo.jpg, images/g12.jpg and images/g13.jpg (the three
licensed images, see README.md) and the fonts. The manifest records the file under "composites" with the
place of each picture in it, so qa/licensing_check.py can prove that every photo in it is one of the
allowed ones and nothing else (build contract, decision 39).

To show other photos once the owner has her own (they must be photos she owns, recorded as owner-photo in
the manifest, or the three allowed ones), change LEFT and RIGHT below and run the script again.
"""

import argparse
import hashlib
import io
import json
import os
import sys

sys.dont_write_bytecode = True

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFont
except ImportError:
    sys.exit("make_share_image: this script needs Pillow (python -m pip install Pillow)")

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = "images/share.jpg"
MANIFEST = "image-manifest.json"
WIDTH, HEIGHT = 1200, 630

LEFT, RIGHT, LOGO = "images/g13.jpg", "images/g12.jpg", "images/logo.jpg"
SERIF = "fonts/bodoni-moda-italic-latin.woff2"
SANS = "fonts/figtree-latin.woff2"

BEIGE = (0xE8, 0xE1, 0xDA)      # --beige of the stylesheet
INK = (0x1D, 0x15, 0x09)        # --ink of the stylesheet

# The words, all facts the site states on every page.
NAME = "Hair & Makeup by Gerta"
ROLE = "Hair Stylist & Makeup Artist"
PLACE = "Le Vigne Hair Salon, Staten Island, NY"

LOGO_HEIGHT = 196               # px, the drawing of the logo
NAME_SIZE = 38                  # px, Bodoni Moda Italic bold
LINE_SIZE = 23                  # px, Figtree regular
QUALITY = 86


def photo(rel, width, height):
    """One photo at the full height of the image, cut to width x height around its middle."""
    im = Image.open(os.path.join(SITE, *rel.split("/"))).convert("RGB")
    scale = height / im.height
    w = im.width * scale
    if w < width:                                   # a photo that is too narrow is cut at top and bottom instead
        scale = width / im.width
        h = im.height * scale
        top = (h - height) / 2 / scale
        box = (0, top, im.width, top + height / scale)
    else:
        left = (w - width) / 2 / scale
        box = (left, 0, left + width / scale, im.height)
    return im.resize((width, height), Image.Resampling.LANCZOS, box=box), [round(v, 2) for v in box]


def logo_artwork(height):
    """The black drawing of the logo on the beige, cut to the box around its ink, height px tall."""
    im = Image.open(os.path.join(SITE, *LOGO.split("/"))).convert("RGB")
    white = 244                                     # JPEG haze at or above this counts as pure white
    im = im.point([255 if v >= white else round(v * 255 / white) for v in range(256)] * 3)
    box = im.convert("L").point(lambda v: 255 if v < 200 else 0).getbbox()
    width = max(1, round((box[2] - box[0]) * height / (box[3] - box[1])))
    art = im.resize((width, height), Image.Resampling.LANCZOS, box=box)
    return ImageChops.multiply(art, Image.new("RGB", art.size, BEIGE)), list(box)


def font(rel, size, weight):
    f = ImageFont.truetype(os.path.join(SITE, *rel.split("/")), size)
    f.set_variation_by_axes([weight])
    return f


def build():
    """-> (JPEG bytes, the parts as the manifest records them)"""
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BEIGE)
    side = round(HEIGHT * 900 / 1600)               # 354: a photo of 900 x 1600 px at full height
    left, left_box = photo(LEFT, side, HEIGHT)
    right, right_box = photo(RIGHT, side, HEIGHT)
    canvas.paste(left, (0, 0))
    canvas.paste(right, (WIDTH - side, 0))

    name_font, line_font = font(SERIF, NAME_SIZE, 700), font(SANS, LINE_SIZE, 400)
    art, art_box = logo_artwork(LOGO_HEIGHT)
    draw = ImageDraw.Draw(canvas)
    middle = WIDTH // 2

    def text_size(text, f):
        x0, y0, x1, y1 = draw.textbbox((0, 0), text, font=f)
        return x1 - x0, y1 - y0, x0, y0

    # the block: logo, 26 px, name, 18 px, dotted rule, 18 px, role, 10 px, place. Centred in the height.
    name_w, name_h, name_x0, name_y0 = text_size(NAME, name_font)
    role_w, role_h, role_x0, role_y0 = text_size(ROLE, line_font)
    place_w, place_h, place_x0, place_y0 = text_size(PLACE, line_font)
    gaps = (26, 18, 18, 10)
    total = art.height + gaps[0] + name_h + gaps[1] + 1 + gaps[2] + role_h + gaps[3] + place_h
    y = (HEIGHT - total) // 2
    art_at = (middle - art.width // 2, y)
    canvas.paste(art, art_at)
    y += art.height + gaps[0]
    text_boxes = []                                 # where each line of text stands, for the licensing check

    def line(text, f, w, h, x0, y0, top):
        left = middle - w // 2
        draw.text((left - x0, top - y0), text, font=f, fill=INK)
        text_boxes.append([left, top, left + w, top + h])

    line(NAME, name_font, name_w, name_h, name_x0, name_y0, y)
    y += name_h + gaps[1]
    rule = 300                                      # the dotted rule of the beige box on the home page
    for x in range(middle - rule // 2, middle + rule // 2, 3):
        draw.point((x, y), fill=INK)
    text_boxes.append([middle - rule // 2, y, middle + rule // 2, y + 1])
    y += 1 + gaps[2]
    line(ROLE, line_font, role_w, role_h, role_x0, role_y0, y)
    y += role_h + gaps[3]
    line(PLACE, line_font, place_w, place_h, place_x0, place_y0, y)

    out = io.BytesIO()
    canvas.save(out, "JPEG", quality=QUALITY, optimize=True, progressive=True)     # no Exif, no ICC, no comment
    parts = [
        {"source": LEFT, "kind": "photo", "box": [0, 0, side, HEIGHT], "source_box": left_box},
        {"source": RIGHT, "kind": "photo", "box": [WIDTH - side, 0, WIDTH, HEIGHT], "source_box": right_box},
        {"source": LOGO, "kind": "artwork", "box": [art_at[0], art_at[1], art_at[0] + art.width, art_at[1] + art.height], "source_box": art_box},
    ] + [{"kind": "text", "box": box} for box in text_boxes]
    return out.getvalue(), parts


def record(data, parts):
    return {
        "file": OUT, "status": "allowed-derivative", "use": "og:image, the picture of link previews",
        "width": WIDTH, "height": HEIGHT, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
        "parts": parts,
        "text": [NAME, ROLE, PLACE],
        "made_by": "tools/make_share_image.py",
    }


def main():
    parser = argparse.ArgumentParser(description="Make images/share.jpg, the picture of link previews.")
    parser.add_argument("--check", action="store_true", help="write nothing, exit 1 when the file is not what the manifest records")
    args = parser.parse_args()
    path = os.path.join(SITE, MANIFEST)
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    if args.check:
        recorded = next((r for r in manifest.get("composites") or [] if r.get("file") == OUT), None)
        try:
            with open(os.path.join(SITE, *OUT.split("/")), "rb") as f:
                on_disk = hashlib.sha256(f.read()).hexdigest()
        except OSError:
            on_disk = None
        ok = recorded is not None and on_disk == recorded.get("sha256")
        print("%s: %s" % (OUT, "as recorded in %s" % MANIFEST if ok else "NOT as recorded in %s (run this script again)" % MANIFEST))
        return 0 if ok else 1
    data, parts = build()
    with open(os.path.join(SITE, *OUT.split("/")), "wb") as f:
        f.write(data)
    composites = [r for r in manifest.get("composites") or [] if r.get("file") != OUT] + [record(data, parts)]
    manifest["composites"] = composites
    with open(path, "wb") as f:                     # the layout build_pages.py writes: 2 spaces, ASCII, LF
        f.write((json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii"))
    print("%s  %d x %d  %d bytes  sha256 %s" % (OUT, WIDTH, HEIGHT, len(data), hashlib.sha256(data).hexdigest()))
    print("%s: recorded under composites" % MANIFEST)
    return 0


if __name__ == "__main__":
    sys.exit(main())
