"""Page health check: every page of the site, at desktop and at phone size.

Run it with the Python that has Playwright (see common.py), from any folder:

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_page.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_page.py --page home,gallery --viewport phone
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_page.py --base https://achoostorm.github.io/hairbygerta/

For each page and viewport it writes one entry per check into qa/reports/check_page.json:

    page-loads          the address answers 200 (the 404 page may answer 200 or 404)
    screenshot          full-page screenshot in qa/screenshots/<slug>-<viewport>.png
    console-errors      no console error and no uncaught script error
    requests            no failed request, no 4xx or 5xx answer, no call to an unexpected third party
    internal-links      every internal href, src and srcset entry answers 200 (a trailing-slash redirect is followed),
                        the page links the stylesheet, the script, the three icons and the two font files it preloads,
                        fragment targets exist
    external-links      every external link is one of the links in FACTS (Facebook, Instagram, Maps link)
    tel-mailto          every tel and mailto link is exactly the salon phone and the salon email
    images-load         every image is complete with a natural width above 0 after the whole page was scrolled
    document-width      no sideways scrolling: scrollWidth equals innerWidth equals the viewport width
    one-h1              exactly one h1
    title, meta-description, lang, viewport-meta, canonical, robots-meta
    relative-addresses  every internal address in the HTML source is relative
    no-inline-style     no style attribute in the HTML source
    landmarks           header, main and footer
    skip-link           the skip link is the first focusable element, its target exists and it stays on the page
    ph-alt              every placeholder image has class ph and alt "". A placeholder is an image that
                        image-manifest.json records with the status placeholder and whose file still is the recorded
                        one (same SHA-256). A photo the owner saved over a placeholder is not one: neither with the
                        status owner-photo (build contract, decision 27) nor while the manifest still calls it a
                        placeholder (decision 15). Whether such a file may be published is judged by licensing_check.py.
    404-deep-address    (404 page only) the 404 page still finds its files when shown for a deep broken address

Exit code 0 when every check passed, 1 otherwise. One line is printed per failed check, then a summary line.

Extra options, used for the self-test of this script only: --root FOLDER serves another copy of the site,
--out FOLDER writes the report and the screenshots there instead of qa/reports and qa/screenshots.
"""
import hashlib, html.parser, json, os, queue, re, sys, threading, time, traceback
import urllib.error, urllib.parse, urllib.request
from urllib.parse import urldefrag, urljoin, urlsplit

sys.dont_write_bytecode = True   # no __pycache__ in the site folder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from common import PAGES  # noqa: E402

NAME = "check_page"

# FACTS. Never paraphrase.
CANONICAL_ROOT = "https://www.hairbygerta.com/"
FACEBOOK = "https://www.facebook.com/profile.php?id=61588784402912"
INSTAGRAM = "https://www.instagram.com/hairbygerta/"
MAPS = "https://www.google.com/maps/search/?api=1&query=644+Forest+Ave,+Staten+Island,+NY+10310"
TEL = "tel:" + common.PHONE
MAILTO = "mailto:" + common.EMAIL
# External links a page may carry. Add a link here only after the owner confirmed it.
ALLOWED_EXTERNAL = {FACEBOOK: "Facebook", INSTAGRAM: "Instagram", MAPS: "Maps link"}
# Every host this site is or will be published on. An absolute address to one of them is an internal address.
SITE_HOSTS = ("www.hairbygerta.com", "hairbygerta.com", "achoostorm.github.io")
# Files every page must link (contract, section 6), given relative to the site root.
REQUIRED_FILES = ("css/style.css", "js/site.js", "favicon.ico", "images/favicon.png", "images/apple-touch-icon.png",
                  "fonts/figtree-latin.woff2", "fonts/bodoni-moda-italic-latin.woff2")     # the two font preloads (decision 38)
# Used only when image-manifest.json cannot be read from the site under test.
PLACEHOLDER_NAMES = (
    "about-salon", "brunette-balayage", "copper-waves", "foils-highlights", "g01", "g02", "g04", "g05", "g06", "g07",
    "g10", "g14", "g15", "g16", "g17", "g18", "g19", "g20", "g21", "home-smile", "home-styling", "home-waves",
    "makeup-red-lips", "meet-extensions", "svc-bridal", "svc-haircut")
DEEP_404 = "qa-check-no-such-folder/no-such-page/"
# Errors of the connection itself (the server refused, dropped or never answered). They say nothing about the site,
# so a page that hits one is checked again before anything is reported.
TRANSPORT = re.compile(r"ERR_CONNECTION_|ERR_EMPTY_RESPONSE|ERR_TIMED_OUT|ERR_SOCKET|ERR_NETWORK|ERR_INTERNET_DISCONNECTED|"
                       r"ERR_NAME_NOT_RESOLVED|ERR_ADDRESS_|ERR_TUNNEL|ERR_PROXY|ERR_HTTP2|ERR_QUIC|ERR_INCOMPLETE|ERR_CONTENT_LENGTH", re.I)

CHECKS = ["page-loads", "screenshot", "console-errors", "requests", "internal-links", "external-links", "tel-mailto",
          "images-load", "document-width", "one-h1", "title", "meta-description", "lang", "viewport-meta", "canonical",
          "robots-meta", "relative-addresses", "no-inline-style", "landmarks", "skip-link", "ph-alt"]
CHECKS_404 = ["404-deep-address"]
# Checks whose result depends on every file arriving. If the connection kept failing, their failures go to QA.
NETWORK_CHECKS = {"page-loads", "console-errors", "requests", "internal-links", "images-load", "document-width", "404-deep-address"}


# ---------------------------------------------------------------- small helpers

def first_line(err):
    text = str(err).strip().splitlines()
    return (text[0] if text else type(err).__name__)[:300]


def short(items, limit=12):
    """A list cut to a readable length for the report."""
    items = list(items)
    if len(items) <= limit:
        return items
    return items[:limit] + ["... and %d more" % (len(items) - limit)]


def unique(items):
    seen, out = set(), []
    for it in items:
        key = json.dumps(it, sort_keys=True) if isinstance(it, (dict, list)) else it
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out


def scrub(value):
    """Take folder paths of this computer out of anything that goes into the report."""
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [scrub(v) for v in value]
    if not isinstance(value, str):
        return value
    for folder, name in ((common.PARENT, ".."), (os.path.expanduser("~"), "~")):
        if not folder or len(folder) < 4:
            continue
        for variant in {folder, folder.replace("\\", "/"), folder.replace("\\", "\\\\")}:
            value = re.sub(re.escape(variant), lambda m: name, value, flags=re.I)
    return value


def srcset_urls(value):
    return [part.split()[0] for part in (value or "").split(",") if part.strip()]


def owner_for(path):
    """Who owns the file behind an address written relative to the site root.
    An address outside the site folder is a wrong link, and links are written by PAGES."""
    path = str(path or "")
    if path.startswith(("http:", "https:", "/")):
        return "PAGES"
    path = path.lstrip("./")
    if path.startswith("images/") or path.startswith("favicon"):
        return "ASSETS"
    if path.startswith("css/"):
        return "DESIGN"
    if path.startswith("js/"):
        return "INTERACTION"
    if path in ("sitemap.xml", "robots.txt") or path.startswith("seo/"):
        return "SEO"
    return "PAGES"


