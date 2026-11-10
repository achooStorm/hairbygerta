#!/usr/bin/env python3
"""Rebuild the web font files of hairbygerta.com from the two open fonts.

The site sets its texts in two fonts. Both are free to use and to pass on under the SIL Open Font License:

    Figtree              the text font, regular and bold
    Bodoni Moda Italic   the slanted serif of the headings, regular and bold

The pages load them from the folder fonts/ of the site itself, not from Google Fonts. That saves every
visitor a connection to two more servers before the first text can be drawn, and no visitor's address
goes to a font server.

Source (the only input; it is not kept in the site folder):
    the repository github.com/google/fonts
        ofl/figtree/Figtree[wght].ttf                      and OFL.txt next to it
        ofl/bodonimoda/BodoniModa-Italic[opsz,wght].ttf    and OFL.txt next to it

Output, all in fonts/:
    figtree-latin.woff2                    the letters of English and of western Europe
    figtree-latin-ext.woff2                letters of other languages written in Latin letters
    bodoni-moda-italic-latin.woff2
    bodoni-moda-italic-latin-ext.woff2
    OFL-Figtree.txt, OFL-BodoniModa.txt    the license of each font, copied word for word
    fonts.json                             the list of these files: where each comes from, which
                                           characters it holds, its size and its SHA-256

How to run it:
    python tools/make_fonts.py --check             needs nothing but Python: writes nothing, exit 1
                                                   when a file in fonts/ is not the one fonts.json lists,
                                                   is missing, or is not listed
    python tools/make_fonts.py --source FOLDER     builds the files again. FOLDER is a copy of the two
                                                   folders named above (the script looks through FOLDER
                                                   for the two .ttf files). Needs two Python packages:
                                                   python -m pip install fonttools brotli
                                                   Add --commit TEXT to write down which version of the
                                                   repository the files came from.

What it does to the fonts
    Both      Each font is cut down to the characters of one group (latin, latin-ext) and saved as
              WOFF2, the smallest format every current browser reads. The stylesheet names the
              characters of each file (unicode-range), so a browser fetches the latin-ext files only for
              a page that shows such a letter. No drawing of a letter and no spacing is changed.
    Figtree   Nothing else. The file keeps its weight axis as it is.
    Bodoni    The stylesheet draws the serif at one fixed optical size ("opsz" 14, see body in
              css/style.css). That size is built into the file, and the weight axis is cut to 400 to 700,
              the two weights the site uses. The file is then half as large and the page looks the same.

The same source files and the same versions of the two packages give the same bytes. A newer fonttools
may write other bytes that draw the same letters. fonts.json then changes with them, which is fine.

When a font file changes, run the QA suite: qa/check_repo.py compares fonts/ with fonts.json and with the
@font-face rules of the stylesheet.
"""

import argparse
import hashlib
import io
import json
import os
import shutil
import sys

sys.dont_write_bytecode = True

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = "fonts"
LIST_NAME = "fonts/fonts.json"
REPOSITORY = "https://github.com/google/fonts"

