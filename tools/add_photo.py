#!/usr/bin/env python3
"""Put one of Gerta's own photos in the place of a placeholder, ready to publish.

    python tools/add_photo.py --list
        the 26 places that still wait for a photo: name, the shape the page shows it in, page. A page leaves
        such a place out until its photo is in (build contract, decision 44), and every page shows a photo
        in a tall frame, 9 to 16

    python tools/add_photo.py PHOTO NAME --alt "What the photo shows"
        puts the photo PHOTO (a .jpg, .jpeg, .png or .webp file, anywhere on this computer) in the place NAME

    python tools/add_photo.py --batch LIST.csv
        many photos at once. LIST.csv has one line per photo: photo,name,alt
        (a header line "photo,name,alt" is allowed; the photo path is read from the folder of LIST.csv)

    Add --dry-run to see what would happen without writing anything.

It needs Pillow (the Python setup in hairbygerta-env has it). Every path inside the site is worked out from
where this script is.

WHICH PHOTOS
    Only photos Gerta took herself or has written permission for (MIGRATION.md, section 6, "Which photos you
    may use"). Never a photo of the old Wix site: the script refuses a file whose fingerprint is on the list
    of Wix-only photos (tools/restricted-hashes.txt), but a resaved Wix photo has another fingerprint, so
    the list is no proof. Ask a client before her face goes on the site.

    Keep the original photos OUTSIDE the site folder, for example in a folder new-photos next to it
    (projects/new-photos). Originals from a phone carry the place where they were taken. A folder named
    new-photos inside the site folder is kept out of git too (.gitignore and the commit guard), but the QA
    suite then reports it as a leftover until it is moved out.

WHAT IT DOES WITH A PHOTO
    1. Turns it upright (phones store many photos lying on their side with a note to turn them).
    2. Converts its colours to sRGB, the colours of the web, when it carries another colour profile.
    3. Makes images/NAME.jpg (at most 1600 px on the long side), images/sm/NAME.jpg (at most 800 px) and a
       WebP copy of each (images/NAME.webp, images/sm/NAME.webp). WebP files are about a third smaller and
       every current browser shows them first, the JPG files are for the rest. None of the four files keeps
       anything but the picture: no place, no date, no camera, no name.
    4. Writes the alt text (the words a screen reader says for the photo) into every content file that shows
       the place NAME.
    5. Takes NAME out of the list PLACEHOLDERS in tools/build_pages.py, records the WebP copies in
       image-manifest.json and builds the pages. The build records the photo as owner-photo with its
       fingerprints (build contract, decision 27).
    A photo is never made larger than it is. One smaller than 800 px on its long side is refused: it would
    look soft on a phone.

AFTERWARDS
    Look at the pages (README.md, "Looking at the site on this computer"), then run
        python tools/licensing_check.py
    and the QA suite, and commit. The photo goes live only when the commit is pushed to main.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True

try:
    from PIL import Image, ImageCms, ImageOps
except ImportError:
    sys.exit("add_photo: this script needs Pillow (python -m pip install Pillow)")

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(SITE, "tools", "build_pages.py")
MANIFEST = os.path.join(SITE, "image-manifest.json")
RESTRICTED = os.path.join(SITE, "tools", "restricted-hashes.txt")
CONTENT = os.path.join(SITE, "content")

FULL, SMALL, LEAST = 1600, 800, 800         # px on the long side
JPG_QUALITY, WEBP_QUALITY = 82, 80
READABLE = (".jpg", ".jpeg", ".png", ".webp")


class Refused(Exception):
    """A photo that cannot be used, with the reason in plain words."""


# ---------------------------------------------------------------- what the site knows

def placeholders():
    """The names in the list PLACEHOLDERS of tools/build_pages.py, in its order."""
    text = open(BUILD, encoding="utf-8").read()
    block = re.search(r"^PLACEHOLDERS = \[\n(.*?)^\]", text, re.M | re.S)
    if not block:
        raise SystemExit("add_photo: the list PLACEHOLDERS was not found in tools/build_pages.py")
    return re.findall(r'^\s+"([^"]+)",\s*$', block.group(1), re.M)


def places():
    """{name: [(content file, page, the size the page shows it at or None)]} for every image slot of the content files."""
    found = {}

    def walk(value, rel, page):
        if isinstance(value, dict):
            if isinstance(value.get("file"), str) and "alt" in value:
                size = (value["width"], value["height"]) if isinstance(value.get("width"), int) and isinstance(value.get("height"), int) else None
                found.setdefault(value["file"], []).append((rel, page, size))
            for item in value.values():
                walk(item, rel, page)
        elif isinstance(value, list):
            for item in value:
                walk(item, rel, page)

    for name in sorted(os.listdir(CONTENT)):
        if name.endswith(".json"):
            data = json.load(open(os.path.join(CONTENT, name), encoding="utf-8"))
            walk(data, "content/" + name, data.get("path", name))
    return found


def restricted():
    try:
        return {line.split()[0].lower() for line in open(RESTRICTED, encoding="utf-8") if re.match(r"[0-9a-fA-F]{64}", line)}
    except OSError:
        return set()


# ---------------------------------------------------------------- the photo

def load(path):
    """The photo upright, in sRGB, RGB without transparency, and nothing else of the file."""
    ext = os.path.splitext(path)[1].lower()
    if ext in (".heic", ".heif"):
        raise Refused("%s is a HEIC photo (iPhone). Save it as JPG first: on the iPhone, Settings, Camera, Formats, "
                      "Most Compatible, or send it to the computer by email, which turns it into JPG" % path)
    if ext not in READABLE:
        raise Refused("%s is not a .jpg, .jpeg, .png or .webp file" % path)
    data = open(path, "rb").read()
    if hashlib.sha256(data).hexdigest() in restricted():
        raise Refused("%s is one of the Wix-only photos (its fingerprint is in tools/restricted-hashes.txt). It may never "
                      "be used outside Wix" % path)
    im = Image.open(io.BytesIO(data))
    im.load()
    im = ImageOps.exif_transpose(im)                # upright, and the turn note is used up
    profile = im.info.get("icc_profile")
    if profile:
        try:
            src = ImageCms.ImageCmsProfile(io.BytesIO(profile))
            im = ImageCms.profileToProfile(im.convert("RGB"), src, ImageCms.createProfile("sRGB"), outputMode="RGB")
        except Exception:
            im = im.convert("RGB")                  # an unreadable profile: the colours stay as they are
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (254, 254, 253))
        flat.paste(im, mask=im.getchannel("A"))
        im = flat
    im = im.convert("RGB")
    clean = Image.new("RGB", im.size)               # a fresh picture: no Exif, no XMP, no comment, no profile
    clean.paste(im)
    return clean


def sized(im, long_side):
    if max(im.size) <= long_side:
        return im.copy()
    scale = long_side / float(max(im.size))
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.Resampling.LANCZOS)


def encode(im, kind):
    out = io.BytesIO()
    if kind == "jpg":
        im.save(out, "JPEG", quality=JPG_QUALITY, optimize=True, progressive=True)
    else:
        im.save(out, "WEBP", quality=WEBP_QUALITY, method=6)
    return out.getvalue()


def record(rel, data, im):
    return {"file": rel, "width": im.width, "height": im.height, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


# ---------------------------------------------------------------- writing

def set_alt(text, name, alt):
    """The content file text with the alt of every slot of name set to alt. -> (new text, how many slots)."""
    count = 0
    out, pos = [], 0
    for m in re.finditer(r'"file"\s*:\s*"%s"' % re.escape(name), text):
        start = text.rfind("{", 0, m.start())
        end = text.find("}", m.end())
        obj = text[start:end + 1]
        new_obj, n = re.subn(r'("alt"\s*:\s*)"(?:[^"\\]|\\.)*"', lambda a: a.group(1) + json.dumps(alt, ensure_ascii=False), obj, count=1)
        if n:
            out.append(text[pos:start])
            out.append(new_obj)
            pos = end + 1
            count += 1
    out.append(text[pos:])
    return "".join(out), count


def add(photo, name, alt, dry, names, where):
    if name not in names:
        raise Refused('"%s" is not a place that shows a placeholder. Run --list for the names' % name)
    if not where.get(name):
        raise Refused('no page shows the place "%s" today (run --list), so a photo put there would not be seen. '
                      "Pick a place that a page shows" % name)
    if not alt or not alt.strip():
        raise Refused("the photo for %s needs an alt text: a few words that say what it shows" % name)
    im = load(photo)
    if max(im.size) < LEAST:
        raise Refused("%s is only %d x %d px. It needs at least %d px on its long side" % (photo, im.width, im.height, LEAST))
    full, small = sized(im, FULL), sized(im, SMALL)
    files = {
        "images/%s.jpg" % name: (encode(full, "jpg"), full), "images/sm/%s.jpg" % name: (encode(small, "jpg"), small),
        "images/%s.webp" % name: (encode(full, "webp"), full), "images/sm/%s.webp" % name: (encode(small, "webp"), small),
    }
    notes = []
    for rel, page, size in where.get(name, []):
        if size and (size[0] > size[1]) != (full.width > full.height):
            notes.append("%s shows it %s (%d x %d), the photo is %s: the page will crop it" % (
                page, "wide" if size[0] > size[1] else "tall", size[0], size[1], "wide" if full.width > full.height else "tall"))
    print("%s -> %s: %d x %d px, %s" % (photo, name, full.width, full.height,
                                         ", ".join("%s %d KB" % (rel, len(data) // 1024) for rel, (data, _im) in files.items())))
    for note in notes:
        print("  note: " + note)
    if dry:
        return
    for rel, (data, _im) in files.items():
        with open(os.path.join(SITE, *rel.split("/")), "wb") as f:
            f.write(data)
    # the content files: the alt of every slot that shows the place
    slots = 0
    for rel in sorted({rel for rel, _page, _size in where.get(name, [])}):
        path = os.path.join(SITE, *rel.split("/"))
        text = open(path, encoding="utf-8").read()
        new, n = set_alt(text, name, alt.strip())
        json.loads(new)                             # still valid JSON, or stop before writing
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        slots += n
    # the list PLACEHOLDERS
    text = open(BUILD, encoding="utf-8").read()
    new = re.sub(r'^    "%s",\n' % re.escape(name), "", text, count=1, flags=re.M)
    with open(BUILD, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    # the WebP copies in the manifest (the build records the JPG files itself)
    manifest = json.load(open(MANIFEST, encoding="utf-8"))
    webp = record("images/%s.webp" % name, *files["images/%s.webp" % name])
    webp["sm"] = record("images/sm/%s.webp" % name, *files["images/sm/%s.webp" % name])
    manifest["images"][name]["webp"] = webp
    with open(MANIFEST, "wb") as f:
        f.write((json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii"))
    print("  alt text written into %d slot%s, %s taken out of PLACEHOLDERS" % (slots, "" if slots == 1 else "s", name))


def main():
    ap = argparse.ArgumentParser(description="Put one of Gerta's own photos in the place of a placeholder.")
    ap.add_argument("photo", nargs="?", help="the photo file")
    ap.add_argument("name", nargs="?", help="the place, for example g05 (see --list)")
    ap.add_argument("--alt", help="what the photo shows, in a few words")
    ap.add_argument("--batch", metavar="LIST.csv", help="many photos: one line photo,name,alt per photo")
    ap.add_argument("--list", action="store_true", help="show the places that still wait for a photo")
    ap.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    args = ap.parse_args()

    names, where = placeholders(), places()
    if args.list:
        # Every page shows a photo in a tall frame since the redesign of 12 November 2026 (decision 44), whatever
        # shape the placeholder file has. A name that no content file uses has no page.
        print("%-18s %-10s %s" % ("name", "shape", "shown on"))
        for name in names:
            pages = sorted({page for _rel, page, _size in where.get(name, [])})
            print("%-18s %-10s %s" % (name, "tall" if pages else "-", ", ".join(pages) or "no page shows this place today"))
        return 0

    jobs = []
    if args.batch:
        folder = os.path.dirname(os.path.abspath(args.batch))
        with open(args.batch, encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                if not row or row[0].strip().lower() == "photo" or row[0].strip().startswith("#"):
                    continue
                if len(row) < 3:
                    sys.exit("add_photo: every line of %s needs photo,name,alt (this one has %d parts: %s)" % (args.batch, len(row), ",".join(row)))
                jobs.append((os.path.join(folder, row[0].strip()), row[1].strip(), ",".join(row[2:]).strip()))
    elif args.photo and args.name:
        jobs.append((args.photo, args.name, args.alt or ""))
    else:
        ap.error("give PHOTO NAME --alt TEXT, or --batch LIST.csv, or --list")

    taken, failed = set(), 0
    for photo, name, alt in jobs:
        if name in taken:
            print("REFUSED  %s: the place %s already got a photo in this run" % (photo, name))
            failed += 1
            continue
        try:
            add(photo, name, alt, args.dry_run, names, where)
            taken.add(name)
        except (Refused, OSError) as e:
            print("REFUSED  %s" % e)
            failed += 1
    if taken and not args.dry_run:
        print("building the pages ...")
        done = subprocess.run([sys.executable, BUILD], cwd=SITE)
        if done.returncode:
            print("add_photo: the build reported a problem, see above")
            return 1
        print("Done. Look at the pages, then run: python tools/licensing_check.py")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
