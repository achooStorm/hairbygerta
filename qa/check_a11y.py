"""Accessibility check with axe-core.

Run it with the Python of the tools folder (it has Playwright):

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_a11y.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_a11y.py --page gallery,contact --viewport phone
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_a11y.py --base https://achoostorm.github.io/hairbygerta/

What it does
  Opens every page at both viewports, brings it into each state below, injects axe-core (common.AXE_JS)
  and runs the rules tagged wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa and best-practice.
  Google Fonts are let through, and the script waits for them, so contrast and text size are judged on the real fonts.

States
  base           every page, desktop and phone
  menu-open      every page, phone only (after a click on .menu-btn; on a wide screen there is no menu button)
  lightbox-open  gallery, desktop and phone (after a click on the first photo)
  form-blocked   contact, desktop and phone (Send clicked on the empty form, the required email field stops it)
  form-sent      contact, desktop and phone (test values typed in, Send clicked, status line shown)
  Every state starts from a fresh page load. The form never sends anything: the mail link the script builds is
  caught before it can open a mail program.

Report (qa/reports/check_a11y.json, shared format)
  axe:<state>            one entry per page, viewport and state. ok when the page loaded cleanly, the state was
                         reached and axe ran. Its evidence lists what axe could not decide (needs_review),
                         the fonts that loaded and the blocked requests.
  axe:<state>:<rule id>  one entry per violated rule, with impact, help address and up to five offending
                         selectors with their failure summary. ok is false for impact serious or critical.
                         Moderate and minor ones are reported with ok true and a note.
  In a state other than base, elements that fail only in that state are listed first, and an entry whose
  elements all fail in the base state too says so.

Not analysed
  The Google map frame on the contact page. The network rule blocks it, so axe runs with iframes off.
  The iframe element itself (for example its title) is still checked as part of the contact page.

Speed
  The pages are shared out over several browsers that work at the same time (--jobs N, default 4). Without --base
  every browser gets its own local server (common.site_server), so no server has to answer more than one browser.
  A scan in which a connection to the server failed is repeated, up to three more times and with all other browsers
  waiting, before it counts as a failure. A state that was not reached after a click is tried once more the same way.
  A missing file is never repeated away: the server answers it with status 404, which is reported at once.

Extra switches: --jobs N, --no-shots (no screenshots of the menu, lightbox and form states).
Exit code 0 when no entry of this run failed, 1 otherwise.
"""
import contextlib, copy, os, queue, sys, threading, time
from urllib.parse import urlsplit

sys.dont_write_bytecode = True  # no __pycache__ in the site folder (a compiled file would carry the path of this computer)

from playwright.sync_api import sync_playwright

import common
from common import PAGES, VIEWPORTS, context_options, guard, watch, is_expected_external, save_report, parse_viewports

NAME = "check_a11y"
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"]
BLOCKING = ("serious", "critical")
SEVERITY = {"critical": 0, "serious": 1, "moderate": 2, "minor": 3}
MAX_NODES = 5
WEB_FONTS = ("Bodoni Moda", "Figtree")
STATES = ("base", "menu-open", "lightbox-open", "form-blocked", "form-sent")
# Generous on purpose: the whole QA suite may be running at the same time and the computer may be slow.
NAV_TIMEOUT = 60000
ACTION_TIMEOUT = 15000
STATE_TIMEOUT = 10000
RETRIES = 3  # extra tries for a scan in which a connection to the server failed
FORM_VALUES = {"first-name": "Test", "last-name": "Visitor", "email": "visitor@example.com", "message": "Accessibility check. Please ignore."}

# Who most likely has to fix a violated rule. A best guess from the rule and from where the elements sit.
DESIGN_RULES = {"color-contrast", "color-contrast-enhanced", "link-in-text-block", "target-size", "avoid-inline-spacing", "css-orientation-lock"}
CONTENT_RULES = {"document-title", "image-redundant-alt"}
CONTENT_RULES_IN_LEGAL = {"heading-order", "empty-heading"}

STATE_TEXT = {
    "base": "the page as it loads",
    "menu-open": "phone menu open (after a click on .menu-btn)",
    "lightbox-open": "lightbox open (after a click on the first photo)",
    "form-blocked": "contact form after Send was clicked on the empty form",
    "form-sent": "contact form after a valid message was sent",
}
NOT_ANALYSED = [
    "The Google map frame on the contact page. The network rule blocks every host except the site's own and Google Fonts, "
    "so the map never loads and axe runs with iframes off. The iframe element itself (for example its title) is still checked.",
    "What axe-core cannot decide by itself. It is listed as needs_review in each axe:<state> entry, needs a human look and is not a failure.",
    "The browser's own message bubble on the blocked contact form. The browser draws it, not the page.",
]

