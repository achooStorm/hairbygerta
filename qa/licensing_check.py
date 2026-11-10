#!/usr/bin/env python3
"""Licensing check: is a photo that may only be used on Wix in the site folder, in git or on the published site?

Only three image files of the old site may ever be committed, pushed or published: images/logo.jpg, images/g12.jpg
and images/g13.jpg, plus files made only from them (the 800 px and WebP copies of g12 and g13, the favicon and the
touch icons made from the logo). Every other photo of the old site is licensed for Wix only (or has no proven
license) and stays in the restricted folder next to the site folder. In the site each one is a flat beige
placeholder with the same file name and pixel size, until the owner saves a photo of her own over it. The site
generator then records that file in image-manifest.json with the status owner-photo (build contract, decision 27).

What is checked

  Hashes  SHA-256 of every file under the site folder (hidden files, _tmp, qa and .git included, every member
          of every archive, every picture embedded as base64 text) against SHA-256 of every file under the
          restricted folder (archive members included) and of the Wix reference screenshots. Not restricted
          are only the allowed sources, recognised by content: files identical to a site file that
          image-manifest.json records as allowed or allowed-derivative with the same hash (never an
          owner-photo).
          One identical file is a hard stop: LICENSING MATCH with both paths, exit code 2.
  Pixels  every image file is sorted into allowed, allowed-derivative, placeholder, owner-photo, site
          screenshot (under qa/, not for publishing) or UNKNOWN. A placeholder must pass the placeholder test:
          at least 90 percent of the pixels within 6 levels per channel of (232, 225, 218), darkest channel
          above 165, standard deviation below 12 per channel, and the pixel size recorded in the manifest.
          UNKNOWN images and placeholders that fail the test are failures.
  Owner photos  an image whose manifest entry has the status owner-photo is accepted when the file has exactly
          the SHA-256 recorded in that entry and that hash is not the hash of a restricted file. It is counted
          in a class of its own (owner-photo) and listed in the report, so that a person can look at each one.
          Not accepted (class "owner-photo that is not accepted", check owner_photos): the file has another
          hash than the entry (the photo was changed after the pages were built: build them again), the entry
          has no hash, the file is not a picture or is still the beige placeholder (for example the 800 px copy
          in images/sm/ when only the large file was replaced), and above all a file that is identical to a
          restricted file. That one is a LICENSING MATCH and a hard stop like any other:
          the word owner-photo in the manifest never makes a restricted photo acceptable.
          What this cannot see: a Wix-only photo that was saved again or resized has other bytes and another
          hash. The hash proves that a file is not one of the restricted files, not whose picture it is.
  Composites  an image made from several allowed pictures (the share image images/share.jpg, made by
          tools/make_share_image.py, build contract decision 39). image-manifest.json lists it under "composites"
          with its SHA-256 and the box each picture fills ("parts"). It is accepted only when the file has the
          recorded SHA-256, every picture part comes from a verified allowed image (or an accepted owner photo)
          and shows it (a photo: the same small grey copy as the recorded box of its source; the logo: the same
          drawing), and the rest is plain: outside every part at least 99.5 percent of the pixels are the beige of
          the site (within 12 levels), and inside each text part (a line of text) every pixel lies on the line
          between the beige and the ink and at least half of them are beige. So no other picture can hide in it:
          the photos of this site are beige and brown too, which is why the beige itself is tested.
  Pages   every image address in the ten pages and the stylesheets must be one of those checked files.
  Git     .gitignore excludes every folder named source-photos, new-photos, zip or _tmp and every *.zip. In a
          repository:
          nothing of that kind is tracked, staged or in the history, no stored object is identical to a
          restricted file, every tracked image is allowed, allowed-derivative, a placeholder or an accepted
          owner photo.
  --base  the same hash, pixel and page checks on what a web server really serves, plus a few addresses that
          must answer 404.

How to run it (it needs Pillow, so use the Python of the tools folder next to the site folder)

    ../hairbygerta-env/venv/Scripts/python.exe qa/licensing_check.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/licensing_check.py --base https://achoostorm.github.io/hairbygerta/

Options shared by all QA scripts: --base URL, --page SLUG[,SLUG] or all (here it only limits which pages are read
for image addresses, the folder is always checked completely), --viewport (accepted, not used: no browser).

Report: qa/reports/licensing.json and qa/reports/licensing.md.
Exit code: 0 pass, 1 failure, 2 a file identical to a restricted file was found.

The script only reads. Nothing is ever copied or unpacked from the restricted folder: archives are read in
memory. With --base the downloads go to a temporary folder outside the site folder and are deleted at the end.
"""
import base64, bz2, gzip, hashlib, html.parser, io, json, lzma, os, posixpath, re, shutil, stat, subprocess, sys
import tarfile, tempfile, urllib.error, urllib.parse, urllib.request, warnings, zipfile

sys.dont_write_bytecode = True   # no __pycache__ in the site folder (a compiled file carries the path of this computer)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

try:
    from PIL import Image, ImageChops, ImageStat
except ImportError:
    sys.exit("licensing_check: this script needs Pillow. Run it with the Python of the tools folder (hairbygerta-env/venv).")

NAME = "licensing"                 # qa/reports/licensing.json and licensing.md
SITE_PAGE = common.SITE_PAGE       # value of "page" for checks that belong to the whole site
VIEWPORT = common.NO_VIEWPORT      # no browser, no viewport
USER_AGENT = "hairbygerta-qa/licensing_check"
MANIFEST = "image-manifest.json"
STYLESHEET = "css/style.css"
# Addresses of the final domain mean the same files as relative addresses. They are never fetched from that domain.
CANONICAL_ORIGINS = ("https://www.hairbygerta.com/", "http://www.hairbygerta.com/",
                     "https://hairbygerta.com/", "http://hairbygerta.com/")

# ---------------------------------------------------------------- the licensing facts

# The only images licensed for use outside Wix. A new licensed photo needs a new name here, not only in the manifest.
ALLOWED_NAMES = ("logo", "g12", "g13")
# Licensed for Wix only, or no proven license. In the site these names are placeholders.
RESTRICTED_NAMES = (
    "about-salon", "brunette-balayage", "copper-waves", "foils-highlights", "g01", "g02", "g04", "g05", "g06",
    "g07", "g10", "g14", "g15", "g16", "g17", "g18", "g19", "g20", "g21", "home-smile", "home-styling",
    "home-waves", "makeup-red-lips", "meet-extensions", "svc-bridal", "svc-haircut")
# An allowed file must be byte-identical to its licensed source in the restricted folder (the logo master
# hbg_logo.jpg, g12.jpg and g13.jpg in the backup). If one is changed on purpose (for example metadata removed),
# QA looks at the picture and adds its SHA-256 here: {"g12": {"<sha256>"}}.
REVIEWED_SHA256 = {}

# The placeholder test.
BEIGE = (232, 225, 218)            # #e8e1da
TOLERANCE = 6                      # a pixel is beige within this many levels per channel
MIN_BEIGE_SHARE = 0.90
MIN_DARKEST = 165                  # the darkest channel value must be above this
MAX_STDDEV = 12.0                  # the standard deviation of every channel must be below this
# "Made from" test for the allowed derivatives (measured: copies differ by less than 1, other pictures by 40 and more;
# icons correlate 0.85 and more with the logo artwork, photos 0.35 and less).
MAX_COPY_DIFFERENCE = 6.0
MIN_ARTWORK_CORRELATION = 0.6
# A composite (see the docstring): outside its parts the beige of the site, in a text part beige and ink only.
SITE_BEIGE, SITE_INK = (232, 225, 218), (29, 21, 9)
BEIGE_LEVELS = 12                   # how far each channel of a background pixel may be from the beige (JPEG noise)
MIN_BEIGE_SHARE_OUTSIDE = 0.995
LINE_DISTANCE = 24.0                # how far (RGB) a text pixel may lie from the line beige to ink (anti-aliased edges)
MIN_TEXT_ON_LINE = 0.99
MIN_TEXT_BEIGE = 0.5                # a line of text is mostly the beige between the letters
PART_MARGIN = 8                     # px around a picture part left out of the tests: JPEG blurs the edge of a photo
TEXT_MARGIN = 3                     # px around a text part counted with it: the anti-aliased edges of the letters

ALLOWED, DERIVATIVE, PLACEHOLDER = "allowed", "allowed-derivative", "placeholder"
# Build contract, decision 27: a photo of the owner's own that she saved over a placeholder. The site generator writes
# this status into the manifest together with the SHA-256 of the file. See owner_photo() for what is accepted.
OWNER, OWNER_REFUSED = "owner-photo", "owner-photo that is not accepted"
PLACEHOLDER_FAILED, SCREENSHOT, SVG, UNKNOWN = "placeholder that fails the test", "site screenshot", "svg for review", "UNKNOWN"
CLASS_ORDER = (ALLOWED, DERIVATIVE, PLACEHOLDER, OWNER, SCREENSHOT, SVG, PLACEHOLDER_FAILED, OWNER_REFUSED, UNKNOWN)
PUBLISHABLE = (ALLOWED, DERIVATIVE, PLACEHOLDER, OWNER)
REBUILD = "build the pages again (python tools/build_pages.py), the generator then records the photo that is there now"

RASTER_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".ico", ".bmp", ".avif",
              ".jfif", ".tif", ".tiff", ".heic", ".heif", ".jp2", ".jxl", ".apng", ".cur", ".psd")
SVG_EXT = (".svg", ".svgz")
NOT_IMAGE_EXT = (".css", ".woff", ".woff2", ".ttf", ".otf", ".eot")
# Text files inside old archives of the restricted folder are not photos and are not compared.
TEXT_EXT = (".html", ".css", ".js", ".txt", ".xml", ".md", ".json", ".py")
ARCHIVE_EXT = (".zip", ".tar", ".tgz", ".gz", ".bz2", ".tbz2", ".xz", ".txz", ".7z", ".rar")
MAX_ARCHIVE_DEPTH = 4
MAX_MEMBER_BYTES = 400 * 1024 * 1024
MAX_DOWNLOAD_BYTES = 60 * 1024 * 1024
MAX_LINES_PER_CHECK = 12

FORBIDDEN_FOLDERS = ("source-photos", "new-photos", "zip", "_tmp")
# .gitignore must exclude all of these (git check-ignore is asked).
IGNORE_SAMPLES = ("source-photos/g01.jpg", "zip/g01.jpg", "_tmp/site2.zip", "_tmp/notes.txt", "backup.zip",
                  "hbg_images.zip", "images/photos.zip", "images/source-photos/g01.jpg", "qa/zip/g01.jpg",
                  "tools/_tmp/draft.png", "new-photos/IMG_0001.jpg", "images/new-photos/g01.jpg")
# The published site must answer 404 for these.
FORBIDDEN_ADDRESSES = ("source-photos/g01.jpg", "zip/g01.jpg", "_tmp/site2.zip", "hbg_images.zip", "site.zip")
MAX_SCREENSHOT_PROBES = 20


# ---------------------------------------------------------------- small helpers