class Fetcher:
    """Plain GET requests with a cache shared by all workers. Redirects are followed."""

    def __init__(self, base):
        host = urlsplit(base).hostname or ""
        local = host in ("127.0.0.1", "localhost", "::1")
        self.opener = urllib.request.build_opener(*([urllib.request.ProxyHandler({})] if local else []))
        self.cache, self.lock = {}, threading.Lock()

    def get(self, url):
        url = urldefrag(url)[0]
        with self.lock:
            hit = self.cache.get(url)
        if hit is None:
            hit = self._get(url)
            if hit["status"]:              # an answer that never arrived is not remembered, the next caller tries again
                with self.lock:
                    self.cache[url] = hit
        return hit

    def _get(self, url):
        safe = urllib.parse.quote(url, safe="%/:=&?~#+!$,;'@()*[]")
        req = urllib.request.Request(safe, headers={"User-Agent": "Mozilla/5.0 (hairbygerta QA check_page)"})
        error = ""
        for attempt in range(4):
            try:
                with self.opener.open(req, timeout=25) as r:
                    body = r.read()
                    ctype = r.headers.get("Content-Type", "")
                    text = body.decode("utf-8", "replace") if ("html" in ctype or "javascript" in ctype or "json" in ctype) else ""
                    return {"status": r.status, "final": r.geturl(), "type": ctype, "bytes": len(body), "text": text, "error": "",
                            "sha256": hashlib.sha256(body).hexdigest()}
            except urllib.error.HTTPError as e:
                return {"status": e.code, "final": e.geturl() or url, "type": "", "bytes": 0, "text": "", "error": ""}
            except Exception as e:
                error = "%s: %s" % (type(e).__name__, first_line(e))
                time.sleep(0.3 * (attempt + 1))
        return {"status": 0, "final": url, "type": "", "bytes": 0, "text": "", "error": error}


# ---------------------------------------------------------------- the HTML source

class Source(html.parser.HTMLParser):
    """The page as it was sent, before any script ran: every start tag with its attributes and line number."""

    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags, self.titles, self.h1 = [], [], 0
        self._svg, self._in_title = 0, False
        try:
            self.feed(text or "")
            self.close()
        except Exception:
            pass

    def handle_starttag(self, tag, attrs):
        a = {}
        for k, v in attrs:
            a.setdefault(k.lower(), v if v is not None else "")
        self.tags.append({"tag": tag, "attrs": a, "line": self.getpos()[0]})
        if tag == "svg":
            self._svg += 1
        elif tag == "title" and not self._svg:
            self._in_title = True
            self.titles.append("")
        elif tag == "h1":
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag == "svg" and self._svg:
            self._svg -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.titles:
            self.titles[-1] += data

    def all(self, tag):
        return [t for t in self.tags if t["tag"] == tag]

    def meta(self, name):
        return [t for t in self.all("meta") if t["attrs"].get("name", "").strip().lower() == name]

    def refs(self):
        """Every address written in the source: {tag, attr, value, rel, line, databook, target}."""
        out = []
        for t in self.tags:
            a = t["attrs"]

            def add(attr, value, t=t, a=a):
                out.append({"tag": t["tag"], "attr": attr, "value": value, "rel": a.get("rel", "").lower(),
                            "line": t["line"], "databook": "data-book" in a, "target": a.get("target", "")})
            for attr in ("href", "xlink:href", "src", "poster", "formaction"):
                if attr in a:
                    add(attr, a[attr])
            if t["tag"] == "form" and "action" in a:
                add("action", a["action"])
            if t["tag"] == "object" and "data" in a:
                add("data", a["data"])
            for attr in ("srcset", "imagesrcset"):
                for u in srcset_urls(a.get(attr)):
                    add(attr, u)
            if t["tag"] == "meta" and a.get("http-equiv", "").lower() == "refresh":
                m = re.search(r"url\s*=\s*['\"]?([^'\";]+)", a.get("content", ""), re.I)
                if m:
                    add("content", m.group(1).strip())
        return out


def show_tag(t):
    """A start tag as short readable text, for the report."""
    attrs = " ".join('%s="%s"' % (k, v[:70]) for k, v in list(t["attrs"].items())[:4])
    return "<%s%s> (line %d)" % (t["tag"], " " + attrs if attrs else "", t["line"])


class Addresses:
    """Sorts an address into fragment, tel, mailto, other, internal, site-absolute or external."""

    def __init__(self, base):
        self.base = base
        parts = urlsplit(base)
        self.origin = "%s://%s" % (parts.scheme, parts.netloc)
        self.own_host = parts.hostname or ""

    def kind(self, value, doc_url, resolved=None):
        v = (value or "").strip()
        low = v.lower()
        if not v:
            return "empty"
        if v.startswith("#"):
            return "fragment"
        if low.startswith("tel:"):
            return "tel"
        if low.startswith("mailto:"):
            return "mailto"
        m = re.match(r"^([a-z][a-z0-9+.\-]*):", low)
        if m and m.group(1) not in ("http", "https"):
            return "other"
        absolute = resolved or urljoin(doc_url, v)
        parts = urlsplit(absolute)
        if "%s://%s" % (parts.scheme, parts.netloc) == self.origin:
            return "internal"
        if (parts.hostname or "") in SITE_HOSTS or (parts.hostname or "") == self.own_host:
            return "site-absolute"
        return "external"

    def rel(self, url):
        """An address of the site under test, written relative to the site root (shorter, and the same on every run)."""
        if not url:
            return url
        if url.startswith(self.base):
            return url[len(self.base):] or "./"
        if url.startswith(self.origin + "/"):
            return url[len(self.origin):]
        return url


# ---------------------------------------------------------------- scripts run inside the page

JS_DESC = r"""
const desc = el => {
  if (!el || !el.tagName) return '';
  let s = el.tagName.toLowerCase();
  if (el.id) s += '#' + el.id;
  const c = ((el.getAttribute && el.getAttribute('class')) || '').trim();
  if (c) s += '.' + c.split(/\s+/).join('.');
  return s;
};
const txt = el => ((el && el.textContent) || '').replace(/\s+/g, ' ').trim().slice(0, 60);
"""