# Runs before any script of the page. Catches the mail link the contact form builds, so no mail program can open,
# and counts submit events. It changes nothing a visitor or a screen reader would notice.
INIT_JS = r"""(() => {
  const qa = window.__qa = {mailto: [], submits: 0};
  const click = HTMLAnchorElement.prototype.click;
  HTMLAnchorElement.prototype.click = function () {
    const href = this.getAttribute('href') || '';
    if (/^mailto:/i.test(href)) { qa.mailto.push(href); return; }
    return click.apply(this, arguments);
  };
  const open = window.open;
  window.open = function (url) {
    if (typeof url === 'string' && /^mailto:/i.test(url)) { qa.mailto.push(url); return null; }
    return open.apply(this, arguments);
  };
  document.addEventListener('submit', () => { qa.submits += 1; }, true);
})();"""

# Wait for the web fonts and for every transition or animation that ends by itself (the endless marquee is left alone),
# so axe never measures a colour halfway through a fade.
SETTLE_JS = r"""async () => {
  try { await Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 8000))]); } catch (e) {}
  const end = Date.now() + 4000;
  let busy = 0;
  for (;;) {
    busy = 0;
    try {
      busy = document.getAnimations().filter((a) => {
        if (a.playState !== 'running' && !a.pending) return false;
        const t = a.effect && a.effect.getComputedTiming ? a.effect.getComputedTiming() : null;
        return !t || Number.isFinite(t.endTime);
      }).length;
    } catch (e) {}
    if (!busy || Date.now() > end) break;
    await new Promise((r) => setTimeout(r, 60));
  }
  await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  const fonts = {};  // family -> how many of its faces are loaded, unloaded (not needed by this page), loading or error
  try {
    for (const f of document.fonts) {
      const family = f.family.replace(/["']/g, '');
      fonts[family] = fonts[family] || {};
      fonts[family][f.status] = (fonts[family][f.status] || 0) + 1;
    }
  } catch (e) {}
  return {fonts: fonts, unfinished_animations: busy};
}"""

AXE_RUN_JS = r"""async (o) => {
  const area = (sel) => {
    let el = null;
    try { el = document.querySelector(sel); } catch (e) {}
    if (!el) return '';
    if (el.closest('.lightbox')) return 'lightbox';
    if (el.closest('#contact-form')) return 'form';
    if (el.closest('.site-header')) return 'header';
    if (el.closest('.site-footer')) return 'footer';
    if (el.closest('article.legal')) return 'legal';
    return 'main';
  };
  const flat = (t) => (t || []).map((p) => Array.isArray(p) ? p.join(' >>> ') : String(p)).join(' | ');
  const first = (t) => { const p = (t || [])[0]; return Array.isArray(p) ? String(p[0]) : String(p || ''); };
  const text = (n) => (n.failureSummary || [].concat(n.any || [], n.all || [], n.none || []).map((c) => c.message).join('; ') || '').replace(/\s+/g, ' ').trim();
  const pack = (v) => ({
    id: v.id, impact: v.impact || null, help: v.help, helpUrl: v.helpUrl, tags: v.tags,
    nodes: v.nodes.map((n) => ({selector: flat(n.target), area: area(first(n.target)), summary: text(n), html: (n.html || '').replace(/\s+/g, ' ').slice(0, 200)})),
  });
  const r = await axe.run(document, {runOnly: {type: 'tag', values: o.tags}, iframes: false, resultTypes: ['violations', 'incomplete']});
  return {version: (r.testEngine && r.testEngine.version) || axe.version, violations: r.violations.map(pack), incomplete: r.incomplete.map(pack),
          passes: r.passes.length, inapplicable: r.inapplicable.length};
}"""

MENU_INFO_JS = r"""() => {
  const vis = (e) => {
    if (!e) return false;
    const r = e.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0 || r.bottom <= 0 || r.right <= 0 || r.top >= innerHeight || r.left >= innerWidth) return false;
    return e.checkVisibility ? e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) : getComputedStyle(e).visibility !== 'hidden';
  };
  const btn = document.querySelector('.menu-btn'), nav = document.getElementById('main-nav');
  const links = nav ? [...nav.querySelectorAll('a')] : [];
  return {button: !!btn, button_visible: vis(btn), aria_expanded: btn ? btn.getAttribute('aria-expanded') : null,
          nav: !!nav, nav_class: nav ? nav.className : null, body_class: document.body.className,
          links: links.length, links_visible: links.filter(vis).length};
}"""

LIGHTBOX_INFO_JS = r"""() => {
  const box = document.querySelector('.lightbox');
  if (!box) return {lightbox: false, body_class: document.body.className};
  const img = box.querySelector('img'), a = document.activeElement, count = box.querySelector('.lb-count');
  const name = (e) => e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\s+/).join('.') : '');
  return {lightbox: true, class: box.className, role: box.getAttribute('role'), aria_modal: box.getAttribute('aria-modal'),
          aria_label: box.getAttribute('aria-label'), body_class: document.body.className,
          image: img ? (img.getAttribute('src') || '') : null, image_loaded: !!(img && img.complete && img.naturalWidth > 0),
          image_alt: img ? img.getAttribute('alt') : null, count: count ? count.textContent.trim() : null,
          focus: a && a !== document.body ? name(a) : null, focus_inside: !!(a && box.contains(a))};
}"""

