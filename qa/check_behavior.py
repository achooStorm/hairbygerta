"""Behaviour tests on the real pages.

What is tested:
  phone menu, gallery photo viewer (lightbox), Book Now buttons, contact form, the Call button and the Text link
  and the one motion of the home page, the footer year, the site with JavaScript switched off, broken addresses
  and old Wix addresses.

Run it with the Python of the tools folder (it has Playwright), from anywhere:

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_behavior.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_behavior.py --page gallery,contact --viewport phone
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_behavior.py --base https://achoostorm.github.io/hairbygerta/

  --base URL        test that address instead of a local server
  --page SLUGS      all (default) or a list such as home,gallery,404
  --viewport NAME   desktop, phone or both (default both)
  --jobs N          how many browsers work side by side (default 4, use 1 to debug)
  --timing          also print the seconds each test took

Which page slug carries which tests:
  every page    menu, footer year, the navigation without JavaScript
  home          the reveal of the hero photos (the one motion of the site), the Call button and the Text link,
                footer year with another clock. The scrolling hours line and the Book Online button were tested here
                until the redesign of 12 November 2026 removed them (build contract, decisions 44 and 45).
  gallery       photo viewer, gallery links without JavaScript
  book-online   Book Now buttons, with and without a booking link, and without JavaScript
  contact       contact form, with and without JavaScript
  404           a broken address shows the styled 404 page, old Wix booking addresses end on Book Online.
                Run twice on a local run: with the site under /hairbygerta/ (the GitHub Pages address) and with the
                site at the top of the host (www.hairbygerta.com), check names of the second start with
                "site at the top of the host:"

The report goes to qa/reports/check_behavior.json. One line is printed per failed check, then a summary.
Exit code 0 when everything passed, 1 otherwise.

The tests follow the build contract (tools/CONTRACT.md, sections 6 to 8): class names, attributes and
behaviour are taken from there, not from what a page happens to do today.
"""
import contextlib, datetime, os, queue, re, sys, threading, time
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True   # no __pycache__ in the site folder (a compiled file carries the path of this computer)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

NAME = "check_behavior"
TEL = "tel:" + common.PHONE
MAILTO = "mailto:" + common.EMAIL
# The third item is called Services since the redesign of 12 November 2026 (Book Online until then), its address stays.
NAV = [("Home", "home"), ("Gallery", "gallery"), ("Services", "book-online"), ("About", "about"), ("Contact", "contact")]
TEST_BOOKING_URL = "https://example.com/book"
BROKEN = "nope/deeper/"
OLD_ADDRESSES = ["booking-calendar/balayage", "service-page/hair-coloring"]
ACTION_MS = 8000      # longest wait for one click, tap or key
STATE_MS = 5000       # longest wait for the page to show the result of a click, tap or key
# The waits are long on purpose: they end as soon as the expected state is there, and a busy computer must not turn into a failed check.
NAV_MS = 30000        # longest wait for one page load
REVEAL_MS = (500, 700)                  # the reveal of the hero photos takes about 600 ms (design brief, decision 45)
SMS = "sms:+13476715095"                # the Text link: the digits of the phone number (decision 45)
SENDER = {"first": "Maria", "last": "Rossi", "email": "maria.rossi@example.com",
          "message": "Hello Gerta,\nI would like a balayage & cut for 2 people on 5/12 at 10 AM (#1 choice).\n"
                     "Is that possible? I am 100% flexible + can come earlier. Grazie, caf\u00e9 later!"}


class Stop(Exception):
    """Raised inside a test when the checks that follow cannot be done. The text says why,
    owner says who has to fix the cause (the checks that were not reached are listed under that owner)."""

    def __init__(self, reason, owner=None):
        super().__init__(reason)
        self.owner = owner


# ----------------------------------------------------------------------------- small helpers

def brief(exc):
    if isinstance(exc, Stop):
        return str(exc)
    first = (str(exc).strip().splitlines() or [""])[0]
    return (type(exc).__name__ + ": " + first)[:300]


def norm_url(url):
    """Address without query and fragment, and without a trailing index.html."""
    s = urlsplit(url or "")
    path = s.path
    if path.endswith("/index.html"):
        path = path[:-len("index.html")]
    return f"{s.scheme}://{s.netloc}{path}"


def one_line(text, limit=400):
    text = re.sub(r"\s+", " ", str(text)).strip()
    return text if len(text) <= limit else text[:limit - 3] + "..."


def poll(page, read, good, timeout_ms=STATE_MS, step_ms=100, default=None):
    """Read a value again and again until good(value) is true or the time is up. Returns the last value."""
    end = time.monotonic() + timeout_ms / 1000
    value = default
    while True:
        try:
            value = read()
        except Exception:
            pass                   # for example: the page is just moving to another address. Keep the last value read.
        try:
            ok = bool(good(value))
        except Exception:
            ok = False
        if ok or time.monotonic() >= end:
            return value
        page.wait_for_timeout(step_ms)


def press(vp, target, **kw):
    """A finger tap on the phone, a mouse click on the desktop."""
    if vp == "phone":
        target.tap(**kw)
    else:
        target.click(**kw)


def shot(page, name):
    """Screenshot of our own site into qa/screenshots. Never stops a test."""
    try:
        os.makedirs(common.SHOTS, exist_ok=True)
        page.wait_for_timeout(350)      # let a fade or a button animation finish, so the picture shows the end state
        page.screenshot(path=os.path.join(common.SHOTS, name))
        return "qa/screenshots/" + name
    except Exception:
        return ""


class Checks:
    """The entries of one test on one page in one viewport.
    Every planned check ends up in the report, also when the test has to stop early,
    so the report always holds the same set of entries."""

    def __init__(self, page, viewport, plan):
        self.page, self.viewport = page, viewport
        self.plan = {name: (owner, expected) for name, owner, expected in plan}
        self.entries = []
        self.done = set()

    def put(self, check, ok, actual, expected=None, evidence="", owner=None):
        plan_owner, plan_expected = self.plan.get(check, ("PAGES", ""))
        entry = {"page": self.page, "viewport": self.viewport, "check": check, "ok": bool(ok),
                 "expected": plan_expected if expected is None else expected, "actual": actual,
                 "evidence": evidence, "owner": owner or plan_owner}
        if check in self.done:          # a later, worse result for the same check replaces the earlier one
            self.entries = [entry if e["check"] == check else e for e in self.entries]
        else:
            self.done.add(check)
            self.entries.append(entry)
        return bool(ok)

    def finish(self, reason, owner=None):
        for check in self.plan:
            if check not in self.done:
                self.put(check, False, "not checked: " + reason, owner=owner)


class Env:
    """What one worker has: its Playwright, its browser, the address of the site, and its open pages."""

    def __init__(self, p, browser, base, shared):
        self.p, self.browser, self.base, self.shared = p, browser, base, shared
        self.local = (urlsplit(base).hostname or "") in ("127.0.0.1", "localhost", "::1")   # the local test server
        self.year = shared["year"]
        self.trouble = False        # set when a request to the site failed on the way (see connection_trouble)
        self.pages = {}             # (viewport, fonts allowed, context options) -> (context, page, log)

    def url(self, slug):
        return self.base + common.PAGES[slug]

    def discard(self, key):
        held = self.pages.pop(key, None)
        if held:
            with contextlib.suppress(Exception):
                held[0].close()

    def close(self):
        for key in list(self.pages):
            self.discard(key)


def new_context(env, vp, allow_fonts=False, **context_kwargs):
    """A browser context with the network guard and the console watcher. -> (context, page, log)"""
    opts = common.context_options(env.p, vp, dsf=1 if vp == "phone" else None)
    opts.update(context_kwargs)
    ctx = env.browser.new_context(**opts)
    ctx.set_default_timeout(ACTION_MS)
    ctx.set_default_navigation_timeout(NAV_MS)
    log = {}
    common.guard(ctx, log, env.base, allow_fonts=allow_fonts)
    if env.local:
        steady_local_server(ctx, env)
    page = ctx.new_page()
    common.watch(page, log)
    return ctx, page, log


BUSY_SERVER = ("ECONNREFUSED", "ECONNRESET", "ECONNABORTED", "EPIPE", "socket hang up")


def fetch_patiently(fetch):
    """Call fetch() and, when the connection is refused or dropped, try again a few times.
    The local test server (qa/serve.py) takes only a handful of waiting connections at a time and turns the
    rest away when the computer is busy. That is a limit of the test server, not a fault of the site."""
    for pause in (0, 0.1, 0.2, 0.4, 0.8):
        if pause:
            time.sleep(pause)
        try:
            return fetch()
        except Exception as exc:
            if not any(word in str(exc) for word in BUSY_SERVER):
                raise
            last = exc
    raise last


def steady_local_server(ctx, env):
    """Local server only: requests to the site go through fetch_patiently, so a connection that the busy test
    server turned away is asked for again instead of showing up as a broken image or a missing script.
    Requests to any other host fall through to the network guard of common.py. Redirects are passed on as they are."""
    own = urlsplit(env.base).netloc

    def handle(route):
        try:
            if urlsplit(route.request.url).netloc != own:
                route.fallback()
                return
            response = fetch_patiently(lambda: route.fetch(max_redirects=0))
            route.fulfill(response=response)
        except Exception:
            with contextlib.suppress(Exception):
                route.fallback()        # the browser asks itself: a server that is really down still shows as an error
    ctx.route("**/*", handle)


def held_page(env, vp, allow_fonts=False, **context_kwargs):
    """The worker's page for this viewport and these options. It is kept open between tests, because opening
    a page costs seconds. Every test starts from an empty page and an empty log. -> (key, context, page, log)"""
    key = (vp, allow_fonts, tuple(sorted(context_kwargs.items())))
    held = env.pages.get(key)
    if held and held[1].is_closed():
        env.discard(key)
        held = None
    if not held:
        held = env.pages[key] = new_context(env, vp, allow_fonts, **context_kwargs)
    ctx, page, log = held
    try:
        page.goto("about:blank")
        if vp != "phone":
            page.mouse.move(1, 1)
    except Exception:
        env.discard(key)
        ctx, page, log = env.pages[key] = new_context(env, vp, allow_fonts, **context_kwargs)
    log.clear()
    return key, ctx, page, log


def run_test(env, ck, vp, body, clean_check=None, allow_fonts=False, **context_kwargs):
    """Take the worker's page, run body(ctx, page, log), add the 'clean run' entry, fill in what was not reached."""
    reason = "an earlier step of this test failed"
    key = cause_owner = None
    try:
        key, ctx, page, log = held_page(env, vp, allow_fonts, **context_kwargs)
        try:
            body(ctx, page, log)
        except Stop as exc:
            reason = "the test stopped: " + brief(exc)
            cause_owner = exc.owner
        except Exception as exc:
            reason = "the test stopped: " + brief(exc)
            env.discard(key)        # the page may be in an unknown state: the next test gets a new one
        if connection_trouble(log, env.base):
            env.trouble = True
        if clean_check:
            put_clean(env, ck, clean_check, log)
    except Exception as exc:
        reason = "the test stopped: " + brief(exc)
        if key:
            env.discard(key)
    if any(word in reason for word in CONNECTION_ERRORS):
        env.trouble = True
    ck.finish(reason, cause_owner)
    return ck.entries


CONNECTION_ERRORS = ("ERR_CONNECTION_REFUSED", "ERR_CONNECTION_RESET", "ERR_CONNECTION_ABORTED", "ERR_CONNECTION_CLOSED",
                     "ERR_EMPTY_RESPONSE", "ERR_TIMED_OUT", "ERR_NETWORK_CHANGED", "ERR_INTERNET_DISCONNECTED")


def connection_trouble(log, base):
    """True when a request to the site itself failed on the way (server too busy, network gone).
    That says nothing about the site, so the test is run once more before its result counts."""
    own = urlsplit(base).hostname
    return any(urlsplit(item.get("url", "")).hostname == own and any(word in str(item.get("error")) for word in CONNECTION_ERRORS)
               for item in log.get("failed", []))


