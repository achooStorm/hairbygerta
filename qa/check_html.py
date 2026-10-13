"""Validate the built HTML, the stylesheet and the small site files. No browser needed.

What it checks
  every page   the vnu validator (the same checker as validator.w3.org/nu) on index.html, the page folders and 404.html.
               One entry per validator message: an error is a failure, a warning or note is listed with ok true.
               The home page embeds seo/jsonld-home.json exactly once, every other page has no JSON-LD script.
               The business facts in seo/jsonld-home.json are the facts of the brief (entry jsonld-facts): business
               name, phone, email, address of the site, street address, opening days and hours, Facebook and
               Instagram. No other QA script reads them: the content check does not look into scripts.
  site files   css/style.css through the vnu CSS checker (--css)
               sitemap.xml is well formed and lists exactly the nine www.hairbygerta.com page addresses
               robots.txt allows everything and names the sitemap
               .nojekyll is empty
               seo/jsonld-home.json, every content/*.json and image-manifest.json parse as strict UTF-8 JSON
               js/site.js passes node --check and its first statement is one of the two forms the build contract
               allows (decision 19):  var BOOKING_URL = "";  (no booking link yet, Book Now calls the phone) or
               var BOOKING_URL = "https://...";  (the owner's booking link). The report says which one was found.

Without --base the files are read straight from the site folder. With --base the pages and files are
fetched from that address and what the server returns is validated.

Run it with the Python from the tools folder (it also needs java and node on the PATH):

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_html.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_html.py --page home,gallery
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_html.py --base https://achoostorm.github.io/hairbygerta/

Results go to qa/reports/check_html.json. Exit code 0 when everything passed, 1 otherwise.
Entries for the whole site (stylesheet, sitemap, robots, JSON files, script) have page "site".
Every entry has viewport "-" because nothing here depends on a screen size.
"""
import concurrent.futures, glob, html.parser, json, os, re, shutil, subprocess, sys, tempfile
import urllib.error, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True      # no __pycache__ in the site folder: compiled files carry paths from this computer
import common

NAME = "check_html"
SITE_PAGE = common.SITE_PAGE        # value of "page" for checks that belong to the whole site
VIEWPORT = common.NO_VIEWPORT       # no browser, no viewport
CANON = "https://www.hairbygerta.com/"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
SITEMAP_URLS = [CANON + common.PAGES[s] for s in common.PAGES if s != "404"]
SITEMAP_ADDRESS = CANON + "sitemap.xml"
# The first statement of js/site.js, build contract section 8 and decision 19. Two forms are valid:
BOOKING_STATEMENT = 'var BOOKING_URL = "";'                     # empty: no booking link yet
BOOKING_FILLED = re.compile(r'var BOOKING_URL = "(.*)";')       # filled: the owner's link, which starts with https://
BOOKING_EXPECTED = 'var BOOKING_URL = "";  or  var BOOKING_URL = "https://...";'
CSS_FILE = "css/style.css"
JS_FILE = "js/site.js"
JSONLD_FILE = "seo/jsonld-home.json"
# FACTS of the brief, as structured data states them. Never paraphrase.
JSONLD_FACTS = {"name": "Hair & Makeup by Gerta", "telephone": common.PHONE, "email": common.EMAIL, "url": CANON}
JSONLD_ADDRESS = {"streetAddress": "644 Forest Ave", "addressLocality": "Staten Island", "addressRegion": "NY", "postalCode": "10310"}
JSONLD_DAYS = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
JSONLD_OPENS, JSONLD_CLOSES = "09:00", "17:00"
JSONLD_SAME_AS = ["https://www.facebook.com/profile.php?id=61588784402912", "https://www.instagram.com/hairbygerta/"]
MANIFEST_FILE = "image-manifest.json"
# The content files the build contract names. Any other content/*.json found in the site folder is checked too.
CONTRACT_CONTENT = ["content/site.json"] + ["content/%s.json" % s for s in common.PAGES]
USER_AGENT = "hairbygerta-qa/check_html"
OWN_MARK = b"hairbygerta.com"   # every page of this site carries it (canonical link, mail link)


# ---------------------------------------------------------------- where the bytes come from

class Got:
    """One file as read from disk or as answered by the server."""
    def __init__(self, status, body=b"", note="", where=""):
        self.status, self.body, self.note, self.where = status, body or b"", note, where

    @property
    def ok(self):
        return self.status == 200

    def problem(self):
        if self.note:
            return "%s: %s" % (self.where, self.note)
        return "%s answered with status %s" % (self.where, self.status)


