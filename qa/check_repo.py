"""Checks of the site folder as a whole: what a commit would carry. No browser, standard library only.

  generator-output      (one entry per page) the page file in the site folder is byte for byte what
                        tools/build_pages.py --out writes today. The generator is run into a scratch folder
                        outside the site folder; nothing in the site folder is written.
  generator-runs        the generator ends without an error, prints no WARNING and wants no change of
                        image-manifest.json
  font-preload          (one entry per page) the head asks for the two font files of the site early: one preload link
                        each for fonts/figtree-latin.woff2 and fonts/bodoni-moda-italic-latin.woff2 (as="font",
                        type="font/woff2", crossorigin), before the stylesheet, and both files exist. No link of the
                        page leads to Google Fonts any more (build contract, section 6 and decision 38)
  fonts-folder          the folder fonts holds exactly the files fonts/fonts.json lists, each font file with the
                        SHA-256 recorded there, and the two license texts
  font-face-rules       css/style.css gives every font file of fonts.json an @font-face rule, and the rules cover
                        Figtree upright 400 and 700 and Bodoni Moda italic 400 and 700 (a rule names one weight or a
                        range), each with font-display: swap and the characters (unicode-range) fonts.json records,
                        names no font file that is not there, and no stylesheet or page asks another server for a font
  line-endings          every text file is UTF-8 without a byte order mark and has LF line endings
  no-absolute-path      no file names a folder of this computer (home folder, the folders next to the site folder,
                        the temporary folder, the Python folder), with either kind of slash
  no-pycache            no __pycache__ folder and no compiled Python file
  no-leftovers          no _tmp, source-photos, new-photos or zip folder, no archive, backup or editor leftover
  readme-short          README.md exists and has fewer than 60 lines
  docs-no-em-dash       README.md, MIGRATION.md, redirects-check.md and qa/REPORT.md hold no em dash
  no-cname              there is no CNAME file yet (the domain is connected later; GitHub adds the file then,
                        and this check has to be turned round on that day)
  git-folder            no repository yet, or one without surprises: a real .git folder in the site folder itself,
                        no other remote than the GitHub repository achooStorm/hairbygerta, the commit guard
                        installed, no repository inside a subfolder, no submodules

Not here because another script has it: .nojekyll exists and is empty (qa/check_html.py, nojekyll-empty).

These checks read the site folder on this computer. --base, --page and --viewport are accepted because every QA
script takes them: --page limits the two per-page checks, the other two options change nothing.

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_repo.py

The report goes to qa/reports/check_repo.json. Exit code 0 when everything passed, 1 otherwise.
For the self-test of this script: --root DIR checks that copy of the site, --out DIR writes the report there.
"""
import html.parser, json, os, re, shutil, subprocess, sys, tempfile, time

sys.dont_write_bytecode = True   # no __pycache__ in the site folder
import common  # noqa: E402

NAME = "check_repo"
SITE_PAGE, VIEWPORT = common.SITE_PAGE, common.NO_VIEWPORT
README_LINES = 60
EM_DASH = "—"
DOCS = ("README.md", "MIGRATION.md", "redirects-check.md", "qa/REPORT.md")
REPOSITORY = "achoostorm/hairbygerta"
SKIP_DIRS = (".git",)                   # never read: the repository itself
PICTURE_DIRS = ("qa/screenshots",)      # pictures of our own pages, ignored by git: not read as text
TEXT_EXT = (".html", ".htm", ".css", ".js", ".cjs", ".mjs", ".json", ".xml", ".txt", ".md", ".py", ".svg", ".yml", ".yaml",
            ".cfg", ".ini", ".toml", ".sh", ".webmanifest", ".csv")
TEXT_NAMES = (".gitignore", ".gitattributes", ".nojekyll", "CNAME", "pre-commit")
LEFTOVER_DIRS = ("_tmp", "source-photos", "new-photos", "zip", "tmp", "temp")
LEFTOVER_EXT = (".zip", ".7z", ".rar", ".tar", ".gz", ".tmp", ".bak", ".orig", ".rej", ".swp", ".log")
LEFTOVER_NAMES = ("thumbs.db", ".ds_store", "desktop.ini")
GENERATOR = "tools/build_pages.py"
GENERATOR_SECONDS = 180