JS_DOM = "() => {" + JS_DESC + r"""
  const abs = v => { try { return new URL(v, document.baseURI).href; } catch (e) { return ''; } };
  const refs = [];
  const add = (el, attr, value) => {
    if (value === null) return;
    refs.push({tag: el.tagName.toLowerCase(), attr, value, abs: abs(value), rel: (el.getAttribute('rel') || '').toLowerCase(),
               target: el.getAttribute('target') || '', databook: el.hasAttribute('data-book'), where: desc(el),
               text: txt(el), label: el.getAttribute('aria-label') || ''});
  };
  document.querySelectorAll('[href]').forEach(el => add(el, 'href', el.getAttribute('href')));
  document.querySelectorAll('[src]').forEach(el => add(el, 'src', el.getAttribute('src')));
  document.querySelectorAll('[srcset]').forEach(el => (el.getAttribute('srcset') || '').split(',').forEach(c => {
    const u = c.trim().split(/\s+/)[0]; if (u) add(el, 'srcset', u); }));
  document.querySelectorAll('form[action]').forEach(el => add(el, 'action', el.getAttribute('action')));
  document.querySelectorAll('[poster]').forEach(el => add(el, 'poster', el.getAttribute('poster')));
  document.querySelectorAll('object[data]').forEach(el => add(el, 'data', el.getAttribute('data')));

  const fragments = [];
  document.querySelectorAll('a[href^="#"], area[href^="#"]').forEach(el => {
    const raw = el.getAttribute('href').slice(1);
    if (!raw) return;
    let id = raw; try { id = decodeURIComponent(raw); } catch (e) {}
    fragments.push({href: '#' + raw, where: desc(el), exists: !!(document.getElementById(id) || document.getElementsByName(id).length)});
  });

  const shown = el => el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden';
  const sel = 'a[href], area[href], button, input, select, textarea, iframe, summary, [contenteditable], [tabindex], audio[controls], video[controls]';
  const focusable = Array.from(document.querySelectorAll(sel)).filter(el => {
    if (el.disabled) return false;
    if (el.tagName === 'INPUT' && el.type === 'hidden') return false;
    const t = el.getAttribute('tabindex');
    if (t !== null && parseInt(t, 10) < 0) return false;
    if (el.closest('[inert]')) return false;
    return shown(el);
  });
  const skip = document.querySelector('a.skip');
  const skipHref = skip ? skip.getAttribute('href') : null;
  let skipUrl = null; try { skipUrl = skip && typeof skip.href === 'string' ? new URL(skip.href) : null; } catch (e) {}
  let targetId = skipUrl ? skipUrl.hash.slice(1) : '';
  try { targetId = decodeURIComponent(targetId); } catch (e) {}
  const samePage = !!skipUrl && skipUrl.href.split('#')[0] === location.href.split('#')[0];
  const target = targetId ? document.getElementById(targetId) : null;

  const outer = s => Array.from(document.querySelectorAll(s)).filter(el => !el.parentElement.closest('main, article, section, aside, nav'));
  const headers = outer('header'), mains = Array.from(document.querySelectorAll('main')), footers = outer('footer');
  const before = (a, b) => !!(a && b && (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING));

  return {
    refs, fragments,
    h1: Array.from(document.querySelectorAll('h1')).map(txt),
    landmarks: {headers: headers.map(desc), mains: mains.map(desc), footers: footers.map(desc),
                order: before(headers[0], mains[0]) && before(mains[0], footers[footers.length - 1])},
    skip: {exists: !!skip, count: document.querySelectorAll('a.skip').length, href: skipHref, samePage, targetId, target: desc(target),
           firstFocusable: desc(focusable[0]), firstIsSkip: !!skip && focusable[0] === skip,
           positiveTabindex: Array.from(document.querySelectorAll('[tabindex]')).filter(el => parseInt(el.getAttribute('tabindex'), 10) > 0).map(desc),
           active: desc(document.activeElement)},
    imgs: Array.from(document.querySelectorAll('img')).map(i => ({src: i.getAttribute('src') || '', alt: i.getAttribute('alt'),
           ph: i.classList.contains('ph'), lightbox: !!i.closest('.lightbox'), where: desc(i.parentElement) + ' > ' + desc(i)})),
    styleAttrs: document.querySelectorAll('[style]').length,
  };
}"""

JS_ACTIVE = "() => {" + JS_DESC + r"""
  const a = document.activeElement;
  return {isSkip: !!(a && a.matches && a.matches('a.skip')), what: desc(a), href: a && a.getAttribute ? a.getAttribute('href') : null, text: txt(a)};
}"""

JS_SCROLL = r"""async () => {
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const to = y => window.scrollTo({top: y, left: 0, behavior: 'instant'});
  const step = Math.max(200, Math.floor(window.innerHeight * 0.75));
  let y = 0;
  for (let i = 0; i < 400; i++) {
    to(y);
    await wait(70);
    const max = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    if (y >= max) break;
    y = Math.min(y + step, max);
  }
  await wait(150);
  to(0);
  await wait(100);
  return document.documentElement.scrollHeight;
}"""

JS_IMAGES_PENDING = r"""() => Array.from(document.images)
  .filter(i => !(i.closest('.lightbox') && !i.closest('.lightbox.open')))
  .every(i => i.complete)"""

JS_IMAGES_FORCE = r"""() => {
  const forced = [];
  for (const i of document.images) {
    if (i.closest('.lightbox') && !i.closest('.lightbox.open')) continue;
    if (!i.complete && i.loading === 'lazy') { forced.push((i.getAttribute('src') || '') + (i.getClientRects().length ? '' : ' (not shown at this size)')); i.loading = 'eager'; }
  }
  return forced;
}"""

JS_IMAGES = "() => {" + JS_DESC + r"""
  return Array.from(document.images).map(i => ({
    src: i.getAttribute('src') || '', current: i.currentSrc || '', complete: i.complete, nw: i.naturalWidth,
    lazy: i.getAttribute('loading') === 'lazy', closedLightbox: !!(i.closest('.lightbox') && !i.closest('.lightbox.open')),
    hasSource: i.hasAttribute('src') || i.hasAttribute('srcset'), where: desc(i.parentElement) + ' > ' + desc(i)}));
}"""

JS_DECODE = r"""() => Promise.race([
  Promise.all(Array.from(document.images).filter(i => i.complete && i.naturalWidth > 0 && !(i.closest('.lightbox') && !i.closest('.lightbox.open')))
    .map(i => i.decode().catch(() => null))),
  new Promise(r => setTimeout(r, 5000))
]).then(() => true)"""

JS_WIDTH = "(vw) => {" + JS_DESC + r"""
  const de = document.documentElement;
  const out = {sw: de.scrollWidth, cw: de.clientWidth, iw: window.innerWidth, wide: []};
  if (out.sw > vw && document.body) {
    const clipped = el => {
      for (let p = el.parentElement; p && p !== document.body && p !== de; p = p.parentElement) {
        if (getComputedStyle(p).overflowX !== 'visible' && p.getBoundingClientRect().right <= vw + 1) return true;
      }
      return false;
    };
    const all = Array.from(document.body.querySelectorAll('*')).map(el => ({el, r: el.getBoundingClientRect()}))
      .filter(x => x.r.width > 0 && x.r.right > vw + 1 && !clipped(x.el));
    all.sort((a, b) => b.r.right - a.r.right);
    out.wide = all.slice(0, 6).map(x => desc(x.el) + ' reaches ' + Math.round(x.r.right) + ' px');
  }
  return out;
}"""

JS_FONTS = r"""() => Promise.race([
  document.fonts.ready.then(() => 'ready'), new Promise(r => setTimeout(() => r('timeout'), 8000))
]).then(state => ({state, loaded: Array.from(document.fonts).filter(f => f.status === 'loaded').length, declared: document.fonts.size}))"""

JS_DEEP = "(origin) => {" + JS_DESC + r"""
  const here = location.href.split('#')[0];
  const sheets = Array.from(document.querySelectorAll('link[rel~="stylesheet"]')).filter(l => l.href.startsWith(origin)).map(l => {
    let rules = -1; try { rules = l.sheet ? l.sheet.cssRules.length : -1; } catch (e) { rules = -2; }
    return {href: l.href, rules};
  });
  const imgs = Array.from(document.images).filter(i => !i.closest('.lightbox'))
    .map(i => ({src: i.currentSrc || i.src, ok: i.complete && i.naturalWidth > 0, waiting: !i.complete && i.loading === 'lazy'}));
  const links = [];
  document.querySelectorAll('a[href], link[href], script[src], img[src]').forEach(el => {
    const u = el.tagName === 'A' || el.tagName === 'LINK' ? el.href : el.src;
    if (typeof u !== 'string' || !u) return;
    links.push({url: u, where: desc(el), value: el.getAttribute('href') || el.getAttribute('src') || '', rel: (el.getAttribute('rel') || '').toLowerCase()});
  });
  const skip = document.querySelector('a.skip');
  return {title: document.title, h1: document.querySelectorAll('h1').length, sheets, imgs, links, here,
          skip: skip && typeof skip.href === 'string' ? skip.href : null};
}"""


# ---------------------------------------------------------------- one page at one viewport

class Job:
    def __init__(self, slug, viewport):
        self.slug, self.viewport, self.entries = slug, viewport, {}
        self.flaky = []      # connection errors seen during this attempt

    def add(self, check, ok, expected, actual, evidence="", owner="PAGES"):
        self.entries[check] = {"page": self.slug, "viewport": self.viewport, "check": check, "ok": bool(ok),
                               "expected": expected, "actual": actual, "evidence": evidence, "owner": owner}

    def names(self):
        return CHECKS + (CHECKS_404 if self.slug == "404" else [])

    def finish(self, reason, owner):
        """Every check always gets an entry, so a report never keeps an old result for a check that did not run."""
        for name in self.names():
            if name not in self.entries:
                self.add(name, False, "the check runs", "not checked: " + reason, owner=owner)
        return [self.entries[n] for n in self.names()]


