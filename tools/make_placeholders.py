#!/usr/bin/env python3
"""Make the placeholder images for hairbygerta.com.

Twenty-six photos on the old Wix site are licensed for Wix only, so this site
ships a placeholder in place of each one: a flat beige image (#e8e1da) with a
faint logo mark in the middle, with exactly the file name and pixel size of
the photo it stands in for. The owner can later save a real, licensed photo
over any placeholder and nothing else has to change.

This script writes the 52 placeholder files:

    images/<name>.jpg       full size
    images/sm/<name>.jpg    small copy (800 px on the long side)

It needs Pillow and nothing else. The mark is taken from images/logo.jpg.
All paths are worked out from where this script is, so it can be started
from any folder. The pixel sizes are written into the table below, so the
original photos are not needed.

Usage

    python tools/make_placeholders.py                 all 52 files
    python tools/make_placeholders.py --only g05      just g05 (full and small)
    python tools/make_placeholders.py --only g05,g06  several names
    python tools/make_placeholders.py --check         write nothing, only report
    python tools/make_placeholders.py --force         see the warning below

Real photos are safe. Without --force the script refuses to overwrite a file
that is not already a placeholder. A file counts as a placeholder when at
least 90 percent of its pixels are within 6 levels per channel of the beige
(232, 225, 218). Anything else (a real photo, a file that cannot be read as
an image) is kept and listed. --force overwrites those files too, so use it
only when you really want the photo gone.

The script never touches images/logo.jpg, images/g12.jpg or images/g13.jpg.

Exit status: 0 when every file asked for is a placeholder with the expected
bytes, 2 when at least one file was kept (or, with --check, is not the
expected placeholder), 1 on an error.

Running it twice gives the same bytes. A different Pillow version may encode
the JPEG slightly differently, the picture stays the same.
"""

import argparse
import io
import os
import sys

try:
    from PIL import Image, ImageChops
except ImportError:  # pragma: no cover
    sys.exit("This script needs Pillow. Install it with: python -m pip install Pillow")

# ---------------------------------------------------------------- settings

BEIGE = (232, 225, 218)      # #e8e1da, the flat background
INK = (0x55, 0x4F, 0x46)     # #554f46, the colour of the mark
MARK_OPACITY = 0.18          # how strongly the mark is laid over the beige
MARK_HEIGHT = 0.28           # mark height as a share of the shorter side
JPEG_QUALITY = 82
JPEG_SUBSAMPLING = "4:2:0"   # the picture has almost no colour detail, this halves the file

TOLERANCE = 6                # a pixel is "beige" within this many levels per channel
MIN_BEIGE_SHARE = 0.90       # a file is a placeholder from this share of beige pixels
BACKGROUND_TOLERANCE = 2     # the saved background must decode this close to BEIGE

# Pixel sizes of the photos the placeholders stand in for.
# name: ((full width, full height), (small width, small height))
SIZES = {
    "about-salon":       ((1200, 1600), (600, 800)),
    "brunette-balayage": ((1066, 1600), (533, 800)),
    "copper-waves":      ((1067, 1600), (533, 800)),
    "foils-highlights":  ((1600, 1066), (800, 533)),
    "g01":               ((1600, 843),  (800, 422)),
    "g02":               ((1600, 900),  (800, 450)),
    "g04":               ((1600, 1065), (800, 533)),
    "g05":               ((1600, 1066), (800, 533)),
    "g06":               ((1600, 985),  (800, 493)),
    "g07":               ((1600, 1066), (800, 533)),
    "g10":               ((1600, 1066), (800, 533)),
    "g14":               ((1600, 1064), (800, 532)),
    "g15":               ((1067, 1600), (533, 800)),
    "g16":               ((1200, 1600), (600, 800)),
    "g17":               ((1600, 1066), (800, 533)),
    "g18":               ((1600, 1066), (800, 533)),
    "g19":               ((1600, 1066), (800, 533)),
    "g20":               ((1600, 1064), (800, 532)),
    "g21":               ((1600, 1066), (800, 533)),
    "home-smile":        ((1200, 1600), (600, 800)),
    "home-styling":      ((1600, 1066), (800, 533)),
    "home-waves":        ((1600, 900),  (800, 450)),
    "makeup-red-lips":   ((1600, 802),  (800, 401)),
    "meet-extensions":   ((1200, 1600), (600, 800)),
    "svc-bridal":        ((1600, 1066), (800, 533)),
    "svc-haircut":       ((411, 523),   (411, 523)),
}