def entry(page, check, ok, expected, actual, evidence, owner, **more):
    e = {"page": page, "viewport": VIEWPORT, "check": check, "ok": bool(ok), "expected": expected,
         "actual": actual, "evidence": evidence, "owner": owner}
    e.update(more)
    return e


def short(text, limit=200):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def plural(n, word, many=None):
    return "%d %s" % (n, word if n == 1 else (many or word + "s"))


def page_file(slug):
    address = common.PAGES[slug]
    return address if address.endswith(".html") else address + "index.html"


def owner_of(rel):
    """Who owns this file (build contract, section 1). A compiled file belongs to whoever owns its source."""
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    name = parts[-1]
    if "__pycache__" in parts or name.endswith((".pyc", ".pyo")):
        source = name.split(".")[0] + ".py"
        return owner_of("/".join([p for p in parts[:-1] if p != "__pycache__"] + [source]))
    if parts[0] == "qa":
        return "QA"
    if parts[0] in ("images", "fonts") or rel in ("favicon.ico", "image-manifest.json", "tools/make_placeholders.py", "tools/make_icons.py",
                                                  "tools/make_fonts.py", "tools/make_share_image.py", "tools/add_photo.py"):
        return "ASSETS"
    if parts[0] == "content":
        return "CONTENT"
    if parts[0] == "css":
        return "DESIGN"
    if parts[0] == "js":
        return "INTERACTION"
    if parts[0] == "seo" or rel in ("sitemap.xml", "robots.txt", ".nojekyll", "redirects-check.md"):
        return "SEO"
    if rel in ("MIGRATION.md", "README.md"):
        return "RUNBOOK"
    if parts[0] == ".git" or rel in (".gitignore", ".gitattributes", "CNAME", "tools/licensing_check.py", "tools/restricted-hashes.txt") or rel.startswith("tools/hooks/"):
        return "DEPLOY"
    if name == "index.html" or rel == "404.html" or rel == GENERATOR or rel.startswith("tools/pages/"):
        return "PAGES"
    return "QA"         # a file the contract does not name (tools/CONTRACT.md is kept by the director)


def walk(site):
    """-> (files, folders) as paths relative to the site folder with forward slashes. The .git folder is left out."""
    files, folders = [], []
    for here, dirs, names in os.walk(site):
        rel_here = os.path.relpath(here, site).replace(os.sep, "/")
        rel_here = "" if rel_here == "." else rel_here + "/"
        dirs[:] = sorted(d for d in dirs if (rel_here + d) not in SKIP_DIRS)
        folders += [rel_here + d for d in dirs]
        files += [rel_here + n for n in sorted(names)]
    return files, folders


def is_picture_evidence(rel):
    return any(rel.startswith(d + "/") for d in PICTURE_DIRS)


def read(site, rel):
    try:
        with open(os.path.join(site, *rel.split("/")), "rb") as f:
            return f.read()
    except OSError:
        return None


def is_text(rel, data):
    name = rel.split("/")[-1]
    if name in TEXT_NAMES or name.lower().endswith(TEXT_EXT) or rel.startswith("tools/hooks/"):
        return True
    if "." in name or b"\0" in data[:8192]:
        return False
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def grouped(check, expected, problems, checked, evidence):
    """problems: [(rel, what)]. One entry when all is well, else one entry per owner, so each owner sees only their files."""
    if not problems:
        return [entry(SITE_PAGE, check, True, expected, "%s checked, none wrong" % checked, evidence, "QA")]
    out = []
    for owner in sorted({owner_of(rel) for rel, _ in problems}):
        mine = [(rel, what) for rel, what in problems if owner_of(rel) == owner]
        out.append(entry(SITE_PAGE, "%s (%s files)" % (check, owner), False, expected,
                         "%s: %s" % (plural(len(mine), "file"), "; ".join("%s (%s)" % m for m in mine[:8]) + (" and %d more" % (len(mine) - 8) if len(mine) > 8 else "")),
                         evidence, owner, files=[rel for rel, _ in mine]))
    return out


# ---------------------------------------------------------------- the generator