def run_job(p, browser, base, slug, viewport, shared, attempts=3):
    """One page at one viewport. Checked again (up to 3 times) when the connection to the server failed."""
    for attempt in range(1, attempts + 1):
        job = Job(slug, viewport)
        opts = common.context_options(p, viewport, dsf=1)
        ctx = browser.new_context(**opts)
        reason, owner = "the run stopped early", "QA"
        try:
            stop = inspect(ctx, opts["viewport"]["width"], base, job, shared)
            if stop:
                reason, owner = stop, ("QA" if job.flaky else "PAGES")
        except Exception as e:
            line = traceback.extract_tb(e.__traceback__)[-1].lineno if e.__traceback__ else 0
            reason = "the check script stopped (%s: %s, check_page.py near line %s)" % (type(e).__name__, first_line(e), line)
        finally:
            try:
                ctx.close()
            except Exception:
                pass
        if not job.flaky or attempt == attempts:
            break
        time.sleep(0.7 * attempt)
    entries = job.finish(reason, owner)
    if job.flaky:
        note = ("the connection to the server failed in %d attempt(s): %s. This is a problem of the test run, not of the site; run the check again."
                % (attempt, "; ".join(unique(job.flaky)[:4])))
        for e in entries:   # only the checks a lost connection can spoil; a wrong tag stays a wrong tag
            if not e["ok"] and (e["check"] in NETWORK_CHECKS or str(e["actual"]).startswith("not checked")):
                e["owner"] = "QA"
                e["evidence"] = {"note": note, "details": e["evidence"]}
    return entries, list(job.flaky), attempt


def step(job, name, fn):
    """Run one check. A check that breaks is reported as failed for QA and does not stop the others."""
    try:
        fn()
    except Exception as e:
        job.add(name, False, "the check runs", "the check stopped with an error: %s: %s" % (type(e).__name__, first_line(e)), owner="QA")