def put_clean(env, ck, check, log):
    """One entry for script errors and broken requests seen during a test.
    Blocked requests to Google Maps are expected: listed as evidence, not failures. (The fonts are files of the site
    itself since decision 38, so a request to Google Fonts would be a failure like any other unexpected host.)"""
    problems, owner = [], "PAGES"
    for text in log.get("pageerrors", []):
        problems.append("script error: " + one_line(text, 200))
        owner = "INTERACTION"
    blocked = log.get("blocked", [])
    for url in common.unexpected_blocked(log):
        problems.append("request to another site (blocked): " + url)
    for item in log.get("failed", []):
        url, err = item.get("url", ""), str(item.get("error"))
        # ERR_ABORTED = the browser itself dropped the request (a click moved on, the viewer changed photo)
        if "ERR_ABORTED" in err or url in blocked or common.is_expected_external(url):
            continue
        problems.append(f"failed request: {url} ({err})")
    for item in log.get("bad_status", []):
        problems.append(f"{item['status']} for {item['url']}")
        if "/images/" in item["url"] and owner == "PAGES":
            owner = "ASSETS"
    for item in log.get("console", []):
        # "Failed to load resource" repeats a blocked, failed or 4xx request that is already counted above
        if item["type"] == "error" and not item["text"].startswith("Failed to load resource"):
            problems.append("console error: " + one_line(item["text"], 200))
            owner = "INTERACTION"
    planned = sorted({urlsplit(u).hostname or "" for u in blocked if common.is_expected_external(u)})
    env.shared["blocked_expected"].update(u for u in blocked if common.is_expected_external(u))
    evidence = ("blocked as planned: " + ", ".join(planned)) if planned else ""
    ck.put(check, not problems, "clean" if not problems else "; ".join(problems[:8]) +
           (f" (and {len(problems) - 8} more)" if len(problems) > 8 else ""), evidence=evidence, owner=owner)


# ----------------------------------------------------------------------------- scripts run inside the page

JS_D = r"""const D = (el) => !el ? 'nothing' : el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
  (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).join('.') : '');"""

# For every element that matches: is it drawn, inside the screen, and on top (not covered)?
JS_VIS = r"""([sel, scroll]) => {
  /*D*/
  return Array.from(document.querySelectorAll(sel)).map((el) => {
    if (scroll) el.scrollIntoView({block: 'center', inline: 'nearest'});
    const vw = window.innerWidth, vh = window.innerHeight;
    const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
    const rendered = el.getClientRects().length > 0 && r.width >= 1 && r.height >= 1 && cs.visibility === 'visible' &&
      (typeof el.checkVisibility !== 'function' || el.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}));
    const inX = r.left >= -1 && r.right <= vw + 1;
    const inView = inX && r.top >= -1 && r.bottom <= vh + 1;
    let hit = false, cover = '';
    if (rendered) {
      const cx = r.left + r.width / 2, cy = r.top + r.height / 2;
      if (cx >= 0 && cy >= 0 && cx < vw && cy < vh) {
        const top = document.elementFromPoint(cx, cy);
        const label = top && top.closest ? top.closest('label') : null;
        hit = !!top && (top === el || el.contains(top) || (!!label && label.control === el));   // its own label on top is fine
        if (!hit) cover = D(top);
      }
    }
    return {text: (el.textContent || '').replace(/\s+/g, ' ').trim(), href: el.href || '', attr: el.getAttribute('href'),
            rendered, inX, inView, hit, cover, box: [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]};
  });
}""".replace("/*D*/", JS_D)

JS_MENU = r"""() => {
  /*D*/
  const btn = document.querySelector('.menu-btn'), nav = document.getElementById('main-nav');
  return {btn: !!btn, nav: !!nav, expanded: btn ? btn.getAttribute('aria-expanded') : null,
          navOpen: !!nav && nav.classList.contains('open'), bodyOpen: document.body.classList.contains('menu-open'),
          focusOnBtn: !!btn && document.activeElement === btn, active: D(document.activeElement)};
}""".replace("/*D*/", JS_D)

MENU_UNKNOWN = {"btn": False, "nav": False, "expanded": None, "navOpen": False, "bodyOpen": False, "focusOnBtn": False, "active": "nothing"}

JS_YEAR = r"""() => ({spots: Array.from(document.querySelectorAll('[data-year]')).map((e) => e.textContent.trim()),
                    clock: new Date().getFullYear()})"""

JS_GALLERY = r"""() => Array.from(document.querySelectorAll('.gallery a')).map((a) => {
  const i = a.querySelector('img');
  return {href: a.href, attr: a.getAttribute('href'), alt: i ? (i.getAttribute('alt') || '') : '', thumb: i ? i.src : '', hasImg: !!i};
})"""

JS_LB = r"""() => {
  /*D*/
  const boxes = document.querySelectorAll('.lightbox'), box = boxes[0];
  const links = Array.from(document.querySelectorAll('.gallery a'));
  const a = document.activeElement;
  const out = {boxes: boxes.length, bodyOpen: document.body.classList.contains('lightbox-open'), active: D(a),
               activeLink: links.indexOf(a), url: location.href, open: false, onTop: false, focusInside: false,
               src: null, alt: null, count: null, complete: false, natural: 0, parts: {}};
  if (!box) return out;
  const img = box.querySelector('img.lb-img'), cnt = box.querySelector('.lb-count');
  const c = document.elementFromPoint(window.innerWidth / 2, window.innerHeight / 2);
  const n = (s) => box.querySelectorAll(s).length;
  return Object.assign(out, {open: box.classList.contains('open'), onTop: !!c && box.contains(c),
    role: box.getAttribute('role'), modal: box.getAttribute('aria-modal'), label: box.getAttribute('aria-label'),
    parts: {'button.lb-close': n('button.lb-close'), 'button.lb-prev': n('button.lb-prev'), 'img.lb-img': n('img.lb-img'),
            'button.lb-next': n('button.lb-next'), 'p.lb-count': n('p.lb-count')},
    src: img ? img.src : null, alt: img ? img.getAttribute('alt') : null, complete: !!img && img.complete,
    natural: img ? img.naturalWidth : 0, count: cnt ? cnt.textContent.replace(/\s+/g, ' ').trim() : null,
    focusInside: !!a && a !== document.body && box.contains(a)});
}""".replace("/*D*/", JS_D)

# A point of the dark layer itself (not the photo, not a button), as far from photo and buttons as possible.
JS_BACKDROP = r"""() => {
  const box = document.querySelector('.lightbox');
  if (!box) return null;
  const vw = window.innerWidth, vh = window.innerHeight;
  const kids = Array.from(box.querySelectorAll('img, button')).map((k) => k.getBoundingClientRect()).filter((r) => r.width > 0 && r.height > 0);
  let best = null;
  for (let iy = 0; iy <= 24; iy++) for (let ix = 0; ix <= 24; ix++) {
    const x = Math.round(6 + ix * (vw - 13) / 24), y = Math.round(6 + iy * (vh - 13) / 24);
    if (document.elementFromPoint(x, y) !== box) continue;
    let d = 1e9;
    for (const r of kids) d = Math.min(d, Math.hypot(Math.max(r.left - x, 0, x - r.right), Math.max(r.top - y, 0, y - r.bottom)));
    if (!best || d > best.d) best = {x, y, d: Math.round(d)};
  }
  return best;
}"""

JS_BOOK = r"""() => ({
  pills: Array.from(document.querySelectorAll('a.pill[data-book]')).map((a) => ({href: a.getAttribute('href'),
    target: a.getAttribute('target'), rel: a.getAttribute('rel'), text: a.textContent.replace(/\s+/g, ' ').trim()})),
  marked: document.querySelectorAll('[data-book]').length})"""

JS_HOME_LINKS = r"""() => ({
  call: Array.from(document.querySelectorAll('.hero a.btn-call')).map((a) => ({attr: a.getAttribute('href'),
    target: a.getAttribute('target'), book: a.hasAttribute('data-book'), text: a.textContent.replace(/\s+/g, ' ').trim()})),
  text: Array.from(document.querySelectorAll('.hero a.text-link')).map((a) => ({attr: a.getAttribute('href'),
    target: a.getAttribute('target'), book: a.hasAttribute('data-book'), text: a.textContent.replace(/\s+/g, ' ').trim()})),
  marked: document.querySelectorAll('[data-book]').length})"""

# Watches every way a page can open a mail link, and stops it so that no mail program starts:
#  - a click on an a element (capture-phase listener on window, and on the a element itself when the script
#    clicks one that is not in the page)
#  - a change of address to mailto: (location, a form sent to mailto:), through the Navigation API
#  - window.open
JS_MAIL_HOOK = r"""(() => {
  if (window.__qaMail) return;
  const rec = window.__qaMail = {clicks: [], navs: [], opens: [], known: new WeakSet(), last: null};
  const seen = new WeakSet();
  const isMail = (a) => /^\s*mailto:/i.test(a.getAttribute('href') || '');
  function note(a, e, how) {
    if (seen.has(e)) return;
    seen.add(e);
    rec.clicks.push({href: a.getAttribute('href'), how, attached: a.isConnected, existedBefore: rec.known.has(a)});
    rec.last = a;
    e.preventDefault();
  }
  window.addEventListener('click', (e) => {
    const a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (a && isMail(a)) note(a, e, 'capture listener on window');
  }, true);
  function withListener(a, run) {
    const h = (e) => note(a, e, 'capture listener on the a element');
    a.addEventListener('click', h, true);
    try { return run(); } finally { a.removeEventListener('click', h, true); }
  }
  const click = HTMLElement.prototype.click;
  HTMLElement.prototype.click = function () {
    const self = this, args = arguments;
    if (self instanceof HTMLAnchorElement && isMail(self)) return withListener(self, () => click.apply(self, args));
    return click.apply(self, args);
  };
  const dispatch = EventTarget.prototype.dispatchEvent;
  EventTarget.prototype.dispatchEvent = function (ev) {
    const self = this;
    if (ev && ev.type === 'click' && self instanceof HTMLAnchorElement && isMail(self)) return withListener(self, () => dispatch.call(self, ev));
    return dispatch.call(self, ev);
  };
  if (window.navigation && navigation.addEventListener) navigation.addEventListener('navigate', (e) => {
    const url = (e.destination && e.destination.url) || '';
    if (/^mailto:/i.test(url)) { rec.navs.push({url, form: !!e.formData}); if (e.cancelable) e.preventDefault(); }
  });
  const open = window.open;
  window.open = function (url) {
    if (/^\s*mailto:/i.test(String(url || ''))) { rec.opens.push(String(url)); return null; }
    return open.apply(window, arguments);
  };
  rec.arm = () => { rec.clicks.length = 0; rec.navs.length = 0; rec.opens.length = 0; rec.last = null;
                    rec.known = new WeakSet(document.querySelectorAll('a')); return true; };
  rec.read = () => ({clicks: rec.clicks.slice(), navs: rec.navs.slice(), opens: rec.opens.slice(),
    lastStillInPage: rec.last ? rec.last.isConnected : null,
    leftovers: Array.from(document.querySelectorAll('a')).filter((a) => !rec.known.has(a)).length});
})()"""