def entry(page, check, ok, expected, actual, evidence, owner, **more):
    e = {"page": page, "viewport": VIEWPORT, "check": check, "ok": bool(ok), "expected": expected,
         "actual": actual, "evidence": evidence, "owner": owner}
    e.update(more)
    return e


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def short(value, limit=160):
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def plural(n, word, many=None):
    return "%d %s" % (n, word if n == 1 else (many or word + "s"))


def last_name(label):
    """The file name at the end of a path or of an 'archive.zip!member' label."""
    return re.split(r"[!/\\]", label)[-1]


def stem(label):
    return os.path.splitext(last_name(label))[0].lower()


def ext(label):
    return os.path.splitext(last_name(label))[1].lower()


def clean_rel(value):
    """A file name as written in the manifest or in a page, as a path inside the site. None when it points outside."""
    if not isinstance(value, str):
        return None
    rel = posixpath.normpath(value.replace("\\", "/").strip())
    if rel in ("", ".", "..") or rel.startswith(("../", "/")) or ":" in rel or "\0" in rel:
        return None
    return rel


def page_file(slug):
    address = common.PAGES[slug]
    return address + "index.html" if address == "" or address.endswith("/") else address


def walk(root):
    """(relative path with forward slashes, full path) of every file under root, hidden ones included."""
    for folder, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            full = os.path.join(folder, name)
            yield os.path.relpath(full, root).replace(os.sep, "/"), full


def read_file(path, problems, label):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        if os.path.exists(path):
            problems.append("%s cannot be read (%s)" % (label, type(e).__name__))
        return None      # a file that is gone was removed while the check ran


def make_workdir():
    """A scratch folder in the tools folder (or the system temp folder), never in the site folder."""
    scratch = os.path.join(common.ENV, "stage", "qa", "licensing_check")
    try:
        os.makedirs(scratch, exist_ok=True)
        path = tempfile.mkdtemp(prefix="run-", dir=scratch)
    except OSError:
        path = tempfile.mkdtemp(prefix="hbg-licensing-")
    site = os.path.realpath(common.SITE)
    if os.path.commonpath([site, os.path.realpath(path)]) == site:
        remove_tree(path)
        raise RuntimeError("the temporary folder would be inside the site folder")
    return path


def remove_tree(path):
    """Delete a temporary folder completely, read-only files included. True when it is gone."""
    def retry(function, target, _problem):
        try:
            os.chmod(target, stat.S_IWRITE)
            function(target)
        except OSError:
            pass
    try:
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=retry)
        else:
            shutil.rmtree(path, onerror=retry)
    except OSError:
        pass
    return not os.path.exists(path)


# ---------------------------------------------------------------- archives (always read in memory)

