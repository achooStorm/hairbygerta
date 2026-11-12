"""Check the words: every built page against its content file, the business facts and the live Wix wording.

No browser is needed. Each page is fetched from a local server (or from --base) and its HTML is read with the
standard library. The content files are always read from the site folder on this computer (content/*.json).

What it checks on every page
  content-file          content/<slug>.json is JSON with a title, a description, an h1 and notes
  title, meta-description, h1, og-tags
                        equal the content file (og:site_name equals og_site_name in content/site.json)
  text-in-order         every text of the content file, and the header, navigation and footer text of
                        content/site.json, is on the page, in the same order, with nothing lost. One more entry per
                        difference: text-changed (other words in that place), text-missing (nothing in that place)
                        or text-order (the text stands somewhere else), each named after the content key.
                        Texts of html fields are compared without their tags.
  no-extra-text         the page shows no text that is not in its content file, in site.json or fixed by the build
                        contract (the pin in front of the address, the copyright sign and the year). One entry
                        text-extra per find.
  text-verbatim         the texts are on the page letter for letter, spaces and punctuation included
  screen-reader-labels  every aria-label, alt, title and data-sent on the page is a text of the content file or a label
                        the page modules compose from it ("View photo 3 of 21", "Book Now: Balayage", "Menu").
                        The labels found are listed in the entry.
  links-from-content    every link written in a content file (nav, footer, buttons, links inside html fields) is on
                        the page with the same text and the same target
  images-from-content   the photos of the page are the image slots of the content file, in the same order
  copyright-line        the footer ends with the copyright sign, a year and the business name
  fact-...              the business facts are exact wherever they appear: business name, Gerta Lila (Olgerta Lila on
                        the Terms and Accessibility pages only), salon name and address, phone text and tel links,
                        email text and mailto links, hours, the Facebook, Instagram and Maps links
  fact-services, fact-service-images (Book Online), fact-gallery-images (Gallery), fact-about-photos (About),
  fact-home-photos (Home)
                        the ten services with title, description, duration and price, and the photos, in the order
                        the brief gives
  privacy-...           (Privacy Policy) no sentence says that Wix stores data or sets cookies, the three statements
                        the brief asks for are there, the last heading is Questions. Online booking was dropped on
                        2 November 2026, so the booking statement says that appointments are booked by phone and that
                        the website does not collect or store booking details, and the cookies statement names Google
                        Maps on the Contact page (no booking provider any more). Since 9 November 2026 the fonts are
                        files of the site itself, so the page no longer names Google Fonts, and naming it is a failure
  wix-wording           (the nine pages that exist on Wix) title, meta description, main text, footer and navigation
                        compared sentence by sentence with the reference files in the tools folder (wix-ref/<slug>.txt).
                        One entry per sentence that differs. A difference is intended, and listed with ok true, only
                        when it is on this fixed list: the privacy rule above (with a sentence that goes on about Wix),
                        the closing booking note, the Hours block and the Open in Google Maps link of the contact page,
                        the copyright line, the Call
                        button at the bottom of the screen on phones (its label and the phone number), text that Wix
                        repeats for screen readers, the copies of the scrolling hours line, an order the build contract
                        decided (sections 10.6 and 10.8), the mark of the required Email field (10.8), the new title of
                        the Contact page (10.33), and two changes made when online booking was dropped on 2 November 2026
                        (the Book Now buttons call 347-671-5095): the new meta description of the Book Online page, and
                        the Privacy Policy list item "Service providers that help us operate the website" without the
                        words "and booking system"; and two changes of 9 November 2026: the new meta description of the
                        home page and the comma taken out of "high-quality, hair extensions" on the home page; and three
                        changes of 12 November 2026: the titles of the four policy pages end with "Hair & Makeup by Gerta"
                        (Wix: "Hairbygerta"), three sentences of the Terms & Conditions no longer speak of booking online
                        or through the site, and the Accessibility Statement says it was last updated on 11/12/2026. A note in
                        a content file does not make a difference intended. A title tag or meta description that Wix has
                        must equal the Wix value (the Contact title, the four policy page titles and the Book Online and
                        home meta descriptions apart).
                        Skipped with a note when the reference folder is not there.
  site-json-facts       (page "site") the business facts stored in content/site.json are the facts of the brief

Who has to fix a failure (owner): CONTENT when the content file is wrong (it breaks a fact of the brief, or it differs
from the live Wix wording and the difference is not on the fixed list), PAGES when the content file is right and the page differs from it.

    ../hairbygerta-env/venv/Scripts/python.exe qa/check_content.py
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_content.py --page home,contact
    ../hairbygerta-env/venv/Scripts/python.exe qa/check_content.py --base https://achoostorm.github.io/hairbygerta/

Results go to qa/reports/check_content.json. Every entry has viewport "-": the words do not depend on a screen size
(--viewport is accepted because every QA script takes it). One line is printed per failed check, then a summary.
Exit code 0 when everything passed, 1 otherwise.

Extra options: --show-intended also prints the intended differences from the Wix wording. For the self-test of this
script only: --root FOLDER serves another copy of the site and reads its content folder, --out FOLDER writes the
report there instead of qa/reports. The self-test plants defects in scratch copies of the site (a changed word,
a dropped paragraph, a wrong phone link, two services swapped and more) and lives outside the site folder, in the
tools folder: stage/qa/check_content/selftest.py.

How a page is read: every text node of the body counts, also text that is hidden from screen readers (the pin, the
copies of the scrolling hours line, the star behind Email). Scripts and styles do not count. A text built by
js/site.js while the page runs (the photo viewer, the status line of the form) is not in the HTML and is not checked
here; the status line is checked as the data-sent attribute it is taken from.
"""
import collections, difflib, html.parser, json, os, posixpath, re, sys, time
import urllib.error, urllib.parse, urllib.request

sys.dont_write_bytecode = True      # no __pycache__ in the site folder: compiled files carry paths from this computer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

NAME = "check_content"
VIEWPORT = common.NO_VIEWPORT       # no browser, no viewport
SITE_PAGE = common.SITE_PAGE
USER_AGENT = "hairbygerta-qa/check_content"
OWN_MARK = b"hairbygerta.com"       # every page of this site carries it (canonical link, mail link)
ORIGIN = "https://site.invalid/"    # stands for the site root when a relative address is worked out
SITE_FILE = "content/site.json"

# ---------------------------------------------------------------- FACTS, as the brief gives them. Never paraphrase.
BUSINESS = "Hair & Makeup by Gerta"
STYLIST = "Gerta Lila"
LEGAL_NAME = "Olgerta Lila"
LEGAL_NAME_PAGES = ("terms-conditions", "accessibility-statement")     # the only pages that use the legal name
SALON = "Le Vigne Hair Salon"
STREET = "644 Forest Ave"
CITY = "Staten Island, NY 10310"
ADDRESS = STREET + ", " + CITY
PHONE_TEXT = "347-671-5095"
TEL = "tel:" + common.PHONE
EMAIL = common.EMAIL
MAILTO = "mailto:" + EMAIL
HOURS_DAYS, HOURS_TIMES = "Tuesday - Saturday", "9 AM - 5 PM"
HOURS = HOURS_DAYS + ", " + HOURS_TIMES
# The closing note of the Book Online page is the closing line of the first version of the site, word for word.
# It gives the hours with "to". That wording is accepted on that page only.
HOURS_OTHER_WORDING = {"book-online": ("Tuesday to Saturday", "9 AM to 5 PM", "Tuesday to Saturday, 9 AM to 5 PM")}
FACEBOOK = "https://www.facebook.com/profile.php?id=61588784402912"
INSTAGRAM = "https://www.instagram.com/hairbygerta/"
MAPS = "https://www.google.com/maps/search/?api=1&query=644+Forest+Ave,+Staten+Island,+NY+10310"
PRICE = "Call for price"
SERVICES = (    # title, description, duration, price
    ("Haircut & Style", "Transform your hair with precision cutting and styling.", "45 min", PRICE),
    ("Hair Coloring", "Revitalize your hair with our expert coloring services.", "1 hr 30 min", PRICE),
    ("Makeup Session", "Natural makeup that enhances your beauty.", "45 min", PRICE),
    ("Dream Bridal Hair", "Romantic, long-lasting bridal hair tailored to your dress and vision.", "1 hr 30 min", PRICE),
    ("Highlights & Lowlights", "Customized foils to add brightness, depth, and dimension.", "2 hr 30 min", PRICE),
    ("Balayage", "Hand-painted color for a soft, sun-kissed finish.", "3 hr", PRICE),
    ("Keratin Treatment", "Frizz-fighting smoothing treatment for sleek, manageable hair.", "2 hr 30 min", PRICE),
    ("Brazilian Blowout", "Long-lasting smoothness with mirror-like shine.", "2 hr", PRICE),
    ("Perm & Texture Waves", "Custom curls or waves with movement and body.", "1 hr", PRICE),
    ("Kids' Haircut", "Friendly, patient cuts just for kids.", "45 min", PRICE),
)
SERVICE_IMAGES = ("svc-haircut", "g10", "makeup-red-lips", "svc-bridal", "foils-highlights", "g19", "g17", "g16", "g14", "g18")
GALLERY_IMAGES = ("g01", "g02", "foils-highlights", "g04", "g05", "g06", "g07", "brunette-balayage", "copper-waves", "g10",
                  "makeup-red-lips", "g12", "g13", "g14", "g15", "g16", "g17", "g18", "g19", "g20", "g21")
ABOUT_LEFT, ABOUT_RIGHT = ("brunette-balayage", "about-salon"), ("g10", "copper-waves")
HOME_ROW, HOME_MEET = ("home-styling", "foils-highlights", "home-smile", "home-waves"), ("makeup-red-lips", "meet-extensions")
BRIEF_IMAGES = {"book-online": SERVICE_IMAGES, "gallery": GALLERY_IMAGES, "about": ABOUT_LEFT + ABOUT_RIGHT,
                "home": HOME_ROW + HOME_MEET}

# ---------------------------------------------------------------- what the build contract fixes (tools/CONTRACT.md)
MENU_LABEL, NAV_LABEL = "Menu", "Main"                  # section 6: button.menu-btn, nav.main-nav
PHOTO_ROW_LABEL = "Featured work"                       # section 7, Home: section.photo-row
HOURS_LABEL = "Hours: %s"                               # section 7, Home: div.marquee
BOOK_LABEL = "%s: %s"                                   # section 7, Book Online: "Book Now: SERVICE"
BOOK_TEXT = "Book Now"                                  # section 7, used when the content file has no button_label
GALLERY_LABEL = "View photo {n} of {total}"             # section 7, used when the content file has no link_label
PIN = "\U0001F4CD"                                      # section 7, Home: span.pin in front of the address
COPYRIGHT_SIGN = "\u00a9"                               # section 6: p.copy
H1_IS_ALSO = {"home": "hero.heading"}                   # the h1 is stored twice in home.json, the page prints it once
H1_COMES_AFTER = {"home": "site_title", "contact": "kicker"}    # section 7: where the h1 is not the first text of main
PLACES = ("header", "main", "footer")
PLACE_NAMES = {"top": "above the header", "header": "header", "main": "main", "footer": "footer"}

# Keys of a content file that never hold a text of the page.
HEAD_KEYS = ("slug", "path", "title", "description", "h1", "notes")       # top level only
NON_TEXT_KEYS = frozenset(("slot", "file", "alt_original", "width", "height", "id", "type", "required", "autocomplete",
                           "href", "path", "query", "marquee_repeat", "required_mark", "notes"))
# Attributes whose value a visitor may hear or see.
LABEL_ATTRS = ("aria-label", "alt", "title", "placeholder", "aria-description", "aria-roledescription",
               "aria-valuetext", "aria-placeholder", "data-sent")

VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
NO_TEXT = frozenset(("script", "style", "template"))
BLOCK = frozenset("html body header footer main nav section article aside div p h1 h2 h3 h4 h5 h6 ul ol li dl dt dd table "
                  "thead tbody tfoot tr td th caption form fieldset legend figure figcaption blockquote pre address hr br "
                  "iframe textarea select option details summary dialog noscript picture video audio canvas svg".split())
# An inline element (a link, a button, a label, a span) that sits straight in one of these, with no text beside it,
# is a line of its own on the screen (home: the Book Online button and the phone link inside the hero box).
CONTAINER = frozenset("body header footer main nav section article aside div form fieldset ul ol li td th figure".split())
KINDS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6", "li", "p"))
HEADINGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))


# ---------------------------------------------------------------- text helpers

INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"))    # zero-width characters and the soft hyphen
APOSTROPHES = {0x2019: "'", 0x2018: "'", 0x02BC: "'"}
TOKEN = re.compile(r"\w+|[^\w\s]")
QUOTES = "\"'\u201c\u201d\u2018\u2019"


def norm(text):
    """Visible text: invisible characters out, every run of white space (line breaks, no-break spaces) one space."""
    return " ".join(str(text).translate(INVISIBLE).split())


def fold(text):
    """For the facts of the brief only: a typographic apostrophe counts as a straight one (Kids' Haircut)."""
    return norm(text).translate(APOSTROPHES)


def short(text, limit=200):
    text = norm(text)
    return text if len(text) <= limit else text[:limit - 3] + "..."


def quote(text, limit=200):
    return '"%s"' % short(text, limit)


def plural(n, word, many=None):
    return "%d %s" % (n, word if n == 1 else (many or word + "s"))


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def word_diff(expected, actual, limit=6):
    """The words that differ, as short pairs: content has "X", page has "Y"."""
    a, b = expected.split(), actual.split()
    parts = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            parts.append('"%s" became "%s"' % (" ".join(a[i1:i2]), " ".join(b[j1:j2])))
    more = "" if len(parts) <= limit else " (and %d more)" % (len(parts) - limit)
    return "; ".join(parts[:limit]) + more


SENTENCE_END = re.compile(r"[.!?][\"'\u201d\u2019)\]]*\s+")


def sentences(line):
    """A line of text as sentences. A numbered heading such as "9. Contact" stays one piece."""
    out, start = [], 0
    for m in SENTENCE_END.finditer(line):
        head = line[start:m.end()].strip()
        nxt = line[m.end():m.end() + 1]
        if not nxt or not (nxt.isupper() or nxt.isdigit() or nxt in "\u201c\"('\u2018"):
            continue
        if re.fullmatch(r"\d+[.)]", head):
            continue
        out.append(head)
        start = m.end()
    tail = line[start:].strip()
    if tail:
        out.append(tail)
    return out


class Line:
    __slots__ = ("text", "start", "end", "place", "kind")

    def __init__(self, text, start, end, ctx):
        self.text, self.start, self.end = text, start, end
        self.place, self.kind = ctx if ctx else ("main", None)


class Flow:
    """Text in reading order: one string with single spaces, the places where an element starts or ends (a word
    never runs across one), and the lines (the text between two block boundaries)."""

    def __init__(self):
        self.chars, self.marks, self.lines = [], set(), []
        self._start, self._ctx, self._open = 0, None, False
        self.text = ""

    def add(self, data, ctx=None):
        for ch in data.translate(INVISIBLE):
            if ch.isspace():
                if self.chars and self.chars[-1] != " ":
                    self.chars.append(" ")
            else:
                if not self._open:
                    self._open, self._ctx = True, ctx
                self.chars.append(ch)

    def mark(self):
        self.marks.add(len(self.chars))

    def brk(self):
        end = len(self.chars)
        while end > self._start and self.chars[end - 1] == " ":
            end -= 1
        if end > self._start:
            self.lines.append(Line("".join(self.chars[self._start:end]), self._start, end, self._ctx))
        if self.chars and self.chars[-1] != " ":
            self.chars.append(" ")
        self._start, self._ctx, self._open = len(self.chars), None, False
        self.marks.add(len(self.chars))

    def done(self):
        self.brk()
        self.text = "".join(self.chars).rstrip()
        return self


def tokens_of(text, marks=()):
    """Words and punctuation marks with their place in the text: [(token, start, end)]. White space never counts."""
    out = []
    for m in TOKEN.finditer(text):
        s, e = m.span()
        if marks and e - s > 1:
            for cut in [k for k in range(s + 1, e) if k in marks]:
                out.append((text[s:cut], s, cut))
                s = cut
        out.append((text[s:e], s, e))
    return out


# ---------------------------------------------------------------- reading a page

class Node:
    __slots__ = ("tag", "attrs", "parent", "children", "data")

    def __init__(self, tag, attrs=None, parent=None, data=None):
        self.tag, self.attrs, self.parent, self.children, self.data = tag, attrs or {}, parent, [], data

    def classes(self):
        return self.attrs.get("class", "").split()