# The three licensed images. They are not placeholders and are never written.
NEVER_WRITE = ("logo", "g12", "g13")

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO = os.path.join(SITE, "images", "logo.jpg")

_BICUBIC = getattr(Image, "Resampling", Image).BICUBIC
_SUPERSAMPLE = 4

# ---------------------------------------------------------------- drawing


def _levels(image, low, high):
    """Stretch the range low..high to 0..255 and clip the rest."""
    span = float(high - low)
    table = [0 if v <= low else 255 if v >= high else int(round((v - low) * 255 / span))
             for v in range(256)]
    return image.point(table)


_logo_mask = None


def logo_mask():
    """The logo artwork as a mask: 255 where the logo is black, 0 where it is white.

    The logo is black artwork on white, so the mask is the inverted brightness,
    cropped to the artwork.
    """
    global _logo_mask
    if _logo_mask is None:
        if not os.path.isfile(LOGO):
            sys.exit("images/logo.jpg is missing, the mark is made from it.")
        with Image.open(LOGO) as logo:
            mask = ImageChops.invert(logo.convert("L"))
        box = _levels(mask, 31, 32).getbbox()
        if box is None:
            sys.exit("images/logo.jpg has no dark artwork, cannot make the mark.")
        _logo_mask = mask.crop(box)
    return _logo_mask


_mark_cache = {}


def mark_alpha(height):
    """The mark scaled to `height` px, as an alpha layer (0 to 18 percent of 255)."""
    if height not in _mark_cache:
        mask = logo_mask()
        width = max(1, int(round(mask.width * height / float(mask.height))))
        # Enlarge four times, sharpen the soft edge of the small logo file,
        # then average back down. This gives clean edges at every size and
        # removes the JPEG speckle of the logo file from the flat area.
        big = mask.resize((width * _SUPERSAMPLE, height * _SUPERSAMPLE), _BICUBIC)
        clean = _levels(big, 64, 192).reduce(_SUPERSAMPLE)
        _mark_cache[height] = clean.point(
            [int(round(v * MARK_OPACITY)) for v in range(256)])
    return _mark_cache[height]


