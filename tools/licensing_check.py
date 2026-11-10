#!/usr/bin/env python3
"""Photo licensing check for hairbygerta.com.

WHY
    Only three pictures of the old Wix site may be published anywhere else:
    the salon logo (images/logo.jpg) and the owner's own two photos
    (images/g12.jpg and images/g13.jpg), together with the copies and icons
    made from them. Every other photo is licensed for the Wix site only, or
    has no proven license, and must never be committed, pushed or published.
    This script is the guard. It stops a commit that holds one of those
    photos, whatever the file is called.

WHAT IT CHECKS
    1. Content. The SHA-256 fingerprint of every file is compared with
       - tools/restricted-hashes.txt, the fingerprints of all Wix-only photos
         in every size and copy we know of and of the backup zip files that
         hold them, and
       - the private folder "hairbygerta-wix-only-photos" next to the site
         folder, when it exists on this computer: every image in it, images
         inside its zip files included, and those zip files themselves, read
         fresh on every run. The licensed files are left out. They are
         recognised by content. A file that carries the name of one of the
         26 Wix-only photos is never left out.
       A zip archive that hides under another file name is opened and the
       files inside it are checked the same way.
    2. Path. Nothing inside a folder named source-photos, new-photos, zip or
       _tmp and no *.zip file may be committed.
    Every other file passes. That includes the file named CNAME that GitHub
    adds to the top folder when the custom domain is set.

WHICH FILES
    python tools/licensing_check.py
        every file git would track: tracked files plus new files that
        .gitignore does not exclude, as they are on disk (before "git init"
        the script reads .gitignore itself to pick the same files)
    python tools/licensing_check.py --staged
        exactly what the next commit would hold: the staged content of every
        file in the index (this is what the pre-commit hook runs)
    python tools/licensing_check.py --all
        every file in the site folder, ignored files included
    python tools/licensing_check.py --write-list
        maintenance: read the private photo folder again and add any new
        fingerprint to tools/restricted-hashes.txt (the list only grows)

THE COMMIT GUARD
    python tools/licensing_check.py --install-hook
        switches it on: copies tools/hooks/pre-commit to the place where git
        looks for it. Needed once after "git init" and once after every fresh
        clone. Works in Command Prompt, PowerShell and Git Bash. From then on
        every commit runs the check first, in GitHub Desktop too. When a
        commit is stopped, the message names each file and says what to do
        in GitHub Desktop and on the command line.

EXIT STATUS
    0  nothing restricted found
    1  LICENSING MATCH, or a path that is NOT ALLOWED: do not commit
    2  the check could not run (treat it as a stop)

Python standard library only. All paths are worked out from where this script
is, so it can be started from any folder.
"""

import argparse
import sys
sys.dont_write_bytecode = True
import hashlib
import io
import os
import re
import subprocess
import sys
import zipfile

# ---------------------------------------------------------------- settings

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIST_NAME = "tools/restricted-hashes.txt"
HOOK_NAME = "tools/hooks/pre-commit"
PRIVATE_FOLDER_NAME = "hairbygerta-wix-only-photos"
PRIVATE_FOLDER = os.path.join(os.path.dirname(SITE), PRIVATE_FOLDER_NAME)

# Nothing inside a folder with one of these names may be committed.
FORBIDDEN_FOLDERS = ("source-photos", "new-photos", "zip", "_tmp")

# The licensed files of this site. A file in the private folder with exactly
# the same content as one of these is licensed too and is not restricted.
LICENSED_FILES = (
    "images/logo.jpg",
    "images/g12.jpg",
    "images/g13.jpg",
    "images/sm/g12.jpg",
    "images/sm/g13.jpg",
    "images/g12.webp",
    "images/g13.webp",
    "images/sm/g12.webp",
    "images/sm/g13.webp",
    "favicon.ico",
    "images/favicon.png",
    "images/apple-touch-icon.png",
)

# The 26 photos of the old site that are licensed for Wix only, or have no
# proven license. A file of the private folder that carries one of these names
# is always restricted, whatever the files of the site hold at the moment.
RESTRICTED_NAMES = frozenset((
    "about-salon", "brunette-balayage", "copper-waves", "foils-highlights",
    "g01", "g02", "g04", "g05", "g06", "g07", "g10", "g14", "g15", "g16",
    "g17", "g18", "g19", "g20", "g21", "home-smile", "home-styling",
    "home-waves", "makeup-red-lips", "meet-extensions", "svc-bridal",
    "svc-haircut",
))