class LocalSource:
    remote = False
    label = common.LOCAL_BASE

    def __init__(self, root):
        self.root = root

    def get(self, rel, address=None):
        try:
            with open(os.path.join(self.root, *rel.split("/")), "rb") as f:
                return Got(200, f.read(), "", rel)
        except FileNotFoundError:
            return Got(404, b"", "the file is missing", rel)
        except OSError as e:      # no str(e) here: it would carry a path from this computer into the report
            return Got(None, b"", "the file could not be read (%s)" % (e.strerror or type(e).__name__), rel)


class RemoteSource:
    remote = True

    def __init__(self, base):
        self.base = base if base.endswith("/") else base + "/"
        self.label = self.base
        host = urllib.parse.urlsplit(self.base).hostname or ""
        handlers = [urllib.request.ProxyHandler({})] if host in ("127.0.0.1", "localhost", "::1") else []
        self.opener = urllib.request.build_opener(*handlers)

    def get(self, rel, address=None):
        url = self.base + (rel if address is None else address)
        note = ""
        for _ in range(2):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
                with self.opener.open(req, timeout=30) as r:
                    return Got(r.status, r.read(), "", url)
            except urllib.error.HTTPError as e:
                return Got(e.code, e.read(), "", url)
            except Exception as e:
                note = "no answer (%s: %s)" % (type(e).__name__, e)
        return Got(None, b"", note, url)


def page_file(slug):
    address = common.PAGES[slug]
    return address + "index.html" if address == "" or address.endswith("/") else address


# ---------------------------------------------------------------- small helpers

def entry(page, check, ok, expected, actual, evidence, owner, **more):
    e = {"page": page, "viewport": VIEWPORT, "check": check, "ok": bool(ok), "expected": expected,
         "actual": actual, "evidence": evidence, "owner": owner}
    e.update(more)
    return e


def short(value, limit=160):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


def plural(n, word):
    return "%d %s%s" % (n, word, "" if n == 1 else "s")


def load_json_text(text):
    """Strict JSON: no byte order mark, no NaN or Infinity, no key written twice in one object. -> (value, problem)"""
    if text.startswith("\ufeff"):
        return None, "starts with a byte order mark, which a JSON file must not have"

    def constant(name):
        raise ValueError("%s is not valid JSON" % name)

    def pairs(items):
        seen, twice = set(), []
        for key, _ in items:
            if key in seen and key not in twice:
                twice.append(key)
            seen.add(key)
        if twice:
            raise ValueError("the key %s is written more than once in the same object" % ", ".join('"%s"' % k for k in twice))
        return dict(items)
    try:
        return json.loads(text, parse_constant=constant, object_pairs_hook=pairs), None
    except ValueError as e:
        return None, "does not parse: %s" % e


def load_json_bytes(body):
    try:
        text = body.decode("utf-8")
    except UnicodeDecodeError as e:
        return None, "is not UTF-8 (byte %d)" % e.start
    return load_json_text(text)


def json_diff(wanted, found, path=""):
    """Differences between the JSON-LD file (wanted) and what the page embeds (found), as short sentences."""
    if isinstance(wanted, dict) and isinstance(found, dict):
        out = []
        for key in sorted(set(wanted) | set(found)):
            where = "%s/%s" % (path, key) if path else key
            if key not in found:
                out.append('"%s" is missing in the page' % where)
            elif key not in wanted:
                out.append('"%s" is only in the page' % where)
            else:
                out += json_diff(wanted[key], found[key], where)
        return out
    if wanted != found:
        return ['"%s": the file has %s, the page has %s' % (path or "value", short(wanted, 70), short(found, 70))]
    return []


# ---------------------------------------------------------------- the vnu validator