JS_FORM = r"""() => {
  const f = document.getElementById('contact-form');
  if (!f) return {form: false};
  const e = document.getElementById('email'), note = document.querySelector('.form-note');
  const err = document.getElementById('email-error');
  const has = (s) => !!f.querySelector(s);
  const shown = (el) => { if (!el || el.hidden) return false; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0; };
  return {form: true, action: f.getAttribute('action'), method: f.getAttribute('method'), enctype: f.getAttribute('enctype'),
    mailto: f.getAttribute('data-mailto'), sent: f.getAttribute('data-sent'), novalidate: f.noValidate,
    error: err ? {shown: shown(err), text: err.textContent.replace(/\s+/g, ' ').trim(), missing: err.getAttribute('data-missing'),
                  invalid: err.getAttribute('data-invalid')} : null,
    ariaInvalid: e ? e.getAttribute('aria-invalid') : null, describedBy: e ? e.getAttribute('aria-describedby') : null,
    focused: e ? document.activeElement === e : null,
    missing: ['#first-name', '#last-name', '#email', '#message', 'button[type=submit]'].filter((s) => !has(s)).concat(note ? [] : ['.form-note']),
    emailType: e ? e.getAttribute('type') : null, emailRequired: e ? e.required : null,
    emailValue: e ? e.value : null,
    validity: e ? {valid: e.validity.valid, valueMissing: e.validity.valueMissing, typeMismatch: e.validity.typeMismatch} : null,
    note: note ? note.textContent.replace(/\s+/g, ' ').trim() : null, url: location.href};
}"""

# The animations of the home page: the reveal of the hero photos and anything else that moves.
JS_REVEAL = r"""() => {
  const box = document.querySelector('.hero-photos');
  const all = document.getAnimations().map((a) => ({name: a.animationName || a.constructor.name, state: a.playState,
    target: a.effect && a.effect.target ? (a.effect.target.className || a.effect.target.tagName) : ''}));
  if (!box) return {box: false, all};
  const cs = getComputedStyle(box);
  const own = box.getAnimations()[0];
  const frames = own && own.effect ? own.effect.getKeyframes().map((k) => k.clipPath || '') : [];
  return {box: true, all, name: cs.animationName, duration: cs.animationDuration, count: cs.animationIterationCount,
          clip: cs.clipPath, frames, photos: box.querySelectorAll('img').length};
}"""

JS_404 = r"""() => {
  const nf = document.querySelector('div.notfound'), btn = document.querySelector('.notfound a.btn');
  const logo = document.querySelector('.site-header .logo img');
  const rules = (s) => { try { return s.cssRules.length; } catch (e) { return -1; } };
  return {notfound: document.querySelectorAll('div.notfound').length,
    h1: nf && nf.querySelector('h1') ? nf.querySelector('h1').textContent.replace(/\s+/g, ' ').trim() : null,
    btn: btn ? {href: btn.href, attr: btn.getAttribute('href'), text: btn.textContent.replace(/\s+/g, ' ').trim(),
                background: getComputedStyle(btn).backgroundColor} : null,
    sheets: Array.from(document.styleSheets).map((s) => ({href: s.href, rules: rules(s)})),
    logo: logo ? {src: logo.currentSrc || logo.src, natural: logo.naturalWidth} : null,
    base: document.baseURI, url: location.href, title: document.title};
}"""


# ----------------------------------------------------------------------------- menu and footer year (every page)

def hidden_reason(v):
    if not v["rendered"]:
        return "not shown"
    if not v["inView"]:
        return f"outside the screen (box {v['box']})"
    if not v["hit"]:
        return "covered by " + (v["cover"] or "another element")
    return "visible"


def seen(v):
    return v["rendered"] and v["inView"] and v["hit"]


def test_page(env, vp, slug):
    year = str(env.year)
    plan = [("menu: five links to the five pages", "PAGES", "Home, Gallery, Book Online, About, Contact, each to its own page")]
    if vp == "desktop":
        plan += [("menu: navigation shown, no menu button", "DESIGN", "all five links visible in the header, .menu-btn not shown")]
    else:
        plan += [
            ("menu: closed at first, button shown", "DESIGN", ".menu-btn visible with aria-expanded=false, no link visible, no class open, no class menu-open"),
            ("menu: button opens it", "INTERACTION", "class open on #main-nav, aria-expanded=true on .menu-btn, class menu-open on body"),
            ("menu: five links visible when open", "DESIGN", "all five links inside the screen and not covered"),
            ("menu: button closes it again", "INTERACTION", "no class open, aria-expanded=false, no class menu-open, no link visible"),
            ("menu: Escape closes it, focus back on the button", "INTERACTION", "menu closed and the focus on .menu-btn"),
            ("menu: link click navigates", "INTERACTION", "a tap on a menu link opens that page"),
        ]
    plan += [("footer year is the current year", "INTERACTION", f"every [data-year] says {year}")]
    if slug == "home":
        plan += [("footer year follows the visitor's clock", "INTERACTION", f"with the clock set to {env.year + 3} every [data-year] says {env.year + 3}")]
    plan += [("page: no script error, no broken request", "PAGES", "clean")]
    ck = Checks(slug, vp, plan)
    url = env.url(slug)
    links_sel = "#main-nav a"

    def menu_state(page):
        return page.evaluate(JS_MENU)

    def link_vis(page):
        return page.evaluate(JS_VIS, [links_sel, False])

    def is_open(s):
        return bool(s) and s["navOpen"] and s["expanded"] == "true" and s["bodyOpen"]

    def is_closed(s):
        return bool(s) and not s["navOpen"] and s["expanded"] == "false" and not s["bodyOpen"]

    def describe(s):
        return (f"class open on nav: {'yes' if s['navOpen'] else 'no'}, aria-expanded={s['expanded']}, "
                f"class menu-open on body: {'yes' if s['bodyOpen'] else 'no'}")

    def body(ctx, page, log):
        page.goto(url, wait_until="load")

        # footer year
        y = page.evaluate(JS_YEAR)
        want = {year, str(y["clock"])}      # the two only differ in the minute around New Year
        ck.put("footer year is the current year", bool(y["spots"]) and all(s in want for s in y["spots"]),
               "no [data-year] element on the page" if not y["spots"] else "[data-year] says " + ", ".join(y["spots"]),
               owner="PAGES" if not y["spots"] else None)

        # the year with another clock (home only): shows that the script writes the year, not only the generator
        if slug == "home":
            future = env.year + 3
            ctx2 = None
            try:
                ctx2, page2, log2 = new_context(env, vp)      # its own context: the changed clock must not reach other tests
                page2.clock.set_fixed_time(datetime.datetime(future, 7, 1, 12, 0, 0))
                page2.goto(url, wait_until="load")
                y2 = page2.evaluate(JS_YEAR)
                ck.put("footer year follows the visitor's clock",
                       y2["clock"] == future and bool(y2["spots"]) and all(s == str(future) for s in y2["spots"]),
                       f"[data-year] says {', '.join(y2['spots']) or 'nothing'} (browser clock {y2['clock']})",
                       owner="PAGES" if not y2["spots"] else None)
                if connection_trouble(log2, env.base):
                    env.trouble = True
            except Exception as exc:
                ck.put("footer year follows the visitor's clock", False, "could not be checked: " + brief(exc))
            finally:
                if ctx2:
                    with contextlib.suppress(Exception):
                        ctx2.close()

        # the five links
        vis = link_vis(page)
        expected_links = [(label, env.url(target)) for label, target in NAV]
        got_links = [(v["text"], norm_url(v["href"])) for v in vis]
        ck.put("menu: five links to the five pages", got_links == expected_links,
               "as expected" if got_links == expected_links else "#main-nav has " + (", ".join(f"{t} -> {h}" for t, h in got_links) or "no links"))

        st = menu_state(page)
        btn = page.evaluate(JS_VIS, [".menu-btn", False])
        if vp == "desktop":
            shown = len(vis) == 5 and all(seen(v) for v in vis)
            no_btn = not any(b["rendered"] for b in btn)
            bad = [f"{v['text']}: {hidden_reason(v)}" for v in vis if not seen(v)]
            ck.put("menu: navigation shown, no menu button", shown and no_btn,
                   "; ".join(([f"{len(vis)} links in #main-nav"] if len(vis) != 5 else []) + bad +
                             ([] if no_btn else ["the menu button is shown"])) or "five links visible, button not shown")
        else:
            if not st["btn"] or not st["nav"]:
                raise Stop("the page has no " + (".menu-btn" if not st["btn"] else "#main-nav"), "PAGES")
            btn_ok = len(btn) == 1 and seen(btn[0])
            links_hidden = not any(seen(v) for v in vis)
            ck.put("menu: closed at first, button shown", btn_ok and is_closed(st) and links_hidden,
                   "; ".join(([] if btn_ok else ["menu button " + (hidden_reason(btn[0]) if btn else "missing")]) +
                             ([] if is_closed(st) else [describe(st)]) +
                             ([] if links_hidden else ["links already visible: " + ", ".join(v["text"] for v in vis if seen(v))]))
                   or "button visible, menu closed",
                   owner="DESIGN" if is_closed(st) else "PAGES")
            if not btn_ok:
                raise Stop("the menu button cannot be tapped (" + (hidden_reason(btn[0]) if btn else "missing") + ")", "DESIGN" if is_closed(st) else "PAGES")
            button = page.locator(".menu-btn")

            # open
            press(vp, button)
            st = poll(page, lambda: menu_state(page), is_open, default=MENU_UNKNOWN)
            opened = ck.put("menu: button opens it", is_open(st), describe(st))
            vis = poll(page, lambda: link_vis(page), lambda v: len(v) == 5 and all(seen(x) for x in v), STATE_MS if opened else 300, default=[])
            all_seen = len(vis) == 5 and all(seen(v) for v in vis)
            evidence = shot(page, f"check_behavior-menu-open-{vp}.png") if slug == "home" else ""
            ck.put("menu: five links visible when open", all_seen,
                   "five links visible" if all_seen else "; ".join(f"{v['text']}: {hidden_reason(v)}" for v in vis if not seen(v)) or f"{len(vis)} links",
                   evidence=evidence, owner="DESIGN" if opened else "INTERACTION")
            if not opened:
                raise Stop("the menu did not open")

            # close with the button
            press(vp, button)
            st = poll(page, lambda: menu_state(page), is_closed, default=MENU_UNKNOWN)
            vis = poll(page, lambda: link_vis(page), lambda v: not any(seen(x) for x in v), default=[])
            gone = not any(seen(v) for v in vis)
            ck.put("menu: button closes it again", is_closed(st) and gone,
                   describe(st) + ("" if gone else "; links still visible: " + ", ".join(v["text"] for v in vis if seen(v))),
                   owner="DESIGN" if is_closed(st) and not gone else None)

            # Escape: open, move the focus onto the first link, press Escape
            if not is_closed(st):
                page.reload(wait_until="load")
            press(vp, button)
            st = poll(page, lambda: menu_state(page), is_open, default=MENU_UNKNOWN)
            if not is_open(st):
                ck.put("menu: Escape closes it, focus back on the button", False, "the menu did not open a second time: " + describe(st))
            else:
                with contextlib.suppress(Exception):
                    page.locator(links_sel).first.focus(timeout=2000)
                before = menu_state(page)
                if not is_open(before):
                    ck.put("menu: Escape closes it, focus back on the button", False,
                           "the menu closed by itself when the focus moved onto its first link: " + describe(before))
                else:
                    page.keyboard.press("Escape")
                    st = poll(page, lambda: menu_state(page), lambda s: is_closed(s) and s["focusOnBtn"], default=MENU_UNKNOWN)
                    ck.put("menu: Escape closes it, focus back on the button", is_closed(st) and st["focusOnBtn"],
                           ("menu closed" if is_closed(st) else "menu still open (" + describe(st) + ")") + ", focus on " + st["active"],
                           evidence="focus was on " + before["active"] + " before Escape")

            # a tap on a link goes to that page
            st = menu_state(page)
            if not is_closed(st):
                page.reload(wait_until="load")
            current = [i for i, (_, target) in enumerate(NAV) if target == slug]
            pick = (current[0] + 1) % len(NAV) if current else list(common.PAGES).index(slug) % len(NAV)
            label, target = NAV[pick]
            press(vp, button)
            st = poll(page, lambda: menu_state(page), is_open, default=MENU_UNKNOWN)
            try:
                press(vp, page.locator(links_sel).nth(pick))
                arrived = poll(page, lambda: page.url, lambda u: norm_url(u) == env.url(target), 8000, default="")
                with contextlib.suppress(Exception):
                    page.wait_for_load_state("load")
                ok = norm_url(arrived) == env.url(target)
                ck.put("menu: link click navigates", ok, f"tap on {label}: the browser is on {norm_url(page.url)}",
                       expected=f"a tap on {label} opens {env.url(target)}")
            except Exception as exc:
                ck.put("menu: link click navigates", False, f"the link {label} could not be tapped: {brief(exc)}",
                       expected=f"a tap on {label} opens {env.url(target)}", owner="DESIGN" if is_open(st) else "INTERACTION")

    return run_test(env, ck, vp, body, clean_check="page: no script error, no broken request")