IMAGE_EXTENSIONS = frozenset((
    ".jpg", ".jpeg", ".jpe", ".jfif", ".png", ".gif", ".webp", ".bmp",
    ".tif", ".tiff", ".ico", ".cur", ".svg", ".svgz", ".avif", ".heic",
    ".heif", ".psd", ".jp2", ".jxl",
))
HEIF_BRANDS = (b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1", b"avif", b"avis")

MAX_ZIP_DEPTH = 3                        # a zip inside a zip inside a zip
MAX_MEMBER_BYTES = 512 * 1024 * 1024     # larger files inside a zip are not unpacked

LIST_HEADER = """\
# Restricted file fingerprints for hairbygerta.com
#
# One SHA-256 fingerprint per line, sorted, no file names. A file with one of
# these fingerprints must never be committed, pushed or published with this
# site. The list is made from the private folder
# "hairbygerta-wix-only-photos". When it was first written it held 60 lines:
#
#   53  pictures that are licensed for the old Wix site only, or have no
#       proven license: the 26 original photos and their copies in every size
#       we know of (52 files) and the contact sheet that shows them
#    2  backup zip files that hold those pictures
#    5  old copies, from the first version of this site, of files made from
#       the licensed pictures (three icons made from the logo and the first
#       800 px copies of g12.jpg and g13.jpg). They sit inside one of the
#       backup zip files and are not the files this site uses today. They are
#       not Wix-only photos. They are kept on the list on purpose, because a
#       file that comes out of a photo backup does not belong in this site.
#
# Not on the list: the licensed files as they are in this site today, which
# are the salon logo, the owner's own photos g12.jpg and g13.jpg, and the
# copies and icons made from them. They are recognised by content, not by
# name. A picture of the private folder that is not exactly one of them is on
# the list, because any doubt means restricted.
#
# tools/licensing_check.py reads this list and stops every commit that holds
# a file with one of these fingerprints, whatever the file is called.
# Do not remove lines. To add the fingerprints of new restricted photos run:
#     python tools/licensing_check.py --write-list
"""


class CheckError(Exception):
    """The check could not run."""


# ---------------------------------------------------------------- helpers


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def site_path(name):
    """The place on disk of a site path written with forward slashes."""
    return os.path.join(SITE, *name.split("/"))


def read_file(path, label):
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as error:
        raise CheckError("%s could not be read (%s)." % (label, error.strerror or error))


def is_image(name, data):
    """True when a file is a picture, judged by its name or its first bytes."""
    if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
        return True
    head = data[:16]
    return (head.startswith(b"\xff\xd8\xff")                                # JPEG
            or head.startswith(b"\x89PNG\r\n\x1a\n")                        # PNG
            or head[:6] in (b"GIF87a", b"GIF89a")                           # GIF
            or (head[:4] == b"RIFF" and head[8:12] == b"WEBP")              # WebP
            or head[:4] in (b"II*\x00", b"MM\x00*")                         # TIFF
            or head[:4] in (b"\x00\x00\x01\x00", b"\x00\x00\x02\x00")       # ICO, CUR
            or (head[:2] == b"BM" and head[6:10] == b"\x00\x00\x00\x00")    # BMP
            or head[:4] == b"8BPS"                                          # Photoshop
            or (head[4:8] == b"ftyp" and head[8:12] in HEIF_BRANDS))        # HEIC, AVIF


def open_zip(data):
    """A ZipFile for `data` when it is a zip archive, otherwise None."""
    if data[:2] != b"PK":
        return None
    try:
        return zipfile.ZipFile(io.BytesIO(data))
    except Exception:
        return None


def zip_members(archive, depth=1):
    """Yield (name, content) for every file in a zip archive, zips inside it
    included. The content is None for a file that cannot be unpacked
    (password, damage, too large)."""
    for info in archive.infolist():
        if info.filename.endswith("/"):
            continue
        try:
            if info.file_size > MAX_MEMBER_BYTES:
                raise ValueError("too large")
            data = archive.read(info)
        except Exception:
            yield info.filename, None
            continue
        yield info.filename, data
        inner = open_zip(data) if depth < MAX_ZIP_DEPTH else None
        if inner is not None:
            for name, inner_data in zip_members(inner, depth + 1):
                yield info.filename + " > " + name, inner_data


def photo_name(label):
    """The file name at the end of a path or of an "archive > member" label,
    in small letters and without its ending."""
    last = label.replace("\\", "/").split(" > ")[-1].split("/")[-1]
    return os.path.splitext(last)[0].lower()


def forbidden_path(path):
    """Why a path may never be committed, or None when the path is fine."""
    parts = path.replace("\\", "/").split("/")
    for folder in parts[:-1]:
        if folder.lower() in FORBIDDEN_FOLDERS:
            return ('It is inside a folder named "%s". Nothing in a folder with that '
                    "name may be committed." % folder)
    if parts[-1].lower().endswith(".zip"):
        return "It is a zip file. Zip files may not be committed."
    return None


# ---------------------------------------------------------------- what is restricted


def load_list():
    """The fingerprints in tools/restricted-hashes.txt, or None when the file
    is not there."""
    path = site_path(LIST_NAME)
    if not os.path.isfile(path):
        return None
    hashes = set()
    text = read_file(path, LIST_NAME).decode("utf-8-sig", "replace")
    for number, line in enumerate(text.splitlines(), 1):
        entry = line.strip().lower()
        if not entry or entry.startswith("#"):
            continue
        if len(entry) != 64 or entry.strip("0123456789abcdef"):
            raise CheckError("line %d of %s is not a SHA-256 fingerprint. The list may be "
                             "damaged." % (number, LIST_NAME))
        hashes.add(entry)
    return hashes


def licensed_hashes():
    """The fingerprints of the licensed files, as they are in the site folder."""
    hashes = set()
    for name in LICENSED_FILES:
        path = site_path(name)
        if os.path.isfile(path):
            hashes.add(sha256(read_file(path, name)))
    return hashes


def scan_private_folder():
    """Read the private photo folder. Returns ({fingerprint: where it is},
    {the fingerprints among them that are archives}, [what could not be read])
    for every restricted image in it and for every archive that holds one."""
    licensed = licensed_hashes()
    found = {}
    archives = set()
    unreadable = []

    def record(label, digest):
        if digest not in found or len(label) < len(found[digest]):
            found[digest] = label

    def add_image(label, data):
        """True when the image is restricted, False when it is a licensed one."""
        digest = sha256(data)
        if digest in licensed and photo_name(label) not in RESTRICTED_NAMES:
            return False
        record(label, digest)
        return True

    def add_archive(label, digest):
        record(label, digest)
        archives.add(digest)

    for folder, folders, files in os.walk(PRIVATE_FOLDER):
        folders.sort()
        for name in sorted(files):
            path = os.path.join(folder, name)
            label = os.path.relpath(path, PRIVATE_FOLDER).replace(os.sep, "/")
            try:
                with open(path, "rb") as handle:
                    data = handle.read()
            except OSError:
                unreadable.append(label)
                continue
            if is_image(name, data):
                add_image(label, data)
            archive = open_zip(data)
            if archive is None:
                if name.lower().endswith(".zip"):
                    unreadable.append(label)
                    add_archive(label, sha256(data))     # cannot be looked into: doubt means restricted
                continue
            restricted_members = []
            inner_archives = {}
            closed = False
            for member, member_data in zip_members(archive):
                if member_data is None:
                    unreadable.append(label + " > " + member)
                    closed = True
                elif is_image(member, member_data):
                    if add_image(label + " > " + member, member_data):
                        restricted_members.append(member)
                elif member_data[:2] == b"PK":
                    inner_archives[member] = sha256(member_data)
            # An archive that holds a restricted picture is a restricted file itself.
            if restricted_members or closed:
                add_archive(label, sha256(data))
            for member, digest in inner_archives.items():
                if any(hit.startswith(member + " > ") for hit in restricted_members):
                    add_archive(label + " > " + member, digest)
    return found, archives, unreadable


class Restricted(object):
    """Everything the check compares against."""

    def __init__(self):
        listed = load_list()
        self.list_missing = listed is None
        self.listed = listed or set()
        self.have_folder = os.path.isdir(PRIVATE_FOLDER)
        self.private, self.private_archives, self.unreadable = (
            scan_private_folder() if self.have_folder else ({}, set(), []))
        self.not_on_list = sorted(set(self.private) - self.listed)
        self.total = len(self.listed | set(self.private))
        if not self.total:
            if self.list_missing:
                raise CheckError("%s is missing, so there is nothing to compare the files "
                                 "with. Put the file back." % LIST_NAME)
            raise CheckError("%s holds no fingerprint, so there is nothing to compare the "
                             "files with." % LIST_NAME)

    def __contains__(self, digest):
        return digest in self.listed or digest in self.private

    def explain(self, digest):
        where = self.private.get(digest)
        if where and digest in self.private_archives:
            return ('It has the same content as the photo backup "%s", which holds '
                    "Wix-only photos. The file name does not matter." % where)
        if where and photo_name(where) in RESTRICTED_NAMES:
            return ('It has the same content as the Wix-only photo "%s". '
                    "The file name does not matter." % where)
        if where:
            return ('It has the same content as the restricted file "%s" of the private '
                    "photo folder. The file name does not matter." % where)
        return ("Its content is on the list of files that are kept out of this site, "
                "most of them Wix-only photos (%s). The file name does not matter."
                % LIST_NAME)

    def sources(self):
        parts = []
        if not self.list_missing:
            parts.append(LIST_NAME)
        if self.have_folder:
            parts.append("the private photo folder next to the site folder")
        return " and ".join(parts)


# ---------------------------------------------------------------- which files


def have_git():
    return os.path.exists(os.path.join(SITE, ".git"))


def git(*args, **options):
    data = options.get("data")
    feed = {"input": data} if data is not None else {"stdin": subprocess.DEVNULL}
    try:
        done = subprocess.run(("git",) + args, cwd=SITE, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, **feed)
    except OSError:
        raise CheckError("git could not be started.")
    if done.returncode != 0:
        detail = done.stderr.decode("utf-8", "replace").strip()
        raise CheckError("git %s did not work: %s" % (args[0], detail or "no message"))
    return done.stdout


def decode_path(raw):
    return raw.decode("utf-8", "surrogateescape")


def staged_files():
    """(path, content) for every file in the index, with its staged content."""
    entries = []
    for record in git("ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        meta, _, raw_path = record.partition(b"\t")
        fields = meta.split()
        if len(fields) < 2 or fields[0] == b"160000":    # 160000 is a submodule, not a file
            continue
        entries.append((decode_path(raw_path), fields[1]))
    if not entries:
        return
    out = git("cat-file", "--batch", data=b"".join(oid + b"\n" for _, oid in entries))
    position = 0
    for path, _ in entries:
        try:
            end = out.index(b"\n", position)
            kind, size = out[position:end].split()[1:3]
            size = int(size)
        except ValueError:
            raise CheckError("git could not hand over the staged content of %s." % path)
        if kind != b"blob":
            raise CheckError("git could not hand over the staged content of %s." % path)
        yield path, out[end + 1:end + 1 + size]
        position = end + 1 + size + 1


def staged_states():
    """How the staged files differ from the last commit: {path: "new" or
    "changed"}. A staged path that is not in the answer is the same as in the
    last commit. None when there is no commit yet, or git cannot tell."""
    try:
        out = git("diff-index", "--cached", "--name-status", "--no-renames", "-z", "HEAD")
    except CheckError:
        return None
    fields = out.split(b"\0")
    states = {}
    for status, raw_path in zip(fields[0::2], fields[1::2]):
        states[decode_path(raw_path)] = "new" if status[:1] == b"A" else "changed"
    return states


def hook_file():
    """(the place where git looks for the pre-commit hook of this repository,
    True when that place is the repository's own hooks folder)."""
    folder = os.path.join(SITE, decode_path(git("rev-parse", "--git-path", "hooks")).strip())
    usual = os.path.join(SITE, decode_path(git("rev-parse", "--git-dir")).strip(), "hooks")
    same = os.path.normcase(os.path.abspath(folder)) == os.path.normcase(os.path.abspath(usual))
    return os.path.join(folder, "pre-commit"), same


def hook_state():
    """Is the commit guard switched on in this repository? "on", "off" (git
    finds no pre-commit hook), "other" (it finds one that is not the one in
    tools/hooks), or None when that cannot be told."""
    try:
        target, _ = hook_file()
        wanted = read_file(site_path(HOOK_NAME), HOOK_NAME)
        if not os.path.isfile(target):
            return "off"
        have = read_file(target, "the installed hook")
    except CheckError:
        return None
    same = have.replace(b"\r\n", b"\n") == wanted.replace(b"\r\n", b"\n")
    return "on" if same else "other"


def tracked_files():
    """(path, content) for every file git would track, as it is on disk."""
    seen = set()
    listing = git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    for raw_path in listing.split(b"\0"):
        path = decode_path(raw_path)
        if not path or path in seen:
            continue
        seen.add(path)
        full = site_path(path)
        if os.path.isfile(full):                 # not there: deleted on disk, or a submodule
            yield path, read_file(full, path)


def all_files():
    """(path, content) for every file in the site folder, git's own .git folder aside."""
    for folder, folders, files in os.walk(SITE):
        folders[:] = sorted(name for name in folders if name != ".git")
        for name in sorted(files):
            full = os.path.join(folder, name)
            path = os.path.relpath(full, SITE).replace(os.sep, "/")
            yield path, read_file(full, path)


def _pattern_to_regex(pattern):
    """A .gitignore pattern as the text of a regular expression."""
    out = []
    i = 0
    while i < len(pattern):
        char = pattern[i]
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            out.append(".*")
            i += 2
            continue
        if char == "*":
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        elif char == "[" and pattern.find("]", i + 2) != -1:
            end = pattern.find("]", i + 2)
            body = pattern[i + 1:end].replace("\\", "\\\\")
            if body[0] in "!^":
                body = "^" + body[1:]
            out.append("[" + body + "]")
            i = end
        elif char == "\\" and i + 1 < len(pattern):
            out.append(re.escape(pattern[i + 1]))
            i += 1
        else:
            out.append(re.escape(char))
        i += 1
    return "".join(out)


def ignore_rules():
    """The rules of the .gitignore in the site folder, as (regex, is an
    exception, folders only). Used only before "git init", when git itself
    cannot be asked. It covers the usual forms (name, folder/, *.ext, a/b,
    **, !exception) and only this one .gitignore file."""
    path = os.path.join(SITE, ".gitignore")
    rules = []
    if not os.path.isfile(path):
        return rules
    flags = re.IGNORECASE if os.path.normcase("A") == "a" else 0
    for line in read_file(path, ".gitignore").decode("utf-8-sig", "replace").splitlines():
        pattern = line.rstrip()
        if not pattern or pattern.startswith("#"):
            continue
        exception = pattern.startswith("!")
        if exception:
            pattern = pattern[1:]
        folders_only = pattern.endswith("/")
        pattern = pattern.rstrip("/")
        if not pattern:
            continue
        anywhere = "/" not in pattern        # a bare name matches at every depth
        body = _pattern_to_regex(pattern.lstrip("/"))
        rules.append((re.compile(("^(?:.*/)?" if anywhere else "^") + body + "$", flags),
                      exception, folders_only))
    return rules


def is_ignored(rules, path, is_folder):
    ignored = False
    for regex, exception, folders_only in rules:
        if (is_folder or not folders_only) and regex.match(path):
            ignored = not exception
    return ignored


def files_git_would_track(left_out):
    """(path, content) for every file .gitignore does not exclude, for a folder
    that is not a git repository yet. What was skipped is added to `left_out`."""
    rules = ignore_rules()
    for folder, folders, files in os.walk(SITE):
        base = os.path.relpath(folder, SITE).replace(os.sep, "/")
        prefix = "" if base == "." else base + "/"
        kept = []
        for name in sorted(folders):
            if name == ".git":
                continue
            if is_ignored(rules, prefix + name, True):
                left_out.append(prefix + name + "/")
            else:
                kept.append(name)
        folders[:] = kept
        for name in sorted(files):
            path = prefix + name
            if is_ignored(rules, path, False):
                left_out.append(path)
            else:
                yield path, read_file(os.path.join(folder, name), path)


# ---------------------------------------------------------------- the check


def check(files, restricted):
    """Returns (number of files, [(headline, path, explanation)])."""
    problems = []
    count = 0
    for path, data in files:
        count += 1
        reason = forbidden_path(path)
        if reason:
            problems.append(("NOT ALLOWED", path, reason))
        digest = sha256(data)
        if digest in restricted:
            problems.append(("LICENSING MATCH", path, restricted.explain(digest)))
            continue
        archive = open_zip(data)
        if archive is None:
            continue
        hits = []
        closed = 0
        for member, member_data in zip_members(archive):
            if member_data is None:
                closed += 1
            elif sha256(member_data) in restricted:
                hits.append(member)
        if hits:
            problems.append(("LICENSING MATCH", path,
                             "It is an archive that holds %d restricted picture%s from the "
                             'Wix-only photos, for example "%s".'
                             % (len(hits), "" if len(hits) == 1 else "s", hits[0])))
        elif closed and not reason:
            problems.append(("NOT ALLOWED", path,
                             "It is an archive with files that cannot be opened (a password, "
                             "or damage), so its content cannot be checked."))
    return count, problems


SCOPES = {
    "staged": "the files staged for the next commit",
    "tracked": "every file git would track",
    "all": "every file in the site folder",
}


def notes(restricted, left_out, hook=None):
    lines = []
    if hook == "off":
        lines.append("Note: the commit guard is not switched on in this folder, so a commit "
                     "would not be checked. To switch it on: python tools/licensing_check.py "
                     "--install-hook")
    elif hook == "other":
        lines.append("Note: the commit guard in this folder is not the one in %s (an older "
                     "copy, or another hook). To put the current one in place: python "
                     "tools/licensing_check.py --install-hook" % HOOK_NAME)
    if left_out is not None:
        text = "Note: this folder is not a git repository yet, so .gitignore was read directly."
        if left_out:
            shown = ", ".join(left_out[:6]) + (" and more" if len(left_out) > 6 else "")
            text += (" Left out, as git would leave them out: %s. To check those too: "
                     "python tools/licensing_check.py --all" % shown)
        lines.append(text)
    if restricted.list_missing:
        lines.append("Note: %s is missing. Only the private photo folder was used. "
                     "Put the list back before you commit." % LIST_NAME)
    if restricted.not_on_list:
        lines.append("Note: %d file(s) in the private photo folder are not on %s yet. They "
                     "were checked anyway. To add them: python tools/licensing_check.py "
                     "--write-list" % (len(restricted.not_on_list), LIST_NAME))
    if restricted.unreadable:
        lines.append("Note: %d file(s) in the private photo folder could not be read and were "
                     "not compared, for example %s."
                     % (len(restricted.unreadable), restricted.unreadable[0]))
    return lines


def name_list(paths, limit=4):
    """A few file names for a sentence, with "and N more" when there are many."""
    shown = ", ".join(paths[:limit])
    if len(paths) > limit:
        shown += " and %d more (all listed above)" % (len(paths) - limit)
    return shown


def in_command(paths):
    """The file name as it is typed in a command, in double quotes."""
    if len(paths) == 1 and not set(paths[0]) & set('"$`\\!%^'):
        return '"%s"' % paths[0]
    return '"path/of/the/file"'


def advice_for_commit(problems, states):
    """The "What to do" lines for a commit that was stopped, for GitHub Desktop
    and for the command line. `states` is the answer of staged_states()."""
    paths = []
    for _, path, _ in problems:
        if path not in paths:
            paths.append(path)
    not_allowed = set(path for headline, path, _ in problems if headline == "NOT ALLOWED")
    if states is None:                       # no commit yet: every file is new
        states = dict((path, "new") for path in paths)
    replaced = [p for p in paths if states.get(p) == "changed" and p not in not_allowed]
    new = [p for p in paths if states.get(p) == "new"]
    earlier = [p for p in paths if p not in replaced and p not in new]

    lines = ["What to do:"]
    say = lines.append
    if replaced:
        say("  * Saved over a file of the site: %s" % name_list(replaced))
        say("    Save a photo that you own or have a license for over it, with the same")
        say("    name, in the same folder. Or put the file back as it was:")
        say("        GitHub Desktop:  right-click the file in the Changes list and choose")
        say("                         Discard Changes")
        say("        Command line:    git checkout HEAD -- %s" % in_command(replaced))
    if new:
        say("  * New in this commit: %s" % name_list(new))
        say("    Move the file out of the site folder, to a place that is not inside it.")
        say("    If the site needs a photo with this name, save a photo that you own or")
        say("    have a license for under this name.")
    if earlier:
        say("  * In the repository since an earlier commit: %s" % name_list(earlier))
        say("    Move the file out of the site folder, or save a photo that you own or")
        say("    have a license for over it. The file also stays in the history of the")
        say("    repository, so do not push, and ask for help first.")
    say("  Then commit again. In GitHub Desktop click the Commit button once more. On")
    say('  the command line run "git add -u" first, then "git commit". The check runs')
    say("  by itself.")
    return lines


DO_NOT_SKIP = (
    'Please do not skip this check: no "Bypass Commit Hooks" in GitHub Desktop and no',
    '"git commit --no-verify". If you are not sure about a photo, ask before you',
    "publish it.",
)


def report(count, problems, restricted, scope, left_out, states=None, hook=None):
    """Returns (exit status, the lines to show)."""
    lines = []
    say = lines.append
    files = "1 file" if count == 1 else "%d files" % count
    if not problems:
        say("Photo licensing check passed: %s checked (%s), no Wix-only photo, no zip "
            "file, nothing from a source-photos, new-photos, zip or _tmp folder." % (files, SCOPES[scope]))
        say("Compared with %d fingerprints of restricted files from %s."
            % (restricted.total, restricted.sources()))
        lines.extend(notes(restricted, left_out, hook))
        return 0, lines

    say("PHOTO LICENSING CHECK: STOP")
    say("---------------------------")
    for headline, path, explanation in problems:
        say("%s: %s" % (headline, path))
        say("    " + explanation)
    say("")
    say("%d problem%s found in %s (%s)."
        % (len(problems), "" if len(problems) == 1 else "s", files, SCOPES[scope]))
    if scope == "staged":
        say("The commit was stopped. Nothing was committed.")
    else:
        say("Do not commit, push or publish until this is fixed.")
    say("")
    say("Why: the photos of the old Wix site are licensed for Wix only. Only the salon")
    say("logo and the owner's own photos (g12 and g13) may be published with this site.")
    say("Zip files and the folders source-photos, new-photos, zip and _tmp are kept out")
    say("as well,")
    say("because that is where photo backups are kept.")
    say("")
    if scope == "staged":
        lines.extend(advice_for_commit(problems, states))
    else:
        say("What to do:")
        say("  1. A Wix photo that was saved over a file of the site (a placeholder")
        say("     image): save a photo that you own or have a license for over it, with")
        say("     the same name, in the same folder. In GitHub Desktop you can also put")
        say("     the file back as it was: right-click it in the Changes list and choose")
        say("     Discard Changes.")
        say("  2. Every other file listed above: move it out of the site folder, to a")
        say("     place that is not inside it.")
        say("  3. Run the check again:    python tools/licensing_check.py%s"
            % (" --all" if scope == "all" else ""))
    lines.extend(DO_NOT_SKIP)
    lines.extend(notes(restricted, left_out, hook))
    return 1, lines


# ---------------------------------------------------------------- the list


def write_list():
    """Add every fingerprint of the private folder to tools/restricted-hashes.txt."""
    if not os.path.isdir(PRIVATE_FOLDER):
        raise CheckError('the private photo folder "%s" was not found next to the site '
                         "folder, so the list cannot be rebuilt on this computer. Nothing "
                         "was changed." % PRIVATE_FOLDER_NAME)
    old = load_list() or set()
    private, _, unreadable = scan_private_folder()
    if unreadable:
        raise CheckError("%d file(s) in the private photo folder could not be read, for "
                         "example %s. Nothing was changed." % (len(unreadable), unreadable[0]))
    new = sorted(old | set(private))
    if not new:
        raise CheckError("no restricted picture was found in the private photo folder. "
                         "Nothing was changed.")
    with open(site_path(LIST_NAME), "w", encoding="ascii", newline="\n") as handle:
        handle.write(LIST_HEADER)
        for digest in new:
            handle.write(digest + "\n")
    return 0, ["%s now holds %d fingerprints (%d new, %d kept from before that are no longer "
               "in the private photo folder)."
               % (LIST_NAME, len(new), len(set(private) - old), len(old - set(private)))]


# ---------------------------------------------------------------- the commit guard


def install_hook():
    """Copy tools/hooks/pre-commit to the place where git looks for it.
    Returns (exit status, the lines to show)."""
    if not have_git():
        return 2, ["The commit guard was not switched on: this folder is not a git "
                   'repository yet. Run this again after "git init".']
    try:
        target, usual = hook_file()
        data = read_file(site_path(HOOK_NAME), HOOK_NAME).replace(b"\r\n", b"\n")
        if not usual:
            if hook_state() == "on":
                return 0, ["The commit guard is switched on already."]
            return 2, ["The commit guard was not switched on: git on this computer is set to "
                       "look for hooks in another folder (the setting core.hooksPath), and "
                       "this script does not write there. Nothing was changed."]
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(data)
        try:
            os.chmod(target, 0o755)
        except OSError:
            pass
    except (CheckError, OSError) as error:
        return 2, ["The commit guard was not switched on: %s"
                   % (str(error) or type(error).__name__)]
    return 0, ["The commit guard is switched on: from now on every commit in this folder runs "
               "the photo licensing check first, in GitHub Desktop too."]


# ---------------------------------------------------------------- command line


def emit(lines, stream):
    """Write the lines. When nobody is reading (a closed pipe) the result of
    the check still counts, so a failed write never changes the exit status."""
    try:
        stream.write("\n".join(lines) + "\n")
        stream.flush()
    except (OSError, ValueError):
        try:
            os.dup2(os.open(os.devnull, os.O_WRONLY), stream.fileno())
        except (OSError, ValueError, AttributeError):
            pass


def run(args):
    """Returns (exit status, the lines to show)."""
    if args.write_list:
        return write_list()
    if args.install_hook:
        return install_hook()
    left_out = None                  # a list only when .gitignore is read without git
    if args.staged:
        if not have_git():
            raise CheckError("this folder is not a git repository yet, so nothing is "
                             "staged. To check every file in it use: "
                             "python tools/licensing_check.py --all")
        scope, files = "staged", staged_files()
    elif args.all:
        scope, files = "all", all_files()
    elif have_git():
        scope, files = "tracked", tracked_files()
    else:
        left_out = []
        scope, files = "tracked", files_git_would_track(left_out)
    restricted = Restricted()
    count, problems = check(files, restricted)
    states = staged_states() if scope == "staged" and problems else None
    hook = hook_state() if scope != "staged" and have_git() else None
    return report(count, problems, restricted, scope, left_out, states, hook)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream.isatty():
                stream.reconfigure(errors="backslashreplace")
            else:
                stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError, OSError):
            pass
    parser = argparse.ArgumentParser(
        description="Photo licensing check: stops a commit that holds a Wix-only photo, a "
                    "zip file or anything from a source-photos, new-photos, zip or _tmp folder. With no "
                    "option it checks every file git would track.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true",
                       help="check exactly what the next commit would hold (used by the "
                            "pre-commit hook)")
    group.add_argument("--all", action="store_true",
                       help="check every file in the site folder, ignored files included")
    group.add_argument("--write-list", action="store_true",
                       help="maintenance: add the fingerprints of the private photo folder to "
                            "tools/restricted-hashes.txt")
    group.add_argument("--install-hook", action="store_true",
                       help="switch on the commit guard: copy tools/hooks/pre-commit to the "
                            "place where git looks for it (once after git init, and once "
                            "after every fresh clone)")
    args = parser.parse_args(argv)

    try:
        status, lines = run(args)
    except CheckError as error:
        reason = str(error)
    except Exception as error:           # a fault in the check itself must not look like a pass
        reason = "unexpected error, %s: %s" % (type(error).__name__, error)
    else:
        emit(lines, sys.stdout)
        return status
    emit(["PHOTO LICENSING CHECK: COULD NOT RUN",
          "Reason: " + reason,
          "Nothing was verified, so please treat this as a stop: do not commit or publish "
          "until the check runs and passes."], sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