def render(size):
    """A placeholder picture of `size` (width, height)."""
    width, height = size
    canvas = Image.new("RGB", size, BEIGE)
    alpha = mark_alpha(max(1, int(round(min(width, height) * MARK_HEIGHT))))
    tile = Image.composite(Image.new("RGB", alpha.size, INK),
                           Image.new("RGB", alpha.size, BEIGE), alpha)
    canvas.paste(tile, ((width - alpha.width) // 2, (height - alpha.height) // 2))
    return canvas


def encode(image):
    """The JPEG bytes of a placeholder: quality 82, no metadata."""
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=JPEG_QUALITY, subsampling=JPEG_SUBSAMPLING,
               optimize=True, progressive=False)
    return buffer.getvalue()


# ---------------------------------------------------------------- testing


def beige_share(image):
    """Share (0 to 1) of pixels within TOLERANCE levels per channel of BEIGE."""
    image = image.convert("RGB")
    near = None
    for band, target in zip(image.split(), BEIGE):
        hit = band.point([255 if abs(v - target) <= TOLERANCE else 0 for v in range(256)])
        near = hit if near is None else ImageChops.darker(near, hit)
    return near.histogram()[255] / float(image.width * image.height)


def is_placeholder_image(image):
    return beige_share(image) >= MIN_BEIGE_SHARE


def is_placeholder_file(path):
    """True when the file at `path` is a placeholder. False for a real photo
    and for anything that cannot be read as an image."""
    try:
        with Image.open(path) as image:
            return is_placeholder_image(image)
    except Exception:
        return False


def placeholder_bytes(size):
    """Render, encode and double check one placeholder. Returns the JPEG bytes."""
    data = encode(render(size))
    with Image.open(io.BytesIO(data)) as check:
        check = check.convert("RGB")
        if check.size != tuple(size):
            raise RuntimeError("wrong size after encoding: %r" % (check.size,))
        w, h = check.size
        for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            pixel = check.getpixel(corner)
            if max(abs(a - b) for a, b in zip(pixel, BEIGE)) > BACKGROUND_TOLERANCE:
                raise RuntimeError("background decodes to %r, expected %r" % (pixel, BEIGE))
        if not is_placeholder_image(check):
            raise RuntimeError("the result does not pass the placeholder test")
    return data


# ---------------------------------------------------------------- command line


def targets(names):
    """(label, path, size) for every file that belongs to `names`."""
    for name in names:
        full, small = SIZES[name]
        yield ("images/%s.jpg" % name, os.path.join(SITE, "images", name + ".jpg"), full)
        yield ("images/sm/%s.jpg" % name, os.path.join(SITE, "images", "sm", name + ".jpg"), small)


def parse_names(only):
    if not only:
        return sorted(SIZES)
    names = []
    for chunk in only:
        for name in chunk.split(","):
            name = name.strip()
            if name.lower().endswith(".jpg"):
                name = name[:-4]
            if not name:
                continue
            if name in NEVER_WRITE:
                sys.exit("%s is a licensed image, not a placeholder. Nothing written." % name)
            if name not in SIZES:
                sys.exit("Unknown name: %s. Known names: %s" % (name, ", ".join(sorted(SIZES))))
            if name not in names:
                names.append(name)
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Make the beige placeholder images (images/ and images/sm/).")
    parser.add_argument("--only", action="append", metavar="NAME",
                        help="make only this name, full and small (repeat or separate with commas)")
    parser.add_argument("--force", action="store_true",
                        help="also overwrite files that are not placeholders (real photos are lost)")
    parser.add_argument("--check", action="store_true",
                        help="write nothing, only report the state of each file")
    args = parser.parse_args(argv)
    names = parse_names(args.only)

    counts = {"created": 0, "updated": 0, "unchanged": 0, "kept": 0,
              "missing": 0, "differs": 0, "photo": 0}
    for label, path, size in targets(names):
        data = placeholder_bytes(size)
        if not os.path.exists(path):
            state = "missing" if args.check else "created"
        else:
            with open(path, "rb") as handle:
                same = handle.read() == data
            if same:
                state = "unchanged"
            elif is_placeholder_file(path):
                state = "differs" if args.check else "updated"
            elif args.check:
                state = "photo"
            elif args.force:
                state = "updated"
            else:
                state = "kept"
        if state in ("created", "updated"):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as handle:
                handle.write(data)
        counts[state] += 1
        note = ""
        if state == "kept":
            note = "  (not a placeholder, left alone, --force would overwrite it)"
        elif state == "photo":
            note = "  (not a placeholder)"
        print("%-9s %-34s %4d x %-4d %6d bytes%s" % (state, label, size[0], size[1], len(data), note))

    total = sum(counts.values())
    summary = ", ".join("%d %s" % (n, k) for k, n in counts.items() if n)
    print("%d files: %s" % (total, summary))
    if counts["kept"]:
        print("Kept files hold something that is not a placeholder (a real photo?). "
              "They were not changed.")
    if counts["kept"] or counts["missing"] or counts["differs"] or counts["photo"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