# ----------------------------------------------------------------------------- lightbox (gallery)

def test_lightbox(env, vp):
    L = "lightbox: "
    plan = [
        (L + "thumbnail click opens the viewer", "INTERACTION", "class open on .lightbox, class lightbox-open on body, the viewer covers the page, the address stays the gallery"),
        (L + "built to the contract", "INTERACTION", "one div.lightbox with role=dialog, aria-modal=true, aria-label=Photo viewer, holding button.lb-close, button.lb-prev, img.lb-img, button.lb-next, p.lb-count"),
        (L + "image src equals the link href", "INTERACTION", "after every opening and every step img.lb-img shows the full-size file of that gallery link"),
        (L + "every full-size photo loads", "ASSETS", "each photo shown in the viewer loads (naturalWidth above 0)"),
        (L + "alt equals the thumbnail alt", "INTERACTION", "img.lb-img has the alt text of the thumbnail of the photo on show"),
        (L + "counter shows position and total", "INTERACTION", "p.lb-count holds the number of the photo on show and the number of photos"),
        (L + "next button goes through all photos", "INTERACTION", "each tap on button.lb-next shows the next gallery photo, in order, to the last one"),
        (L + "previous button", "INTERACTION", "button.lb-prev shows the photo before"),
        (L + "right arrow key", "INTERACTION", "ArrowRight shows the next photo"),
        (L + "left arrow key", "INTERACTION", "ArrowLeft shows the photo before"),
        (L + "wraps from the last photo to the first", "INTERACTION", "on the last photo the next button and ArrowRight show photo 1"),
        (L + "wraps from the first photo to the last", "INTERACTION", "on photo 1 the previous button and ArrowLeft show the last photo"),
        (L + "focus stays inside while open", "INTERACTION", "focus inside .lightbox right after opening and after every Tab and Shift+Tab"),
        (L + "Escape closes", "INTERACTION", "no class open, no class lightbox-open, the viewer no longer covers the page"),
        (L + "click on the backdrop closes", "INTERACTION", "a click on the dark layer (not the photo, not a button) closes the viewer"),
        (L + "close button closes", "INTERACTION", "button.lb-close closes the viewer"),
        (L + "focus returns to the opening link", "INTERACTION", "after closing, the focus is on the gallery link that opened the viewer"),
        (L + "no script error, no broken request", "PAGES", "clean"),
    ]
    ck = Checks("gallery", vp, plan)
    url = env.url("gallery")

    def body(ctx, page, log):
        page.goto(url, wait_until="load")
        links = page.evaluate(JS_GALLERY)
        total = len(links)
        if total < 3:
            raise Stop(f"the gallery has {total} links (.gallery a), the viewer cannot be tested", "PAGES")

        def state():
            return page.evaluate(JS_LB)

        def rel(u):
            return (u or "nothing").replace(env.base, "/")

        hrefs = [x["href"] for x in links]
        src_bad, nav_bad, alt_bad, count_bad, load_bad, unpressable = [], [], [], [], [], []
        stats = {"shown": 0, "loaded": 0, "opener": None}
        steps = {"next": [], "prev": [], "right": [], "left": [], "wrap_end": [], "wrap_start": []}
        focus_back, focus_open, opened = [], [], []

        def shown(idx, what, opening=False):
            """Wait until the viewer shows gallery photo idx, then check counter, alt text and loading."""
            want = hrefs[idx]
            s = poll(page, state, lambda s: s["src"] == want, default={})
            if not s or s.get("src") != want:
                got = (s or {}).get("src")
                text = f"{what}: the viewer shows {rel(got)}, expected photo {idx + 1} ({rel(want)})"
                # a step that lands on another gallery photo is a fault of that step, not of the src rule
                (nav_bad if got in hrefs and not opening else src_bad).append(text)
                return False
            stats["shown"] += 1
            numbers = [int(n) for n in re.findall(r"\d+", s.get("count") or "")]
            if numbers != [idx + 1, total]:
                count_bad.append(f"{what}: counter says {s.get('count')!r}, expected {idx + 1} and {total}")
            if s.get("alt") != links[idx]["alt"]:
                alt_bad.append(f"{what}: alt is {s.get('alt')!r}, thumbnail {idx + 1} has {links[idx]['alt']!r}")
            s = poll(page, state, lambda s: s["src"] != want or s["complete"], 15000, default={})
            if s and s.get("src") == want and s.get("natural", 0) > 0:
                stats["loaded"] += 1
            else:
                load_bad.append(f"photo {idx + 1} ({rel(want)}) did not load")
            return True

        def act(kind, what, do, idx):
            """One press of a button or key, then: does the viewer show photo idx?"""
            try:
                do()
            except Exception as exc:
                unpressable.append(f"{what}: could not be pressed ({brief(exc)})")
                steps[kind].append((what, False))
                return False
            ok = shown(idx, what)
            steps[kind].append((what, ok))
            return ok

        def tap(sel):
            press(vp, page.locator(".lightbox " + sel), timeout=4000)

        def key(name):
            page.keyboard.press(name)

        def open_at(idx):
            press(vp, page.locator(".gallery a").nth(idx))
            s = poll(page, state, lambda s: s["open"] and s["bodyOpen"] and s["onTop"], default={}) or {}
            stayed = norm_url(s.get("url", page.url)) == url
            ok = bool(s.get("open") and s.get("bodyOpen") and s.get("onTop") and stayed)
            if not stayed:
                actual = f"the browser left the gallery and opened {rel(page.url)} (the click was not taken over)"
            elif not s.get("boxes"):
                actual = "no .lightbox element was built"
            else:
                actual = (f"class open on .lightbox: {'yes' if s.get('open') else 'no'}, class lightbox-open on body: "
                          f"{'yes' if s.get('bodyOpen') else 'no'}, viewer covers the page: {'yes' if s.get('onTop') else 'no'}")
            if not ok or not opened:
                ck.put(L + "thumbnail click opens the viewer", ok, f"thumbnail {idx + 1}: " + actual,
                       evidence=shot(page, f"check_behavior-lightbox-{vp}.png") if ok else "")
            if not ok:
                raise Stop(f"the viewer did not open on thumbnail {idx + 1}")
            opened.append(idx)
            stats["opener"] = idx
            focus_open.append((idx, s.get("focusInside"), s.get("active")))
            return s

        def ensure_at(idx):
            """Put the viewer on photo idx without using anything that is under test:
            if it is not there already, load the page again when the viewer is in the way, then open that thumbnail."""
            s = state()
            if s.get("open") and s.get("src") == hrefs[idx]:
                return True
            if s.get("open") or s.get("bodyOpen") or s.get("onTop"):
                page.reload(wait_until="load")
            open_at(idx)
            return shown(idx, f"opening thumbnail {idx + 1}", opening=True)

        def step(kind, name, do, start, delta):
            what = f"{name} on photo {start + 1}"
            if not ensure_at(start):
                nav_bad.append(f"{what}: not tried, the viewer could not be put on photo {start + 1} first")
                steps[kind].append((what, False))
                return False
            return act(kind, what, do, (start + delta) % total)

        def closed(s):
            return bool(s) and s["boxes"] >= 1 and not s["open"] and not s["bodyOpen"] and not s["onTop"]

        def close_with(check, do):
            if not state().get("open"):
                ensure_at(stats["opener"] if stats["opener"] is not None else 0)
            opener = stats["opener"]
            try:
                do()
            except Exception as exc:
                ck.put(check, False, "could not be pressed (" + brief(exc) + ")", owner="DESIGN")
                return False
            s = poll(page, state, lambda s: closed(s) and s["activeLink"] == opener, default={}) or {}
            ok = closed(s)
            ck.put(check, ok, "viewer closed" if ok else
                   f"still there: class open {'yes' if s.get('open') else 'no'}, class lightbox-open on body "
                   f"{'yes' if s.get('bodyOpen') else 'no'}, covers the page {'yes' if s.get('onTop') else 'no'}")
            if ok:
                focus_back.append((check.replace(L, ""), opener, s.get("activeLink"), s.get("active")))
            return ok

        # ---- part 1: open the first thumbnail, walk through every photo with the next button, focus, Escape
        s = open_at(0)
        parts = s.get("parts", {})
        built = (s["boxes"] == 1 and s.get("role") == "dialog" and s.get("modal") == "true" and s.get("label") == "Photo viewer"
                 and all(parts.get(k) == 1 for k in ("button.lb-close", "button.lb-prev", "img.lb-img", "button.lb-next", "p.lb-count")))
        ck.put(L + "built to the contract", built,
               "as expected" if built else f"{s['boxes']} .lightbox, role={s.get('role')}, aria-modal={s.get('modal')}, "
               f"aria-label={s.get('label')!r}, parts found: " + ", ".join(f"{k} x {v}" for k, v in parts.items()))
        if not parts.get("img.lb-img"):
            raise Stop("the viewer has no img.lb-img, so what it shows cannot be checked")

        walked = shown(0, "opening thumbnail 1", opening=True)
        if walked:
            for k in range(1, total):
                if not act("next", f"next button on photo {k}", lambda: tap("button.lb-next"), k):
                    walked = False
                    break
        pressed = [u for u in unpressable if u.startswith("next button")]
        ck.put(L + "next button goes through all photos", walked,
               f"all {total} photos shown in order" if walked else (pressed or [x for x in nav_bad + src_bad if x.startswith(("next button", "opening"))] or ["stopped"])[-1],
               owner="DESIGN" if pressed else None)

        trail, inside = [], True
        if not state().get("open"):
            ensure_at(0)
        for name in ["Tab"] * 5 + ["Shift+Tab"] * 5:
            page.keyboard.press(name)
            s = state()
            trail.append(f"{name} -> {s['active']}")
            if not s["focusInside"] or not s["open"]:
                inside = False
        if not state().get("open"):
            ensure_at(0)
        close_with(L + "Escape closes", lambda: key("Escape"))

        # ---- part 2: a thumbnail in the middle, previous button and arrow keys, close on the backdrop
        m = total // 2
        step("prev", "previous button", lambda: tap("button.lb-prev"), m, -1)
        step("right", "ArrowRight", lambda: key("ArrowRight"), m - 1, +1)
        step("left", "ArrowLeft", lambda: key("ArrowLeft"), m, -1)
        if not state().get("open"):
            ensure_at(m)
        spot = page.evaluate(JS_BACKDROP)
        if not spot:
            ck.put(L + "click on the backdrop closes", False, "no free spot of the dark layer was found to click on (photo and buttons cover everything)", owner="DESIGN")
        else:
            close_with(L + "click on the backdrop closes",
                       lambda: page.touchscreen.tap(spot["x"], spot["y"]) if vp == "phone" else page.mouse.click(spot["x"], spot["y"]))

        # ---- part 3: the last and the first photo, wrap around both ways, close with the button
        last = total - 1
        step("wrap_end", "next button", lambda: tap("button.lb-next"), last, +1)
        step("wrap_start", "ArrowLeft", lambda: key("ArrowLeft"), 0, -1)
        step("wrap_end", "ArrowRight", lambda: key("ArrowRight"), last, +1)
        step("wrap_start", "previous button", lambda: tap("button.lb-prev"), 0, -1)
        close_with(L + "close button closes", lambda: tap("button.lb-close"))

        # ---- verdicts collected over the three parts
        def verdict(check, kinds, need):
            done = [x for k in kinds for x in steps[k]]
            bad = [what for what, ok in done if not ok]
            missing = [n for n in need if not any(what.startswith(n) for what, _ in done)]
            ok = bool(done) and not bad and not missing
            details = [x for x in unpressable + nav_bad + src_bad if any(x.startswith(b + ":") for b in bad)]
            only_unpressable = bool(bad) and all(any(u.startswith(b + ":") for u in unpressable) for b in bad)
            ck.put(check, ok, "works" if ok else "; ".join(details + [f"not reached: {n}" for n in missing]) or "; ".join("failed: " + b for b in bad) or "not reached",
                   evidence="; ".join(what for what, _ in done), owner="DESIGN" if only_unpressable else None)

        verdict(L + "previous button", ["prev"], ["previous button"])
        verdict(L + "right arrow key", ["right"], ["ArrowRight"])
        verdict(L + "left arrow key", ["left"], ["ArrowLeft"])
        verdict(L + "wraps from the last photo to the first", ["wrap_end"], ["next button", "ArrowRight"])
        verdict(L + "wraps from the first photo to the last", ["wrap_start"], ["previous button", "ArrowLeft"])

        ck.put(L + "image src equals the link href", stats["shown"] > 0 and not src_bad,
               f"img.lb-img showed the file of the gallery link on all {stats['shown']} photo views" if not src_bad else "; ".join(src_bad[:4]) + (f" (and {len(src_bad) - 4} more)" if len(src_bad) > 4 else ""))
        never = "not checked: the viewer never showed the file of a gallery link"
        ck.put(L + "every full-size photo loads", stats["shown"] > 0 and not load_bad, never if not stats["shown"] else
               f"{stats['loaded']} of {stats['shown']} photo views loaded" + ("" if not load_bad else ": " + "; ".join(sorted(set(load_bad))[:6])))
        ck.put(L + "alt equals the thumbnail alt", stats["shown"] > 0 and not alt_bad, never if not stats["shown"] else
               f"equal on {stats['shown']} photo views" if not alt_bad else "; ".join(alt_bad[:4]) + (f" (and {len(alt_bad) - 4} more)" if len(alt_bad) > 4 else ""),
               evidence=f"{sum(1 for x in links if x['alt'])} of {total} thumbnails have a non-empty alt text")
        ck.put(L + "counter shows position and total", stats["shown"] > 0 and not count_bad, never if not stats["shown"] else
               f"right on {stats['shown']} photo views" if not count_bad else "; ".join(count_bad[:4]) + (f" (and {len(count_bad) - 4} more)" if len(count_bad) > 4 else ""))

        opened_inside = all(inside_now for _, inside_now, _ in focus_open)
        ck.put(L + "focus stays inside while open", inside and opened_inside,
               "focus inside after every opening and after 10 Tab presses" if inside and opened_inside else
               "; ".join([f"after opening thumbnail {i + 1} the focus is on {a}" for i, ins, a in focus_open if not ins] +
                         ([] if inside else ["focus left the viewer during Tab or Shift+Tab"])),
               evidence="; ".join(trail))
        wrong = [f"after {how}: focus on {active}, expected gallery link {opener + 1}" for how, opener, got, active in focus_back if got != opener]
        ck.put(L + "focus returns to the opening link", bool(focus_back) and not wrong,
               "; ".join(wrong) if wrong else (f"focus back on the opening link after {len(focus_back)} of 3 ways to close" if focus_back else "the viewer never closed, nothing to check"))

    return run_test(env, ck, vp, body, clean_check=L + "no script error, no broken request")