FORM_INFO_JS = r"""() => {
  const f = document.querySelector('#contact-form');
  if (!f) return {form: false};
  const note = document.querySelector('.form-note'), a = document.activeElement, qa = window.__qa || {mailto: [], submits: 0};
  const email = f.querySelector('#email');
  return {form: true, submit_button: !!f.querySelector('button[type=submit], input[type=submit]'),
          novalidate: f.noValidate, valid: f.matches(':valid'), email_required: !!(email && email.required),
          note: note ? note.textContent.trim() : null, note_role: note ? note.getAttribute('role') : null,
          sent_text: f.getAttribute('data-sent') || '', mail_links_opened: qa.mailto.length, submit_events: qa.submits,
          aria_invalid: [...f.querySelectorAll('[aria-invalid="true"]')].map((e) => e.id || e.name || e.tagName.toLowerCase()),
          focus: a && a !== document.body ? (a.id ? '#' + a.id : a.tagName.toLowerCase()) : null,
          missing_fields: ['first-name', 'last-name', 'email', 'message'].filter((id) => !f.querySelector('#' + id))};
}"""

SUBMIT = "#contact-form button[type=submit], #contact-form input[type=submit]"


def first_line(e):
    text = str(e).strip()
    return (text.splitlines()[0] if text else type(e).__name__)[:300]


def squash(text, limit=0):
    text = " ".join(str(text or "").split())
    return text[:limit - 3] + "..." if limit and len(text) > limit else text


def states_for(slug, viewport):
    states = ["base"]
    if viewport == "phone":
        states.append("menu-open")
    if slug == "gallery":
        states.append("lightbox-open")
    if slug == "contact":
        states += ["form-blocked", "form-sent"]
    return states


# ---------------------------------------------------------------- bringing a page into a state
# Each function returns (reached, why not, owner of the problem, what was seen).

def setup_base(page):
    return True, "", "", {}


def setup_menu(page):
    info = page.evaluate(MENU_INFO_JS)
    if not info["button"]:
        return False, "there is no .menu-btn in the page", "PAGES", info
    if not info["nav"]:
        return False, "there is no #main-nav in the page", "PAGES", info
    if not info["button_visible"]:
        return False, "the menu button (.menu-btn) is not visible at phone width", "DESIGN", info
    if info["aria_expanded"] != "true":
        page.locator(".menu-btn").first.click(timeout=ACTION_TIMEOUT)
    try:
        page.wait_for_function("() => { const b = document.querySelector('.menu-btn'); return !!b && b.getAttribute('aria-expanded') === 'true'; }", timeout=STATE_TIMEOUT)
    except Exception:
        return False, 'aria-expanded on .menu-btn did not become "true" after a click', "INTERACTION", page.evaluate(MENU_INFO_JS)
    page.evaluate(SETTLE_JS)
    info = page.evaluate(MENU_INFO_JS)
    if not info["links_visible"]:
        return False, "aria-expanded is true but no link of #main-nav is visible on screen", "DESIGN", info
    return True, "", "", info


def setup_lightbox(page):
    links = page.locator(".gallery a")
    count = links.count()
    if not count:
        return False, "there is no .gallery a link in the page", "PAGES", {"links": 0}
    before = page.url
    links.first.click(timeout=ACTION_TIMEOUT)
    try:
        page.wait_for_selector(".lightbox.open", state="visible", timeout=STATE_TIMEOUT)
    except Exception:
        if page.url != before:
            return False, "the click on the first photo left the page (now at %s) and opened no lightbox" % urlsplit(page.url).path, "INTERACTION", {"links": count}
        return False, "no visible .lightbox.open after a click on the first photo", "INTERACTION", dict(page.evaluate(LIGHTBOX_INFO_JS), links=count)
    try:
        page.wait_for_function("() => { const i = document.querySelector('.lightbox img'); return !i || (i.complete && i.naturalWidth > 0); }", timeout=STATE_TIMEOUT)
    except Exception:
        pass
    return True, "", "", dict(page.evaluate(LIGHTBOX_INFO_JS), links=count)


def _form_ready(page):
    info = page.evaluate(FORM_INFO_JS)
    if not info["form"]:
        return "there is no #contact-form in the page", info
    if not info["submit_button"]:
        return "#contact-form has no submit button", info
    return "", info


def setup_form_blocked(page):
    why, info = _form_ready(page)
    if why:
        return False, why, "PAGES", info
    button = page.locator(SUBMIT).first
    button.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT)
    button.click(timeout=ACTION_TIMEOUT)
    page.wait_for_timeout(400)
    info = page.evaluate(FORM_INFO_JS)
    if info["valid"]:
        return False, "the empty form counts as valid (no required field), so nothing blocks the submit", "PAGES", info
    if info["mail_links_opened"] or (info["sent_text"] and info["note"] == info["sent_text"]):
        return False, "the empty form was sent although the required email field is empty", "INTERACTION", info
    return True, "", "", info