def inspect(ctx, vw, base, job, shared):
    """All checks for one page at one viewport. Returns a reason when the page could not be checked."""
    slug, viewport = job.slug, job.viewport
    adr, fetch = shared["adr"], shared["fetch"]
    rel = adr.rel
    log, console, own = {}, [], []
    common.guard(ctx, log, base, allow_fonts=True)
    page = ctx.new_page()
    page.set_default_timeout(15000)
    common.watch(page, log)
    page.on("console", lambda m: console.append({"type": m.type, "text": m.text, "url": (m.location or {}).get("url", "")}))
    page.on("response", lambda r: own.append({"url": r.url, "status": r.status}) if r.url.startswith(adr.origin + "/") else None)

    # ---- load
    url = base + PAGES[slug]
    try:
        resp = page.goto(url, wait_until="load", timeout=45000)
    except Exception as e:
        if TRANSPORT.search(str(e)) or "Timeout" in str(e):
            job.flaky.append(first_line(e)[:120])
        job.add("page-loads", False, "the page loads with status 200", "the page did not load: " + first_line(e), evidence=rel(url))
        return "the page did not load"
    status = resp.status if resp else 0
    doc_url = urldefrag(page.url)[0]
    wanted = (200, 404) if slug == "404" else (200,)
    job.add("page-loads", status in wanted, "status 200" + (" (404 is also fine for the 404 page)" if slug == "404" else ""),
            "status %s" % status, evidence={"address": rel(url), "landed on": rel(doc_url)})
    if status not in wanted:
        return "the page did not load (status %s)" % status
    try:
        source_text = resp.text()
    except Exception:
        source_text = fetch.get(url)["text"]
    src = Source(source_text)
    src_refs = src.refs()

    fonts = {"state": "unknown"}
    try:
        fonts = page.evaluate(JS_FONTS)
    except Exception:
        pass

    # ---- keyboard: the first Tab, before anything else touches the page
    tab = {"isSkip": False, "what": "", "href": None, "text": ""}
    try:
        page.keyboard.press("Tab")
        tab = page.evaluate(JS_ACTIVE)
        page.evaluate("() => { if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); window.scrollTo(0, 0); }")
    except Exception as e:
        tab["what"] = "Tab could not be pressed: " + first_line(e)

    dom = page.evaluate(JS_DOM)

    # ---- scroll the whole page so lazy images and the lazy map load
    forced = []
    try:
        page.evaluate(JS_SCROLL)
        try:
            page.wait_for_function(JS_IMAGES_PENDING, timeout=8000)
        except Exception:
            pass
        forced = page.evaluate(JS_IMAGES_FORCE)
        if forced:
            try:
                page.wait_for_function(JS_IMAGES_PENDING, timeout=8000)
            except Exception:
                pass
        try:
            page.wait_for_load_state("networkidle", timeout=6000)
        except Exception:
            pass
    except Exception:
        pass
    imgs = page.evaluate(JS_IMAGES)
    width = page.evaluate(JS_WIDTH, vw)

    # everything the browser reported up to here; what happens later (screenshot, pressing the skip link) is not judged
    seen = {k: list(v) for k, v in log.items()}
    seen_console, seen_own = list(console), list(own)
    job.flaky += ["%s %s" % (rel(f["url"]), f.get("error")) for f in seen.get("failed", [])
                  if adr.kind(f["url"], doc_url) == "internal" and TRANSPORT.search(str(f.get("error") or ""))]
    # an image that is still on its way after all that waiting means a slow run, not a broken image: look again
    job.flaky += ["%s was still loading" % i["src"] for i in imgs if not i["closedLightbox"] and i["hasSource"] and not i["complete"]]

    def kind_src(r):
        return adr.kind(r["value"], doc_url)

    def kind_dom(r):
        return adr.kind(r["value"], doc_url, r["abs"] or None)

    # ---- console-errors
    def console_errors():
        real, excused = [], []
        for c in seen_console:
            if c["type"] != "error":
                continue
            failed_load = c["text"].startswith("Failed to load resource")
            if failed_load and c["url"] and common.is_expected_external(c["url"]):
                excused.append(c)
            elif failed_load and slug == "404" and status == 404 and urldefrag(c["url"])[0] == doc_url:
                excused.append(c)
            else:
                real.append(c)
        page_errors = seen.get("pageerrors", [])
        warnings = [c["text"][:200] for c in seen_console if c["type"] == "warning"]
        owner = "INTERACTION"
        if not page_errors and real and all(c["text"].startswith("Failed to load resource") for c in real):
            owner = owner_for(rel(real[0]["url"]))
        job.add("console-errors", not real and not page_errors, "no console error and no script error",
                "%d console error(s), %d script error(s)" % (len(real), len(page_errors)),
                evidence={"console errors": short(unique({"text": c["text"][:300], "from": rel(c["url"])} for c in real)),
                          "script errors": short(unique(e[:300] for e in page_errors)),
                          "not counted, blocked third party": short(unique(rel(c["url"])[:120] for c in excused), 6),
                          "warnings": short(unique(warnings), 6)},
                owner=owner)
    step(job, "console-errors", console_errors)

    # ---- requests
    def requests():
        bad = unique({"address": rel(b["url"]), "status": b["status"]} for b in seen.get("bad_status", [])
                     if not (slug == "404" and b["status"] == 404 and urldefrag(b["url"])[0] == doc_url))
        unexpected = unique(common.unexpected_blocked(seen))
        failed = unique({"address": rel(f["url"]), "error": str(f.get("error") or "")} for f in seen.get("failed", [])
                        if not common.is_expected_external(f["url"]) and f["url"] not in unexpected)
        expected_hosts = sorted({urlsplit(f["url"]).hostname or "" for f in seen.get("failed", []) if common.is_expected_external(f["url"])}
                                | {urlsplit(u).hostname or "" for u in seen.get("blocked", []) if common.is_expected_external(u)})
        owner = "PAGES"
        if bad or failed:
            owner = owner_for((bad or failed)[0]["address"])
        job.add("requests", not bad and not failed and not unexpected,
                "no failed request, no 4xx or 5xx answer, no call to an unexpected third party",
                "%d answers from the site; %d with 4xx or 5xx, %d failed, %d to an unexpected third party"
                % (len(seen_own), len(bad), len(failed), len(unexpected)),
                evidence={"4xx or 5xx": short(bad), "failed": short(failed), "unexpected third party": short(unexpected),
                          "expected third parties, blocked or not reachable (not a failure)": expected_hosts,
                          "fonts": "%s, %s of %s font faces loaded" % (fonts.get("state"), fonts.get("loaded", "?"), fonts.get("declared", "?"))},
                owner=owner)
    step(job, "requests", requests)

    # ---- internal-links
    def internal_links():
        found = {}   # absolute address without fragment -> where it was seen
        frags = {}   # (absolute address, fragment) -> where
        for r in src_refs:
            if kind_src(r) == "internal":
                full = urljoin(doc_url, r["value"].strip())
                found.setdefault(urldefrag(full)[0], '%s %s="%s" (line %d)' % (r["tag"], r["attr"], r["value"], r["line"]))
                if urldefrag(full)[1]:
                    frags.setdefault(urldefrag(full), r["value"])
        for r in dom["refs"]:
            if kind_dom(r) == "internal" and r["abs"]:
                found.setdefault(urldefrag(r["abs"])[0], '%s %s="%s"' % (r["where"], r["attr"], r["value"]))
                if urldefrag(r["abs"])[1]:
                    frags.setdefault(urldefrag(r["abs"]), r["value"])
        og = [t["attrs"].get("content", "") for t in src.all("meta") if t["attrs"].get("property", "").lower() == "og:image"]
        for content in og:
            if content.startswith(CANONICAL_ROOT):
                found.setdefault(base + content[len(CANONICAL_ROOT):], 'og:image "%s", looked up in the site under test' % content)
        broken, redirects = [], []
        for target, where in sorted(found.items()):
            if target == doc_url:
                continue
            got = fetch.get(target)
            if not got["status"]:
                job.flaky.append("%s %s" % (rel(target), got["error"]))
            if got["status"] != 200:
                broken.append({"address": rel(target), "status": got["status"] or got["error"], "found in": where})
            elif urldefrag(got["final"])[0] != target:
                redirects.append("%s -> %s" % (rel(target), rel(got["final"])))
        missing_frag = ["%s (in %s)" % (f["href"], f["where"]) for f in dom["fragments"] if not f["exists"]]
        for (target, frag), value in sorted(frags.items()):
            if target == doc_url:
                text = source_text
            else:
                got = fetch.get(target)
                text = got["text"] if got["status"] == 200 and "html" in got["type"] else ""
            if text and not re.search(r"""\b(?:id|name)\s*=\s*["']?%s["'\s>]""" % re.escape(urllib.parse.unquote(frag)), text):
                missing_frag.append('%s (no element with id "%s" on that page)' % (value, frag))
        missing_frag = unique(missing_frag)
        required_missing = [f for f in REQUIRED_FILES if base + f not in found]
        owner = "PAGES"
        if broken and not required_missing and not missing_frag:
            owner = owner_for(broken[0]["address"])
        job.add("internal-links", not broken and not missing_frag and not required_missing,
                "every internal address answers 200, the page links %s, every fragment target exists" % ", ".join(REQUIRED_FILES),
                "%d distinct internal addresses requested, %d did not answer 200, %d fragment target(s) missing, %d required file(s) not linked"
                % (len(found), len(broken), len(missing_frag), len(required_missing)),
                evidence={"broken": short(broken), "missing fragment targets": short(missing_frag), "required files not linked": required_missing,
                          "answered after a redirect (not a failure)": short(redirects, 6)},
                owner=owner)
    step(job, "internal-links", internal_links)

    # ---- external-links
    def external_links():
        booking = shared["booking_url"]
        anchors = [r for r in dom["refs"] if r["tag"] in ("a", "area") and r["attr"] == "href"]
        ext = [r for r in anchors if kind_dom(r) == "external"]
        wrong, form = [], []
        for r in ext:
            v, what = r["value"], '%s "%s"' % (r["where"], r["label"] or r["text"])
            host = (urlsplit(v).hostname or "").lower()
            if r["databook"]:
                if not booking or v != booking:
                    wrong.append('Book Now link %s goes to %s but BOOKING_URL in js/site.js is "%s"' % (what, v, booking or ""))
            elif v not in ALLOWED_EXTERNAL:
                if "facebook." in host or host.startswith("fb."):
                    wrong.append("%s goes to %s, FACTS says %s" % (what, v, FACEBOOK))
                elif "instagram." in host:
                    wrong.append("%s goes to %s, FACTS says %s" % (what, v, INSTAGRAM))
                elif "google." in host or "goo.gl" in host:
                    wrong.append("%s goes to %s, FACTS says %s" % (what, v, MAPS))
                else:
                    wrong.append("%s goes to %s, which is not a link from FACTS" % (what, v))
            if r["target"].lower() == "_blank" and "noopener" not in r["rel"].split():
                form.append("%s opens %s in a new tab without rel=noopener" % (what, v))
        have = {r["value"] for r in ext}
        needed = [FACEBOOK, INSTAGRAM] + ([MAPS] if slug == "home" else [])
        missing = ["%s link %s is not on the page" % (ALLOWED_EXTERNAL[n], n) for n in needed if n not in have]
        other = sorted({urlsplit(r["abs"]).hostname or "" for r in dom["refs"]
                        if r["tag"] not in ("a", "area") and kind_dom(r) == "external"})
        counts = {}
        for r in ext:
            counts[r["value"]] = counts.get(r["value"], 0) + 1
        job.add("external-links", not wrong and not form and not missing,
                "every external link is the Facebook, Instagram or Maps link from FACTS, written exactly; Facebook and Instagram on every page, the Maps link on the home page",
                "%d external link(s) to %d address(es); %d wrong, %d missing, %d without rel=noopener"
                % (len(ext), len(counts), len(wrong), len(missing), len(form)),
                evidence={"external links": ["%s (%d x)" % (k, n) for k, n in sorted(counts.items())], "wrong": short(wrong),
                          "missing": missing, "new tab without rel=noopener": short(form),
                          "other third-party hosts (fonts, map)": other},
                owner="CONTENT" if wrong or missing else "PAGES")
    step(job, "external-links", external_links)

    # ---- tel-mailto
    def tel_mailto():
        booking = shared["booking_url"]
        seen_links = []   # (kind, value, where, from the source or the live page)
        for r in src_refs:
            k = kind_src(r)
            if k in ("tel", "mailto"):
                seen_links.append((k, r["value"], '%s %s (line %d)' % (r["tag"], r["attr"], r["line"]), "source"))
        for r in dom["refs"]:
            k = kind_dom(r)
            if k in ("tel", "mailto"):
                seen_links.append((k, r["value"], '%s %s' % (r["where"], r["attr"]), "page"))
        wrong = unique('%s "%s" in %s, must be exactly "%s"' % (k, v, where, TEL if k == "tel" else MAILTO)
                       for k, v, where, _ in seen_links if v != (TEL if k == "tel" else MAILTO))
        only_live = bool(wrong) and all(v == (TEL if k == "tel" else MAILTO) for k, v, _, origin in seen_links if origin == "source")
        if not booking:
            for r in dom["refs"]:
                if r["databook"] and r["attr"] == "href" and r["value"] != TEL:
                    wrong.append('Book Now button %s has href "%s", must be "%s" while BOOKING_URL is empty' % (r["where"], r["value"], TEL))
        n_tel = sum(1 for k, _, _, origin in seen_links if k == "tel" and origin == "page")
        n_mail = sum(1 for k, _, _, origin in seen_links if k == "mailto" and origin == "page")
        missing = [name for name, n in (("no tel link on the page", n_tel), ("no mailto link on the page", n_mail)) if not n]
        job.add("tel-mailto", not wrong and not missing, 'every tel link is "%s" and every mailto link is "%s", at least one of each' % (TEL, MAILTO),
                "%d tel and %d mailto link(s) on the page; %d wrong" % (n_tel, n_mail, len(wrong)),
                evidence={"wrong": short(wrong), "missing": missing},
                owner="INTERACTION" if only_live else "CONTENT")
    step(job, "tel-mailto", tel_mailto)

    # ---- images-load
    def images_load():
        counted = [i for i in imgs if not i["closedLightbox"]]
        broken = [{"image": i["src"] or "(no src)", "loaded file": rel(i["current"]), "where": i["where"],
                   "state": "no src attribute" if not i["hasSource"] else ("did not finish loading" if not i["complete"] else "broken, natural width 0")}
                  for i in counted if not (i["complete"] and i["nw"] > 0)]
        owner = "ASSETS"
        if broken and (broken[0]["state"] == "no src attribute" or broken[0]["image"].startswith(("http", "/"))):
            owner = "PAGES"
        job.add("images-load", not broken, "every image is complete with a natural width above 0 after the whole page was scrolled",
                "%d image(s), %d lazy, %d not loaded" % (len(counted), sum(1 for i in counted if i["lazy"]), len(broken)),
                evidence={"not loaded": short(broken),
                          "lazy images that only loaded after loading was forced (not a failure)": short(forced, 8),
                          "skipped, inside the closed photo viewer": len(imgs) - len(counted)},
                owner=owner)
    step(job, "images-load", images_load)

    # ---- document-width
    def document_width():
        ok = width["sw"] == vw and width["iw"] == vw
        job.add("document-width", ok, "scrollWidth = innerWidth = %d (no sideways scrolling)" % vw,
                "scrollWidth %s, innerWidth %s, clientWidth %s" % (width["sw"], width["iw"], width["cw"]),
                evidence={"elements that reach past the right edge": width["wide"]} if not ok else "", owner="DESIGN")
    step(job, "document-width", document_width)

    # ---- one-h1
    def one_h1():
        ok = len(dom["h1"]) == 1 and src.h1 == 1
        job.add("one-h1", ok, "exactly one h1", "%d h1 on the page, %d in the HTML source" % (len(dom["h1"]), src.h1),
                evidence={"h1": dom["h1"]}, owner="INTERACTION" if src.h1 == 1 and not ok else "PAGES")
    step(job, "one-h1", one_h1)

    # ---- head: title, description, lang, viewport, canonical, robots
    def head():
        title = [t.strip() for t in src.titles]
        job.add("title", len(title) == 1 and bool(title[0]), "one title tag that is not empty",
                "%d title tag(s): %s" % (len(title), json.dumps(title, ensure_ascii=False)), owner="CONTENT")
        d = [t["attrs"].get("content", "").strip() for t in src.meta("description")]
        job.add("meta-description", len(d) == 1 and bool(d[0]), "one meta description that is not empty",
                "%d meta description(s)%s" % (len(d), ": " + json.dumps([x[:160] for x in d], ensure_ascii=False) if d else ""), owner="CONTENT")
        htmls = src.all("html")
        lang = htmls[0]["attrs"].get("lang") if htmls else None
        job.add("lang", lang == "en", 'html lang="en"', "lang is %s" % (json.dumps(lang) if lang is not None else "missing"))
        v = [t["attrs"].get("content", "") for t in src.meta("viewport")]
        ok = len(v) == 1 and "width=device-width" in v[0].replace(" ", "").lower()
        job.add("viewport-meta", ok, "one viewport meta with width=device-width", "%d viewport meta: %s" % (len(v), json.dumps(v)))
        canon = [t["attrs"].get("href", "") for t in src.all("link") if "canonical" in t["attrs"].get("rel", "").lower().split()]
        robots = [t["attrs"].get("content", "").lower() for t in src.meta("robots")]
        blocked = any(tok.strip() in ("noindex", "none") for r in robots for tok in r.split(","))
        if slug == "404":
            job.add("canonical", not canon, "no canonical link on the 404 page", "%d canonical link(s): %s" % (len(canon), json.dumps(canon)))
            job.add("robots-meta", blocked, 'the 404 page has <meta name="robots" content="noindex">',
                    "robots meta: %s" % (json.dumps(robots) if robots else "missing"))
        else:
            want = CANONICAL_ROOT + PAGES[slug]
            job.add("canonical", canon == [want], 'one canonical link, href="%s"' % want, "%d canonical link(s): %s" % (len(canon), json.dumps(canon)))
            job.add("robots-meta", not blocked, "no noindex on a real page", "robots meta: %s" % (json.dumps(robots) if robots else "none"))
    step(job, "title", head)

    # ---- relative-addresses
    def relative_addresses():
        bad = []
        for r in src_refs:
            v = r["value"].strip()
            if r["tag"] == "link" and ({"canonical", "alternate"} & set(r["rel"].split())):
                continue
            k = kind_src(r)
            where = '%s %s="%s" (line %d)' % (r["tag"], r["attr"], v[:120], r["line"])
            if v.startswith("//") or re.match(r"^https?:", v, re.I):
                if k in ("internal", "site-absolute"):
                    bad.append(where + ": absolute address of this site")
            elif v.startswith(("/", "\\")):
                bad.append(where + ": starts with a slash")
        bad = unique(bad)
        job.add("relative-addresses", not bad, "every internal address in the HTML source is relative (no leading slash, no absolute address of this site)",
                "%d address(es) in the source, %d not relative" % (len(src_refs), len(bad)), evidence={"not relative": short(bad, 15)})
    step(job, "relative-addresses", relative_addresses)

    # ---- no-inline-style
    def no_inline_style():
        styled = [show_tag(t) for t in src.tags if "style" in t["attrs"]]
        job.add("no-inline-style", not styled, "no style attribute in the HTML source", "%d style attribute(s)" % len(styled),
                evidence={"style attributes": short(styled), "style elements in the source (listed, not judged here)": len(src.all("style"))})
    step(job, "no-inline-style", no_inline_style)

    # ---- landmarks
    def landmarks():
        lm = dom["landmarks"]
        ok = len(lm["headers"]) >= 1 and len(lm["mains"]) == 1 and len(lm["footers"]) >= 1 and lm["order"]
        job.add("landmarks", ok, "a page header, exactly one main and a page footer, in that order",
                "%d header, %d main, %d footer%s" % (len(lm["headers"]), len(lm["mains"]), len(lm["footers"]),
                                                     "" if lm["order"] or not (lm["headers"] and lm["mains"] and lm["footers"]) else ", out of order"),
                evidence=lm)
    step(job, "landmarks", landmarks)

    # ---- ph-alt
    def ph_alt():
        names, replaced = shared["placeholders"], shared.get("replaced", ())
        bad, n = [], 0
        for i in dom["imgs"]:
            if i["lightbox"]:
                continue
            path = i["src"].split("?")[0].split("#")[0]
            name = os.path.splitext(path.rsplit("/", 1)[-1])[0]
            shown = re.search(r"images/(?:sm/)?[^/]+$", path)
            is_ph_file = name in names and not (shown and shown.group(0) in replaced)
            if i["ph"] or is_ph_file:
                n += 1
            if i["ph"] and i["alt"] != "":
                bad.append('%s src="%s" has class ph but alt is %s' % (i["where"], i["src"], json.dumps(i["alt"]) if i["alt"] is not None else "missing"))
            elif is_ph_file and not i["ph"]:
                bad.append('%s src="%s" shows a placeholder file without class ph (alt is %s)' % (i["where"], i["src"], json.dumps(i["alt"]) if i["alt"] is not None else "missing"))
        job.add("ph-alt", not bad, 'every placeholder image has class ph and alt=""', "%d placeholder image(s), %d wrong" % (n, len(bad)),
                evidence={"wrong": short(bad), "placeholder names taken from": shared["placeholders_from"]})
    step(job, "ph-alt", ph_alt)

    # ---- screenshot (our own site, so it belongs in qa/screenshots)
    def screenshot():
        path = os.path.join(shared["shots"], "%s-%s.png" % (slug, viewport))
        if os.path.isfile(path):
            os.remove(path)
        page.evaluate("() => window.scrollTo(0, 0)")
        try:    # a picture far down the page may be loaded but not decoded yet, and would be an empty box in the screenshot
            page.evaluate(JS_DECODE)
        except Exception:
            pass
        page.screenshot(path=path, full_page=True, animations="disabled")
        size = os.path.getsize(path) if os.path.isfile(path) else 0
        job.add("screenshot", size > 0, "a full-page screenshot is saved", "%d bytes" % size,
                evidence="qa/screenshots/%s-%s.png" % (slug, viewport), owner="QA")
    step(job, "screenshot", screenshot)

    # ---- skip-link (last, because pressing the link may leave the page)
    def skip_link():
        s = dom["skip"]
        problems = []
        if not s["exists"]:
            problems.append('no <a class="skip"> on the page')
        else:
            if not s["targetId"]:
                problems.append('the skip link href is %s, it names no target (the contract says "#main")' % json.dumps(s["href"]))
            elif not s["target"]:
                problems.append('the skip link points to "#%s" but no element on this page has that id' % s["targetId"])
            if not s["firstIsSkip"]:
                problems.append("the first focusable element in the page is %s, not the skip link" % (s["firstFocusable"] or "nothing"))
            if not tab["isSkip"]:
                problems.append("the first press of Tab lands on %s, not on the skip link" % (tab["what"] or "nothing"))
        stays = None
        if s["exists"]:
            try:
                stays, landed = press_skip(page)
                if not stays:
                    problems.append("pressing the skip link leaves the page: it goes to %s instead of the main content of this page" % rel(landed))
            except Exception as e:
                problems.append("the skip link could not be pressed: " + first_line(e))
        job.add("skip-link", not problems, "the skip link is the first focusable element, its target exists and pressing it stays on the page",
                "; ".join(problems) if problems else 'first Tab lands on a.skip, href "%s" leads to %s' % (s["href"], s["target"]),
                evidence={"skip link href": s["href"], "target": s["target"], "first focusable": s["firstFocusable"], "first Tab lands on": tab["what"],
                          "href resolves to this page": s["samePage"], "stays on the page when pressed": stays,
                          "elements with a positive tabindex": s["positiveTabindex"]})
    step(job, "skip-link", skip_link)

    # ---- 404 page shown for a deep broken address
    if slug == "404":
        step(job, "404-deep-address", lambda: deep_404(ctx, base, job, shared))
    return None