# ----------------------------------------------------------------------------- Book Now and Book Online button

DECLARATION = re.compile(r"""\b(var|let|const)\s+BOOKING_URL\s*=\s*(["'])(.*?)\2\s*;""")
FIRST_STATEMENT = re.compile(r"""var\s+BOOKING_URL\s*=\s*(["'])(.*?)\1\s*;""")


def without_leading_comments(js):
    s = js.lstrip("\ufeff")
    while True:
        s = s.lstrip()
        if s.startswith("/*"):
            end = s.find("*/")
            s = s[end + 2:] if end >= 0 else ""
        elif s.startswith("//"):
            end = s.find("\n")
            s = s[end + 1:] if end >= 0 else ""
        else:
            return s


def read_site_js(ctx, env):
    """The script as the server sends it: (status, text, value of BOOKING_URL or None, declared first?)."""
    try:
        r = fetch_patiently(lambda: ctx.request.get(env.base + "js/site.js"))
        status, text = r.status, r.text() if r.ok else ""
    except Exception as exc:
        return None, "", None, False, brief(exc)
    m = DECLARATION.search(text)
    first = FIRST_STATEMENT.match(without_leading_comments(text))
    return status, text, (m.group(3) if m else None), bool(first), ""


@contextlib.contextmanager
def booking_url_forced(page, value):
    """While this is open the page gets js/site.js with another BOOKING_URL (None = the script as it is).
    Yields a list that collects, per request for the script, how many declarations were changed."""
    hits = []
    if value is None:
        yield [1]
        return
    pattern = re.compile(r"/js/site\.js(\?.*)?$")

    def handle(route):
        try:
            response = fetch_patiently(route.fetch)
            text, n = DECLARATION.subn(lambda m: f'{m.group(1)} BOOKING_URL = "{value}";', response.text(), count=1)
            hits.append(n)
            route.fulfill(response=response, body=text)
        except Exception:
            hits.append(0)
            with contextlib.suppress(Exception):
                route.continue_()
    page.route(pattern, handle)
    try:
        yield hits
    finally:
        with contextlib.suppress(Exception):
            page.unroute(pattern, handle)


def real_link(value):
    s = urlsplit(value.strip())
    host = (s.hostname or "").lower()
    return s.scheme == "https" and "." in host and not host.endswith(("example.com", "example.org", "example.net", ".test", ".localhost", ".invalid")) \
        and "example" not in value.lower()


def test_book_now(env, vp):
    B = "book now: "
    plan = [
        (B + "ten Book Now pills", "PAGES", "10 a.pill[data-book], one per service"),
        (B + "BOOKING_URL is the first statement of js/site.js", "INTERACTION", 'var BOOKING_URL = ""; first in the file (empty until the owner pastes a real https link)'),
        (B + "pills call the phone while BOOKING_URL is empty", "INTERACTION", f"every pill has href {TEL} and no target"),
        (B + "pills open the booking link when BOOKING_URL is set", "INTERACTION", f"with BOOKING_URL = {TEST_BOOKING_URL}: every pill has that href, target=_blank and rel=noopener"),
        (B + "no script error, no broken request", "PAGES", "clean"),
    ]
    ck = Checks("book-online", vp, plan)
    url = env.url("book-online")

    def pills_wrong(pills, href, new_tab):
        bad = []
        for i, p in enumerate(pills, 1):
            if p["href"] != href:
                bad.append(f"pill {i} href {p['href']!r}")
            elif new_tab and (p["target"] != "_blank" or "noopener" not in (p["rel"] or "").split()):
                bad.append(f"pill {i} target={p['target']!r} rel={p['rel']!r}")
            elif not new_tab and p["target"]:
                bad.append(f"pill {i} has target={p['target']!r}")
        return bad

    def body(ctx, page, log):
        status, text, served, first, err = read_site_js(ctx, env)
        if status != 200:
            raise Stop(f"js/site.js could not be read (status {status}{', ' + err if err else ''})")

        # as served
        page.goto(url, wait_until="load")
        got = page.evaluate(JS_BOOK)
        pills = got["pills"]
        ck.put(B + "ten Book Now pills", len(pills) == 10,
               f"{len(pills)} a.pill[data-book], {got['marked']} [data-book] elements in all")
        as_served_bad = []
        if served:
            link = served.strip()
            as_served_bad = pills_wrong(pills, link if re.match(r"https?://", link, re.I) else "https://" + link.lstrip("/"), True)
        setting_ok = first and served is not None and (served.strip() == "" or (real_link(served) and not as_served_bad))
        if served is None:
            actual = "no BOOKING_URL declaration found in js/site.js"
        elif not first:
            actual = f"BOOKING_URL = {served!r} is declared, but not as the first statement with var"
        elif served.strip() == "":
            actual = 'var BOOKING_URL = ""; (empty, the buttons call the phone)'
        elif not real_link(served):
            actual = f"BOOKING_URL is set to {served!r}, which is not a real https booking link"
        else:
            actual = f"BOOKING_URL is set to {served!r}" + ("" if not as_served_bad else ", but the pills do not follow it: " + "; ".join(as_served_bad[:3]))
        ck.put(B + "BOOKING_URL is the first statement of js/site.js", setting_ok, actual)

        # empty: as served when it is empty, otherwise with a copy of the script in which it is emptied
        how = "js/site.js as served"
        if served is None or served.strip():
            with booking_url_forced(page, "") as hits:
                page.goto(url, wait_until="load")
                pills_e = page.evaluate(JS_BOOK)["pills"]
            how = "js/site.js served with BOOKING_URL emptied" if any(hits) else "BOOKING_URL could not be emptied (no declaration)"
        else:
            pills_e = pills
        bad = pills_wrong(pills_e, TEL, False)
        ck.put(B + "pills call the phone while BOOKING_URL is empty", bool(pills_e) and not bad,
               f"{len(pills_e)} pills, all {TEL}, no target" if pills_e and not bad else "; ".join(bad[:5]) or "no pills", evidence=how)

        # set
        with booking_url_forced(page, TEST_BOOKING_URL) as hits:
            page.goto(url, wait_until="load")
            pills_s = page.evaluate(JS_BOOK)["pills"]
        if not any(hits):
            ck.put(B + "pills open the booking link when BOOKING_URL is set", False,
                   "the test could not set BOOKING_URL: js/site.js was " + ("not requested by the page" if not hits else "requested, but has no BOOKING_URL declaration"),
                   owner="PAGES" if not hits else "INTERACTION")
        else:
            bad = pills_wrong(pills_s, TEST_BOOKING_URL, True)
            ck.put(B + "pills open the booking link when BOOKING_URL is set", bool(pills_s) and not bad,
                   f"{len(pills_s)} pills, all {TEST_BOOKING_URL}, target=_blank, rel=noopener" if pills_s and not bad else "; ".join(bad[:5]) or "no pills")

    return run_test(env, ck, vp, body, clean_check=B + "no script error, no broken request")


def test_home_links(env, vp):
    """The Call button and the Text link of the hero (decision 45). They call and text the number whatever
    BOOKING_URL says: a button says what it does, so neither is marked data-book."""
    C, T = "call button: ", "text link: "
    plan = [
        (C + "calls 347-671-5095 while BOOKING_URL is empty", "PAGES", f"one .hero a.btn-call with the text Call 347-671-5095 and href {TEL}, no data-book, no target"),
        (C + "still calls 347-671-5095 when BOOKING_URL is set", "INTERACTION", f"with BOOKING_URL = {TEST_BOOKING_URL} the button still calls {TEL}"),
        (T + "texts the same number", "PAGES", f"one .hero a.text-link with the text Text Gerta and href {SMS}, no data-book, no target"),
    ]
    ck = Checks("home", vp, plan)

    def one_case(page, value):
        with booking_url_forced(page, value) as hits:
            page.goto(env.url("home"), wait_until="load")
            if not any(hits):
                raise Stop("the test could not set BOOKING_URL: js/site.js was " +
                           ("not requested by the page" if not hits else "requested, but has no BOOKING_URL declaration"), "INTERACTION")
            page.wait_for_timeout(200)          # js/site.js runs on DOMContentLoaded, give it a moment
            return page.evaluate(JS_HOME_LINKS)

    def judge(links, kind, text, href):
        found = links[kind]
        if len(found) != 1:
            return False, f"{len(found)} links of this kind on the home page"
        a = found[0]
        ok = a["text"] == text and a["attr"] == href and not a["book"] and not a["target"]
        return ok, f"text {a['text']!r}, href {a['attr']!r}, target {a['target']!r}, data-book: {'yes' if a['book'] else 'no'}"

    def body(ctx, page, log):
        status, text, served, first, err = read_site_js(ctx, env)
        links = one_case(page, None if served is not None and not served.strip() else "")
        ck.put(C + "calls 347-671-5095 while BOOKING_URL is empty", *judge(links, "call", "Call 347-671-5095", TEL))
        ck.put(T + "texts the same number", *judge(links, "text", "Text Gerta", SMS))
        links = one_case(page, TEST_BOOKING_URL)
        ok, actual = judge(links, "call", "Call 347-671-5095", TEL)
        ck.put(C + "still calls 347-671-5095 when BOOKING_URL is set", ok, actual)

    return run_test(env, ck, vp, body)