def setup_form_sent(page):
    why, info = _form_ready(page)
    if why:
        return False, why, "PAGES", info
    if "email" in info["missing_fields"]:
        return False, "#contact-form has no #email field", "PAGES", info
    before = info["note"] or ""
    for field, value in FORM_VALUES.items():
        box = page.locator("#contact-form #" + field)
        if box.count():
            box.first.fill(value, timeout=ACTION_TIMEOUT)
    button = page.locator(SUBMIT).first
    button.scroll_into_view_if_needed(timeout=ACTION_TIMEOUT)
    button.click(timeout=ACTION_TIMEOUT)
    try:
        page.wait_for_function("(before) => { const n = document.querySelector('.form-note'); const t = n ? n.textContent.trim() : ''; return t.length > 0 && t !== before; }",
                               arg=before, timeout=STATE_TIMEOUT)
    except Exception:
        return False, "no status line appeared in .form-note after a valid form was sent", "INTERACTION", page.evaluate(FORM_INFO_JS)
    return True, "", "", page.evaluate(FORM_INFO_JS)


SETUP = {"base": setup_base, "menu-open": setup_menu, "lightbox-open": setup_lightbox, "form-blocked": setup_form_blocked, "form-sent": setup_form_sent}


class Tab:
    """One browser tab per worker and viewport, used again for every scan. Opening a tab is the slow part
    (seconds on some computers); loading the page anew in the same tab gives the same clean start."""

    def __init__(self, browser, p, base, viewport):
        self.base = base
        self.ctx = browser.new_context(**context_options(p, viewport, dsf=1))
        guard(self.ctx, {}, base, allow_fonts=True)  # safety net for anything the rule on the tab would miss
        self.page = None
        self.log = {}
        self.down = False  # the last scan could not load its page at all, on any try

    def drop(self):
        """Close the tab. The next scan opens a new one (used when a scan stopped with an error)."""
        page, self.page = self.page, None
        if page is not None:
            for step in (lambda: page.unroute_all(behavior="ignoreErrors"), page.close):
                try:
                    step()
                except Exception:
                    pass

    def blank(self):
        """Leave the document of the last scan and start with an empty log. Returns the tab's page."""
        if self.page is not None and not self.page.is_closed():
            left = False
            for _ in range(3):
                try:
                    self.page.goto("about:blank", timeout=NAV_TIMEOUT)
                    self.page.mouse.move(1, 1)
                    left = True
                    break
                except Exception:
                    time.sleep(0.2)  # after a failed load the browser may still be putting up its error page
            if not left:
                self.drop()
        if self.page is None or self.page.is_closed():
            self.log = {}
            self.page = self.ctx.new_page()
            guard(self.page, self.log, self.base, allow_fonts=True)
            watch(self.page, self.log)
            self.page.add_init_script(INIT_JS)
        self.log.clear()  # the same dict stays wired to the tab
        return self.page


def run_state(tab, slug, viewport, state, axe_src, shots_dir):
    """Load the page anew, bring it into the state, run axe. Returns a plain record, never raises."""
    rec = {"state": state, "url": tab.base + PAGES[slug], "status": None, "reached": False, "why": "", "owner": "", "detail": {},
           "axe": None, "error": "", "log": {}, "net": {}, "settle": {}, "shot": "", "load_error": False, "unsure": False, "attempts": 1}
    try:
        page = tab.blank()
        try:
            response = page.goto(rec["url"], wait_until="load", timeout=NAV_TIMEOUT)
        except Exception as e:
            rec["why"], rec["owner"], rec["load_error"] = "the page did not load: " + first_line(e), "PAGES", True
            return rec
        rec["status"] = response.status if response else None
        if rec["status"] and rec["status"] >= 400:
            rec["why"], rec["owner"] = "the page answered with HTTP status %d" % rec["status"], "PAGES"
            return rec
        rec["settle"] = page.evaluate(SETTLE_JS)
        try:
            reached, why, owner, detail = SETUP[state](page)
        except Exception as e:
            reached, why, owner, detail = False, "the state could not be reached: " + first_line(e), "INTERACTION", {}
        rec.update(reached=reached, why=why, owner=owner, detail=detail)
        if not reached:
            rec["unsure"] = owner == "INTERACTION"  # the page did not react in time: on a slow computer worth a second look
            return rec
        if state != "base":
            page.mouse.move(1, 1)  # no hover style left on whatever was clicked
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        rec["settle"] = page.evaluate(SETTLE_JS)
        page.evaluate(axe_src)
        if not page.evaluate("() => typeof window.axe === 'object' && !!window.axe && typeof window.axe.run === 'function'"):
            page.add_script_tag(content=axe_src)
        rec["axe"] = page.evaluate(AXE_RUN_JS, {"tags": TAGS})
        if shots_dir and state != "base":
            try:
                os.makedirs(shots_dir, exist_ok=True)
                shot = os.path.join(shots_dir, "%s-%s-%s-%s.png" % (NAME, slug, viewport, state))
                page.screenshot(path=shot, full_page=False)
                rec["shot"] = shot
            except Exception:
                pass
    except Exception as e:
        rec["error"] = "%s: %s" % (type(e).__name__, first_line(e))
    finally:
        rec["log"] = copy.deepcopy(tab.log)  # a copy: the tab goes on to the next scan
        rec["net"] = classify(rec["log"], rec["url"], bool(rec["status"] and rec["status"] >= 400))
    return rec