def archive_kind(data):
    head = data[:8]
    if head[:4] in (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"):
        return "zip"
    if head[:2] == b"\x1f\x8b":
        return "gz"
    if head[:3] == b"BZh":
        return "bz2"
    if head[:6] == b"\xfd7zXZ\x00":
        return "xz"
    if head[:6] == b"7z\xbc\xaf\x27\x1c":
        return "7z"
    if head[:6] == b"Rar!\x1a\x07":
        return "rar"
    if data[257:262] == b"ustar":
        return "tar"
    return None


def expand(label, data, problems, depth=0):
    """Yield (label, bytes) for every member of an archive, archives inside archives included.
    Nothing is written to disk. What cannot be opened is added to problems."""
    kind = archive_kind(data)
    named = ext(label) in ARCHIVE_EXT
    sure = named or kind in ("zip", "tar")      # two magic bytes alone are not proof of a gz or bz2 file
    if kind is None and data.rfind(b"PK\x05\x06", max(0, len(data) - 70000)) >= 0 and zipfile.is_zipfile(io.BytesIO(data)):
        kind = "zip"            # a zip behind other bytes (self-extracting file, picture with a zip appended)
    if kind is None:
        if named and data:
            problems.append("%s has the name of an archive but cannot be opened as one" % label)
        return
    if kind in ("7z", "rar"):
        problems.append("%s is a %s archive, this script cannot look into it" % (label, kind))
        return
    if depth >= MAX_ARCHIVE_DEPTH:
        problems.append("%s: archives nested more than %d deep, not opened" % (label, MAX_ARCHIVE_DEPTH))
        return
    try:
        if kind == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                for info in z.infolist():
                    if info.is_dir():
                        continue
                    inner = "%s!%s" % (label, info.filename)
                    if info.file_size > MAX_MEMBER_BYTES:
                        problems.append("%s is too large to check" % inner)
                        continue
                    try:
                        member = z.read(info)
                    except Exception as e:
                        problems.append("%s cannot be read (%s)" % (inner, short(e, 80) or type(e).__name__))
                        continue
                    yield inner, member
                    yield from expand(inner, member, problems, depth + 1)
        elif kind == "tar":
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as t:
                for info in t:
                    if not info.isfile():
                        continue
                    inner = "%s!%s" % (label, info.name)
                    member = t.extractfile(info).read()
                    yield inner, member
                    yield from expand(inner, member, problems, depth + 1)
        else:
            member = {"gz": gzip.decompress, "bz2": bz2.decompress, "xz": lzma.decompress}[kind](data)
            inner = "%s!(unpacked)" % label
            yield inner, member
            yield from expand(inner, member, problems, depth + 1)
    except Exception as e:
        if sure:
            problems.append("%s cannot be opened (%s)" % (label, short(e, 80) or type(e).__name__))


# ---------------------------------------------------------------- what is an image

def raster_magic(data):
    """The picture format the first bytes announce, or None."""
    h = data[:16]
    if h[:3] == b"\xff\xd8\xff":
        return "JPEG"
    if h[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "GIF"
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "WebP"
    if h[4:8] == b"ftyp" and h[8:12] in (b"avif", b"avis", b"heic", b"heix", b"hevc", b"mif1", b"msf1"):
        return "AVIF or HEIC"
    if h[:4] in (b"II*\x00", b"MM\x00*"):
        return "TIFF"
    if h[:4] == b"8BPS":
        return "PSD"
    if h[:12] in (b"\x00\x00\x00\x0cjP  \r\n\x87\n", b"\x00\x00\x00\x0cJXL \r\n\x87\n"):
        return "JPEG 2000 or JPEG XL"
    if h[:2] == b"BM" and len(data) > 26 and int.from_bytes(data[14:18], "little") in (12, 40, 52, 56, 64, 108, 124):
        return "BMP"
    if h[:4] in (b"\x00\x00\x01\x00", b"\x00\x00\x02\x00") and len(data) > 22:
        count = int.from_bytes(data[4:6], "little")
        if 0 < count <= 64 and data[9] == 0 and int.from_bytes(data[18:22], "little") >= 6 + 16 * count:
            return "ICO"
    return None


def image_kind(label, data):
    """'raster', 'svg' or None. Decided by the file name and by the content, so a renamed picture is found too."""
    e = ext(label)
    if e in SVG_EXT:
        return "svg"
    if e in RASTER_EXT or raster_magic(data):
        return "raster"
    head = data[:2048].lstrip().lower()
    if head.startswith(b"<svg") or (head.startswith(b"<?xml") and b"<svg" in head):
        return "svg"
    return None


# ---------------------------------------------------------------- pixels

def frames(data, limit=64):
    """Every picture inside an image file, as RGB (an .ico holds several sizes, a GIF or WebP may hold several frames)."""
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with Image.open(io.BytesIO(data)) as im:
            if im.format == "ICO" and hasattr(im, "ico"):
                for size in sorted(im.ico.sizes())[:limit]:
                    out.append(im.ico.getimage(size).convert("RGB"))
            else:
                for i in range(min(getattr(im, "n_frames", 1), limit)):
                    im.seek(i)
                    out.append(im.convert("RGB"))
    return out


def pixel_stats(rgb):
    """(share of beige pixels, darkest channel value, largest standard deviation of a channel)."""
    near = None
    for band, target in zip(rgb.split(), BEIGE):
        hit = band.point([255 if abs(v - target) <= TOLERANCE else 0 for v in range(256)])
        near = hit if near is None else ImageChops.darker(near, hit)
    share = near.histogram()[255] / float(rgb.width * rgb.height)
    darkest = min(low for low, _high in rgb.getextrema())
    return share, darkest, max(ImageStat.Stat(rgb).stddev)


def placeholder_test(data, size=None):
    """The placeholder test of the hard rule. Returns (passed, what was measured, list of reasons it failed).
    size is the (width, height) recorded in the manifest, None leaves that condition out."""
    try:
        pictures = frames(data)
        stats = [pixel_stats(p) for p in pictures]
    except Exception as e:
        return False, "cannot be read as an image", ["cannot be read as an image (%s)" % type(e).__name__]
    if not pictures:
        return False, "holds no picture", ["holds no picture"]
    share, darkest, spread = min(s[0] for s in stats), min(s[1] for s in stats), max(s[2] for s in stats)
    width, height = pictures[0].size
    measured = "%d x %d px, %.1f percent beige, darkest channel %d, standard deviation %.1f" % (
        width, height, share * 100, darkest, spread)
    reasons = []
    if share < MIN_BEIGE_SHARE:
        reasons.append("only %.1f percent of the pixels are beige (at least %d needed)" % (share * 100, MIN_BEIGE_SHARE * 100))
    if darkest <= MIN_DARKEST:
        reasons.append("darkest channel value %d (must be above %d)" % (darkest, MIN_DARKEST))
    if spread >= MAX_STDDEV:
        reasons.append("standard deviation %.1f (must be below %d)" % (spread, MAX_STDDEV))
    if size is not None:
        if not (isinstance(size[0], int) and isinstance(size[1], int)):
            reasons.append("the manifest records no pixel size")
        elif (width, height) != tuple(size):
            reasons.append("is %d x %d px, the manifest records %d x %d" % (width, height, size[0], size[1]))
    return not reasons, measured, reasons


def gray_thumb(picture, n=24):
    return list(picture.convert("L").resize((n, n), Image.Resampling.BOX).tobytes())


def artwork_thumb(picture, n=24):
    """The drawing inside a picture, cut out of its plain background, so margin and size do not matter."""
    gray = picture.convert("L")
    paper = gray.getpixel((0, 0))
    box = gray.point([255 if abs(v - paper) > 64 else 0 for v in range(256)]).getbbox()
    return gray_thumb(gray.crop(box) if box else gray, n)


def difference(a, b):
    return sum(abs(x - y) for x, y in zip(a, b)) / float(len(a))


def correlation(a, b):
    mean_a, mean_b = sum(a) / float(len(a)), sum(b) / float(len(b))
    top = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    low = (sum((x - mean_a) ** 2 for x in a) * sum((y - mean_b) ** 2 for y in b)) ** 0.5
    return top / low if low else 0.0


def made_from(copy_data, source_data, artwork):
    """Does a derived file show the picture it is recorded as made from? Returns (yes, what was measured).
    artwork=True is for the icons: the logo drawing at another size and margin."""
    try:
        copies, source = frames(copy_data), frames(source_data)[0]
    except Exception as e:
        return False, "cannot be read as an image (%s)" % type(e).__name__
    if not copies:
        return False, "holds no picture"
    if artwork:
        target = artwork_thumb(source)
        worst = min(abs(correlation(artwork_thumb(c), target)) for c in copies)
        return worst >= MIN_ARTWORK_CORRELATION, "correlation with the logo artwork %.2f (at least %.1f needed)" % (worst, MIN_ARTWORK_CORRELATION)
    shape, wanted = copies[0].width / float(copies[0].height), source.width / float(source.height)
    if abs(shape - wanted) > 0.02 * wanted:
        return False, "is %d x %d px, another shape than its source (%d x %d)" % (copies[0].size + source.size)
    target = gray_thumb(source)
    worst = max(difference(gray_thumb(c), target) for c in copies)
    return worst <= MAX_COPY_DIFFERENCE, "mean difference to its source %.1f of 255 (at most %d allowed)" % (worst, MAX_COPY_DIFFERENCE)


def on_ink_line(rgb):
    """Does the colour lie on the line between the beige and the ink of the site (a pixel of text)?"""
    bx, by, bz = (SITE_INK[i] - SITE_BEIGE[i] for i in range(3))
    dx, dy, dz = (rgb[i] - SITE_BEIGE[i] for i in range(3))
    t = min(1.0, max(0.0, (dx * bx + dy * by + dz * bz) / float(bx * bx + by * by + bz * bz)))
    ex, ey, ez = dx - t * bx, dy - t * by, dz - t * bz
    return ex * ex + ey * ey + ez * ez <= LINE_DISTANCE * LINE_DISTANCE


def is_beige(rgb):
    return all(abs(rgb[i] - SITE_BEIGE[i]) <= BEIGE_LEVELS for i in range(3))


def plain_parts(picture, picture_boxes, text_boxes):
    """-> (share of beige pixels outside every part, [(share on the ink line, share beige) per text part], pixels outside)"""
    width, height = picture.size
    pixels = picture.load()
    grow = lambda b, m: (max(0, b[0] - m), max(0, b[1] - m), min(width, b[2] + m), min(height, b[3] + m))
    skip = [grow(b, PART_MARGIN) for b in picture_boxes] + [grow(b, TEXT_MARGIN) for b in text_boxes]
    looked = beige = 0
    for y in range(height):
        spans = [(x0, x1) for x0, y0, x1, y1 in skip if y0 <= y < y1]
        for x in range(width):
            if any(x0 <= x < x1 for x0, x1 in spans):
                continue
            looked += 1
            beige += is_beige(pixels[x, y])
    texts = []
    for box in text_boxes:
        x0, y0, x1, y1 = grow(box, TEXT_MARGIN)
        n = on = flat = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                n += 1
                rgb = pixels[x, y]
                on += on_ink_line(rgb)
                flat += is_beige(rgb)
        texts.append((on / float(n) if n else 1.0, flat / float(n) if n else 1.0))
    return (beige / float(looked) if looked else 1.0), texts, looked


def composite_shows(data, parts, read_source):
    """Does a composite show its parts, and nothing else outside them? -> (yes, what was measured, problems).
    read_source(rel) gives the bytes of a source picture, or None."""
    problems, measured = [], []
    try:
        picture = frames(data)[0]
    except Exception as e:
        return False, "", ["cannot be read as an image (%s)" % type(e).__name__]
    boxes, text_boxes = [], []
    for n, part in enumerate(parts or []):
        rel, kind, box = clean_rel(part.get("source")), part.get("kind"), part.get("box")
        if kind not in ("photo", "artwork", "text") or not (isinstance(box, list) and len(box) == 4 and all(isinstance(v, int) for v in box)):
            problems.append("part %d: kind must be photo, artwork or text and box four whole numbers" % (n + 1))
            continue
        x0, y0, x1, y1 = box
        if not (0 <= x0 < x1 <= picture.width and 0 <= y0 < y1 <= picture.height):
            problems.append("part %d: the box %s is not inside the %d x %d px picture" % (n + 1, box, picture.width, picture.height))
            continue
        if kind == "text":
            text_boxes.append(box)
            continue
        source_data = read_source(rel) if rel else None
        if source_data is None:
            problems.append("part %d: its source %s cannot be read" % (n + 1, part.get("source")))
            continue
        source = frames(source_data)[0]
        region = picture.crop(box)
        if kind == "artwork":
            value = abs(correlation(artwork_thumb(region), artwork_thumb(source)))
            ok, text = value >= MIN_ARTWORK_CORRELATION, "%s correlation with the drawing of %s %.2f" % (kind, rel, value)
        else:
            sbox = part.get("source_box")
            if not (isinstance(sbox, list) and len(sbox) == 4):
                problems.append("part %d: a photo needs its source_box" % (n + 1))
                continue
            cut = source.crop(tuple(int(round(v)) for v in sbox))
            shape, wanted = region.width / float(region.height), cut.width / float(cut.height)
            value = difference(gray_thumb(region), gray_thumb(cut))
            ok = abs(shape - wanted) <= 0.02 * wanted and value <= MAX_COPY_DIFFERENCE
            text = "%s from %s, mean difference %.1f of 255" % (kind, rel, value)
        measured.append(text)
        if not ok:
            problems.append("part %d does not show what the manifest says (%s)" % (n + 1, text))
        boxes.append(box)
    if not boxes:
        problems.append("the manifest records no picture part")
    share, texts, looked = plain_parts(picture, boxes, text_boxes)
    measured.append("outside the parts %.2f percent of %d pixels are the beige" % (share * 100, looked))
    if share < MIN_BEIGE_SHARE_OUTSIDE:
        problems.append("outside the parts only %.2f percent of the pixels are the beige (at least %.1f percent needed): "
                        "the picture holds something the manifest does not record" % (share * 100, MIN_BEIGE_SHARE_OUTSIDE * 100))
    for n, (on, flat) in enumerate(texts):
        if on < MIN_TEXT_ON_LINE or flat < MIN_TEXT_BEIGE:
            problems.append("text part %d is not plain text: %.1f percent of its pixels are beige, ink or a mix (at least %d needed), "
                            "%.1f percent are beige (at least %d needed)" % (n + 1, on * 100, MIN_TEXT_ON_LINE * 100, flat * 100, MIN_TEXT_BEIGE * 100))
    if texts:
        measured.append("%d text parts, the plainest %.1f and the least plain %.1f percent beige" % (len(texts), max(f for _o, f in texts) * 100, min(f for _o, f in texts) * 100))
    return not problems, "; ".join(measured), problems


def svg_findings(data):
    """What makes an svg more than a drawing: a picture inside it or a file fetched from elsewhere."""
    if data[:2] == b"\x1f\x8b":
        try:
            data = gzip.decompress(data)
        except Exception:
            return ["cannot be unpacked"]
    text = urllib.parse.unquote(data.decode("utf-8", "replace"))
    found = []
    if re.search(r"<image\b", text, re.I):
        found.append("holds an <image> element")
    if re.search(r"data:image/(?!svg)", text, re.I):
        found.append("holds an embedded picture")
    if re.search(r"(?:href|src)\s*=\s*[\"']\s*(?:https?:)?//", text, re.I) and re.search(r"<(?:image|use|feImage|script|foreignObject)\b", text, re.I):
        found.append("loads something from another address")
    return found


# ---------------------------------------------------------------- the manifest

def read_manifest(raw):
    """(document, problem text)."""
    if raw is None:
        return None, "%s is missing" % MANIFEST
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except Exception as e:
        return None, "%s is not valid JSON (%s)" % (MANIFEST, short(e, 80))
    if not isinstance(doc, dict) or not isinstance(doc.get("images"), dict):
        return None, "%s has no images table" % MANIFEST
    return doc, None


def nested_files(node, path=""):
    """(key path, record) of every record with a file name below a manifest entry: sm, webp, webp.sm ..."""
    pairs = node.items() if isinstance(node, dict) else enumerate(node)
    for key, value in pairs:
        here = "%s.%s" % (path, key) if path else str(key)
        if isinstance(value, dict):
            if isinstance(value.get("file"), str):
                yield here, value
            yield from nested_files(value, here)
        elif isinstance(value, list):
            yield from nested_files(value, here)


def manifest_index(doc):
    """{site path: what the manifest says about it}, plus the things that are wrong in the manifest itself.
    expect is allowed, allowed-derivative, placeholder, owner-photo or None (then why says what is wrong with the
    record). The small copy of an owner photo is an owner photo too, with a hash of its own in the manifest."""
    index, problems = {}, []
    if not doc:
        return index, problems
    allowed_files = ["images/%s.jpg" % n for n in ALLOWED_NAMES]

    def add(name, record, expect, why, role, source):
        rel = clean_rel(record.get("file"))
        if rel is None:
            problems.append("entry %s names a file outside the site: %s" % (name, short(record.get("file"), 60)))
            return None
        digest = record.get("sha256")
        index[rel] = {"name": name, "expect": expect, "why": why, "role": role, "source": source,
                      "sha256": digest.lower() if isinstance(digest, str) else None,
                      "width": record.get("width"), "height": record.get("height")}
        return rel

    for name, record in doc["images"].items():
        if not isinstance(record, dict):
            problems.append("entry %s is not a record" % name)
            continue
        status, expect, why = record.get("status"), None, ""
        if status == ALLOWED and name not in ALLOWED_NAMES:
            why = "the manifest calls %s allowed, but only %s are licensed" % (name, ", ".join(ALLOWED_NAMES))
        elif status == ALLOWED and record.get("file") != "images/%s.jpg" % name:
            why = "the allowed image %s must be the file images/%s.jpg" % (name, name)
        elif status == OWNER and name in ALLOWED_NAMES:
            why = "the manifest calls %s an owner-photo, but it is one of the three allowed images and must stay recorded as allowed" % name
        elif status in (ALLOWED, PLACEHOLDER, OWNER):
            expect = status
        else:
            why = "the manifest gives it the status %s" % json.dumps(status)
        if why:
            problems.append(why)
        main = add(name, record, expect, why, "main", None)
        if main is None:
            continue
        for key, sub in nested_files(record):
            role = "webp" if "webp" in key.lower() or ext(sub["file"]) == ".webp" else key
            add(name, sub, DERIVATIVE if expect == ALLOWED else expect, why, role, main)
    for record in doc.get("icons") or []:
        if not isinstance(record, dict):
            continue
        source, expect, why = clean_rel(record.get("derived_from")), None, ""
        if record.get("status") != DERIVATIVE:
            why = "icon with the status %s" % json.dumps(record.get("status"))
        elif source not in allowed_files:
            why = "icon recorded as made from %s, which is not an allowed image" % json.dumps(record.get("derived_from"))
        else:
            expect = DERIVATIVE
        if why:
            problems.append("%s: %s" % (short(record.get("file"), 60), why))
        add("icon", record, expect, why, "icon", source)
    for record in doc.get("composites") or []:
        if not isinstance(record, dict):
            continue
        why, expect = "", DERIVATIVE
        if record.get("status") != DERIVATIVE:
            why, expect = "composite with the status %s" % json.dumps(record.get("status")), None
        if why:
            problems.append("%s: %s" % (short(record.get("file"), 60), why))
        rel = add("composite", record, expect, why, "composite", None)
        if rel is not None:
            index[rel]["parts"] = record.get("parts") or []
    for name in ALLOWED_NAMES:
        record = doc["images"].get(name)
        if not isinstance(record, dict) or record.get("status") != ALLOWED:
            problems.append("%s is not recorded as allowed" % name)
    return index, problems


# ---------------------------------------------------------------- sorting one image

def classify(rel, data, kind, index):
    """Sort one image file of the site into its class."""
    info = {"file": rel, "class": UNKNOWN, "bytes": len(data), "sha256": sha256(data), "detail": ""}
    if rel.startswith("qa/"):
        info["class"] = SCREENSHOT
        return info
    if kind == "svg":
        info["class"] = SVG
        info["findings"] = svg_findings(data)
        info["detail"] = "; ".join(info["findings"])
        return info
    record = index.get(rel)
    if record is None:
        info["detail"] = "not listed in %s" % MANIFEST
    elif record["expect"] in (ALLOWED, DERIVATIVE):
        if not record["sha256"]:
            info["detail"] = "the manifest records no hash for it"
        elif record["sha256"] != info["sha256"]:
            info["detail"] = "recorded as %s, but the file is not the one the manifest describes (other SHA-256)" % record["expect"]
        else:
            info["class"] = record["expect"]
            return info
    elif record["expect"] == PLACEHOLDER:
        passed, measured, reasons = placeholder_test(data, (record["width"], record["height"]))
        info["class"] = PLACEHOLDER if passed else PLACEHOLDER_FAILED
        info["detail"] = measured if passed else "%s (%s)" % ("; ".join(reasons), measured)
        return info
    elif record["expect"] == OWNER:
        return owner_photo(info, data, record)
    else:
        info["detail"] = record["why"] or "the manifest does not say what it is"
    passed, measured, _reasons = placeholder_test(data)
    info["detail"] += " (%s, %s)" % (measured, "looks like a placeholder" if passed else "not a placeholder")
    return info


def owner_photo(info, data, record):
    """An image the manifest records as owner-photo (build contract, decision 27). It is accepted when the file has
    exactly the SHA-256 the manifest records for it. Whether that hash is the hash of a restricted file is not known
    yet at this point: refuse_restricted_owner_photos() takes the acceptance back for such a file."""
    passed, measured, reasons = placeholder_test(data)
    if not record["sha256"]:
        why = "the manifest records no SHA-256 for it; %s" % REBUILD
    elif record["sha256"] != info["sha256"]:
        why = "the file is not the one the manifest describes (other SHA-256); if the photo was changed on purpose, %s" % REBUILD
    elif any(r.startswith(("cannot be read", "holds no picture")) for r in reasons):
        why = "the file %s" % measured
    elif passed:
        why = ("the file is still a beige placeholder, not a photo. A replaced photo needs both files, the large one in images/ and its 800 px copy "
               "in images/sm/: save the photo over this file too, or record the entry as placeholder again")
    else:
        info["class"], info["detail"] = OWNER, "%s, SHA-256 as recorded in the manifest" % measured.split(",")[0]
        return info
    info["class"], info["detail"], info["refused"] = OWNER_REFUSED, "recorded as owner-photo, but %s (%s)" % (why, measured), "record"
    return info


def refuse_restricted_owner_photos(images, blocked):
    """The word owner-photo in the manifest never makes a restricted file acceptable: an owner photo whose SHA-256
    is the hash of a restricted file loses its class here (the hash comparison reports the same file as a
    LICENSING MATCH). images is a list of classify() results and is changed in place."""
    for info in images:
        if info["class"] == OWNER and info["sha256"] in blocked:
            info["class"], info["refused"] = OWNER_REFUSED, "restricted"
            info["detail"] = "recorded as owner-photo, but the file is identical to %s: a restricted file is never an owner photo, whatever the manifest says" % (
                ", ".join(blocked[info["sha256"]][:2]))
    return images


# ---------------------------------------------------------------- pictures written into text files

EMBEDDED = re.compile(rb"data:image/([a-z0-9.+-]+)[^,\"'()\s]*?(;base64)?,([^\"'()\s<>\\]+)", re.I)
TEXT_LIKE = TEXT_EXT + (".htm", ".svg", ".mjs", ".map", ".yml", ".yaml", ".csv", ".webmanifest", "")


def embedded_pictures(label, data):
    """(media type, bytes) of every picture written into a text file as a data address."""
    if ext(label) not in TEXT_LIKE or b"data:image/" not in data:
        return
    for m in EMBEDDED.finditer(data):
        kind = m.group(1).decode("ascii", "replace").lower()
        if kind.startswith("svg"):
            continue
        payload = m.group(3)
        try:
            if m.group(2):
                payload = urllib.parse.unquote_to_bytes(payload)
                picture = base64.b64decode(payload + b"=" * (-len(payload) % 4))
            else:
                picture = urllib.parse.unquote_to_bytes(payload)
        except Exception:
            continue
        if picture:
            yield kind, picture


def owner_of(rel):
    """Who has to fix a file, after the table in tools/CONTRACT.md."""
    if rel.startswith(("_tmp/", "zip/", "source-photos/", "new-photos/", ".git", "git object")) or "!" in rel or ext(rel) in ARCHIVE_EXT:
        return "DEPLOY"
    if rel.startswith("css/"):
        return "DESIGN"
    if rel.startswith("js/"):
        return "INTERACTION"
    if rel.startswith("content/"):
        return "CONTENT"
    if rel.startswith("seo/") or rel in ("sitemap.xml", "robots.txt"):
        return "SEO"
    if ext(rel) == ".html" or rel.startswith("tools/pages/") or rel == "tools/build_pages.py":
        return "PAGES"
    return "ASSETS"


# ---------------------------------------------------------------- the two sides of the hash comparison

def site_inventory(root, index):
    """Hash every file under root and sort every image. Nothing under root is changed."""
    inv = {"items": [], "images": [], "embedded": [], "archives": {}, "problems": [], "paths": set(),
           "counts": {"files": 0, "archive_members": 0, "embedded_pictures": 0}}
    for rel, full in walk(root):
        data = read_file(full, inv["problems"], rel)
        if data is None:
            continue
        inv["paths"].add(rel)
        inv["counts"]["files"] += 1
        inv["items"].append({"path": rel, "sha256": sha256(data), "bytes": len(data)})
        if rel != ".git" and not rel.startswith(".git/"):
            kind = image_kind(rel, data)
            if kind:
                inv["images"].append(classify(rel, data, kind, index))
            for n, (media, picture) in enumerate(embedded_pictures(rel, data), 1):
                label = "%s (embedded picture %d, image/%s)" % (rel, n, media)
                inv["counts"]["embedded_pictures"] += 1
                inv["items"].append({"path": label, "sha256": sha256(picture), "bytes": len(picture)})
                passed, measured, _reasons = placeholder_test(picture)
                inv["embedded"].append({"file": rel, "label": label, "detail": measured, "placeholder_like": passed})
        for label, member in expand(rel, data, inv["problems"]):
            inv["counts"]["archive_members"] += 1
            digest = sha256(member)
            inv["items"].append({"path": label, "sha256": digest, "bytes": len(member)})
            top = inv["archives"].setdefault(rel, {"members": 0, "pictures": 0, "known": 0, "placeholder_like": 0, "other": []})
            top["members"] += 1
            if image_kind(label, member) == "raster":
                top["pictures"] += 1
                top.setdefault("_pictures", []).append((label, digest, member if len(member) < MAX_MEMBER_BYTES else b""))
    return inv


def judge_archive_pictures(inv, verified):
    """A picture inside an archive of the site folder is fine when it is a verified allowed file or passes the pixel test."""
    for info in inv["archives"].values():
        for label, digest, member in info.pop("_pictures", []):
            if digest in verified:
                info["known"] += 1
            elif placeholder_test(member)[0]:
                info["placeholder_like"] += 1
            else:
                info["other"].append(label)


def restricted_side():
    """{sha256: [where]} of every file that must never be in the site, read from the restricted folder
    (archive members included, in memory) and from the Wix reference screenshots."""
    side = {"table": {}, "problems": [], "available": os.path.isdir(common.RESTRICTED), "stems": set(),
            "counts": {"files": 0, "archive_members": 0, "skipped_text_members": 0, "skipped_empty": 0, "reference_screenshots": 0}}

    def add(label, data):
        if not data:
            side["counts"]["skipped_empty"] += 1      # an empty file holds nothing that could be a photo
            return
        side["table"].setdefault(sha256(data), []).append(label)
        side["stems"].add(stem(label))

    if side["available"]:
        for rel, full in walk(common.RESTRICTED):
            data = read_file(full, side["problems"], "restricted folder/" + rel)
            if data is None:
                continue
            side["counts"]["files"] += 1
            add("restricted folder/" + rel, data)
            for label, member in expand("restricted folder/" + rel, data, side["problems"]):
                side["counts"]["archive_members"] += 1
                if ext(label) in TEXT_EXT and not raster_magic(member):
                    side["counts"]["skipped_text_members"] += 1
                    continue
                add(label, member)
    shots = os.path.join(common.WIX_REF, "shots")
    if os.path.isdir(shots):
        for rel, full in walk(shots):
            data = read_file(full, side["problems"], "wix reference screenshots/" + rel)
            if data:
                side["counts"]["reference_screenshots"] += 1
                side["table"].setdefault(sha256(data), []).append("wix reference screenshots/" + rel)
    return side


def match(site, digest, blocked):
    """One finding of the hash comparison, with a word about what the restricted file is."""
    labels = blocked[digest]
    if any(l.startswith("restricted folder/") and stem(l) in RESTRICTED_NAMES for l in labels):
        kind = "Wix-only photo"
    elif any(l.startswith("wix reference screenshots/") for l in labels):
        kind = "screenshot of the Wix site"
    elif any(l.startswith("restricted folder/") for l in labels):
        kind = "other file of the restricted folder"
    else:
        kind = "listed as restricted in the manifest"
    return {"site": site, "sha256": digest, "restricted": labels, "kind": kind}


def blocked_table(side, exempt, listed):
    """{sha256: [where]} a site file must not be identical to. exempt holds the hashes of the verified allowed site
    files. A restricted file that carries the name of a Wix-only photo is never exempt, whatever the manifest says."""
    blocked = {}
    for digest, labels in side["table"].items():
        if digest in exempt:
            labels = [l for l in labels if stem(l) in RESTRICTED_NAMES or l.startswith("wix reference screenshots/")]
        if labels:
            blocked[digest] = labels
    for digest in listed:
        blocked.setdefault(digest, ["restricted_sha256 list in %s" % MANIFEST])
    return blocked


# ---------------------------------------------------------------- image addresses in pages and stylesheets

FAKE_ORIGIN = "http://site.invalid/SITE/"
CSS_URL = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^)\s]*))\s*\)", re.I)
CSS_IMPORT = re.compile(r"@import\s+(?:url\(\s*)?[\"']?([^\"')\s;]+)", re.I)
CSS_IMAGE_SET = re.compile(r"image-set\(([^;{}]*)\)", re.I)
QUOTED_IMAGE = re.compile(r"[\"'(]\s*([^\"'()\s<>]+?\.(?:jpe?g|png|webp|gif|ico|bmp|avif|svg)(?:\?[^\"'()\s<>]*)?)\s*[\"')]", re.I)
IMAGE_ATTRIBUTES = {("img", "src"), ("video", "poster"), ("image", "href"), ("image", "xlink:href")}