# ----------------------------------------------------------------------------- contact form

def parse_mailto(href):
    """-> (address part, [(name, decoded value), ...]). Decoding is plain percent decoding: a + stays a +."""
    head, _, query = (href or "").partition("?")
    pairs = []
    for piece in query.split("&") if query else []:
        name, _, value = piece.partition("=")
        pairs.append((name, unquote(value)))
    return head, pairs


def test_contact_form(env, vp):
    C = "contact form: "
    subject = f"Website message from {SENDER['first']} {SENDER['last']}"
    plan = [
        (C + "empty email is stopped by the browser", "INTERACTION", "no mail link, the status line stays empty, #email is marked as missing by the browser"),
        (C + "malformed email is stopped by the browser", "INTERACTION", "no mail link, the status line stays empty, #email is marked as mistyped by the browser"),
        (C + "empty email shows its message in words", "INTERACTION",
         "#email-error is shown under the field with the text of its data-missing, #email has aria-invalid=true, points at #email-error and has the focus"),
        (C + "malformed email shows its message in words", "INTERACTION",
         "#email-error is shown with the text of its data-invalid, #email has aria-invalid=true and the focus"),
        (C + "the message goes once the address is right", "INTERACTION", "after a valid address is typed #email-error is hidden and #email has no aria-invalid"),
        (C + "valid submit builds the mail link", "INTERACTION", f"{MAILTO}?subject={subject}&body=(the message and {SENDER['email']}), percent-encoded"),
        (C + "mail link is opened by clicking a temporary a element", "INTERACTION", "one click on an a element made for it and removed again, no other way of opening"),
        (C + "status line appears in .form-note", "INTERACTION", "the text of the form's data-sent attribute, visible in .form-note"),
        (C + "submit causes no network request", "INTERACTION", "no request of any kind after Send, the page stays where it is"),
        (C + "no script error, no broken request", "PAGES", "clean"),
    ]
    ck = Checks("contact", vp, plan)
    url = env.url("contact")

    def form_checks(page, requests):
        page.goto(url, wait_until="load")
        page.evaluate(JS_MAIL_HOOK)
        info = page.evaluate(JS_FORM)
        if not info["form"]:
            raise Stop("the page has no #contact-form", "PAGES")
        if info["missing"]:
            raise Stop("the form lacks " + ", ".join(info["missing"]), "PAGES")
        send = page.locator("#contact-form button[type=submit]")

        def quiet():
            for _ in range(12):
                n = len(requests)
                page.wait_for_timeout(500)
                if len(requests) == n:
                    return

        def settle():
            # let everything that loads late (map, lazy images) start now, so it is not mistaken for the submit
            page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
            page.wait_for_timeout(300)
            send.scroll_into_view_if_needed()
            quiet()

        settle()

        def attempt(email, wait_for_mail):
            if page.evaluate(JS_FORM).get("note") or page.url != url:
                # an earlier attempt left its mark (a status line, another address): start from a fresh page,
                # so that one fault is not counted again in the next check
                page.goto(url, wait_until="load")
                settle()
            page.fill("#first-name", SENDER["first"])
            page.fill("#last-name", SENDER["last"])
            page.fill("#email", email)
            page.fill("#message", SENDER["message"])
            quiet()
            page.evaluate(JS_MAIL_HOOK)         # again, in case an earlier attempt made the page load anew
            page.evaluate("() => window.__qaMail.arm()")
            n0 = len(requests)
            press(vp, send, no_wait_after=True)
            nothing = {"clicks": [], "navs": [], "opens": [], "lastStillInPage": None, "leftovers": 0}
            read = lambda: page.evaluate("(nothing) => window.__qaMail ? window.__qaMail.read() : nothing", nothing)
            if wait_for_mail:
                poll(page, read, lambda r: r["clicks"] or r["navs"] or r["opens"], default=nothing)
                page.wait_for_timeout(1000)
            else:
                page.wait_for_timeout(800)
            with contextlib.suppress(Exception):
                page.wait_for_load_state("load")        # only matters when the submit wrongly made the page load anew
            rec = poll(page, read, lambda r: True, 2000, default=nothing)
            new = [u for u in requests[n0:] if not u.startswith(("mailto:", "data:", "blob:", "about:"))]
            return rec, page.evaluate(JS_FORM), new

        def in_words(check, f, which):
            e = f.get("error")
            want = e.get(which) if e else None
            ok = bool(e) and bool(want) and e["shown"] and e["text"] == want and f["ariaInvalid"] == "true" \
                and f["describedBy"] == "email-error" and f["focused"]
            ck.put(check, ok, "no #email-error under the field" if not e else
                   "; ".join([("message shown: %r" % e["text"]) if e["shown"] else "message not shown",
                              "matches data-%s" % ("missing" if which == "missing" else "invalid") if e["text"] == want else "expected %r" % want,
                              "aria-invalid=%s" % f["ariaInvalid"], "aria-describedby=%s" % f["describedBy"],
                              "focus on #email" if f["focused"] else "the focus is elsewhere"]))

        def stopped(check, email, flag, word, words_check=None, which=None):
            rec, f, _ = attempt(email, False)
            if words_check:
                in_words(words_check, f, which)
            mails = [c["href"] for c in rec["clicks"]] + [n["url"] for n in rec["navs"]] + rec["opens"]
            marked = bool(f["validity"]) and f["validity"][flag] and not f["novalidate"]
            ok = not mails and not f["note"] and marked
            owner = "PAGES" if (f["novalidate"] or f["emailType"] != "email" or not f["emailRequired"]) else "INTERACTION"
            ck.put(check, ok,
                   "; ".join((["a mail link was opened: " + one_line(mails[0], 160)] if mails else ["no mail link"]) +
                             ([f"status line says {f['note']!r}"] if f["note"] else ["status line empty"]) +
                             ([f"#email marked as {word}"] if marked else
                              [f"#email not stopped by the browser (type={f['emailType']}, required={f['emailRequired']}, novalidate={f['novalidate']})"])),
                   owner=owner)

        stopped(C + "empty email is stopped by the browser", "", "valueMissing", "missing", C + "empty email shows its message in words", "missing")
        stopped(C + "malformed email is stopped by the browser", "maria.rossi", "typeMismatch", "mistyped",
                C + "malformed email shows its message in words", "invalid")
        # the address is corrected: the message goes as the visitor types
        page.fill("#email", SENDER["email"])
        page.wait_for_timeout(200)
        f = page.evaluate(JS_FORM)
        e = f.get("error") or {}
        ck.put(C + "the message goes once the address is right", bool(f.get("error")) and not e.get("shown") and f["ariaInvalid"] is None,
               "message hidden, no aria-invalid" if not e.get("shown") and f["ariaInvalid"] is None else
               "message still shown (%r), aria-invalid=%s" % (e.get("text"), f["ariaInvalid"]))

        rec, f, new = attempt(SENDER["email"], True)
        evidence = shot(page, f"check_behavior-contact-sent-{vp}.png")
        clicks, navs, opens = rec["clicks"], rec["navs"], rec["opens"]
        href = clicks[0]["href"] if clicks else navs[0]["url"] if navs else opens[0] if opens else None

        # the link itself
        if href is None:
            ck.put(C + "valid submit builds the mail link", False, "no mail link was opened after Send")
        else:
            head, pairs = parse_mailto(href)
            got = dict(pairs)
            body_text = got.get("body", "").replace("\r\n", "\n").replace("\r", "\n")
            wrong = []
            if head != MAILTO:
                wrong.append(f"address part is {head!r}")
            if [n for n, _ in pairs] != ["subject", "body"]:
                wrong.append("fields are " + (", ".join(n for n, _ in pairs) or "none") + " (expected subject, body)")
            if got.get("subject") != subject:
                wrong.append(f"subject is {got.get('subject')!r}")
            if SENDER["message"] not in body_text:
                wrong.append("the body does not hold the message as typed: " + one_line(repr(body_text), 260))
            if SENDER["email"] not in body_text:
                wrong.append("the body does not hold the sender's email")
            ck.put(C + "valid submit builds the mail link", not wrong,
                   "; ".join(wrong) if wrong else f"{head} with subject {got.get('subject')!r} and a body holding the message and {SENDER['email']}",
                   evidence=one_line(href, 600))

        # how it was opened
        temp_ok = (len(clicks) == 1 and not navs and not opens and not clicks[0]["existedBefore"]
                   and rec["leftovers"] == 0 and rec["lastStillInPage"] is False)
        if temp_ok:
            actual = "one click on a temporary a element, seen by the " + clicks[0]["how"]
        elif not clicks and navs:
            actual = ("the browser sent the form itself (the script did not take over)" if navs[0].get("form")
                      else "opened by changing the address of the page, not by clicking an a element")
        elif not clicks and opens:
            actual = "opened with window.open, not by clicking an a element"
        elif not clicks:
            actual = "no mail link was opened"
        else:
            actual = "; ".join(([f"{len(clicks)} clicks on a mail link"] if len(clicks) != 1 else []) +
                               (["the clicked a element was already in the page"] if clicks[0]["existedBefore"] else []) +
                               (["the a element stays in the page after the click"] if rec["leftovers"] or rec["lastStillInPage"] else []) +
                               (["the browser also sent the form itself (the script did not stop it)"] if any(n.get("form") for n in navs) else
                                [f"and {len(navs) + len(opens)} more opening by another way"] if navs or opens else [])) or "could not be confirmed"
        ck.put(C + "mail link is opened by clicking a temporary a element", temp_ok, actual)

        # status line
        note = page.evaluate(JS_VIS, [".form-note", True])
        note_text = f["note"] or ""
        sent = (info["sent"] or "").strip()
        sent = re.sub(r"\s+", " ", sent)
        shown = bool(note) and note[0]["rendered"] and bool(note_text)
        ck.put(C + "status line appears in .form-note", shown and (not sent or note_text == sent),
               (f".form-note says {note_text!r}" if note_text else ".form-note is empty") +
               ("" if not note_text or (note and note[0]["rendered"]) else ", but it is not shown") +
               ("" if sent else " (the form has no data-sent text to compare with)"),
               expected=f".form-note shows {sent!r}" if sent else None, evidence=evidence)

        # no request
        stayed = f.get("url", page.url) == url
        ck.put(C + "submit causes no network request", not new and stayed,
               "; ".join(([f"{len(new)} requests after Send: " + ", ".join(new[:4])] if new else ["no request"]) +
                         (["the page stayed"] if stayed else [f"the page moved to {f.get('url')}"])))

    def body(ctx, page, log):
        requests = []

        def on_request(r):
            requests.append(r.url)
        ctx.on("request", on_request)
        try:
            form_checks(page, requests)
        finally:
            with contextlib.suppress(Exception):
                ctx.remove_listener("request", on_request)

    return run_test(env, ck, vp, body, clean_check=C + "no script error, no broken request")


# ----------------------------------------------------------------------------- the reveal of the hero photos (home)