class Gate:
    """Scans run side by side. A scan that is repeated after a failed connection runs alone: a server that could not
    keep up with several browsers then has to answer only one."""

    def __init__(self):
        self.cond = threading.Condition()
        self.running = 0   # scans in progress side by side
        self.waiting = 0   # repeated scans waiting to run alone
        self.alone = False

    @contextlib.contextmanager
    def together(self):
        with self.cond:
            while self.alone or self.waiting:
                self.cond.wait()
            self.running += 1
        try:
            yield
        finally:
            with self.cond:
                self.running -= 1
                self.cond.notify_all()

    @contextlib.contextmanager
    def by_itself(self):
        with self.cond:
            self.waiting += 1
            while self.alone or self.running:
                self.cond.wait()
            self.waiting -= 1
            self.alone = True
        try:
            yield
        finally:
            with self.cond:
                self.alone = False
                self.cond.notify_all()


def run_state_steady(tab, gate, slug, viewport, state, axe_src, shots_dir):
    """run_state, repeated when a connection failed or the scan stopped
    (a busy server, a network hiccup or a crashed tab, not a defect of the site)."""
    tries = 1 if tab.down else RETRIES + 1  # a server that is plainly not there is not asked four times for every scan
    for attempt in range(1, tries + 1):
        with gate.together() if attempt == 1 else gate.by_itself():
            rec = run_state(tab, slug, viewport, state, axe_src, shots_dir)
        rec["attempts"] = attempt
        if rec["error"]:
            tab.drop()  # the tab may be broken: the next scan opens a new one
        shaky = rec["load_error"] or rec["net"]["failed"] or rec["error"] or (rec["unsure"] and attempt == 1)
        if not shaky or attempt == tries:
            break
        time.sleep(0.3 * attempt)
    tab.down = rec["load_error"]
    return rec


# ---------------------------------------------------------------- turning records into report entries

def owner_for_url(url):
    ext = os.path.splitext(urlsplit(url).path)[1].lower()
    if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".ico"):
        return "ASSETS"
    if ext == ".css":
        return "DESIGN"
    if ext == ".js":
        return "INTERACTION"
    return "PAGES"


def classify(log, main_url, main_failed):
    """Sort the network log into what is expected and what is a real problem."""
    blocked = list(dict.fromkeys(log.get("blocked", [])))
    blocked_set = set(blocked)
    out = {"blocked_expected": [u for u in blocked if is_expected_external(u)],
           "blocked_unexpected": [u for u in blocked if not is_expected_external(u)],
           "bad_status": [], "failed": [], "cancelled": [], "font_failed": []}
    seen = set()
    for b in log.get("bad_status", []):
        key = (b.get("url"), b.get("status"))
        if key in seen or (main_failed and b.get("url") == main_url):
            continue
        seen.add(key)
        out["bad_status"].append({"url": b.get("url"), "status": b.get("status")})
    for f in log.get("failed", []):
        url, error = f.get("url") or "", str(f.get("error") or "")
        if url in blocked_set or not url.startswith(("http://", "https://")):
            continue  # stopped by the network rule (listed above), or not a web request at all (a mail link)
        item = {"url": url, "error": error}
        if (urlsplit(url).hostname or "") in common.FONT_HOSTS:
            out["font_failed"].append(item)  # no way to Google Fonts from here: a network matter, not a site defect
        elif "ERR_ABORTED" in error:
            out["cancelled"].append(item)  # the page itself dropped the request, nothing is missing
        elif item not in out["failed"]:
            out["failed"].append(item)
    return out


def owner_for_rule(rule, nodes, state, only_in_state):
    if rule in DESIGN_RULES:
        return "DESIGN"
    areas = {n.get("area") for n in nodes if n.get("area")}
    if areas == {"lightbox"}:
        return "INTERACTION"  # the lightbox is built by js/site.js
    if state != "base" and only_in_state:
        return "INTERACTION"  # clean in the base state, so the script's change of the page brings it in
    if rule in CONTENT_RULES or (rule in CONTENT_RULES_IN_LEGAL and areas == {"legal"}):
        return "CONTENT"
    return "PAGES"


def rel_to_site(path):
    try:
        rel = os.path.relpath(path, common.SITE).replace("\\", "/")
    except ValueError:
        return os.path.basename(path)
    return os.path.basename(path) if rel.startswith("..") else rel