def looks_like_image(value):
    path = urllib.parse.urlsplit(value.strip()).path if "://" in value or value.startswith("//") else value.split("?")[0].split("#")[0]
    return ext(path) in RASTER_EXT + SVG_EXT


def resolve(value, page_rel, base=None):
    """An address as written in a page or stylesheet: ('site', path inside the site), ('external', address),
    ('outside', address) or None for something that is not a web address."""
    value = value.strip()
    low = value.lower()
    if not value or value.startswith("#") or low.startswith(("data:", "blob:", "about:", "javascript:", "mailto:", "tel:")):
        return None
    for origin in CANONICAL_ORIGINS + ((base,) if base else ()):
        if low.startswith(origin.lower()):
            value = FAKE_ORIGIN + value[len(origin):]
            break
    try:
        parts = urllib.parse.urlsplit(urllib.parse.urljoin(FAKE_ORIGIN + page_rel, value))
    except ValueError:
        return None
    if parts.scheme not in ("http", "https"):
        return None
    if parts.netloc != "site.invalid":
        return "external", value
    path = urllib.parse.unquote(parts.path)
    if not path.startswith("/SITE/"):
        return "outside", value
    rel = clean_rel(path[len("/SITE/"):])
    return ("site", rel) if rel else None


def css_addresses(text):
    """(image addresses, imported stylesheets) of a piece of CSS."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    images, sheets = [], [m.group(1) for m in CSS_IMPORT.finditer(text)]
    for m in CSS_URL.finditer(text):
        value = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if not value or value.startswith("#") or value.lower().startswith("data:"):
            continue
        e = ext(value.split("?")[0].split("#")[0])
        if e == ".css":
            if value not in sheets:
                sheets.append(value)
        elif e not in NOT_IMAGE_EXT:
            images.append(value)
    for m in CSS_IMAGE_SET.finditer(text):
        images += [q.group(1) for q in QUOTED_IMAGE.finditer(m.group(1))]
    return images, sheets


class PageScan(html.parser.HTMLParser):
    """Collects every image address of a page: src, srcset, poster, icons, Open Graph, links to image files,
    inline CSS and the addresses inside scripts (JSON-LD)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.images, self.sheets, self.inside = [], [], None

    def handle_starttag(self, tag, attrs):
        self.inside = tag if tag in ("script", "style") else self.inside
        a = {k.lower(): v for k, v in attrs if v is not None}
        if tag == "link" and "stylesheet" in a.get("rel", "").lower() and a.get("href"):
            self.sheets.append(a["href"])
        for key, value in a.items():
            if key in ("srcset", "imagesrcset"):
                self.images += [c.strip().split()[0] for c in value.split(",") if c.strip()]
            elif key == "style":
                self.images += css_addresses(value)[0]
            elif (tag, key) in IMAGE_ATTRIBUTES or (tag == "input" and key == "src"):
                self.images.append(value)
            elif (key in ("href", "src", "content", "data") or key.startswith("data-")) and looks_like_image(value):
                # a plain link to a picture on another site is only a link, not a picture of this site
                if tag == "a" and (resolve(value, "") or ("", ""))[0] == "external":
                    continue
                self.images.append(value)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.inside = None if tag in ("script", "style") else self.inside

    def handle_endtag(self, tag):
        if tag == self.inside:
            self.inside = None

    def handle_data(self, data):
        if self.inside == "style":
            images, sheets = css_addresses(data)
            self.images += images
            self.sheets += sheets
        elif self.inside == "script":
            self.images += [m.group(1) for m in QUOTED_IMAGE.finditer(data.replace("\\/", "/"))]


