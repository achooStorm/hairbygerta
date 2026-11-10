"""Visual comparison of our pages with the live Wix site, and the brief's measurement list.

Both sides are measured with the same JavaScript function (MEASURE_JS below is the function of
../hairbygerta-env/scripts/wix_measure.py, copied word for word): the box, font and colour of every text node,
every image, every coloured box and every button, field, rule and frame. The Wix numbers are the reference
files in ../hairbygerta-env/wix-ref, ours are measured live.

    ../hairbygerta-env/venv/Scripts/python.exe qa/visual_compare.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/visual_compare.py --page home,contact --viewport desktop
    ../hairbygerta-env/venv/Scripts/python.exe qa/visual_compare.py --width 1440          (one desktop width)
    ../hairbygerta-env/venv/Scripts/python.exe qa/visual_compare.py --base https://achoostorm.github.io/hairbygerta/
    ../hairbygerta-env/venv/Scripts/python.exe qa/visual_compare.py --refresh-wix     (measure the live Wix site again first)

Viewports (build contract, section 10, decisions 1, 2, 16 and 17)
  --viewport desktop   four widths, each 900 px high, each compared with the Wix reference taken at that width:
                         1265  entries "desktop-1265"   measure-<slug>-w1265.json    (also the brief's list, see below)
                         1280  entries "desktop"        measure-<slug>-desktop.json
                         1440  entries "desktop-1440"   measure-<slug>-w1440.json
                         1920  entries "desktop-1920"   measure-<slug>-w1920.json
  --viewport phone     the Playwright iPhone 13 preset, entries "phone", measure-<slug>-phone.json
  --viewport both      all five (the default)
  --width N            one desktop width alone (N from 1101). Add --viewport both to run the phone as well.
  A desktop width without a reference file gets one entry "no reference" with ok true and is not compared for that page.

How things are paired
  text      by its text (exact after trimming, then a fuzzy match), inside the same page region first
            (header, main, footer). Text that only one side shows is listed, not counted: wording is the
            business of the content check.
  images    inside the page region: first by the paired texts around them (the nearest above and the nearest
            below in the same column), then in reading order
  the rest  buttons by their text; fields, rules, frames, icon links and coloured boxes like the images.
            A photo, box, button, field, rule or frame that only one side has counts as a difference.

What is measured on our side beyond the element boxes (so that a different way of building the same look is
not reported as a difference)
  a rule drawn by ::before or ::after (a pseudo-element has no element of its own), and a colour band painted
  wider than its element with a filled border image (the painted area counts, as the visitor sees it)

Desktop: what counts as a difference (ok false). At every width only the Wix value passes.
  text      x, y, font size, weight, style, colour, letter spacing, decoration, and for text of two or more
            lines also line height and alignment
  others    x, y, width, height, and where it applies background, border and corner radius
  A length that is off by more than 2 px. Any other font size (0.5 px), weight, style, colour or decoration.
  Letter spacing counts from 3 % of the font size, at least 0.3 px: 2 px would never show there. The y of text
  gets 6 % of the font size on top of the tolerance, because two fonts do not put their letters at the same
  height in the line.

How desktop positions are judged, so that one cause gives one entry
  x   at the edge the text is aligned to (left edge, centre or right edge). An element also passes when it sits
      at the same place inside its coloured box as on Wix, so a box that moved is reported once, not once per child.
  y   text at the centre of its first line (the same for any font), everything else at its top edge. An element
      passes when its distance to the element straight above it is right, or its place inside its coloured box,
      or its place on the page. So an element that moved is reported once, what follows it is not, and text that
      wraps to more lines in our fonts does not make everything under it count as moved.

Phone (decision 16): Wix draws its phone page 320 px wide and the phone enlarges it by 390 / 320.
  counts        font size, letter spacing, line height, border thickness and corner radius as written on the Wix
                phone page (no factor), weight, style, colour, decoration, alignment, backgrounds, and anything
                that only one side has
  block order   one entry per page: the paired blocks of main and footer come in the same order, top to bottom,
                as on the Wix phone page. Two blocks are out of order when one is wholly above the other on Wix
                and wholly below it on our page. Not part of it: the phone header, the home photo row, the extra
                Hours block, the closing booking note, the copyright line, the order of the contact details
                among themselves (decision 8), and what PHONE_ORDER_OPEN lists as an open question for the
                owner (those blocks get an entry of their own with ok true).
  fits screen   one entry per page: no element and no line of text reaches past the edge of the screen, and
                the page does not scroll sideways
  sizes         places and sizes are not pass or fail on the phone. Where they differ by more than 4 px from the
                Wix numbers times 390 / 320 they are listed in one entry per page with ok true.

The brief's measurement list (entries whose check name starts with "brief-")
  Every line of the list is tested on our own pages at 1265 x 900, the width the list was taken at (decision 1),
  within 2 px, with decision 3 (1 px lines, service card text 16 px) and decision 4 (beige box centred).
  These entries need no Wix reference. The phone line of the list (header 96 px, 80 px logo, menu button,
  address and hours line 14 px) is tested in the phone viewport. See BRIEF_SPEC and brief_checks below.

Reported with ok true
  font metrics   width of text and height of wrapped text (Bodoni Moda and Figtree are not Didot and Proxima Nova)
  intended       placeholders instead of photos, the extra Hours block on the contact page, the closing booking
                 note, on the Privacy Policy what stands under a sentence about Wix that our page leaves out on
                 purpose (it sits higher than on Wix, because our text there is shorter), the copyright line,
                 the phone photo row (a 2 x 2 grid where Wix hides the row), the Wix chat button, underlined
                 links inside a sentence (decision 18), the centred beige box
                 (decision 4), an empty stretch of 300 px or more that only the Wix page has above its footer
  intended x     desktop, the horizontal place alone (size, font and vertical place are compared as everywhere):
                 home (decision 21): site title, welcome paragraph, dotted rule, Book Online button and address
                 line, while ours is centred on the page (within 2 px) and the Wix one sits no more than 18 px
                 (plus 2) beside the centre.
                 the four policy pages (decision 24): a title, while ours is centred and the Wix one sits no more
                 than 28 px (plus 2) beside the centre; a block of text, while ours stands on the one text edge of
                 the page, that edge is where the Wix column starts (the middle value of all blocks, within 2 px)
                 and the Wix block sits no more than 28 px (plus 2) beside it. Not intended: a list item (indented
                 on purpose on both sides), and a block that Wix shows as an indented list item.
                 An element that is neither where the decision puts it nor where Wix has it stays a difference.
  not an exception  service card text on the phone (decision 25): it is compared with the Wix phone sizes as
                 written, like all phone text (decision 16). The 16 px of decision 3 is the brief line at 1265 px.

Output
  qa/reports/visual_compare.json (text and numbers only), per page and viewport: a summary, then the differences,
  biggest first. It is the only report this script writes.
  qa/screenshots/visual_compare/<slug>-<viewport>-full.png          our page
  <tools folder>/qa-private/side-by-side/<slug>-<viewport>.png      our page next to the Wix reference screenshot.
  The side-by-side images show Wix-only photos. The script refuses to write them inside the site folder.

Exit code 0 when nothing counts as a difference, 1 otherwise.
"""
import concurrent.futures, difflib, itertools, json, math, os, re, subprocess, sys, time, unicodedata
from urllib.parse import urlsplit

sys.dont_write_bytecode = True   # no __pycache__ in the site folder (a compiled file carries the path of this computer)
import common  # noqa: E402

NAME = "visual_compare"
OLD_COPY = "visual"             # earlier versions wrote the same report a second time under this name; see drop_old_copy
SHOT_DIR = "visual_compare"     # folder inside qa/screenshots
SIDE_DIR = "side-by-side"       # folder inside common.PRIVATE
PHONE_SCALE = 390.0 / 320.0
DESKTOP_HEIGHT = 900
BASE_WIDTH = 1280               # its entries keep the plain viewport name "desktop", so existing readers keep working
BRIEF_WIDTH = 1265              # the width the brief's measurement list belongs to (decision 1)
DESKTOP_WIDTHS = (1265, 1280, 1440, 1920)
MIN_DESKTOP = 1101              # below this our stylesheet and the Wix page switch to another layout
TOL = {"desktop": 2.0, "phone": 4.0}    # lengths. On the phone places and sizes are only listed, from this size on.
TYPE_TOL = 2.0                  # line height and corner radius
PRIVACY_SLUG = "english-privacy-policy"
WIX_WORD = re.compile(r"\bwix\b", re.I)     # a sentence that names Wix (see the privacy rule of qa/check_content.py)
FONT_TOL = 0.5                  # font size
SPACING_TOL = 0.3               # letter spacing, and never less than SPACING_EM of the font size
SPACING_EM = 0.03
BASELINE_EM = 0.06              # extra room for the y of text: two fonts do not put their letters at the same height in the line
BORDER_TOL = 0.5                # border thickness
BRIEF_TOL = 2.0                 # the brief: "match these within 2 px"
EPS = 0.05
# Gallery: how far the height of the area the photos fill may be from the Wix height, as a share of the Wix height.
# Our masonry and the hand-placed Wix photos cannot end on the same pixel. With the columns of decision 32
# (three, and a fourth from about 1600 px) the two are 1 to 15 percent apart; with a column missing 80 percent and more.
AREA_HEIGHT_SHARE = 0.20
WIDE_GALLERY = (1500, 1700)     # px: where a min-width rule for that fourth column may start ("about 1600 px")
ICON_MAX = 48                   # an image up to this size is an icon and is compared through its link
EMPTY_GAP = 300                 # px: a Wix footer that sits this much further below the content than ours stands under an empty stretch
SLUGS = [s for s in common.PAGES if s != "404"]     # the nine pages that exist on Wix
PAGE_TIMEOUT = 60000
LOAD_TRIES = 3                  # a page whose own files did not all arrive is loaded again before it is measured
# What a busy machine does to a local server, as opposed to a file that is really missing (that one answers 404).
TRANSIENT = ("ERR_CONNECTION_REFUSED", "ERR_CONNECTION_RESET", "ERR_CONNECTION_CLOSED", "ERR_CONNECTION_ABORTED", "ERR_EMPTY_RESPONSE",
             "ERR_TIMED_OUT", "ERR_SOCKET_NOT_CONNECTED", "ERR_NETWORK_CHANGED", "ERR_CONNECTION_TIMED_OUT")
WIX_SCRIPT = ("scripts", "wix_measure.py")


class View:
    """One viewport of a run: the name written into the entries, and the name of its Wix reference files."""

    def __init__(self, kind, width=None):
        self.kind = kind                    # "desktop" or "phone": which rules apply
        if kind == "phone":
            self.width, self.name, self.ref = 390, "phone", "phone"
        else:
            self.width = int(width)
            self.name = "desktop" if self.width == BASE_WIDTH else "desktop-%d" % self.width
            self.ref = "desktop" if self.width == BASE_WIDTH else "w%d" % self.width
        self.brief = kind == "phone" or self.width == BRIEF_WIDTH      # the brief's list has lines for this viewport

    def options(self, p):
        """Browser context options. dsf 1 keeps the full-page screenshots at a readable size."""
        return common.context_options(p, "phone" if self.kind == "phone" else (self.width, DESKTOP_HEIGHT), dsf=1)

    def size(self):
        return "iPhone 13, 390 px wide" if self.kind == "phone" else "%d x %d" % (self.width, DESKTOP_HEIGHT)


# The measuring function of ../hairbygerta-env/scripts/wix_measure.py, copied unchanged.
MEASURE_JS = """() => {
  const out = {doc: {w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight, vw: innerWidth}, text: [], images: [], boxes: [], controls: []};
  const box = e => { const r = e.getBoundingClientRect(); return {x: Math.round(r.x * 10) / 10, y: Math.round((r.y + scrollY) * 10) / 10, w: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10}; };
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0; };
  const region = e => e.closest('header') ? 'header' : e.closest('footer') ? 'footer' : 'main';
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e)) continue;
    const s = getComputedStyle(e);
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    if (own && !['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(e.tagName)) {
      out.text.push({region: region(e), tag: e.tagName.toLowerCase(), text: own.slice(0, 90), box: box(e), fontFamily: s.fontFamily.slice(0, 60), fontSize: s.fontSize,
        fontWeight: s.fontWeight, fontStyle: s.fontStyle, lineHeight: s.lineHeight, letterSpacing: s.letterSpacing, color: s.color, textAlign: s.textAlign,
        textTransform: s.textTransform, textDecoration: s.textDecorationLine});
    }
    if (e.tagName === 'IMG') out.images.push({region: region(e), alt: e.alt, box: box(e), objectFit: s.objectFit});
    const bg = s.backgroundColor;
    const r = e.getBoundingClientRect();
    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' && r.width >= 40 && r.height >= 12)
      out.boxes.push({region: region(e), tag: e.tagName.toLowerCase(), box: box(e), bg, position: s.position, borderRadius: s.borderRadius, border: s.borderTopWidth + ' ' + s.borderTopStyle + ' ' + s.borderTopColor});
    if (['A', 'BUTTON', 'INPUT', 'TEXTAREA', 'IFRAME', 'HR'].includes(e.tagName) || s.borderTopStyle === 'dotted' || s.borderBottomStyle === 'dotted')
      out.controls.push({region: region(e), tag: e.tagName.toLowerCase(), text: (e.innerText || e.value || e.title || '').trim().slice(0, 60), box: box(e), bg, color: s.color,
        borderTop: s.borderTopWidth + ' ' + s.borderTopStyle + ' ' + s.borderTopColor, borderBottom: s.borderBottomWidth + ' ' + s.borderBottomStyle + ' ' + s.borderBottomColor,
        borderRadius: s.borderRadius, padding: s.padding, fontSize: s.fontSize, letterSpacing: s.letterSpacing});
  }
  const hd = document.querySelector('header');
  if (hd) { const s = getComputedStyle(hd); out.header = {box: box(hd), position: s.position, bg: s.backgroundColor}; }
  out.bodyBg = getComputedStyle(document.body).backgroundColor;
  return out;
}"""

# Our side only: the same walk with the same tests, so entry i here belongs to entry i of MEASURE_JS. It adds what
# the live page can tell and a stored Wix measurement cannot: which element it is (for the report and for the
# intended differences), where the lines of text really are (the text box of an element with padding is not its
# border box), whether a parent hides it, and the underline a text inherits from a parent.
EXTRA_JS = """() => {
  const out = {text: [], images: [], boxes: [], controls: [], lines: []};
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0; };
  const r1 = v => Math.round(v * 10) / 10;
  const one = n => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + [...n.classList].slice(0, 3).map(c => '.' + c).join('');
  const sel = e => { const parts = []; let n = e; while (n && n !== document.body && parts.length < 3) { parts.unshift(one(n)); n = n.parentElement; } return parts.join(' > '); };
  const marks = e => { const m = new Set(); let n = e; while (n && n !== document.documentElement) { m.add(n.tagName.toLowerCase()); if (n.id) m.add('#' + n.id); for (const c of n.classList) m.add('.' + c); n = n.parentElement; } return [...m]; };
  const faded = e => { let n = e.parentElement; while (n && n !== document.documentElement) { if (parseFloat(getComputedStyle(n).opacity) === 0) return true; n = n.parentElement; } return false; };
  const shown = c => { const m = /rgba?\\(([^)]+)\\)/.exec(c); if (!m) return true; const p = m[1].split(/[,\\/ ]+/).filter(Boolean); return p.length < 4 || parseFloat(p[3]) > 0; };
  const edge = (w, st, c) => parseFloat(w) > 0 && st !== 'none' && st !== 'hidden' && shown(c);
  const deco = e => { const set = new Set(); let n = e;
    while (n && n !== document.documentElement) { const d = getComputedStyle(n);
      for (const t of d.textDecorationLine.split(' ')) if (t && t !== 'none') set.add(t);
      if (d.display.indexOf('inline-') === 0 || d.position === 'absolute' || d.position === 'fixed' || d.cssFloat !== 'none') break;
      n = n.parentElement; }
    return [...set].sort().join(' ') || 'none'; };
  const geom = e => {
    const all = [], mine = [], rg = document.createRange();
    for (const n of e.childNodes) {
      if (n.nodeType === 3) { if (!n.textContent.trim()) continue; rg.selectNodeContents(n); for (const q of rg.getClientRects()) if (q.width > 0 && q.height > 0) { all.push(q); mine.push(q); } }
      else if (n.nodeType === 1) { const d = getComputedStyle(n); if (d.display.indexOf('inline') === 0 && d.position !== 'absolute' && d.position !== 'fixed' && vis(n)) for (const q of n.getClientRects()) if (q.width > 0 && q.height > 0) all.push(q); }
    }
    if (!mine.length) return {};
    const lines = [];
    for (const q of mine.slice().sort((a, b) => a.top - b.top || a.left - b.left)) {
      const c = (q.top + q.bottom) / 2, L = lines[lines.length - 1];
      if (L && Math.abs(c - (L.top + L.bottom) / 2) < Math.min(q.height, L.bottom - L.top) * 0.6) { L.top = Math.min(L.top, q.top); L.bottom = Math.max(L.bottom, q.bottom); }
      else lines.push({top: q.top, bottom: q.bottom});
    }
    const first = lines[0], last = lines[lines.length - 1];
    return {tl: r1(Math.min(...all.map(q => q.left))), tr: r1(Math.max(...all.map(q => q.right))), tt: r1(first.top + scrollY), tb: r1(last.bottom + scrollY),
            c1: r1((first.top + first.bottom) / 2 + scrollY), n: lines.length, ca: r1(first.bottom - first.top)};
  };
  // A band that is painted wider than its element (a filled border image with an outset, the usual way to let a
  // colour run to both edges of the screen): what the visitor sees is the painted area, so that is what is compared.
  const painted = (e, s, r) => {
    if (!s.borderImageSource || s.borderImageSource === 'none' || !/fill/.test(s.borderImageSlice || '')) return {};
    const v = (s.borderImageOutset || '0').trim().split(/ +/).map(x => /px$/.test(x) ? parseFloat(x) : 0);
    const top = v[0] || 0, right = v.length > 1 ? v[1] : top, bottom = v.length > 2 ? v[2] : top, left = v.length > 3 ? v[3] : right;
    if (!(top || right || bottom || left)) return {};
    const dw = document.documentElement.clientWidth, dh = document.documentElement.scrollHeight;
    const x0 = Math.max(0, r.left - left), x1 = Math.min(dw, r.right + right);
    const y0 = Math.max(0, r.top + scrollY - top), y1 = Math.min(dh, r.bottom + scrollY + bottom);
    return {paint: {x: r1(x0), y: r1(y0), w: r1(x1 - x0), h: r1(y1 - y0)}};
  };
  for (const e of document.querySelectorAll('body *')) {
    if (!vis(e)) continue;
    const s = getComputedStyle(e);
    const info = () => ({sel: sel(e), marks: marks(e), faded: faded(e)});
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join('').trim();
    if (own && !['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(e.tagName)) {
      const item = e.closest('.info-item') || (e.closest('.info') ? e.parentElement : null); const head = item ? item.querySelector('h2') : null;
      const flow = s.display === 'inline' && !!e.parentElement && [...e.parentElement.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
      out.text.push(Object.assign(info(), geom(e), {deco: deco(e), flow, group: head ? head.textContent.trim() : ''}));
    }
    if (e.tagName === 'IMG') out.images.push(Object.assign(info(), {ph: e.classList.contains('ph'), file: (e.getAttribute('src') || '').split('/').pop()}));
    const bg = s.backgroundColor;
    const r = e.getBoundingClientRect();
    if (bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent' && r.width >= 40 && r.height >= 12) out.boxes.push(Object.assign(info(), painted(e, s, r)));
    if (['A', 'BUTTON', 'INPUT', 'TEXTAREA', 'IFRAME', 'HR'].includes(e.tagName) || s.borderTopStyle === 'dotted' || s.borderBottomStyle === 'dotted')
      out.controls.push(Object.assign(info(), {hasImg: !!e.querySelector('img')}));
    else {
      const t = edge(s.borderTopWidth, s.borderTopStyle, s.borderTopColor), b = edge(s.borderBottomWidth, s.borderBottomStyle, s.borderBottomColor);
      const l = edge(s.borderLeftWidth, s.borderLeftStyle, s.borderLeftColor), rr = edge(s.borderRightWidth, s.borderRightStyle, s.borderRightColor);
      if (t !== b && !l && !rr && r.width >= 20) {
        const th = parseFloat(t ? s.borderTopWidth : s.borderBottomWidth);
        out.lines.push(Object.assign(info(), {region: e.closest('header') ? 'header' : e.closest('footer') ? 'footer' : 'main',
          x: r1(r.x), y: r1((t ? r.y : r.bottom - th) + scrollY), w: r1(r.width), thick: th,
          style: t ? s.borderTopStyle : s.borderBottomStyle, color: t ? s.borderTopColor : s.borderBottomColor}));
      }
    }
    // A rule drawn by ::before or ::after has no element of its own, so the walk above cannot see it and the rule would
    // be reported as missing although it is on the screen. Only the plain case is read: a block pseudo-element in the
    // normal flow of a block parent, no higher than 2 px, with a border on one side (top or bottom).
    for (const which of ['::before', '::after']) {
      const q = getComputedStyle(e, which);
      if (!q.content || q.content === 'none' || q.content === 'normal' || q.display !== 'block' || q.visibility === 'hidden' || parseFloat(q.opacity) === 0) continue;
      if ((q.position !== 'static' && q.position !== 'relative') || !['block', 'list-item', 'flow-root'].includes(s.display)) continue;
      const n = v => parseFloat(v) || 0;
      const t = edge(q.borderTopWidth, q.borderTopStyle, q.borderTopColor), b = edge(q.borderBottomWidth, q.borderBottomStyle, q.borderBottomColor);
      const side = edge(q.borderLeftWidth, q.borderLeftStyle, q.borderLeftColor) || edge(q.borderRightWidth, q.borderRightStyle, q.borderRightColor);
      const w = n(q.width), h = n(q.height);
      if (t === b || side || w < 20 || h > 2) continue;
      const th = n(t ? q.borderTopWidth : q.borderBottomWidth), tall = n(q.borderTopWidth) + h + n(q.borderBottomWidth);
      const padTop = n(s.borderTopWidth) + n(s.paddingTop), padBottom = n(s.borderBottomWidth) + n(s.paddingBottom);
      // without a border or padding on the parent, the margin of the pseudo-element falls outside the parent (margin collapse)
      const top = which === '::before' ? r.top + padTop + (padTop > 0 ? n(q.marginTop) : 0) : r.bottom - padBottom - (padBottom > 0 ? n(q.marginBottom) : 0) - tall;
      out.lines.push(Object.assign(info(), {sel: sel(e) + which, region: e.closest('header') ? 'header' : e.closest('footer') ? 'footer' : 'main',
        x: r1(r.left + n(s.borderLeftWidth) + n(s.paddingLeft) + n(q.marginLeft)), y: r1((t ? top : top + tall - th) + scrollY), w: r1(w), thick: th,
        style: t ? q.borderTopStyle : q.borderBottomStyle, color: t ? q.borderTopColor : q.borderBottomColor}));
    }
  }
  out.fullText = document.body.innerText || '';
  out.fonts = [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, ''));
  return out;
}"""