def build_entries(base, slug, viewport, recs):
    def short(text):
        """Addresses of the site without the server part: the port of a local server changes with every run."""
        return str(text).replace(base, "/")

    entries = []
    base_fail = None  # rule id -> selectors of the elements failing in the base state; None when base was not analysed
    for rec in recs:
        state, axe = rec["state"], rec["axe"]
        net = {key: [short(v) if isinstance(v, str) else dict(v, url=short(v["url"])) for v in values] for key, values in rec["net"].items()}
        problems = []
        if rec["error"]:
            problems.append(("the scan stopped: " + rec["error"], "QA"))
        if not rec["reached"] and rec["why"]:
            problems.append((short(rec["why"]), rec["owner"] or "PAGES"))
        if not rec["load_error"] and not (rec["status"] and rec["status"] >= 400):  # a page that is not there: say it once
            for b in net["bad_status"]:
                problems.append(("HTTP %s for %s" % (b["status"], b["url"]), owner_for_url(b["url"])))
            for f in net["failed"]:
                problems.append(("request failed (%s): %s" % (f["error"], f["url"]), owner_for_url(f["url"])))
        for u in net["blocked_unexpected"]:
            problems.append(("the page calls a host it is not expected to call: " + u, "PAGES"))
        errors = list(dict.fromkeys(rec["log"].get("pageerrors", [])))
        for e in errors:
            problems.append(("script error: " + squash(e, 200), "INTERACTION"))
        if rec["reached"] and axe is None and not rec["error"]:
            problems.append(("axe-core did not run", "QA"))

        notes = []
        fonts = rec["settle"].get("fonts", {}) if rec["settle"] else {}
        # A family the page knows but does not use stays "unloaded": that is fine. Unknown, still loading or error is not.
        missing_fonts = [f for f in WEB_FONTS if f not in fonts or (not fonts[f].get("loaded") and (fonts[f].get("error") or fonts[f].get("loading")))]
        if rec["settle"] and missing_fonts:
            notes.append("Web font not loaded: %s. Contrast and text size were judged on a fallback font." % ", ".join(missing_fonts))
        if rec["settle"] and rec["settle"].get("unfinished_animations"):
            notes.append("%d transition(s) or animation(s) were still running when axe started." % rec["settle"]["unfinished_animations"])
        if slug == "contact":
            notes.append("The Google map frame is blocked by the network rule and is not analysed. The iframe element itself is.")
        if rec["attempts"] > 1:
            notes.append("The first try did not go through (failed connection, or the page did not react in time). This is try number %d." % rec["attempts"])

        evidence = {"state": state, "state_meaning": STATE_TEXT[state], "address": "/" + PAGES[slug], "http_status": rec["status"]}
        if rec["detail"]:
            evidence["state_seen"] = {k: short(v) if isinstance(v, str) else v for k, v in rec["detail"].items()}
        if axe:
            blocking = [v for v in axe["violations"] if (v["impact"] or "serious") in BLOCKING]
            evidence.update({
                "axe_version": axe["version"], "tags": TAGS, "rules_passed": axe["passes"], "rules_not_applicable": axe["inapplicable"],
                "rules_violated": [v["id"] for v in axe["violations"]],
                "needs_review": [{"rule": v["id"], "elements": len(v["nodes"]),
                                  "selectors": [n["selector"] for n in v["nodes"][:3]],
                                  "why": squash(v["nodes"][0]["summary"], 300) if v["nodes"] else ""} for v in axe["incomplete"]],
            })
            summary = "axe-core %s ran: %d rule(s) violated (%d serious or critical, %d moderate or minor), %d passed, %d need a human look" % (
                axe["version"], len(axe["violations"]), len(blocking), len(axe["violations"]) - len(blocking), axe["passes"], len(axe["incomplete"]))
        else:
            summary = "axe-core did not run"
        if rec["settle"]:
            evidence["fonts_loaded"] = sorted(f for f in fonts if fonts[f].get("loaded"))
        for key in ("blocked_expected", "blocked_unexpected", "bad_status", "failed", "cancelled", "font_failed"):
            if net[key]:
                evidence[{"failed": "failed_requests", "cancelled": "cancelled_requests", "font_failed": "font_requests_failed"}.get(key, key)] = net[key]
        if errors:
            evidence["script_errors"] = errors
        console = rec["log"].get("console", [])
        if console:
            evidence["console"] = [{"type": c.get("type"), "text": squash(c.get("text"), 300)} for c in console[:10]]
        if rec["shot"]:
            evidence["screenshot"] = rel_to_site(rec["shot"])
        if notes:
            evidence["notes"] = notes
        entries.append({
            "page": slug, "viewport": viewport, "check": "axe:" + state, "ok": not problems,
            "expected": "the page loads without a missing or unexpected request, the state is reached (%s) and axe-core runs" % STATE_TEXT[state],
            "actual": "; ".join(squash(p[0], 300) for p in problems) + ("" if axe is None else ". " + summary) if problems else summary,
            "evidence": evidence, "owner": problems[0][1] if problems else "PAGES",
        })
        if not axe:
            continue

        if state == "base":
            base_fail = {v["id"]: {n["selector"] for n in v["nodes"]} for v in axe["violations"]}
        for v in sorted(axe["violations"], key=lambda v: (SEVERITY.get(v["impact"] or "serious", 1), v["id"])):
            impact = v["impact"] or "serious"  # axe always gives an impact for a violation; if it ever does not, stay strict
            nodes = v["nodes"]
            if state == "base" or base_fail is None:
                fresh, known = nodes, []
            else:
                in_base = base_fail.get(v["id"], set())
                fresh = [n for n in nodes if n["selector"] not in in_base]
                known = [n for n in nodes if n["selector"] in in_base]
            compared = state != "base" and base_fail is not None
            note = []
            if impact not in BLOCKING:
                note.append("Impact %s: reported for information, it does not fail the check." % impact)
            if compared and not fresh:
                note.append("Every offending element fails in the base state of this page too. Fix it there and this entry goes away.")
            elif compared and known:
                note.append("%d of %d offending elements fail only in this state. They are listed first." % (len(fresh), len(nodes)))
            elif compared:
                note.append("None of these elements fails in the base state of this page: the state brings the problem in.")
            elif state != "base":
                note.append("The base state of this page was not analysed, so it is not known whether these elements fail there too.")
            shown = (fresh + known)[:MAX_NODES]
            lead = shown[0] if shown else {"selector": "", "summary": ""}
            label = impact if impact in BLOCKING else impact + " (reported only)"
            entries.append({
                "page": slug, "viewport": viewport, "check": "axe:%s:%s" % (state, v["id"]), "ok": impact not in BLOCKING,
                "expected": "no element violates the axe rule %s (%s)" % (v["id"], v["help"]),
                "actual": "%s: %d element(s). First: %s : %s" % (label, len(nodes), lead["selector"], squash(lead["summary"], 260)),
                "evidence": {
                    "state": state, "rule": v["id"], "impact": impact, "help": v["help"], "help_url": v["helpUrl"],
                    "tags": [t for t in v["tags"] if t.startswith("wcag") or t == "best-practice"],
                    "elements": len(nodes),
                    "nodes": [dict({"selector": n["selector"], "failure_summary": n["summary"], "html": n["html"]},
                                   **({"only_in_this_state": n in fresh} if compared else {})) for n in shown],
                    "same_as_base": bool(compared and not fresh),
                    "note": " ".join(note),
                },
                "owner": owner_for_rule(v["id"], fresh or nodes, state, compared and bool(fresh)),
            })
    return entries