# The characters of each group, as Google Fonts cuts them. The stylesheet repeats them (unicode-range).
SUBSETS = {
    "latin": ("U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, "
              "U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
    "latin-ext": ("U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, "
                  "U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, "
                  "U+A720-A7FF"),
}

# name of the output files: (source file, folder in the repository, family, style, what is fixed in the
# file (None: nothing), the weights the file can draw, name of the license copy)
FAMILIES = {
    "figtree": ("Figtree[wght].ttf", "ofl/figtree", "Figtree", "normal", None, "300 to 900", "OFL-Figtree.txt"),
    "bodoni-moda-italic": ("BodoniModa-Italic[opsz,wght].ttf", "ofl/bodonimoda", "Bodoni Moda", "italic",
                           {"opsz": 14, "wght": (400, 700)}, "400 to 700", "OFL-BodoniModa.txt"),
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def find(folder, name):
    """The path of the file called name somewhere under folder, or None."""
    for here, _dirs, files in os.walk(folder):
        if name in files:
            return os.path.join(here, name)
    return None


def build_one(source_path, limits, unicodes):
    """One WOFF2 file as bytes: the source font, with limits built in, cut down to the characters in unicodes."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    font = TTFont(source_path, recalcTimestamp=False)
    if limits:
        font = instancer.instantiateVariableFont(font, limits)
        # Saved and read again: the next step needs the tables as a fresh file has them.
        middle = io.BytesIO()
        font.save(middle)
        middle.seek(0)
        font = TTFont(middle, recalcTimestamp=False)
    options = subset.Options()
    options.layout_features = ["*"]         # every feature of the font stays (kerning, ligatures and the rest)
    options.notdef_outline = True
    options.name_IDs = [1, 2, 3, 4, 5, 6, 13, 14]   # the names, and the two lines about the license
    options.name_languages = [0x409]
    options.flavor = "woff2"
    options.unicodes = subset.parse_unicodes(unicodes.replace(" ", ""))
    cutter = subset.Subsetter(options)
    cutter.populate(unicodes=options.unicodes)
    cutter.subset(font)
    out = io.BytesIO()
    subset.save_font(font, out, options)
    return out.getvalue()


def source_version(source_path):
    from fontTools.ttLib import TTFont
    return TTFont(source_path)["name"].getDebugName(5) or ""


def build(source, commit):
    try:
        import fontTools  # noqa: F401
        import brotli  # noqa: F401
    except ImportError as e:
        sys.exit("make_fonts: building needs two Python packages (python -m pip install fonttools brotli). Missing: %s" % e.name)
    target = os.path.join(SITE, FONTS_DIR)
    os.makedirs(target, exist_ok=True)
    records, licenses = [], []
    for stem, (ttf, repo_folder, family, style, limits, weights, license_name) in FAMILIES.items():
        path = find(source, ttf)
        if path is None:
            sys.exit("make_fonts: %s was not found under %s" % (ttf, source))
        license_path = os.path.join(os.path.dirname(path), "OFL.txt")
        if not os.path.isfile(license_path):
            sys.exit("make_fonts: OFL.txt was not found next to %s" % ttf)
        shutil.copyfile(license_path, os.path.join(target, license_name))
        licenses.append("%s/%s" % (FONTS_DIR, license_name))
        with open(path, "rb") as f:
            source_hash = sha256(f.read())
        version = source_version(path)
        for group, unicodes in SUBSETS.items():
            name = "%s/%s-%s.woff2" % (FONTS_DIR, stem, group)
            data = build_one(path, limits, unicodes)
            with open(os.path.join(SITE, *name.split("/")), "wb") as f:
                f.write(data)
            records.append({
                "file": name, "family": family, "style": style, "weights": weights, "characters": group,
                "unicode_range": unicodes,
                "fixed": ("optical size 14" if limits else "nothing"),
                "source": "%s/%s" % (repo_folder, ttf), "source_version": version, "source_sha256": source_hash,
                "bytes": len(data), "sha256": sha256(data),
            })
            print("%-44s %6d bytes  sha256 %s" % (name, len(data), sha256(data)))
    doc = {
        "what": "The web font files of the site. Written by tools/make_fonts.py, do not edit by hand.",
        "license": "SIL Open Font License 1.1, the text of each font is in the files named under license_files",
        "license_files": licenses,
        "source_repository": REPOSITORY,
        "source_commit": commit or "",
        "fonts": records,
    }
    with open(os.path.join(SITE, *LIST_NAME.split("/")), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
    print("%s written" % LIST_NAME)
    return 0


def check():
    """Compare fonts/ with fonts/fonts.json. Returns the list of things that are wrong."""
    wrong = []
    try:
        with open(os.path.join(SITE, *LIST_NAME.split("/")), encoding="utf-8") as f:
            doc = json.load(f)
    except (OSError, ValueError) as e:
        return ["%s cannot be read (%s)" % (LIST_NAME, e)]
    listed = {}
    for record in doc.get("fonts") or []:
        listed[record.get("file")] = record.get("sha256")
    for name in doc.get("license_files") or []:
        listed[name] = None
    listed[LIST_NAME] = None
    for name, wanted in sorted(listed.items()):
        path = os.path.join(SITE, *str(name).split("/"))
        if not os.path.isfile(path):
            wrong.append("%s is listed in %s but is not there" % (name, LIST_NAME))
            continue
        if wanted is not None:
            with open(path, "rb") as f:
                data = f.read()
            if sha256(data) != wanted:
                wrong.append("%s is not the file %s lists (other SHA-256)" % (name, LIST_NAME))
            if data[:4] != b"wOF2":
                wrong.append("%s is not a WOFF2 file" % name)
    folder = os.path.join(SITE, FONTS_DIR)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if "%s/%s" % (FONTS_DIR, name) not in listed:
            wrong.append("%s/%s is in the folder but not in %s" % (FONTS_DIR, name, LIST_NAME))
    return wrong


def main():
    parser = argparse.ArgumentParser(description="Rebuild or check the web font files in fonts/.")
    parser.add_argument("--source", metavar="FOLDER", help="build the files from the two .ttf files found under FOLDER")
    parser.add_argument("--commit", metavar="TEXT", help="with --source: the version of the font repository, written into fonts.json")
    parser.add_argument("--check", action="store_true", help="write nothing, exit 1 when fonts/ and fonts.json do not agree")
    args = parser.parse_args()
    if args.check == bool(args.source):
        parser.error("give either --check or --source FOLDER")
    if args.source:
        return build(args.source, args.commit)
    wrong = check()
    for line in wrong:
        print(line)
    print("fonts: %s" % ("%d problems" % len(wrong) if wrong else "every file is the one %s lists" % LIST_NAME))
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