class Tree(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.cur = self.root

    def _open(self, tag, attrs):
        node = Node(tag, {k: ("" if v is None else v) for k, v in attrs}, self.cur)
        self.cur.children.append(node)
        return node

    def handle_starttag(self, tag, attrs):
        node = self._open(tag, attrs)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self._open(tag, attrs)

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.children.append(Node(None, None, self.cur, data))


def parse_html(source):
    tree = Tree()
    tree.feed(source)
    tree.close()
    return tree.root


def descend(node):
    """Every element below node, in the order of the source. Scripts, styles and templates are left out."""
    for child in node.children:
        if child.tag is not None and child.tag not in NO_TEXT:
            yield child
            yield from descend(child)


def find(node, tag=None, cls=None):
    return [n for n in descend(node) if (tag is None or n.tag == tag) and (cls is None or cls in n.classes())]


def is_block(node):
    if node.tag in BLOCK:
        return True
    parent = node.parent
    return (parent is not None and parent.tag in CONTAINER
            and not any(c.tag is None and norm(c.data) for c in parent.children))


def flow_of(node, flow=None, place=None, kind=None, places=False):
    """Feed the text below node into a Flow. With places=True every line also knows whether it is in the header,
    in main or in the footer, and whether it is a heading, a paragraph or a list item."""
    flow = flow or Flow()
    for child in node.children:
        if child.tag is None:
            flow.add(child.data, (place or "top", kind) if places else None)
            continue
        if child.tag in NO_TEXT:
            continue
        block = is_block(child)
        flow.brk() if block else flow.mark()
        flow_of(child, flow, place or (child.tag if child.tag in PLACES else None),
                child.tag if child.tag in KINDS else kind, places)
        flow.brk() if block else flow.mark()
    return flow


def node_text(node):
    return flow_of(node).done().text


def place_of(node):
    found = "top"
    while node is not None:
        if node.tag in PLACES:
            found = node.tag
        node = node.parent
    return found


def image_name(address):
    """images/sm/g12.jpg -> g12"""
    path = urllib.parse.urlsplit(address.strip()).path
    return os.path.splitext(posixpath.basename(path))[0]


def resolve(slug, href):
    """A link of a page as a full address, so that ../gallery/ on one page and gallery/ on another compare equal."""
    return urllib.parse.urljoin(ORIGIN + common.PAGES[slug], href.strip())


def content_target(target):
    """A link of a content file (a site path, a {{root}} address, or tel:, mailto:, https:) as a full address."""
    target = target.strip()
    if target.startswith("{{root}}"):
        return ORIGIN + target[len("{{root}}"):].lstrip("/")
    if target.startswith("/") and not target.startswith("//"):
        return ORIGIN + target.lstrip("/")
    return target


Link = collections.namedtuple("Link", "place href text label book node")
Image = collections.namedtuple("Image", "place name alt node")


class Page:
    """One built page, read from its HTML."""

    def __init__(self, slug, source):
        self.slug = slug
        root = parse_html(source)
        body = next((n for n in descend(root) if n.tag == "body"), None)
        self.body = body if body is not None else root
        in_body = set(id(n) for n in descend(self.body)) if body is not None else set()
        head = [n for n in descend(root) if id(n) not in in_body and n is not body]
        self.titles = [norm(node_text(n)) for n in head if n.tag == "title"]
        self.descriptions, self.og = [], {}
        for n in head:
            if n.tag != "meta":
                continue
            if n.attrs.get("name", "").strip().lower() == "description":
                self.descriptions.append(norm(n.attrs.get("content", "")))
            prop = n.attrs.get("property", "").strip().lower()
            if prop.startswith("og:"):
                self.og.setdefault(prop, []).append(norm(n.attrs.get("content", "")))
        flow = flow_of(self.body, places=True).done()
        self.text, self.lines = flow.text, flow.lines
        self.tokens = tokens_of(flow.text, flow.marks)
        self.links, self.images, self.labels, self.forms, self.h1 = [], [], [], [], []
        self.form_actions = []
        self.year = None
        for n in descend(self.body):
            for attr in LABEL_ATTRS:
                value = norm(n.attrs.get(attr, ""))
                if value:
                    self.labels.append((attr, value, n.tag))
            if n.tag == "input" and n.attrs.get("type", "").lower() in ("button", "submit", "reset") and norm(n.attrs.get("value", "")):
                self.labels.append(("value", norm(n.attrs["value"]), n.tag))
            if n.tag == "a" and "href" in n.attrs:
                self.links.append(Link(place_of(n), n.attrs["href"].strip(), norm(node_text(n)),
                                       norm(n.attrs.get("aria-label", "")), "data-book" in n.attrs, n))
            elif n.tag == "img":
                self.images.append(Image(place_of(n), image_name(n.attrs.get("src", "")), norm(n.attrs.get("alt", "")), n))
            elif n.tag == "form":
                # Since 9 November 2026 (decision 41) the form names its address in data-mailto and has no action.
                self.forms.append(n.attrs.get("data-mailto", "").strip())
                self.form_actions.append(n.attrs.get("action", "").strip())
            elif n.tag == "h1":
                self.h1.append(norm(node_text(n)))
            if "data-year" in n.attrs and self.year is None:
                self.year = norm(node_text(n))

    def lines_in(self, place):
        return [l.text for l in self.lines if l.place == place]

    def lines_between(self, start, end):
        return [l.text for l in self.lines if l.start < end and l.end > start]

    def with_class(self, cls, tag=None, place="main"):
        return [n for n in find(self.body, tag, cls) if place is None or place_of(n) == place]


# ---------------------------------------------------------------- what the content files say the page shows

class Piece:
    """One text the page has to show."""
    __slots__ = ("file", "key", "text", "marks", "lines", "kind", "place", "intended")

    def __init__(self, file, key, text, marks, lines, kind, place, intended):
        self.file, self.key, self.text, self.marks, self.lines = file, key, text, marks, lines
        self.kind, self.place, self.intended = kind, place, intended

    @property
    def where(self):
        return "%s: %s" % (self.file, self.key) if self.file else self.key


ContentLink = collections.namedtuple("ContentLink", "place target text label where")
Slot = collections.namedtuple("Slot", "where file alt")

INLINE_TAG = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)([^<>]*)>")
HREF = re.compile(r"""href\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)


def inline_parts(source):
    """The text of an html field without its tags: (text, element boundaries, lines, links).
    The text between the tags is taken as written: the generator escapes it, so an entity there would show as typed."""
    flow, links, link, pos = Flow(), [], None, 0
    for m in INLINE_TAG.finditer(source):
        flow.add(source[pos:m.start()])
        pos = m.end()
        tag = m.group(2).lower()
        if tag == "br":
            flow.brk()
            continue
        flow.mark()
        if tag == "a":
            if not m.group(1):
                href = HREF.search(m.group(3))
                link = (next((g for g in href.groups() if g is not None), "") if href else "", len(flow.chars))
            elif link:
                links.append((link[0], norm("".join(flow.chars[link[1]:]))))
                link = None
    flow.add(source[pos:])
    flow.done()
    return flow.text, flow.marks, [l.text for l in flow.lines], links


class Expected:
    """Everything one page has to show, worked out from its content file and from site.json."""

    def __init__(self, slug):
        self.slug, self.file = slug, "content/%s.json" % slug
        self.top, self.header, self.main, self.footer = [], [], [], []
        self.labels, self.links, self.slots, self.problems = [], [], [], []
        self.title = self.description = self.h1 = None
        self.notes = ""

    @property
    def pieces(self):
        return self.top + self.header + self.main + self.footer

    def lines_in(self, place):
        return [line for p in self.pieces if p.place == place for line in p.lines]

    def piece(self, bucket, file, key, text, is_html=False, kind=None, place="main", intended=None):
        if not isinstance(text, str):
            self.problems.append("%s: %s must be a text" % (file, key))
            return None
        if is_html:
            body, marks, lines, links = inline_parts(text)
            for href, link_text in links:
                self.links.append(ContentLink(place, content_target(href), link_text, "", "%s: %s" % (file, key)))
        else:
            body, marks = norm(text), ()
            lines = [body] if body else []
        if not body:
            return None
        made = Piece(file, key, body, marks, lines, kind, place, intended)
        bucket.append(made)
        return made


def is_slot(value):
    return isinstance(value, dict) and isinstance(value.get("file"), str) and ("slot" in value or "alt" in value)


def expect_main(ex, content, site):
    """Walk the content file in key order: that is the reading order of the page (contract, section 3)."""
    slug, file = ex.slug, ex.file
    state = {"intended": None}

    def emit(key, text, is_html=False, kind=None, intended=None):
        return ex.piece(ex.main, file, key, text, is_html, kind, "main", intended or state["intended"])

    def label(attr, text, key):
        if isinstance(text, str) and norm(text):
            ex.labels.append((attr, norm(text), "%s: %s" % (file, key)))

    def walk(value, path, depth):
        if is_slot(value):
            alt = value.get("alt") if isinstance(value.get("alt"), str) else ""
            ex.slots.append(Slot("%s: %s" % (file, path), value["file"], norm(alt)))
            label("alt", alt, path + ".alt")
        elif isinstance(value, dict):
            if set(value) == {"html"}:
                emit(path, value["html"], True)
                return
            before = state["intended"]
            if slug == "contact" and path.startswith("info[") and (value.get("id") == "hours" or value.get("heading") == "Hours"):
                state["intended"] = "the Hours block of the contact page is not on the Wix page, it is added on purpose"
            for key, item in value.items():
                handle(key, item, value, "%s.%s" % (path, key) if path else key, depth)
            state["intended"] = before
        elif isinstance(value, list):
            for i, item in enumerate(value):
                where = "%s[%d]" % (path, i)
                if isinstance(item, str):
                    emit(where, item)
                else:
                    walk(item, where, depth + 1)
        elif isinstance(value, str):
            emit(path, value)

    def handle(key, value, parent, path, depth):
        if depth == 0 and key in HEAD_KEYS or key in NON_TEXT_KEYS:
            return
        if key == "blocks" and isinstance(value, list):
            for i, block in enumerate(value):
                where = "%s[%d]" % (path, i)
                if not isinstance(block, dict) or block.get("type") not in ("h2", "h3", "p", "ul"):
                    ex.problems.append("%s: %s is not a block of type h2, h3, p or ul" % (file, where))
                elif block["type"] == "ul":
                    for j, item in enumerate(block["items"] if isinstance(block.get("items"), list) else []):
                        is_html = isinstance(item, dict)
                        emit("%s.items[%d]" % (where, j), item.get("html") if is_html else item, is_html, "li")
                else:
                    is_html = "html" in block
                    emit(where, block.get("html") if is_html else block.get("text"), is_html, block["type"])
        elif key == "services" and isinstance(value, list):
            button = content.get("button_label") if isinstance(content.get("button_label"), str) else BOOK_TEXT
            for i, service in enumerate(value):
                where = "%s[%d]" % (path, i)
                walk(service, where, depth + 1)
                title = service.get("title") if isinstance(service, dict) else None
                emit("button_label (card %d)" % (i + 1), button)
                if isinstance(title, str):
                    label("aria-label", BOOK_LABEL % (button, title), "button_label + %s.title" % where)
        elif key == "button_label" and isinstance(content.get("services"), list):
            pass                                        # printed in every card, see above
        elif key == "social" and isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    label("aria-label", item.get("label"), "%s[%d].label" % (path, i))
                    if isinstance(item.get("href"), str):
                        ex.links.append(ContentLink("main", item["href"].strip(), "", norm(item.get("label") or ""),
                                                    "%s: %s[%d]" % (file, path, i)))
        elif key == "fields" and isinstance(value, list):
            mark = parent.get("required_mark")
            for i, field in enumerate(value):
                if isinstance(field, dict):
                    emit("%s[%d].label" % (path, i), field.get("label"))
                    if field.get("required") and isinstance(mark, str):
                        emit("required_mark (after %s[%d].label)" % (path, i), mark)
        elif key == "sent_message":
            label("data-sent", value, path)
        elif key == "link_label":
            pass                                        # one label per photo, added below
        elif key == "map" and isinstance(value, dict):
            label("title", value.get("title"), path + ".title")
            for k, item in value.items():
                if k == "open_label" and isinstance(item, str):
                    # the link under the map (9 November 2026): not on Wix, it opens the Maps link of site.json
                    emit(path + ".open_label", item, intended="the Open in Google Maps link under the map is not on the Wix page, it is added on purpose")
                    maps = site.get("maps_href") if isinstance(site.get("maps_href"), str) else MAPS
                    ex.links.append(ContentLink("main", maps.strip(), norm(item), "", "%s: %s.open_label" % (file, path)))
                elif k not in ("title", "query"):
                    handle(k, item, value, "%s.%s" % (path, k), depth + 1)
        elif key == "errors" and isinstance(value, dict):
            pass                                        # shown by the script only, written into the page as data attributes
        elif key == "hours" and isinstance(parent.get("marquee_repeat"), int) and isinstance(value, str):
            count = max(1, parent["marquee_repeat"])
            for i in range(count):
                emit("%s (copy %d of %d)" % (path, i + 1, count), value)
            label("aria-label", HOURS_LABEL % norm(value), path)
        elif key == "address" and slug == "home" and isinstance(value, str):
            ex.piece(ex.main, "", "the pin the build contract puts in front of the address (section 7)", PIN)
            emit(path, value)
            maps = site.get("maps_href") if isinstance(site.get("maps_href"), str) else MAPS
            ex.links.append(ContentLink("main", maps.strip(), norm(value), "", "%s: %s, a Maps link by section 7 of the build contract" % (file, path)))
        elif key == "phone" and slug == "home" and isinstance(value, str):
            emit(path, value)
            tel = site.get("tel_href") if isinstance(site.get("tel_href"), str) else TEL
            ex.links.append(ContentLink("main", tel.strip(), norm(value), "", "%s: %s, a phone link by section 7 of the build contract" % (file, path)))
        elif isinstance(value, dict) and isinstance(value.get("label"), str) and isinstance(value.get("path"), str):
            emit(path + ".label", value["label"])       # a button: a text and where it leads
            ex.links.append(ContentLink("main", content_target(value["path"]), norm(value["label"]), "", "%s: %s" % (file, path)))
        elif isinstance(value, str):
            intended = None
            if slug == "book-online" and path == "closing_note_html":
                intended = "the closing booking note is not on the Wix page, it is kept from the first version of the site"
            emit(path, value, key.endswith("_html") or key == "html", None, intended)
        else:
            walk(value, path, depth + 1)

    walk(content, "", 0)

    if slug == "gallery" or isinstance(content.get("link_label"), str):
        template = content.get("link_label") if isinstance(content.get("link_label"), str) else GALLERY_LABEL
        for i in range(len(ex.slots)):
            label("aria-label", template.replace("{n}", str(i + 1)).replace("{total}", str(len(ex.slots))), "link_label")
    if slug == "home":
        ex.labels.append(("aria-label", PHOTO_ROW_LABEL, "build contract, section 7"))

    # The h1: the contract fixes its key (fifth in the file), not its place on the page.
    if ex.h1 is None:
        return
    same = next((p for p in ex.main if p.key == H1_IS_ALSO.get(slug)), None)
    if same is not None and same.text == ex.h1:
        same.kind, same.key = "h1", "h1 (stored again as %s)" % same.key
        return
    if same is not None:
        ex.problems.append('%s: h1 is "%s" but %s is "%s". The two keys hold the one heading of the page and must be the same text'
                           % (file, ex.h1, same.key, same.text))
    after = next((i for i, p in enumerate(ex.main) if p.key == H1_COMES_AFTER.get(slug)), None)
    made = Piece(file, "h1", ex.h1, (), [ex.h1], "h1", "main", None)
    ex.main.insert(0 if after is None else after + 1, made)


def expect_shell(ex, site, year):
    """Skip link, navigation and footer (contract, section 6) from content/site.json."""
    def need(dotted, kind=str):
        value = site
        for part in dotted.split("."):
            value = value.get(part) if isinstance(value, dict) else None
        if not isinstance(value, kind) or (kind is str and not norm(value)):
            ex.problems.append("%s: %s is missing or is not %s" % (SITE_FILE, dotted, "a text" if kind is str else "a list"))
            return None
        return value

    def label(attr, text, key):
        if isinstance(text, str) and norm(text):
            ex.labels.append((attr, norm(text), "%s: %s" % (SITE_FILE, key) if key else "build contract, section 6"))

    def link(place, target, text, name, key):
        if isinstance(target, str) and target.strip():
            ex.links.append(ContentLink(place, content_target(target), norm(text or ""), norm(name or ""), "%s: %s" % (SITE_FILE, key)))

    ex.piece(ex.top, SITE_FILE, "skip_link", need("skip_link") or "", place="top")
    label("aria-label", need("logo_label"), "logo_label")
    link("header", "/", "", site.get("logo_label"), "logo_label")
    label("aria-label", MENU_LABEL, None)
    label("aria-label", NAV_LABEL, None)
    for i, item in enumerate(need("nav", list) or []):
        if isinstance(item, dict):
            ex.piece(ex.header, SITE_FILE, "nav[%d].label" % i, item.get("label"), place="header")
            link("header", item.get("path"), item.get("label"), "", "nav[%d]" % i)
    # The Call button at the bottom of the screen on phones (9 November 2026): its words, a space, the phone number.
    call = " ".join(x for x in (need("call_bar_label") or "", need("phone") or "") if x)
    ex.piece(ex.footer, SITE_FILE, "call_bar_label (then the phone number)", call, place="footer",
             intended="the Call button at the bottom of the screen on phones is not on the Wix site, it is added on purpose")
    link("footer", need("tel_href"), call, "", "call_bar_label")
    ex.piece(ex.footer, SITE_FILE, "footer.name", need("footer.name") or "", place="footer")
    ex.piece(ex.footer, SITE_FILE, "footer.role", need("footer.role") or "", place="footer")
    for i, item in enumerate(need("social", list) or []):
        if isinstance(item, dict):
            label("aria-label", item.get("label"), "social[%d].label" % i)
            link("footer", item.get("href"), "", item.get("label"), "social[%d]" % i)
    ex.piece(ex.footer, SITE_FILE, "phone", need("phone") or "", place="footer")
    link("footer", need("tel_href"), site.get("phone"), "", "tel_href")
    ex.piece(ex.footer, SITE_FILE, "email", need("email") or "", place="footer")
    link("footer", need("mailto_href"), site.get("email"), "", "mailto_href")
    for i, line in enumerate(need("address_lines", list) or []):
        ex.piece(ex.footer, SITE_FILE, "address_lines[%d]" % i, line, place="footer")
    for i, item in enumerate(need("footer.policy_links", list) or []):
        if isinstance(item, dict):
            ex.piece(ex.footer, SITE_FILE, "footer.policy_links[%d].label" % i, item.get("label"), place="footer")
            link("footer", item.get("path"), item.get("label"), "", "footer.policy_links[%d]" % i)
    line = " ".join(x for x in (COPYRIGHT_SIGN, year, need("copyright") or "") if x)
    ex.piece(ex.footer, SITE_FILE, "copyright (after the copyright sign and the year)", line, place="footer",
             intended="the copyright line is not on the Wix site, it is added on purpose")


def expect(slug, content, site, year):
    ex = Expected(slug)
    for key in ("title", "description", "h1"):
        value = content.get(key)
        if isinstance(value, str) and norm(value):
            setattr(ex, key, norm(value))
        else:
            ex.problems.append('%s: "%s" is missing or is not a text' % (ex.file, key))
    notes = content.get("notes")
    if not isinstance(notes, list):
        ex.problems.append('%s: "notes" is missing or is not a list' % ex.file)
        notes = []
    site_notes = site.get("notes") if isinstance(site.get("notes"), list) else []
    ex.notes = norm(" \n ".join(str(n) for n in list(notes) + list(site_notes)))
    expect_main(ex, content, site)
    expect_shell(ex, site, year)
    return ex


# ---------------------------------------------------------------- report entries

def entry(page, check, ok, expected, actual, evidence, owner, **more):
    e = {"page": page, "viewport": VIEWPORT, "check": check, "ok": bool(ok), "expected": expected,
         "actual": actual, "evidence": evidence, "owner": owner}
    e.update(more)
    return e


def page_file(slug):
    address = common.PAGES[slug]
    return address + "index.html" if address == "" or address.endswith("/") else address


# ---------------------------------------------------------------- the page against its content file

# Decision 33 of the build contract: (page, what, the Wix value, our value). Any other title is a difference.
CONTACT_TITLE = ("contact", "title", "Contact | Hairbygerta", "Contact | Hair & Makeup by Gerta, Staten Island NY")
# Online booking was dropped on 2 November 2026, so the Book Online page no longer asks visitors to book online.
# The Book Now buttons call 347-671-5095. Same shape as CONTACT_TITLE. Any other meta description is a difference.
BOOK_ONLINE_DESCRIPTION = (
    "book-online", "meta description",
    "Book hair and makeup appointments online with HairByGerta in Staten Island, NY. Reserve haircuts, color, balayage, "
    "keratin treatments, Brazilian blowouts and makeup in minutes.",
    "Call or text to book hair and makeup appointments with Gerta in Staten Island, NY. Haircuts, color, balayage, "
    "keratin treatments, Brazilian blowouts and makeup.")
# 9 November 2026: the Wix meta description of the home page read badly ("is a hair stylist Staten Island NY and makeup
# artist"), so it was rewritten. Same shape as CONTACT_TITLE.
HOME_DESCRIPTION = (
    "home", "meta description",
    "Hair & Makeup by Gerta is a hair stylist Staten Island NY and makeup artist specializing in balayage highlights, color, "
    "cuts, keratin treatments, Brazilian blowouts and soft, natural glam for every occasion.",
    "Gerta Lila, hair stylist and makeup artist at Le Vigne Hair Salon, Staten Island, NY. Balayage, color, cuts, keratin, "
    "Brazilian blowouts and natural makeup.")
# 9 November 2026, a typo: the comma after "high-quality" on the home page. (page, the Wix sentence, our sentence).
HOME_EXTENSIONS = ("home",
                   "I work with high-quality, hair extensions that blend naturally with your own hair, so they look and move like the real thing.",
                   "I work with high-quality hair extensions that blend naturally with your own hair, so they look and move like the real thing.")
# For the same reason the Privacy Policy no longer names a booking system: (page, the Wix list item, our list item).
# Any other rewording of that list item is a difference.
PRIVACY_SERVICE_PROVIDERS = ("english-privacy-policy",
                             "Service providers that help us operate the website and booking system",
                             "Service providers that help us operate the website")
# 12 November 2026: the four policy pages carry the business name that the other pages use in their titles.
# Same shape as CONTACT_TITLE: (page, what, the Wix value, our value). Any other title is a difference.
POLICY_TITLES = (
    ("english-refund-policy", "title", "Refund Policy | Hairbygerta", "Refund Policy | Hair & Makeup by Gerta"),
    ("accessibility-statement", "title", "Accessibility Statement | Hairbygerta", "Accessibility Statement | Hair & Makeup by Gerta"),
    ("english-privacy-policy", "title", "Privacy Policy | Hairbygerta", "Privacy Policy | Hair & Makeup by Gerta"),
    ("terms-conditions", "title", "Terms and Conditions | Hairbygerta", "Terms and Conditions | Hair & Makeup by Gerta"),
)
# 12 November 2026: online booking was dropped on 2 November 2026, so the Terms & Conditions no longer speak of booking
# online or through the site. (page, the Wix sentence, our sentence). Any other rewording of these is a difference.
TERMS_PHONE_BOOKING = (
    ("terms-conditions",
     "By using this site or booking an appointment through it, you agree to these Terms & Conditions and to our Privacy Policy and Refund & Cancellation Policy.",
     "By using this site or booking an appointment, you agree to these Terms & Conditions and to our Privacy Policy and Refund & Cancellation Policy."),
    ("terms-conditions",
     "Appointments can be requested online, by phone, or in person.",
     "Appointments can be requested by phone or in person."),
    ("terms-conditions",
     "Submitting a booking request does not guarantee availability; your appointment is confirmed only after you receive a confirmation message from us.",
     "Requesting an appointment does not guarantee availability; your appointment is confirmed only after you receive a confirmation from us."),
)
# 12 November 2026: the Accessibility Statement carries the day it was last read again. (page, the Wix sentence, our sentence).
ACCESSIBILITY_UPDATED = ("accessibility-statement",
                         "This statement reflects our ongoing commitment to accessibility and was last updated on 11/28/2025.",
                         "This statement reflects our ongoing commitment to accessibility and was last updated on 11/12/2026.")


class Rules:
    """Which differences from the live Wix wording are intended. The list is fixed and lives in this class (and in the
    intended= marks of the extraction: copyright line, Hours block, closing booking note). Nothing else is intended."""

    def __init__(self, slug, ex):
        self.slug, self.ex = slug, ex
        self.by_key = {s: p.intended for p in ex.pieces if p.intended for line in p.lines for s in sentences(line)}
        self.first_block = set(s for p in ex.main[:2] if p.kind != "h1" for line in p.lines for s in sentences(line))
        self.last_heading = next((p.text for p in reversed(ex.main) if p.kind in HEADINGS), None)

    def noted(self, sentence):
        """A note in the content file never makes a difference intended: whoever writes the text could approve any
        change of wording by writing a note about it. Only the fixed list in this class counts. -> always None."""
        return None

    def in_notes(self, *sentences_):
        """For the evidence line only: do the notes of the content file talk about one of these sentences?"""
        return any(s and quoted_in_notes(s, self.ex.notes) for s in sentences_)

    def head(self, what, wix_value, our_value):
        """Why the title tag or the meta description may differ from the Wix one, or None. Only the cases below are on the list."""
        if (self.slug, what, wix_value, our_value) == CONTACT_TITLE:
            return 'build contract, section 10.33: the Contact page gets the new title (the Wix one is the automatic default)'
        if (self.slug, what, wix_value, our_value) == BOOK_ONLINE_DESCRIPTION:
            return "online booking was dropped on 2 November 2026 and the Book Now buttons call 347-671-5095"
        if (self.slug, what, wix_value, our_value) == HOME_DESCRIPTION:
            return "rewritten on 9 November 2026: the Wix text read badly (a hair stylist Staten Island NY and makeup artist)"
        if (self.slug, what, wix_value, our_value) in POLICY_TITLES:
            return "changed on 12 November 2026: the policy pages carry the business name that the other pages use in their titles"
        return None

    def reworded(self, w, o):
        """Why a sentence may read differently than on the Wix page, or None."""
        if self.slug == "contact" and (w, o) == ("Email", "Email *"):
            return "build contract, section 10.8: the Email label carries the mark of a required field"
        if (self.slug, w, o) == PRIVACY_SERVICE_PROVIDERS:
            return "online booking was dropped on 2 November 2026, so the site has no booking system"
        if (self.slug, w, o) == HOME_EXTENSIONS:
            return "typo fixed on 9 November 2026: no comma after high-quality"
        if (self.slug, w, o) in TERMS_PHONE_BOOKING:
            return "changed on 12 November 2026: online booking was dropped on 2 November 2026, appointments are booked by phone"
        if (self.slug, w, o) == ACCESSIBILITY_UPDATED:
            return "changed on 12 November 2026: the statement carries the day it was last read again"
        return None

    def removed(self, w, wix_rows):
        """Why a sentence of the Wix page may be missing on ours, or None."""
        if self.slug == "english-privacy-policy":
            if WIX_WORD.search(w):
                return "privacy rule: a sentence that names Wix is not carried over"
            if wix_rows.count(w) > 1 and self.last_heading == "Questions":
                return 'privacy rule: the heading Wix shows twice is "Questions" the second time'
            at = wix_rows.index(w) if w in wix_rows else 0
            if at and WIX_WORD.search(wix_rows[at - 1]) and re.match(r"(They|Their|It|Its)\b", w):
                return "privacy rule: it goes on about Wix, which the sentence before it names (%s)" % quote(wix_rows[at - 1], 60)
        return self.noted(w)

    def added(self, o):
        """Why a sentence of ours may be missing on the Wix page, or None."""
        if o in self.by_key:
            return self.by_key[o]
        if self.slug == "english-privacy-policy":
            low = o.lower()
            if is_phone_booking(o):
                return "privacy rule: appointments are booked by phone, online booking was dropped on 2 November 2026"
            if is_no_database(o) or "google maps" in low:
                return "privacy rule: one of the statements the brief asks for"
            if o == "Questions" and self.last_heading == "Questions":
                return 'privacy rule: the last heading is "Questions"'
        return self.noted(o)

    def moved(self, s):
        """Why a sentence may stand in another place than on the Wix page, or None."""
        if self.slug == "contact" and s in ("Phone", PHONE_TEXT, "Email", EMAIL):
            return "build contract, section 10.8: the info blocks come in the order Address, Phone, Email, Social Media, Hours"
        if self.slug == "accessibility-statement" and (s == self.ex.h1 or s in self.first_block):
            return "build contract, section 10.6: the markup keeps the h1 first, the stylesheet shows the first paragraph above it"
        return self.noted(s)


def rows_of(lines):
    """Lines as sentences. A sentence that only repeats the one before it is counted once. -> (rows, repeats)"""
    out, folded = [], collections.Counter()
    for row in (s for line in lines for s in sentences(line)):
        if out and out[-1] == row:
            folded[row] += 1
        else:
            out.append(row)
    return out, folded


def text_owner(pieces, page_lines, wix, rules):
    """Who is wrong when page and content file differ: CONTENT when the page shows the live Wix wording and the
    content file shows something else that is no intended difference, else PAGES."""
    if not wix or not page_lines:
        return "PAGES"
    known = wix_sentences(wix)
    page_is_wix = all(s in known for line in page_lines for s in sentences(line))
    content_fine = all(s in known or rules.added(s) for p in pieces for line in p.lines for s in sentences(line))
    return "CONTENT" if page_is_wix and not content_fine else "PAGES"


def order_owner(ex, page, wix, rules, part="main"):
    """Who is wrong when the order differs: CONTENT when the page has the order of the Wix page and the content
    file has another one, else PAGES."""
    if not wix:
        return "PAGES"
    in_content, on_page, on_wix = rows_of(ex.lines_in(part))[0], rows_of(page.lines_in(part))[0], rows_of(wix[part])[0]
    shared = set(in_content) & set(on_page) & set(on_wix)
    keep = lambda rows: [s for s in rows if s in shared and not rules.moved(s)]
    return "CONTENT" if keep(on_page) == keep(on_wix) != keep(in_content) else "PAGES"


def anchor(wanted, act):
    """Which texts stand on the page word for word and in order. wanted: the tokens of every text, act: the tokens
    of the page. -> for every text the place of its first token, or None. The chain that covers most words wins."""
    index = collections.defaultdict(list)
    for k, token in enumerate(act):
        index[token].append(k)
    states = []                                 # (score, -end, start, text number, state before)
    for i, toks in enumerate(wanted):
        n, fresh = len(toks), []
        for k in (index.get(toks[0], ()) if n else ()):
            if act[k:k + n] == toks:
                before = max((s for s in states if -s[1] <= k), key=lambda s: s[:2], default=None)
                fresh.append(((before[0] if before else 0) + n, -(k + n), k, i, before))
        states += fresh
    start = [None] * len(wanted)
    state = max(states, key=lambda s: s[:2], default=None)
    while state:
        start[state[3]] = state[2]
        state = state[4]
    return start


def compare_text(slug, ex, page, wix, rules):
    """text-in-order, no-extra-text and text-verbatim, with one entry per difference."""
    pieces, where = ex.pieces, page_file(slug)
    wanted = [[t for t, _, _ in tokens_of(p.text, p.marks)] for p in pieces]
    act = [t for t, _, _ in page.tokens]
    start = anchor(wanted, act)
    claimed = [False] * len(act)
    for toks, at in zip(wanted, start):
        if at is not None:
            claimed[at:at + len(toks)] = [True] * len(toks)

    def page_text(lo, hi):
        return page.text[page.tokens[lo][1]:page.tokens[hi - 1][2]] if hi > lo else ""

    def free_text(lo, hi):
        free = [k for k in range(lo, hi) if not claimed[k]]
        return (page_text(free[0], free[-1] + 1), free[0], free[-1] + 1) if free else ("", lo, lo)

    def names(group):
        return group[0].where + ("" if len(group) == 1 else " (and the %s after it)" % plural(len(group) - 1, "text"))

    def before(index):
        return 'after "%s"' % short(pieces[index - 1].text, 60) if index > 0 else "at the top of the page"

    # a text that is not in its place may stand somewhere else on the page
    moved = {}
    for i, toks in enumerate(wanted):
        if start[i] is None and toks:
            n = len(toks)
            at = next((k for k in range(len(act) - n + 1) if act[k] == toks[0] and act[k:k + n] == toks and not any(claimed[k:k + n])), None)
            if at is not None:
                claimed[at:at + n] = [True] * n
                moved[i] = at

    details, gaps = [], []                      # gaps: (first token, behind the last token, number of the text after it)
    i, prev_end = 0, 0
    while i < len(pieces):
        if start[i] is not None:
            gaps.append((prev_end, start[i], i))
            prev_end = start[i] + len(wanted[i])
            i += 1
            continue
        j = i
        while j < len(pieces) and start[j] is None:
            j += 1
        lo, hi = prev_end, (start[j] if j < len(pieces) else len(act))
        elsewhere = [k for k in range(i, j) if k in moved]
        rest = [pieces[k] for k in range(i, j) if k not in moved]
        if elsewhere:
            group, at = [pieces[k] for k in elsewhere], moved[elsewhere[0]]
            found = 'after "%s"' % short(page_text(max(0, at - 8), at), 60) if at > 0 else "at the top of the page"
            details.append(entry(slug, "text-order: " + names(group), False,
                                 "%s %s: %s" % (plural(len(group), "text"), before(i), " | ".join(quote(p.text, 80) for p in group)),
                                 "on the page, but in another place: " + found, where, order_owner(ex, page, wix, rules)))
        if rest:
            actual, first, last = free_text(lo, hi)
            expected = " | ".join(quote(p.text, 400) for p in rest)
            if actual:
                claimed[first:last] = [True] * (last - first)
                lines = page.lines_between(page.tokens[first][1], page.tokens[last - 1][2])
                details.append(entry(slug, "text-changed: " + names(rest), False, expected, quote(actual, 1200),
                                     "%s, %s. %s" % (where, before(i), word_diff(" ".join(p.text for p in rest), actual)),
                                     text_owner(rest, lines, wix, rules)))
            else:
                details.append(entry(slug, "text-missing: " + names(rest), False, expected,
                                     "not on the page (it belongs %s)" % before(i), where, "PAGES"))
        gaps.append((lo, hi, i))
        prev_end, i = hi, j
    gaps.append((prev_end, len(act), len(pieces)))

    extras = []
    for lo, hi, index in gaps:
        run = []
        for k in list(range(lo, hi)) + [None]:
            if k is not None and not claimed[k]:
                run.append(k)
            elif run:
                extras.append(entry(slug, "text-extra: %s" % before(index), False,
                                    "no text here: every text of the page comes from %s, %s or the build contract" % (ex.file, SITE_FILE),
                                    quote(page_text(run[0], run[-1] + 1), 1200), where, "PAGES"))
                run = []
    seen = collections.Counter()
    for e in details + extras:                  # two differences can carry the same name: number them
        seen[e["check"]] += 1
        if seen[e["check"]] > 1:
            e["check"] += " (%d)" % seen[e["check"]]

    verbatim = []
    for p, toks, at in zip(pieces, wanted, start):
        if at is not None:
            first = page.tokens[at][1]
            if page.text[first:first + len(p.text)] != p.text:
                verbatim.append('%s: content has %s, the page has %s'
                                % (p.where, quote(p.text, 300), quote(page_text(at, at + len(toks)), 300)))

    in_place = sum(1 for at in start if at is not None)
    out = [entry(slug, "text-in-order", not details,
                 "all %s of %s and of the header and footer in %s are on the page, in this order, nothing lost"
                 % (plural(len(pieces), "text"), ex.file, SITE_FILE),
                 "all %d found in order" % len(pieces) if not details else
                 "%s (%d of %d texts found in place)" % (plural(len(details), "difference"), in_place, len(pieces)),
                 where, "PAGES" if not details else collections.Counter(d["owner"] for d in details).most_common(1)[0][0])]
    out += details
    composed = [p.text for p in pieces if not p.file or p.key.startswith(("copyright", "call_bar"))]
    out.append(entry(slug, "no-extra-text", not extras,
                     "no visible text that is not in %s, in %s or fixed by the build contract" % (ex.file, SITE_FILE),
                     "none" if not extras else plural(len(extras), "text") + " that no content file holds",
                     "%s. Fixed by the build contract and allowed: %s" % (where, ", ".join(quote(t, 60) for t in composed) or "nothing"),
                     "PAGES"))
    out += extras
    out.append(entry(slug, "text-verbatim", not verbatim,
                     "every text is on the page letter for letter, spaces and punctuation included",
                     "all the same" if not verbatim else " ; ".join(verbatim), where, "PAGES"))
    return out


def compare_head(slug, ex, page, site):
    where, out = page_file(slug), []

    def one(check, wanted, found, what, key):
        if wanted is None:
            out.append(entry(slug, check, False, "the %s of %s" % (key, ex.file), "not checked: the content file has no " + key, ex.file, "CONTENT"))
        else:
            out.append(entry(slug, check, found == [wanted], '%s "%s"' % (what, wanted),
                             "no %s on the page" % what.split(" ", 1)[1] if not found else " | ".join(quote(f, 400) for f in found),
                             "%s, %s: %s" % (where, ex.file, key), "PAGES"))

    one("title", ex.title, page.titles, "one title tag", "title")
    one("meta-description", ex.description, page.descriptions, "one meta description", "description")
    one("h1", ex.h1, page.h1, "one h1", "h1")
    site_name = site.get("og_site_name") if isinstance(site.get("og_site_name"), str) else BUSINESS
    wanted = {"og:title": ex.title, "og:description": ex.description, "og:site_name": norm(site_name)}
    wrong = ['%s is %s, expected "%s"' % (k, " | ".join(quote(x) for x in page.og.get(k, [])) or "missing", v)
             for k, v in wanted.items() if v is not None and page.og.get(k, []) != [v]]
    if slug == "404":  # a noindex page carries no Open Graph tags at all
        wrong = ["%s is present on the noindex 404 page" % k for k in page.og if page.og.get(k)]
    out.append(entry(slug, "og-tags", not wrong, "og:title and og:description equal the title and the meta description, og:site_name is \"%s\"" % norm(site_name),
                     "as expected" if not wrong else "; ".join(wrong), where, "PAGES"))
    return out


def compare_labels(slug, ex, page):
    wanted = collections.Counter((attr, text) for attr, text, _ in ex.labels)
    found = collections.Counter((attr, text) for attr, text, _ in page.labels)
    known = set(text for _, text, _ in ex.labels) | set(p.text for p in ex.pieces)
    missing = wanted - found
    extra = found - wanted                      # a label too many, or a text no content file holds
    wrong = (['missing: %s "%s" (%s)' % (a, t, next(k for x, y, k in ex.labels if (x, y) == (a, t))) for (a, t) in missing.elements()]
             + ['not in a content file: %s "%s"' % (a, t) for (a, t) in extra.elements() if t not in known]
             + ['there %d times, expected %d: %s "%s"' % (found[(a, t)], wanted[(a, t)], a, t) for (a, t) in extra if (a, t) in wanted])
    listed = ['%s "%s"' % (attr, text) for attr, text, _ in page.labels]
    return [entry(slug, "screen-reader-labels", not wrong,
                  "every aria-label, alt, title and data-sent is a text of %s or %s, or a label the page module composes from it"
                  % (ex.file, SITE_FILE),
                  "%s, all known" % plural(len(listed), "label") if not wrong else "; ".join(wrong),
                  "%s. Labels on the page: %s" % (page_file(slug), " | ".join(listed) or "none"), "PAGES", labels=listed)]


def compare_links(slug, ex, page):
    unpin = lambda text: text[len(PIN):].strip() if text.startswith(PIN) else text
    free = [(l.place, resolve(slug, l.href), unpin(l.text), l.label) for l in page.links]
    wrong = []
    for want in ex.links:
        match = next((k for k, (place, target, text, name) in enumerate(free)
                      if place == want.place and target == want.target and text == want.text and (not want.label or name == want.label)), None)
        if match is not None:
            free.pop(match)
            continue
        shown = want.target[len(ORIGIN) - 1:] if want.target.startswith(ORIGIN) else want.target
        near = [l for l in page.links if l.place == want.place and (unpin(l.text), l.label) == (want.text, want.label or l.label)]
        wrong.append('%s: the link %s to %s is not in the %s%s'
                     % (want.where, quote(want.text or want.label), shown, PLACE_NAMES[want.place],
                        " (a link with this text leads to %s)" % near[0].href if near else ""))
    return [entry(slug, "links-from-content", not wrong,
                  "every link of %s and %s is on the page with the same text and the same target" % (ex.file, SITE_FILE),
                  "all %d there" % len(ex.links) if not wrong else "; ".join(wrong), page_file(slug), "PAGES")]


def compare_images(slug, ex, page):
    wanted = [(s.file, s.alt) for s in ex.slots]
    found = [(i.name, i.alt) for i in page.images if i.place == "main"]
    show = lambda rows: ", ".join(name + (' (alt "%s")' % alt if alt else "") for name, alt in rows) or "no photo"
    brief = list(BRIEF_IMAGES.get(slug, ()))        # the page has the order of the brief and the content file has not
    owner = "CONTENT" if brief and [name for name, _ in found] == brief != [name for name, _ in wanted] else "PAGES"
    return [entry(slug, "images-from-content", wanted == found,
                  "the photos in main are the image slots of %s, in order, each with the alt of its slot: %s" % (ex.file, show(wanted)),
                  "as expected" if wanted == found else show(found), page_file(slug), owner)]


def check_copyright(slug, page, site):
    lines = page.lines_in("footer")
    last = lines[-1] if lines else ""
    year_ok = bool(page.year and re.fullmatch(r"20\d\d", page.year))
    ok = year_ok and last == "%s %s %s" % (COPYRIGHT_SIGN, page.year, BUSINESS)
    owner = "CONTENT" if norm(site.get("copyright") or "") != BUSINESS else "PAGES"
    return [entry(slug, "copyright-line", ok,
                  'the footer ends with "%s <year> %s", the year inside an element with the attribute data-year' % (COPYRIGHT_SIGN, BUSINESS),
                  quote(last) + ("" if year_ok else ", no four-digit year in an element with data-year"),
                  "%s, %s: copyright" % (page_file(slug), SITE_FILE), owner)]


# ---------------------------------------------------------------- the facts of the brief

RE_BUSINESS = re.compile(r"\bhair\s*(?:&|and|\+|n|'n'|\u2019n\u2019)?\s*make[\s-]?up\s+by\s+gerta\b", re.I)
RE_GERTA = re.compile(r"\b(ol)?gerta\s+([a-z]+)", re.I)
RE_LILA = re.compile(r"\b([a-z]+)\s+lila\b", re.I)
RE_LEGAL = re.compile(r"\bolgerta\b", re.I)
RE_VIGNE = re.compile(r"\ble\s*vigne\b", re.I)
RE_STREET = re.compile(r"forest\s+av[a-z]*", re.I)
RE_CITY = re.compile(r"staten\s+island,?\s+(?:ny|n\.y\.|new\s+york)\.?,?\s+\d{5}(?:-\d{4})?", re.I)
RE_PHONE = re.compile(r"(?<![\w+-])(?:\+?1[\s.-]*)?\(?\d{3}\)?[\s.-]*\d{3}[\s.-]*\d{4}(?!\d)")
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+")
_DAY = r"\b(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*"
_TO = r"(?:\s*[-\u2013\u2014]\s*|\s+(?:to|through|thru|until|till)\s+)"
_TIME = r"(?<![\d:])\d{1,2}(?::\d{2})?\s*[ap]\.?m\b"
RE_DAYS = re.compile(_DAY + r"\.?" + _TO + _DAY, re.I)
RE_TIME = re.compile(_TIME, re.I)
RE_TIMES = re.compile(_TIME + _TO + _TIME, re.I)
RE_HOURS = re.compile(_DAY + r"\.?" + _TO + _DAY + r"\s*[,;:]?\s*" + _TIME + _TO + _TIME, re.I)
FACT_KINDS = (
    ("business", "fact-business-name", 'every mention of the business name is exactly "%s"' % BUSINESS),
    ("stylist", "fact-stylist-name", 'the name is exactly "%s"; "%s" is used on the Terms and Accessibility pages and nowhere else' % (STYLIST, LEGAL_NAME)),
    ("address", "fact-salon-address", 'salon and address are exactly "%s" and "%s"' % (SALON, ADDRESS)),
    ("phone", "fact-phone", 'the phone number is written "%s" and every phone link is %s' % (PHONE_TEXT, TEL)),
    ("email", "fact-email", 'the email address is written "%s" and every mail link is %s' % (EMAIL, MAILTO)),
    ("hours", "fact-hours", 'the hours are exactly "%s"' % HOURS),
    ("links", "fact-links", "the Facebook, Instagram and Maps links are exactly the three links of the brief"),
)


class View:
    """What one side says: the page as built, or the page as the content files describe it."""

    def __init__(self):
        self.units = []         # (where, text) of every text: head, lines, labels
        self.hrefs = []         # (where, address) of every link
        self.lines = {}         # place -> lines of text
        self.links = []         # (place, address, text)
        self.labels = set()     # (attribute, text)


def page_view(slug, page):
    v, where = View(), page_file(slug)
    for what, values in (("title", page.titles), ("meta description", page.descriptions)):
        v.units += [("%s, %s" % (where, what), x) for x in values]
    for prop, values in sorted(page.og.items()):
        if prop in ("og:title", "og:description", "og:site_name"):
            v.units += [("%s, %s" % (where, prop), x) for x in values]
    v.units += [("%s, %s" % (where, PLACE_NAMES[l.place]), l.text) for l in page.lines]
    v.units += [("%s, %s" % (where, attr), text) for attr, text, _ in page.labels]
    v.hrefs = [("%s, link %s" % (where, quote(l.text or l.label, 40)), l.href) for l in page.links]
    v.hrefs += [("%s, form data-mailto" % where, a) for a in page.forms if a.lower().startswith("mailto:")]
    v.lines = {place: page.lines_in(place) for place in ("top",) + PLACES}
    v.links = [(l.place, l.href, l.text) for l in page.links]
    v.labels = set((attr, text) for attr, text, _ in page.labels)
    return v


def content_view(ex):
    v = View()
    v.units += [("%s: %s" % (ex.file, key), value) for key, value in (("title", ex.title), ("description", ex.description)) if value]
    v.units += [(p.where, line) for p in ex.pieces for line in p.lines]
    v.units += [(key, text) for _, text, key in ex.labels]
    v.hrefs = [(l.where, l.target) for l in ex.links if not l.target.startswith(ORIGIN)]
    v.lines = {place: ex.lines_in(place) for place in ("top",) + PLACES}
    v.links = [(l.place, l.target, l.text) for l in ex.links]
    v.labels = set((attr, text) for attr, text, _ in ex.labels)
    return v


def scan_facts(slug, view):
    """Every place where a fact is written, or nearly written, must have it exactly. -> ({kind: [problem]}, {kind: mentions})"""
    problems, mentions = collections.defaultdict(list), collections.Counter()
    other = HOURS_OTHER_WORDING.get(slug, ())

    def bad(kind, found, why, where):
        text = '%s: "%s" %s' % (where, found, why)
        if text not in problems[kind]:
            problems[kind].append(text)

    for where, t in view.units:
        for m in RE_BUSINESS.finditer(t):
            mentions["business"] += 1
            if m.group(0) != BUSINESS:
                bad("business", m.group(0), 'is not exactly "%s"' % BUSINESS, where)
        for m in RE_GERTA.finditer(t):
            if similar(m.group(2).lower(), "lila") < 0.6:
                continue
            mentions["stylist"] += 1
            if m.group(0) != (LEGAL_NAME if m.group(1) else STYLIST):
                bad("stylist", m.group(0), 'is not exactly "%s"' % (LEGAL_NAME if m.group(1) else STYLIST), where)
        for m in RE_LILA.finditer(t):
            first = m.group(1).lower()
            if first not in ("gerta", "olgerta") and max(similar(first, "gerta"), similar(first, "olgerta")) >= 0.6:
                bad("stylist", m.group(0), 'is not exactly "%s"' % STYLIST, where)
        for m in RE_LEGAL.finditer(t):
            if slug not in LEGAL_NAME_PAGES:
                bad("stylist", t[m.start():m.start() + len(LEGAL_NAME)],
                    "is the legal name, which belongs on the Terms and Accessibility pages only", where)
            elif t[m.start():m.start() + len(LEGAL_NAME)] != LEGAL_NAME:
                bad("stylist", t[m.start():m.start() + len(LEGAL_NAME) + 4], 'is not exactly "%s"' % LEGAL_NAME, where)
        for m in RE_VIGNE.finditer(t):
            mentions["address"] += 1
            if t[m.start():m.start() + len(SALON)] != SALON:
                bad("address", t[m.start():m.start() + len(SALON) + 4], 'is not exactly "%s"' % SALON, where)
        for m in re.finditer(r"Hair Salon", t):
            if t[max(0, m.start() - 9):m.end()] != SALON:
                bad("address", t[max(0, m.start() - 12):m.end()], 'is not exactly "%s"' % SALON, where)
        for m in RE_STREET.finditer(t):
            mentions["address"] += 1
            if t[max(0, m.start() - 4):m.end()] != STREET:
                bad("address", t[max(0, m.start() - 6):m.end()], 'is not exactly "%s"' % STREET, where)
        for m in RE_CITY.finditer(t):
            if m.group(0) != CITY:
                bad("address", m.group(0), 'is not exactly "%s"' % CITY, where)
        for m in re.finditer(re.escape(STREET) + r"\s*,", t):
            if t[m.start():m.start() + len(ADDRESS)] != ADDRESS:
                bad("address", t[m.start():m.start() + len(ADDRESS) + 4], 'is not exactly "%s"' % ADDRESS, where)
        for m in RE_PHONE.finditer(t):
            mentions["phone"] += 1
            if m.group(0) != PHONE_TEXT:
                bad("phone", m.group(0), 'is not written "%s"' % PHONE_TEXT, where)
        for m in RE_EMAIL.finditer(t):
            mentions["email"] += 1
            if m.group(0) != EMAIL:
                bad("email", m.group(0), 'is not exactly "%s"' % EMAIL, where)
        for regex, exact, n in ((RE_HOURS, HOURS, 2), (RE_DAYS, HOURS_DAYS, 0), (RE_TIMES, HOURS_TIMES, 1)):
            for m in regex.finditer(t):
                mentions["hours"] += regex is not RE_HOURS      # a full line is counted as its days and its times
                if m.group(0) != exact and not (other and m.group(0) == other[n]):
                    bad("hours", m.group(0), 'is not exactly "%s"' % exact, where)
        for m in RE_TIME.finditer(t):
            if m.group(0) not in ("9 AM", "5 PM"):
                bad("hours", m.group(0), 'is not one of the opening times, written "9 AM" and "5 PM"', where)
    for where, href in view.hrefs:
        low = href.lower()
        parts = urllib.parse.urlsplit(href)
        host = (parts.hostname or "").lower()
        if low.startswith("tel:"):
            mentions["phone"] += 1
            if href != TEL:
                bad("phone", href, "is not exactly %s" % TEL, where)
        elif low.startswith("mailto:"):
            mentions["email"] += 1
            if href != MAILTO:
                bad("email", href, "is not exactly %s" % MAILTO, where)
        elif host.endswith(("facebook.com", "fb.com", "fb.me")):
            mentions["links"] += 1
            if href != FACEBOOK:
                bad("links", href, "is not the Facebook link %s" % FACEBOOK, where)
        elif host.endswith(("instagram.com", "instagr.am")):
            mentions["links"] += 1
            if href != INSTAGRAM:
                bad("links", href, "is not the Instagram link %s" % INSTAGRAM, where)
        elif (".google." in "." + host and parts.path.startswith("/maps")) or host.startswith("maps.") or host in ("goo.gl", "maps.app.goo.gl"):
            mentions["links"] += 1
            if href != MAPS:
                bad("links", href, "is not the Maps link %s" % MAPS, where)
    return problems, mentions


def required_facts(slug, view, built):
    """The places where a fact has to be (contract, sections 6 and 7). -> {kind: [problem]}"""
    problems = collections.defaultdict(list)

    def need(kind, ok, what):
        if not ok:
            problems[kind].append(what)

    def run(lines, wanted):
        return any(lines[k:k + len(wanted)] == list(wanted) for k in range(len(lines) - len(wanted) + 1))

    def has_link(place, href, text=None):
        return any(p == place and h == href and (text is None or t == text or t.endswith(text)) for p, h, t in view.links)

    foot, main = view.lines.get("footer", []), view.lines.get("main", [])
    need("stylist", STYLIST in foot, 'the footer does not show the name "%s"' % STYLIST)
    need("business", any(l.startswith(COPYRIGHT_SIGN) and l.endswith(BUSINESS) for l in foot),
         'the footer has no copyright line that ends with "%s"' % BUSINESS)
    need("address", run(foot, (SALON, STREET, CITY)), 'the footer does not show the three lines "%s", "%s", "%s"' % (SALON, STREET, CITY))
    need("phone", has_link("footer", TEL, PHONE_TEXT), 'the footer has no link %s with the text "%s"' % (TEL, PHONE_TEXT))
    need("email", has_link("footer", MAILTO, EMAIL), 'the footer has no link %s with the text "%s"' % (MAILTO, EMAIL))
    need("links", has_link("footer", FACEBOOK) and has_link("footer", INSTAGRAM), "the footer does not carry the Facebook link and the Instagram link")
    if slug == "home":
        need("business", BUSINESS in main, 'main does not show the site title "%s"' % BUSINESS)
        need("phone", has_link("main", TEL, PHONE_TEXT), 'main has no link %s with the text "%s"' % (TEL, PHONE_TEXT))
        need("address", SALON in main, 'main has no line "%s"' % SALON)
        need("address", has_link("main", MAPS, ADDRESS), 'main has no Maps link with the text "%s"' % ADDRESS)
        need("links", has_link("main", MAPS), "main does not carry the Maps link %s" % MAPS)
        need("hours", HOURS in main, 'main does not show the hours line "%s"' % HOURS)
        need("hours", ("aria-label", HOURS_LABEL % HOURS) in view.labels, 'no element is labelled "%s"' % (HOURS_LABEL % HOURS))
    if slug == "contact":
        need("phone", has_link("main", TEL, PHONE_TEXT), 'main has no link %s with the text "%s"' % (TEL, PHONE_TEXT))
        need("email", has_link("main", MAILTO, EMAIL), 'main has no link %s with the text "%s"' % (MAILTO, EMAIL))
        need("address", SALON in main and ADDRESS in main, 'main does not show the lines "%s" and "%s"' % (SALON, ADDRESS))
        need("hours", HOURS_DAYS in main and HOURS_TIMES in main, 'main does not show the lines "%s" and "%s"' % (HOURS_DAYS, HOURS_TIMES))
        need("links", has_link("main", FACEBOOK) and has_link("main", INSTAGRAM), "main does not carry the Facebook link and the Instagram link")
        if built is not None:
            need("email", built.forms == [MAILTO], "the contact form does not write to %s (form data-mailto: %s)" % (MAILTO, ", ".join(built.forms) or "none"))
            need("email", not any(built.form_actions), "the contact form has an action (%s): a mailto action makes browsers warn about an "
                 "insecure form, the script opens the email app from data-mailto instead (decision 41)" % ", ".join(a for a in built.form_actions if a))
    if slug in LEGAL_NAME_PAGES:
        need("stylist", any(LEGAL_NAME in l for l in main), 'main does not name "%s"' % LEGAL_NAME)
    if slug == "book-online" and built is not None:
        book = [l for l in built.links if l.book]
        wrong = [l.href for l in book if l.href != TEL]
        need("phone", book and not wrong, "the Book Now links (data-book) must call %s until the booking link is set: %s"
             % (TEL, ", ".join(wrong) or "no link with data-book found"))
    return problems


def check_facts(slug, ex, page):
    built, wanted = page_view(slug, page), content_view(ex)
    page_bad, mentions = scan_facts(slug, built)
    content_bad, _ = scan_facts(slug, wanted)
    page_need, content_need = required_facts(slug, built, page), required_facts(slug, wanted, None)
    out = []
    for kind, check, expected in FACT_KINDS:
        in_content = content_bad[kind] + content_need[kind]
        on_page = page_bad[kind] + page_need[kind]
        wrong = in_content + [p for p in on_page if p not in in_content]
        out.append(entry(slug, check, not wrong, expected,
                         ("%s on the page, all exact" % plural(mentions[kind], "mention") if mentions[kind] else "as expected")
                         if not wrong else "; ".join(wrong),
                         "%s, %s, %s" % (page_file(slug), ex.file, SITE_FILE), "CONTENT" if in_content else "PAGES"))
    return out


def check_site_facts(site, problem):
    if problem:
        return [entry(SITE_PAGE, "site-json-facts", False, "content/site.json holds the business facts of the brief", "not checked: " + problem, SITE_FILE, "CONTENT")]
    wanted = [("business_name", BUSINESS, False), ("stylist", STYLIST, False), ("salon", SALON, False),
              ("address_lines", [SALON, STREET, CITY], True), ("address_one_line", ADDRESS, False), ("phone", PHONE_TEXT, True),
              ("tel_href", TEL, True), ("email", EMAIL, True), ("mailto_href", MAILTO, True), ("hours", HOURS, False),
              ("maps_href", MAPS, False), ("footer.name", STYLIST, True), ("copyright", BUSINESS, True), ("og_site_name", BUSINESS, True)]
    wrong, checked = [], 0
    for dotted, fact, required in wanted:
        value, missing = site, False
        for part in dotted.split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                missing = True
        if missing:
            if required:
                wrong.append("%s is missing" % dotted)
            continue
        checked += 1
        if value != fact:
            wrong.append("%s is %s, the brief says %s" % (dotted, json.dumps(value, ensure_ascii=False), json.dumps(fact, ensure_ascii=False)))
    social = {s.get("name"): s.get("href") for s in site.get("social", []) if isinstance(s, dict)} if isinstance(site.get("social"), list) else {}
    for name, fact in (("Facebook", FACEBOOK), ("Instagram", INSTAGRAM)):
        checked += 1
        if social.get(name) != fact:
            wrong.append("the %s link in social is %s, the brief says %s" % (name, social.get(name) or "missing", fact))
    return [entry(SITE_PAGE, "site-json-facts", not wrong, "the business facts stored in content/site.json are exactly the facts of the brief",
                  "%d values, all exact" % checked if not wrong else "; ".join(wrong), SITE_FILE, "CONTENT")]


def order_entry(slug, check, what, brief, in_content, on_page, ex):
    """One list of the brief (services, photos) against the content file and against the page."""
    show = lambda rows: ", ".join(str(r) for r in rows) if rows else "none"
    content_ok = in_content is None or list(in_content) == list(brief)
    page_ok = list(on_page) == list(brief)
    if content_ok and page_ok:
        actual = "as the brief says"
    elif not content_ok:
        actual = "%s has: %s" % (ex.file, show(in_content)) + ("" if page_ok else ". The page has: " + show(on_page))
    else:
        actual = "the page has: " + show(on_page)
    return entry(slug, check, content_ok and page_ok, "%s, in this order: %s" % (what, show(brief)), actual,
                 "%s, %s" % (page_file(slug), ex.file), "PAGES" if content_ok else "CONTENT")


def names_in(nodes):
    return [image_name(i.attrs.get("src", "")) for n in nodes for i in ([n] if n.tag == "img" else find(n, "img"))]


def check_page_facts(slug, ex, page, content):
    """The services and the photo orders the brief gives."""
    slots = [s.file for s in ex.slots]
    out = []
    if slug == "book-online":
        row = lambda cells: " / ".join(fold(c if isinstance(c, str) else "(missing)") for c in cells)
        services = content.get("services") if isinstance(content.get("services"), list) else []
        in_content = [row(s.get(k) for k in ("title", "description", "duration", "price")) for s in services if isinstance(s, dict)]
        on_page = []
        for card in page.with_class("card"):
            cell = lambda tag, cls: next((norm(node_text(n)) for n in find(card, tag, cls)), None)
            on_page.append(row((cell("h2", None), cell(None, "desc"), cell(None, "duration"), cell(None, "price"))))
        out.append(order_entry(slug, "fact-services", "the ten services (title / description / duration / price)",
                               [row(s) for s in SERVICES], in_content, on_page, ex))
        out.append(order_entry(slug, "fact-service-images", "the photos of the ten service cards", SERVICE_IMAGES, slots,
                               names_in(page.with_class("card")), ex))
    elif slug == "gallery":
        links = [l for l in page.links if l.place == "main" and find(l.node, "img")]
        thumbs = [image_name(find(l.node, "img")[0].attrs.get("src", "")) for l in links]
        large = [image_name(l.href) for l in links]
        out.append(order_entry(slug, "fact-gallery-images", "the 21 gallery photos", GALLERY_IMAGES, slots, thumbs, ex))
        if thumbs != large:
            e = out[-1]
            e["ok"], e["owner"] = False, "PAGES" if e["owner"] == "PAGES" else e["owner"]
            e["actual"] += ". The links open other photos than the thumbnails show: " + ", ".join(large)
    elif slug == "about":
        left = names_in([n for n in page.with_class("left") if "col" in n.classes()])
        right = names_in([n for n in page.with_class("right") if "col" in n.classes()])
        side = lambda l, r: ["left: " + ", ".join(l), "right: " + ", ".join(r)]
        in_content = None
        if isinstance(content.get("photos_left"), list) and isinstance(content.get("photos_right"), list):
            pick = lambda rows: [r.get("file") for r in rows if isinstance(r, dict)]
            in_content = side(pick(content["photos_left"]), pick(content["photos_right"]))
        elif slots != list(ABOUT_LEFT + ABOUT_RIGHT):
            in_content = ["all: " + ", ".join(slots)]
        out.append(order_entry(slug, "fact-about-photos", "the About photos", side(ABOUT_LEFT, ABOUT_RIGHT), in_content, side(left, right), ex))
    elif slug == "home":
        row = names_in(page.with_class("photo-row"))
        meet = names_in(page.with_class("p1")) + names_in(page.with_class("p2"))
        split = lambda a, b: ["photo row: " + ", ".join(a), "Meet Gerta: " + ", ".join(b)]
        out.append(order_entry(slug, "fact-home-photos", "the home photo row and the Meet Gerta photos", split(HOME_ROW, HOME_MEET),
                               split(slots[:len(HOME_ROW)], slots[len(HOME_ROW):]), split(row, meet), ex))
    return out


# ---------------------------------------------------------------- the Privacy Policy page

NEGATION = re.compile(r"\b(?:no|not|never|without|neither|nor)\b|n['\u2019]t\b", re.I)
WIX_WORD = re.compile(r"\bwix\b", re.I)
WIX_CLAIM = re.compile(r"stor|cookie|data|server|host|platform|database|tool|app|analytic|collect|track|firewall", re.I)


def is_no_database(s):
    low = s.lower()
    return "database" in low and "visitor" in low and bool(NEGATION.search(low))


def is_phone_booking(s):
    """A sentence that says appointments are booked by phone and the website does not collect or store booking details.
    Online booking was dropped on 2 November 2026, so this takes the place of the old statement about the online
    booking provider."""
    low = s.lower()
    return "book" in low and "phone" in low and ("collect" in low or "store" in low) and bool(NEGATION.search(low))


def privacy_findings(rows):
    """rows: (kind, line) of main in reading order. -> the findings the three privacy checks need."""
    found = {"wix": [], "wix_other": [], "database": [], "booking": [], "cookies": {}, "google_fonts": [], "last_heading": None}
    lead = ""                                   # the last line that is not a list item: it introduces the list after it
    for kind, line in rows:
        if kind in HEADINGS:
            found["last_heading"] = line
        if kind != "li":
            lead = line
        context = line if kind != "li" else lead + " " + line
        for s in sentences(line):
            if WIX_WORD.search(s):
                claim = WIX_CLAIM.search(WIX_WORD.sub("", s)) or (kind == "li" and WIX_CLAIM.search(lead))
                found["wix" if claim else "wix_other"].append(s)
            if is_no_database(s):
                found["database"].append(s)
            if is_phone_booking(s):
                found["booking"].append(s)
        low = line.lower()
        if "cookie" in context.lower():
            if "google maps" in low and "contact page" in low:
                found["cookies"].setdefault("Google Maps on the Contact page", line)
        if "google fonts" in low:       # anywhere on the page, not only in the cookies list
            found["google_fonts"].append(line)
    return found


def check_privacy(slug, ex, page):
    where = "%s, %s" % (page_file(slug), ex.file)
    on_page = privacy_findings([(l.kind, l.text) for l in page.lines if l.place == "main"])
    in_content = privacy_findings([(p.kind, line) for p in ex.main for line in p.lines])
    owner = lambda content_ok: "PAGES" if content_ok else "CONTENT"
    out = []
    wix = on_page["wix"] or in_content["wix"]
    also = on_page["wix_other"]
    out.append(entry(slug, "privacy-no-wix-statement", not wix, "no sentence says that Wix stores data or sets cookies",
                     ("none" if not wix else " | ".join(quote(s, 300) for s in wix))
                     + ("" if not also else ". Wix is also named, without such a statement, in: " + " | ".join(quote(s, 200) for s in also)),
                     where, owner(not in_content["wix"])))
    for key, check, expected in (("database", "privacy-statement-no-visitor-database", "a sentence says that the site keeps no database of visitors"),
                                 ("booking", "privacy-statement-booking-by-phone", "a sentence says that appointments are booked by phone and that the website does not collect or store booking details")):
        ok = bool(on_page[key]) and bool(in_content[key])
        out.append(entry(slug, check, ok, expected, quote(on_page[key][0], 400) if on_page[key] else "no such sentence on the page",
                         where, owner(bool(in_content[key]))))
    # Since 2 November 2026 there is no online booking, so no booking provider is named here any more.
    # Since 9 November 2026 the fonts are files of the site itself (folder fonts), so Google Fonts is not named either:
    # a sentence that still names it says something that is no longer true.
    wanted = ("Google Maps on the Contact page",)
    lost = [w for w in wanted if w not in on_page["cookies"]]
    lost_content = [w for w in wanted if w not in in_content["cookies"]]
    stale, stale_content = on_page["google_fonts"], in_content["google_fonts"]
    out.append(entry(slug, "privacy-statement-third-party-cookies", not lost and not lost_content and not stale and not stale_content,
                     "the page says that Google Maps on the Contact page may set its own cookies, and it does not name Google Fonts "
                     "(the fonts are files of the site itself)",
                     ("not said about: " + ", ".join(lost)) if lost else
                     ("Google Fonts is still named: " + " | ".join(quote(s, 200) for s in (stale or stale_content))) if (stale or stale_content) else
                     " | ".join(quote(on_page["cookies"][w], 200) for w in wanted),
                     where, owner(not lost_content and not stale_content)))
    ok = on_page["last_heading"] == "Questions" and in_content["last_heading"] == "Questions"
    out.append(entry(slug, "privacy-last-heading", ok, 'the last heading of the page is "Questions"',
                     quote(on_page["last_heading"] or "no heading"), where, owner(in_content["last_heading"] == "Questions")))
    return out


# ---------------------------------------------------------------- the live Wix wording

def read_wix(slug):
    """wix-ref/<slug>.txt -> {title, description, main, footer, header} or None when there is no such file."""
    try:
        with open(os.path.join(common.WIX_REF, slug + ".txt"), encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeError):
        return None
    ref, section = {"title": None, "description": None, "main": [], "footer": [], "header": []}, None
    for raw in text.splitlines():
        marker = re.fullmatch(r"=== (\w+) ===", raw.strip())
        if marker:
            section = marker.group(1).lower()
        elif section is None:
            if raw.startswith("TITLE:"):
                ref["title"] = norm(raw[6:]) or None
            elif raw.startswith("DESCRIPTION:"):
                ref["description"] = None if norm(raw[12:]) in ("", "None") else norm(raw[12:])
        elif section in ref and norm(raw):
            ref[section].append(norm(raw))
    return ref


def wix_sentences(ref):
    return set(s for part in ("main", "footer", "header") for line in ref[part] for s in sentences(line))


def quoted_in_notes(sentence, notes):
    """Do the notes of the content file quote this sentence? A short one (under four words) must stand in quotes."""
    start = 0
    while True:
        at = notes.find(sentence, start)
        if at < 0:
            return False
        end = at + len(sentence)
        left, right = notes[at - 1:at], notes[end:end + 1]
        whole = not (left.isalnum() and sentence[:1].isalnum()) and not (right.isalnum() and sentence[-1:].isalnum())
        if whole and (len(sentence.split()) >= 4 or (left and left in QUOTES and right and right in QUOTES)):
            return True
        start = at + 1


def compare_wix(slug, ex, page, ref, rules):
    """One entry per sentence that differs from the live Wix page, and a summary."""
    where = "%s, wix-ref/%s.txt" % (page_file(slug), slug)
    details, compared, repeats = [], 0, []

    def comes_after(rows, s):
        at = rows.index(s)
        return "after %s" % quote(rows[at - 1], 80) if at else "first"

    def add(kind, wix_text, our_text, reason, owner):
        details.append(entry(slug, "wix-wording %02d: %s" % (len(details) + 1, kind), reason is not None,
                             "Wix: " + (wix_text or "(not on the Wix page)"),
                             "ours: " + (our_text or "(not on our page)"),
                             "%s. %s" % (where, "Intended: " + reason if reason else "Not on the fixed list of intended differences (docstring of this script)"
                                         + ("; the notes of %s mention it, but a note does not make a difference intended" % ex.file if rules.in_notes(*(m.group(1) for m in (re.match(r'"(.*)"', t or "") for t in (wix_text, our_text)) if m)) else "")),
                             owner, intended=reason is not None))

    # title and meta description
    for what, wix_value, ours, known in (("title", ref["title"], page.titles, ex.title), ("meta description", ref["description"], page.descriptions, ex.description)):
        our_value = ours[0] if ours else ""
        if wix_value is None:
            details.append(entry(slug, "wix-wording %02d: %s" % (len(details) + 1, what), True, "Wix: (the Wix page has no %s)" % what,
                                 "ours: " + quote(our_value, 600), where + ". Nothing to compare with", "CONTENT", intended=True, nothing_to_compare=True))
            continue
        compared += 1
        if our_value != wix_value:
            reason = rules.head(what, wix_value, our_value)
            add(what + " differs", quote(wix_value, 600), quote(our_value, 600) if our_value else "", reason, "CONTENT" if our_value == known else "PAGES")

    for part in ("main", "footer", "header"):
        wix_rows, wix_folded = rows_of(ref[part])
        our_rows, our_folded = rows_of(page.lines_in(part))
        content_rows, content_folded = rows_of(ex.lines_in(part))
        # The page shows what the content file says: CONTENT has to change. The page differs from its content file: PAGES.
        ours_from = lambda o: "CONTENT" if content_rows.count(o) >= our_rows.count(o) else "PAGES"
        lost_by = lambda w: "PAGES" if content_rows.count(w) > our_rows.count(w) else "CONTENT"
        for s in list(wix_folded) + [s for s in our_folded if s not in wix_folded]:
            theirs, ours, wanted = wix_folded.get(s, 0), our_folded.get(s, 0), content_folded.get(s, 0)
            if theirs > ours:           # a line that only repeats the line before it is compared once
                repeats.append((part, s, theirs, ours, "Wix repeats this text for screen readers, the page prints it once", "CONTENT"))
            elif ours > theirs:
                reason = "the content file asks for these copies (a scrolling line)" if wanted == ours else None
                repeats.append((part, s, theirs, ours, reason, "CONTENT" if wanted == ours else "PAGES"))
        compared += len(wix_rows)
        removed, added = [], []                         # (sentence, number of the stretch that differs)
        for n, (tag, i1, i2, j1, j2) in enumerate(difflib.SequenceMatcher(None, wix_rows, our_rows, autojunk=False).get_opcodes()):
            if tag != "equal":
                removed += [(w, n) for w in wix_rows[i1:i2]]
                added += [(o, n) for o in our_rows[j1:j2]]
        for w, n in list(removed):                      # the same sentence, in another place
            twin = next((x for x in added if x[0] == w), None)
            if twin is not None:
                removed.remove((w, n))
                added.remove(twin)
                add("%s order differs" % part, "%s comes %s" % (quote(w, 300), comes_after(wix_rows, w)),
                    "%s comes %s" % (quote(w, 300), comes_after(our_rows, w)), rules.moved(w), order_owner(ex, page, ref, rules, part))
        for near in (True, False):                      # a reworded sentence: the two side by side, neighbours first
            for w, n in list(removed):
                best = max((x for x in added if x[1] == n or not near), key=lambda x: similar(w, x[0]), default=None)
                if best is not None and similar(w, best[0]) >= 0.6:
                    removed.remove((w, n))
                    added.remove(best)
                    gone, new = rules.removed(w, wix_rows), rules.added(best[0])
                    reason = (gone if gone and new else None) or rules.reworded(w, best[0])
                    add("%s sentence differs" % part, quote(w, 600), quote(best[0], 600), reason, ours_from(best[0]))
        for w, _ in removed:
            also = " (Wix has it %s, our page %s)" % (plural(wix_rows.count(w), "time"), plural(our_rows.count(w), "time")) if w in our_rows else ""
            add("%s sentence of Wix is not on our page" % part, quote(w, 600) + also, "", rules.removed(w, wix_rows), lost_by(w))
        for o, _ in added:
            also = " (our page has it %s, Wix %s)" % (plural(our_rows.count(o), "time"), plural(wix_rows.count(o), "time")) if o in wix_rows else ""
            add("%s sentence is not on the Wix page" % part, "", quote(o, 600) + also, rules.added(o), ours_from(o))

    times = lambda n: "repeats the line before it %s" % plural(n, "time") if n else "never repeats the line before it"
    for part, s, theirs, ours, reason, owner in repeats:
        add("%s text repeated" % part, "%s %s" % (quote(s, 300), times(theirs)), "%s %s" % (quote(s, 300), times(ours)), reason, owner)
    bad = [d for d in details if not d["ok"]]
    differ = [d for d in details if not d.get("nothing_to_compare")]
    summary = entry(slug, "wix-wording", not bad,
                    "title, meta description, main text, footer and navigation are the live Wix wording, apart from the intended differences",
                    "%s compared with Wix: %s, %d intended, %d not" % (plural(compared, "sentence"), plural(len(differ), "difference"), len(differ) - len(bad), len(bad)),
                    where,
                    "PAGES" if not bad else collections.Counter(d["owner"] for d in bad).most_common(1)[0][0])
    return [summary] + details


# ---------------------------------------------------------------- where the pages and the content files come from

class Server:
    def __init__(self, base):
        self.base = base if base.endswith("/") else base + "/"
        self.opener = urllib.request.build_opener(*([urllib.request.ProxyHandler({})] if common.is_local(self.base) else []))

    def get(self, address):
        """-> (status or None, bytes, note)"""
        note = ""
        for _ in range(2):
            try:
                req = urllib.request.Request(self.base + address, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
                with self.opener.open(req, timeout=30) as r:
                    return r.status, r.read(), ""
            except urllib.error.HTTPError as e:
                return e.code, e.read(), ""
            except Exception as e:      # no str(e): it may carry a path from this computer
                note = "no answer (%s)" % type(e).__name__
        return None, b"", note


def load_json(folder, name):
    """-> (value, problem). The problem never carries a path from this computer."""
    try:
        with open(os.path.join(folder, name), encoding="utf-8") as f:
            value = json.load(f)
    except FileNotFoundError:
        return None, "content/%s is missing" % name
    except (OSError, UnicodeError) as e:
        return None, "content/%s cannot be read (%s)" % (name, type(e).__name__)
    except ValueError as e:
        return None, "content/%s is not valid JSON (%s)" % (name, e)
    if not isinstance(value, dict):
        return None, "content/%s is not a JSON object" % name
    return value, ""


def check_one(slug, server, content_dir, site, site_problem, wix_there):
    """Every check of one page."""
    where, file = page_file(slug), "content/%s.json" % slug
    status, body, note = server.get(common.PAGES[slug])
    # Only a page of this site is read: an empty answer, or the stock "not found" page of a host, is not.
    ours = (status == 200 or (slug == "404" and status == 404)) and OWN_MARK in body
    out = [entry(slug, "page-loads", ours, "status 200" + (" (or 404 for the 404 page)" if slug == "404" else "") + " and a page of this site",
                 note or "status %s%s" % (status, "" if ours or status != 200 else ", but the answer is empty or is not a page of this site"),
                 where, "PAGES")]
    content, problem = load_json(content_dir, slug + ".json")
    problem = problem or site_problem
    if problem:
        out.append(entry(slug, "content-file", False, "%s and %s are JSON objects" % (file, SITE_FILE), problem, file, "CONTENT"))
    if not ours or problem:
        out.append(entry(slug, "text-in-order", False, "every text of %s is on the page, in the same order" % file,
                         "not checked: " + (problem or "the page did not load"), where, "CONTENT" if problem else "PAGES"))
        return out
    page = Page(slug, body.decode("utf-8-sig", "replace"))
    year = page.year if page.year and re.fullmatch(r"20\d\d", page.year) else ""
    ex = expect(slug, content, site, year)
    out.append(entry(slug, "content-file", not ex.problems, "%s has a title, a description, an h1 and notes, and every text key holds a text" % file,
                     "as expected, %s" % plural(len(ex.main), "text") if not ex.problems else "; ".join(ex.problems), file, "CONTENT"))
    ref = read_wix(slug) if wix_there and slug != "404" else None
    rules = Rules(slug, ex)
    out += compare_head(slug, ex, page, site)
    out += compare_text(slug, ex, page, ref, rules)
    out += compare_labels(slug, ex, page)
    out += compare_links(slug, ex, page)
    out += compare_images(slug, ex, page)
    out += check_copyright(slug, page, site)
    out += check_facts(slug, ex, page)
    out += check_page_facts(slug, ex, page, content)
    if slug == "english-privacy-policy":
        out += check_privacy(slug, ex, page)
    if ref:
        out += compare_wix(slug, ex, page, ref, rules)
    elif wix_there and slug != "404":
        out.append(entry(slug, "wix-wording", True, "the text is the live Wix wording, apart from the intended differences",
                         "skipped: the reference folder has no file %s.txt" % slug, "wix-ref/%s.txt" % slug, "QA", skipped=True))
    return out


def main(argv=None):
    ap = common.cli_parser(
        "The words of every page against its content file, the business facts and the live Wix wording. No browser.",
        viewport_help="accepted because every QA script takes it; not used, the words do not depend on a screen size")
    ap.add_argument("--show-intended", action="store_true", help="also print the intended differences from the Wix wording")
    ap.add_argument("--root", help="self-test only: serve this copy of the site and read its content folder")
    ap.add_argument("--out", help="self-test only: write the report into this folder")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    slugs = common.cli_pages(ap, args.page)

    site_dir = os.path.abspath(args.root) if args.root else common.SITE
    content_dir = os.path.join(site_dir, "content")
    out_dir = args.out or (os.path.join(common.ENV, "stage", "qa", NAME, "out") if args.root else None)
    if out_dir:
        common.REPORTS = os.path.join(os.path.abspath(out_dir), "reports")

    started = time.time()
    site, site_problem = load_json(content_dir, "site.json")
    wix_there = os.path.isdir(common.WIX_REF)
    results = check_site_facts(site or {}, site_problem)
    if not wix_there:
        results.append(entry(SITE_PAGE, "wix-wording", True, "the text of the nine pages is compared with the live Wix wording",
                             "skipped: the folder with the Wix reference files (wix-ref in the tools folder next to the site folder) is not there",
                             "wix-ref", "QA", skipped=True))
    with (common.site_server(root=site_dir) if args.root else common.target_base(args.base)) as base:
        server = Server(base)
        for slug in slugs:
            try:
                results += check_one(slug, server, content_dir, site or {}, site_problem, wix_there)
            except Exception as e:      # a page that is half written must not stop the other pages
                tb = e.__traceback__
                while tb is not None and tb.tb_next is not None:
                    tb = tb.tb_next
                results.append(entry(slug, "script-error", False, "the page can be checked",
                                     "check_content.py failed on this page: %s (line %s of the script)" % (type(e).__name__, tb.tb_lineno if tb else "?"),
                                     page_file(slug), "QA"))
    tested = "self-test copy" if args.root else common.report_base(args.base)
    failed = [r for r in results if not r["ok"]]
    intended = [r for r in results if r.get("intended") and not r.get("nothing_to_compare")]
    extra = {"script": "qa/%s.py" % NAME, "content_files": "content folder of the site on this computer",
             "wix_reference": "compared" if wix_there else "skipped, the folder is not there",
             "last_run": {"pages": slugs, "checks": len(results), "failed": len(failed), "intended_differences_from_wix": len(intended),
                          "seconds": round(time.time() - started, 1)}}
    doc = common.save_report(NAME, results, tested, extra, replace=set(slugs) | {SITE_PAGE})

    for r in failed:
        line = "FAIL [%s] %s | %s | expected: %s | actual: %s" % (r["owner"], r["page"], r["check"], r["expected"], r["actual"])
        print(line if len(line) <= 460 else line[:457] + "...")
    if args.show_intended:
        for r in intended:
            line = "intended %s | %s | %s | %s | %s" % (r["page"], r["check"], r["expected"], r["actual"], r["evidence"])
            print(line if len(line) <= 460 else line[:457] + "...")
    owners = collections.Counter(r["owner"] for r in failed)
    by_owner = " (%s)" % ", ".join("%s %d" % (o, n) for o, n in sorted(owners.items())) if owners else ""
    report = "qa/reports/%s.json" % NAME if not out_dir else "reports/%s.json in the folder given with --out" % NAME
    print("%s: %s on %s, %d failed%s, %s from the Wix wording, Wix reference %s%s. Report: %s"
          % (NAME, plural(len(results), "check"), plural(len(slugs), "page"), len(failed), by_owner,
             plural(len(intended), "intended difference"), "compared" if wix_there else "skipped (folder not there)",
             "" if doc["ok"] or failed else " (the report still holds older failures of pages not run this time)", report))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