def crash_entries(slug, viewport, text):
    return [{"page": slug, "viewport": viewport, "check": "axe:" + state, "ok": False,
             "expected": "the page loads without a missing or unexpected request, the state is reached (%s) and axe-core runs" % STATE_TEXT[state],
             "actual": "the scan did not run: " + text, "evidence": {"state": state}, "owner": "QA"} for state in states_for(slug, viewport)]


# ---------------------------------------------------------------- running

_STARTING = threading.Lock()


def _take(queues, prefer):
    for viewport in [prefer] + [v for v in queues if v != prefer]:
        try:
            return queues[viewport].get_nowait()
        except queue.Empty:
            pass
    return None


def _worker(prefer, base, root, queues, gate, done, errors, bases, axe_src, shots_dir):
    """One browser per worker thread (the Playwright sync interface must not be shared between threads) and,
    unless an address was given, one local server per browser. A worker does the pages of its own viewport first
    and then helps with the other one."""
    try:
        with contextlib.ExitStack() as stack:
            if not base:
                with _STARTING:  # one after the other, so that two servers can never be given the same free port
                    base = stack.enter_context(common.site_server(root=root or common.SITE))
            bases.append(base)
            p = stack.enter_context(sync_playwright())
            browser = p.chromium.launch()
            tabs = {}
            try:
                while True:
                    task = _take(queues, prefer)
                    if task is None:
                        break
                    slug, viewport = task
                    try:
                        if viewport not in tabs:
                            tabs[viewport] = Tab(browser, p, base, viewport)
                        recs = [run_state_steady(tabs[viewport], gate, slug, viewport, state, axe_src, shots_dir) for state in states_for(slug, viewport)]
                        done[(slug, viewport)] = build_entries(base, slug, viewport, recs)
                    except Exception as e:
                        done[(slug, viewport)] = crash_entries(slug, viewport, "%s: %s" % (type(e).__name__, first_line(e)))
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
    except Exception as e:
        errors.append("%s: %s" % (type(e).__name__, first_line(e)))