def press_skip(page):
    """Focus the skip link and press Enter. Returns (the browser stayed on the same page, the address it is on now).
    A <base> element makes href="#main" point to another page, and only pressing the link shows that."""
    before = page.url
    page.evaluate("() => document.querySelector('a.skip').focus()")
    page.keyboard.press("Enter")
    try:
        page.wait_for_url(lambda u: u != before, wait_until="commit", timeout=3000)
    except Exception:
        pass
    return urldefrag(page.url)[0] == urldefrag(before)[0], page.url


def deep_404(ctx, base, job, shared):
    """The 404 page is what a visitor gets for ANY broken address, also one inside a folder that does not exist."""
    adr, fetch = shared["adr"], shared["fetch"]
    rel = adr.rel
    log = {}
    page = ctx.new_page()
    page.set_default_timeout(15000)
    common.watch(page, log)
    url = base + DEEP_404
    try:
        resp = page.goto(url, wait_until="load", timeout=45000)
        status = resp.status if resp else 0
        try:
            page.evaluate(JS_FONTS)
        except Exception:
            pass
        info = page.evaluate(JS_DEEP, adr.origin)
        doc_url = urldefrag(page.url)[0]
        problems = []
        if status != 404:
            problems.append("a broken address answers status %s, not 404" % status)
        good_sheets = [s for s in info["sheets"] if s["rules"] > 0]
        if not good_sheets:
            problems.append("the stylesheet did not load (%s)" % (", ".join(rel(s["href"]) for s in info["sheets"]) or "no stylesheet link of the site"))
        # A browser reads ahead and may ask for css, js and images next to the broken address before the page has set its
        # base address. Those wasted requests answer 404 and are only listed: what counts is what the visitor ends up with.
        early = unique(rel(b["url"]) for b in log.get("bad_status", []) if urldefrag(b["url"])[0] != doc_url)
        job.flaky += ["%s %s" % (rel(f["url"]), f.get("error")) for f in log.get("failed", [])
                      if adr.kind(f["url"], doc_url) == "internal" and TRANSPORT.search(str(f.get("error") or ""))]
        broken_imgs = [rel(i["src"]) for i in info["imgs"] if not i["ok"] and not i["waiting"]]
        if broken_imgs:
            problems.append("%d image(s) did not load" % len(broken_imgs))
        broken_links = []
        for link in info["links"]:
            if adr.kind(link["url"], doc_url, link["url"]) != "internal" or urldefrag(link["url"])[0] == doc_url:
                continue
            got = fetch.get(link["url"])
            if not got["status"]:
                job.flaky.append("%s %s" % (rel(link["url"]), got["error"]))
            if got["status"] != 200:
                broken_links.append({"address": rel(urldefrag(link["url"])[0]), "status": got["status"] or got["error"],
                                     "found in": '%s "%s"' % (link["where"], link["value"])})
        broken_links = unique(broken_links)
        if broken_links:
            problems.append("%d link(s) or file(s) lead nowhere" % len(broken_links))
        if not info["h1"]:
            problems.append("no h1 on the page that came back")
        stays = None
        if info["skip"] is not None:
            try:
                stays, landed = press_skip(page)
                if not stays:
                    problems.append("pressing the skip link leaves the page: it goes to %s instead of the main content of this page" % rel(landed))
            except Exception as e:
                problems.append("the skip link could not be pressed: " + first_line(e))
        job.add("404-deep-address", not problems,
                "for a broken address inside a folder the 404 page answers 404 and still finds its stylesheet, script, images and links",
                "; ".join(problems) if problems else "status 404, stylesheet loaded, %d links and files checked" % len(info["links"]),
                evidence={"tested address": DEEP_404, "title": info["title"], "stylesheets": [{"file": rel(s["href"]), "rules": s["rules"]} for s in info["sheets"]],
                          "images not loaded": short(broken_imgs), "links that lead nowhere": short(broken_links),
                          "requests that answered 404 before the page had set its base address (listed, not judged)": short(early, 6),
                          "skip link stays on the page when pressed": stays})
    finally:
        try:
            page.close()
        except Exception:
            pass


