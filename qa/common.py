"""Shared helpers for every QA script in this folder.

The QA scripts need Pillow and Playwright, which live in the tools folder next to the site folder
(hairbygerta-env). Run them with that Python, for example:

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_page.py

Typical use inside a script:

    from common import site_server, context_options, guard, watch, PAGES, unexpected_blocked, target_base
    with target_base(args.base) as base, sync_playwright() as p:   # local server unless --base is given
        ctx = p.chromium.launch().new_context(**context_options(p, "phone", dsf=1))
        log = {}
        guard(ctx, log, base, allow_fonts=True)
        page = ctx.new_page(); watch(page, log)
        page.goto(base + PAGES["gallery"])

What every check script of the suite shares (qa/run_all.py relies on it):

  Command line   --base URL, --page SLUG[,SLUG] or all, --viewport desktop, phone or both. Build the parser with
                 cli_parser() and read the pages with cli_pages(), so every script answers a wrong option the same way.
                 --base is refused when the address serves the Wix site instead of the new one (see foreign_site):
                 a screenshot of the Wix site must never be saved in the site folder.
  Exit code      0 every check passed, 1 a check failed or the command line was wrong.
                 2 is used by qa/licensing_check.py alone and means: a file identical to a restricted file was found.
  Report         qa/reports/<name>.json, written with save_report():
                 {ok, base, generated, results: [{page, viewport, check, ok, expected, actual, evidence, owner}]}
                 page      a slug from PAGES, or "site" for a check of the whole site
                 viewport  "desktop", "phone", or "-" for a check that needs no browser
                 owner     who has to fix it when it fails, one name from OWNERS
                 base      the address given with --base, or report_base(None) for the site folder on this computer
  Screenshots    of our own pages only, in qa/screenshots, named in evidence as qa/screenshots/<file>.
                 Anything that shows the live Wix site goes to PRIVATE (outside the site folder), never into qa/.
"""
import argparse, contextlib, json, os, socket, subprocess, sys, time, urllib.error, urllib.request
from urllib.parse import urlsplit

sys.dont_write_bytecode = True   # no __pycache__ in the site folder (a compiled file carries the path of this computer)

QA = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(QA)
PARENT = os.path.dirname(SITE)
# Tools (browser, validator, axe) and private scratch space live outside the site folder.
ENV = os.environ.get("HB_ENV") or os.path.join(PARENT, "hairbygerta-env")
# The Wix-only originals. Reference for the licensing check, never copied into the site.
RESTRICTED = os.environ.get("HB_RESTRICTED") or os.path.join(PARENT, "hairbygerta-wix-only-photos")
# Anything that shows the live Wix site (reference screenshots, side-by-side images) goes here, never into the site folder.
PRIVATE = os.path.join(ENV, "qa-private")
WIX_REF = os.path.join(ENV, "wix-ref")
REPORTS = os.path.join(QA, "reports")
SHOTS = os.path.join(QA, "screenshots")
VNU_JAR = os.path.join(ENV, "node_modules", "vnu-jar", "build", "dist", "vnu.jar")
AXE_JS = os.path.join(ENV, "node_modules", "axe-core", "axe.min.js")