BOTH_JS = "() => { const base = (%s)(); const extra = (%s)(); return {base, extra}; }" % (MEASURE_JS, EXTRA_JS)

# Phone only: what reaches past the edge of the screen. An element counts with its own box and with the lines of its
# own text (a long word can stick out of a box that fits). Not counted: what a parent cuts off that itself fits the
# screen (the scrolling hours line), and what is parked wholly outside the screen (the skip link, a closed menu): if
# that widens the page, the sideways scroll (docW against vw) shows it. html and body do not count as a parent that
# cuts off: a page that hides what sticks out still has something wider than the screen. Only the outermost element
# is listed, not everything inside it.
OVERFLOW_JS = """() => {
  const vw = document.documentElement.clientWidth;
  const out = {vw, docW: document.documentElement.scrollWidth, wide: []};
  const r1 = v => Math.round(v * 10) / 10;
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0; };
  const one = n => n.tagName.toLowerCase() + (n.id ? '#' + n.id : '') + [...n.classList].slice(0, 3).map(c => '.' + c).join('');
  const sel = e => { const parts = []; let n = e; while (n && n !== document.body && parts.length < 3) { parts.unshift(one(n)); n = n.parentElement; } return parts.join(' > '); };
  const faded = e => { let n = e.parentElement; while (n && n !== document.documentElement) { if (parseFloat(getComputedStyle(n).opacity) === 0) return true; n = n.parentElement; } return false; };
  const clipped = e => { let n = e.parentElement;
    while (n && n !== document.body && n !== document.documentElement) { const s = getComputedStyle(n);
      if (s.overflowX !== 'visible') { const r = n.getBoundingClientRect(); if (r.left >= -1 && r.right <= vw + 1) return true; }
      n = n.parentElement; }
    return false; };
  const bad = new Set(), rg = document.createRange();
  for (const e of document.querySelectorAll('body *')) {
    if (e.parentElement && bad.has(e.parentElement)) { bad.add(e); continue; }
    if (!vis(e) || faded(e)) continue;
    const r = e.getBoundingClientRect();
    let l = r.left, rt = r.right, what = 'box';
    for (const n of e.childNodes) if (n.nodeType === 3 && n.textContent.trim()) { rg.selectNodeContents(n);
      for (const q of rg.getClientRects()) if (q.width > 0 && q.height > 0) { if (q.right > rt + 0.5) { rt = q.right; what = 'text'; } if (q.left < l - 0.5) { l = q.left; what = 'text'; } } }
    if (rt <= vw + 1 && l >= -1) continue;
    if (rt <= 0 || l >= vw) continue;
    if (clipped(e)) continue;
    bad.add(e);
    out.wide.push({sel: sel(e), what, x: r1(l), right: r1(rt), w: r1(rt - l), y: r1(r.top + scrollY), over: r1(Math.max(rt - vw, -l))});
  }
  return out;
}"""

# The brief's measurement list: what our page shows for the elements the list names. spec is a list of
# [key, selector]; every element a selector finds is read. The font of an element is read where its longest piece of
# text sits (p.site-title holds a link, the link holds the letters; a.addr starts with the pin in a span of its own),
# "letters" is where the lines of text really are, "deco" the text decoration of the element and of that piece.
BRIEF_JS = """async (spec) => {
  const r1 = v => Math.round(v * 10) / 10;
  const vis = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity) > 0; };
  const box = e => { const r = e.getBoundingClientRect(); return {x: r1(r.left), y: r1(r.top + scrollY), w: r1(r.width), h: r1(r.height)}; };
  const edge = (s, side) => ({w: parseFloat(s['border' + side + 'Width']) || 0, style: s['border' + side + 'Style'], color: s['border' + side + 'Color']});
  const textNodes = e => { const found = []; const w = document.createTreeWalker(e, NodeFilter.SHOW_TEXT);
    for (let n = w.nextNode(); n; n = w.nextNode()) if (n.textContent.trim() && n.parentElement && vis(n.parentElement)) found.push(n);
    return found; };
  const letters = e => { const rg = document.createRange(), rects = [];
    for (const n of textNodes(e)) { rg.selectNodeContents(n); for (const q of rg.getClientRects()) if (q.width > 0 && q.height > 0) rects.push(q); }
    if (!rects.length) return null;
    const first = rects.reduce((a, b) => (b.top < a.top ? b : a));
    return {x: r1(Math.min(...rects.map(q => q.left))), right: r1(Math.max(...rects.map(q => q.right))), y: r1(first.top + scrollY),
            bottom: r1(Math.max(...rects.map(q => q.bottom)) + scrollY), c1: r1((first.top + first.bottom) / 2 + scrollY)}; };
  const deco = e => { const set = new Set(); let n = e;
    while (n && n !== document.documentElement) { const d = getComputedStyle(n);
      for (const t of d.textDecorationLine.split(' ')) if (t && t !== 'none') set.add(t);
      if (d.display.indexOf('inline-') === 0 || d.position === 'absolute' || d.position === 'fixed' || d.cssFloat !== 'none') break;
      n = n.parentElement; }
    return [...set].sort().join(' ') || 'none'; };
  const pseudo = (e, which) => { const q = getComputedStyle(e, which);
    if (!q.content || q.content === 'none' || q.content === 'normal' || q.display === 'none') return null;
    return {w: parseFloat(q.width) || 0, h: parseFloat(q.height) || 0, top: edge(q, 'Top'), bottom: edge(q, 'Bottom'), bg: q.backgroundColor}; };
  const main = e => textNodes(e).reduce((a, b) => (!a || b.textContent.trim().length > a.textContent.trim().length ? b : a), null);
  const read = e => { const s = getComputedStyle(e); const tn = main(e); const leaf = tn ? tn.parentElement : e; const t = getComputedStyle(leaf);
    return {shown: vis(e), tag: e.tagName.toLowerCase(), box: box(e), letters: letters(e), text: (e.innerText || e.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 80),
      family: t.fontFamily, size: parseFloat(t.fontSize), weight: t.fontWeight, style: t.fontStyle, lh: t.lineHeight, ls: t.letterSpacing, color: t.color, align: t.textAlign,
      deco: [deco(e), deco(leaf)].join(' '),
      bg: s.backgroundColor, position: s.position, top: edge(s, 'Top'), bottom: edge(s, 'Bottom'), left: edge(s, 'Left'), right: edge(s, 'Right'),
      radius: [s.borderTopLeftRadius, s.borderTopRightRadius, s.borderBottomRightRadius, s.borderBottomLeftRadius],
      before: pseudo(e, '::before'), after: pseudo(e, '::after'), current: e.getAttribute('aria-current') || ''}; };
  const out = {vw: document.documentElement.clientWidth, vh: innerHeight, docH: document.documentElement.scrollHeight, items: {}};
  for (const [key, selector] of spec) { try { out.items[key] = [...document.querySelectorAll(selector)].map(read); } catch (err) { out.items[key] = []; } }
  const bodyS = getComputedStyle(document.body), htmlS = getComputedStyle(document.documentElement);
  out.bodyBg = bodyS.backgroundColor; out.htmlBg = htmlS.backgroundColor; out.bodyFamily = bodyS.fontFamily;
  out.serifFamilies = [...new Set([...document.querySelectorAll('.serif')].filter(vis).map(e => { const t = main(e); return getComputedStyle(t ? t.parentElement : e).fontFamily; }))];
  // fonts: a link that still leads to Google Fonts (there must be none), and the @font-face rules the page really has
  out.fontLinks = [...document.querySelectorAll('link')].map(l => l.getAttribute('href') || '').filter(h => /fonts\\.(googleapis|gstatic)\\.com/.test(h));
  out.fontFaces = [];
  for (const sh of document.styleSheets) { let rules = null; try { rules = sh.cssRules; } catch (err) { continue; }
    for (const r of rules) { if (!(r instanceof CSSFontFaceRule)) continue;
      const st = r.style, found = /url\\(\\s*["']?([^"')]+)/.exec(st.getPropertyValue('src') || ''); let abs = '';
      try { abs = found ? new URL(found[1], sh.href || location.href).href : ''; } catch (err) { abs = ''; }
      out.fontFaces.push({family: (st.getPropertyValue('font-family') || '').replace(/["']/g, '').trim(), style: (st.getPropertyValue('font-style') || 'normal').trim(),
        weight: (st.getPropertyValue('font-weight') || '400').trim(), display: (st.getPropertyValue('font-display') || '').trim(), src: abs,
        own: abs.indexOf(location.origin + '/') === 0 && abs.indexOf('/fonts/') > 0}); } }
  // the breakpoints of our own stylesheet, as the browser read them
  out.media = []; out.sheet = false;
  const walk = rules => { for (const r of rules) { if (r.media && r.cssRules) out.media.push(r.media.mediaText); if (r.cssRules) walk(r.cssRules); } };
  for (const sh of document.styleSheets) { if (!/css\\/style\\.css(\\?|#|$)/.test(sh.href || '')) continue; out.sheet = true; try { walk(sh.cssRules); } catch (err) { out.mediaError = String(err); } }
  // sticky: does the header stay at the top once the page is scrolled?
  const hd = document.querySelector('header.site-header');
  out.stuck = null;
  if (hd && out.docH > out.vh + 450) { const before = scrollY; window.scrollTo({top: 400, behavior: 'instant'});
    out.stuck = {scrolled: r1(scrollY), top: r1(hd.getBoundingClientRect().top)}; window.scrollTo({top: before, behavior: 'instant'}); }
  // scrolling: does the hours line move?
  const track = document.querySelector('.marquee .track');
  out.marquee = null;
  if (track) { const probe = track.firstElementChild || track; const x0 = probe.getBoundingClientRect().left;
    const running = (track.getAnimations ? track.getAnimations({subtree: true}) : []).filter(a => a.playState === 'running').length;
    await new Promise(r => setTimeout(r, 400));
    out.marquee = {moved: r1(probe.getBoundingClientRect().left - x0), running}; }
  return out;
}"""

# key -> selector. The class names are those of the build contract (tools/CONTRACT.md, sections 6 and 7).
BRIEF_SPEC = [
    ("header", "header.site-header"), ("logo", "header.site-header a.logo img"), ("nav_links", "#main-nav a"), ("menu_btn", "header.site-header .menu-btn"),
    ("footer", "footer.site-footer"), ("foot_rule", "footer.site-footer .foot-rule"), ("foot_cols", "footer.site-footer .foot-cols"),
    ("foot_name", "footer.site-footer .foot-name"), ("foot_role", "footer.site-footer .foot-role"),
    ("foot_brand", "footer.site-footer .foot-brand"), ("foot_contact", "footer.site-footer .foot-contact"), ("foot_links", "footer.site-footer .foot-links"),
    ("foot_text", "footer.site-footer .foot-contact p, footer.site-footer .foot-links a"),
    ("site_title", "main p.site-title"), ("hero_box", "main .hero-box"), ("hero_h", "main #hero-h"), ("dots", "main hr.dots"), ("welcome", "main p.welcome"),
    ("btn", "main a.btn"), ("phone", "main a.phone"), ("salon", "main p.salon"), ("addr", "main a.addr"), ("pin", "main a.addr .pin"),
    ("hours", "main .marquee .track span"),
    ("row", "main .photo-row img"), ("meet_h", "main #meet-h"), ("meet_p", "main .meet p.t1, main .meet p.t2"),
    ("meet_p1", "main .meet .p1 img"), ("meet_p2", "main .meet .p2 img"),
    ("gallery_title", "main h1.page-title"), ("gallery_imgs", "main .gallery a img"),
    ("cards", "main .services article.card"), ("card_imgs", "main .services article.card img"), ("card_titles", "main .services article.card h2"),
    ("card_body", "main .services article.card .desc, main .services article.card .duration, main .services article.card .price, main .services article.card a.pill"),
    ("pills", "main .services article.card a.pill"),
    ("kicker", "main .contact-head p.kicker"), ("contact_h1", "main .contact-head h1"), ("labels", "main #contact-form label"), ("map", "main .map iframe"),
]
# Which nav link is the current page (the five pages of the menu; a policy page has none).
NAV_CURRENT = {"home": "Home", "gallery": "Gallery", "book-online": "Book Online", "about": "About", "contact": "Contact"}
SERIF, SANS = "Bodoni Moda", "Figtree"      # stand in for Didot italic and Proxima Nova, which are licensed for Wix only
INK, PAPER, BEIGE, BUTTON = (29, 21, 9), (254, 254, 253), (232, 225, 218), (85, 79, 70)     # #1d1509 #fefefd #e8e1da #554f46

# What our pages differ in on purpose although Wix is the reference (build contract, section 10).
DECISION_4 = "decision 4 of the build contract: the beige box is centred on the page"
DECISION_8 = "decision 8 of the build contract: the contact details come as Address, Phone, Email, Social Media, Hours"
DECISION_18 = "decision 18 of the build contract: a link inside a sentence is underlined so that it can be told from the text around it"
DECISION_21 = "decision 21 of the build contract: centred means centred, the place where Wix put it by hand is not copied"
DECISION_24 = "decision 24 of the build contract: a policy page keeps one text edge and a centred title, the editor drift of the Wix blocks is not copied"
# Decisions 21 and 24 make one thing intended: the horizontal place (x) of the elements below, on the desktop, and
# only while our element really is centred (or really stands on the one text edge) and the Wix element is no further
# from that place than the drift the decision names. Size, font and vertical place are compared as everywhere else.
HOME_CENTRED = (".site-title", ".welcome", ".dots", ".btn", ".addr")     # decision 21: site title, welcome paragraph, dotted rule, Book Online button, address line
HOME_DRIFT = 18.0               # decision 21: on Wix they sit 3 to 18 px beside the centre
POLICY_PAGES = ("english-refund-policy", "accessibility-statement", "english-privacy-policy", "terms-conditions")
POLICY_DRIFT = 28.0             # decision 24: the Wix blocks stand up to 28 px beside the text edge (titles: beside the centre)
# Phone: where the order of the Wix page is an open question for the owner, and is not asked of our page until she
# has decided. page -> (how the first text of the group starts on the Wix phone page, what is the matter). Every
# paired block of main that stands at or below that text on the Wix phone page is left out of the order check and
# listed in an entry of its own with ok true.
PHONE_ORDER_OPEN = {
    "english-privacy-policy": (
        "Your data may be stored through",
        "On the Wix phone page the paragraphs of the section 'How do we store, use, share and disclose your information?' stand at the very end of the page, "
        "after the contact details, and their heading stands alone above the next heading. On the Wix desktop page and on our page they follow their heading"),
}