def run_vnu(workdir, names, css=False):
    """Check the named files (inside workdir) in one validator run. -> dict(error, version, checked, messages, stray)"""
    out = {"error": None, "version": "", "checked": set(), "messages": {n: [] for n in names}, "stray": []}
    if not names:
        return out
    java = shutil.which("java")
    if not java:
        out["error"] = "java was not found on the PATH, so the vnu validator could not run"
        return out
    if not os.path.isfile(common.VNU_JAR):
        out["error"] = "node_modules/vnu-jar/build/dist/vnu.jar was not found in the tools folder"
        return out
    cmd = [java, "-Dfile.encoding=UTF-8", "-Dstdout.encoding=UTF-8", "-Dstderr.encoding=UTF-8", "-jar", common.VNU_JAR,
           "--format", "json", "--asciiquotes", "--exit-zero-always", "--verbose"]
    if css:
        cmd.append("--css")
    try:
        proc = subprocess.run(cmd + list(names), cwd=workdir, capture_output=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        out["error"] = "the vnu validator could not be run (%s)" % type(e).__name__
        return out
    # --verbose writes the name of every checked file to stdout, the JSON result goes to stderr as one line.
    doc = None
    for line in reversed(proc.stderr.decode("utf-8", "replace").splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                doc = json.loads(line)
                break
            except ValueError:
                continue
    if not isinstance(doc, dict) or not isinstance(doc.get("messages"), list):
        out["error"] = "the vnu validator gave no JSON result (exit code %s)" % proc.returncode
        return out
    out["version"] = str(doc.get("version", ""))
    out["checked"] = {re.split(r"[\\/]", l.strip())[-1] for l in proc.stdout.decode("utf-8", "replace").splitlines() if l.strip()}
    for m in doc["messages"]:
        name = urllib.parse.unquote(str(m.get("url") or "").rsplit("/", 1)[-1])
        (out["messages"][name] if name in out["messages"] else out["stray"]).append(m)
    return out


def message_level(m):
    if m.get("type") == "info":
        return "warning" if m.get("subType") == "warning" else "note"
    return "error"      # "error", "non-document-error" and anything unknown


def message_place(m):
    last, first = m.get("lastLine"), m.get("firstLine") or m.get("lastLine")
    if not last:
        return "whole document"
    place = "line %s" % first if first == last else "lines %s to %s" % (first, last)
    if m.get("firstColumn") and first == last:
        place += ", column %s" % m["firstColumn"]
    elif m.get("lastColumn"):
        place += ", column %s" % m["lastColumn"]
    return place


def validator_entries(run, name, page, kind, label, owner):
    """Entries for one document: a summary (<kind>-valid) and one entry per validator message."""
    what = "HTML" if kind == "html" else "CSS"
    expected = "0 errors from the vnu %s validator" % what
    if run["error"]:
        return [entry(page, kind + "-valid", False, expected, "not checked: " + run["error"], label, "QA")]
    if run["checked"] and name not in run["checked"]:
        return [entry(page, kind + "-valid", False, expected, "not checked: the vnu validator did not report this document as checked", label, "QA")]
    counts = {"error": 0, "warning": 0, "note": 0}
    details = []
    for m in run["messages"].get(name, []):
        level = message_level(m)
        counts[level] += 1
        evidence = "%s, %s" % (label, message_place(m))
        if m.get("extract"):
            evidence += ": " + short(m["extract"], 200)
        details.append(entry(page, "%s-%s-%02d" % (kind, level, counts[level]), level != "error",
                             "no validator error" if level == "error" else "validator %s, listed for information" % level,
                             short(str(m.get("message", "")), 400), evidence, owner, level=level))
    actual = "%s, %s, %s" % (plural(counts["error"], "error"), plural(counts["warning"], "warning"), plural(counts["note"], "note"))
    summary = entry(page, kind + "-valid", counts["error"] == 0, expected, actual, "%s, vnu %s" % (label, run["version"]), owner)
    return [summary] + details


# ---------------------------------------------------------------- JSON-LD inside the pages

class LdScripts(html.parser.HTMLParser):
    """Collects the text of every <script type="application/ld+json"> in a page."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self._open, self._text = [], False, []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and (dict(attrs).get("type") or "").strip().lower() == "application/ld+json":
            self._open, self._text = True, []

    def handle_endtag(self, tag):
        if tag == "script" and self._open:
            self.blocks.append("".join(self._text))
            self._open = False

    def handle_data(self, data):
        if self._open:
            self._text.append(data)


def ld_blocks(body):
    parser = LdScripts()
    parser.feed(body.decode("utf-8", "replace"))
    parser.close()
    return parser.blocks


def check_page_jsonld(slug, body, label, ld_value, ld_problem):
    blocks = ld_blocks(body)
    parsed = [load_json_text(b.strip()) for b in blocks]
    if slug == "home":
        expected = "exactly one JSON-LD script in the page, with the same content as %s" % JSONLD_FILE
        if ld_problem:
            return entry(slug, "jsonld-embedded", False, expected, "cannot compare: %s %s" % (JSONLD_FILE, ld_problem), label, "SEO")
        if len(blocks) != 1:
            return entry(slug, "jsonld-embedded", False, expected, "%s in the page" % plural(len(blocks), "JSON-LD script"), label, "PAGES")
        value, problem = parsed[0]
        if problem:
            return entry(slug, "jsonld-embedded", False, expected, "the JSON-LD script in the page " + problem, label, "PAGES")
        if value != ld_value:
            diff = json_diff(ld_value, value)
            actual = "the page embeds other content than %s (%s)" % (JSONLD_FILE, plural(len(diff), "difference"))
            return entry(slug, "jsonld-embedded", False, expected, actual, "%s: %s" % (label, "; ".join(diff[:4])), "PAGES")
        return entry(slug, "jsonld-embedded", True, expected, "one JSON-LD script, same content as %s" % JSONLD_FILE, label, "PAGES")
    expected = "no JSON-LD script on this page (the build contract puts it on the home page only)"
    if not blocks:
        return entry(slug, "jsonld-absent", True, expected, "no JSON-LD script", label, "PAGES")
    same = sum(1 for value, problem in parsed if not problem and not ld_problem and value == ld_value)
    actual = "%s on this page" % plural(len(blocks), "JSON-LD script")
    if same:
        actual += ", with the content of %s" % JSONLD_FILE
    return entry(slug, "jsonld-absent", False, expected, actual, "%s: %s" % (label, short(blocks[0], 120)), "PAGES")


# ---------------------------------------------------------------- site files, standard library only

def check_sitemap(got):
    rel = "sitemap.xml"
    wanted = "well formed XML"
    if not got.ok:
        return [entry(SITE_PAGE, "sitemap-wellformed", False, wanted, got.problem(), rel, "SEO")]
    try:
        root = ET.fromstring(got.body)
    except ET.ParseError as e:
        return [entry(SITE_PAGE, "sitemap-wellformed", False, wanted, "not well formed: %s" % e, rel, "SEO")]
    out = [entry(SITE_PAGE, "sitemap-wellformed", True, wanted, "well formed, %d bytes" % len(got.body), rel, "SEO")]
    expected = "exactly these %d addresses: %s" % (len(SITEMAP_URLS), ", ".join(SITEMAP_URLS))
    if root.tag != SITEMAP_NS + "urlset":
        out.append(entry(SITE_PAGE, "sitemap-urls", False, expected,
                         "the root element is %s, not urlset in the sitemaps.org 0.9 namespace" % root.tag, rel, "SEO"))
        return out
    locs = [(u.findtext(SITEMAP_NS + "loc") or "").strip() for u in root.findall(SITEMAP_NS + "url")]
    missing = [u for u in SITEMAP_URLS if u not in locs]
    extra = sorted({u for u in locs if u not in SITEMAP_URLS})
    twice = sorted({u for u in locs if u in SITEMAP_URLS and locs.count(u) > 1})
    problems = []
    if missing:
        problems.append("missing: " + ", ".join(missing))
    if extra:
        problems.append("not expected: " + ", ".join(u or "(a url entry without loc)" for u in extra))
    if twice:
        problems.append("listed more than once: " + ", ".join(twice))
    actual = "; ".join(problems) if problems else "%d addresses, exactly the expected ones" % len(locs)
    out.append(entry(SITE_PAGE, "sitemap-urls", not problems, expected, actual, "%s lists %s" % (rel, plural(len(locs), "address")), "SEO"))
    return out


def check_robots(got):
    rel = "robots.txt"
    allow_expected = "robots.txt blocks nothing: no Disallow rule with a path, for any crawler"
    if not got.ok:
        return [entry(SITE_PAGE, "robots-allows-all", False, allow_expected, got.problem(), rel, "SEO")]
    text = got.body.decode("utf-8", "replace").lstrip("\ufeff")
    lines, malformed = [], []
    for number, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        field, colon, value = line.partition(":")
        field = field.strip().lower()
        if not colon or not re.fullmatch(r"[a-z][a-z-]*", field):
            malformed.append("line %d is not a robots.txt rule: %s" % (number, short(raw, 60)))
            continue
        lines.append((number, field, value.strip()))
    problems = list(malformed[:3])
    if len(malformed) > 3:
        problems.append("and %d more lines like that" % (len(malformed) - 3))
    in_group = False
    for number, field, value in lines:
        if field == "user-agent":
            in_group = True
        elif field in ("allow", "disallow") and not in_group:
            problems.append("line %d: %s rule before any User-agent line" % (number, field.capitalize()))
        if field == "disallow" and value:
            problems.append("line %d blocks crawlers: Disallow: %s" % (number, value))
    rules = ", ".join("%s: %s" % (f.capitalize(), v) for _, f, v in lines if f in ("user-agent", "allow", "disallow")) or "no rules"
    out = [entry(SITE_PAGE, "robots-allows-all", not problems, allow_expected, "; ".join(problems) if problems else rules, rel, "SEO")]
    sitemaps = [v for _, f, v in lines if f == "sitemap"]
    ok = bool(sitemaps) and set(sitemaps) == {SITEMAP_ADDRESS}
    actual = ", ".join("Sitemap: " + s for s in sitemaps) if sitemaps else "no Sitemap line"
    out.append(entry(SITE_PAGE, "robots-sitemap", ok, "one line  Sitemap: " + SITEMAP_ADDRESS, actual, rel, "SEO"))
    return out


def check_nojekyll(source, got):
    rel, expected = ".nojekyll", ".nojekyll exists and is empty (0 bytes)"
    size = lambda g: "empty (0 bytes)" if not g.body else "not empty: %s" % plural(len(g.body), "byte")
    if got.ok:
        return entry(SITE_PAGE, "nojekyll-empty", not got.body, expected, size(got), rel, "SEO")
    if source.remote and got.status == 404:
        # Some hosts do not serve files whose name starts with a dot. Then the file in the site folder is what can be checked.
        local = LocalSource(common.SITE).get(rel)
        if local.ok:
            actual = "%s (%s is not served by this address, so the file in the site folder was checked instead)" % (size(local), rel)
            return entry(SITE_PAGE, "nojekyll-empty", not local.body, expected, actual, rel, "SEO")
        return entry(SITE_PAGE, "nojekyll-empty", False, expected, "not served by this address and missing in the site folder", rel, "SEO")
    return entry(SITE_PAGE, "nojekyll-empty", False, expected, got.problem(), rel, "SEO")


def check_json_file(rel, got, owner, check=None, optional=False):
    """-> (entry, value, problem)"""
    check = check or "json-parses %s" % rel
    expected = "%s parses as strict UTF-8 JSON" % rel
    if not got.ok:
        if optional and got.status == 404:
            note = "not published at this address and not named in the build contract, so not checked"
            return entry(SITE_PAGE, check, True, expected, note, rel, owner, level="note"), None, "is missing"
        return entry(SITE_PAGE, check, False, expected, got.problem(), rel, owner), None, "is missing"
    value, problem = load_json_bytes(got.body)
    if problem:
        return entry(SITE_PAGE, check, False, expected, "%s %s" % (rel, problem), rel, owner), None, problem
    kind = type(value).__name__
    size = "%s with %s" % ("object", plural(len(value), "key")) if isinstance(value, dict) else kind
    return entry(SITE_PAGE, check, True, expected, "parses (%s, %d bytes)" % (size, len(got.body)), rel, owner), value, None


def check_jsonld_facts(value):
    """The business facts inside the JSON-LD file against the facts of the brief. One entry, owner SEO.
    Read loosely where schema.org allows more than one spelling (a day as a word or as a schema.org address,
    a time with or without seconds, one opening rule or a list of them), strictly in what the values say."""
    expected = ("the facts in %s are the facts of the brief: name %s, telephone %s, email %s, url %s, address %s, "
                "open %s to %s from %s to %s, sameAs the Facebook and the Instagram address"
                % (JSONLD_FILE, JSONLD_FACTS["name"], JSONLD_FACTS["telephone"], JSONLD_FACTS["email"], JSONLD_FACTS["url"],
                   ", ".join(JSONLD_ADDRESS.values()), JSONLD_DAYS[0], JSONLD_DAYS[-1], JSONLD_OPENS, JSONLD_CLOSES))
    nodes = value if isinstance(value, list) else [value]
    node = next((n for n in nodes if isinstance(n, dict) and ("telephone" in n or "address" in n)), nodes[0] if nodes and isinstance(nodes[0], dict) else {})
    wrong = []
    for key, want in JSONLD_FACTS.items():
        if node.get(key) != want:
            wrong.append("%s is %s (the brief: %s)" % (key, json.dumps(node.get(key), ensure_ascii=False), want))
    address = node.get("address") if isinstance(node.get("address"), dict) else {}
    for key, want in JSONLD_ADDRESS.items():
        if address.get(key) != want:
            wrong.append("address.%s is %s (the brief: %s)" % (key, json.dumps(address.get(key), ensure_ascii=False), want))
    rules = node.get("openingHoursSpecification")
    rules = [rules] if isinstance(rules, dict) else [r for r in rules or [] if isinstance(r, dict)] if isinstance(rules, list) else []
    days, hours = [], set()
    for rule in rules:
        listed = rule.get("dayOfWeek")
        for day in (listed if isinstance(listed, list) else [listed]):
            days.append(str(day).rstrip("/").rsplit("/", 1)[-1])
        hours.add(tuple(re.sub(r"^(\d\d:\d\d):00$", r"\1", str(rule.get(k))) for k in ("opens", "closes")))
    if sorted(days) != sorted(JSONLD_DAYS):
        wrong.append("the opening days are %s (the brief: %s)" % (", ".join(days) or "not given", ", ".join(JSONLD_DAYS)))
    if hours != {(JSONLD_OPENS, JSONLD_CLOSES)}:
        wrong.append("the opening hours are %s (the brief: %s to %s)" % (
            "; ".join("%s to %s" % h for h in sorted(hours)) or "not given", JSONLD_OPENS, JSONLD_CLOSES))
    same = node.get("sameAs")
    same = [same] if isinstance(same, str) else same if isinstance(same, list) else []
    if sorted(map(str, same)) != sorted(JSONLD_SAME_AS):
        wrong.append("sameAs is %s (the brief: %s)" % (json.dumps(same, ensure_ascii=False), ", ".join(JSONLD_SAME_AS)))
    actual = "%s: %s" % (plural(len(wrong), "fact") + " differ" + ("s" if len(wrong) == 1 else ""), "; ".join(wrong)) if wrong else "all facts match the brief"
    return entry(SITE_PAGE, "jsonld-facts", not wrong, expected, actual, JSONLD_FILE, "SEO")


def statement_start(source):
    """Where the first statement of a script starts: the index after the leading white space and comments."""
    i, n = (1 if source.startswith("\ufeff") else 0), len(source)
    while i < n:
        if source[i].isspace():
            i += 1
        elif source.startswith("//", i):
            end = source.find("\n", i)
            i = n if end < 0 else end + 1
        elif source.startswith("/*", i):
            end = source.find("*/", i + 2)
            i = n if end < 0 else end + 2
        else:
            break
    return i


def statement_end(source, start):
    """Where the statement that starts at `start` ends: after its first semicolon, or at the line end.
    A semicolon inside a quoted text does not end it (a link may hold one)."""
    j, n, quote = start, len(source), None
    while j < n and source[j] != "\n":
        c = source[j]
        if quote:
            if c == "\\":
                j += 1                      # the next character is escaped
            elif c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == ";":
            return j + 1
        j += 1
    return min(j, n)


def first_statement(source):
    """The first statement of a script: what follows the leading white space and comments, up to the first semicolon or line end."""
    start = statement_start(source)
    return source[start:statement_end(source, start)].strip()


# The host of a link on the web: at least two names with a dot between them.
_LINK_HOST = re.compile(r"[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+", re.I)


def link_host(link):
    try:
        return urllib.parse.urlsplit(link).hostname or ""
    except ValueError:      # for example a broken address in square brackets
        return ""


def booking_statement(source):
    """Which of the two valid forms the first statement of js/site.js has (build contract, decision 19).

    -> (form, statement, link, problem)
       form     "empty"   the statement is  var BOOKING_URL = "";
                "filled"  the statement is  var BOOKING_URL = "https://...";  with a link that can be opened
                "neither" anything else; problem then says what is wrong, when that can be told
       link     the text between the quote marks ("" for the empty form)"""
    start = statement_start(source)
    end = statement_end(source, start)
    statement = source[start:end].strip()
    if statement == BOOKING_STATEMENT:
        return "empty", statement, "", ""
    filled = BOOKING_FILLED.fullmatch(statement)
    if not filled:
        if not statement:
            return "neither", statement, "", "the file has no statement"
        hint = ""
        if "BOOKING_URL" not in statement:
            hint = "another statement comes before BOOKING_URL"
        elif statement + ";" == BOOKING_STATEMENT or BOOKING_FILLED.fullmatch(statement + ";"):
            hint = "the ; at the end is missing"
        elif statement.replace("'", '"') == BOOKING_STATEMENT or BOOKING_FILLED.fullmatch(statement.replace("'", '"')):
            hint = "single quote marks where the contract writes double ones"
        return "neither", statement, "", hint
    link = filled.group(1)
    if '"' in link or "\\" in link:
        problem = "there is more between the first and the last quote mark than one plain link"
    elif not link.strip():
        problem = "there are only spaces between the quote marks, and without a link there must be nothing between them"
    elif re.search(r"[\s<>\x00-\x1f\x7f]", link):
        problem = "the link has a space or a character that does not belong in a link"
    elif link.lower().startswith("http://"):
        problem = "the link starts with http://, the contract asks for https://"
    elif not link.startswith("https://"):
        problem = "the link does not start with https://"
    elif not _LINK_HOST.fullmatch(link_host(link)):
        problem = "there is no web host name (such as book.squareup.com) after https://, so this is not a real address"
    else:
        # The note in the script shows a made-up address as an example. Pasting that one is not a booking link.
        rest = source[:start] + " " + source[end:]
        examples = {u.rstrip(".,;:)").rstrip("/") for u in re.findall(r"https?://[^\s\"'<>\\]+", rest)}
        problem = "the link is the example address from the notes in the script, not a real booking link" if link.rstrip("/") in examples else ""
    return ("neither" if problem else "filled"), statement, link, problem


def run_node_check(workdir, name):
    """node --check on a copy of the script. -> (ok, actual, evidence), ok None when node could not run."""
    node = shutil.which("node")
    if not node:
        return None, "not checked: node was not found on the PATH", ""
    try:
        proc = subprocess.run([node, "--check", name], cwd=workdir, capture_output=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, "not checked: node could not be run (%s)" % type(e).__name__, ""
    if proc.returncode == 0:
        return True, "no syntax error", ""
    # Typical output: "<path>:LINE", the source line, a caret line, an empty line, "SyntaxError: ...". Keep the path out of the report.
    lines = [l.rstrip() for l in proc.stderr.decode("utf-8", "replace").splitlines()]
    error = next((l.strip() for l in lines if re.match(r"\s*\w*Error\b", l)), "node --check failed with exit code %s" % proc.returncode)
    evidence = ""
    for index, line in enumerate(lines):
        found = re.search(re.escape(name) + r":(\d+)\s*$", line)
        if found:
            code = lines[index + 1].strip() if index + 1 < len(lines) else ""
            evidence = "line %s: %s" % (found.group(1), short(code, 160))
            break
    return False, error, evidence


def check_script(got, node_result):
    out = []
    syntax_expected = "%s passes node --check" % JS_FILE
    first_expected = ("the first statement of %s is exactly  %s  (empty until the owner pastes the Square link, then the link "
                      "between the quote marks; build contract, decision 19)" % (JS_FILE, BOOKING_EXPECTED))
    if not got.ok:
        return [entry(SITE_PAGE, "js-syntax", False, syntax_expected, got.problem(), JS_FILE, "INTERACTION")]
    ok, actual, evidence = node_result
    label = JS_FILE + (", " + evidence if evidence else "")
    out.append(entry(SITE_PAGE, "js-syntax", bool(ok), syntax_expected, actual, label, "QA" if ok is None else "INTERACTION"))
    form, found, link, problem = booking_statement(got.body.decode("utf-8", "replace"))
    if form == "empty":
        actual = "the empty form:  %s  No booking link yet, so the Book Now buttons call the phone number" % found
    elif form == "filled":
        actual = "the filled form:  %s  The Book Now buttons open this link" % short(found, 300)
    elif not found:
        actual = problem
    else:
        actual = "not one of the two valid forms. The first statement is  %s" % short(found, 160) + ("  Problem: " + problem if problem else "")
    out.append(entry(SITE_PAGE, "js-booking-url-first", form != "neither", first_expected, actual, JS_FILE, "INTERACTION",
                     form=form, booking_url=link))
    return out


# ---------------------------------------------------------------- scratch folder

def make_workdir():
    """A scratch folder for the copies handed to java and node: in the tools folder, never in the site folder."""
    scratch = os.path.join(common.ENV, "stage", "qa", NAME)
    try:
        os.makedirs(scratch, exist_ok=True)
        return tempfile.mkdtemp(prefix="run-", dir=scratch)
    except OSError:
        return tempfile.mkdtemp(prefix="hbg-" + NAME + "-")


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = common.cli_parser(
        "HTML and CSS validation (vnu) plus sitemap, robots, .nojekyll, JSON and script checks. No browser.",
        base_help="check this address instead of the files in the site folder, for example https://achoostorm.github.io/hairbygerta/",
        page_help="SLUG[,SLUG] or all (default). The site files are checked on every run.",
        viewport_help="accepted because every QA script takes it; not used, this script needs no browser")
    ap.add_argument("--show-warnings", action="store_true", help="also print the validator warnings and notes")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    slugs = common.cli_pages(ap, args.page)

    source = RemoteSource(args.base) if args.base else LocalSource(common.SITE)
    found_content = sorted("content/" + os.path.basename(p) for p in glob.glob(os.path.join(common.SITE, "content", "*.json")))
    content_files = CONTRACT_CONTENT + [c for c in found_content if c not in CONTRACT_CONTENT]

    # what to read: key -> (path in the site folder, address on the server)
    plan = {("page", s): (page_file(s), common.PAGES[s]) for s in slugs}
    for rel in [CSS_FILE, JS_FILE, "sitemap.xml", "robots.txt", ".nojekyll", JSONLD_FILE, MANIFEST_FILE] + content_files:
        plan[("file", rel)] = (rel, None)

    results = []
    workdir = make_workdir()
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            keys = list(plan)
            got = dict(zip(keys, pool.map(lambda k: source.get(*plan[k]), keys)))

            # copies for the validator and for node. Some hosts answer with status 404 even when 404.html is asked for by name.
            # That answer is only taken as our page when it carries the site's own address (canonical link, mail link),
            # so the host's stock "not found" page of an unpublished site is never validated as ours.
            usable = {s: got[("page", s)] for s in slugs
                      if got[("page", s)].ok or (s == "404" and source.remote and got[("page", s)].status == 404
                                                 and OWN_MARK in got[("page", s)].body)}
            for slug, g in usable.items():
                with open(os.path.join(workdir, slug + ".html"), "wb") as f:
                    f.write(g.body)
            css, js = got[("file", CSS_FILE)], got[("file", JS_FILE)]
            if css.ok:
                with open(os.path.join(workdir, "style.css"), "wb") as f:
                    f.write(css.body)
            if js.ok:       # .cjs: checked as a classic script, the way a browser runs a script tag without type=module
                with open(os.path.join(workdir, "site.cjs"), "wb") as f:
                    f.write(js.body)
            html_run = pool.submit(run_vnu, workdir, [s + ".html" for s in usable], False)
            css_run = pool.submit(run_vnu, workdir, ["style.css"] if css.ok else [], True)
            node_run = pool.submit(run_node_check, workdir, "site.cjs") if js.ok else None

            # standard library checks, while java and node are running
            ld_entry, ld_value, ld_problem = check_json_file(JSONLD_FILE, got[("file", JSONLD_FILE)], "SEO", check="jsonld-file-parses")
            if not ld_problem and not isinstance(ld_value, (dict, list)):
                ld_problem = "is not a JSON object"
                ld_entry = entry(SITE_PAGE, "jsonld-file-parses", False, ld_entry["expected"], "%s %s" % (JSONLD_FILE, ld_problem), JSONLD_FILE, "SEO")
            label = {s: (got[("page", s)].where if source.remote else page_file(s)) for s in slugs}
            jsonld = {s: check_page_jsonld(s, g.body, label[s], ld_value, ld_problem) for s, g in usable.items()}
            site = check_sitemap(got[("file", "sitemap.xml")]) + check_robots(got[("file", "robots.txt")])
            site.append(check_nojekyll(source, got[("file", ".nojekyll")]))
            site.append(ld_entry)
            if not ld_problem:      # a file that cannot be read has its failed entry already
                site.append(check_jsonld_facts(ld_value))
            for rel in content_files:
                site.append(check_json_file(rel, got[("file", rel)], "CONTENT", optional=source.remote and rel not in CONTRACT_CONTENT)[0])
            site.append(check_json_file(MANIFEST_FILE, got[("file", MANIFEST_FILE)], "ASSETS")[0])

            html_run, css_run = html_run.result(), css_run.result()
            node_result = node_run.result() if node_run else None

        for slug in slugs:
            if slug in usable:
                results += validator_entries(html_run, slug + ".html", slug, "html", label[slug], "PAGES")
                results.append(jsonld[slug])
            else:
                results.append(entry(slug, "html-valid", False, "0 errors from the vnu HTML validator",
                                     "not checked: " + got[("page", slug)].problem(), label[slug], "PAGES"))
        if css.ok:
            results += validator_entries(css_run, "style.css", SITE_PAGE, "css", CSS_FILE, "DESIGN")
        else:
            results.append(entry(SITE_PAGE, "css-valid", False, "0 errors from the vnu CSS validator", "not checked: " + css.problem(), CSS_FILE, "DESIGN"))
        for m in html_run["stray"] + css_run["stray"]:      # a message that belongs to none of the documents: a validator problem
            results.append(entry(SITE_PAGE, "validator-message-%02d" % (sum(1 for r in results if r["check"].startswith("validator-message")) + 1),
                                 message_level(m) != "error", "no message outside the checked documents", short(str(m.get("message", "")), 400),
                                 "vnu validator", "QA", level=message_level(m)))
        results += site
        results += check_script(js, node_result)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    failed = [r for r in results if not r["ok"]]
    warnings = [r for r in results if r["ok"] and r.get("level") in ("warning", "note")]
    # Which form of the BOOKING_URL statement the script has: "empty", "filled", "neither", or "not checked" (no script to read).
    booking = next((r for r in results if r["check"] == "js-booking-url-first"), None)
    booking_form = booking["form"] if booking else "not checked"
    extra = {"script": "qa/%s.py" % NAME, "source": "server answers" if source.remote else "files in the site folder",
             "validator": "vnu %s" % (html_run["version"] or css_run["version"] or "did not run"),
             "booking_url": {"form": booking_form, "link": booking["booking_url"] if booking else ""},
             "last_run": {"pages": slugs, "checks": len(results), "failed": len(failed), "warnings": len(warnings)}}
    # Validator messages have no fixed names, so every earlier entry of the pages of this run is replaced.
    common.save_report(NAME, results, source.label, extra, replace=set(slugs) | {SITE_PAGE})

    for r in failed:
        print("FAIL [%s] %s | %s | %s | %s" % (r["owner"], r["page"], r["check"], r["actual"], r["evidence"]))
    if args.show_warnings:
        for r in warnings:
            print("warn [%s] %s | %s | %s | %s" % (r["owner"], r["page"], r["check"], r["actual"], r["evidence"]))
    owners = {}
    for r in failed:
        owners[r["owner"]] = owners.get(r["owner"], 0) + 1
    by_owner = " (%s)" % ", ".join("%s %d" % (o, n) for o, n in sorted(owners.items())) if owners else ""
    print("%s: %s, %d failed%s, %s, BOOKING_URL %s, source %s, report qa/reports/%s.json"
          % (NAME, plural(len(results), "check"), len(failed), by_owner, plural(len(warnings), "warning"),
             {"empty": "empty (Book Now calls the phone)", "filled": "filled (Book Now opens the link)",
              "neither": "in neither valid form"}.get(booking_form, booking_form), source.label, NAME))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