PREFIX = "/hairbygerta/"
FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
# Third parties the site is expected to call. A blocked request to any other host is a real problem.
EXPECTED_EXTERNAL_HOSTS = FONT_HOSTS + ("www.google.com", "maps.google.com", "maps.googleapis.com", "maps.gstatic.com")
# slug -> address relative to the site root (append to the base url)
PAGES = {
    "home": "", "gallery": "gallery/", "book-online": "book-online/", "about": "about/", "contact": "contact/",
    "english-refund-policy": "english-refund-policy/", "accessibility-statement": "accessibility-statement/",
    "english-privacy-policy": "english-privacy-policy/", "terms-conditions": "terms-conditions/", "404": "404.html",
}
VIEWPORTS = ("desktop", "phone")
PHONE = "+1-347-671-5095"
EMAIL = "info@hairbygerta.com"
# The areas of the build contract (tools/CONTRACT.md, section 1). The owner of a report entry is one of these.
OWNERS = ("ASSETS", "CONTENT", "DESIGN", "PAGES", "INTERACTION", "SEO", "DEPLOY", "RUNBOOK", "QA")
SITE_PAGE = "site"          # value of "page" for a check of the whole site
NO_VIEWPORT = "-"           # value of "viewport" for a check that needs no browser
LOCAL_BASE = "local site folder"   # value of "base" in a report when no --base was given


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@contextlib.contextmanager
def site_server(root=SITE, port=None, prefix=PREFIX):
    """Start qa/serve.py as a child process on a free port and yield the base url. Stops it on exit."""
    port = port or free_port()
    inner = (prefix or "").strip("/")
    prefix = "/" + inner + "/" if inner else "/"   # "/" serves the site at the top of the host
    proc = subprocess.Popen([sys.executable, os.path.join(QA, "serve.py"), "--root", root, "--port", str(port), "--prefix", prefix],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = f"http://127.0.0.1:{port}{prefix}"
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(base, timeout=1)
                break
            except urllib.error.HTTPError:
                break
            except Exception:
                time.sleep(0.1)
        yield base
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


@contextlib.contextmanager
def target_base(base=None):
    """Yield the address to test: the given one (for example the published GitHub Pages address), or a local server."""
    if base:
        yield base if base.endswith("/") else base + "/"
    else:
        with site_server() as local:
            yield local


def context_options(p, viewport="desktop", dsf=None):
    """'desktop' = 1280 x 900, 'phone' = the Playwright iPhone 13 preset, or a (width, height) tuple.
    dsf=1 keeps full-page phone screenshots at a readable size (the preset uses 3)."""
    if viewport == "desktop":
        opts = {"viewport": {"width": 1280, "height": 900}}
    elif viewport == "phone":
        opts = dict(p.devices["iPhone 13"])
        opts.pop("default_browser_type", None)
    else:
        opts = {"viewport": {"width": viewport[0], "height": viewport[1]}}
    if dsf:
        opts["device_scale_factor"] = dsf
    return opts


def guard(target, log, base, allow_fonts=True):
    """Let through only requests to the host of the site under test (and Google Fonts when allow_fonts).
    Everything else is aborted and listed in log['blocked'], so a missing local asset shows up as an error."""
    own = urlsplit(base).hostname or "127.0.0.1"

    def handle(route):
        url = route.request.url
        host = urlsplit(url).hostname or ""
        if url.startswith(("data:", "blob:", "about:")) or host == own or (allow_fonts and host in FONT_HOSTS):
            route.continue_()
        else:
            log.setdefault("blocked", []).append(url)
            route.abort()
    target.route("**/*", handle)


def watch(page, log):
    """Collect console errors and warnings, page errors, failed requests and 4xx/5xx responses into log."""
    def on_console(m):
        if m.type in ("error", "warning"):
            log.setdefault("console", []).append({"type": m.type, "text": m.text})
    page.on("console", on_console)
    page.on("pageerror", lambda e: log.setdefault("pageerrors", []).append(str(e)))
    page.on("requestfailed", lambda r: log.setdefault("failed", []).append({"url": r.url, "error": r.failure}))

    def on_response(r):
        if r.status >= 400:
            log.setdefault("bad_status", []).append({"url": r.url, "status": r.status})
    page.on("response", on_response)


def is_expected_external(url):
    return (urlsplit(url).hostname or "") in EXPECTED_EXTERNAL_HOSTS


def unexpected_blocked(log):
    """Blocked urls that are not on the list of third parties the site is expected to call."""
    return [u for u in log.get("blocked", []) if not is_expected_external(u)]


def report_base(base=None):
    """The value of "base" in a report: the address given with --base (with its closing slash), else LOCAL_BASE.
    The address of a local test server is never written: its port changes with every run."""
    if not base:
        return LOCAL_BASE
    return base if base.endswith("/") else base + "/"


def old_results(name):
    """The entries of the report qa/reports/<name>.json as it is on disk, or [] when there is none."""
    try:
        with open(os.path.join(REPORTS, name + ".json"), encoding="utf-8") as f:
            found = json.load(f).get("results", [])
        return [r for r in found if isinstance(r, dict)] if isinstance(found, list) else []
    except Exception:
        return []


def replaced(entry, replace):
    """Is this old entry inside what a run covers? replace holds page names and (page, viewport) pairs."""
    return bool(replace) and (entry.get("page") in replace or (entry.get("page"), entry.get("viewport")) in replace)


def save_report(name, results, base, extra=None, replace=None):
    """Write qa/reports/<name>.json. results is a list of dicts that each have page, viewport, check and ok.
    A run limited to some pages or viewports replaces only its own entries and keeps the rest.

    replace: what the run covers, as a collection of page names ("home", "site") and (page, viewport) pairs.
    Every older entry of those is dropped, not only the ones with the same check name. A script whose check names
    change from run to run (one entry per validator message, per violated rule, per difference) must pass it,
    or an entry for something that has been fixed would stay in the report for ever.

    Every entry gets the eight shared fields; an owner is written in capitals."""
    os.makedirs(REPORTS, exist_ok=True)
    path = os.path.join(REPORTS, name + ".json")
    results = [dict(r) for r in results]
    for r in results:
        r.setdefault("page", SITE_PAGE)
        r.setdefault("viewport", NO_VIEWPORT)
        r.setdefault("check", "(check without a name)")
        r["ok"] = bool(r.get("ok"))
        for field in ("expected", "actual", "evidence"):
            r.setdefault(field, "")
        r["owner"] = str(r.get("owner") or "QA").strip().upper()
    key = lambda r: (r.get("page"), r.get("viewport"), r.get("check"))
    fresh = {key(r) for r in results}
    replace = set(replace or ())
    merged = [r for r in old_results(name) if key(r) not in fresh and not replaced(r, replace)] + results
    doc = {"ok": all(r.get("ok") for r in merged), "base": base, "generated": time.strftime("%Y-%m-%d %H:%M:%S"), "results": merged}
    if extra:
        doc.update(extra)
    # Written next to the report and then moved over it, so a run that is stopped half way never leaves half a file.
    part = path + ".part"
    with open(part, "w", encoding="utf-8", newline="\n") as f:     # LF on every computer: the reports are committed
        json.dump(doc, f, ensure_ascii=False, indent=1)
    os.replace(part, path)
    return doc


def parse_pages(value):
    """'all' or 'home,gallery' -> list of slugs in the order of PAGES. Unknown names are left out (cli_pages reports them)."""
    if not value or value.strip().lower() == "all":
        return list(PAGES)
    asked = {s.strip() for s in value.split(",")}
    return [s for s in PAGES if s in asked]


def parse_viewports(value):
    return list(VIEWPORTS) if not value or value == "both" else [value]


LOCAL_HOSTS = ("127.0.0.1", "localhost", "::1")
# What tells the new site and the old Wix site apart in the HTML of the home page: every page of the new site links
# css/style.css (build contract, section 6), a Wix page loads its files from the Wix hosts below.
OUR_MARK = "css/style.css"
WIX_MARKS = ("wixstatic.com", "parastorage.com", "wix.com website builder")


def is_local(base):
    host = (urlsplit(base or "").hostname or "").lower()
    return host in LOCAL_HOSTS or host.endswith((".localhost", ".test"))


def foreign_site(base):
    """Why the address given with --base must not be tested, or "" when it may be.

    The check scripts save screenshots under qa/ in the site folder. Until the domain is moved, www.hairbygerta.com
    is still the Wix site, and a screenshot of it shows photos that are licensed for Wix only: such a picture must
    never land in the site folder. So an address that answers with a page that is not the new site is refused.
    An address that does not answer at all, or answers 404, is let through: there is nothing of Wix to photograph
    there, and the scripts report that the site is not there. Only the HTML of the home page is read, no image."""
    if not base or is_local(base):
        return ""
    url = base if base.endswith("/") else base + "/"
    if not url.lower().startswith(("http://", "https://")):
        return "%s is not a web address (it must start with http:// or https://)" % base
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (hairbygerta QA)", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=20) as r:
            if r.status != 200:
                return ""
            text = r.read(2000000).decode("utf-8", "replace").lower()
    except Exception:
        return ""
    wix = [m for m in WIX_MARKS if m in text]
    if wix or OUR_MARK not in text:
        what = "it is a Wix page (it names %s)" % wix[0] if wix else "its home page does not link %s" % OUR_MARK
        return ("%s does not serve the new site: %s. The QA scripts save screenshots in the site folder, and a picture of the "
                "Wix site shows photos licensed for Wix only, so this address is not tested" % (url, what))
    return ""


class Parser(argparse.ArgumentParser):
    """A wrong option ends every QA script with exit code 1. argparse would use 2, which in this suite means
    "a file identical to a restricted file was found" and stops every commit.
    An address given with --base that serves the Wix site (or any site but ours) is a wrong option too, see foreign_site()."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(1, "%s: error: %s\n" % (self.prog, message))

    def parse_args(self, args=None, namespace=None):
        found = super().parse_args(args, namespace)
        why = foreign_site(getattr(found, "base", None))
        if why:
            self.error("--base: " + why)
        return found


def cli_parser(description, page_help=None, viewport_help=None, base_help=None):
    """The parser every check script starts from: --base, --page and --viewport, the same everywhere."""
    ap = Parser(description=description)
    ap.add_argument("--base", default=None, help=base_help or "test this address instead of a local server, for example https://achoostorm.github.io/hairbygerta/")
    ap.add_argument("--page", default="all", help=page_help or "SLUG[,SLUG] or all (default all). Slugs: " + ", ".join(PAGES))
    ap.add_argument("--viewport", default="both", choices=VIEWPORTS + ("both",), help=viewport_help or "desktop, phone or both (default both)")
    return ap


def cli_pages(ap, value):
    """--page as a list of slugs in the order of PAGES. An unknown or empty name is a wrong option (exit code 1)."""
    if not value or value.strip().lower() == "all":
        return list(PAGES)
    asked = [s.strip() for s in value.split(",") if s.strip()]
    unknown = [s for s in asked if s not in PAGES]
    if unknown or not asked:
        ap.error("--page: unknown page %s. Pages: %s" % (", ".join(unknown) or "(none given)", ", ".join(PAGES)))
    return [s for s in PAGES if s in asked]