def page_addresses(raw):
    scan = PageScan()
    scan.feed(raw.decode("utf-8", "replace"))
    scan.close()
    return scan.images, scan.sheets


def unique(values):
    seen, out = set(), []
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


# ---------------------------------------------------------------- where the site is read from

class Local:
    """The files in the site folder."""
    remote = False
    label = common.LOCAL_BASE
    base = None

    def __init__(self, root):
        self.root = root

    def read(self, rel, address=None):
        try:
            with open(os.path.join(self.root, *rel.split("/")), "rb") as f:
                return f.read()
        except OSError:
            return None

    def why_missing(self, rel):
        return "no such file"


class SameHost(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect to another host: the final domain still shows the Wix site, nothing is downloaded from it."""

    def __init__(self, host):
        self.host = host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl).hostname or ""
        if target != self.host:
            raise urllib.error.HTTPError(req.full_url, code, "redirect to another host (%s), not followed" % target, headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Published:
    """What a web server answers. Every file that is read is saved into a temporary folder outside the site folder."""
    remote = True

    def __init__(self, base, root):
        self.base = base if base.endswith("/") else base + "/"
        self.label = self.base
        self.root = root
        self.opener = urllib.request.build_opener(SameHost(urllib.parse.urlsplit(self.base).hostname or ""))
        self.answers = {}
        os.makedirs(root, exist_ok=True)

    def request(self, address, method="GET", body=True):
        """(status or None, bytes or None, note)."""
        url = self.base + urllib.parse.quote(address, safe="/~!$&'()*+,;=:@")
        note = ""
        for _ in range(2):
            try:
                req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
                with self.opener.open(req, timeout=30) as r:
                    return r.status, (r.read(MAX_DOWNLOAD_BYTES) if body else None), ""
            except urllib.error.HTTPError as e:
                return e.code, None, short(e.reason, 80)
            except Exception as e:
                note = "no answer (%s)" % type(e).__name__
        return None, None, note

    def read(self, rel, address=None):
        rel = clean_rel(rel)
        if rel is None:
            return None
        target = os.path.join(self.root, *rel.split("/"))
        if rel in self.answers:
            if self.answers[rel][0] != 200:
                return None
            with open(target, "rb") as f:
                return f.read()
        status, data, note = self.request(rel if address is None else address)
        self.answers[rel] = (status, note)
        if status != 200 or data is None:
            return None
        try:
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as f:
                f.write(data)
        except OSError as e:
            self.answers[rel] = (None, "cannot be saved for checking (%s)" % type(e).__name__)
            return None
        return data

    def status(self, address):
        """Only the status of an address. The body is never read, so nothing that must not exist is downloaded."""
        status, _data, note = self.request(address, method="HEAD", body=False)
        if status in (405, 501):
            status, _data, note = self.request(address, method="GET", body=False)
        return status, note

    def why_missing(self, rel):
        status, note = self.answers.get(rel, (None, "not requested"))
        if status and note and not 400 <= status < 500:
            return "the server answers %s (%s)" % (status, note)      # for example a redirect to another host
        return "the server answers %s" % (status if status else note or "nothing")


# ---------------------------------------------------------------- git

def run_git(args, root, git_dir=None, stdin=None):
    """(exit code or None when git cannot be started, stdout bytes, stderr text). Read-only commands only."""
    cmd = ["git", "-c", "core.excludesFile=", "-c", "core.quotepath=off"]
    cmd += ["--git-dir", git_dir, "--work-tree", root] if git_dir else ["-C", root]
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        p = subprocess.run(cmd + args, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, cwd=root, timeout=600)
    except (OSError, subprocess.SubprocessError) as e:
        return None, b"", type(e).__name__
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").strip()


def repository_state(root):
    """True for a git repository, False when there is none, a text when .git is there but git cannot use it."""
    if not os.path.exists(os.path.join(root, ".git")):
        return False
    code, _out, err = run_git(["rev-parse", "--git-dir"], root)
    if code is None:
        return "git cannot be started, the repository was not checked"
    if code != 0:
        return "git cannot read the repository (%s)" % short(err, 120)
    return True


def ignore_rules(paths, root, git_dir=None):
    """{path: the rule that makes git ignore it, or None}. Asked from git itself, for tracked files too."""
    paths = list(paths)
    if not paths:
        return {}
    code, out, err = run_git(["check-ignore", "--no-index", "-v", "-n", "-z", "--stdin"], root, git_dir,
                             "\0".join(paths).encode("utf-8") + b"\0")
    if code not in (0, 1):
        raise RuntimeError(short(err, 160) or "git check-ignore did not run")
    fields = out.decode("utf-8", "replace").split("\0")
    rules = {}
    for n, path in enumerate(paths):
        source, line, pattern = (fields[4 * n:4 * n + 3] + ["", "", ""])[:3]
        rules[path] = "%s line %s: %s" % (source, line, pattern) if pattern and not pattern.startswith("!") else None
    return rules


def forbidden_path(path):
    """Why a path may never be tracked, or ''."""
    parts = path.replace("\\", "/").split("/")
    for folder in FORBIDDEN_FOLDERS:
        if folder in [p.lower() for p in parts[:-1]]:
            return "is in a folder named %s" % folder
    return "is a zip file" if parts[-1].lower().endswith(".zip") else ""


def git_objects(root):
    """Every object git stores for the branches, tags and the index: (index entries, {object id: [paths]}, problem)."""
    code, out, err = run_git(["ls-files", "-s", "-z"], root)
    if code != 0:
        return [], {}, "git ls-files did not run (%s)" % short(err, 120)
    staged, names = [], {}
    for record in out.decode("utf-8", "replace").split("\0"):
        if "\t" in record:
            meta, path = record.split("\t", 1)
            staged.append((meta.split()[1], path))
            names.setdefault(meta.split()[1], []).append(path)
    code, out, err = run_git(["rev-list", "--objects", "--all"], root)
    if code != 0:
        return staged, names, "git rev-list did not run (%s)" % short(err, 120)
    for line in out.decode("utf-8", "replace").splitlines():
        oid, _, path = line.partition(" ")
        if path and path not in names.setdefault(oid, []):
            names[oid].append(path)
        elif not path:
            names.setdefault(oid, [])
    return staged, names, ""


def git_blobs(root, ids):
    """Yield (object id, bytes) of every file content among the given objects."""
    ids = list(ids)
    if not ids:
        return
    code, out, _err = run_git(["cat-file", "--batch"], root, stdin=("\n".join(ids) + "\n").encode("ascii"))
    if code != 0:
        return
    pos = 0
    while pos < len(out):
        end = out.find(b"\n", pos)
        if end < 0:
            break
        head = out[pos:end].split()
        pos = end + 1
        if len(head) != 3:
            continue        # "<id> missing"
        size = int(head[2])
        if head[1] == b"blob":
            yield head[0].decode("ascii"), out[pos:pos + size]
        pos += size + 1


def git_checks(root, index, blocked, screenshots, workdir, add, matches, counts, notes):
    """The git part. Without a repository only the .gitignore rules can be checked (git is asked through an empty
    repository in the temporary folder, nothing is written into the site folder)."""
    state = repository_state(root)
    rule_text = "%s excludes every folder named %s and every *.zip" % (".gitignore", ", ".join(FORBIDDEN_FOLDERS))
    git_dir = None
    if state is not True:
        git_dir = os.path.join(workdir, "empty-repository")
        try:
            made = subprocess.run(["git", "init", "-q", git_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120).returncode == 0
        except (OSError, subprocess.SubprocessError):
            made = False
        git_dir = os.path.join(git_dir, ".git") if made else None
    how = "git check-ignore in the repository" if state is True else "git check-ignore against the .gitignore of the folder (not a repository yet)"
    if state is True or git_dir:
        try:
            rules = ignore_rules(list(IGNORE_SAMPLES) + screenshots, root, git_dir)
            open_paths = [p for p in IGNORE_SAMPLES if not rules.get(p)]
            add(SITE_PAGE, "gitignore_rules", not open_paths, rule_text,
                "all %d sample paths are ignored" % len(IGNORE_SAMPLES) if not open_paths else "%s not ignored" % plural(len(open_paths), "sample path", "sample paths"),
                how, "DEPLOY", items=["git would not ignore %s" % p for p in open_paths])
            shown = [p for p in screenshots if not rules.get(p)]
            if state is True:
                add(SITE_PAGE, "screenshots_ignored", not shown, "git ignores every image file under qa/ (screenshots are not for publishing)",
                    "%s under qa/, %d not ignored" % (plural(len(screenshots), "image file"), len(shown)), how, "DEPLOY",
                    items=["git would not ignore %s" % p for p in shown])
            else:
                add(SITE_PAGE, "screenshots_ignored", True, "git ignores every image file under qa/ (a failure once the folder is a git repository)",
                    "%s under qa/, %d would not be ignored" % (plural(len(screenshots), "image file"), len(shown)), how, "DEPLOY", level="note")
                if shown:
                    notes.append("DEPLOY: the current .gitignore would not ignore %s under qa/ (for example %s). Screenshots are not for "
                                 "publishing, extend .gitignore before the first commit." % (plural(len(shown), "image file"), shown[0]))
        except RuntimeError as e:
            add(SITE_PAGE, "gitignore_rules", False, rule_text, "git check-ignore did not run: %s" % e, how, "QA")
    else:
        add(SITE_PAGE, "gitignore_rules", True, rule_text, "not applicable: git cannot be started on this computer, so nothing can be committed from here",
            "no git", "DEPLOY", level="note")

    names = ("git_tracked_paths", "git_tracked_images", "git_history")
    if state is not True:
        text = "not applicable: the site folder is not a git repository yet" if state is False else state
        for check in names:
            add(SITE_PAGE, check, state is False, "checked once the folder is a git repository", text, "no usable .git folder", "DEPLOY" if state is False else "QA",
                level="note")
        return
    staged, objects, problem = git_objects(root)
    if problem:
        for check in names:
            add(SITE_PAGE, check, False, "git answers", problem, "git", "QA")
        return
    code, out, _err = run_git(["ls-tree", "-r", "-z", "--name-only", "HEAD"], root)
    committed = [p for p in out.decode("utf-8", "replace").split("\0") if p] if code == 0 else []
    current = unique([path for _oid, path in staged] + committed)
    bad = ["%s %s" % (p, forbidden_path(p)) for p in current if forbidden_path(p)]
    add(SITE_PAGE, "git_tracked_paths", not bad, "nothing from a folder named %s and no *.zip is tracked or staged" % ", ".join(FORBIDDEN_FOLDERS),
        "%s tracked or staged, %d not allowed" % (plural(len(current), "file"), len(bad)), "git ls-files and git ls-tree HEAD", "DEPLOY", items=bad)

    staged_ids = {}
    for oid, path in staged:
        staged_ids.setdefault(oid, []).append(path)
    wrong, tracked, old_paths, found = [], {}, [], 0
    for oid, data in git_blobs(root, objects):
        counts["git_objects"] += 1
        paths = objects.get(oid) or ["(no name)"]
        label = "git object %s (%s)" % (oid[:10], ", ".join(paths[:3]))
        digests = [(label, sha256(data))] + [(inner, sha256(member)) for inner, member in expand(label, data, [])]
        for where, digest in digests:
            if digest in blocked:
                found += 1
                matches.append(match(where, digest, blocked))
        for path in staged_ids.get(oid, []):
            kind = image_kind(path, data)
            if kind:
                info = refuse_restricted_owner_photos([classify(path, data, kind, index)], blocked)[0]
                tracked[info["class"]] = tracked.get(info["class"], 0) + 1
                if info["class"] not in PUBLISHABLE and not (info["class"] == SVG and not info.get("findings")):
                    wrong.append("%s is %s%s" % (path, info["class"], ": " + info["detail"] if info["detail"] else ""))
    for oid, paths in objects.items():
        old_paths += ["%s %s (in the history)" % (p, forbidden_path(p)) for p in paths if forbidden_path(p) and p not in current]
    add(SITE_PAGE, "git_tracked_images", not wrong, "every tracked image is allowed, allowed-derivative, a placeholder or an accepted owner photo",
        ", ".join("%d %s" % (n, c) for c, n in sorted(tracked.items())) or "no tracked image", "content of the git index, sorted like the files", "ASSETS", items=wrong)
    old_paths = unique(old_paths)
    add(SITE_PAGE, "git_history", not found and not old_paths, "no object stored by git is identical to a restricted file, no forbidden path in the history",
        "%s read, %d identical to a restricted file, %d forbidden paths in the history" % (plural(counts["git_objects"], "stored file"), found, len(old_paths)),
        "git rev-list --objects --all and the index, every object hashed", "DEPLOY", items=old_paths)


# ---------------------------------------------------------------- the whole check

def run(source, slugs, workdir):
    """Returns (results, matches, facts for the report)."""
    results, matches, notes = [], [], []

    def add(*args, **more):
        results.append(entry(*args, **more))

    # 1. The manifest says which files are allowed, which are placeholders (and how large) and which are owner photos.
    doc, manifest_problem = read_manifest(source.read(MANIFEST))
    index, manifest_problems = manifest_index(doc)
    problems = ([manifest_problem] if manifest_problem else []) + manifest_problems
    add(SITE_PAGE, "manifest", not problems, "%s can be read and records logo, g12 and g13 as allowed and nothing else" % MANIFEST,
        "%s recorded" % plural(len(index), "file") if not problems else short("; ".join(problems), 300), MANIFEST, "ASSETS", items=problems)
    if source.remote and doc is None:
        add(SITE_PAGE, "published_site", False, "the address serves the new site",
            "nothing was downloaded: without %s this does not look like the new site (%s)" % (MANIFEST, source.why_missing(MANIFEST)), source.base, "ASSETS")
        return results, matches, {"notes": notes, "images": [], "counts": {}, "classes": {}}
    if manifest_problem:
        notes.append("Without a readable %s no file can be recognised as allowed, so the licensed files that also sit in the restricted "
                     "folder (logo, g12, g13) are reported as matches too." % MANIFEST)

    # 2. Read the pages and stylesheets for image addresses. With --base this downloads them.
    page_refs, sheets = {}, [STYLESHEET]
    for slug in slugs:
        rel = page_file(slug)
        raw = source.read(rel, common.PAGES[slug])
        if raw is None:
            page_refs[slug] = None
            continue
        images, linked = page_addresses(raw)
        page_refs[slug] = unique(r for r in (resolve(v, rel, source.base) for v in images) if r)
        for href in linked:
            found = resolve(href, rel, source.base)
            if found and found[0] == "site" and found[1] not in sheets:
                sheets.append(found[1])
    sheet_refs, queue = {}, list(sheets)
    while queue:
        rel = queue.pop(0)
        raw = source.read(rel)
        if raw is None:
            sheet_refs[rel] = None
            continue
        images, imported = css_addresses(raw.decode("utf-8", "replace"))
        sheet_refs[rel] = unique(r for r in (resolve(v, rel, source.base) for v in images) if r)
        for href in imported:
            found = resolve(href, rel, source.base)
            if found and found[0] == "site" and found[1] not in sheet_refs and found[1] not in queue:
                queue.append(found[1])
    if source.remote:
        wanted = [r[1] for refs in list(page_refs.values()) + list(sheet_refs.values()) if refs for r in refs if r[0] == "site"]
        for rel in unique(wanted + list(index)):
            source.read(rel)

    # 3. Hash every file of the folder and sort every image.
    inv = site_inventory(source.root, index)
    table = {i["file"]: i for i in inv["images"]}
    verified = {i["sha256"]: i["file"] for i in inv["images"] if i["class"] in (ALLOWED, DERIVATIVE)}
    exempt = {d for d, rel in verified.items() if index[rel]["role"] in ("main", "sm", "icon")}
    judge_archive_pictures(inv, set(verified))

    # 4. The restricted side and the comparison.
    side = restricted_side()
    listed = [h.lower() for h in (doc or {}).get("restricted_sha256") or [] if isinstance(h, str)]
    blocked = blocked_table(side, exempt, listed)
    refuse_restricted_owner_photos(inv["images"], blocked)
    missing_names = sorted(n for n in RESTRICTED_NAMES if n not in side["stems"])
    restricted_ok = side["available"] and not missing_names and not side["problems"]
    if not side["available"]:
        restricted_text = "the restricted folder was not found next to the site folder (or where HB_RESTRICTED points), so the comparison is not proven"
    elif missing_names:
        restricted_text = "the restricted folder holds no file named %s" % ", ".join(missing_names[:8])
    elif side["problems"]:
        restricted_text = short("; ".join(side["problems"]), 300)
    else:
        restricted_text = "%s and %s hashed, %d text members of old archives left out, %d different hashes to compare" % (
            plural(side["counts"]["files"], "file"), plural(side["counts"]["archive_members"], "archive member"),
            side["counts"]["skipped_text_members"], len(blocked))
    add(SITE_PAGE, "restricted_folder", restricted_ok, "every file of the restricted folder can be read and all 26 Wix-only photos are there",
        restricted_text, "restricted folder next to the site folder, read only", "QA", items=side["problems"])
    for item in inv["items"]:
        if item["sha256"] in blocked:
            matches.append(match(item["path"], item["sha256"], blocked))
    counts = dict(inv["counts"], git_objects=0)

    # 5. Git (the folder on this computer only).
    screenshots = sorted(i["file"] for i in inv["images"] if i["class"] == SCREENSHOT)
    if source.remote:
        for check in ("gitignore_rules", "screenshots_ignored", "git_tracked_paths", "git_tracked_images", "git_history"):
            add(SITE_PAGE, check, True, "checked on the site folder, not on a published site", "not applicable: this run checked a web address",
                source.base, "DEPLOY", level="note")
    else:
        git_checks(source.root, index, blocked, screenshots, workdir, add, matches, counts, notes)

    where = "what the server serves" if source.remote else "every file of the site folder"
    add(SITE_PAGE, "hash_match", not matches, "no file is identical to a file of the restricted folder (0 matches)",
        plural(len(matches), "match", "matches"),
        "SHA-256 of %s (%s, %s, %s, %s) against %d restricted hashes" % (
            where, plural(counts["files"], "file"), plural(counts["archive_members"], "archive member"),
            plural(counts["embedded_pictures"], "embedded picture"), plural(counts["git_objects"], "git object"), len(blocked)),
        owner_of(matches[0]["site"]) if matches else "ASSETS", items=["%s is identical to %s" % (m["site"], ", ".join(m["restricted"][:4])) for m in matches])

    add(SITE_PAGE, "archives_readable", not inv["problems"], "every archive in the site folder can be opened and checked",
        "%s opened" % plural(len(inv["archives"]), "archive") if not inv["problems"] else plural(len(inv["problems"]), "problem"),
        "zip, tar, gz, bz2 and xz are read in memory", "DEPLOY", items=inv["problems"])
    strangers = [label for info in inv["archives"].values() for label in info["other"]]
    add(SITE_PAGE, "archive_pictures", not strangers, "a picture inside an archive of the site folder is a verified allowed file or passes the placeholder test",
        "%s in archives, %d of them neither allowed nor a placeholder" % (plural(sum(a["pictures"] for a in inv["archives"].values()), "picture"), len(strangers)),
        ", ".join(sorted(inv["archives"])) or "no archive in the site folder", "DEPLOY",
        items=["%s is neither a verified allowed file nor a placeholder" % s for s in strangers])

    # 6. The classes.
    by_class = {c: [i for i in inv["images"] if i["class"] == c] for c in CLASS_ORDER}
    missing_allowed = ["images/%s.jpg" % n for n in ALLOWED_NAMES if table.get("images/%s.jpg" % n, {}).get("class") != ALLOWED]
    add(SITE_PAGE, "allowed_images", not missing_allowed, "images/logo.jpg, images/g12.jpg and images/g13.jpg are there and have the SHA-256 the manifest records",
        "%d of %d verified" % (len(ALLOWED_NAMES) - len(missing_allowed), len(ALLOWED_NAMES)), "SHA-256 against %s" % MANIFEST, "ASSETS",
        items=["%s: %s" % (rel, table[rel]["detail"] if rel in table else source.why_missing(rel)) for rel in missing_allowed])

    unproven = []
    if side["available"]:
        for name in ALLOWED_NAMES:
            info = table.get("images/%s.jpg" % name)
            if not info or info["class"] != ALLOWED:
                continue
            sources = [l for l in side["table"].get(info["sha256"], []) if stem(l) in (name, "hbg_" + name)]
            if not sources and info["sha256"] not in REVIEWED_SHA256.get(name, ()):
                unproven.append("images/%s.jpg is recorded as allowed but is not byte-identical to its licensed source in the restricted folder. "
                                "If it was changed on purpose, QA looks at the picture and adds its SHA-256 to REVIEWED_SHA256 in qa/licensing_check.py" % name)
    add(SITE_PAGE, "allowed_sources", not unproven, "each allowed image is byte-identical to its licensed source (logo master, g12 and g13 of the backup)",
        "all verified allowed images are identical to their source" if not unproven and side["available"] else
        ("cannot be compared without the restricted folder" if not side["available"] else plural(len(unproven), "image") + " without a proven source"),
        "SHA-256 against the file with the same name in the restricted folder", "ASSETS", items=unproven)

    odd = []
    for info in by_class[DERIVATIVE]:
        record = index[info["file"]]
        if record["role"] == "composite":
            usable = lambda rel: table.get(rel or "", {}).get("class") in (ALLOWED, OWNER)
            unproven_sources = [str(p.get("source")) for p in record.get("parts") or []
                                if p.get("kind") != "text" and not usable(clean_rel(p.get("source")))]
            if unproven_sources:
                odd.append("%s: made from %s, which %s not a verified allowed image or accepted owner photo"
                           % (info["file"], ", ".join(unproven_sources), "is" if len(unproven_sources) == 1 else "are"))
                continue
            copy_data = source.read(info["file"])
            if copy_data is None:
                continue
            same, measured, problems = composite_shows(copy_data, record.get("parts"), source.read)
            info["detail"] = "composite, " + measured
            odd += ["%s: %s" % (info["file"], p) for p in problems]
            continue
        origin = table.get(record["source"] or "")
        if not origin or origin["class"] != ALLOWED:
            odd.append("%s: the image it is made from (%s) is not a verified allowed image" % (info["file"], record["source"]))
            continue
        copy_data, source_data = source.read(info["file"]), source.read(origin["file"])
        if copy_data is None or source_data is None:
            continue
        same, measured = made_from(copy_data, source_data, record["role"] == "icon" and stem(origin["file"]) == "logo")
        info["detail"] = "made from %s, %s" % (origin["file"], measured)
        if not same:
            odd.append("%s does not show %s: %s" % (info["file"], origin["file"], measured))
    add(SITE_PAGE, "allowed_derivatives", not odd, "every allowed-derivative has the SHA-256 the manifest records and shows the allowed image it is made from",
        "%s, %d not proven" % (plural(len(by_class[DERIVATIVE]), "derivative"), len(odd)), "SHA-256 against %s, small grey copies compared" % MANIFEST, "ASSETS", items=odd)

    failed = by_class[PLACEHOLDER_FAILED]
    add(SITE_PAGE, "placeholders", not failed,
        "every placeholder: at least 90 percent of the pixels within 6 levels of (232, 225, 218), darkest channel above 165, standard deviation below 12, the pixel size of the manifest",
        "%d of %d pass" % (len(by_class[PLACEHOLDER]), len(by_class[PLACEHOLDER]) + len(failed)), "pixel test with Pillow", "ASSETS",
        items=["%s: %s" % (i["file"], i["detail"]) for i in failed])
    owned, refused = by_class[OWNER], by_class[OWNER_REFUSED]
    add(SITE_PAGE, "owner_photos", not refused,
        "every image the manifest records as owner-photo has exactly the SHA-256 recorded there, is not identical to a restricted file and is a photo, not a placeholder",
        "%d of %d accepted" % (len(owned), len(owned) + len(refused)) if owned or refused else "no image is recorded as owner-photo",
        "SHA-256 against %s and against the restricted hashes (build contract, decision 27)" % MANIFEST,
        "ASSETS" if any(i.get("refused") == "restricted" for i in refused) else "PAGES",
        items=["%s: %s" % (i["file"], i["detail"]) for i in refused], level="note" if owned and not refused else None)
    if owned:
        notes.append("%s accepted (status owner-photo in %s, SHA-256 as recorded, identical to no restricted file): %s. The hash proves that a file is "
                     "not one of the restricted files, it cannot prove whose picture it is: a person looks at each new owner photo once."
                     % (plural(len(owned), "owner photo"), MANIFEST, ", ".join(i["file"] for i in owned)))
    add(SITE_PAGE, "unknown_images", not by_class[UNKNOWN], "no image file that is neither allowed, allowed-derivative, placeholder, owner-photo nor a screenshot under qa/",
        plural(len(by_class[UNKNOWN]), "UNKNOWN image"), "every file with an image name or image content", "ASSETS",
        items=["%s: %s" % (i["file"], i["detail"]) for i in by_class[UNKNOWN]])
    loud = [e for e in inv["embedded"] if not e["file"].startswith("qa/")]
    quiet = [e for e in inv["embedded"] if e["file"].startswith("qa/")]
    add(SITE_PAGE, "embedded_pictures", not loud, "no picture is written into a page, stylesheet, script or data file as base64 text",
        plural(len(loud), "embedded picture"), "every text file read for data addresses",
        owner_of(loud[0]["file"]) if loud else "ASSETS", items=["%s: %s" % (e["label"], e["detail"]) for e in loud])
    if quiet:
        notes.append("%s under qa/ (not judged, hashed like every file): %s" % (plural(len(quiet), "embedded picture"), ", ".join(unique(e["file"] for e in quiet))))
    risky = [i for i in by_class[SVG] if i.get("findings")]
    add(SITE_PAGE, "svg_files", not risky, "an svg file is only a drawing: no picture inside it, nothing loaded from another address",
        "%s flagged for review, %d with a picture inside" % (plural(len(by_class[SVG]), "svg file"), len(risky)),
        ", ".join(i["file"] for i in by_class[SVG]) or "no svg file", "ASSETS", items=["%s: %s" % (i["file"], i["detail"]) for i in risky],
        level="note" if by_class[SVG] and not risky else None)
    absent = [rel for rel in sorted(index) if rel not in inv["paths"]]
    add(SITE_PAGE, "manifest_files_present", not absent, "every image file the manifest records %s" % ("is served" if source.remote else "exists"),
        "%d of %d there" % (len(index) - len(absent), len(index)), MANIFEST, "ASSETS", items=["%s: %s" % (rel, source.why_missing(rel)) for rel in absent])
    if not source.remote:
        add(SITE_PAGE, "site_screenshots", True, "image files under qa/ are evidence of the checks, not site files",
            "%s under qa/, not for publishing" % plural(len(screenshots), "image file"), "qa/", "QA", level="note" if screenshots else None)

    # 7. The image addresses of the pages and stylesheets.
    def judge(refs):
        bad, good = [], 0
        for kind, value in refs:
            info = table.get(value) if kind == "site" else None
            if kind == "external":
                bad.append("%s is a picture on another host" % short(value, 120))
            elif kind == "outside":
                bad.append("%s points outside the site folder" % short(value, 120))
            elif info is None:
                bad.append("%s: %s" % (value, source.why_missing(value) if value not in inv["paths"] else "is not an image file"))
            elif info["class"] in PUBLISHABLE or (info["class"] == SVG and not info.get("findings")):
                good += 1
            else:
                bad.append("%s is %s" % (value, info["class"]))
        return bad, good

    for slug in slugs:
        refs, rel = page_refs[slug], page_file(slug)
        if refs is None:
            add(slug, "page_images", False, "the page can be read", "%s: %s" % (rel, source.why_missing(rel)), rel, "PAGES")
            continue
        bad, good = judge(refs)
        add(slug, "page_images", not bad, "every image address of the page is an allowed image, an allowed-derivative, a placeholder or an accepted owner photo of this site",
            "%s, %d not acceptable" % (plural(len(refs), "image address", "image addresses"), len(bad)), rel, "PAGES", items=bad)
    for rel, refs in sheet_refs.items():
        name = "stylesheet_images" if rel == STYLESHEET else "stylesheet_images %s" % rel
        if refs is None:
            add(SITE_PAGE, name, False, "the stylesheet can be read", "%s: %s" % (rel, source.why_missing(rel)), rel, "DESIGN")
            continue
        bad, good = judge(refs)
        add(SITE_PAGE, name, not bad, "every image address of the stylesheet is an allowed image, an allowed-derivative, a placeholder or an accepted owner photo of this site",
            "%s, %d not acceptable" % (plural(len(refs), "image address", "image addresses"), len(bad)), rel, "DESIGN", items=bad)

    # 8. Addresses that must not exist on a published site.
    if source.remote:
        answers = [(address,) + source.status(address) for address in FORBIDDEN_ADDRESSES]
        open_doors = ["%s answers %s" % (a, status if status else note or "nothing") for a, status, note in answers if status != 404]
        add(SITE_PAGE, "published_forbidden_addresses", not open_doors, "%s answer 404" % ", ".join(FORBIDDEN_ADDRESSES),
            "%d of %d answer 404" % (len(answers) - len(open_doors), len(answers)), source.base, "DEPLOY", items=open_doors)
        local_shots = []
        if os.path.isdir(common.QA):
            for rel, full in walk(common.QA):
                if ext(rel) in RASTER_EXT + SVG_EXT:
                    local_shots.append("qa/" + rel)
        probes = local_shots[:MAX_SCREENSHOT_PROBES]
        seen = [(address,) + source.status(address) for address in probes]
        served = ["%s answers %s" % (a, status if status else note or "nothing") for a, status, note in seen if status != 404]
        add(SITE_PAGE, "published_screenshots", not served, "the screenshots under qa/ of this computer are not on the published site",
            "%d of %s answer 404" % (len(seen) - len(served), plural(len(seen), "address", "addresses")) if probes else "no screenshot under qa/ to ask for",
            source.base, "DEPLOY", items=served, level=None if probes else "note")
        local_doc, _problem = read_manifest(Local(common.SITE).read(MANIFEST))
        if local_doc is not None:
            local_index = manifest_index(local_doc)[0]
            same = {r: v["sha256"] for r, v in index.items()} == {r: v["sha256"] for r, v in local_index.items()}
            notes.append("The published %s records %s as the one in the site folder." % (MANIFEST, "the same files and hashes" if same else "OTHER files or hashes than"))
    else:
        for check in ("published_forbidden_addresses", "published_screenshots"):
            add(SITE_PAGE, check, True, "checked with --base on the published site", "not applicable: this run checked the site folder", "local files", "DEPLOY", level="note")

    for rel, info in sorted(inv["archives"].items()):
        notes.append("Archive %s: %s, %s (%d verified allowed files, %d placeholder-like, %d other)." % (
            rel, plural(info["members"], "member"), plural(info["pictures"], "picture"), info["known"], info["placeholder_like"], len(info["other"])))
    if side["counts"]["skipped_empty"]:
        notes.append("%s in the restricted folder left out of the comparison." % plural(side["counts"]["skipped_empty"], "empty file"))
    facts = {"notes": notes, "images": inv["images"],
             "classes": {c: len(by_class[c]) for c in CLASS_ORDER},
             "counts": {"site": counts, "restricted": dict(side["counts"], different_hashes_compared=len(blocked))}}
    return results, matches, facts


# ---------------------------------------------------------------- report files

def cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def write_markdown(doc, results, matches, facts, verdict, code):
    lines = ["# Licensing check", "",
             "Result: **%s** (exit code %d)" % (verdict, code), "",
             "- Checked: %s" % ("the published site at %s" % doc["base"] if doc.get("source") == "server answers" else "the files in the site folder"),
             "- When: %s" % doc["generated"],
             "- Script: qa/licensing_check.py, data: qa/reports/licensing.json", ""]
    if matches:
        lines += ["**Hard stop. No commit, no push. Tell the owner.** A file in the site is identical to a restricted file.", ""]
    counts = facts.get("counts") or {}
    if counts:
        s, r = counts["site"], counts["restricted"]
        lines += ["## Files hashed (SHA-256)", "",
                  "| Side | Files | Archive members | Also |", "|---|---|---|---|",
                  "| Site | %d | %d | %d embedded pictures, %d git objects |" % (s["files"], s["archive_members"], s["embedded_pictures"], s["git_objects"]),
                  "| Restricted folder | %d | %d | %d text members of old archives left out, %d Wix reference screenshots |" % (
                      r["files"], r["archive_members"], r["skipped_text_members"], r["reference_screenshots"]),
                  "", "Different restricted hashes a site file was compared with: %d" % r["different_hashes_compared"], ""]
    classes = facts.get("classes") or {}
    if classes:
        lines += ["## Images by class", "", "| Class | Files |", "|---|---|"]
        lines += ["| %s | %d |" % (c, classes[c]) for c in CLASS_ORDER]
        lines += [""]
    owner = [i for i in facts.get("images") or [] if i.get("class") in (OWNER, OWNER_REFUSED)]
    if owner:
        lines += ["## Owner photos (status owner-photo in the manifest)", "",
                  "Accepted when the file has the SHA-256 the manifest records and that hash is the hash of no restricted file. "
                  "The hash cannot prove whose picture it is, so a person looks at each new one once.", "",
                  "| File | Result | What was found | SHA-256 |", "|---|---|---|---|"]
        lines += ["| %s | %s | %s | %s |" % (cell(i["file"]), "accepted" if i["class"] == OWNER else "NOT ACCEPTED", cell(i["detail"]), i["sha256"][:16]) for i in owner]
        lines += [""]
    lines += ["## Matches (zero expected)", ""]
    if matches:
        lines += ["| File in the site | Identical to | What that is | SHA-256 |", "|---|---|---|---|"]
        lines += ["| %s | %s | %s | %s |" % (cell(m["site"]), cell(", ".join(m["restricted"])), m["kind"], m["sha256"][:16]) for m in matches]
        if any(m["kind"] == "other file of the restricted folder" for m in matches):
            lines += ["", "A match with a file that is not one of the 26 Wix-only photos (for example an old icon inside an old zip) is a stop "
                      "all the same: the file leaves the site folder, or the owner decides that it is not restricted."]
    else:
        lines += ["None."]
    failed = [r for r in results if not r["ok"]]
    lines += ["", "## Failures", ""]
    if failed:
        lines += ["| Owner | Page | Check | Found |", "|---|---|---|---|"]
        for r in failed:
            lines.append("| %s | %s | %s | %s |" % (r["owner"], r["page"], r["check"], cell(r["actual"])))
        details = [(r, i) for r in failed if r["check"] != "hash_match" for i in r.get("items") or []]
        if details:
            lines += ["", "Details:", ""]
            lines += ["- [%s] %s: %s" % (r["owner"], r["check"], i) for r, i in details[:200]]
            if len(details) > 200:
                lines.append("- and %d more, see the JSON report" % (len(details) - 200))
    else:
        lines += ["None."]
    if facts.get("notes"):
        lines += ["", "## Notes", ""] + ["- %s" % n for n in facts["notes"]]
    lines += ["", "## All checks of this run", "", "| Page | Check | Result | Found |", "|---|---|---|---|"]
    for r in results:
        lines.append("| %s | %s | %s | %s |" % (r["page"], r["check"], "ok" if r["ok"] else "FAIL", cell(r["actual"])))
    lines += ["", "Exit codes: 0 pass, 1 failure, 2 a file identical to a restricted file was found.", ""]
    os.makedirs(common.REPORTS, exist_ok=True)
    with open(os.path.join(common.REPORTS, NAME + ".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- main

def main(argv=None):
    # A wrong option ends with exit code 1 (common.Parser). Exit code 2 is kept for a hash match alone.
    ap = common.cli_parser(
        "Licensing check: hashes against the restricted folder, pixel test of every image, git and the published site.",
        base_help="check what this address serves instead of the site folder, for example https://achoostorm.github.io/hairbygerta/",
        page_help="SLUG[,SLUG] or all (default): the pages read for image addresses. The folder is always checked completely.",
        viewport_help="accepted because every QA script takes it; not used, this script needs no browser")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    slugs = common.cli_pages(ap, args.page)

    workdir = make_workdir()
    try:
        source = Published(args.base, os.path.join(workdir, "served")) if args.base else Local(common.SITE)
        results, matches, facts = run(source, slugs, workdir)
    finally:
        if not remove_tree(workdir):
            print("licensing: the temporary folder %s could not be deleted, delete it by hand" % workdir)

    failed = [r for r in results if not r["ok"]]
    code = 2 if matches else (1 if failed else 0)
    verdict = "LICENSING MATCH" if matches else ("FAIL" if failed else "PASS")
    for r in results:
        if r.get("level") is None:
            r.pop("level", None)
        if not r.get("items"):
            r.pop("items", None)
    site_counts = (facts.get("counts") or {}).get("site") or {}
    restricted_counts = (facts.get("counts") or {}).get("restricted") or {}
    # The first keys are plain numbers so that qa/run_all.py can quote them.
    extra = {"script": "qa/licensing_check.py", "source": "server answers" if source.remote else "files in the site folder",
             "verdict": verdict, "exit_code": code,
             "files_hashed": site_counts.get("files", 0),
             "restricted_hashes": restricted_counts.get("different_hashes_compared", 0),
             "restricted_files_hashed": restricted_counts.get("files", 0) + restricted_counts.get("archive_members", 0)
             - restricted_counts.get("skipped_text_members", 0) + restricted_counts.get("reference_screenshots", 0),
             "images_checked": len(facts.get("images") or []),
             "matches": matches,
             "last_run": {"pages": slugs, "checks": len(results), "failed": len(failed), "matches": len(matches)},
             "counts": facts.get("counts"), "images_by_class": facts.get("classes"),
             "failures": [{"owner": r["owner"], "page": r["page"], "check": r["check"], "actual": r["actual"], "items": r.get("items", [])} for r in failed],
             "notes": facts.get("notes"), "images": facts.get("images")}
    # A run always judges the whole site, so every earlier entry of the pages it covers is replaced, not merged.
    doc = common.save_report(NAME, results, source.label, extra, replace=set(slugs) | {SITE_PAGE})
    write_markdown(doc, results, matches, facts, verdict, code)

    for m in matches:
        print("LICENSING MATCH  %s  ==  %s  [%s]" % (m["site"], ", ".join(m["restricted"]), m["kind"]))
    for r in failed:
        items = r.get("items") or [r["actual"]]
        if r["check"] == "hash_match":
            items = ["%s, listed above as LICENSING MATCH" % r["actual"]]
        for item in items[:MAX_LINES_PER_CHECK]:
            print("FAIL [%s] %s | %s | %s" % (r["owner"], r["page"], r["check"], short(item, 300)))
        if len(items) > MAX_LINES_PER_CHECK:
            print("FAIL [%s] %s | %s | and %d more, see the report" % (r["owner"], r["page"], r["check"], len(items) - MAX_LINES_PER_CHECK))
    owners = {}
    for r in failed:
        owners[r["owner"]] = owners.get(r["owner"], 0) + 1
    by_owner = " (%s)" % ", ".join("%s %d" % (o, n) for o, n in sorted(owners.items())) if owners else ""
    classes = facts.get("classes") or {}
    print("%s: %s, %s, %d failed%s, images: %s, source %s, report qa/reports/%s.json and .md"
          % (NAME, verdict, plural(len(results), "check"), len(failed), by_owner,
             ", ".join("%d %s" % (classes[c], c) for c in CLASS_ORDER if classes.get(c)) or "none", source.label, NAME)
          + (" | %s: hard stop, no commit, no push, tell the owner" % plural(len(matches), "match", "matches") if matches else ""))
    return code


if __name__ == "__main__":
    sys.exit(main())