def run_generator(site, env_dir):
    """Run tools/build_pages.py --out into a scratch folder outside the site folder. -> (folder or None, problem, output)"""
    script = os.path.join(site, *GENERATOR.split("/"))
    if not os.path.isfile(script):
        return None, GENERATOR + " is missing", ""
    scratch = os.path.join(env_dir, "stage", "qa", NAME)
    try:
        os.makedirs(scratch, exist_ok=True)
        out = tempfile.mkdtemp(prefix="run-", dir=scratch)
    except OSError:
        out = tempfile.mkdtemp(prefix="hbg-" + NAME + "-")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    try:
        done = subprocess.run([sys.executable, "-B", script, "--out", out], cwd=out, env=env, capture_output=True, timeout=GENERATOR_SECONDS)
    except subprocess.TimeoutExpired:
        return out, "the generator did not finish in %d seconds" % GENERATOR_SECONDS, ""
    except OSError as e:
        return out, "the generator could not be started (%s)" % type(e).__name__, ""
    text = (done.stdout or b"").decode("utf-8", "replace") + (done.stderr or b"").decode("utf-8", "replace")
    return out, ("" if done.returncode == 0 else "the generator ended with exit code %s" % done.returncode), text


def scrub(text, *folders):
    for folder in folders:
        if folder:
            for form in {folder, folder.replace("\\", "/"), folder.replace("/", "\\")}:
                text = text.replace(form, "<folder>")
    return text


def first_difference(a, b):
    la, lb = a.split(b"\n"), b.split(b"\n")
    for n, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            return "line %d: the site folder has %s, the generator writes %s" % (n, json.dumps(short(x.decode("utf-8", "replace"), 90), ensure_ascii=False),
                                                                             json.dumps(short(y.decode("utf-8", "replace"), 90), ensure_ascii=False))
    return "the first %d lines are the same, then one of the two goes on (%d and %d lines)" % (min(len(la), len(lb)), len(la), len(lb))


def check_generator(site, env_dir, slugs):
    out, problem, text = run_generator(site, env_dir)
    results = []
    try:
        shown = short(scrub(text, out or "", site, env_dir, os.path.dirname(site)), 500)
        warnings = [short(scrub(line, out or "", site, env_dir, os.path.dirname(site)), 240) for line in text.splitlines() if "WARNING" in line.upper()]
        manifest_new = read(out, "image-manifest.json") if out else None
        manifest_changed = manifest_new is not None and manifest_new != read(site, "image-manifest.json")
        notes = []
        if problem:
            notes.append(problem + (": " + shown if shown else ""))
        if warnings:
            notes.append("%s: %s" % (plural(len(warnings), "WARNING"), " | ".join(warnings[:4])))
        if manifest_changed:
            notes.append("the generator wants to change image-manifest.json (a replaced photo is not recorded yet): run it once without --out")
        results.append(entry(SITE_PAGE, "generator-runs", not notes, "python %s --out <scratch folder> ends with exit code 0, prints no WARNING and leaves image-manifest.json as it is" % GENERATOR,
                             "; ".join(notes) if notes else "exit code 0, no warning, manifest unchanged", GENERATOR + ", run into a scratch folder outside the site folder", "PAGES"))
        for slug in slugs:
            rel = page_file(slug)
            expected = "%s is byte for byte what the generator writes (HTML is never edited by hand, build contract section 1)" % rel
            ours, fresh = read(site, rel), (read(out, rel) if out and not problem else None)
            if fresh is None:
                results.append(entry(slug, "generator-output", False, expected, "not compared: " + (problem or "the generator did not write %s" % rel), rel, "PAGES"))
            elif ours is None:
                results.append(entry(slug, "generator-output", False, expected, "%s is missing in the site folder" % rel, rel, "PAGES"))
            else:
                same = ours == fresh
                results.append(entry(slug, "generator-output", same, expected,
                                     "identical (%d bytes)" % len(ours) if same else "differs: " + first_difference(ours, fresh),
                                     rel + ("" if same else ". Either the page was edited by hand, or a content file, a page module or the generator changed and the pages were not built again"), "PAGES"))
    finally:
        if out:
            shutil.rmtree(out, ignore_errors=True)
    return results