# ---------------------------------------------------------------- running everything

def worker(base, jobs, results, flaky, shared, problems, attempts=3):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                while True:
                    try:
                        slug, viewport = jobs.get_nowait()
                    except queue.Empty:
                        break
                    entries, lost, tries = run_job(p, browser, base, slug, viewport, shared, attempts)
                    results[(slug, viewport)], flaky[(slug, viewport)] = entries, lost
                    if tries > 1:
                        shared["retried"]["%s %s" % (slug, viewport)] = shared["retried"].get("%s %s" % (slug, viewport), 0) + tries
            finally:
                browser.close()
    except Exception as e:
        problems.append("%s: %s" % (type(e).__name__, first_line(e)))


def prepare(base, shots):
    """Things every page needs: the address sorter, the request cache, BOOKING_URL and the placeholder names."""
    fetch = Fetcher(base)
    booking = None
    alive = fetch.get(base)
    if not alive["status"]:                # nothing answers: run() reports that, do not wait for the other files
        return {"adr": Addresses(base), "fetch": fetch, "booking_url": None, "placeholders": set(PLACEHOLDER_NAMES),
                "placeholders_from": "not read", "shots": shots, "retried": {}, "dead": alive["error"] or "no answer"}
    got = fetch.get(base + "js/site.js")
    if got["status"] == 200:
        m = re.search(r"""^\s*var\s+BOOKING_URL\s*=\s*(["'])(.*?)\1\s*;""", got["text"], re.M)
        if m:
            booking = m.group(2).strip()
    names, source = set(PLACEHOLDER_NAMES), "the built-in list of 26 names (image-manifest.json could not be read)"
    replaced = set()
    got = fetch.get(base + "image-manifest.json")
    if got["status"] == 200:
        try:
            images = json.loads(got["text"]).get("images", {})
            listed = {n for n, v in images.items() if isinstance(v, dict) and v.get("status") == "placeholder"}
            if images:
                names, source = listed, "image-manifest.json (%d placeholders)" % len(listed)
                replaced = replaced_files(fetch, base, [images[n] for n in sorted(listed)])
                if replaced:
                    source += ("; %s no longer the recorded placeholder (other SHA-256) and not treated as one here: %s"
                               % ("1 of their files is" if len(replaced) == 1 else "%d of their files are" % len(replaced), ", ".join(sorted(replaced)[:8])))
        except Exception:
            pass
    return {"adr": Addresses(base), "fetch": fetch, "booking_url": booking, "placeholders": names, "replaced": replaced,
            "placeholders_from": source, "shots": shots, "retried": {}}