def inset_sides(value):
    """'inset(0px 0px 100%)' -> ('0', '0', '100%', '0'): top, right, bottom, left as CSS fills them in. None for anything else."""
    m = re.fullmatch(r"\s*inset\(([^)]*)\)\s*", value or "")
    if not m:
        return None
    parts = [re.sub(r"^0(px|%)?$", "0", p) for p in m.group(1).split()]
    if not 1 <= len(parts) <= 4:
        return None
    top = parts[0]
    right = parts[1] if len(parts) > 1 else top
    bottom = parts[2] if len(parts) > 2 else top
    left = parts[3] if len(parts) > 3 else right
    return (top, right, bottom, left)


def test_reveal(env, vp):
    """The one motion of the site (design brief of 12 November 2026, decision 45): the hero photos are revealed from
    top to bottom once when the home page opens, in about 600 ms, and not at all when the visitor prefers reduced
    motion. Nothing else on the page moves. It took the place of the scrolling hours line."""
    R = "reveal: "
    plan = [
        (R + "the hero photos are revealed from top to bottom, once", "DESIGN",
         f"div.hero-photos runs the animation reveal once, {REVEAL_MS[0]} to {REVEAL_MS[1]} ms, from clip-path inset(0px 0px 100% 0px) to inset(0px)"),
        (R + "nothing else moves", "DESIGN", "after 1.5 s no animation of the home page is still running, and the reveal was the only one"),
        (R + "skipped with reduced motion", "DESIGN", "with prefers-reduced-motion: reduce div.hero-photos has no animation and the photos show in full"),
    ]
    ck = Checks("home", vp, plan)
    url = env.url("home")

    def body(ctx, page, log):
        page.goto(url, wait_until="load")
        info = page.evaluate(JS_REVEAL)
        if not info.get("box"):
            raise Stop("the home page has no div.hero-photos", "PAGES")
        ms = float(info["duration"][:-2]) * 1000 if info["duration"].endswith("ms") else float(info["duration"][:-1] or 0) * 1000
        frames = [re.sub(r"\s+", " ", f) for f in info["frames"]]
        sides = [inset_sides(f) for f in frames]
        top_down = len(sides) >= 2 and sides[0] == ("0", "0", "100%", "0") and sides[-1] == ("0", "0", "0", "0")
        ok = info["name"] == "reveal" and info["count"] == "1" and REVEAL_MS[0] <= ms <= REVEAL_MS[1] and top_down
        ck.put(R + "the hero photos are revealed from top to bottom, once", ok,
               f"animation {info['name']}, {ms:.0f} ms, {info['count']} time(s), key frames {frames}")
        page.wait_for_timeout(1500)
        later = page.evaluate(JS_REVEAL)
        running = [a for a in later["all"] if a["state"] == "running"]
        others = sorted({a["name"] for a in later["all"] if a["name"] != "reveal"})
        ck.put(R + "nothing else moves", not running and not others,
               "no animation is running" + (", but there were others: %s" % ", ".join(others) if others else "")
               if not running else "still running: " + ", ".join("%s on %s" % (a["name"], a["target"]) for a in running))
        try:
            page.emulate_media(reduced_motion="reduce")
            page.goto(url, wait_until="load")
            calm = page.evaluate(JS_REVEAL)
            asked = page.evaluate("() => matchMedia('(prefers-reduced-motion: reduce)').matches")
            still = calm["name"] == "none" and calm["clip"] in ("none", "") and not [a for a in calm["all"] if a["name"] == "reveal"]
            ck.put(R + "skipped with reduced motion", asked and still,
                   f"animation {calm['name']}, clip-path {calm['clip']!r}" + ("" if asked else " (the browser did not take over the reduced motion setting)"))
        finally:
            with contextlib.suppress(Exception):
                page.emulate_media(reduced_motion="null")

    return run_test(env, ck, vp, body)


# ----------------------------------------------------------------------------- JavaScript off (phone)

def test_nojs(env, slug):
    vp = "phone"
    N = "no-js: "
    plan = [
        (N + "five navigation links visible", "DESIGN", "Home, Gallery, Book Online, About, Contact drawn on the page, inside the screen width, not covered"),
        (N + "menu button hidden", "DESIGN", ".menu-btn not shown, it cannot work without the script"),
    ]
    if slug == "book-online":
        plan += [(N + "Book Now links call the phone", "PAGES", f"10 a.pill[data-book], and every [data-book] link has href {TEL}")]
    if slug == "gallery":
        plan += [(N + "gallery links point at the full-size images", "PAGES", "every .gallery a leads to images/NAME.jpg (the file exists) and its thumbnail is images/sm/NAME.jpg")]
    if slug == "contact":
        plan += [(N + "contact form hidden, phone and email links shown", "DESIGN",
                  f"#contact-form is not shown (it needs the script to open an email app), the sentence above it shows a link {TEL} and a link {MAILTO}"),
                 (N + "contact form has no action", "PAGES",
                  f"no action attribute (a mailto action makes browsers warn about an insecure form, decision 41), data-mailto is {MAILTO}"),
                 (N + "map link shown", "PAGES", "the map stays empty without the script, the Open in Google Maps link under it is shown")]
    plan += [(N + "no broken request", "PAGES", "clean")]
    ck = Checks(slug, vp, plan)

    def body(ctx, page, log):
        page.goto(env.url(slug), wait_until="load")
        if page.evaluate("() => document.documentElement.classList.contains('js')"):
            raise Stop("scripts ran although JavaScript is switched off in this test", "QA")
        vis = page.evaluate(JS_VIS, ["#main-nav a", True])
        labels = [v["text"] for v in vis]
        good = [v for v in vis if v["rendered"] and v["inX"] and v["hit"]]
        ok = labels == [label for label, _ in NAV] and len(good) == 5
        ck.put(N + "five navigation links visible", ok,
               "five links visible" if ok else (f"#main-nav has {len(vis)} links ({', '.join(labels)}); " if labels != [label for label, _ in NAV] else "") +
               "; ".join(f"{v['text']}: " + ("not shown" if not v["rendered"] else "outside the screen width" if not v["inX"] else "covered by " + (v["cover"] or "another element"))
                         for v in vis if v not in good),
               evidence=shot(page, f"check_behavior-nojs-{slug}-phone.png") if slug == "home" else "",
               owner="PAGES" if labels != [label for label, _ in NAV] else None)
        btn = page.evaluate(JS_VIS, [".menu-btn", True])
        ck.put(N + "menu button hidden", not any(b["rendered"] for b in btn), "not shown" if not any(b["rendered"] for b in btn) else f"shown at {btn[0]['box']}")

        if slug == "book-online":
            links = page.evaluate("() => Array.from(document.querySelectorAll('[data-book]')).map((a) => a.getAttribute('href'))")
            pills = page.locator("a.pill[data-book]").count()
            bad = [h for h in links if h != TEL]
            ck.put(N + "Book Now links call the phone", pills == 10 and not bad,
                   f"{pills} a.pill[data-book], {len(links)} [data-book] links" + (", all call the phone" if not bad else ", wrong href: " + ", ".join(repr(h) for h in bad[:4])))

        if slug == "gallery":
            links = page.evaluate(JS_GALLERY)
            bad = []
            for i, a in enumerate(links, 1):
                m = re.fullmatch(re.escape(env.base) + r"images/([^/?#]+)\.jpg", a["href"])
                if not m:
                    bad.append(f"link {i} leads to {a['href']}")
                    continue
                if norm_url(a["thumb"]) != f"{env.base}images/sm/{m.group(1)}.jpg":
                    bad.append(f"link {i} ({m.group(1)}.jpg) has the thumbnail {a['thumb'] or 'none'}")
                try:
                    r = fetch_patiently(lambda: ctx.request.head(a["href"]))
                    if r.status == 405:
                        r = fetch_patiently(lambda: ctx.request.get(a["href"]))
                    if r.status != 200 or not r.headers.get("content-type", "").startswith("image/"):
                        bad.append(f"link {i}: {a['href']} answers {r.status} {r.headers.get('content-type', '')}")
                except Exception as exc:
                    bad.append(f"link {i}: {a['href']} could not be fetched ({brief(exc)})")
            ck.put(N + "gallery links point at the full-size images", bool(links) and not bad,
                   f"{len(links)} links, each to an existing full-size image" if links and not bad else "; ".join(bad[:5]) or "no .gallery a links",
                   owner="ASSETS" if bad and all("answers" in b or "fetched" in b for b in bad) else None)

        if slug == "contact":
            f = page.evaluate(JS_FORM)
            if not f["form"]:
                ck.put(N + "contact form hidden, phone and email links shown", False, "the page has no #contact-form")
                ck.put(N + "contact form has no action", False, "the page has no #contact-form")
            else:
                form_vis = page.evaluate(JS_VIS, ["#contact-form", True])
                tel = page.evaluate(JS_VIS, [f".contact-intro a[href='{TEL}']", True])
                mail = page.evaluate(JS_VIS, [f".contact-intro a[href='{MAILTO}']", True])
                seen = lambda v: bool(v) and v[0]["rendered"] and v[0]["inX"] and v[0]["hit"]
                hidden = not any(v["rendered"] for v in form_vis)
                ck.put(N + "contact form hidden, phone and email links shown", hidden and seen(tel) and seen(mail),
                       "; ".join(["form hidden" if hidden else "the form is shown, but it cannot work without the script",
                                  "phone link shown" if seen(tel) else "no visible phone link in .contact-intro",
                                  "email link shown" if seen(mail) else "no visible email link in .contact-intro"]))
                ck.put(N + "contact form has no action", f["action"] is None and f["mailto"] == MAILTO,
                       f"action={f['action']!r}, data-mailto={f['mailto']!r}")
            link = page.evaluate(JS_VIS, [".map-open a", True])
            frame = page.evaluate("() => { const i = document.querySelector('.map iframe'); return i ? i.getAttribute('src') : 'no iframe'; }")
            ck.put(N + "map link shown", bool(link) and link[0]["rendered"] and link[0]["inX"] and frame is None,
                   "; ".join(["link shown" if link and link[0]["rendered"] else "no visible .map-open link",
                              "the frame stays empty" if frame is None else "the frame has src=%r" % frame]))

    return run_test(env, ck, vp, body, clean_check=N + "no broken request", java_script_enabled=False)


# ----------------------------------------------------------------------------- broken and old addresses