# ---------------------------------------------------------------- fonts: the links of a page, the folder, the rules

# Since 9 November 2026 the fonts are files of the site itself (build contract, decision 38). Until then every page
# linked a Google Fonts stylesheet behind two preconnect links, and this script checked those.
FONT_LIST = "fonts/fonts.json"
FONT_PRELOADS = ("fonts/figtree-latin.woff2", "fonts/bodoni-moda-italic-latin.woff2")     # the two files an English page needs
FONT_SERVERS = ("fonts.googleapis.com", "fonts.gstatic.com")                                # no page and no stylesheet may ask them
FONT_FACES = (("Figtree", "normal", 400), ("Figtree", "normal", 700), ("Bodoni Moda", "italic", 400), ("Bodoni Moda", "italic", 700))
STYLESHEET = "css/style.css"


class Head(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.in_head = [], False

    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        elif tag == "link" and self.in_head:
            self.links.append(dict((k.lower(), v or "") for k, v in attrs))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


def check_font_preload(site, slug):
    rel = page_file(slug)
    expected = ('in the head, before the stylesheet: <link rel="preload" href=".../%s" as="font" type="font/woff2" crossorigin> and the same '
                'for %s; both files exist; no link to Google Fonts' % FONT_PRELOADS)
    data = read(site, rel)
    if data is None:
        return entry(slug, "font-preload", False, expected, rel + " is missing", rel, "PAGES")
    text = data.decode("utf-8", "replace")
    head = Head()
    head.feed(text)
    rels = lambda l: l.get("rel", "").lower().split()
    up = "../" * rel.count("/")                 # from the page to the top of the site
    sheet = next((i for i, l in enumerate(head.links) if "stylesheet" in rels(l)), None)
    problems = []
    for font in FONT_PRELOADS:
        at = next((i for i, l in enumerate(head.links) if "preload" in rels(l) and l.get("href", "") == up + font), None)
        if at is None:
            problems.append("no preload link for %s" % font)
            continue
        link = head.links[at]
        if link.get("as", "").lower() != "font":
            problems.append('the preload link for %s has no as="font"' % font)
        if link.get("type", "").lower() != "font/woff2":
            problems.append('the preload link for %s has no type="font/woff2"' % font)
        if "crossorigin" not in link:
            problems.append("the preload link for %s has no crossorigin attribute (the browser would fetch the file twice)" % font)
        if sheet is not None and at > sheet:
            problems.append("the preload link for %s stands after the stylesheet, where it no longer helps" % font)
        if not os.path.isfile(os.path.join(site, *font.split("/"))):
            problems.append("%s is not in the site folder" % font)
    if sheet is None:
        problems.append("no stylesheet link")
    low = text.lower()
    problems += ["the page still names %s" % host for host in FONT_SERVERS if host in low]
    return entry(slug, "font-preload", not problems, expected, "; ".join(problems) if problems else "both there, before the stylesheet", rel, "PAGES")


def read_font_list(site):
    """fonts/fonts.json -> (document, problem text)."""
    raw = read(site, FONT_LIST)
    if raw is None:
        return None, "%s is missing" % FONT_LIST
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception as e:
        return None, "%s is not valid JSON (%s)" % (FONT_LIST, short(e, 80))
    if not isinstance(doc, dict) or not isinstance(doc.get("fonts"), list) or not doc["fonts"]:
        return None, "%s lists no fonts" % FONT_LIST
    return doc, None


def check_fonts_folder(site):
    """The folder fonts against fonts/fonts.json (the same comparison tools/make_fonts.py --check makes)."""
    expected = ("fonts/ holds exactly the files %s lists: each font file is WOFF2 and has the SHA-256 recorded there, "
                "and the license text of each font is there" % FONT_LIST)
    doc, problem = read_font_list(site)
    if problem:
        return entry(SITE_PAGE, "fonts-folder", False, expected, problem, FONT_LIST, "ASSETS")
    import hashlib
    problems, listed = [], {FONT_LIST}
    for record in doc["fonts"]:
        rel = record.get("file") if isinstance(record, dict) else None
        if not isinstance(rel, str) or not rel.startswith("fonts/") or ".." in rel:
            problems.append("an entry names no file inside fonts/")
            continue
        listed.add(rel)
        data = read(site, rel)
        if data is None:
            problems.append("%s is listed but is not there" % rel)
        elif hashlib.sha256(data).hexdigest() != str(record.get("sha256", "")).lower():
            problems.append("%s is not the file the list describes (other SHA-256): run tools/make_fonts.py again, or put the file back" % rel)
        elif data[:4] != b"wOF2":
            problems.append("%s is not a WOFF2 file" % rel)
    licenses = [l for l in doc.get("license_files") or [] if isinstance(l, str)]
    if not licenses:
        problems.append("%s names no license text" % FONT_LIST)
    for rel in licenses:
        listed.add(rel)
        data = read(site, rel)
        if data is None:
            problems.append("the license text %s is not there" % rel)
        elif b"SIL OPEN FONT LICENSE" not in data.upper():
            problems.append("%s is not the text of the SIL Open Font License" % rel)
    folder = os.path.join(site, "fonts")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if "fonts/" + name not in listed:
            problems.append("fonts/%s is in the folder but not in the list" % name)
    return entry(SITE_PAGE, "fonts-folder", not problems, expected,
                 "; ".join(problems) if problems else "%s and %s, all as listed" % (plural(len(doc["fonts"]), "font file"), plural(len(licenses), "license text")),
                 "fonts/, %s" % FONT_LIST, "ASSETS")


_FACE = re.compile(r"@font-face\s*\{([^}]*)\}", re.S)
_DECL = re.compile(r"([a-z-]+)\s*:\s*([^;]+);")
_URL = re.compile(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)")
_COMMENT = re.compile(r"/\*.*?\*/", re.S)


def font_ranges(text):
    """A unicode-range value as a set of its parts, so spaces and line breaks do not count."""
    return {part.strip().upper() for part in str(text).split(",") if part.strip()}


def check_font_faces(site):
    """The @font-face rules of the stylesheet against fonts/fonts.json."""
    expected = ("%s has an @font-face rule for every font file, and the rules cover %s; each has font-display: swap, a file of fonts/ that %s lists and "
                "the unicode-range recorded there; nothing asks another server for a font"
                % (STYLESHEET, ", ".join("%s %s %d" % f for f in FONT_FACES), FONT_LIST))
    doc, problem = read_font_list(site)
    raw = read(site, STYLESHEET)
    if problem or raw is None:
        return entry(SITE_PAGE, "font-face-rules", False, expected, problem or STYLESHEET + " is missing", STYLESHEET, "DESIGN")
    css = _COMMENT.sub("", raw.decode("utf-8", "replace"))
    records = {r["file"]: r for r in doc["fonts"] if isinstance(r, dict) and isinstance(r.get("file"), str)}
    problems, seen, used = [], set(), set()
    for body in _FACE.findall(css):
        decl = {name.lower(): value.strip() for name, value in _DECL.findall(body)}
        family = decl.get("font-family", "").strip("\"' ")
        style = decl.get("font-style", "normal").lower()
        weight = decl.get("font-weight", "400")
        what = "the rule %s %s %s" % (family, style, weight)
        urls = _URL.findall(decl.get("src", ""))
        if len(urls) != 1:
            problems.append("%s names %d files, expected one" % (what, len(urls)))
            continue
        if re.match(r"(?:[a-z][a-z0-9+.-]*:)?//", urls[0], re.I):
            problems.append("%s fetches its font from another server (%s)" % (what, short(urls[0], 80)))
            continue
        rel = os.path.normpath(os.path.join(os.path.dirname(STYLESHEET), urls[0])).replace(os.sep, "/")
        record = records.get(rel)
        if record is None:
            problems.append("%s names %s, which %s does not list" % (what, rel, FONT_LIST))
            continue
        used.add(rel)
        if decl.get("font-display", "").lower() != "swap":
            problems.append("%s (%s) has no font-display: swap" % (what, rel))
        if (family, style) != (record.get("family"), record.get("style")):
            problems.append("%s names %s, which is %s %s" % (what, rel, record.get("family"), record.get("style")))
        if font_ranges(decl.get("unicode-range", "")) != font_ranges(record.get("unicode_range", "")):
            problems.append("%s (%s): the unicode-range is not the one %s records" % (what, rel, FONT_LIST))
        marks = [int(x) for x in weight.split() if x.isdigit()]          # one weight ("400") or a range ("400 700")
        if record.get("characters") == "latin" and marks:
            seen.update((family, style, w) for _f, _s, w in FONT_FACES if min(marks) <= w <= max(marks))
    problems += ["no @font-face rule for %s %s %d with the latin file" % face for face in FONT_FACES if face not in seen]
    problems += ["%s is listed in %s but no @font-face rule uses it" % (rel, FONT_LIST) for rel in sorted(set(records) - used)]
    if re.search(r"@import", css, re.I):
        problems.append("the stylesheet imports another stylesheet")
    problems += ["the stylesheet names %s" % host for host in FONT_SERVERS if host in css.lower()]
    return entry(SITE_PAGE, "font-face-rules", not problems, expected,
                 "; ".join(problems) if problems else "%s, all in order" % plural(len(_FACE.findall(css)), "rule"), STYLESHEET, "DESIGN")


# ---------------------------------------------------------------- the folder

def computer_paths(site, env_dir):
    """The folders of this computer that must not be named in any file, lower case with forward slashes."""
    found = set()
    for path in (os.path.expanduser("~"), os.environ.get("USERPROFILE"), os.environ.get("HOME"), os.path.dirname(common.SITE), common.SITE,
                 os.path.dirname(site), env_dir, common.RESTRICTED, tempfile.gettempdir(), sys.prefix, sys.base_prefix):
        if not path:
            continue
        for form in (path, os.path.abspath(path), os.path.realpath(path)):
            clean = re.sub(r"/+", "/", form.replace("\\", "/")).rstrip("/").lower()
            if len(clean) > 3 and clean.count("/") >= 2:        # never a bare drive or a top folder such as /usr
                found.add(clean)
                if re.match(r"/[a-z]/", clean):                  # /c/Users/name, the spelling of Git Bash
                    found.add(clean[1] + ":" + clean[2:])
                elif re.match(r"[a-z]:/", clean):
                    found.add("/" + clean[0] + clean[2:])
    # A parent of another entry adds nothing; the shortest ones are enough and are faster to look for.
    return sorted(p for p in found if not any(p != q and p.startswith(q + "/") for q in found))


def check_folder(site, env_dir):
    files, folders = walk(site)
    results = []
    roots = computer_paths(site, env_dir)
    endings, paths, n_text, n_read = [], [], 0, 0
    for rel in files:
        if is_picture_evidence(rel) or rel.endswith(".part"):      # .part: a report another QA script is writing this second
            continue
        data = read(site, rel)
        if data is None:
            continue
        n_read += 1
        # folders of this computer, in any file. Slashes are made the same first: a\\b in JSON, a\b, a/b.
        flat = re.sub(rb"[\\/]+", b"/", data).lower()
        hit = next((r for r in roots if r.encode("utf-8", "replace") in flat), None)
        if hit:
            line = flat[:flat.find(hit.encode("utf-8", "replace"))].count(b"\n") + 1
            paths.append((rel, "line %d names the folder %s" % (line, "/".join(hit.split("/")[:2]) + "/...")))
        if is_text(rel, data):
            n_text += 1
            wrong = []
            if data.startswith(b"\xef\xbb\xbf"):
                wrong.append("starts with a byte order mark")
            if b"\r" in data:
                wrong.append("%s with a carriage return, first on line %d" % (plural(data.count(b"\r"), "line ending"), data[:data.find(b"\r")].count(b"\n") + 1))
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as e:
                wrong.append("not UTF-8 (byte %d)" % e.start)
            if wrong:
                endings.append((rel, ", ".join(wrong)))
    results += grouped("line-endings", "every text file is UTF-8 without a byte order mark and ends its lines with LF alone", endings, plural(n_text, "text file"),
                       "every file with a text extension (pages, stylesheet, script, JSON, XML, Markdown, Python, the hook), .git and qa/screenshots left out")
    results += grouped("no-absolute-path", "no file names a folder of this computer", paths, plural(n_read, "file"),
                       "looked for: the home folder, the folder the site folder is in, the tools folder, the temporary folder and the Python folder, with / or \\ and in any capitals; .git and qa/screenshots left out")

    compiled = [(f, "a __pycache__ folder") for f in folders if f.split("/")[-1] == "__pycache__"]
    inside = tuple(f + "/" for f, _ in compiled)
    compiled += [(f, "a compiled Python file") for f in files if f.endswith((".pyc", ".pyo")) and not f.startswith(inside)]
    named = []
    for f, what in compiled:        # name one file of a folder, so the owner of its source is found
        first = next((x for x in files if x.startswith(f + "/")), f) if what.startswith("a __pycache__") else f
        named.append((first, what if first == f else "in " + what))
    results += grouped("no-pycache", "no __pycache__ folder and no .pyc file (run Python with -B, or set sys.dont_write_bytecode in the script)", named,
                       plural(len(folders), "folder"), "a compiled file carries the path of this computer; whoever ran the named script left it")

    left = [(f, "a folder for temporary files or photo sources") for f in folders if f.split("/")[-1].lower() in LEFTOVER_DIRS]
    left += [(f, "an archive, a backup or a leftover of a program") for f in files
             if f.split("/")[-1].lower().endswith(LEFTOVER_EXT) or f.split("/")[-1].lower() in LEFTOVER_NAMES or f.split("/")[-1].startswith("~$")]
    results += grouped("no-leftovers", "nothing temporary lives in the site folder (decision 20): no _tmp, source-photos, new-photos or zip folder, no archive, backup or editor leftover",
                       left, "%s and %s" % (plural(len(files), "file"), plural(len(folders), "folder")), "names only; what is inside a picture is the job of qa/licensing_check.py")

    readme = read(site, "README.md")
    lines = None if readme is None else len(readme.decode("utf-8", "replace").splitlines())
    results.append(entry(SITE_PAGE, "readme-short", lines is not None and 0 < lines < README_LINES, "README.md exists and has fewer than %d lines" % README_LINES,
                         "README.md is missing" if lines is None else plural(lines, "line"), "README.md", "RUNBOOK"))

    dashes, there = [], 0
    for rel in DOCS:
        data = read(site, rel)
        if data is None:
            continue
        there += 1
        text = data.decode("utf-8", "replace")
        if EM_DASH in text:
            at = [n for n, line in enumerate(text.splitlines(), 1) if EM_DASH in line]
            dashes.append((rel, "%s, first on line %d" % (plural(text.count(EM_DASH), "em dash", "em dashes"), at[0])))
    results += grouped("docs-no-em-dash", "no em dash in %s" % ", ".join(DOCS), dashes, plural(there, "document"), "the character U+2014")

    cname = [f for f in files if "/" not in f and f.lower() == "cname"]
    results.append(entry(SITE_PAGE, "no-cname", not cname, "no CNAME file yet: the domain is not connected in this stage",
                         "there is a CNAME file" + (" (it says %s)" % short((read(site, cname[0]) or b"").decode("utf-8", "replace"), 60) if cname else "") if cname else "no CNAME file",
                         "GitHub adds the file when the custom domain is set (MIGRATION.md). From that day on this check has to expect it, with www.hairbygerta.com in it", "DEPLOY"))
    results.append(check_git(site, files))
    return results


def check_git(site, files):
    expected = ("no repository yet, or one without surprises: a .git folder of the site folder itself, no remote but github.com/achooStorm/hairbygerta, "
                "the commit guard installed (.git/hooks/pre-commit), no repository inside a subfolder, no submodules")
    evidence = "read from the files in .git, git itself is not run"
    git = os.path.join(site, ".git")
    surprises = ["%s: a second repository inside the site folder" % f for f in files if f.endswith("/.git")]      # a .git file in a subfolder
    for here, dirs, _ in os.walk(site):
        if here != site and ".git" in dirs:
            surprises.append("%s/.git: a second repository inside the site folder" % os.path.relpath(here, site).replace(os.sep, "/"))
        dirs[:] = [d for d in dirs if d != ".git"]
    if ".gitmodules" in files:
        surprises.append(".gitmodules: the site has no submodules")
    if not os.path.lexists(git):
        actual = "no repository yet (no .git folder)"
    elif not os.path.isdir(git):
        surprises.append(".git is a file, not a folder: the repository lives somewhere else")
        actual = ""
    else:
        try:
            with open(os.path.join(git, "config"), encoding="utf-8", errors="replace") as f:
                config = f.read()
        except OSError:
            config = None
            surprises.append(".git has no config file: not a complete repository")
        remotes = re.findall(r"^\s*(?:push)?url\s*=\s*(\S+)", config or "", re.M | re.I)
        for url in remotes:
            flat = re.sub(r"\.git$", "", url.lower().rstrip("/"))
            if not re.search(r"github\.com[:/]" + re.escape(REPOSITORY) + "$", flat):
                surprises.append("remote %s is not the repository of this site" % re.sub(r"//[^/@]*@", "//<name>@", url))
            if re.search(r"//[^/@\s]+:[^/@\s]+@", url):
                surprises.append("a remote address carries a password or token")
        if not os.path.isfile(os.path.join(git, "hooks", "pre-commit")):
            surprises.append("the commit guard is not installed: run python tools/licensing_check.py --install-hook (decision 30)")
        actual = "a repository with %s and the commit guard installed" % (plural(len(remotes), "remote") if remotes else "no remote yet")
    return entry(SITE_PAGE, "git-folder", not surprises, expected, "; ".join(surprises) if surprises else actual, evidence, "DEPLOY")


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = common.cli_parser(
        "Checks of the site folder as a whole: generator output, line endings, paths of this computer, leftovers, README, CNAME, .git. No browser.",
        base_help="accepted because every QA script takes it; these checks always read the site folder on this computer",
        page_help="SLUG[,SLUG] or all (default). Limits the per-page checks; the folder checks run every time.",
        viewport_help="accepted because every QA script takes it; not used, this script needs no browser")
    ap.add_argument("--root", help="self-test only: check this copy of the site instead of the site folder")
    ap.add_argument("--out", help="self-test only: write the report into this folder")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    slugs = common.cli_pages(ap, args.page)
    site = os.path.abspath(args.root) if args.root else common.SITE
    started = time.time()
    results = []
    for step in (lambda: check_generator(site, common.ENV, slugs), lambda: [check_font_preload(site, s) for s in slugs], lambda: [check_fonts_folder(site), check_font_faces(site)],
                 lambda: check_folder(site, common.ENV)):
        try:
            results += step()
        except Exception as e:      # a check that breaks is a failed check of this script, never a crash without a report
            import traceback
            last = traceback.extract_tb(sys.exc_info()[2])[-1]
            results.append(entry(SITE_PAGE, "check ran (%s line %d)" % (last.name, last.lineno), False, "the check runs to its end",
                                 "%s: %s" % (type(e).__name__, short(scrub(str(e), site, common.ENV, os.path.dirname(site)), 200)), "qa/%s.py" % NAME, "QA"))
    failed = [r for r in results if not r["ok"]]
    extra = {"script": "qa/%s.py" % NAME, "last_run": {"pages": slugs, "checks": len(results), "failed": len(failed), "seconds": round(time.time() - started, 1)},
             "note": "These checks read the site folder on this computer, whatever --base says."}
    if args.out:
        common.REPORTS = os.path.abspath(args.out)
    common.save_report(NAME, results, common.LOCAL_BASE, extra, replace=set(slugs) | {SITE_PAGE})
    for r in failed:
        print("FAIL [%s] %s | %s | expected: %s | actual: %s" % (r["owner"], r["page"], r["check"], short(r["expected"], 140), short(r["actual"], 300)))
    owners = {}
    for r in failed:
        owners[r["owner"]] = owners.get(r["owner"], 0) + 1
    print("%s: %d checks, %d failed%s. Report: qa/reports/%s.json" % (NAME, len(results), len(failed),
                                                                    (" (%s)" % ", ".join("%s %d" % kv for kv in sorted(owners.items()))) if owners else "", NAME))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