def run(base, pages, viewports, jobs=4, shots_dir=None, root=None):
    """Scan the given pages and viewports. base is the address to test, or None for local servers that serve root
    (default: the site folder). Returns (report entries, address that was tested).
    Writes nothing except the state screenshots, and those only when shots_dir is given."""
    if base and not base.endswith("/"):
        base += "/"
    with open(common.AXE_JS, encoding="utf-8") as f:
        axe_src = f.read()
    order = [(slug, viewport) for slug in pages for viewport in viewports]
    queues = {viewport: queue.Queue() for viewport in viewports}
    load = {viewport: 0 for viewport in viewports}
    for slug, viewport in order:
        queues[viewport].put((slug, viewport))
        load[viewport] += len(states_for(slug, viewport))
    # Share the workers out by the amount of work: the phone has the menu state on every page, so it gets more of them.
    share = {viewport: 0 for viewport in viewports}
    prefer = []
    for _ in range(max(1, min(jobs, len(order)))):
        viewport = max(viewports, key=lambda v: load[v] / (share[v] + 1))
        share[viewport] += 1
        prefer.append(viewport)
    done, errors, bases, gate = {}, [], [], Gate()
    threads = [threading.Thread(target=_worker, args=(v, base, root, queues, gate, done, errors, bases, axe_src, shots_dir), daemon=True) for v in prefer]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    results = []
    for slug, viewport in order:
        results += done.get((slug, viewport)) or crash_entries(slug, viewport, "; ".join(errors) or "the worker stopped early")
    return results, base or (bases[0] if bases else "")


def distinct_violations(results):
    """The same defect shows up on many pages (shared header and footer). One line per rule, with where it was seen."""
    groups = {}
    for r in results:
        ev = r.get("evidence")
        if not isinstance(ev, dict) or "rule" not in ev:
            continue
        g = groups.setdefault(ev["rule"], {"rule": ev["rule"], "impact": ev.get("impact"), "fails_the_check": False, "help_url": ev.get("help_url"),
                                           "owners": [], "entries": 0, "where": [], "selectors": []})
        g["entries"] += 1
        g["fails_the_check"] = g["fails_the_check"] or not r.get("ok")
        if SEVERITY.get(ev.get("impact"), 9) < SEVERITY.get(g["impact"], 9):
            g["impact"] = ev.get("impact")
        if r.get("owner") and r["owner"] not in g["owners"]:
            g["owners"].append(r["owner"])
        g["where"].append("%s/%s/%s" % (r.get("page"), r.get("viewport"), ev.get("state")))
        for n in ev.get("nodes", []):
            if n.get("selector") not in g["selectors"] and len(g["selectors"]) < 12:
                g["selectors"].append(n.get("selector"))
    return sorted(groups.values(), key=lambda g: (SEVERITY.get(g["impact"], 9), g["rule"]))


def counts(results):
    scans = [r for r in results if r["check"].count(":") == 1]
    rules = [r for r in results if r["check"].count(":") > 1]
    return {"scans": len(scans), "scans_failed": sum(1 for r in scans if not r["ok"]),
            "violation_entries": len(rules), "serious_or_critical": sum(1 for r in rules if not r["ok"]),
            "moderate_or_minor": sum(1 for r in rules if r["ok"])}


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    ap = common.cli_parser("Accessibility check with axe-core: ten pages, two viewports, plus menu, lightbox and contact form states.")
    ap.add_argument("--jobs", type=int, default=4, help="browsers working in parallel (default 4)")
    ap.add_argument("--no-shots", action="store_true", help="take no screenshot of the menu, lightbox and form states")
    args = ap.parse_args()
    pages = common.cli_pages(ap, args.page)
    viewports = [v for v in VIEWPORTS if v in parse_viewports(args.viewport)]

    results, base = run(args.base, pages, viewports, jobs=args.jobs, shots_dir=None if args.no_shots else common.SHOTS)

    # A rule that is no longer violated has no new entry, so every old entry of the pages and viewports of this run
    # is replaced (see common.save_report), not only the ones with the same name.
    covered = {(slug, viewport) for slug in pages for viewport in viewports}
    kept = [r for r in common.old_results(NAME) if not common.replaced(r, covered)]
    versions = sorted({r["evidence"]["axe_version"] for r in results if r["evidence"].get("axe_version")})
    c = counts(results)
    doc = save_report(NAME, results, common.report_base(args.base), {
        "script": "qa/%s.py" % NAME, "axe_version": versions[0] if len(versions) == 1 else versions, "tags": TAGS,
        "fails_on_impact": list(BLOCKING),
        "states": {s: STATE_TEXT[s] for s in STATES},
        "not_analysed": NOT_ANALYSED,
        "last_run": dict(c, pages=pages, viewports=viewports),
        "distinct_violations": distinct_violations(kept + results),
    }, replace=covered)

    for r in results:
        if not r["ok"]:
            print("FAIL %s %s %s [%s] %s" % (r["page"], r["viewport"], r["check"], r["owner"], squash(r["actual"], 400)))
    failed = sum(1 for r in results if not r["ok"])
    print("%s: %s. %d scans (%d failed), %d violated rules found: %d serious or critical, %d moderate or minor (reported only). Whole report %s. Report: qa/reports/%s.json" % (
        NAME, "PASS" if not failed else "FAIL (%d entries)" % failed, c["scans"], c["scans_failed"], c["violation_entries"],
        c["serious_or_critical"], c["moderate_or_minor"], "ok" if doc["ok"] else "not ok", NAME))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