def replaced_files(fetch, base, records):
    """The image files that the manifest records as placeholders but that are another file by now: the owner saved a
    photo over the placeholder and the manifest was not brought up to date (the generator does that when it builds
    the pages, build contract decision 27). Such a file is a photo with a description, not a placeholder that needs
    class ph and alt "". Compared by SHA-256 with what the server serves. A file that cannot be read, or an entry
    without a hash, stays a placeholder. -> set of paths like images/g05.jpg and images/sm/g05.jpg"""
    out = set()
    for record in records:
        for part in (record, record.get("sm")):
            if not isinstance(part, dict) or not isinstance(part.get("file"), str) or not isinstance(part.get("sha256"), str):
                continue
            rel = part["file"].replace("\\", "/").lstrip("/")
            if not re.fullmatch(r"images/(?:sm/)?[^/]+", rel):
                continue
            got = fetch.get(base + rel)
            if got["status"] == 200 and got.get("sha256") and got["sha256"] != part["sha256"].lower():
                out.add(rel)
    return out


def run(base, slugs, viewports, shots, jobs_n):
    shared = prepare(base, shots)
    todo = [(s, v) for s in slugs for v in viewports]
    shared["unreliable"], shared["checked twice"] = [], []
    if shared.get("dead"):             # nothing answers at all: say so once instead of trying every page three times
        reason = "nothing answers at the address under test (%s)" % shared["dead"]
        shared["unreliable"] = ["%s %s" % item for item in todo]
        return scrub([e for s, v in todo for e in Job(s, v).finish(reason, "QA")]), shared
    jobs = queue.Queue()
    for item in todo:
        jobs.put(item)
    results, flaky, problems = {}, {}, []
    n = max(1, min(jobs_n, len(todo)))
    if n == 1:
        worker(base, jobs, results, flaky, shared, problems)
    else:
        threads = [threading.Thread(target=worker, args=(base, jobs, results, flaky, shared, problems), daemon=True) for _ in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        if not jobs.empty():           # a browser did not start: finish the rest in this thread
            worker(base, jobs, results, flaky, shared, problems)
    # pages that kept losing the connection while several browsers worked at once get one more quiet turn, one at a time
    again = [item for item in todo if flaky.get(item)]
    if again and n > 1:
        for item in again:
            jobs.put(item)
        worker(base, jobs, results, flaky, shared, problems)
    out = []
    for slug, viewport in todo:
        entries = results.get((slug, viewport))
        if entries is None:
            entries = Job(slug, viewport).finish("the browser did not start (%s)" % ("; ".join(problems) or "unknown reason"), "QA")
        out.extend(entries)
    shared["unreliable"] = ["%s %s" % item for item in todo if flaky.get(item)]
    shared["checked twice"] = ["%s %s" % item for item in again]
    return scrub(out), shared


def main():
    ap = common.cli_parser("Page health check for every page at desktop and phone size.")
    ap.add_argument("--jobs", type=int, default=4, help="how many browsers work at the same time (default 4)")
    ap.add_argument("--root", help="self-test only: serve this folder instead of the site")
    ap.add_argument("--out", help="self-test only: write the report and the screenshots into this folder")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    slugs = common.cli_pages(ap, args.page)
    viewports = common.parse_viewports(args.viewport)

    out = args.out
    if args.root and not out:
        out = os.path.join(common.ENV, "stage", "qa", NAME, "out")
    shots = common.SHOTS
    if out:
        out = os.path.abspath(out)
        common.REPORTS = os.path.join(out, "reports")
        shots = os.path.join(out, "screenshots")
    os.makedirs(shots, exist_ok=True)

    started = time.time()
    server = common.site_server(root=os.path.abspath(args.root)) if args.root else common.target_base(args.base)
    with server as base:
        results, shared = run(base, slugs, viewports, shots, args.jobs)
        tested = "self-test copy" if args.root else common.report_base(args.base)
    doc = common.save_report(NAME, results, tested, extra={"script": "qa/%s.py" % NAME, NAME: {
        "last run": {"pages": slugs, "viewports": viewports, "seconds": round(time.time() - started, 1),
                     "BOOKING_URL": shared["booking_url"], "placeholder names from": shared["placeholders_from"],
                     "attempts where the connection failed at first (page viewport: attempts)": shared["retried"],
                     "checked again one at a time after connection errors": shared["checked twice"],
                     "connection still failing, results not reliable": shared["unreliable"]},
        "checks": CHECKS + CHECKS_404}})

    failed = [r for r in results if not r["ok"]]
    for r in failed:
        line = "FAIL %s %s %s [%s] expected: %s | actual: %s" % (r["page"], r["viewport"], r["check"], r["owner"], r["expected"], r["actual"])
        print(line if len(line) <= 420 else line[:417] + "...")
    if shared["unreliable"]:
        print("check_page: the connection to the server kept failing for %s. Those results are not reliable, run the check again."
              % ", ".join(shared["unreliable"]))
    where = "qa/reports/%s.json" % NAME if not out else scrub(os.path.join(common.REPORTS, NAME + ".json"))
    print("check_page: %d checks on %d page(s) x %d viewport(s), %d passed, %d failed%s. Report: %s"
          % (len(results), len(slugs), len(viewports), len(results) - len(failed), len(failed),
             "" if doc["ok"] or failed else " (the report still holds older failures of pages not run this time)", where))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