INLINE_TAGS = {"span", "a", "em", "strong", "b", "i", "u", "font", "small"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2013": "-", "\u2014": "-", "\u2011": "-", "\u00a0": " "})
RGB_RE = re.compile(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)")
BORDER_RE = re.compile(r"^\s*([\d.]+)px\s+(\w+)\s+(.*)$")


# ---------------------------------------------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------------------------------------------

def px(value, default=None):
    """'12.5px' -> 12.5; 'normal', '50%' and anything else -> default."""
    m = re.match(r"^\s*(-?[\d.]+)px", str(value))
    return float(m.group(1)) if m else default


def colour(value):
    """'rgb(1, 2, 3)' or 'rgba(1, 2, 3, 0.5)' -> (1, 2, 3, 0.5); anything else -> None."""
    m = RGB_RE.search(str(value or ""))
    if not m:
        return None
    a = m.group(4)
    alpha = 1.0 if a is None else (float(a[:-1]) / 100.0 if a.endswith("%") else float(a))
    return (int(round(float(m.group(1)))), int(round(float(m.group(2)))), int(round(float(m.group(3)))), round(alpha, 2))


def show_colour(c):
    if c is None:
        return "none"
    s = "#%02x%02x%02x" % c[:3]
    return s if c[3] >= 0.995 else "%s at %d%%" % (s, round(c[3] * 100))


def same_colour(a, b):
    if a is None or b is None:
        return a is b
    return a[:3] == b[:3] and abs(a[3] - b[3]) <= 0.05


def num(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def text_key(text):
    """The text as it is matched: no spaces, no symbols or emoji, plain quotes and dashes, lower case."""
    t = unicodedata.normalize("NFKC", text or "").translate(QUOTES)
    t = "".join(ch for ch in t if not ch.isspace() and unicodedata.category(ch) not in ("So", "Sk", "Cs", "Co", "Cf", "Mn", "Cc"))
    return t.casefold()


def short(text, limit=44):
    s = " ".join(str(text or "").split())
    return s if len(s) <= limit else s[:limit - 3].rstrip() + "..."


def weight(value):
    v = str(value).strip().lower()
    return {"normal": 400, "bold": 700}.get(v) or int(float(v))


def align_name(value):
    v = str(value or "").replace("-webkit-", "").strip().lower()
    return {"start": "left", "end": "right", "": "left"}.get(v, v)


def anchor_of(align):
    return align if align in ("center", "right") else "left"


def rel_path(path):
    """A path as it may be written into the report: relative to the site folder, forward slashes."""
    try:
        return os.path.relpath(path, common.SITE).replace(os.sep, "/")
    except ValueError:
        return "<tools folder>/" + os.path.basename(path)


def inside(path, folder):
    a, b = os.path.realpath(path), os.path.realpath(folder)
    try:
        return os.path.commonpath([a, b]) == b
    except ValueError:
        return False


def private_file(*parts):
    """Path of a file that shows the Wix site. Raises when it would land inside the site folder."""
    path = os.path.abspath(os.path.join(common.PRIVATE, *parts))
    if inside(path, common.SITE) or inside(common.PRIVATE, common.SITE):
        raise RuntimeError("refused: %s is inside the site folder, and images that show Wix photos must stay outside it" % rel_path(path))
    if not inside(path, common.PRIVATE):
        raise RuntimeError("refused: %s is not inside the private folder" % rel_path(path))
    return path


def entry(page, viewport, check, ok, expected, actual, evidence, owner, **more):
    e = {"page": page, "viewport": viewport, "check": check, "ok": bool(ok), "expected": expected, "actual": actual,
         "evidence": evidence, "owner": owner}
    e.update(more)
    return e


def est_lines(tag, y, h, fs, lh):
    """Lines of text, centre of the first line and line height of a measured element, from its box alone.
    A block is n lines of the line height; an inline element is n - 1 line heights plus the height of its font."""
    if not lh or lh <= 0:
        n = max(1, int(round(h / max(1.0, fs * 1.2))))
        return n, y + h / (2.0 * n), h / n
    first = min(lh, fs * 1.15) if tag in INLINE_TAGS else lh
    n = max(1, int(round((h - first) / lh)) + 1)
    return n, y + (h - (n - 1) * lh) / 2.0, lh


def parse_border(value, scale=1.0):
    """'1px solid rgb(...)' -> (thickness, style, colour), or None when nothing shows."""
    m = BORDER_RE.match(str(value or ""))
    if not m:
        return None
    w, style, col = float(m.group(1)) * scale, m.group(2), colour(m.group(3))
    if w <= 0 or style in ("none", "hidden") or (col is not None and col[3] <= 0):
        return None
    return (w, style, col)


def show_border(b):
    return "none" if b is None else "%spx %s %s" % (num(b[0]), b[1], show_colour(b[2]))


def same_border(a, b, tol):
    if a is None or b is None:
        return a is b
    return a[1] == b[1] and same_colour(a[2], b[2]) and abs(a[0] - b[0]) <= tol + EPS


def radius_of(value, w, h, scale=1.0):
    """Corner radius as it shows: never more than half the shorter side."""
    first = str(value or "0px").split()[0] if str(value or "").strip() else "0px"
    if first.endswith("%"):
        try:
            r = float(first[:-1]) / 100.0 * min(w, h)
        except ValueError:
            r = 0.0
    else:
        r = (px(first, 0.0) or 0.0) * scale
    return min(r, min(w, h) / 2.0)


def overlap_share(a, b):
    """Share of box a that box b covers."""
    ix = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    iy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    area = a["w"] * a["h"]
    return (ix * iy) / area if ix > 0 and iy > 0 and area > 0 else 0.0


def contains(outer, inner, slack=1.5):
    return (outer["x"] - slack <= inner["x"] and outer["y"] - slack <= inner["y"]
            and outer["x"] + outer["w"] + slack >= inner["x"] + inner["w"] and outer["y"] + outer["h"] + slack >= inner["y"] + inner["h"])


def reading_order(items):
    """Top to bottom, and left to right inside a row."""
    rows = []
    for it in sorted(items, key=lambda i: (i["y"], i["x"])):
        if rows and it["y"] - rows[-1][0]["y"] <= max(6.0, 0.3 * min(rows[-1][0]["h"], it["h"])):
            rows[-1].append(it)
        else:
            rows.append([it])
    return [it for row in rows for it in sorted(row, key=lambda i: i["x"])]


def align_lists(A, B, cost, gap):
    """Pair two ordered lists without crossing (the classic alignment). -> list of (a or None, b or None)."""
    n, m = len(A), len(B)
    D = [[0.0] * (m + 1) for _ in range(n + 1)]
    step = [[""] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        D[i][0], step[i][0] = i * gap, "a"
    for j in range(1, m + 1):
        D[0][j], step[0][j] = j * gap, "b"
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i][j], step[i][j] = min((D[i - 1][j - 1] + cost(A[i - 1], B[j - 1]), "ab"), (D[i - 1][j] + gap, "a"), (D[i][j - 1] + gap, "b"))
    out, i, j = [], n, m
    while i > 0 or j > 0:
        how = step[i][j]
        if how == "ab":
            out.append((A[i - 1], B[j - 1])); i -= 1; j -= 1
        elif how == "a":
            out.append((A[i - 1], None)); i -= 1
        else:
            out.append((None, B[j - 1])); j -= 1
    return out[::-1]


def ratio_cost(a, b):
    return min(2.0, abs(math.log(max(a, 0.01) / max(b, 0.01))))


# ---------------------------------------------------------------------------------------------------------------
# From a raw measurement to comparable items. scale is 390 / 320 for the Wix phone page, 1 otherwise: boxes and
# places are multiplied by it, so they are the size they have on a 390 px screen. Font size, letter spacing, line
# height, border thickness and corner radius are never multiplied: they are compared as written (decision 16).
# A text item therefore has two line heights: "lh" as written, and "lh_px" as it is on the screen.
# ---------------------------------------------------------------------------------------------------------------

def scaled_box(b, s):
    return {"x": b["x"] * s, "y": b["y"] * s, "w": b["w"] * s, "h": b["h"] * s}


def build_side(raw, scale, extra=None):
    """-> {text, images, icons, boxes, allboxes, controls, lines, page_bg, header, doc, full_text}"""
    ours = extra is not None
    ex = extra or {}

    def more(kind, i):
        lst = ex.get(kind) or []
        return lst[i] if ours and i < len(lst) else {}

    def gone(it):       # ours only: hidden by a parent, or parked far off the screen (the skip link)
        return ours and (it.get("faded") or it["x"] + it["w"] < -200 or it["y"] + it["h"] < -200)

    side = {"text": [], "images": [], "icons": [], "allboxes": [], "controls": [], "lines": [], "doc": raw.get("doc", {}),
            "header": raw.get("header"), "full_text": ex.get("fullText", "")}

    for i, t in enumerate(raw.get("text", [])):
        it = dict(kind="text", idx=i, region=t["region"], tag=t["tag"], text=t["text"], key=text_key(t["text"]), raw_box=t["box"])
        it.update(scaled_box(t["box"], scale))
        m = more("text", i)
        it.update(sel=m.get("sel", t["tag"]), marks=set(m.get("marks", [])), faded=m.get("faded", False), flow=m.get("flow", False), group=m.get("group", ""))
        family = t.get("fontFamily", "").split(",")[0].strip().strip("\"'")
        it["family"] = family
        it["fs"] = px(t["fontSize"], 0.0) or 0.0
        it["weight"] = weight(t["fontWeight"])
        it["italic"] = t["fontStyle"] in ("italic", "oblique") or "italic" in family.lower()
        it["ls"] = px(t["letterSpacing"], 0.0) or 0.0
        it["color"] = colour(t["color"])
        it["align"] = align_name(t["textAlign"])
        it["deco_el"] = t.get("textDecoration", "none") or "none"
        it["deco"] = m.get("deco", it["deco_el"])
        lh = px(t["lineHeight"]) or None
        if "c1" in m:       # the real lines of text, measured on the live page (ours, never scaled)
            it["ax"] = {"left": m["tl"], "right": m["tr"], "center": (m["tl"] + m["tr"]) / 2.0}
            it["ay"], it["lines"], it["lh"] = m["c1"], m["n"], lh or m["ca"]
            it["tw"], it["tight"] = m["tr"] - m["tl"], True
        else:               # from the stored box, in the numbers as written, then put on the screen
            n, c1, line = est_lines(t["tag"], t["box"]["y"], t["box"]["h"], it["fs"], lh)
            it["ax"] = {"left": it["x"], "right": it["x"] + it["w"], "center": it["x"] + it["w"] / 2.0}
            it["ay"], it["lines"], it["lh"] = c1 * scale, n, line
            it["tw"], it["tight"] = it["w"], t["tag"] in INLINE_TAGS
        it["lh_px"] = it["lh"] * scale
        if not any(ch.isalnum() for ch in it["key"]) or (it["w"] <= 2 * scale and it["h"] <= 2 * scale) or gone(it):
            continue        # an emoji or a star alone, a 1 px label for screen readers, the skip link
        side["text"].append(it)

    for i, im in enumerate(raw.get("images", [])):
        it = dict(kind="image", idx=i, region=im["region"], alt=im.get("alt", ""))
        it.update(scaled_box(im["box"], scale))
        m = more("images", i)
        it.update(sel=m.get("sel", "img"), marks=set(m.get("marks", [])), faded=m.get("faded", False), ph=m.get("ph", False), file=m.get("file", ""))
        it["ay"] = it["y"]
        if gone(it):
            continue
        side["icons" if it["w"] <= ICON_MAX * scale and it["h"] <= ICON_MAX * scale else "images"].append(it)

    for i, b in enumerate(raw.get("boxes", [])):
        c = colour(b["bg"])
        if c is None or c[3] <= 0:
            continue
        it = dict(kind="box", idx=i, region=b["region"], tag=b["tag"], bg=c, position=b.get("position", ""))
        it.update(scaled_box(b["box"], scale))
        m = more("boxes", i)
        it.update(sel=m.get("sel", b["tag"]), marks=set(m.get("marks", [])), faded=m.get("faded", False))
        if ours and isinstance(m.get("paint"), dict):       # painted wider than the element itself, see painted() in EXTRA_JS
            it.update(m["paint"])
        it["ay"] = it["y"]
        if gone(it):
            continue
        side["allboxes"].append(it)

    for i, c in enumerate(raw.get("controls", [])):
        it = dict(kind="control", idx=i, region=c["region"], tag=c["tag"], text=c.get("text", ""), key=text_key(c.get("text", "")), bg=colour(c["bg"]))
        it.update(scaled_box(c["box"], scale))
        m = more("controls", i)
        it.update(sel=m.get("sel", c["tag"]), marks=set(m.get("marks", [])), faded=m.get("faded", False), has_img=m.get("hasImg"))
        it["top"], it["bottom"] = parse_border(c["borderTop"]), parse_border(c["borderBottom"])
        it["radius"] = radius_of(c.get("borderRadius"), c["box"]["w"], c["box"]["h"])
        it["round"] = it["radius"] > 0 and it["radius"] >= min(c["box"]["w"], c["box"]["h"]) / 2.0 - 0.5    # a pill or a circle
        it["ay"] = it["y"]
        if gone(it):
            continue
        side["controls"].append(it)

    for i, ln in enumerate(ex.get("lines") or []):      # ours only: a hairline drawn as the border of a plain element
        col = colour(ln["color"])
        it = dict(kind="line", idx=1000 + i, region=ln["region"], x=ln["x"], y=ln["y"], w=ln["w"], h=ln["thick"], thick=ln["thick"],
                  style=ln["style"], color=col, sel=ln.get("sel", ""), marks=set(ln.get("marks", [])), faded=ln.get("faded", False), spare=True)
        it["ay"] = it["y"]
        if not gone(it):
            side["lines"].append(it)

    # The colour of the page: our body background, on Wix the colour of the box that spans the whole document.
    body = colour(raw.get("bodyBg"))
    if body is None or body[3] <= 0:
        doc_w, doc_h = side["doc"].get("w", 0) * scale, side["doc"].get("h", 0) * scale
        whole = [b for b in side["allboxes"] if b["w"] >= doc_w - 2 and b["h"] >= doc_h * 0.9]
        body = whole[0]["bg"] if whole else None
    side["page_bg"] = body
    return side


def classify_controls(side):
    """Sort the measured links, buttons, fields, rules and frames into kinds. Plain text links are left out: their
    text is compared as text."""
    kinds = {"line": list(side["lines"]), "button": [], "field": [], "frame": [], "iconlink": [], "iconbutton": []}
    for c in side["controls"]:
        tag = c["tag"]
        dotted = any(b is not None and b[1] == "dotted" for b in (c["top"], c["bottom"]))
        if tag == "hr" or (dotted and tag not in ("a", "button", "input", "textarea", "iframe")):
            edge = c["top"] or c["bottom"]
            if edge is None:
                continue
            y = c["y"] if c["top"] else c["y"] + c["h"] - edge[0]
            kinds["line"].append(dict(c, kind="line", y=y, ay=y, h=edge[0], thick=edge[0], style=edge[1], color=edge[2], spare=False))
        elif tag == "iframe":
            kinds["frame"].append(dict(c, kind="frame"))
        elif tag in ("input", "textarea"):
            kinds["field"].append(dict(c, kind="field"))
        elif tag == "button":
            kinds["button" if c["key"] else "iconbutton"].append(dict(c, kind="button" if c["key"] else "iconbutton"))
        elif tag == "a":
            boxy = (c["bg"] is not None and c["bg"][3] > 0) or c["top"] is not None or c["bottom"] is not None
            picture = c.get("has_img")
            if picture is None:     # Wix: a link whose box is the box of a photo
                picture = any(overlap_share(c, im) > 0.8 and overlap_share(im, c) > 0.8 for im in side["images"])
            if c["key"]:
                if boxy:
                    kinds["button"].append(dict(c, kind="button"))
            elif not picture or any(overlap_share(c, ic) > 0.6 for ic in side["icons"]):
                if not any(overlap_share(c, im) > 0.8 and overlap_share(im, c) > 0.8 for im in side["images"]):
                    kinds["iconlink"].append(dict(c, kind="iconlink"))
    return kinds


def backdrop(item, side):
    """What shows through a transparent background: the smallest coloured box around the item, else the page."""
    c = item.get("bg")
    if c is not None and c[3] >= 0.5:
        return c
    cx, cy = item["x"] + item["w"] / 2.0, item["y"] + item["h"] / 2.0
    around = [b for b in side["allboxes"] if b["bg"][3] >= 0.5 and b["x"] <= cx <= b["x"] + b["w"] and b["y"] <= cy <= b["y"] + b["h"]
              and b["w"] * b["h"] > item["w"] * item["h"] * 1.05]
    if around:
        return min(around, key=lambda b: b["w"] * b["h"])["bg"]
    return side["page_bg"]


def visible_boxes(side):
    """The coloured boxes a visitor can tell from the page: not the page colour, not a link, button or field (those
    are compared as controls), not hidden under a photo or a frame, not inside a box of the same colour, not buried
    under later boxes."""
    page = side["page_bg"]
    frames = [c for c in side["controls"] if c["tag"] == "iframe"]
    cand = []
    for b in side["allboxes"]:
        if b["tag"] in ("a", "button", "input", "textarea", "select", "iframe", "img", "html", "body"):
            continue
        if page is not None and b["bg"][:3] == page[:3] and b["bg"][3] >= 0.95:
            continue
        if any(overlap_share(b, im) >= 0.9 for im in side["images"]) or any(overlap_share(b, f) >= 0.9 for f in frames):
            continue
        cand.append(b)
    keep = []
    for b in cand:
        if any(o is not b and same_colour(o["bg"], b["bg"]) and contains(o, b) and (o["w"] * o["h"] > b["w"] * b["h"] or o["idx"] < b["idx"]) for o in cand):
            continue
        later = [o for o in side["allboxes"] if o["idx"] > b["idx"] and o["bg"][3] >= 0.95 and o["bg"][:3] != b["bg"][:3] and overlap_share(b, o) > 0]
        if later:
            hit = total = 0
            for gx in range(24):
                for gy in range(24):
                    X, Y = b["x"] + (gx + 0.5) * b["w"] / 24.0, b["y"] + (gy + 0.5) * b["h"] / 24.0
                    total += 1
                    hit += any(o["x"] <= X <= o["x"] + o["w"] and o["y"] <= Y <= o["y"] + o["h"] for o in later)
            if hit >= total * 0.97:
                continue
        keep.append(b)
    return keep


def tidy_wix_images(images):
    """Wix keeps a second copy of some photos while they slide in, and the measurement can catch a photo in the
    middle of that move. Drop the copy, and put a photo that stands a few pixels out of an otherwise even row
    back on the row."""
    out = []
    for im in sorted(images, key=lambda i: -(i["w"] * i["h"])):
        if not any(overlap_share(im, o) > 0.6 and overlap_share(o, im) > 0.5 for o in out):
            out.append(im)
    out.sort(key=lambda i: i["idx"])
    for im in out:
        row = [o for o in out if o is not im and o["region"] == im["region"] and abs(o["y"] - im["y"]) <= 8 and abs(o["h"] - im["h"]) <= 8 and abs(o["w"] - im["w"]) <= 8]
        if len(row) < 2:
            continue
        ys, hs, ws = [round(o["y"], 1) for o in row], [round(o["h"], 1) for o in row], [round(o["w"], 1) for o in row]
        y, h, w = max(set(ys), key=ys.count), max(set(hs), key=hs.count), max(set(ws), key=ws.count)
        if ys.count(y) < 2 or (abs(im["y"] - y) < 0.05 and abs(im["h"] - h) < 0.05 and abs(im["w"] - w) < 0.05):
            continue
        xs = sorted(o["x"] for o in row if round(o["y"], 1) == y)
        steps = [b - a for a, b in zip(xs, xs[1:]) if b - a > 1]
        step = min(steps) if steps else None
        x = im["x"]
        if step:
            k = round((im["x"] - xs[0]) / step)
            if abs(xs[0] + k * step - im["x"]) <= 8:
                x = xs[0] + k * step
        im["moved_from"] = "%s, %s, %s x %s" % (num(im["x"]), num(im["y"]), num(im["w"]), num(im["h"]))
        im.update(x=x, y=y, ay=y, w=w, h=h)
    return out


# ---------------------------------------------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------------------------------------------

def tag_class(tag):
    if tag in HEADING_TAGS:
        return "heading"
    return tag if tag in ("label", "button", "a", "li") else "text"


def pair_same_text(wl, ol):
    """Several elements with the same text on both sides: pair them by kind of element and font size, else in order."""
    if len(wl) == 1 and len(ol) == 1:
        return [(wl[0], ol[0])]
    if max(len(wl), len(ol)) > 6:
        return list(zip(wl, ol))

    def cost(w, o, iw, io):
        return (0.0 if tag_class(w["tag"]) == tag_class(o["tag"]) else 1.0) + min(1.0, 3 * ratio_cost(max(w["fs"], 1), max(o["fs"], 1))) + 0.01 * abs(iw - io)
    best, best_cost = None, None
    small, big, swap = (wl, ol, False) if len(wl) <= len(ol) else (ol, wl, True)
    for perm in itertools.permutations(range(len(big)), len(small)):
        total = 0.0
        for i, j in enumerate(perm):
            total += cost(big[j], small[i], j, i) if swap else cost(small[i], big[j], i, j)
        if best_cost is None or total < best_cost - 1e-9:
            best, best_cost = perm, total
    return [((big[j], small[i]) if swap else (small[i], big[j])) for i, j in enumerate(best)]


def match_texts(W, O):
    pairs, used_w, used_o = [], set(), set()

    def take(groups_w, groups_o):
        for k, wl in groups_w.items():
            ol = groups_o.get(k)
            if not ol:
                continue
            for w, o in pair_same_text(wl, ol):
                pairs.append((w, o, "exact"))
                used_w.add(id(w)); used_o.add(id(o))

    def groups(items, used, by_region):
        g = {}
        for it in items:
            if id(it) not in used:
                g.setdefault((it["region"], it["key"]) if by_region else it["key"], []).append(it)
        return g

    take(groups(W, used_w, True), groups(O, used_o, True))        # same region
    take(groups(W, used_w, False), groups(O, used_o, False))      # anywhere on the page
    cands = []
    for w in W:
        if id(w) in used_w:
            continue
        for o in O:
            if id(o) in used_o:
                continue
            a, b = w["key"], o["key"]
            if min(len(a), len(b)) < 4:
                continue
            if a.startswith(b) or b.startswith(a):
                if abs(len(a) - len(b)) > 3 and min(len(a), len(b)) < 0.6 * max(len(a), len(b)):
                    continue
                r = 0.9 + 0.1 * min(len(a), len(b)) / max(len(a), len(b))
            else:
                if min(len(a), len(b)) < 12:
                    continue
                r = difflib.SequenceMatcher(None, a, b).ratio()
                if r < 0.72:
                    continue
            cands.append((r - (0.05 if w["region"] != o["region"] else 0.0), w["idx"], o["idx"], w, o))
    for r, _i, _j, w, o in sorted(cands, key=lambda c: (-c[0], c[1], c[2])):
        if id(w) in used_w or id(o) in used_o:
            continue
        pairs.append((w, o, "fuzzy"))
        used_w.add(id(w)); used_o.add(id(o))
    return pairs, [w for w in W if id(w) not in used_w], [o for o in O if id(o) not in used_o]


def pair_in_order(wl, ol, cost, gap):
    wl, ol = reading_order(wl), reading_order(ol)
    if len(wl) == len(ol):
        return list(zip(wl, ol))
    return align_lists(wl, ol, cost, gap)


def by_region(items):
    out = {}
    for it in items:
        out.setdefault(it["region"], []).append(it)
    return out


# ---------------------------------------------------------------------------------------------------------------
# The comparison of one page in one viewport
# ---------------------------------------------------------------------------------------------------------------

class Compare:
    def __init__(self, slug, view, wix_raw, ours_raw, extra, wix_text="", wix_shot=None):
        self.slug, self.view, self.vp = slug, view, view.name
        self.phone = view.kind == "phone"
        self.tol, self.scale = TOL[view.kind], (PHONE_SCALE if self.phone else 1.0)
        self.wix = build_side(wix_raw, self.scale)
        self.ours = build_side(ours_raw, 1.0, extra)
        self.wix["images"] = tidy_wix_images(self.wix["images"])
        self.wix_text = text_key(wix_text) + "".join(t["key"] for t in self.wix["text"])
        self.ours_text = text_key(self.ours["full_text"])
        self.wix_shot = wix_shot
        self.pairs = []             # {k, label, w, o, diffs, ...}
        self.fails = []             # ready entries (ok false) that have no pair: something exists on one side only
        self.intended = []          # (label, expected, actual, evidence)
        self.notes = []             # short texts for the summary
        self.font_metrics = []
        self.unpaired = []          # text that only one side shows: listed, not counted (wording is the content check's job)
        self.blocks_ours, self.blocks_wix = [], []      # intended extra blocks that push what is under them
        self.page_info = []         # phone: sizes of the page itself that are listed, not judged (label, wix, ours, d)
        self.counts = {}

    # -- small tools -------------------------------------------------------------------------------------------

    def diff(self, pair, prop, wix, ours, d=None, cls="count", why=""):
        """Note one difference of a pair. cls: "count" (ok false), "intended" (ok true, on purpose), or "info".
        On the phone a place or a size is never judged (decision 16): it becomes "info" whatever was asked."""
        if self.phone and (prop in ("w", "h", "y") or prop.startswith("x")):
            cls = "info"
        pair["diffs"].append({"prop": prop, "wix": wix, "ours": ours, "d": d, "cls": cls, "why": why})

    def add_pair(self, kind, label, w, o, **more):
        p = dict(k=kind, label=label, w=w, o=o, diffs=[], region=o["region"])
        p.update(more)
        self.pairs.append(p)
        return p

    def length(self, pair, prop, wv, ov, tol=None, unit=""):
        """Compare one length. Only the Wix value passes: it counts when it is off by more than the tolerance."""
        tol = self.tol if tol is None else tol
        d = ov - wv
        if abs(d) <= tol + EPS:
            return True
        self.diff(pair, prop, num(wv) + unit, num(ov) + unit, d)
        return False

    # -- the page ----------------------------------------------------------------------------------------------

    def run(self):
        self.match()
        for p in self.pairs:
            if p["k"] == "text":
                self.text_properties(p)
            elif p["k"] == "area":
                self.length(p, "w", p["w"]["w"], p["o"]["w"])
                # The height of a masonry depends on how the photos fall, so it gets a share of the Wix height as
                # allowance, not 2 px. A page with a column too few (or too many) is far outside it.
                self.length(p, "h", p["w"]["h"], p["o"]["h"], max(self.tol, AREA_HEIGHT_SHARE * p["w"]["h"]))
            else:
                self.box_properties(p)
        self.positions()
        self.page_level()
        return self.entries()

    def match(self):
        W, O = self.wix, self.ours
        # 1. text. What our page adds on purpose never takes part in the matching.
        ours_text = []
        for t in O["text"]:
            reason = self.intended_text(t)
            if reason:
                self.intended_extra(reason, t, "text '%s', %spx" % (short(t["text"]), num(t["fs"])))
            else:
                ours_text.append(t)
        pairs, only_w, only_o = match_texts(W["text"], ours_text)
        for w, o, how in pairs:
            p = self.add_pair("text", "text: " + short(o["text"]), w, o, how=how)
            if o["flow"]:
                p["nopos"] = "it is part of a sentence, so its place follows the wrapping of the text"
            if ".marquee" in o["marks"]:
                p["nox"] = "the hours line scrolls"
        matched_keys = {o["key"] for _w, o, _h in pairs}
        for o in only_o:
            if ".marquee" in o["marks"] and o["key"] in matched_keys:
                continue            # the other copies of the scrolling hours line
            if len(o["key"]) >= 3 and o["key"] in self.wix_text:
                self.counts["text_part_ours"] = self.counts.get("text_part_ours", 0) + 1
                continue            # Wix has this text inside a longer text node
            self.unpaired.append({"side": "ours", "text": short(o["text"], 80), "x": round(o["x"], 1), "y": round(o["y"], 1), "where": o["sel"]})
        for w in only_w:
            if len(w["key"]) >= 3 and w["key"] in self.ours_text:
                self.counts["text_part_wix"] = self.counts.get("text_part_wix", 0) + 1
                continue            # our page has this text inside a longer text node
            if self.slug == PRIVACY_SLUG and WIX_WORD.search(w["text"]):
                # The Privacy Policy carries no sentence that names Wix (the privacy rule of qa/check_content.py). Where
                # Wix has such a sentence our page has a shorter text or none: under "Cookies may be set by:" Wix lists
                # two items on three lines, our page one item on one line (the booking provider went on 2 November 2026,
                # Google Fonts on 9 November 2026, decision 38). So what stands under it sits higher than on Wix.
                self.blocks_wix.append((w["y"], w["y"] + w["h"], "a sentence about Wix that our Privacy Policy leaves out on purpose ('%s')" % short(w["text"], 44)))
            self.unpaired.append({"side": "wix", "text": short(w["text"], 80), "x": round(w["x"], 1), "y": round(w["y"], 1), "where": "%s in %s" % (w["tag"], w["region"])})
        text_pairs = [p for p in self.pairs if p["k"] == "text"]

        def rank(items, side):
            """Where an element sits among the paired texts: how many are above it, and which paired text is the
            nearest above and the nearest below in its own column. Two elements with the same texts around them
            are the same element, whatever the order in the page source."""
            for it in items:
                mid = it["y"] + it["h"] / 2.0
                it["rank"] = sum(1 for p in text_pairs if p[side]["region"] == it["region"] and p[side]["ay"] < mid)
                up = down = None
                for n, p in enumerate(text_pairs):
                    t = p[side]
                    if t["region"] != it["region"] or p.get("nopos") or p.get("nox"):
                        continue
                    ov = min(it["x"] + it["w"], t["ax"]["right"]) - max(it["x"], t["ax"]["left"])
                    if ov < min(4.0, 0.5 * min(it["w"], t["ax"]["right"] - t["ax"]["left"])):
                        continue
                    if t["ay"] < it["y"]:
                        if up is None or t["ay"] > up[0]:
                            up = (t["ay"], n)
                    elif down is None or t["ay"] < down[0]:
                        down = (t["ay"], n)
                it["ctx"] = (up[1] if up else None, down[1] if down else None)

        def pair_items(wl, ol, cost, gap):
            out, rest_w, rest_o, gw, go = [], [], [], {}, {}
            for it in wl:
                gw.setdefault(it["ctx"], []).append(it)
            for it in ol:
                go.setdefault(it["ctx"], []).append(it)
            for k in list(gw) + [k for k in go if k not in gw]:
                a, b = reading_order(gw.get(k, [])), reading_order(go.get(k, []))
                n = min(len(a), len(b)) if k != (None, None) else 0
                out += list(zip(a[:n], b[:n]))
                rest_w += a[n:]; rest_o += b[n:]
            return out + pair_in_order(rest_w, rest_o, cost, gap)

        # 2. images
        ours_images = list(O["images"])
        if self.slug == "home" and self.phone:
            row = [i for i in ours_images if ".photo-row" in i["marks"]]
            if row:
                ours_images = [i for i in ours_images if i not in row]
                x0, y0 = min(i["x"] for i in row), min(i["y"] for i in row)
                x1, y1 = max(i["x"] + i["w"] for i in row), max(i["y"] + i["h"] for i in row)
                cols = len({round(i["x"]) for i in row})
                self.intended.append(("phone photo row", "Wix hides the row of photos on the phone",
                                      "%d photos in %d columns, %s x %s px at x %s, y %s" % (len(row), cols, num(x1 - x0), num(y1 - y0), num(x0), num(y0)),
                                      "ours: " + row[0]["sel"]))
                self.blocks_ours.append((y0, y1, "the phone photo row"))
        for m, il in by_region(ours_images).items():
            for n, im in enumerate(sorted([i for i in il if ".photo-row" in i["marks"]], key=lambda i: (round(i["y"] / 20.0), i["x"]))):
                im["place"] = n
        rank(W["images"], "w"); rank(ours_images, "o")
        wi, oi = by_region(W["images"]), by_region(ours_images)
        for region in sorted(set(wi) | set(oi)):
            wl, ol = wi.get(region, []), oi.get(region, [])
            if self.slug == "gallery" and region == "main":
                self.gallery(wl, ol)
                continue
            cost = lambda a, b: ratio_cost(a["w"] / max(a["h"], 1), b["w"] / max(b["h"], 1)) + 0.3 * min(3, abs(a["rank"] - b["rank"]))
            for w, o in pair_items(wl, ol, cost, 0.9):
                if w is not None and o is not None:
                    self.add_pair("image", "image: " + (o["file"] or o["sel"]), w, o, place=o.get("place", 0))
                elif w is not None:
                    if self.slug == "home" and self.phone and self.blocks_ours:
                        self.intended.append(("photo that Wix shows under Meet Gerta on the phone", "%s x %s px at x %s, y %s" % (num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                              "our phone page shows the photos in the photo row instead", "Wix image %d of %s" % (w["idx"] + 1, region)))
                        self.blocks_wix.append((w["y"], w["y"] + w["h"], "a photo that our phone page shows in the photo row instead"))
                    else:
                        self.fails.append(dict(check="only on Wix: image %s x %s at x %s, y %s" % (num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                               expected="an image of %s x %s px at x %s, y %s" % (num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                               actual="our page has no image there", evidence="Wix image %d of %s, alt '%s'" % (w["idx"] + 1, region, short(w["alt"])), owner="PAGES", d=None))
                else:
                    self.fails.append(dict(check="only on our page: image " + (o["file"] or o["sel"]), expected="no image (the Wix page shows none there)",
                                           actual="%s x %s px at x %s, y %s" % (num(o["w"]), num(o["h"]), num(o["x"]), num(o["y"])), evidence="ours: " + o["sel"], owner="DESIGN", d=None))
        placeholders = [i for i in O["images"] if i["ph"]]
        if placeholders:
            self.intended.append(("placeholders instead of photos", "the Wix photos (licensed for Wix only)",
                                  "%d of %d images are placeholders with the size of the photo they stand for" % (len(placeholders), len(O["images"])),
                                  "class ph: " + ", ".join(sorted({i["file"] for i in placeholders if i["file"]})[:30])))

        # 3. coloured boxes
        wb, ob = visible_boxes(W), visible_boxes(O)
        rank(wb, "w"); rank(ob, "o")
        wr, orr = by_region(wb), by_region(ob)
        for region in sorted(set(wr) | set(orr)):
            cost = lambda a, b: (0.0 if same_colour(a["bg"], b["bg"]) else 0.8) + min(1.0, ratio_cost(a["w"], b["w"])) + 0.5 * min(1.0, ratio_cost(a["h"], b["h"])) + 0.3 * min(3, abs(a["rank"] - b["rank"]))
            for w, o in pair_items(wr.get(region, []), orr.get(region, []), cost, 1.0):
                if w is not None and o is not None:
                    self.add_pair("box", "box: " + o["sel"], w, o)
                elif w is not None:
                    self.fails.append(dict(check="only on Wix: %s box %s x %s at x %s, y %s" % (show_colour(w["bg"]), num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                           expected="a %s box of %s x %s px at x %s, y %s" % (show_colour(w["bg"]), num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                           actual="our page has no coloured box there", evidence="Wix %s in %s" % (w["tag"], region), owner="DESIGN", d=None))
                else:
                    self.fails.append(dict(check="only on our page: %s box %s" % (show_colour(o["bg"]), o["sel"]), expected="no coloured box (the Wix page shows none there)",
                                           actual="%s, %s x %s px at x %s, y %s" % (show_colour(o["bg"]), num(o["w"]), num(o["h"]), num(o["x"]), num(o["y"])), evidence="ours: " + o["sel"], owner="DESIGN", d=None))

        # 4. buttons, fields, rules, frames, icon links
        wk, ok_ = classify_controls(W), classify_controls(O)
        names = {"line": "rule", "button": "button", "field": "field", "frame": "frame", "iconlink": "icon link", "iconbutton": "button without text"}
        for kind in ("button", "field", "line", "frame", "iconlink", "iconbutton"):
            rank(wk[kind], "w"); rank(ok_[kind], "o")
            wr, orr = by_region(wk[kind]), by_region(ok_[kind])
            for region in sorted(set(wr) | set(orr)):
                wl, ol = wr.get(region, []), orr.get(region, [])
                if kind == "button":
                    got = []
                    for k in sorted({c["key"] for c in wl} | {c["key"] for c in ol}):
                        got += pair_items([c for c in wl if c["key"] == k], [c for c in ol if c["key"] == k], lambda a, b: 0.0, 0.6)
                elif kind == "line":
                    cost = lambda a, b: (0.0 if a["style"] == b["style"] else 0.6) + min(1.0, ratio_cost(a["w"], b["w"])) + 0.3 * min(3, abs(a["rank"] - b["rank"]))
                    need = len(wl) - len([c for c in ol if not c["spare"]])
                    if need <= 0:
                        ol = [c for c in ol if not c["spare"]]
                    got = pair_items(wl, ol, cost, 0.9)
                else:
                    got = pair_items(wl, ol, lambda a, b: 0.3 * min(3, abs(a["rank"] - b["rank"])), 0.6)
                for w, o in got:
                    if w is not None and o is not None:
                        what = short(o["text"], 30) if kind == "button" else o["sel"]
                        self.add_pair(kind, "%s: %s" % (names[kind], what), w, o)
                    elif w is not None:
                        round_blue = (w["bg"] is not None and w["bg"][:3] == (0, 138, 252)) or (abs(w["w"] - w["h"]) < 2 and w["round"] and w["w"] <= 80 * self.scale)
                        if kind == "iconbutton" and round_blue:
                            self.intended.append(("Wix chat button", "%s button of %s x %s px at x %s, y %s" % (show_colour(w["bg"]), num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                                  "not on our page", "a Wix widget, measured in %s" % region))
                            continue
                        self.fails.append(dict(check="only on Wix: %s %s x %s at x %s, y %s" % (names[kind], num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"])),
                                               expected="a %s of %s x %s px at x %s, y %s%s" % (names[kind], num(w["w"]), num(w["h"]), num(w["x"]), num(w["y"]), (" '%s'" % short(w["text"], 30)) if w.get("key") else ""),
                                               actual="our page has none there", evidence="Wix %s in %s" % (w["tag"], region), owner="PAGES", d=None))
                    elif o is not None:
                        if o.get("spare"):
                            continue
                        if self.phone and region == "header" and ".menu-btn" in o["marks"]:
                            self.intended.append(("phone menu button", "the brief: phone header with a menu button (see brief-phone-header)",
                                                  "%s x %s px at x %s, y %s" % (num(o["w"]), num(o["h"]), num(o["x"]), num(o["y"])), "ours: " + o["sel"]))
                            continue
                        self.fails.append(dict(check="only on our page: %s %s" % (names[kind], o["sel"]), expected="none (the Wix page shows none there)",
                                               actual="%s x %s px at x %s, y %s" % (num(o["w"]), num(o["h"]), num(o["x"]), num(o["y"])), evidence="ours: " + o["sel"], owner="PAGES", d=None))

    def intended_text(self, t):
        marks = t["marks"]
        if ".copy" in marks:
            return "copyright line"
        if ".book-note" in marks:
            return "closing booking note"
        if (".info-item" in marks or ".info" in marks) and text_key(t["group"]) == "hours":
            return "extra Hours block on the contact page"
        return ""

    def intended_extra(self, reason, item, what):
        for i, (label, exp, act, ev) in enumerate(self.intended):
            if label == reason:
                self.intended[i] = (label, exp, act + "; " + what, ev)
                break
        else:
            self.intended.append((reason, "not on the Wix page", what, "ours: " + item["sel"]))
        if reason != "copyright line":
            self.blocks_ours.append((item["y"], item["y"] + item["h"], "the " + reason))

    def gallery(self, wl, ol):
        """The brief asks for a masonry of 3 columns; Wix arranges its 21 photos by hand. So the single photos cannot
        sit at the same place. Compared instead: how many photos, and the area they fill."""
        def area(il, side):
            x0, y0 = min(i["x"] for i in il), min(i["y"] for i in il)
            x1, y1 = max(i["x"] + i["w"] for i in il), max(i["y"] + i["h"] for i in il)
            return dict(kind="area", region="main", x=x0, y=y0, ay=y0, w=x1 - x0, h=y1 - y0, sel="div.gallery", marks=set(il[0].get("marks", ())), side=side)
        if len(wl) != len(ol):
            self.fails.append(dict(check="gallery: number of photos", expected="%d photos" % len(wl), actual="%d photos" % len(ol), evidence="images in main, in the gallery", owner="PAGES", d=abs(len(wl) - len(ol))))
        if not wl or not ol:
            return
        self.add_pair("area", "gallery: the area the photos fill", area(wl, "w"), area(ol, "o"))
        cols = sorted({round(i["x"]) for i in ol})
        self.intended.append(("gallery photos are arranged as a masonry", "Wix: %d photos placed by hand, each with its own size" % len(wl),
                              "%d photos in %d columns" % (len(ol), len(cols)),
                              "the brief asks for a masonry (3 columns at 1265 px, see brief-gallery), so the place and size of the single photos are not compared; the area they fill is"))

    # -- properties --------------------------------------------------------------------------------------------

    def text_properties(self, p):
        w, o = p["w"], p["o"]
        self.length(p, "font-size", w["fs"], o["fs"], FONT_TOL, unit="px")      # on the phone too: the Wix size as written
        if w["weight"] != o["weight"]:
            self.diff(p, "font-weight", str(w["weight"]), str(o["weight"]))
        if w["italic"] != o["italic"]:
            self.diff(p, "font-style", "italic" if w["italic"] else "normal", "italic" if o["italic"] else "normal")
        if not same_colour(w["color"], o["color"]):
            self.diff(p, "colour", show_colour(w["color"]), show_colour(o["color"]))
        self.length(p, "letter-spacing", w["ls"], o["ls"], max(SPACING_TOL, SPACING_EM * o["fs"]), unit="px")
        wrapped = max(w["lines"], o["lines"]) > 1
        if wrapped:
            self.length(p, "line-height", w["lh"], o["lh"], TYPE_TOL, unit="px")
            if w["align"] != o["align"] and not o["flow"]:
                self.diff(p, "text-align", w["align"], o["align"])
        # decoration. The Wix function reads the element alone, and an underline set on a parent does not show there,
        # so a Wix "none" is checked in the Wix screenshot before it is believed.
        ours_ul = "underline" in o["deco"]
        wix_ul = "underline" in w["deco_el"]
        if not wix_ul and w["lines"] == 1 and self.wix_shot is not None:
            seen = shot_underlined(self.wix_shot, w["raw_box"], w["color"])
            wix_ul = seen if seen is not None else (None if ours_ul else False)
        elif not wix_ul and ours_ul:
            wix_ul = None           # cannot be told from the stored measurement
        if wix_ul is None:
            self.notes.append("underline of '%s' could not be compared (not in the Wix measurement of that element)" % short(o["text"], 30))
        elif wix_ul != ours_ul:
            if ours_ul and o["flow"] and o["tag"] == "a":
                self.diff(p, "decoration", "none", "underline", None, "intended", DECISION_18)
            else:
                self.diff(p, "decoration", "underline" if wix_ul else "none", "underline" if ours_ul else "none")
        # font metrics, never counted
        fm = {}
        if w["lines"] != o["lines"]:
            fm["lines"] = (w["lines"], o["lines"])
        hw, ho = w["lines"] * w["lh_px"], o["lines"] * o["lh_px"]
        if wrapped and abs(ho - hw) > self.tol + EPS:
            fm["height"] = (round(hw, 1), round(ho, 1))
        if w["tight"] and o["tight"] and w["lines"] == 1 and o["lines"] == 1 and abs(o["tw"] - w["tw"]) > self.tol + EPS:
            fm["width"] = (round(w["tw"], 1), round(o["tw"], 1))
        if fm:
            fm["size"] = max([abs(v[1] - v[0]) for k, v in fm.items() if k in ("height", "width")] or [0.0])
            fm["text"] = short(o["text"], 50)
            self.font_metrics.append(fm)

    def box_properties(self, p):
        w, o, k = p["w"], p["o"], p["k"]
        if k == "line":
            self.length(p, "w", w["w"], o["w"])
            if w["style"] != o["style"]:
                self.diff(p, "line style", w["style"], o["style"])
            if not same_colour(w["color"], o["color"]):
                self.diff(p, "line colour", show_colour(w["color"]), show_colour(o["color"]))
            self.length(p, "thickness", w["thick"], o["thick"], BORDER_TOL, unit="px")
            return
        self.length(p, "w", w["w"], o["w"])
        if k == "box" and o["region"] == "footer" and self.footer_grew(p):
            pass
        else:
            self.length(p, "h", w["h"], o["h"])
        if k == "box":
            if not same_colour(w["bg"], o["bg"]):
                self.diff(p, "background", show_colour(w["bg"]), show_colour(o["bg"]))
        if k in ("button", "field"):
            bw, bo = backdrop(w, self.wix), backdrop(o, self.ours)
            if not same_colour(bw, bo):
                self.diff(p, "background", show_colour(bw), show_colour(bo))
            for side_name in ("top", "bottom"):
                if not same_border(w[side_name], o[side_name], BORDER_TOL):
                    self.diff(p, "border-" + side_name, show_border(w[side_name]), show_border(o[side_name]))
            if not (w["round"] and o["round"]):     # two pills are the same shape whatever number is written
                self.length(p, "corner radius", w["radius"], o["radius"], TYPE_TOL, unit="px")

    def footer_grew(self, p):
        """The copyright line makes our footer taller than the Wix footer. That much, and no more, is intended."""
        w, o = p["w"], p["o"]
        copy = [t for t in self.ours["text"] if ".copy" in t["marks"] and t["tag"] == "p"]
        if not copy:
            return False
        room = sum(t["h"] for t in copy) + 40
        d = o["h"] - w["h"]
        if self.tol < d <= room + self.tol:
            self.diff(p, "h", num(w["h"]), num(o["h"]), d, "intended", "the copyright line makes the footer taller")
            return True
        return abs(d) <= self.tol + EPS

    # -- positions ---------------------------------------------------------------------------------------------

    def positions(self):
        """x and y of every pair. Each is judged against the page and against the element straight above it, so that
        a column that moved, or a block that grew, is reported where it starts and not again for everything under it."""
        tol = self.tol
        placed = [p for p in self.pairs if not p.get("nopos")]
        boxes = [p for p in placed if p["k"] == "box"]
        for p in placed:
            w, o = p["w"], p["o"]
            if p["k"] == "text":
                names = [anchor_of(w["align"])]
                if anchor_of(o["align"]) not in names:
                    names.append(anchor_of(o["align"]))
                p["dx"] = [(n, w["ax"][n], o["ax"][n]) for n in names]
            else:
                p["dx"] = [("left", w["x"], o["x"])]
                if abs(o["w"] - w["w"]) > tol + EPS:
                    p["dx"] += [("right", w["x"] + w["w"], o["x"] + o["w"]), ("center", w["x"] + w["w"] / 2.0, o["x"] + o["w"] / 2.0)]
            p["dy"] = o["ay"] - w["ay"]
            p["xoff"] = None if p.get("nox") else min((ov - wv for _n, wv, ov in p["dx"]), key=abs)
        header_delta = 0.0
        if self.wix["header"] and self.ours["header"]:
            header_delta = self.ours["header"]["box"]["h"] - self.wix["header"]["box"]["h"] * self.scale
        placed.sort(key=lambda p: (p["w"]["y"], -(p["w"]["w"] * p["w"]["h"])))
        for i, p in enumerate(placed):
            w = p["w"]
            near = far = None           # the nearest element above in the same column, else the nearest above at all
            for q in placed[:i]:
                if q["region"] != p["region"] and not (p["region"] == "footer" and q["region"] == "main"):
                    continue
                r = q["w"]
                holds = contains(r, w, 1) and r["w"] * r["h"] > w["w"] * w["h"]
                if r["y"] > w["y"] - 0.5 and not holds:
                    continue
                ov = min(w["x"] + w["w"], r["x"] + r["w"]) - max(w["x"], r["x"])
                column = ov >= min(4.0, 0.5 * min(w["w"], r["w"])) and not p.get("nox")
                score = (r["y"], ov)
                if column and (near is None or score > near[0]):
                    near = (score, q, holds)
                if far is None or score > far[0]:
                    far = (score, q, holds)
            _score, pred, inside_pred = near or far or (None, None, False)
            if not p.get("nox"):
                self.check_x(p, pred, boxes)
            self.check_y(p, pred, inside_pred, header_delta, boxes)

    def check_x(self, p, pred, boxes):
        tol, w, o = self.tol, p["w"], p["o"]
        bases = [0.0]
        around = [b for b in boxes if b is not p and contains(b["w"], w, 3) and contains(b["o"], o, 3)]
        if around:              # the same place inside its coloured box
            b = min(around, key=lambda q: q["w"]["w"] * q["w"]["h"])
            dl, dw = b["o"]["x"] - b["w"]["x"], b["o"]["w"] - b["w"]["w"]
            bases += [dl, dl + dw / 2.0, dl + dw]
        if pred is not None and pred.get("xoff") is not None:       # moved together with the element above it
            bases.append(pred["xoff"])
        if any(abs((ov - wv) - base) <= tol + EPS for _n, wv, ov in p["dx"] for base in bases):
            return
        name, wv, ov = min(p["dx"], key=lambda t: abs(t[2] - t[1]))
        prop = "x" if name == "left" else "x (%s)" % ("centre" if name == "center" else "right edge")
        why = "" if self.phone else self.x_on_purpose(p)
        if why:
            self.diff(p, prop, num(wv), num(ov), ov - wv, "intended", why)
            return
        self.diff(p, prop, num(wv), num(ov), ov - wv)

    def x_on_purpose(self, p):
        """Desktop: why the horizontal place of this pair differs from Wix on purpose, or "" when it does not.
        Only the build contract's decisions 4, 21 and 24 are known here, and each one only while our element is
        where the decision puts it: an element that is neither there nor where Wix has it stays a difference."""
        tol, w, o = self.tol, p["w"], p["o"]
        marks = o.get("marks", ())
        middle = lambda it: it["ax"]["center"] if it["kind"] == "text" else it["x"] + it["w"] / 2.0
        ours_off = middle(o) - self.ours["doc"].get("vw", 0) / 2.0
        wix_off = middle(w) - self.wix["doc"].get("vw", 0) / 2.0
        beside = "on Wix it sits %s px %s of the centre" % (num(abs(wix_off)), "right" if wix_off > 0 else "left")
        if p["k"] == "box" and ".hero-box" in marks:
            # Decision 4: our beige box is centred on the page, the Wix one sits a few px beside the centre.
            return "%s (%s)" % (DECISION_4, beside) if abs(ours_off) <= tol + EPS else ""
        if self.slug == "home" and p["region"] == "main" and any(m in marks for m in HOME_CENTRED):
            # Decision 21: site title, welcome paragraph, dotted rule, Book Online button and address line are centred.
            if abs(ours_off) <= tol + EPS and abs(wix_off) <= HOME_DRIFT + tol + EPS:
                return "%s (%s)" % (DECISION_21, beside)
            return ""
        if self.slug in POLICY_PAGES and p["k"] == "text" and ".legal" in marks:
            if anchor_of(o["align"]) == "center":       # a title
                if abs(ours_off) <= tol + EPS and abs(wix_off) <= POLICY_DRIFT + tol + EPS:
                    return "%s (%s)" % (DECISION_24, beside)
                return ""
            col = self.policy_column()
            if col is None or not self.policy_block(p):
                return ""
            off = w["ax"]["left"] - col["wix"]
            listed = (w["tag"] not in INLINE_TAGS and off > tol + EPS
                      and any(abs(w["x"] + w["w"] - end) <= tol + EPS for end in col["wix_ends"]))
            # listed: a Wix block that starts further right and ends where the paragraphs of the column end is an indented
            # list item, not a block that drifted (a block that drifts moves as a whole, with its right end). If our
            # page shows it at the text edge, the indent is missing, and that counts.
            if abs(o["ax"]["left"] - col["ours"]) <= tol + EPS and abs(off) <= POLICY_DRIFT + tol + EPS and not listed:
                return "%s (our text edge is at x %s; on Wix the edge is at x %s and this block sits %s px %s of it)" % (
                    DECISION_24, num(col["ours"]), num(col["wix"]), num(abs(off)), "right" if off > 0 else "left")
        return ""

    def policy_block(self, p):
        """A block of a policy page that belongs to the text column: left-aligned text in article.legal that is
        placed by the page (not a piece of a sentence) and is not a list item (those are indented on purpose)."""
        w, o = p["w"], p["o"]
        marks = o.get("marks", ())
        return (p["k"] == "text" and ".legal" in marks and "li" not in marks and not p.get("nopos") and not p.get("nox")
                and anchor_of(o["align"]) == "left" and anchor_of(w["align"]) == "left")

    def policy_column(self):
        """Decision 24: where the text column of a policy page starts on our page and on Wix (the middle value of
        all its blocks, so the blocks that drifted on Wix do not move it), and where the Wix column ends.
        -> {ours, wix, wix_ends}, or None when our column is not where the Wix column is: then nothing is intended."""
        if not hasattr(self, "_policy_column"):
            mid = lambda values: sorted(values)[len(values) // 2]
            blocks = [p for p in self.pairs if self.policy_block(p)]
            col = None
            if blocks:
                col = {"ours": mid([p["o"]["ax"]["left"] for p in blocks]), "wix": mid([p["w"]["ax"]["left"] for p in blocks])}
                # where the Wix column ends: the right ends of its paragraphs (a heading or a piece of text in a span is only as wide as its words)
                col["wix_ends"] = sorted({round(p["w"]["x"] + p["w"]["w"], 1) for p in blocks
                                          if p["w"]["tag"] == "p" and abs(p["w"]["ax"]["left"] - col["wix"]) <= self.tol + EPS})
                if abs(col["ours"] - col["wix"]) > self.tol + EPS:
                    col = None
            self._policy_column = col
        return self._policy_column

    def check_y(self, p, pred, inside_pred, header_delta, boxes):
        """Under a box, photo or button the gap is taken from its lower edge; under text from the centre of its last
        line, so text that wraps differently (font metrics) does not make everything under it count as moved."""
        tol, w, o = self.tol, p["w"], p["o"]

        def low(it):
            return it["ay"] + (it["lines"] - 1) * it["lh_px"] if it["kind"] == "text" else it["y"] + it["h"]
        root = 0.0 if p["region"] == "header" else header_delta
        if pred is None:
            cands = [root]
        else:
            cands = [pred["base_out"], pred["base_in"]]
            if not inside_pred:
                grew = (low(pred["o"]) - pred["o"]["ay"]) - (low(pred["w"]) - pred["w"]["ay"])
                if abs(grew) > EPS:
                    cands = [pred["base_out"] + grew, pred["base_in"] + grew] + cands
        around = [b for b in boxes if b is not p and "dy" in b and contains(b["w"], w, 3) and contains(b["o"], o, 3)]
        if around:              # the same place inside its coloured box, counted from its top or from its bottom
            b = min(around, key=lambda q: q["w"]["w"] * q["w"]["h"])
            cands += [b["dy"], b["dy"] + (b["o"]["h"] - b["w"]["h"])]
        cands.append(root)      # the same place on the page
        fonts = [it["fs"] for it in (o, pred["o"] if pred is not None else None) if it is not None and it["kind"] == "text"]
        tol += BASELINE_EM * max(fonts) if fonts else 0.0
        p["base_in"] = cands[0]
        hit = next((c for c in cands if abs(p["dy"] - c) <= tol + EPS), None)
        if hit is not None:
            p["base_out"] = hit
            return
        p["base_out"] = p["dy"]
        d = p["dy"] - cands[0]
        above = "the element above it ('%s')" % pred["label"] if pred is not None else ("the top of the page" if p["region"] == "header" else "the header")
        why, cls = "", "count"
        if pred is not None:
            lo, hi = pred["o"]["ay"], o["y"]
            for y0, y1, reason in self.blocks_ours:
                if d > 0 and lo - tol <= (y0 + y1) / 2.0 <= hi + tol:
                    cls, why = "intended", "pushed down by %s, which is not on the Wix page" % reason
            lo, hi = pred["w"]["ay"], w["y"]
            for y0, y1, reason in self.blocks_wix:
                if d < 0 and lo - tol <= (y0 + y1) / 2.0 <= hi + tol:
                    cls, why = "intended", "Wix has %s above it" % reason
        if cls == "count" and p["k"] == "box" and ".site-footer" in o.get("marks", ()) and d < -EMPTY_GAP * self.scale:
            # seen on the Wix phone version of the accessibility statement: about 1,300 px of nothing between the last
            # line and the footer. That is a fault of the Wix page, not a look to copy.
            cls, why = "intended", "the Wix page has an empty stretch of about %s px above its footer, our footer follows the content" % num(abs(d))
        note = "%s px %s than on Wix, measured from %s; on the page: Wix y %s, ours y %s" % (num(abs(d)), "lower" if d > 0 else "higher", above, num(w["ay"]), num(o["ay"]))
        self.diff(p, "y", num(w["ay"] + cands[0]), num(o["ay"]), d, cls, note if cls == "count" else why)

    # -- header, page background, page width -------------------------------------------------------------------

    def page_level(self):
        W, O = self.wix, self.ours
        hw, ho = W["header"], O["header"]
        self.page_fail = []
        if hw and ho:
            want = hw["box"]["h"] * self.scale
            got = ho["box"]["h"]
            if abs(got - want) > self.tol + EPS:
                if self.phone:      # the brief gives the phone header its own height: brief-phone-header judges it
                    self.page_info.append(("header: height", num(want), num(got), got - want))
                else:
                    self.page_fail.append(("header: height", "%s px" % num(want), "%s px" % num(got), abs(got - want)))
            if hw.get("position") != ho.get("position"):
                self.page_fail.append(("header: position", str(hw.get("position")), str(ho.get("position")), None))
            cw = colour(hw.get("bg"))
            if cw is None or cw[3] <= 0:
                inner = [b for b in W["allboxes"] if b["region"] == "header" and b["w"] >= hw["box"]["w"] * self.scale * 0.9]
                cw = inner[0]["bg"] if inner else W["page_bg"]
            co = colour(ho.get("bg"))
            if co is None or co[3] <= 0:
                co = O["page_bg"]
            if cw is not None and co is not None and not same_colour(cw, co):
                self.page_fail.append(("header: background", show_colour(cw), show_colour(co), None))
        elif hw and not ho:
            self.page_fail.append(("header", "a header element", "our page has no header element", None))
        if W["page_bg"] is not None and O["page_bg"] is not None and not same_colour(W["page_bg"], O["page_bg"]):
            self.page_fail.append(("page background", show_colour(W["page_bg"]), show_colour(O["page_bg"]), None))
        doc = O["doc"]
        if not self.phone and doc.get("w", 0) > doc.get("vw", 0) + 1:      # on the phone: the entry "fits the screen"
            self.page_fail.append(("page width", "as wide as the screen (%s px), like the Wix page" % num(doc.get("vw", 0)), "%s px wide, the page scrolls sideways" % num(doc.get("w", 0)), doc["w"] - doc["vw"]))

    # -- phone: the order of the blocks ------------------------------------------------------------------------

    def block_order(self):
        """Do the paired blocks of main and footer come in the same order, top to bottom, as on the Wix phone page?
        Two blocks are out of order when one is wholly above the other on Wix and wholly below it on our page, so
        two things that stand side by side on one of the pages never count. The smallest set of blocks that has to
        move is named (the block that is out of order with the most others first).
        -> (number of blocks looked at, the blocks that are out of place as {block, where, ...},
            the labels of the blocks left out because their order on Wix is an open question, see PHONE_ORDER_OPEN)"""
        slack = 1.0
        blocks, left_out = [], []
        open_from = None
        if self.slug in PHONE_ORDER_OPEN:
            start = text_key(PHONE_ORDER_OPEN[self.slug][0])
            first = [t["y"] for t in self.wix["text"] if t["region"] == "main" and t["key"].startswith(start)]
            open_from = first[0] - slack if first else None
        for p in self.pairs:
            if p["region"] == "header" or p.get("nopos"):
                continue        # the phone header is the brief's own; a piece of a sentence follows the wrapping
            w, o = p["w"], p["o"]
            if open_from is not None and p["region"] == "main" and w["y"] >= open_from:
                left_out.append(p["label"])
                continue
            blocks.append({"p": p, "w0": w["y"], "w1": w["y"] + w["h"], "o0": o["y"], "o1": o["y"] + o["h"],
                           "details": self.slug == "contact" and ".info" in o.get("marks", ())})

        def swapped(a, b):      # a above b on Wix, b above a on our page
            return a["w1"] <= b["w0"] + slack and b["o1"] <= a["o0"] + slack

        def clash(a, b):
            if a["details"] and b["details"]:
                return False    # decision 8: the order of the contact details among themselves is ours
            return swapped(a, b) or swapped(b, a)

        left = list(blocks)
        moved = []
        while True:
            against = {id(b): [c for c in left if c is not b and clash(b, c)] for b in left}
            worst = max(left, key=lambda b: (len(against[id(b)]), -(b["o1"] - b["o0"])), default=None)
            if worst is None or not against[id(worst)]:
                break
            others = sorted(against[id(worst)], key=lambda c: abs(c["w0"] - worst["w0"]))
            first = others[0]
            on_wix = "above" if worst["w1"] <= first["w0"] + slack else "below"
            # A photo is named after our file. Photos are paired by place and shape, not by what they show (ours are
            # placeholders), so the y of both blocks on both pages is given: that is what the finding rests on.
            moved.append({"block": worst["p"]["label"], "ours": worst["p"]["o"].get("sel", ""),
                          "where": "on Wix it is %s '%s' (Wix y %s and %s), on our page it is %s it (our y %s and %s)" % (
                              on_wix, first["p"]["label"], num(worst["w0"]), num(first["w0"]), "below" if on_wix == "above" else "above", num(worst["o0"]), num(first["o0"])),
                          "wix_y": round(worst["w0"], 1), "ours_y": round(worst["o0"], 1),
                          "out_of_order_with": [{"block": c["p"]["label"], "wix_y": round(c["w0"], 1), "ours_y": round(c["o0"], 1)} for c in others[:12]]})
            left = [b for b in left if b is not worst]
        return len(blocks), moved, left_out

    # -- report entries ----------------------------------------------------------------------------------------

    def entries(self):
        slug, vp = self.slug, self.vp
        out, seen = [], {}

        def name(check):
            n = seen.get(check, 0) + 1
            seen[check] = n
            return check if n == 1 else "%s (%d)" % (check, n)

        failed, ok_pairs, listed = [], 0, []
        as_written = "; phone: the Wix value as written, not enlarged (decision 16)" if self.phone else ""
        for p in self.pairs:
            counted = [d for d in p["diffs"] if d["cls"] == "count"]
            soft = [d for d in p["diffs"] if d["cls"] == "intended"]
            o, w = p["o"], p["w"]
            where = "ours: %s; Wix: %s in %s" % (o.get("sel", ""), w.get("tag", w["kind"]), w["region"])
            if p.get("how") == "fuzzy":
                where += "; matched although the text differs a little (Wix: '%s')" % short(w["text"], 40)
            if w.get("moved_from"):
                where += "; the Wix capture caught this photo while it moved (%s), its place in the row is used" % w["moved_from"]
            for d in p["diffs"]:
                if d["cls"] == "info":
                    listed.append({"element": p["label"], "ours": o.get("sel", ""), "property": d["prop"], "wix_scaled": d["wix"], "ours_value": d["ours"],
                                   "diff_px": None if d["d"] is None else round(d["d"], 1)})
            if counted:
                size = max([abs(d["d"]) for d in counted if d["d"] is not None] or [0.0])
                notes = "; ".join(d["why"] for d in counted if d["why"])
                failed.append(entry(slug, vp, name(p["label"]), False, ", ".join("%s %s" % (d["prop"], d["wix"]) for d in counted),
                                    ", ".join("%s %s" % (d["prop"], d["ours"]) for d in counted), (notes + "; " if notes else "") + where + as_written, "DESIGN",
                                    kind=p["k"], diff=round(size, 1),
                                    differences=[{"property": d["prop"], "wix": d["wix"], "ours": d["ours"], "diff_px": None if d["d"] is None else round(d["d"], 1)} for d in counted]))
            else:
                ok_pairs += 1
            if soft:
                out.append(entry(slug, vp, name("intended: %s" % p["label"]), True, ", ".join("%s %s" % (d["prop"], d["wix"]) for d in soft),
                                 ", ".join("%s %s" % (d["prop"], d["ours"]) for d in soft), "; ".join(sorted({d["why"] for d in soft if d["why"]})) + "; " + where, "DESIGN",
                                 kind="intended", intended=True, diff=round(max([abs(d["d"]) for d in soft if d["d"] is not None] or [0.0]), 1)))
        for f in self.fails:
            failed.append(entry(slug, vp, name(f["check"]), False, f["expected"], f["actual"], f["evidence"], f["owner"], kind="only-one-side", diff=round(f["d"], 1) if f["d"] is not None else 0.0))
        for check, exp, act, d in self.page_fail:
            failed.append(entry(slug, vp, name(check), False, exp, act, "the header element and the page as measured", "DESIGN", kind="page", diff=round(d, 1) if d is not None else 0.0))
        failed.sort(key=lambda e: -e["diff"])
        moved = []
        if self.phone:
            looked, moved, left_out = self.block_order()
            excepted = ("not part of the order: the phone header, the home photo row, the extra Hours block, the closing booking note, the copyright line, "
                        "pieces of a sentence, and the contact details among themselves (%s)" % DECISION_8)
            if left_out:
                out.append(entry(slug, vp, name("block order: open question"), True, PHONE_ORDER_OPEN[slug][1],
                                 "%d blocks keep their place on our page and are left out of the entry 'block order': %s" % (len(left_out), "; ".join(left_out[:12])),
                                 "an open question for the owner: copy the order of the Wix phone page here, or keep ours. Not judged until she decides", "DESIGN",
                                 kind="open-question", intended=True, diff=0.0, details=left_out))
            order = entry(slug, vp, name("block order"), not moved, "the %d paired blocks of main and footer come in the same order, top to bottom, as on the Wix phone page" % looked,
                          ("%d of %d blocks are out of place: %s" % (len(moved), looked, "; ".join("'%s': %s" % (m["block"], m["where"]) for m in moved[:6]))) if moved else "same order",
                          "two blocks are out of order when one is wholly above the other on Wix and wholly below it on our page; " + excepted, "DESIGN",
                          kind="order", diff=float(len(moved)), details=moved)
            if moved:
                failed.insert(0, order)
            else:
                out.append(order)
            for label, wv, ov, d in self.page_info:
                listed.append({"element": label, "ours": "header.site-header", "property": "h", "wix_scaled": wv, "ours_value": ov, "diff_px": round(d, 1)})
            listed.sort(key=lambda x: -abs(x["diff_px"] or 0.0))
            elements = len({(x["element"], x["ours"]) for x in listed})
            out.append(entry(slug, vp, name("sizes and places (information)"), True,
                             "listed only: on the phone a place or a size is not pass or fail (decision 16). Wix lengths are multiplied by 390 / 320, the size they have on a 390 px screen",
                             ("%d differences of more than %s px on %d elements, biggest first: %s" % (
                                 len(listed), num(self.tol), elements,
                                 "; ".join("%s %s: Wix %s, ours %s" % (x["element"], x["property"], x["wix_scaled"], x["ours_value"]) for x in listed[:8]))) if listed else "no difference of more than %s px" % num(self.tol),
                             "judged instead: the entries 'block order' and 'fits the screen' of this page, and the phone lines of the brief", "DESIGN",
                             kind="phone-sizes", diff=round(abs(listed[0]["diff_px"] or 0.0), 1) if listed else 0.0, details=listed))
        for label, exp, act, ev in self.intended:
            out.append(entry(slug, vp, name("intended: " + label), True, exp, act, ev, "DESIGN", kind="intended", intended=True, diff=0.0))
        if self.font_metrics:
            fm = sorted(self.font_metrics, key=lambda f: -f["size"])
            top = "; ".join("'%s' %s" % (f["text"], ", ".join("%s %s -> %s" % (k, num(v[0]), num(v[1])) for k, v in f.items() if k in ("lines", "height", "width"))) for f in fm[:6])
            out.append(entry(slug, vp, "font metrics", True, "Didot and Proxima Nova (Wix)", "Bodoni Moda and Figtree: %d texts differ in width or in wrapped height" % len(fm),
                             "biggest first: " + top, "DESIGN", kind="font-metrics", diff=round(fm[0]["size"], 1),
                             details=[{k: (list(v) if isinstance(v, tuple) else v) for k, v in f.items() if k != "size"} for f in fm]))
        if self.unpaired:
            only_w, only_o = [u for u in self.unpaired if u["side"] == "wix"], [u for u in self.unpaired if u["side"] == "ours"]
            out.append(entry(slug, vp, "text without a partner", True, "every text of one page is found on the other",
                             "%d only on Wix, %d only on our page: not compared here (the wording is the business of the content check)" % (len(only_w), len(only_o)),
                             "; ".join("%s: '%s'" % ("Wix" if u["side"] == "wix" else "ours", short(u["text"], 50)) for u in self.unpaired[:8]), "CONTENT",
                             kind="text-not-paired", diff=0.0, details=self.unpaired))
        c = self.counts
        dw, do = self.wix["doc"], self.ours["doc"]
        differ = sum(1 for p in self.pairs if any(d["cls"] == "count" for d in p["diffs"]))
        intended = sum(1 for e in out if e.get("kind") == "intended")
        summary = ("%d pairs compared (%d text, %d images, %d other): %d match, %d differ. %d things on one side only. "
                   "%d intended entries. Page height: Wix %s px, ours %s px."
                   % (len(self.pairs), sum(1 for p in self.pairs if p["k"] == "text"), sum(1 for p in self.pairs if p["k"] == "image"),
                      sum(1 for p in self.pairs if p["k"] not in ("text", "image")), ok_pairs, differ, len(self.fails),
                      intended, num(dw.get("h", 0) * self.scale), num(do.get("h", 0))))
        if self.phone:
            summary += " Phone: %d places and sizes listed as information, %d blocks out of order." % (len(listed), len(moved))
        if c.get("text_part_ours") or c.get("text_part_wix"):
            summary += " %d text pieces are part of a longer text on the other side and were not compared alone." % (c.get("text_part_ours", 0) + c.get("text_part_wix", 0))
        self.summary = {"pairs": len(self.pairs), "match": ok_pairs, "differ": len(failed), "one_side_only": len(self.fails),
                        "page_height_wix": round(dw.get("h", 0) * self.scale, 1), "page_height_ours": do.get("h", 0), "notes": sorted(set(self.notes))[:12]}
        if self.phone:
            self.summary.update(listed_sizes=len(listed), blocks_out_of_order=len(moved))
        self.summary_text = summary
        return failed, out


def shot_underlined(img, box, fg):
    """Is the one-line text in this box of the screenshot underlined? Looks under the baseline for a row that is
    nearly all text colour. -> True, False, or None when it cannot be told."""
    try:
        if fg is None:
            return None
        top = int(box["y"])
        x0, x1 = int(box["x"] + 1), int(box["x"] + box["w"] - 1)
        y0, y1 = int(box["y"] + 0.8 * box["h"]), int(math.ceil(box["y"] + box["h"] + 1))
        if x1 - x0 < 12 or x0 < 0 or top < 0 or x1 > img.width or y1 >= img.height:
            return None
        region = img.crop((x0, top, x1, y1 + 1))
        colours = region.getcolors(maxcolors=region.width * region.height)
        bg = max(colours)[1]
        den = float(sum((fg[i] - bg[i]) ** 2 for i in range(3)))
        if den < 600:
            return None
        pix, rows = region.load(), []
        for yy in range(y0 - top, region.height):
            t = 0.0
            for xx in range(region.width):
                c = pix[xx, yy]
                t += min(1.0, max(0.0, sum((c[i] - bg[i]) * (fg[i] - bg[i]) for i in range(3)) / den))
            rows.append(t / region.width)
        best = max((rows[i] + (rows[i + 1] if i + 1 < len(rows) else 0.0)) for i in range(len(rows))) if rows else 0.0
        return best >= 0.7
    except Exception:
        return None


# ---------------------------------------------------------------------------------------------------------------
# Measuring our pages, screenshots, side-by-side images
# ---------------------------------------------------------------------------------------------------------------

def load_reference(slug, ref):
    """The Wix measurement of one page. ref is "desktop" (1280 px), "phone", or "w1265", "w1440", "w1920"."""
    path = os.path.join(common.WIX_REF, "measure-%s-%s.json" % (slug, ref))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def reference_text(slug):
    try:
        with open(os.path.join(common.WIX_REF, slug + ".json"), encoding="utf-8") as f:
            return json.load(f).get("text") or ""
    except Exception:
        return ""


def reference_shot(slug, ref):
    return os.path.join(common.WIX_REF, "shots", "%s-%s-full.png" % (slug, ref))


def side_by_side(ours_png, wix_png, slug, vp):
    """Our full-page screenshot next to the Wix reference, both at the same width. Written to the private folder only."""
    from PIL import Image, ImageDraw
    target = private_file(SIDE_DIR, "%s-%s.png" % (slug, vp))
    a, b = Image.open(ours_png).convert("RGB"), Image.open(wix_png).convert("RGB")
    width = a.width
    if b.width != width:
        b = b.resize((width, max(1, int(round(b.height * width / float(b.width))))), Image.LANCZOS)
    gap, bar = 24, 28
    sheet = Image.new("RGB", (width * 2 + gap, max(a.height, b.height) + bar), (120, 120, 120))
    sheet.paste(a, (0, bar)); sheet.paste(b, (width + gap, bar))
    draw = ImageDraw.Draw(sheet)
    draw.rectangle((0, 0, sheet.width, bar - 1), fill=(40, 40, 40))
    draw.text((8, 8), "OURS  %s  %s  %d x %d" % (slug, vp, a.width, a.height), fill=(255, 255, 255))
    draw.text((width + gap + 8, 8), "WIX reference, scaled to the same width (shows Wix-only photos, never copy into the site)", fill=(255, 255, 255))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    sheet.save(target)
    return target


# ---------------------------------------------------------------------------------------------------------------
# The brief's measurement list, tested on our own pages. No Wix reference is needed for these entries.
# ---------------------------------------------------------------------------------------------------------------

def first_family(value):
    return str(value or "").split(",")[0].strip().strip("\"'")


def visible_edge(e):
    """One side of a border as (thickness, style, colour), or None when nothing shows."""
    if not e or (e.get("w") or 0) <= 0 or e.get("style") in ("none", "hidden", None):
        return None
    col = colour(e.get("color"))
    if col is not None and col[3] <= 0:
        return None
    return (e["w"], e["style"], col)


def rule_of(item):
    """The line an element shows: its own top or bottom border, else one drawn by ::before or ::after.
    -> ((thickness, style, colour), width of the line) or None"""
    for side in ("top", "bottom"):
        e = visible_edge(item.get(side))
        if e:
            return e, item["box"]["w"]
    for which in ("before", "after"):
        ps = item.get(which) or {}
        for side in ("top", "bottom"):
            e = visible_edge(ps.get(side))
            if e:
                return e, ps.get("w") or item["box"]["w"]
    return None


def is_underlined(item):
    """An underline as the visitor sees it: a text decoration, or a line drawn under the element."""
    if "underline" in str(item.get("deco") or ""):
        return True
    if visible_edge(item.get("bottom")):
        return True
    return any(visible_edge((item.get(which) or {}).get(side)) for which in ("before", "after") for side in ("top", "bottom"))


def face_rules(faces, family, italic, wght):
    """The @font-face rules of the page (fontFaces of the measurement) that draw this family, slant and weight.
    A rule names one weight ("400") or a range ("400 700")."""
    out = []
    for f in faces or []:
        if f.get("family") != family or (str(f.get("style", "")).split()[:1] == ["italic"]) != italic:
            continue
        try:
            marks = [float(x) for x in str(f.get("weight", "400")).replace("normal", "400").replace("bold", "700").split()]
        except ValueError:
            continue
        if marks and min(marks) <= wght <= max(marks):
            out.append(f)
    return out


class BriefLine:
    """One line of the brief's list on one page: every value the line names, next to what our page shows."""

    def __init__(self, slug, vp, name, line, where):
        self.slug, self.vp, self.name, self.line, self.where = slug, vp, name, line, where
        self.parts, self.owner = [], "DESIGN"

    def add(self, what, want, got, ok, d=None):
        self.parts.append({"what": what, "brief": want, "ours": got, "ok": bool(ok), "diff_px": None if d is None else round(d, 1)})
        return bool(ok)

    def px(self, what, got, want, tol=BRIEF_TOL):
        """One length or font size, within the tolerance of the brief."""
        return self.each(what, [got], want, tol)

    def each(self, what, values, want, tol=BRIEF_TOL):
        """The same length on several elements: every one has to be within the tolerance."""
        if not values:
            return True
        if any(v is None for v in values):
            return self.add(what, "%s px" % num(want), "could not be measured", False)
        worst = max(values, key=lambda v: abs(v - want))
        distinct = sorted({round(v, 1) for v in values})
        shown = ", ".join(num(v) for v in distinct[:6]) + " px" + (" (%d elements)" % len(values) if len(values) > 1 else "")
        return self.add(what, "%s px" % num(want), shown, abs(worst - want) <= tol + EPS, worst - want)

    def colour(self, what, values, want):
        """A colour, on one element or on several."""
        found = [colour(v) for v in values]
        if not found:
            return True
        ok = all(c is not None and c[:3] == want and c[3] >= 0.95 for c in found)
        distinct = []
        for c in found:
            if show_colour(c) not in distinct:
                distinct.append(show_colour(c))
        return self.add(what, show_colour(want + (1.0,)), ", ".join(distinct[:4]), ok)

    def font(self, what, items, size=None, italic=None, wght=None, family=None):
        if size is not None:
            self.each(what + " font size", [i.get("size") for i in items], size)
        if italic:
            styles = sorted({str(i.get("style")) for i in items})
            self.add(what + " style", "italic", ", ".join(styles), all(s in ("italic", "oblique") for s in styles))
        if wght is not None:
            weights = sorted({weight(i.get("weight")) for i in items})
            self.add(what + " weight", str(wght), ", ".join(str(x) for x in weights), weights == [wght])
        if family:
            fams = sorted({first_family(i.get("family")) for i in items})
            self.add(what + " font", family, ", ".join(fams), fams == [family])

    def entry(self, tol_note):
        bad = [p for p in self.parts if not p["ok"]]
        if bad:
            actual = "%d of %d values differ: %s" % (len(bad), len(self.parts), "; ".join("%s is %s (the brief: %s)" % (p["what"], p["ours"], p["brief"]) for p in bad[:8]))
        else:
            actual = "all %d values match: %s" % (len(self.parts), "; ".join("%s %s" % (p["what"], p["ours"]) for p in self.parts[:14]))
        size = max([abs(p["diff_px"]) for p in bad if p["diff_px"] is not None] or [0.0])
        return entry(self.slug, self.vp, "brief-" + self.name, not bad, self.line, actual, "ours: %s; %s" % (self.where, tol_note),
                     self.owner if bad else "DESIGN", kind="brief", diff=round(size, 1), values=self.parts)


def brief_checks(slug, view, m):
    """The lines of the brief's measurement list that apply to this page in this viewport, as report entries.
    m is what BRIEF_JS measured on our page. Desktop: the list as taken at 1265 px (decision 1), with decision 3
    (a 1 px line where the brief says 0.8 px, service card text 16 px) and decision 4 (the beige box centred).
    Where the brief calls a text "centered" its alignment is tested; where the block of text sits is judged by the
    comparison with the Wix reference at the same width. Phone: the phone line of the list."""
    items = m.get("items") or {}
    selectors = dict(BRIEF_SPEC)
    vw = float(m.get("vw") or view.width)
    tol_note = "measured on our page at %s, lengths and font sizes within %s px" % (view.size(), num(BRIEF_TOL))
    lines = []

    def line(name, text, keys):
        b = BriefLine(slug, view.name, name, text, ", ".join(selectors[k] for k in keys))
        lines.append(b)
        return b

    def got(b, key, what):
        """The visible elements of one selector. When there is none the line gets a failed value that says so."""
        found = items.get(key) or []
        if not found:
            b.owner = "PAGES"
            b.add(what, "on the page", "no element matches %s" % selectors[key], False)
            return []
        seen = [i for i in found if i.get("shown")]
        if not seen:
            b.add(what, "shown", "%s is on the page but not shown" % selectors[key], False)
        return seen

    def line_height(b, what, its, want):
        values = [px(i.get("lh")) for i in its]
        if any(v is None for v in values):
            b.add(what, "%s px" % num(want), ", ".join(sorted({str(i.get("lh")) for i in its})), False)
        else:
            b.each(what, values, want)

    def centred(b, what, box):
        b.add(what, "centred (centre at x %s)" % num(vw / 2.0), "centre at x %s" % num(box["x"] + box["w"] / 2.0),
              abs(box["x"] + box["w"] / 2.0 - vw / 2.0) <= BRIEF_TOL + EPS, box["x"] + box["w"] / 2.0 - vw / 2.0)

    def aligned(b, what, its):
        found = sorted({align_name(i.get("align")) for i in its})
        b.add(what + " alignment", "center", ", ".join(found), found == ["center"])

    spacing_tol = lambda size: max(SPACING_TOL, SPACING_EM * size)

    if view.kind == "phone":
        b = line("phone-header", "Phone header 96 px with an 80 px logo and a menu button", ("header", "logo", "menu_btn"))
        hd = got(b, "header", "header")
        if hd:
            b.px("header height", hd[0]["box"]["h"], 96)
        lg = got(b, "logo", "logo")
        if lg:
            bx = lg[0]["box"]
            near, far = sorted((bx["w"], bx["h"]), key=lambda v: abs(v - 80))
            b.add("logo", "80 px", "%s x %s px" % (num(bx["w"]), num(bx["h"])), abs(near - 80) <= BRIEF_TOL + EPS and abs(far - 80) <= 2 * BRIEF_TOL + EPS, near - 80)
        mb = got(b, "menu_btn", "menu button")
        if mb:
            b.add("menu button", "shown", "shown, %s x %s px" % (num(mb[0]["box"]["w"]), num(mb[0]["box"]["h"])), True)
        if slug == "home":
            b = line("phone-address-hours", "Phone address and hours line 14 px", ("addr", "hours"))
            ad = got(b, "addr", "address line")
            if ad:
                b.px("address line font size", ad[0].get("size"), 14)
            hr = got(b, "hours", "hours line")
            if hr:
                b.each("hours line font size", [i.get("size") for i in hr], 14)
        return [b.entry(tol_note) for b in lines]

    # ---- every page: header, navigation, footer, fonts
    b = line("header", "Header: sticky, 159 px tall, page background #fefefd, nav at x 24 y 24, logo 134 x 138 centered at top 14", ("header", "nav_links", "logo"))
    hd = got(b, "header", "header")
    if hd:
        h = hd[0]
        b.add("header position", "sticky", str(h.get("position")), h.get("position") == "sticky")
        stuck = m.get("stuck")
        if stuck:
            b.add("header after scrolling %s px down" % num(stuck["scrolled"]), "still at the top of the window", "its top is at %s px" % num(stuck["top"]), abs(stuck["top"]) <= 1.0, stuck["top"])
        b.px("header height", h["box"]["h"], 159)
        page_bg = colour(m.get("bodyBg"))
        if page_bg is None or page_bg[3] <= 0:
            page_bg = colour(m.get("htmlBg"))
        b.add("page background", "#fefefd", show_colour(page_bg) if page_bg is not None and page_bg[3] > 0 else "none set", page_bg is not None and page_bg[:3] == PAPER and page_bg[3] >= 0.95)
        head_bg = colour(h.get("bg"))
        if head_bg is not None and head_bg[3] > 0:
            b.add("header background", "#fefefd", show_colour(head_bg), head_bg[:3] == PAPER and head_bg[3] >= 0.95)
    links = got(b, "nav_links", "navigation")
    if links and links[0].get("letters"):
        L = links[0]["letters"]
        b.px("nav text starts at x", L["x"], 24)
        # 24 is the top of the line of text on Wix (a 17 px line, so its centre is at 32.5). A font with a taller line
        # box starts a little higher with its letters at the same height, so either reading passes.
        d_top, d_mid = L["y"] - 24.0, L["c1"] - 32.5
        d = d_top if abs(d_top) <= abs(d_mid) else d_mid
        b.add("nav text at y", "24 px (top of the line, its centre at 32.5)", "%s px (centre at %s)" % (num(L["y"]), num(L["c1"])), abs(d) <= BRIEF_TOL + EPS, d)
    lg = got(b, "logo", "logo")
    if lg:
        bx = lg[0]["box"]
        b.px("logo width", bx["w"], 134)
        b.px("logo height", bx["h"], 138)
        b.px("logo top", bx["y"], 14)
        centred(b, "logo", bx)

    b = line("nav-text", "Nav text 16 px, letter-spacing 0.8 px, color #1d1509, current page underlined", ("nav_links",))
    links = got(b, "nav_links", "navigation links")
    if links:
        b.each("font size", [i.get("size") for i in links], 16)
        b.each("letter spacing", [px(i.get("ls"), 0.0) for i in links], 0.8, spacing_tol(16))
        b.colour("colour", [i.get("color") for i in links], INK)
        current = [i for i in links if i.get("current") == "page"]
        if slug in NAV_CURRENT:
            if not current:
                b.owner = "PAGES"
                b.add("current page", "the link '%s' is marked aria-current=\"page\"" % NAV_CURRENT[slug], "no link is marked", False)
            else:
                b.add("current page link '%s'" % current[0].get("text", ""), "underlined", "underlined" if is_underlined(current[0]) else "not underlined", is_underlined(current[0]))
        others = [i.get("text", "") for i in links if i.get("current") != "page" and is_underlined(i)]
        b.add("the other links", "not underlined", ("underlined: " + ", ".join(others)) if others else "not underlined", not others)

    b = line("footer", "Footer: background #1d1509, text #fefefd 14 px, dotted rule on top, name 27 px italic bold, role 19 px italic bold, three columns starting at x 30, 397 and 889",
             ("footer", "foot_text", "foot_rule", "foot_name", "foot_role", "foot_brand", "foot_contact", "foot_links"))
    ft = got(b, "footer", "footer")
    if ft:
        b.colour("background", [ft[0].get("bg")], INK)
    tx = got(b, "foot_text", "footer text")
    if tx:
        b.each("text font size", [i.get("size") for i in tx], 14)
        b.colour("text colour", [i.get("color") for i in tx], PAPER)
    fr = got(b, "foot_rule", "rule on top")
    if fr:
        rule = rule_of(fr[0])
        b.add("rule on top", "dotted", rule[0][1] if rule else "no line shows", bool(rule) and rule[0][1] == "dotted")
        cols = [i for i in items.get("foot_cols") or [] if i.get("shown")]
        if cols:
            b.add("rule and columns", "the rule is above the columns", "rule at y %s, columns from y %s" % (num(fr[0]["box"]["y"]), num(cols[0]["box"]["y"])), fr[0]["box"]["y"] <= cols[0]["box"]["y"] + 1.0)
    for key, what, size in (("foot_name", "name", 27), ("foot_role", "role", 19)):
        g = got(b, key, what)
        if g:
            b.font(what, g[:1], size=size, italic=True, wght=700)
    for n, (key, want) in enumerate((("foot_brand", 30), ("foot_contact", 397), ("foot_links", 889))):
        g = got(b, key, "column %d" % (n + 1))
        if g:
            b.px("column %d starts at x" % (n + 1), (g[0].get("letters") or {}).get("x"), want)

    # The brief asked for Google Fonts. Since 9 November 2026 the same two fonts are files of the site itself (build
    # contract, decision 38): the page must have an @font-face rule for each of the four faces, each with font-display
    # swap and a file of the site's own folder fonts, and no link to Google Fonts.
    b = line("fonts", "Fonts: Bodoni Moda (italic 400 and 700) and Figtree (400 and 700), loaded with font-display swap from the "
                      "site's own folder fonts (the brief named Google Fonts, decision 38 moved the files into the site)", ())
    b.where = "the @font-face rules of css/style.css, body, .serif"
    faces, old_links = m.get("fontFaces") or [], m.get("fontLinks") or []
    rules_ok = [b.add("link to Google Fonts", "none", ", ".join(short(h, 80) for h in old_links) or "none", not old_links)]
    for fam, italic, wght in ((SERIF, True, 400), (SERIF, True, 700), (SANS, False, 400), (SANS, False, 700)):
        what = "%s %s%d" % (fam, "italic " if italic else "", wght)
        mine = face_rules(faces, fam, italic, wght)
        rules_ok.append(b.add(what, "an @font-face rule", "%d rules" % len(mine) if mine else "no such rule", bool(mine)))
        if mine:
            shown = sorted({f.get("display") or "not set" for f in mine})
            rules_ok.append(b.add(what + " display", "swap", ", ".join(shown), shown == ["swap"]))
            away = sorted({f.get("src") or "no file" for f in mine if not f.get("own")})
            rules_ok.append(b.add(what + " file", "a file of the site's own folder fonts", ", ".join(short(a, 80) for a in away) or "own files", not away))
    if not all(rules_ok):
        b.owner = "DESIGN"
    b.add("body text font", SANS, first_family(m.get("bodyFamily")), first_family(m.get("bodyFamily")) == SANS)
    serifs = sorted({first_family(f) for f in m.get("serifFamilies") or []})
    if serifs:
        b.add("font of the serif texts", SERIF, ", ".join(serifs), serifs == [SERIF])

    if slug == "home":
        b = line("site-title", "Site title \"Hair & Makeup by Gerta\": Didot italic bold 25 px, centered, 30 px line height (Bodoni Moda stands in for Didot)", ("site_title",))
        g = got(b, "site_title", "site title")
        if g:
            b.font("site title", g[:1], size=25, italic=True, wght=700, family=SERIF)
            aligned(b, "site title", g[:1])
            line_height(b, "site title line height", g[:1], 30)

        b = line("beige-box", "Beige box: 778 x 406 px, background #e8e1da, centered (decision 4)", ("hero_box",))
        g = got(b, "hero_box", "beige box")
        if g:
            b.px("width", g[0]["box"]["w"], 778)
            b.px("height", g[0]["box"]["h"], 406)
            b.colour("background", [g[0].get("bg")], BEIGE)
            centred(b, "box", g[0]["box"])

        b = line("hero-heading", "Hero heading \"It's Your Day to Shine!\": 32 px italic bold serif, centered", ("hero_h",))
        g = got(b, "hero_h", "hero heading")
        if g:
            b.font("heading", g[:1], size=32, italic=True, wght=700, family=SERIF)
            aligned(b, "heading", g[:1])

        b = line("dotted-rule", "Dotted rule: 485 px wide, 1 px dotted #1d1509 (the brief's 0.8 px is a 1 px line, decision 3)", ("dots",))
        g = got(b, "dots", "dotted rule")
        if g:
            rule = rule_of(g[0])
            if not rule:
                b.add("line", "1 px dotted #1d1509", "no line shows", False)
            else:
                (thick, style, col), width = rule
                b.px("width", width, 485)
                b.each("thickness", [thick], 1, BORDER_TOL)
                b.add("style", "dotted", style, style == "dotted")
                b.add("colour", "#1d1509", show_colour(col), col is not None and col[:3] == INK and col[3] >= 0.95)

        b = line("welcome", "Welcome paragraph: 16 px, 360 px wide, centered, 22.4 px line height", ("welcome",))
        g = got(b, "welcome", "welcome paragraph")
        if g:
            b.px("font size", g[0].get("size"), 16)
            b.px("width", g[0]["box"]["w"], 360)
            aligned(b, "text", g[:1])
            line_height(b, "line height", g[:1], 22.4)

        b = line("book-button", "Book Online button: 180 x 37 px, background #554f46, text #fefefd 14 px, letter-spacing 1.4 px, square corners", ("btn",))
        g = got(b, "btn", "Book Online button")
        if g:
            t = g[0]
            b.px("width", t["box"]["w"], 180)
            b.px("height", t["box"]["h"], 37)
            b.colour("background", [t.get("bg")], BUTTON)
            b.colour("text colour", [t.get("color")], PAPER)
            b.px("font size", t.get("size"), 14)
            b.each("letter spacing", [px(t.get("ls"), 0.0)], 1.4, spacing_tol(14))
            corner = max([px(str(r).split()[0], 0.0) or 0.0 for r in t.get("radius") or ["0px"]] + [0.0])
            b.add("corners", "square", "square" if corner <= 0.5 else "rounded, %s px" % num(corner), corner <= 0.5)

        b = line("contact-lines", "Phone 22 px, salon name 20 px bold, address 18 px underlined with a pin emoji, hours line 18 px scrolling", ("phone", "salon", "addr", "hours"))
        g = got(b, "phone", "phone")
        if g:
            b.px("phone font size", g[0].get("size"), 22)
        g = got(b, "salon", "salon name")
        if g:
            b.font("salon name", g[:1], size=20, wght=700)
        g = got(b, "addr", "address")
        if g:
            b.px("address font size", g[0].get("size"), 18)
            b.add("address", "underlined", "underlined" if is_underlined(g[0]) else "not underlined", is_underlined(g[0]))
            pin = "\U0001F4CD" in (g[0].get("text") or "") or any("\U0001F4CD" in (i.get("text") or "") for i in items.get("pin") or [])
            b.add("pin emoji", "at the start of the address", "there" if pin else "missing", pin)
        g = got(b, "hours", "hours line")
        if g:
            b.each("hours line font size", [i.get("size") for i in g], 18)
            mq = m.get("marquee") or {}
            moving = abs(mq.get("moved") or 0.0) >= 0.5 or (mq.get("running") or 0) > 0
            b.add("hours line", "scrolling", ("moved %s px in 0.4 s" % num(abs(mq.get("moved") or 0.0))) if moving else "does not move", moving)

        b = line("photo-row", "Home photo row: 4 images 288 x 545 px, gap about 20 px, total width 1213 px", ("row",))
        g = got(b, "row", "photo row")
        if g:
            row = sorted((i["box"] for i in g), key=lambda r: r["x"])
            b.add("number of images", "4", str(len(row)), len(row) == 4)
            b.each("image width", [r["w"] for r in row], 288)
            b.each("image height", [r["h"] for r in row], 545)
            b.each("gap between two images", [n["x"] - (r["x"] + r["w"]) for r, n in zip(row, row[1:])], 20)
            b.px("total width", row[-1]["x"] + row[-1]["w"] - row[0]["x"], 1213)
            b.each("top of the images (one row)", [r["y"] for r in row], row[0]["y"])

        b = line("meet-gerta", "Meet Gerta: heading 28 px italic bold, paragraphs 18 px with 25.2 px line height, portrait photo 313 x 422, large photo 424 x 637", ("meet_h", "meet_p", "meet_p1", "meet_p2"))
        g = got(b, "meet_h", "heading")
        if g:
            b.font("heading", g[:1], size=28, italic=True, wght=700)
        g = got(b, "meet_p", "paragraphs")
        if g:
            b.each("paragraph font size", [i.get("size") for i in g], 18)
            line_height(b, "paragraph line height", g, 25.2)
        for key, what, w_, h_ in (("meet_p1", "portrait photo", 313, 422), ("meet_p2", "large photo", 424, 637)):
            g = got(b, key, what)
            if g:
                b.px(what + " width", g[0]["box"]["w"], w_)
                b.px(what + " height", g[0]["box"]["h"], h_)

    if slug == "gallery":
        b = line("gallery", "Gallery title 57 px italic serif weight 400, masonry of 3 columns", ("gallery_title", "gallery_imgs"))
        g = got(b, "gallery_title", "title")
        if g:
            b.font("title", g[:1], size=57, italic=True, wght=400, family=SERIF)
        g = got(b, "gallery_imgs", "gallery photos")
        if g:
            columns = []
            for x in sorted(i["box"]["x"] for i in g):
                if not columns or x - columns[-1] > BRIEF_TOL:
                    columns.append(x)
            b.add("masonry", "3 columns", "%d columns, at x %s (%d photos)" % (len(columns), ", ".join(num(c) for c in columns[:8]), len(g)), len(columns) == 3)

    if slug == "book-online":
        # Desktop only (this function returns earlier for the phone). Decision 25: the 16 px applies from 761 px up, on
        # phones the cards have the Wix phone sizes as written, and those are judged by the comparison with the Wix phone page.
        b = line("service-cards", "Service cards: 290 px wide, image 290 x 195, title 24 px italic serif, body 16 px (decision 3; the brief's 14 px is within 2 px of it), "
                 "pill button with 1 px #554f46 border (decision 3) and 100 px radius", ("cards", "card_imgs", "card_titles", "card_body", "pills"))
        g = got(b, "cards", "cards")
        if g:
            b.each("card width", [i["box"]["w"] for i in g], 290)
        g = got(b, "card_imgs", "card images")
        if g:
            b.each("image width", [i["box"]["w"] for i in g], 290)
            b.each("image height", [i["box"]["h"] for i in g], 195)
        g = got(b, "card_titles", "card titles")
        if g:
            b.font("title", g, size=24, italic=True, family=SERIF)
        g = got(b, "card_body", "card text")
        if g:
            b.each("body font size (description, duration, price, Book Now)", [i.get("size") for i in g], 16)
        g = got(b, "pills", "pill buttons")
        if g:
            edges = [visible_edge(i.get("top")) for i in g]
            if not all(edges):
                b.add("pill border", "1 px #554f46", "%d of %d pills show no border" % (sum(1 for e in edges if not e), len(g)), False)
            else:
                b.each("pill border thickness", [e[0] for e in edges], 1, BORDER_TOL)
                b.add("pill border colour", "#554f46", ", ".join(sorted({show_colour(e[2]) for e in edges})), all(e[2] is not None and e[2][:3] == BUTTON for e in edges))
            radii = [px(str((i.get("radius") or ["0px"])[0]).split()[0], 0.0) or 0.0 for i in g]
            pill = [abs(r - 100) <= BRIEF_TOL + EPS or (r > 0 and r >= min(i["box"]["w"], i["box"]["h"]) / 2.0 - 0.5) for r, i in zip(radii, g)]
            b.add("pill radius", "100 px (a fully round end)", ", ".join(num(r) for r in sorted(set(radii))[:4]) + " px", all(pill))

    if slug == "contact":
        b = line("contact", "Contact: kicker \"Let's Connect\" 20 px italic bold, title 56 px italic weight 400, form labels 14 px, map 400 px tall", ("kicker", "contact_h1", "labels", "map"))
        g = got(b, "kicker", "kicker")
        if g:
            b.font("kicker", g[:1], size=20, italic=True, wght=700)
        g = got(b, "contact_h1", "title")
        if g:
            b.font("title", g[:1], size=56, italic=True, wght=400)
        g = got(b, "labels", "form labels")
        if g:
            b.each("form label font size", [i.get("size") for i in g], 14)
        g = got(b, "map", "map")
        if g:
            b.px("map height", g[0]["box"]["h"], 400)

    return [b.entry(tol_note) for b in lines]


def breakpoints_entry(view, m):
    """The breakpoint line of the brief, read from our stylesheet as the browser parsed it. One entry for the site."""
    media = m.get("media") or []
    widths = sorted({int(float(x)) for t in media for x in re.findall(r"(?:max|min)-width:\s*([\d.]+)px", t)})
    have = {w: any(re.search(r"max-width:\s*%d(?:\.0+)?px" % w, t) for t in media) for w in (1100, 760)}
    # Decision 32: the gallery gets a fourth column "from about 1600 px wide". That one min-width rule is allowed.
    wide = sorted({int(float(x)) for t in media for x in re.findall(r"min-width:\s*([\d.]+)px", t) if WIDE_GALLERY[0] <= float(x) <= WIDE_GALLERY[1]})
    other = [w for w in widths if w not in (1100, 1101, 760, 761) and w not in wide]
    if not m.get("sheet"):
        ok, actual, owner = False, "css/style.css is not among the stylesheets of the page", "PAGES"
    else:
        ok = all(have.values()) and not other
        actual = "max-width 1100 px: %s; max-width 760 px: %s%s" % ("found" if have[1100] else "missing", "found" if have[760] else "missing",
                                                                 ("; other widths in media rules: %s px" % ", ".join(str(w) for w in other)) if other else "")
        if wide:
            actual += "; also min-width %s px, the fourth gallery column of decision 32 (allowed)" % ", ".join(str(w) for w in wide)
        owner = "DESIGN"
    return entry(common.SITE_PAGE, view.name, "brief-breakpoints", ok, "Breakpoints 1100 px and 760 px", actual,
                 "the media rules of css/style.css as the browser read them (%d rules). The phone header of the same line of the brief is tested on the phone: brief-phone-header" % len(media),
                 owner, kind="brief", diff=0.0)


def fits_entry(slug, vp, ov):
    """Phone: nothing is wider than the screen. ov is what OVERFLOW_JS found."""
    vw, doc_w = ov.get("vw", 0), ov.get("docW", 0)
    wide = sorted(ov.get("wide") or [], key=lambda x: -x.get("over", 0))
    problems = []
    if doc_w > vw + 1:
        problems.append("the page is %s px wide and scrolls sideways" % num(doc_w))
    problems += ["%s (%s) reaches from x %s to x %s, %s px past the edge" % (x["sel"], "a line of its text" if x["what"] == "text" else "its box", num(x["x"]), num(x["right"]), num(x["over"])) for x in wide[:6]]
    worst = max([float(doc_w - vw)] + [x.get("over", 0) for x in wide] + [0.0])
    return entry(slug, vp, "fits the screen", not problems, "nothing reaches past the edge of the %s px wide screen and the page does not scroll sideways" % num(vw),
                 ("%d things stick out: %s" % (len(wide) + (1 if doc_w > vw + 1 else 0), "; ".join(problems))) if problems else "nothing sticks out",
                 "every visible element and every line of text; not counted: what a parent that fits the screen cuts off (the scrolling hours line) and what is parked wholly outside the screen",
                 "DESIGN", kind="overflow", diff=round(worst, 1), details=wide)


def measure_view(base, view, slugs, want_images):
    """Measure our pages in one viewport and compare each with its Wix reference. -> {slug: [entries], "site": [entries]}"""
    from playwright.sync_api import sync_playwright
    results, shared = {}, {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            ctx = browser.new_context(**view.options(p))
            for slug in slugs:
                try:
                    results[slug] = compare_page(ctx, base, slug, view, want_images, shared)
                except Exception as e:
                    results[slug] = [entry(slug, view.name, "comparison ran", False, "the page is measured and compared", "%s: %s" % (type(e).__name__, short(str(e), 300)),
                                           "qa/visual_compare.py, " + where_it_broke(), "QA", kind="error", diff=0.0)]
            ctx.close()
        finally:
            browser.close()
    if view.kind == "desktop" and view.brief and shared.get("brief"):
        results[common.SITE_PAGE] = [breakpoints_entry(view, shared["brief"])]
    return results


def where_it_broke():
    """Function and line of the current exception, without any path of this computer."""
    import traceback
    frames = traceback.extract_tb(sys.exc_info()[2])
    mine = [f for f in frames if os.path.basename(f.filename) == NAME + ".py"] or frames
    return " < ".join("%s line %d" % (f.name, f.lineno) for f in reversed(mine[-3:])) if mine else "unknown place"


# The screenshot is evidence: every picture of the page has to be in it. A full-page screenshot does not wait for
# lazy images, so they are loaded and decoded first (the same steps as qa/check_page.py takes before its screenshot).
WALK_JS = r"""async () => {
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
  return true;
}"""
SHOWN_IMAGES = "Array.from(document.images).filter(i => !(i.closest('.lightbox') && !i.closest('.lightbox.open')))"
IMAGES_DONE_JS = "() => %s.every(i => i.complete)" % SHOWN_IMAGES
IMAGES_FORCE_JS = "() => { let n = 0; for (const i of %s) { if (!i.complete && i.loading === 'lazy') { i.loading = 'eager'; n++; } } return n; }" % SHOWN_IMAGES
DECODE_JS = ("() => Promise.race([Promise.all(%s.filter(i => i.complete && i.naturalWidth > 0).map(i => i.decode().catch(() => null))), "
             "new Promise(r => setTimeout(r, 5000))]).then(() => true)" % SHOWN_IMAGES)
# Pictures of the page that are not drawn (not loaded, or broken) at the moment of the screenshot.
IMAGES_MISSING_JS = "() => %s.filter(i => !(i.complete && i.naturalWidth > 0)).map(i => i.getAttribute('src') || '(no src)')" % SHOWN_IMAGES


def open_page(ctx, base, slug):
    """Load one of our pages and let it settle. -> (page, log, status, list of own files that did not arrive)"""
    log = {}
    page = ctx.new_page()
    common.guard(page, log, base, allow_fonts=True)
    common.watch(page, log)
    status = 0
    try:
        resp = page.goto(base + common.PAGES[slug], wait_until="load", timeout=PAGE_TIMEOUT)
        status = resp.status if resp is not None else 0
        if status == 200:
            page.evaluate("() => document.fonts.ready.then(() => true)")
            page.evaluate(WALK_JS)      # walk down the page once so that lazy images start to load
            try:
                page.wait_for_function(IMAGES_DONE_JS, timeout=8000)
            except Exception:
                pass
            if page.evaluate(IMAGES_FORCE_JS):      # a lazy image the walk did not wake: ask for it outright
                try:
                    page.wait_for_function(IMAGES_DONE_JS, timeout=8000)
                except Exception:
                    pass
            try:
                page.wait_for_load_state("networkidle", timeout=4000)
            except Exception:
                pass
            page.evaluate(DECODE_JS)    # loaded is not yet drawn: without this the screenshot shows empty beige tiles
            page.evaluate("() => document.fonts.ready.then(() => true)")
            page.wait_for_timeout(250)
    except Exception as e:
        log.setdefault("failed", []).append({"url": base + common.PAGES[slug], "error": "%s: %s" % (type(e).__name__, short(str(e), 160))})
        status = status or -1
    blocked = set(log.get("blocked", []))
    lost = []
    for f in log.get("failed", []):
        url, error = str(f.get("url", "")), str(f.get("error"))
        own = url.startswith(base) and (status == -1 or any(t in error for t in TRANSIENT))
        font = (urlsplit(url).hostname or "") in common.FONT_HOSTS and url not in blocked      # no host is a font host any more (decision 38)
        if own or font:
            lost.append(f)
    return page, log, status, lost


def compare_page(ctx, base, slug, view, want_images, shared):
    """One page in one viewport: the comparison with its Wix reference, the lines of the brief that belong to this
    viewport, and on the phone the two layout checks. shared collects what one page tells about the whole site."""
    vp = view.name
    out, ref = [], None
    ref_file = "wix-ref/measure-%s-%s.json in the tools folder" % (slug, view.ref)
    try:
        ref = load_reference(slug, view.ref)
    except FileNotFoundError:
        if view.kind == "desktop":      # a width nobody has measured on Wix: said once, not a failure
            out.append(entry(slug, vp, "no reference", True, "a Wix measurement taken at %d px (%s)" % (view.width, ref_file),
                             "no reference: this width is not compared with Wix for this page",
                             "to make one: scripts/wix_measure.py%s %s in the tools folder, or run this script with --refresh-wix" % ("" if view.width == BASE_WIDTH else " --width %d" % view.width, slug),
                             "QA", kind="no-reference", diff=0.0))
        else:
            out.append(entry(slug, vp, "Wix reference", False, "the reference measurement of the Wix page", "missing", ref_file + "; run with --refresh-wix", "QA", kind="error", diff=0.0))
    except Exception as e:
        out.append(entry(slug, vp, "Wix reference", False, "the reference measurement of the Wix page", "unreadable (%s)" % type(e).__name__, ref_file + "; run with --refresh-wix", "QA", kind="error", diff=0.0))
    if ref is None and not view.brief:
        return out          # nothing to compare with, and the brief has no line for this viewport
    page = None
    try:
        for attempt in range(LOAD_TRIES):
            page, log, status, lost = open_page(ctx, base, slug)
            if not lost:
                break
            if attempt + 1 < LOAD_TRIES:
                page.close()
                page = None
                time.sleep(1.0 + 2.0 * attempt)
        if lost:        # measuring a page without its stylesheet or images would only produce differences that are not there
            return out + [entry(slug, vp, "page loads completely", False, "every file of the page arrives",
                                "%d files did not arrive in %d tries: %s" % (len(lost), LOAD_TRIES, "; ".join(
                                    "%s (%s)" % ((str(f["url"])[len(base):] or "the page") if str(f["url"]).startswith(base) else short(str(f["url"]).split("?")[0], 70), short(str(f["error"]), 60)) for f in lost[:5])),
                                "the server did not answer (a busy machine or a server that went away): not compared, run again", "QA", kind="error", diff=0.0)]
        if status != 200:
            return out + [entry(slug, vp, "page loads", False, "status 200", "status %s" % status, common.PAGES[slug] or "index.html", "PAGES", kind="error", diff=0.0)]
        raw = extra = None
        if ref is not None:
            data = page.evaluate(BOTH_JS)
            raw, extra = data["base"], data["extra"]
            for kind in ("text", "images", "boxes", "controls"):
                if len(raw.get(kind, [])) != len(extra.get(kind, [])):
                    raise RuntimeError("the two measuring passes disagree about the %s (%d and %d)" % (kind, len(raw.get(kind, [])), len(extra.get(kind, []))))
        fonts = set(page.evaluate("() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/[\"']/g, ''))"))
        overflow = page.evaluate(OVERFLOW_JS) if view.kind == "phone" else None
        brief = page.evaluate(BRIEF_JS, [list(s) for s in BRIEF_SPEC]) if view.brief else None      # last: it scrolls the page and waits
        shot_rel = side_rel = ""
        wix_img = None
        ref_png = reference_shot(slug, view.ref)
        if ref is not None and os.path.isfile(ref_png):
            try:
                from PIL import Image
                wix_img = Image.open(ref_png).convert("RGB")
            except Exception:
                wix_img = None
        side_problem = ""
        undrawn = []
        if want_images:
            shot = os.path.join(common.SHOTS, SHOT_DIR, "%s-%s-full.png" % (slug, vp))
            os.makedirs(os.path.dirname(shot), exist_ok=True)
            undrawn = page.evaluate(IMAGES_MISSING_JS)
            page.screenshot(path=shot, full_page=True, animations="disabled")
            shot_rel = rel_path(shot)
            if ref is None:
                pass                    # no reference for this width: nothing to put next to our page
            elif os.path.isfile(ref_png):
                try:
                    side_rel = rel_path(side_by_side(shot, ref_png, slug, vp))
                except Exception as e:
                    side_problem = "%s: %s" % (type(e).__name__, short(str(e), 240))
            else:
                side_problem = "no Wix reference screenshot (wix-ref/shots/%s-%s-full.png in the tools folder)" % (slug, view.ref)
    finally:
        if page is not None:
            page.close()

    failed, soft = [], []
    if ref is not None:
        cmp_ = Compare(slug, view, ref, raw, extra, reference_text(slug), wix_img)
        failed, soft = cmp_.run()
        evidence = "; ".join(x for x in ("our page: " + shot_rel if shot_rel else "", "side by side with Wix (outside the site folder): " + side_rel if side_rel else "",
                                          "; ".join(cmp_.summary["notes"][:4])) if x)
        out.append(entry(slug, vp, "summary", True, "the page is measured at %s and compared with the Wix reference %s" % (view.size(), "measure-%s-%s.json" % (slug, view.ref)),
                         cmp_.summary_text, evidence, "QA", kind="summary", diff=0.0, numbers=cmp_.summary))
    out += failed
    if overflow is not None:
        out.append(fits_entry(slug, vp, overflow))
    if brief is not None:
        out += brief_checks(slug, view, brief)
        if view.kind == "desktop":
            shared.setdefault("brief", brief)
    # requests: only the site's own host is let through (the fonts are its own files, decision 38)
    blocked = log.get("blocked", [])
    bad = common.unexpected_blocked(log)
    here = lambda u: str(u)[len(base):] if str(u).startswith(base) else str(u)
    bad = [here(u) for u in bad]
    bad += ["%s (failed: %s)" % (here(f["url"]), f["error"]) for f in log.get("failed", []) if f["url"] not in blocked and not common.is_expected_external(f["url"])]
    bad += ["%s (status %s)" % (here(b["url"]), b["status"]) for b in log.get("bad_status", []) if not common.is_expected_external(b["url"])]
    expected_blocked = sorted({u.split("?")[0] for u in blocked if common.is_expected_external(u)})
    out.append(entry(slug, vp, "requests", not bad, "every file of the page loads from the site itself, the fonts too (Google Maps blocked on purpose)",
                     "%d requests failed or went to an unexpected host: %s" % (len(bad), "; ".join(short(b, 160) for b in bad[:6])) if bad else "all loaded",
                     ("blocked on purpose: " + ", ".join(short(u, 90) for u in expected_blocked[:4])) if expected_blocked else "nothing blocked", "PAGES", kind="requests", diff=0.0))
    missing = [f for f in (SANS, SERIF) if f not in fonts]
    if missing:         # the font files are the site's own, so a font that is not loaded is one the page does not ask for
        out.append(entry(slug, vp, "web fonts loaded", False, "Bodoni Moda and Figtree are loaded before measuring", "not loaded: %s" % ", ".join(missing),
                         "document.fonts after document.fonts.ready; without them every text is measured in a fallback font", "PAGES", kind="error", diff=0.0))
    if undrawn:         # the picture would show empty tiles that the page itself does not have
        out.append(entry(slug, vp, "screenshot shows every picture", False, "every picture of the page is loaded before the screenshot is taken",
                         "%d not loaded: %s" % (len(undrawn), ", ".join(short(str(u), 60) for u in undrawn[:6])),
                         "%s; a picture that does not load at all is also reported by qa/check_page.py" % (shot_rel or "the screenshot"), "QA", kind="error", diff=0.0))
    if side_problem:
        out.append(entry(slug, vp, "side-by-side image", False, "our screenshot next to the Wix reference, in the private folder", side_problem,
                         "written only outside the site folder", "QA", kind="error", diff=0.0))
    out += soft
    return out


def refresh_wix(slugs, views):
    """Measure and photograph the live Wix site again with the script that made the reference. -> (ok, text)
    That script takes the 1280 px and the phone reference in one run and the other desktop widths in a second one."""
    script = os.path.join(common.ENV, *WIX_SCRIPT)
    if not os.path.isfile(script):
        return False, "%s not found in the tools folder" % "/".join(WIX_SCRIPT)
    if inside(script, common.SITE) or inside(common.WIX_REF, common.SITE):
        return False, "refused: the Wix reference would be written inside the site folder"
    runs = []
    if any(v.ref in ("desktop", "phone") for v in views):
        runs.append([])
    extra_widths = [v.width for v in views if v.ref not in ("desktop", "phone")]
    if extra_widths:
        runs.append([a for w in extra_widths for a in ("--width", str(w))])
    for options in runs:
        try:
            r = subprocess.run([sys.executable, script] + options + list(slugs), cwd=common.ENV, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=2400)
        except Exception as e:
            return False, "%s: %s" % (type(e).__name__, short(str(e), 200))
        text = r.stdout.decode("utf-8", "replace")
        errors = [ln for ln in text.splitlines() if " ERROR " in ln]
        if r.returncode != 0 or errors:
            return False, "exit code %s; %s" % (r.returncode, short(" | ".join(errors) or text[-300:], 300))
    return True, "%d pages measured again for %s" % (len(slugs), ", ".join(v.name for v in views))


def same_function():
    """Is MEASURE_JS still the function that made the Wix reference? -> None when it is (or cannot be checked), else a text."""
    try:
        with open(os.path.join(common.ENV, *WIX_SCRIPT), encoding="utf-8") as f:
            m = re.search(r'JS = """(.*?)"""', f.read(), re.S)
    except Exception:
        return None
    if not m:
        return "could not find the measuring function in %s" % "/".join(WIX_SCRIPT)
    squash = lambda s: "".join(s.split())
    return None if squash(m.group(1)) == squash(MEASURE_JS) else "MEASURE_JS in qa/visual_compare.py is no longer the function of %s" % "/".join(WIX_SCRIPT)


def drop_old_copy():
    """Earlier versions of this script wrote the same report twice, as visual_compare.json and as visual.json.
    Only visual_compare.json is written now. A visual.json that an old run left behind is removed, so that nobody
    reads stale numbers. It is only removed when it says itself that this script wrote it."""
    path = os.path.join(common.REPORTS, OLD_COPY + ".json")
    try:
        with open(path, encoding="utf-8") as f:
            mine = json.load(f).get("script") == "qa/%s.py" % NAME
    except Exception:
        return False
    if mine:
        try:
            os.remove(path)
            return True
        except OSError:
            pass
    return False


def chosen_views(ap, args, argv):
    """The viewports of this run, in the order they are reported."""
    given = [a.split("=")[0] for a in argv if a.startswith("--v")]
    viewport_given = any(len(a) >= 3 and "--viewport".startswith(a) for a in given)
    if args.width is None:
        views = [View("desktop", w) for w in DESKTOP_WIDTHS] if args.viewport in ("desktop", "both") else []
        return views + ([View("phone")] if args.viewport in ("phone", "both") else [])
    if not MIN_DESKTOP <= args.width <= 4000:
        ap.error("--width: a desktop width is %d to 4000 px (below %d px the tablet and phone layouts start)" % (MIN_DESKTOP, MIN_DESKTOP))
    if viewport_given and args.viewport == "phone":
        ap.error("--width: a desktop width cannot go with --viewport phone")
    return [View("desktop", args.width)] + ([View("phone")] if viewport_given and args.viewport == "both" else [])


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    argv = list(sys.argv[1:] if argv is None else argv)
    ap = common.cli_parser("Compare our pages with the live Wix site (positions, sizes, fonts and colours) and test the brief's measurement list.",
                           page_help="SLUG[,SLUG] or all (default all). The 404 page has no Wix counterpart and is skipped.",
                           viewport_help="desktop (the four widths %s), phone or both (default both)" % ", ".join(str(w) for w in DESKTOP_WIDTHS))
    ap.add_argument("--width", type=int, default=None, metavar="N",
                    help="one desktop width alone, N x %d (for example 1440). The phone is left out unless --viewport both is given too" % DESKTOP_HEIGHT)
    ap.add_argument("--refresh-wix", action="store_true", help="measure and photograph the live Wix site again first (runs scripts/wix_measure.py of the tools folder)")
    ap.add_argument("--no-images", action="store_true", help="measure only: no screenshots and no side-by-side images")
    args = ap.parse_args(argv)
    slugs = [s for s in common.cli_pages(ap, args.page) if s in SLUGS]
    views = chosen_views(ap, args, argv)
    names = [v.name for v in views]
    results = []
    if not slugs:       # for example --page 404: a page of ours that Wix does not have, nothing to compare
        print("%s: --page %s names no page that exists on Wix (pages: %s), nothing to compare" % (NAME, args.page, ", ".join(SLUGS)))

    changed = same_function()
    results.append(entry("site", "-", "same measuring function on both sides", changed is None, "the function of scripts/wix_measure.py, unchanged",
                         changed or "unchanged", "MEASURE_JS in qa/visual_compare.py", "QA", kind="setup", diff=0.0))
    if args.refresh_wix and slugs:
        ok, text = refresh_wix(slugs, views)
        results.append(entry("site", "-", "Wix reference measured again", ok, "scripts/wix_measure.py runs for the chosen pages", text, "wix-ref in the tools folder", "QA", kind="setup", diff=0.0))

    started = time.time()
    base_used = common.report_base(args.base)
    if slugs:
        with common.target_base(args.base) as base:
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(views)) as pool:     # one browser per viewport, side by side
                futures = {v.name: pool.submit(measure_view, base, v, slugs, not args.no_images) for v in views}
                done = {}
                for v in views:
                    try:
                        done[v.name] = futures[v.name].result()
                    except Exception as e:
                        done[v.name] = {s: [entry(s, v.name, "comparison ran", False, "the page is measured and compared", "%s: %s" % (type(e).__name__, short(str(e), 300)),
                                                  "qa/visual_compare.py", "QA", kind="error", diff=0.0)] for s in slugs}
        for v in views:
            results += done[v.name].get(common.SITE_PAGE, [])
        for slug in slugs:
            for v in views:
                results += done[v.name].get(slug, [])

    failed = [r for r in results if not r["ok"]]
    without = sum(1 for r in results if r.get("kind") == "no-reference")       # desktop widths nobody measured on Wix: ok true, but said
    per_page = {}
    for r in results:
        if r.get("kind") == "summary":
            per_page.setdefault(r["page"], {})[r["viewport"]] = dict(r.get("numbers", {}), differences=sum(1 for f in failed if f["page"] == r["page"] and f["viewport"] == r["viewport"]))
    try:
        measured = time.strftime("%Y-%m-%d", time.localtime(max(os.path.getmtime(os.path.join(common.WIX_REF, f)) for f in os.listdir(common.WIX_REF) if f.startswith("measure-"))))
    except Exception:
        measured = "unknown"
    extra = {"script": "qa/%s.py" % NAME, "tolerance_desktop_px": TOL["desktop"], "tolerance_brief_px": BRIEF_TOL, "wix_reference_measured": measured,
             "viewports": {v.name: {"size": v.size(), "wix_reference": "measure-<slug>-%s.json" % v.ref} for v in views},
             "screenshots": "qa/screenshots/%s/" % SHOT_DIR, "side_by_side": rel_path(os.path.join(common.PRIVATE, SIDE_DIR)) + "/ (outside the site folder, never commit)",
             "last_run": {"pages": slugs, "viewports": names, "entries": len(results), "differences": len(failed), "without_wix_reference": without,
                          "seconds": round(time.time() - started, 1)},
             "pages": per_page,
             "desktop_note": ("Each desktop width is compared with the Wix reference taken at that width, and only the Wix value passes (decision 17). "
                              "The entries named brief-... test the brief's measurement list on our pages at %d px (decision 1)." % BRIEF_WIDTH),
             "phone_note": ("Phone: font size, letter spacing and line height are compared with the Wix numbers as written (decision 16). Places and sizes are "
                            "listed with ok true against the Wix numbers times 390 / 320 (from %s px). What counts for the layout: the entries 'block order' and 'fits the screen'."
                            % num(TOL["phone"]))}
    # Differences have no fixed names, so one that is fixed would stay in the report for ever: every earlier entry
    # of the pages and viewports of this run is replaced (see common.save_report). Entries for the whole site are
    # replaced only for the viewports of this run, so a phone run keeps the breakpoint entry of the last desktop run.
    covered = {(s, n) for s in slugs for n in names} | {(common.SITE_PAGE, n) for n in names} | {(common.SITE_PAGE, common.NO_VIEWPORT)}
    common.save_report(NAME, results, base_used, extra, replace=covered)
    drop_old_copy()

    for r in failed:
        print("FAIL [%s] %s %s | %s | %s: %s | ours: %s" % (r["owner"], r["page"], r["viewport"], r["check"], "brief" if r.get("kind") == "brief" else "Wix",
                                                          short(r["expected"], 110), short(r["actual"], 110)))
    owners = {}
    for r in failed:
        owners[r["owner"]] = owners.get(r["owner"], 0) + 1
    print("%s: %d pages x %d viewports (%s), %d entries, %d differences%s%s, report qa/reports/%s.json"
          % (NAME, len(slugs), len(views), ", ".join(names), len(results), len(failed),
             (" (%s)" % ", ".join("%s %d" % kv for kv in sorted(owners.items()))) if owners else "",
             (", %d page and width combinations without a Wix reference (not compared)" % without) if without else "", NAME))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