def test_broken(env, vp, layout="", tag=""):
    """layout: a few words put in front of every check name; tag: put into the name of the screenshot.
    Both are empty for the usual run and set by test_broken_at_root."""
    X = layout + "broken address: "
    O = layout + "old address: "
    plan = [
        (X + BROKEN + " shows the 404 page", "PAGES", "status 404, div.notfound with its h1, the address stays as typed"),
        (X + "stylesheet loads on the 404 page", "PAGES", "css/style.css is fetched from the site root with status 200 and is in use"),
        (X + "script and logo load on the 404 page", "PAGES", "js/site.js is fetched from the site root with status 200, the logo is drawn"),
        (X + "navigation links lead to the right pages", "PAGES", "the five links of #main-nav lead to the five pages of the site"),
        (X + "Home button leads to the home page", "PAGES", ".notfound a.btn opens the home page"),
        (X + "no script error", "INTERACTION", "clean"),
    ] + [(O + path + " ends on the Book Online page", "PAGES", "the browser ends on book-online/ and that page answers 200") for path in OLD_ADDRESSES]
    ck = Checks("404", vp, plan)
    home, book = env.url("home"), env.url("book-online")

    def visits(page, log, answers, docs):
        resp = page.goto(env.base + BROKEN, wait_until="load")
        page.wait_for_timeout(400)          # a redirect that should not happen would show up by now
        with contextlib.suppress(Exception):
            page.wait_for_load_state("load")
        status = docs[0][1] if docs else (resp.status if resp else None)
        info = page.evaluate(JS_404)
        stayed = norm_url(info["url"]) == env.base + BROKEN
        is_404 = status == 404 and info["notfound"] == 1 and bool(info["h1"]) and stayed
        ck.put(X + BROKEN + " shows the 404 page", is_404,
               f"status {status}, {info['notfound']} div.notfound" + (f" with h1 {info['h1']!r}" if info["h1"] else "") +
               ("" if stayed else f", the browser moved to {info['url']}"),
               evidence=shot(page, f"check_behavior-404-deep-{tag}{vp}.png"))

        css, js, images = env.base + "css/style.css", env.base + "js/site.js", env.base + "images/"
        css_status = [s for u, s in answers if norm_url(u) == css]
        in_use = [s for s in info["sheets"] if s["href"] and norm_url(s["href"]) == css]
        css_ok = 200 in css_status and any(s["rules"] > 0 for s in in_use)
        stray = sorted({u.replace(env.base, "/") for u, s in answers if s >= 400 and norm_url(u) != env.base + BROKEN})
        ck.put(X + "stylesheet loads on the 404 page", css_ok,
               ("css/style.css from the site root: " + (", ".join(str(s) for s in css_status) or "never asked for")) +
               ("; in use with " + str(max(s["rules"] for s in in_use)) + " rules" if in_use else
                "; stylesheets of the page: " + (", ".join((s["href"] or "inline").replace(env.base, "/") for s in info["sheets"]) or "none")),
               evidence=(f"button background {info['btn']['background']}; " if info["btn"] else "") + (f"other addresses that answered 404 on the way: {stray}" if stray else ""))
        js_status = [s for u, s in answers if norm_url(u) == js]
        logo_ok = bool(info["logo"]) and info["logo"]["natural"] > 0 and norm_url(info["logo"]["src"]).startswith(images)
        ck.put(X + "script and logo load on the 404 page", 200 in js_status and logo_ok,
               "js/site.js from the site root: " + (", ".join(str(s) for s in js_status) or "never asked for") + "; logo " +
               ("drawn" if logo_ok else "not drawn" + (f" (asked for {info['logo']['src'].replace(env.base, '/')})" if info["logo"] else " (no .logo img)")))

        vis = page.evaluate(JS_VIS, ["#main-nav a", False])
        got = [(v["text"], norm_url(v["href"])) for v in vis]
        want = [(label, env.url(target)) for label, target in NAV]
        ck.put(X + "navigation links lead to the right pages", got == want,
               "as expected" if got == want else ", ".join(f"{t} -> {h}" for t, h in got) or "no links in #main-nav")

        if not info["btn"]:
            ck.put(X + "Home button leads to the home page", False, "no .notfound a.btn on the page")
        elif norm_url(info["btn"]["href"]) != home:
            ck.put(X + "Home button leads to the home page", False, f"the button has href {info['btn']['attr']!r}, which leads to {info['btn']['href']}")
        else:
            try:
                press(vp, page.locator(".notfound a.btn"))
                arrived = poll(page, lambda: page.url, lambda u: norm_url(u) == home, 8000, default="")
                with contextlib.suppress(Exception):
                    page.wait_for_load_state("load")
                ck.put(X + "Home button leads to the home page", norm_url(arrived) == home and bool(docs) and docs[-1][1] == 200,
                       f"a click opens {norm_url(page.url)} (status {docs[-1][1] if docs else 'unknown'})")
            except Exception as exc:
                ck.put(X + "Home button leads to the home page", False, "the button could not be clicked: " + brief(exc), owner="DESIGN")

        errors = [one_line(e, 200) for e in log.get("pageerrors", [])] + \
                 [one_line(c["text"], 200) for c in log.get("console", []) if c["type"] == "error" and not c["text"].startswith("Failed to load resource")]
        ck.put(X + "no script error", not errors, "clean" if not errors else "; ".join(errors[:5]))

        for path in OLD_ADDRESSES:
            check = O + path + " ends on the Book Online page"
            try:
                page.goto("about:blank")
                del docs[:]
                page.goto(env.base + path, wait_until="commit")
                arrived = poll(page, lambda: page.url, lambda u: norm_url(u) == book, 8000, default="")
                with contextlib.suppress(Exception):
                    page.wait_for_load_state("load")
                ok = norm_url(arrived) == book and bool(docs) and docs[-1][1] == 200
                ck.put(check, ok, f"the browser ends on {norm_url(page.url)}" + (f" (status {docs[-1][1]})" if docs else ""),
                       evidence="documents on the way: " + ", ".join(f"{u.replace(env.base, '/')} {s}" for u, s in docs))
            except Exception as exc:
                ck.put(check, False, brief(exc))

    def body(ctx, page, log):
        answers, docs = [], []          # every answer, and the answers for the documents the page itself loads

        def on_response(r):
            answers.append((r.url, r.status))
            try:
                if r.request.is_navigation_request() and r.frame == page.main_frame:
                    docs.append((r.url, r.status))
            except Exception:
                pass
        page.on("response", on_response)
        try:
            visits(page, log, answers, docs)
        finally:
            with contextlib.suppress(Exception):
                page.remove_listener("response", on_response)

    return run_test(env, ck, vp, body)


ROOT_LAYOUT = "site at the top of the host: "


def test_broken_at_root(env, vp):
    """The same tests once more with the site served at the top of the host, the layout of www.hairbygerta.com
    (the usual run serves it under /hairbygerta/, the layout of the GitHub Pages address). The 404 page has to find
    the site root in both. Local runs only: with --base the layout is the one of that address."""
    if not env.local:
        return []
    with common.site_server(prefix="/") as base:
        root = Env(env.p, env.browser, base, env.shared)
        try:
            entries = scrub(test_broken(root, vp, ROOT_LAYOUT, "root-"), base)
        finally:
            env.trouble = env.trouble or root.trouble
            root.close()
    return entries


# ----------------------------------------------------------------------------- running it all

def build_tasks(pages, viewports):
    """-> list of (label, page, viewport, function(env)). Slow tests first, so the browsers share the work evenly."""
    tasks = []
    for vp in viewports:
        if "home" in pages:
            tasks.append((f"reveal {vp}", "home", vp, lambda env, vp=vp: test_reveal(env, vp)))
        if "gallery" in pages:
            tasks.append((f"lightbox {vp}", "gallery", vp, lambda env, vp=vp: test_lightbox(env, vp)))
        if "contact" in pages:
            tasks.append((f"contact form {vp}", "contact", vp, lambda env, vp=vp: test_contact_form(env, vp)))
        if "404" in pages:
            tasks.append((f"broken addresses {vp}", "404", vp, lambda env, vp=vp: test_broken(env, vp)))
            tasks.append((f"broken addresses at the top of the host {vp}", "404", vp, lambda env, vp=vp: test_broken_at_root(env, vp)))
        if "book-online" in pages:
            tasks.append((f"book now {vp}", "book-online", vp, lambda env, vp=vp: test_book_now(env, vp)))
        if "home" in pages:
            tasks.append((f"call and text {vp}", "home", vp, lambda env, vp=vp: test_home_links(env, vp)))
    for vp in viewports:
        for slug in pages:
            tasks.append((f"menu and year {slug} {vp}", slug, vp, lambda env, vp=vp, slug=slug: test_page(env, vp, slug)))
    if "phone" in viewports:
        for slug in pages:
            tasks.append((f"no-js {slug}", slug, "phone", lambda env, slug=slug: test_nojs(env, slug)))
    return tasks


def run_tasks(tasks, base_arg, jobs, shared):
    """Each worker thread has its own Playwright and its own browser (the sync API must not be shared between
    threads), and, when no --base is given, its own local server, so the browsers do not queue up at one server."""
    todo = queue.Queue()
    for item in enumerate(tasks):
        todo.put(item)
    results, trouble, bases, timing = {}, [], [], shared["timing"]

    def worker():
        try:
            with common.target_base(base_arg) as base, sync_playwright() as p:
                bases.append(base)
                browser = p.chromium.launch()
                env = Env(p, browser, base, shared)
                timing.append((round(time.monotonic() - shared["started"], 1), "worker ready (server and browser started), seconds after the start"))
                try:
                    while True:
                        try:
                            index, (label, _slug, _vp, fn) = todo.get_nowait()
                        except queue.Empty:
                            break
                        try:
                            began = time.monotonic()
                            for attempt in (1, 2):
                                env.trouble = False
                                entries = fn(env)
                                if not env.trouble:
                                    break       # otherwise once more: a request to the site failed on the way
                            results[index] = scrub(entries, base)
                            timing.append((round(time.monotonic() - began, 1), label + (" (run twice)" if attempt == 2 else "")))
                        except Exception as exc:        # a test function never raises, this is the last safety net
                            trouble.append(f"{label}: {brief(exc)}")
                finally:
                    timing.append((round(time.monotonic() - shared["started"], 1), "worker out of tests, seconds after the start"))
                    with contextlib.suppress(Exception):
                        env.close()
                    with contextlib.suppress(Exception):
                        browser.close()
        except Exception as exc:
            trouble.append("browser or server: " + brief(exc))

    threads = [threading.Thread(target=worker, daemon=True) for _ in range(max(1, min(jobs, len(tasks))))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    entries = [e for index in sorted(results) for e in results[index]]
    missing = [tasks[i][:3] for i in range(len(tasks)) if i not in results]
    return entries, missing, trouble, (sorted(bases)[0] if bases else (base_arg or ""))


def scrub(value, base):
    """Nothing in the report may name a folder of this computer. Addresses are written from the site root."""
    if isinstance(value, str):
        value = value.replace(base, "/")
        for folder, word in ((common.SITE, "<site>"), (common.ENV, "<tools>"), (common.PARENT, "<parent>")):
            for form in {folder, folder.replace("\\", "/"), folder.replace("/", "\\")}:
                value = value.replace(form, word)
        return value
    if isinstance(value, list):
        return [scrub(v, base) for v in value]
    if isinstance(value, dict):
        return {k: scrub(v, base) for k, v in value.items()}
    return value


def main():
    ap = common.cli_parser("Behaviour tests on the real pages (menu, photo viewer, booking, contact form, hours line, no JavaScript, broken addresses).")
    ap.add_argument("--jobs", type=int, default=4, help="browsers working side by side (default 4)")
    ap.add_argument("--timing", action="store_true", help="also print the seconds each test took, slowest first")
    args = ap.parse_args()
    pages = common.cli_pages(ap, args.page)
    viewports = common.parse_viewports(args.viewport)
    started = time.monotonic()
    shared = {"year": datetime.date.today().year, "blocked_expected": set(), "timing": [], "started": started}
    tasks = build_tasks(pages, viewports)
    entries, missing, trouble, base = run_tasks(tasks, args.base, args.jobs, shared)
    for label, slug, vp in missing:     # under the page and viewport of the test, so the next run of that page replaces the entry
        entries.append({"page": slug, "viewport": vp, "check": f"test could run: {label}", "ok": False, "expected": "the test runs",
                        "actual": scrub("; ".join(trouble) or "the test did not run", base), "evidence": "", "owner": "QA"})
    # Every earlier entry of the pages and viewports of this run is replaced (see common.save_report): a "test could
    # run" entry has no successor when the test runs again, and would stay in the report for ever.
    covered = {(slug, vp) for slug in pages for vp in viewports}
    doc = common.save_report(NAME, entries, common.report_base(args.base), extra={
        "script": "qa/check_behavior.py",
        "tested": {"pages": pages, "viewports": viewports},
        "blocked_as_planned": sorted(shared["blocked_expected"]),
        "note": "Addresses are written from the site root. Blocked requests to Google Maps are planned and are not failures."},
        replace=covered)
    if args.timing:
        for seconds, label in sorted(shared["timing"], reverse=True):
            print(f"{seconds:6.1f} s  {label}")
    failed = [e for e in entries if not e["ok"]]
    for e in failed:
        print(f"FAIL {e['page']} [{e['viewport']}] {e['check']}: {one_line(e['actual'], 300)} | expected: {one_line(e['expected'], 200)} | owner: {e['owner']}")
    print(f"{NAME}: {len(entries)} checks, {len(entries) - len(failed)} passed, {len(failed)} failed, "
          f"{time.monotonic() - started:.0f} s. Report: qa/reports/{NAME}.json" + ("" if doc.get("ok") or failed else " (the report also holds older failed entries)"))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
