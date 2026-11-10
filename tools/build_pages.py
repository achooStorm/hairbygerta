#!/usr/bin/env python3
r"""Build the HTML pages of hairbygerta.com.

    python tools/build_pages.py                       build every page
    python tools/build_pages.py --only home,gallery   build only these pages and write nothing else
    python tools/build_pages.py --list                show the page table
    python tools/build_pages.py --out DIR             for testing: write the pages into DIR, not into the site folder
    python tools/build_pages.py --pages-dir DIR       for testing: load the page modules from DIR, not from tools/pages

It needs Python 3 and nothing else (standard library only). It can be started from any folder, because every
path is worked out from where this file is. Exit code 0 when all went well. Exit code 1, with a message that
names the file and the key, when something is missing or wrong. A page with a problem is not written, the
other pages are. The same input always gives the same files, byte for byte (UTF-8, LF line endings).

WHERE THINGS ARE (all inside the site folder, one level above this file)

    content/site.json        the text every page shares: navigation, footer, phone, address, social links
    content/<slug>.json      the text of one page
    image-manifest.json      the pixel size of every image file. A photo that replaced a placeholder is measured
                             from its two files instead, and the script then writes that photo into this
                             file by itself (see the note above the list PLACEHOLDERS, right below). That is
                             the only thing the script ever changes in it.
    seo/jsonld-home.json     data for search engines, copied into the head of the home page (may be absent)
    tools/pages/<name>.py    one page module per page: turns the content of that page into the HTML inside <main>
    tools/build_pages.py     this file: the page table, the shared head, header and footer, and the helpers

The HTML files are only ever made by this script. To change a text, edit the content file and run the script
again. To swap a placeholder photo for a real one, follow the steps above the list PLACEHOLDERS, right below
this note. This script does not write sitemap.xml or robots.txt.

==========================================================================================================
HOW TO WRITE A PAGE MODULE
==========================================================================================================

A page module is a plain Python file in tools/pages/ (the file name is in the page table, see --list) with
two things in it:

    SLUG = "english-refund-policy"          # the slug of the page, exactly as in the page table

    def render(ctx):
        c = ctx.content
        body = "\n".join([
            '<article class="legal">',
            "  <h1>%s</h1>" % ctx.esc(c["h1"]),
            ctx.blocks(c["blocks"]),
            "</article>",
        ])
        return {"body": body, "head_extra": ""}

render(ctx) returns a dict with these keys (any other key is an error):

    "body"        Needed. The HTML that goes between <main id="main"> and </main>. Section 7 of
                  tools/CONTRACT.md lists the elements and classes each page must have. Exactly one <h1>.
    "head_extra"  Optional. Markup added at the very end of <head>.
    "head_first"  Optional. Markup placed right after the viewport meta, before the title and every link.
                  Only the 404 page needs it, for the small script that sets <base>. Two things to know
                  about a <base>: href="#main" of the skip link then leads to the base address and no
                  longer to this page, so that script must also repoint a.skip to the address the visitor
                  is on. And on a deep broken address the browser asks for css/style.css, js/site.js and
                  images/logo.jpg next to the broken address before any script has run (its preloader does
                  not wait). Those few 404 answers are harmless, the page then loads all three correctly.
    "robots"      Optional. The text of <meta name="robots" content="...">. With "noindex" the page also gets
                  no canonical link and no Open Graph tags. Only the 404 page uses it.

The script does the rest: doctype, head (the title tag and the meta description come from "title" and
"description" in the content file), skip link, header with logo, menu button and navigation, footer and the
script tag. A module never writes those and never reads a file itself. Everything it needs is in ctx.

ctx.slug       "gallery"
ctx.path       "/gallery/", the address of the page on the site ("/" for home, "/404.html" for the 404 page)
ctx.root       the way from this page up to the top of the site: "" for index.html and 404.html,
               "../" for a page that lives in a folder
ctx.content    content/<slug>.json as a dict. Reading a key that is not there stops the build with a message
               that names the file and the key (for example: content/home.json: key "hero.welcome" is
               missing). So write ctx.content["hero"]["welcome"] and do not guard it. Use .get() only for a
               key that is truly optional.
ctx.site       content/site.json, same behaviour: ctx.site["phone"], ctx.site["tel_href"], ctx.site["email"],
               ctx.site["mailto_href"], ctx.site["hours"], ctx.site["maps_href"], ctx.site["salon"], ...
ctx.manifest   image-manifest.json, same behaviour: ctx.manifest["images"]["g12"]["width"]

ctx.esc(text) -> str
    Makes plain text safe for HTML: & < > and " become entities. Use it for EVERY piece of text that you put
    into the page yourself, inside an element or inside an attribute, and always write attribute values in
    double quotes:
        '<h1 class="serif">%s</h1>' % ctx.esc(c["h1"])
        '<a class="addr" href="%s" target="_blank" rel="noopener">' % ctx.esc(ctx.site["maps_href"])
    Content files hold real characters (a curly apostrophe, an en dash, a plain &), never entities, and
    straight and curly apostrophes stay exactly as the content file has them. Numbers are accepted. Do NOT
    use it on what ctx.inline, ctx.blocks, ctx.img and ctx.social return: that is finished HTML.

ctx.url(site_path) -> str
    Turns an address that starts at the top of the site into a relative address that works from this page.
        on /gallery/ :      ctx.url("/")                 -> "../"
                            ctx.url("/book-online/")     -> "../book-online/"
                            ctx.url("/images/g01.jpg")   -> "../images/g01.jpg"
        on the home page :  ctx.url("/")                 -> "./"
                            ctx.url("/gallery/")         -> "gallery/"
    An address with a scheme (https:, mailto:, tel:) or one that starts with # comes back unchanged, so a
    "path" or "href" taken from a content file can always be passed through it. Anything else that does not
    start with / is an error. Never type an internal address by hand, neither "/gallery/" nor "../gallery/".
    The site must work at achoostorm.github.io/hairbygerta/ and at www.hairbygerta.com, and only relative
    addresses do. The result is plain text: none of the site's own paths needs escaping, an address from a
    content file goes through ctx.esc as well, ctx.esc(ctx.url(x)).

ctx.inline(html) -> str
    For the content keys whose name ends in _html and for values written {"html": "..."}. Such a text may hold
    <a>, <br>, <strong> and <em> and nothing else. The helper keeps those tags, escapes the text between them
    (a plain & becomes &amp;), swaps {{root}} for ctx.root and makes an href that starts with / relative, so
    href="{{root}}english-privacy-policy/" works from every page. A link with target="_blank" gets
    rel="noopener" if it has none. Any other tag, a style or on... attribute, or a tag that is not closed
    stops the build.
        '<p class="contact-intro">%s</p>' % ctx.inline(c["intro_html"])
    A list in a content file may mix plain strings and {"html": ...} items. Handle that as
        ctx.inline(item["html"]) if isinstance(item, dict) else ctx.esc(item)

ctx.blocks(blocks) -> str
    Renders the "blocks" list of a policy page, one element per block, joined with line breaks, not indented:
        {"type": "h2", "text": "..."}                      -> <h2>...</h2>
        {"type": "h3", "text": "..."}                      -> <h3>...</h3>
        {"type": "p", "text": "..."}                       -> <p>...</p>       plain text, escaped
        {"type": "p", "html": "..."}                       -> <p>...</p>       through ctx.inline
        {"type": "ul", "items": ["...", {"html": "..."}]}  -> <ul> with one <li> per item on its own line
    Any other type or key stops the build with the file and the block named.

ctx.img(name, alt="", width=None, height=None, lazy=True, variant="full", sizes=None) -> str
    The one way to put a photo on a page. name is the file name without folder and extension ("g12"), which
    is the "file" of an image slot in the content file. It must be listed in image-manifest.json.
        variant="full"  src is images/NAME.jpg, with a srcset of the small copy and the full file (their real
                        pixel widths from the manifest) and a sizes attribute. For photos that are shown large.
        variant="sm"    src is images/sm/NAME.jpg and nothing else. For thumbnails and cards.
        alt             the "alt" of the slot. A name in PLACEHOLDERS always gets alt="" and class="ph",
                        whatever is passed, so pass slot["alt"] and never test for placeholders yourself.
                        A photo that is not a placeholder needs a description: an empty alt gives a WARNING
                        line that names the content file and the photo.
        width, height   the size the photo is shown at on the desktop page, written as the width and height
                        attributes (they keep the space free while the photo loads, the stylesheet does the
                        real sizing). Leave both out to get the real pixel size of the chosen file. Give
                        only one and the other follows from the shape of the file.
        lazy            True writes loading="lazy". Pass lazy=False for a photo that is on screen as soon as
                        the page opens (it then gets loading="eager").
        sizes           the sizes attribute: how wide the photo is on screen. For variant "full" it is
                        "(max-width: 760px) 100vw, <width>px" when left out. For variant "sm" it only
                        matters for a photo with a WebP copy, see below. Ignored when there is no srcset.
    The result is one line, for example ctx.img("g01", slot["alt"], 288, 545) on the home page gives
        <img class="ph" src="images/g01.jpg" srcset="images/sm/g01.jpg 800w, images/g01.jpg 1600w"
             sizes="(max-width: 760px) 100vw, 288px" alt="" width="288" height="545" loading="lazy"
             decoding="async">
    Only when the manifest lists a WebP copy of the image (today g12 and g13) the result is wrapped as
        <picture><source type="image/webp" srcset="..."><img ...></picture>
    so the direct child of a link or a box around a photo can be a picture element instead of an img. For
    variant "sm" the WebP source is the small WebP file. When sizes is given it offers the small and the full
    WebP file with their pixel widths, so a sharp or very wide screen gets the larger one, while the JPEG
    img stays the small copy. There is no srcset when the small copy is not smaller than the full file
    (svc-haircut) or does not exist (logo).
    The pixel sizes come from image-manifest.json. The one exception is a photo that replaced a placeholder
    (its name is no longer in PLACEHOLDERS, and the manifest calls it a placeholder or an owner-photo): its
    sizes are read from images/NAME.jpg and images/sm/NAME.jpg themselves, which must be JPG files.

ctx.is_placeholder(name) -> bool
    True when name is in PLACEHOLDERS. ctx.img already takes care of placeholders, so this is rarely needed.

ctx.social(links=None, icons="disc") -> str
    The <div class="social"> with one icon link per network (svg icon, aria-label, target="_blank",
    rel="noopener"), the same markup as in the footer. Without an argument it uses "social" from
    content/site.json. The Contact page passes its own list of the same shape (name, href, label). Icons
    exist for Facebook and Instagram, each in two drawings of the same 23 x 23 px:
        icons="disc"    a filled disc with the sign cut out of it, as in the footer
        icons="bare"    the sign alone, a letter f and the outline of a camera, as in the Social Media
                        item of the Contact page
    (This helper is an addition to the list in section 5 of the contract.)

RULES FOR A PAGE MODULE

  - Standard library only, no import from another page module, no file reading, nothing that changes from
    run to run (no dates, no random numbers).
  - The text of the page comes from ctx.content and ctx.site. A module types a text itself only where
    section 7 of the contract fixes it (an aria-label, for example) and no content key holds it.
  - The body starts at the left edge, nested elements are indented by two spaces, lines are joined with
    "\n", no blank line at the start or the end.
  - Before a page is written the script checks the finished page and stops with a message when it finds
    a number of <h1> other than one, a style attribute, an address that starts with / or names this site
    in full (https://www.hairbygerta.com/... , only the canonical link may), an address that leads out of
    the site folder, or an <img> of a placeholder photo without class="ph" and alt="".
  - A relative address that leads to no page of the page table and to no file in the site folder gives a
    WARNING line. The page is still written, but read the line: it is nearly always a typing mistake.

TRY A MODULE WITHOUT TOUCHING THE REAL PAGES

    python tools/build_pages.py --only gallery --out SOME_SCRATCH_FOLDER

writes SOME_SCRATCH_FOLDER/gallery/index.html and nothing in the site folder. Add --pages-dir DIR to load a
draft module from another folder (the file name stays the one in the page table). Should the run have a
replaced photo to record, the changed image-manifest.json goes into SOME_SCRATCH_FOLDER as well and the one
in the site folder stays as it is.
"""
import sys

sys.dont_write_bytecode = True      # keeps Python from leaving a __pycache__ folder in tools/pages

import argparse
import collections
import datetime
import hashlib
import html.parser
import importlib.util
import json
import os
import posixpath
import re
import struct
import urllib.parse

# ----------------------------------------------------------------------------------------------------------
# PLACEHOLDER PHOTOS
#
# Every name in this list is a photo that still shows the beige placeholder picture.
# When you have a real photo that you are allowed to use:
#   1. Save it over the placeholder with the very same file name: images/NAME.jpg, and a small copy
#      (800 px on its long side) as images/sm/NAME.jpg.
#   2. Delete the line with that name from the list below.
#   3. Open the content file of the page that shows the photo (folder content) and write a short
#      description of the photo between the quotes after "alt", in the entry with "file": "NAME".
#   4. Run this script again:  python tools/build_pages.py
# As long as a name is in this list, its photo is shown without a description (alt="") and with class="ph".
# For a name that is no longer in this list the script reads the pixel size from the two photo files
# themselves. When it builds a page that shows the photo, and neither of the two files is a placeholder
# picture any more, it also writes the photo into image-manifest.json by itself: the status "owner-photo"
# with the pixel size, the number of bytes and the SHA-256 fingerprint of both files. So that file never
# has to be changed by hand, and it only changes when a photo did. Save a newer photo over an owner photo
# later and the next run records the newer one, there is no further step.
# The script prints a line that starts with WARNING when one of the steps was forgotten: the name was
# deleted but a file is still the placeholder picture, a photo was saved but its name is still in this
# list, or the description is still empty.
# ----------------------------------------------------------------------------------------------------------
PLACEHOLDERS = [
    "about-salon",
    "brunette-balayage",
    "copper-waves",
    "foils-highlights",
    "g01",
    "g02",
    "g04",
    "g05",
    "g06",
    "g07",
    "g10",
    "g14",
    "g15",
    "g16",
    "g17",
    "g18",
    "g19",
    "g20",
    "g21",
    "home-smile",
    "home-styling",
    "home-waves",
    "makeup-red-lips",
    "meet-extensions",
    "svc-bridal",
    "svc-haircut",
]

# ----------------------------------------------------------------------------------------------------------
# The page table, exactly as in section 2 of tools/CONTRACT.md.
# ----------------------------------------------------------------------------------------------------------
Page = collections.namedtuple("Page", "slug path content module output")

REGISTRY = tuple(Page(*row) for row in (
    # slug                      address                       content file                              page module                                  output
    ("home",                    "/",                          "content/home.json",                      "tools/pages/home.py",                       "index.html"),
    ("gallery",                 "/gallery/",                  "content/gallery.json",                   "tools/pages/gallery.py",                    "gallery/index.html"),
    ("book-online",             "/book-online/",              "content/book-online.json",               "tools/pages/book_online.py",                "book-online/index.html"),
    ("about",                   "/about/",                    "content/about.json",                     "tools/pages/about.py",                      "about/index.html"),
    ("contact",                 "/contact/",                  "content/contact.json",                   "tools/pages/contact.py",                    "contact/index.html"),
    ("english-refund-policy",   "/english-refund-policy/",    "content/english-refund-policy.json",     "tools/pages/english_refund_policy.py",      "english-refund-policy/index.html"),
    ("accessibility-statement", "/accessibility-statement/",  "content/accessibility-statement.json",   "tools/pages/accessibility_statement.py",    "accessibility-statement/index.html"),
    ("english-privacy-policy",  "/english-privacy-policy/",   "content/english-privacy-policy.json",    "tools/pages/english_privacy_policy.py",     "english-privacy-policy/index.html"),
    ("terms-conditions",        "/terms-conditions/",         "content/terms-conditions.json",          "tools/pages/terms_conditions.py",           "terms-conditions/index.html"),
    ("404",                     "/404.html",                  "content/404.json",                       "tools/pages/not_found.py",                  "404.html"),
))

SITE_JSON = "content/site.json"
MANIFEST_JSON = "image-manifest.json"
# What image-manifest.json calls a photo ("status"). A placeholder is the beige picture. An owner-photo is a
# photo the owner saved over a placeholder: this script writes that status itself (contract, section 10,
# decision 27). Only names with one of these two can be taken out of PLACEHOLDERS, the three "allowed"
# pictures (logo, g12, g13) are never touched.
PLACEHOLDER_STATUS = "placeholder"
OWNER_STATUS = "owner-photo"
JSONLD_JSON = "seo/jsonld-home.json"
JSONLD_SLUG = "home"                    # the only page that carries the JSON-LD script
# The two tags that show Google Search Console and Bing Webmaster Tools that this site belongs to its owner. They
# are the same tags the old Wix site had, so both stay verified after the move. Google and Bing read them on the
# home page, so only the home page has them. Keep them exactly as they are.
VERIFICATION_SLUG = "home"
VERIFICATION_TAGS = (
    ("google-site-verification", "cEwGkDfnBA3KDOjrEJ1VtYTp5NZwNkC0jiX1SQsjxsI"),    # Google Search Console
    ("msvalidate.01", "2798AE29C3678DCCCB40CFBEF9EF84EA"),                           # Bing Webmaster Tools
)
PAGES_DIR = "tools/pages"
PHONE_MAX = 760                         # the phone breakpoint of the stylesheet, used in the default sizes attribute
PAGES_HOST = "achoostorm.github.io"     # where the site is published before the domain is connected
# The fonts are files of the site itself (folder fonts, see the section "05 Fonts" of css/style.css and
# tools/make_fonts.py). Every page asks the browser to fetch the font files named in "font_preloads" of
# content/site.json right away, before it has read the stylesheet, so the text gets its real font sooner.
# crossorigin belongs on such a link also for a file of the site's own: a browser fetches fonts that way,
# and without the word it would fetch the file twice.
FONT_PRELOAD = '<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>'
# The small script in the head of every page. It puts the class "js" on <html> before the page is drawn, which
# tells the stylesheet that the site script is there (on a phone the menu is then folded behind the menu
# button). js/site.js starts with "var BOOKING_URL = ...". When that file did not arrive, or the browser could
# not read it (a quote mark lost while that line was edited, for example), BOOKING_URL does not exist once
# the page is read. The class is then taken away again, so the menu shows as a plain list and still works.
JS_FLAG = ('<script>document.documentElement.classList.add("js");document.addEventListener("DOMContentLoaded",function(){'
           'if(typeof BOOKING_URL!=="string"){document.documentElement.classList.remove("js")}})</script>')
MENU_LABEL = "Menu"                     # accessible name of the phone menu button (contract, section 6)
NAV_LABEL = "Main"                      # accessible name of the navigation (contract, section 6)
RESULT_KEYS = ("body", "head_extra", "head_first", "robots")
INLINE_TAGS = ("a", "br", "strong", "em")
LINK_ATTRS = ("href", "target", "rel", "title", "class", "id", "lang", "hreflang", "download")
BLOCK_KEYS = {"h2": ("type", "text", "html"), "h3": ("type", "text", "html"), "p": ("type", "text", "html"),
              "ul": ("type", "items")}
ADDRESS_ATTRS = ("href", "src", "action", "formaction", "poster", "data")

# Icons of the social links, drawn in the colour of the text around them. The key is "name" in content/site.json.
# Every icon is one filled shape in a box of 23 x 23 px, the size the stylesheet gives the link around it.
# There are two sets, see ctx.social.
# icons="disc": a filled disc with the sign cut out of it, as in the footer.
_SVG = '<svg viewBox="0 0 24 24" width="23" height="23" aria-hidden="true" focusable="false"><path d="%s"/></svg>'
SOCIAL_ICONS = {
    "Facebook": _SVG % (
        "M12 0a12 12 0 0 0-1.9 23.85v-8.4H7.08V12h3.04V9.36c0-3 1.79-4.67 4.53-4.67 1.31 0 2.68.24 2.68.24v2.95h-1.51"
        "c-1.49 0-1.95.93-1.95 1.87V12h3.32l-.53 3.45h-2.79v8.4A12 12 0 0 0 12 0z"),
    "Instagram": _SVG % (
        "M12 0a12 12 0 1 0 0 24 12 12 0 0 0 0-24zm0 5.2c1.85 0 2.08 0 2.8.04 1.98.09 2.9 1.03 2.99 2.99.03.72.04.95.04 "
        "2.77s0 2.05-.04 2.77c-.09 1.95-1 2.9-2.99 2.99-.72.03-.95.04-2.8.04s-2.07 0-2.79-.04c-1.98-.09-2.9-1.04-2.99-"
        "2.99C6.2 13.05 6.2 12.82 6.2 11s0-2.05.04-2.77c.09-1.96 1.01-2.9 2.99-2.99.72-.03.95-.04 2.77-.04zm0 1.25c-1.8"
        " 0-2.02 0-2.73.04-1.4.06-2.06.73-2.12 2.12-.03.71-.04.92-.04 2.71s0 2 .04 2.71c.06 1.39.71 2.06 2.12 2.12.71."
        "03.92.04 2.73.04s2.02 0 2.73-.04c1.4-.06 2.06-.73 2.12-2.12.03-.71.04-.92.04-2.71s0-2-.04-2.71c-.06-1.39-.72-"
        "2.06-2.12-2.12-.71-.03-.93-.04-2.73-.04zm0 2.07a3.48 3.48 0 1 1 0 6.96 3.48 3.48 0 0 1 0-6.96zm0 1.25a2.23 "
        "2.23 0 1 0 0 4.46 2.23 2.23 0 0 0 0-4.46zm3.62-2.2a.81.81 0 1 1 0 1.63.81.81 0 0 1 0-1.63z"),
}
# icons="bare": the sign alone, as in the Social Media item of the Contact page. Drawn for this site to the
# measure of the two signs on the old Contact page. One unit of the numbers below is one pixel on screen.
# Both signs are 17 px tall and stand in the middle of the box, 3 px below its top edge. The letter f is 9 px
# wide and starts 7 px in from the left edge of the box, the camera is 17 px wide and starts 3 px in. The
# stylesheet moves the row of the Contact page 8 px to the left (7 px on a phone), which puts the letter f
# under the first letter of the heading. When a sign is drawn again, keep it inside the same outline.
_SVG_BARE = ('<svg viewBox="0 0 23 23" width="23" height="23" aria-hidden="true" focusable="false">'
             '<path fill-rule="evenodd" d="%s"/></svg>')
SOCIAL_ICONS_BARE = {
    # the letter f: stem, bar and hook
    "Facebook": _SVG_BARE % (
        "M9.8 20v-7.6H7V9h2.8V6.8A3.8 3.8 0 0 1 13.6 3H16v3h-1.6a1.3 1.3 0 0 0-1.3 1.3V9H16l-.5 3.4h-2.4V20z"),
    # a camera: a square with round corners, the ring of the lens and the dot of the flash
    "Instagram": _SVG_BARE % (
        "M7.5 3h8A4.5 4.5 0 0 1 20 7.5v8a4.5 4.5 0 0 1-4.5 4.5h-8A4.5 4.5 0 0 1 3 15.5v-8A4.5 4.5 0 0 1 7.5 3z"
        "M7.5 4.6a2.9 2.9 0 0 0-2.9 2.9v8a2.9 2.9 0 0 0 2.9 2.9h8a2.9 2.9 0 0 0 2.9-2.9v-8a2.9 2.9 0 0 0-2.9-2.9z"
        "M11.5 7a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zm0 1.8a2.7 2.7 0 1 0 0 5.4 2.7 2.7 0 0 0 0-5.4z"
        "M16 5.9a1.1 1.1 0 1 1 0 2.2 1.1 1.1 0 0 1 0-2.2z"),
}
SOCIAL_ICON_SETS = {"disc": SOCIAL_ICONS, "bare": SOCIAL_ICONS_BARE}


class BuildError(Exception):
    """Something is missing or wrong. The message names the file and the key."""


# ----------------------------------------------------------------------------------------------------------
# JSON files. Every object remembers its file and key, so a missing key gives a clear message.
# ----------------------------------------------------------------------------------------------------------

class Node(dict):
    """A JSON object that knows where it came from."""
    __slots__ = ("_file", "_key")

    def __missing__(self, name):
        raise BuildError('%s: key "%s" is missing' % (self._file, _join_key(self._key, name)))


def _join_key(parent, name):
    if isinstance(name, int):
        return "%s[%d]" % (parent, name)
    return "%s.%s" % (parent, name) if parent else str(name)


def _wrap(value, file, key=""):
    """A fresh copy of parsed JSON in which every object is a Node."""
    if isinstance(value, dict):
        node = Node()
        node._file, node._key = file, key
        for name, child in value.items():
            node[name] = _wrap(child, file, _join_key(key, name))
        return node
    if isinstance(value, list):
        return [_wrap(child, file, _join_key(key, i)) for i, child in enumerate(value)]
    return value


def _where(node, name=None):
    """'content/home.json: key "hero.welcome"' for a Node (and one of its keys)."""
    key = node._key if name is None else _join_key(node._key, name)
    return '%s: key "%s"' % (node._file, key) if key else "%s: the file" % node._file


def _read_json(site_dir, rel, optional=False, any_type=False):
    path = os.path.join(site_dir, *rel.split("/"))
    if not os.path.isfile(path):
        if optional:
            return None
        raise BuildError("%s: file not found" % rel)
    try:
        with open(path, encoding="utf-8-sig") as f:
            data = json.load(f)
    except UnicodeDecodeError as e:
        raise BuildError("%s: the file is not saved as UTF-8 (%s)" % (rel, e.reason))
    except json.JSONDecodeError as e:
        raise BuildError("%s: not valid JSON, line %d column %d: %s" % (rel, e.lineno, e.colno, e.msg))
    except OSError as e:
        raise BuildError("%s: cannot be read (%s)" % (rel, e.strerror or e))
    if not any_type and not isinstance(data, dict):
        raise BuildError("%s: the file must hold one JSON object, { ... }" % rel)
    return data


_KINDS = {str: "a text", list: "a list", dict: "an object", int: "a whole number"}


def _need(node, name, kind, empty_ok=False):
    """node[name], checked: it must be there, of the right kind, and not empty."""
    value = node[name]
    if not isinstance(value, kind) or isinstance(value, bool):
        raise BuildError("%s must be %s" % (_where(node, name), _KINDS[kind]))
    if not empty_ok and kind in (str, list) and not (value.strip() if kind is str else value):
        raise BuildError("%s must not be empty" % _where(node, name))
    return value


def _need_objects(node, name):
    """node[name] as a list of objects."""
    items = _need(node, name, list)
    for i, item in enumerate(items):
        if not isinstance(item, Node):
            raise BuildError("%s must be an object, { ... }" % _where(node, "%s[%d]" % (name, i)))
    return items


def _find_key(tree, text):
    """The 'file: key' of the first value in a wrapped JSON tree that equals text, or None."""
    def walk(value, file, key):
        if isinstance(value, dict):
            for name, child in value.items():
                found = walk(child, getattr(value, "_file", file), _join_key(getattr(value, "_key", key), name))
                if found:
                    return found
        elif isinstance(value, list):
            for i, child in enumerate(value):
                found = walk(child, file, _join_key(key, i))
                if found:
                    return found
        elif isinstance(value, str) and value == text:
            return '%s: key "%s"' % (file, key)
        return None
    return walk(tree, getattr(tree, "_file", ""), getattr(tree, "_key", ""))


# ----------------------------------------------------------------------------------------------------------
# Escaping
# ----------------------------------------------------------------------------------------------------------

def _text(value):
    """Plain text for between two tags: & < > become entities, apostrophes and quotes stay as they are."""
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc(value):
    """Plain text for anywhere, also inside a double-quoted attribute: & < > and " become entities."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise BuildError("ctx.esc needs a text, it was given %s (a key read with .get() that is not in the content file?)"
                         % ("nothing (None)" if value is None else type(value).__name__))
    return _text(str(value)).replace('"', "&quot;")


def _short(text, limit=70):
    text = " ".join(str(text).split())
    return text if len(text) <= limit else text[:limit - 3] + "..."


_TAG_RE = re.compile(r"""<(/?)([A-Za-z][A-Za-z0-9-]*)((?:"[^"]*"|'[^']*'|[^<>"'])*)>""")
_ATTR_RE = re.compile(r"""\s*([^\s"'<>/=]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?""")
_ROOT_RE = re.compile(r"\{\{\s*root\s*\}\}")
_SCHEME_RE = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
_FILE_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*(/[A-Za-z0-9_][A-Za-z0-9_.-]*)*\Z")


# ----------------------------------------------------------------------------------------------------------
# The image files themselves. Only looked at for a photo that replaced a placeholder: image-manifest.json
# still describes the placeholder picture then, so the pixel size has to come from the files.
# ----------------------------------------------------------------------------------------------------------

def _exif_turned(tiff):
    """True when the camera marked the photo as lying on its side (Exif orientation 5 to 8). A browser shows
    such a photo turned by a quarter, so its width and height swap places."""
    order = {b"II": "<", b"MM": ">"}.get(tiff[:2])
    if order is None:
        return False
    try:
        start = struct.unpack(order + "I", tiff[4:8])[0]
        count = struct.unpack(order + "H", tiff[start:start + 2])[0]
        for i in range(count):
            entry = tiff[start + 2 + 12 * i:start + 14 + 12 * i]
            if struct.unpack(order + "H", entry[:2])[0] == 0x0112:
                return 5 <= struct.unpack(order + "H", entry[8:10])[0] <= 8
    except struct.error:
        pass
    return False


def _jpeg_size(data):
    """(width, height) of a JPEG picture as a browser shows it, or None when the bytes are not a JPEG."""
    if data[:2] != b"\xff\xd8":
        return None
    turned, pos = False, 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            return None
        marker = data[pos + 1]
        if marker == 0xFF:                              # a fill byte
            pos += 1
            continue
        if marker == 0x01 or 0xD0 <= marker <= 0xD8:    # markers that stand alone
            pos += 2
            continue
        if marker in (0xD9, 0xDA):                      # the picture data starts, and no size was found
            return None
        length = struct.unpack(">H", data[pos + 2:pos + 4])[0]
        if length < 2:
            return None
        segment = data[pos + 4:pos + 2 + length]
        if marker == 0xE1 and segment[:6] == b"Exif\x00\x00":
            turned = _exif_turned(segment[6:])
        elif 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if len(segment) < 5:
                return None
            height, width = struct.unpack(">HH", segment[1:5])
            if not width or not height:
                return None
            return (height, width) if turned else (width, height)
        pos += 2 + length
    return None


class _Photos:
    """What the image files in the site folder really hold. Every file is read once per build at most."""

    def __init__(self, site_dir):
        self.site_dir = site_dir
        self._facts = {}

    def _read(self, rel):
        if rel not in self._facts:
            try:
                with open(os.path.join(self.site_dir, *rel.split("/")), "rb") as f:
                    data = f.read()
                self._facts[rel] = (hashlib.sha256(data).hexdigest(), _jpeg_size(data), len(data))
            except OSError:
                self._facts[rel] = None
        return self._facts[rel]

    def exists(self, rel):
        return self._read(rel) is not None

    def sha256(self, rel):
        facts = self._read(rel)
        return facts[0] if facts else None

    def size(self, rel):
        facts = self._read(rel)
        return facts[1] if facts else None

    def bytes(self, rel):
        facts = self._read(rel)
        return facts[2] if facts else None


# ----------------------------------------------------------------------------------------------------------
# ctx, what a page module gets
# ----------------------------------------------------------------------------------------------------------

ImageFile = collections.namedtuple("ImageFile", "file width height")


class Ctx:
    """Everything a page module may use. The docstring at the top of this file describes each part."""

    def __init__(self, page, content, site, manifest, photos=None, warnings=None, replaced=None):
        self.slug = page.slug
        self.path = page.path
        self.root = "../" * page.output.count("/")
        self.content = content
        self.site = site
        self.manifest = manifest
        self._content_file = page.content
        self._photos = photos if photos is not None else _Photos(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._warnings = warnings if warnings is not None else []
        self._replaced = replaced if replaced is not None else set()    # the replaced photos this page shows

    # ---- text

    def esc(self, text):
        return esc(text)

    def url(self, site_path):
        if not isinstance(site_path, str) or not site_path.strip():
            raise BuildError("ctx.url needs an address like \"/gallery/\", it was given %r" % (site_path,))
        site_path = site_path.strip()
        if site_path.startswith("#") or _SCHEME_RE.match(site_path):
            return site_path
        if not site_path.startswith("/") or site_path.startswith("//") or "\\" in site_path:
            raise BuildError("ctx.url(\"%s\"): an address inside the site starts with one /, for example \"/gallery/\" "
                             "or \"/images/g12.jpg\"" % site_path)
        rest = site_path[1:]
        if self.root == "" and (rest == "" or rest[0] in "#?"):
            return "./" + rest
        return self.root + rest

    def inline(self, html):
        return self._inline(html, None)

    def blocks(self, blocks):
        if not isinstance(blocks, list):
            raise BuildError("%s: ctx.blocks needs the list of blocks, it was given %s"
                             % (self._content_file, type(blocks).__name__))
        out = []
        for i, block in enumerate(blocks):
            where = _where(block) if isinstance(block, Node) and block._key else "%s: block %d" % (self._content_file, i + 1)
            if not isinstance(block, dict):
                raise BuildError('%s must be an object like {"type": "p", "text": "..."}' % where)
            kind = block.get("type")
            if kind not in BLOCK_KEYS:
                raise BuildError('%s: "type" is %s, it must be one of h2, h3, p, ul' % (where, json.dumps(kind)))
            extra = [k for k in block if k not in BLOCK_KEYS[kind]]
            if extra:
                raise BuildError('%s: a %s block has no "%s" (allowed: %s)' % (where, kind, extra[0], ", ".join(BLOCK_KEYS[kind])))
            if kind == "ul":
                items = block.get("items")
                if not isinstance(items, list) or not items:
                    raise BuildError('%s: a ul block needs "items", a list with at least one entry' % where)
                lines = ["<ul>"]
                for j, item in enumerate(items):
                    item_where = "%s, item %d" % (where, j + 1)
                    if isinstance(item, str):
                        lines.append("  <li>%s</li>" % _text(item))
                    elif isinstance(item, dict):
                        lines.append("  <li>%s</li>" % self._text_or_html(item, item_where))
                    else:
                        raise BuildError('%s must be a text or {"html": "..."}' % item_where)
                lines.append("</ul>")
                out.append("\n".join(lines))
            else:
                out.append("<%s>%s</%s>" % (kind, self._text_or_html(block, where), kind))
        return "\n".join(out)

    def _text_or_html(self, node, where):
        has_text, has_html = "text" in node, "html" in node
        if has_text == has_html:
            raise BuildError('%s needs either "text" or "html" (it has %s)' % (where, "both" if has_text else "neither"))
        value = node["html"] if has_html else node["text"]
        if not isinstance(value, str):
            raise BuildError('%s: "%s" must be a text' % (where, "html" if has_html else "text"))
        return self._inline(value, where) if has_html else _text(value)

    def _inline(self, source, where):
        if not isinstance(source, str):
            raise BuildError("%s: ctx.inline needs a text, it was given %s"
                             % (where or self._content_file, "nothing (None)" if source is None else type(source).__name__))

        def fail(problem):
            place = where or _find_key(self.content, source) or _find_key(self.site, source) or self._content_file
            raise BuildError('%s: %s. The text starts: "%s"' % (place, problem, _short(source)))

        out, stack, pos = [], [], 0
        for m in _TAG_RE.finditer(source):
            out.append(_text(_ROOT_RE.sub(self.root, source[pos:m.start()])))
            pos = m.end()
            closing, tag, rest = m.group(1), m.group(2).lower(), m.group(3).strip()
            if tag not in INLINE_TAGS:
                fail("the tag <%s> is not allowed in a text (only %s)" % (tag, ", ".join("<%s>" % t for t in INLINE_TAGS)))
            if tag == "br":
                if closing or rest.rstrip("/").strip():
                    fail("a line break is written <br>, with nothing else in it")
                out.append("<br>")
            elif closing:
                if rest:
                    fail("</%s> must not hold anything else" % tag)
                if not stack or stack[-1] != tag:
                    fail("</%s> closes a tag that is not open at that point" % tag)
                stack.pop()
                out.append("</%s>" % tag)
            else:
                if rest.endswith("/"):
                    fail("<%s> must be closed with </%s>, not with />" % (tag, tag))
                if tag in stack:
                    fail("<%s> inside another <%s>" % (tag, tag))
                stack.append(tag)
                out.append("<%s%s>" % (tag, self._inline_attrs(tag, rest, fail)))
        out.append(_text(_ROOT_RE.sub(self.root, source[pos:])))
        if stack:
            fail("<%s> is never closed" % stack[-1])
        return "".join(out)

    def _inline_attrs(self, tag, rest, fail):
        attrs, pos = [], 0
        while pos < len(rest):
            m = _ATTR_RE.match(rest, pos)
            if not m or m.end() == pos:
                fail("the attributes of <%s> cannot be read" % tag)
            pos = m.end()
            name = m.group(1).lower()
            value = next((g for g in m.group(2, 3, 4) if g is not None), None)
            if tag != "a":
                fail("<%s> takes no attributes" % tag)
            if name == "style" or name.startswith("on"):
                fail('the attribute %s is not allowed on a link' % name)
            if name not in LINK_ATTRS and not name.startswith(("aria-", "data-")):
                fail('the attribute %s is not allowed on a link (allowed: %s, aria-..., data-...)' % (name, ", ".join(LINK_ATTRS)))
            if any(name == n for n, _ in attrs):
                fail("the attribute %s is there twice" % name)
            if value is None and not name.startswith("data-") and name != "download":
                fail('the attribute %s needs a value, %s="..."' % (name, name))
            attrs.append((name, value))
        if tag != "a":
            return ""
        names = [n for n, _ in attrs]
        if "href" not in names:
            fail("a link needs an href")
        fixed = []
        for name, value in attrs:
            if name == "href":
                value = value.strip()
                m = _ROOT_RE.match(value)
                if m:
                    value = self.url("/" + value[m.end():].lstrip("/"))
                elif value.startswith("/") and not value.startswith("//"):
                    value = self.url(value)
                if not value or "{{" in value or value.lower().startswith(("javascript:", "data:", "vbscript:")):
                    fail('the href "%s" is not an address this site can use' % _short(value))
            fixed.append((name, value))
        if dict(fixed).get("target") == "_blank":
            rel = (dict(fixed).get("rel") or "").split()
            if "noopener" not in rel and "noreferrer" not in rel:
                rel.append("noopener")
                fixed = [(n, v) for n, v in fixed if n != "rel"] + [("rel", " ".join(rel))]
        return "".join(" %s" % n if v is None else ' %s="%s"' % (n, esc(v)) for n, v in fixed)

    # ---- images

    def is_placeholder(self, name):
        return name in PLACEHOLDERS

    def _image_file(self, node, what):
        """file, width and height of one manifest record, checked."""
        if not isinstance(node, Node):
            raise BuildError("%s: %s must be an object with file, width and height" % (MANIFEST_JSON, what))
        file = _need(node, "file", str)
        if not _FILE_RE.match(file) or ".." in file:
            raise BuildError('%s must be a path inside the site folder like "images/g12.jpg", not "%s"' % (_where(node, "file"), file))
        width, height = _need(node, "width", int), _need(node, "height", int)
        if width <= 0 or height <= 0:
            raise BuildError("%s: width and height must be larger than 0" % _where(node))
        return ImageFile(file, width, height)

    def _own_photo(self, image, name):
        """The same record with the pixel size read from the file itself (for a photo that replaced a placeholder)."""
        if not self._photos.exists(image.file):
            raise BuildError('%s: file not found. "%s" is not in the list PLACEHOLDERS in tools/build_pages.py, so the photo '
                             "must be there, as images/%s.jpg and as a small copy images/sm/%s.jpg" % (image.file, name, name, name))
        size = self._photos.size(image.file)
        if size is None:
            raise BuildError("%s: this is not a JPG picture, so its size cannot be read. Open your photo in a photo program "
                             "and save a copy as JPG (JPEG) under this name" % image.file)
        return ImageFile(image.file, size[0], size[1])

    def img(self, name, alt="", width=None, height=None, lazy=True, variant="full", sizes=None):
        call = 'ctx.img("%s")' % (name,)
        if variant not in ("full", "sm"):
            raise BuildError('%s: variant must be "full" or "sm", not %r' % (call, variant))
        images = _need(self.manifest, "images", dict)
        if not isinstance(name, str) or name not in images:
            raise BuildError('%s: "images" has no entry "%s". ctx.img takes the name of the photo without folder and '
                             'extension, for example "g12"' % (MANIFEST_JSON, name))
        entry = images[name]
        what = 'key "images.%s"' % name
        placeholder = self.is_placeholder(name)
        full = self._image_file(entry, what)
        small = self._image_file(entry["sm"], what + ".sm") if entry.get("sm") is not None else None
        if not placeholder and entry.get("status") in (PLACEHOLDER_STATUS, OWNER_STATUS):
            # A photo of the owner was saved over the placeholder and its name was taken out of PLACEHOLDERS.
            # The manifest may still describe the placeholder picture, or a photo that was there before, so
            # the pixel sizes always come from the two files themselves (contract, section 10, decision 15).
            # The page then never depends on whether the manifest was brought up to date already.
            full = self._own_photo(full, name)
            small = self._own_photo(small, name) if small is not None else None
            self._replaced.add(name)        # written into the manifest once the page is built (decision 27)
        webp = entry.get("webp")
        webp_full = self._image_file(webp, what + ".webp") if webp is not None else None
        webp_small = self._image_file(webp["sm"], what + ".webp.sm") if webp is not None and webp.get("sm") is not None else None

        if variant == "sm":
            if small is None:
                raise BuildError('%s: %s has no small copy ("sm" is empty), so %s cannot use variant="sm"' % (MANIFEST_JSON, what, call))
            chosen, candidates = small, None
            webp_candidates = [webp_small] if webp_small else None
            # A thumbnail that says how wide it is on screen (sizes) also offers the full WebP file, for
            # sharp and for very wide screens. The JPEG stays the small copy.
            if sizes is not None and webp_small and webp_full and webp_small.width < webp_full.width:
                webp_candidates = [webp_small, webp_full]
        else:
            chosen = full
            candidates = [small, full] if small and small.width < full.width else None
            webp_candidates = None
            if webp_full:
                webp_candidates = [webp_small, webp_full] if webp_small and webp_small.width < webp_full.width else [webp_full]

        for label, value in (("width", width), ("height", height)):
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value <= 0):
                raise BuildError("%s: %s must be a whole number of pixels larger than 0, not %r" % (call, label, value))
        if width is None and height is None:
            width, height = chosen.width, chosen.height
        elif height is None:
            height = max(1, round(width * chosen.height / chosen.width))
        elif width is None:
            width = max(1, round(height * chosen.width / chosen.height))

        if placeholder:
            alt = ""
        elif not isinstance(alt, str):
            raise BuildError('%s: alt must be a text, not %r' % (call, alt))
        elif not alt.strip():
            self._warnings.append('%s: the photo "%s" has no description. Find "file": "%s" in that file and write a few words '
                                  'about the photo between the two quote marks after "alt", then run this script again.'
                                  % (self._content_file, name, name))
        if sizes is None:
            sizes = "(max-width: %dpx) 100vw, %dpx" % (PHONE_MAX, width)
        elif not isinstance(sizes, str) or not sizes.strip():
            raise BuildError("%s: sizes must be a text like \"(max-width: 760px) 100vw, 288px\"" % call)

        def address(image):
            return esc(self.url("/" + image.file))

        def srcset(files):
            if len(files) == 1:
                return address(files[0])
            return ", ".join("%s %dw" % (address(f), f.width) for f in files)

        attrs = []
        if placeholder:
            attrs.append('class="ph"')
        attrs.append('src="%s"' % address(chosen))
        if candidates:
            attrs.append('srcset="%s"' % srcset(candidates))
            attrs.append('sizes="%s"' % esc(sizes))
        attrs.append('alt="%s"' % esc(alt))
        attrs.append('width="%d" height="%d"' % (width, height))
        attrs.append('loading="%s"' % ("lazy" if lazy else "eager"))
        attrs.append('decoding="async"')
        tag = "<img %s>" % " ".join(attrs)
        if webp_candidates:
            source = '<source type="image/webp" srcset="%s"' % srcset(webp_candidates)
            if len(webp_candidates) > 1:
                source += ' sizes="%s"' % esc(sizes)
            tag = "<picture>%s>%s</picture>" % (source, tag)
        return tag

    # ---- shared pieces

    def social(self, links=None, icons="disc"):
        if icons not in SOCIAL_ICON_SETS:
            raise BuildError("ctx.social: icons must be %s, not %r" % (" or ".join('"%s"' % key for key in SOCIAL_ICON_SETS), icons))
        drawings = SOCIAL_ICON_SETS[icons]
        if links is None:
            links = _need_objects(self.site, "social")
        if not isinstance(links, list) or not links:
            raise BuildError("ctx.social needs a list of links with name, href and label")
        lines = ['<div class="social">']
        for i, link in enumerate(links):
            where = _where(link) if isinstance(link, Node) else "ctx.social: link %d" % (i + 1)
            if not isinstance(link, dict):
                raise BuildError("%s must be an object with name, href and label" % where)
            for key in ("name", "href", "label"):
                if not isinstance(link.get(key), str) or not link[key].strip():
                    raise BuildError('%s needs "%s", a text' % (where, key))
            icon = drawings.get(link["name"])
            if icon is None:
                raise BuildError('%s: there is no icon for "%s" in tools/build_pages.py (icons: %s)'
                                 % (where, link["name"], ", ".join(drawings)))
            lines.append('  <a href="%s" target="_blank" rel="noopener" aria-label="%s">%s</a>'
                         % (esc(link["href"]), esc(link["label"]), icon))
        lines.append("</div>")
        return "\n".join(lines)


# ----------------------------------------------------------------------------------------------------------
# The shared page: head, header, footer (contract, section 6)
# ----------------------------------------------------------------------------------------------------------

def _indent(markup, spaces):
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def _lines(markup):
    """Markup handed in by a page module, as clean lines (no CR, no blank line at either end)."""
    markup = (markup or "").replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    return [line.rstrip() for line in markup.split("\n")] if markup.strip() else []


def _site_url(site):
    site_url = _need(site, "site_url", str).strip().rstrip("/")
    parts = urllib.parse.urlsplit(site_url)
    if parts.scheme != "https" or not parts.hostname or parts.path or parts.query or parts.fragment:
        raise BuildError('%s must be the address of the site like "https://www.hairbygerta.com"' % _where(site, "site_url"))
    return site_url


def _image_size(manifest, rel):
    """(width, height) of a picture of the site as image-manifest.json records it (images, icons or composites),
    or None when the manifest does not list it."""
    for record in list(manifest.get("images", {}).values()) + list(manifest.get("composites") or []):
        if isinstance(record, dict) and record.get("file") == rel and record.get("width") and record.get("height"):
            return int(record["width"]), int(record["height"])
    return None


def _jsonld_script(data):
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    text = text.replace("</", "<\\/").replace("<!--", "\\u003c!--")
    return '<script type="application/ld+json">%s</script>' % text


def _document(page, ctx, parts, site, jsonld, year):
    """The whole page as one text."""
    content, url = ctx.content, ctx.url
    site_url = _site_url(site)
    title = _need(content, "title", str)
    description = _need(content, "description", str)
    og_image = _need(site, "og_image", str)
    if not og_image.startswith("/") or og_image.startswith("//"):
        raise BuildError('%s must be a path that starts with /, like "/images/g12.jpg"' % _where(site, "og_image"))
    font_preloads = _need(site, "font_preloads", list)
    for i, font in enumerate(font_preloads):
        if not isinstance(font, str) or not font.startswith("/fonts/") or not font.endswith(".woff2"):
            raise BuildError('%s must be a font file of the site like "/fonts/figtree-latin.woff2"' % _where(site, "font_preloads[%d]" % i))
    robots = parts["robots"].strip()
    noindex = any(token.strip().lower() in ("noindex", "none") for token in robots.split(","))

    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
    ]
    head += _lines(parts["head_first"])
    head.append("<title>%s</title>" % _text(title))
    head.append('<meta name="description" content="%s">' % esc(description))
    if robots:
        head.append('<meta name="robots" content="%s">' % esc(robots))
    if page.slug == VERIFICATION_SLUG:
        head += ['<meta name="%s" content="%s">' % (esc(name), esc(token)) for name, token in VERIFICATION_TAGS]
    if not noindex:
        head.append('<link rel="canonical" href="%s">' % esc(site_url + page.path))
    og_site_name = _need(site, "og_site_name", str)
    og_alt = _need(site, "og_image_alt", str)
    if not noindex:
        # A page that search engines must not list (the 404 page) is not an address to share either,
        # so it gets no Open Graph tags, just as it gets no canonical link.
        size = _image_size(ctx.manifest, og_image.lstrip("/"))
        head += [
            '<meta property="og:type" content="website">',
            '<meta property="og:locale" content="en_US">',
            '<meta property="og:site_name" content="%s">' % esc(og_site_name),
            '<meta property="og:title" content="%s">' % esc(title),
            '<meta property="og:description" content="%s">' % esc(description),
            '<meta property="og:url" content="%s">' % esc(site_url + page.path),
            '<meta property="og:image" content="%s">' % esc(site_url + og_image),
        ]
        if size:
            head += ['<meta property="og:image:width" content="%d">' % size[0], '<meta property="og:image:height" content="%d">' % size[1]]
        head += [
            '<meta property="og:image:alt" content="%s">' % esc(og_alt),
            # X (Twitter) reads these. Other apps read the Open Graph tags above.
            '<meta name="twitter:card" content="summary_large_image">',
            '<meta name="twitter:title" content="%s">' % esc(title),
            '<meta name="twitter:description" content="%s">' % esc(description),
            '<meta name="twitter:image" content="%s">' % esc(site_url + og_image),
            '<meta name="twitter:image:alt" content="%s">' % esc(og_alt),
        ]
    head += [
        '<link rel="icon" href="%s" sizes="any">' % esc(url("/favicon.ico")),
        '<link rel="icon" type="image/png" href="%s">' % esc(url("/images/favicon.png")),
        # 192 x 192: the icon Android shows when the site is added to the home screen
        '<link rel="icon" type="image/png" sizes="192x192" href="%s">' % esc(url("/images/icon-192.png")),
        '<link rel="apple-touch-icon" href="%s">' % esc(url("/images/apple-touch-icon.png")),
        '<meta name="theme-color" content="%s">' % esc(_need(site, "theme_color", str)),
    ]
    head += [FONT_PRELOAD % esc(url(font)) for font in font_preloads]
    head += [
        '<link rel="stylesheet" href="%s">' % esc(url("/css/style.css")),
        JS_FLAG,
    ]
    if jsonld is not None:
        head.append(_jsonld_script(jsonld))
    head += _lines(parts["head_extra"])

    nav = []
    for item in _need_objects(site, "nav"):
        path = _need(item, "path", str)
        current = ' aria-current="page"' if path == page.path else ""
        nav.append('<li><a href="%s"%s>%s</a></li>' % (esc(url(path)), current, _text(_need(item, "label", str))))

    footer = _need(site, "footer", dict)
    address = _need(site, "address_lines", list)
    for i, line in enumerate(address):
        if not isinstance(line, str) or not line.strip():
            raise BuildError("%s must be a text" % _where(site, "address_lines[%d]" % i))
    policy = ['<li><a href="%s">%s</a></li>' % (esc(url(_need(item, "path", str))), _text(_need(item, "label", str)))
              for item in _need_objects(footer, "policy_links")]

    out = ["<!doctype html>", '<html lang="en">', "<head>"]
    out += head
    out += [
        "</head>",
        '<body class="page-%s">' % esc(page.slug),
        '<a class="skip" href="#main">%s</a>' % _text(_need(site, "skip_link", str)),
        '<header class="site-header">',
        '  <div class="inner">',
        '    <a class="logo" href="%s" aria-label="%s"><img src="%s" alt="" width="134" height="138"></a>'
        % (esc(url("/")), esc(_need(site, "logo_label", str)), esc(url("/images/logo.jpg"))),
        '    <button class="menu-btn" type="button" aria-label="%s" aria-expanded="false" aria-controls="main-nav">'
        "<span></span><span></span><span></span></button>" % esc(MENU_LABEL),
        '    <nav class="main-nav" id="main-nav" aria-label="%s">' % esc(NAV_LABEL),
        "      <ul>",
    ]
    out += ["        " + line for line in nav]
    out += [
        "      </ul>",
        "    </nav>",
        "  </div>",
        "</header>",
        '<main id="main">',
    ]
    out += _lines(parts["body"])
    out += [
        "</main>",
        '<footer class="site-footer">',
        '  <div class="inner">',
        '    <hr class="foot-rule">',
        '    <div class="foot-cols">',
        '      <div class="foot-brand">',
        '        <p class="foot-name serif">%s</p>' % _text(_need(footer, "name", str)),
        '        <p class="foot-role serif">%s</p>' % _text(_need(footer, "role", str)),
        _indent(ctx.social(_need_objects(site, "social")), 8),
        "      </div>",
        '      <div class="foot-contact">',
        '        <p><a href="%s">%s</a></p>' % (esc(_need(site, "tel_href", str)), _text(_need(site, "phone", str))),
        '        <p><a href="%s">%s</a></p>' % (esc(_need(site, "mailto_href", str)), _text(_need(site, "email", str))),
        '        <p class="foot-addr">%s</p>' % "<br>".join(_text(line) for line in address),
        "      </div>",
        '      <ul class="foot-links">',
    ]
    out += ["        " + line for line in policy]
    out += [
        "      </ul>",
        "    </div>",
        '    <p class="copy">&copy; <span data-year>%d</span> %s</p>' % (year, _text(_need(site, "copyright", str))),
        "  </div>",
        "</footer>",
        '<script src="%s" defer></script>' % esc(url("/js/site.js")),
        "</body>",
        "</html>",
    ]
    return "\n".join(out) + "\n"


# ----------------------------------------------------------------------------------------------------------
# A last look at the finished page, before it is written
# ----------------------------------------------------------------------------------------------------------

class _Audit(html.parser.HTMLParser):
    def __init__(self, own_hosts):
        super().__init__(convert_charrefs=True)
        self.own_hosts = own_hosts
        self.h1 = 0
        self.problems = []
        self.local = []         # (shown, value) of every relative address, checked against the site folder afterwards

    def _address(self, tag, name, value, rel):
        value = value.strip()
        shown = '<%s %s="%s">' % (tag, name, _short(value))
        if value.startswith("/") and not value.startswith("//") or "\\" in value:
            self.problems.append("%s starts with a slash or holds a backslash. Use ctx.url, every address inside the site "
                                 "must be relative" % shown)
        elif re.match(r"(https?:)?//", value, re.I):
            if tag == "link" and ("canonical" in rel or "alternate" in rel):
                return
            host = (urllib.parse.urlsplit(value).hostname or "").lower()
            if host in self.own_hosts:
                self.problems.append("%s names this site in full. Use ctx.url, every address inside the site must be relative" % shown)
        elif value and not value.startswith("#") and not _SCHEME_RE.match(value):
            self.local.append((shown, value))

    def handle_starttag(self, tag, attrs):
        a = {name: (value or "") for name, value in attrs}
        if tag == "h1":
            self.h1 += 1
        if "style" in a:
            self.problems.append("%s has a style attribute. Styling belongs in css/style.css" % _short(self.get_starttag_text(), 90))
        rel = a.get("rel", "").lower().split()
        for name in ADDRESS_ATTRS:
            if name in a:
                self._address(tag, name, a[name], rel)
        for part in a.get("srcset", "").split(","):
            if part.strip():
                self._address(tag, "srcset", part.split()[0], rel)
        if tag == "img":
            src = a.get("src", "").split("?")[0].split("#")[0]
            name = os.path.splitext(src.rsplit("/", 1)[-1])[0]
            if "images/" in src and name in PLACEHOLDERS and (a.get("alt") != "" or "alt" not in a or "ph" not in a.get("class", "").split()):
                self.problems.append('<img src="%s"> shows the placeholder photo "%s" without class="ph" and alt="". Use ctx.img' % (_short(src), name))


def _audit(text, site_url, page, site_dir):
    """-> (problems that stop the page, notes that do not)."""
    host = urllib.parse.urlsplit(site_url).hostname.lower()
    bare = host[4:] if host.startswith("www.") else host
    parser = _Audit({host, bare, "www." + bare, PAGES_HOST})
    parser.feed(text)
    parser.close()
    problems, notes = list(parser.problems), []
    if parser.h1 != 1:
        problems.insert(0, "the page has %d <h1> elements, it must have exactly one" % parser.h1)
    outputs = {p.output for p in REGISTRY}
    folder = posixpath.dirname(page.output)
    for shown, value in parser.local:
        path = urllib.parse.unquote(value.split("#")[0].split("?")[0])
        if not path:
            continue                                    # only ?query or #anchor: this page
        target = posixpath.normpath(posixpath.join(folder, path))
        if target == ".." or target.startswith("../"):
            problems.append("%s leads out of the site folder" % shown)
            continue
        target = "" if target == "." else target
        if path.endswith("/") or not target:
            target = posixpath.join(target, "index.html")
        if target in outputs or os.path.isfile(os.path.join(site_dir, *target.split("/"))):
            continue
        hint = " (a page address ends with a slash)" if target + "/index.html" in outputs else ""
        note = "%s: %s leads to %s, which is not in the site folder%s." % (page.output, shown, target, hint)
        if note not in notes:
            notes.append(note)
    return problems, notes


# ----------------------------------------------------------------------------------------------------------
# Page modules
# ----------------------------------------------------------------------------------------------------------

def _load_module(path, shown, slug):
    if not os.path.isfile(path):
        raise BuildError('%s: file not found (the page module of "%s")' % (shown, slug))
    name = "hbg_page_" + re.sub(r"\W", "_", slug)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except SyntaxError as e:
        raise BuildError("%s: line %s: Python cannot read the file (%s)" % (shown, e.lineno, e.msg))
    except BuildError:
        raise
    except Exception as e:
        raise BuildError("%s: the file cannot be loaded%s (%s: %s)" % (shown, _line_text(path, e), type(e).__name__, e))
    if getattr(module, "SLUG", None) != slug:
        raise BuildError('%s: SLUG is %r, it must be "%s"' % (shown, getattr(module, "SLUG", None), slug))
    if not callable(getattr(module, "render", None)):
        raise BuildError("%s: the function render(ctx) is missing" % shown)
    return module


def _line_text(path, error):
    """', line N' for the last line of the page module that was running when the error came up."""
    line, tb, wanted = None, error.__traceback__, os.path.normcase(os.path.abspath(path))
    while tb is not None:
        if os.path.normcase(os.path.abspath(tb.tb_frame.f_code.co_filename)) == wanted:
            line = tb.tb_lineno
        tb = tb.tb_next
    return ", line %d" % line if line else ""


def _render(module, ctx, path, shown):
    try:
        parts = module.render(ctx)
    except BuildError as e:
        raise BuildError("%s (asked for by %s%s)" % (e, shown, _line_text(path, e)))
    except Exception as e:
        raise BuildError("%s%s: render(ctx) stopped with %s: %s" % (shown, _line_text(path, e), type(e).__name__, e))
    if not isinstance(parts, dict):
        raise BuildError('%s: render(ctx) must return a dict like {"body": "...", "head_extra": ""}, it returned %s'
                         % (shown, type(parts).__name__))
    unknown = [key for key in parts if key not in RESULT_KEYS]
    if unknown:
        raise BuildError('%s: render(ctx) returned the key "%s", only these are known: %s' % (shown, unknown[0], ", ".join(RESULT_KEYS)))
    clean = {}
    for key in RESULT_KEYS:
        value = parts.get(key)
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise BuildError('%s: "%s" in the result of render(ctx) must be a text, not %s' % (shown, key, type(value).__name__))
        clean[key] = value
    if not clean["body"].strip():
        raise BuildError('%s: render(ctx) returned no "body"' % shown)
    return clean


# ----------------------------------------------------------------------------------------------------------
# Building
# ----------------------------------------------------------------------------------------------------------

def _shown(path):
    return str(path).replace("\\", "/")


_SHA256_RE = re.compile(r"[0-9A-Fa-f]{64}\Z")


def _fingerprint(record):
    """The SHA-256 that one manifest record holds, in small letters, or None when it holds none."""
    value = record.get("sha256") if isinstance(record, dict) else None
    return value.lower() if isinstance(value, str) and _SHA256_RE.match(value) else None


def _records(entry):
    """The manifest records of the JPG files of one photo: the full-size file, then its small copy."""
    return [record for record in (entry, entry.get("sm")) if isinstance(record, dict) and isinstance(record.get("file"), str)]


def _placeholder_prints(images):
    """The fingerprint of every placeholder picture the manifest lists. Placeholders of one pixel size are one and
    the same file, so a placeholder is recognised under any name. What the script cannot do is look at a picture:
    it knows a placeholder by its fingerprint only."""
    return {_fingerprint(record) for entry in images.values()
            if isinstance(entry, dict) and entry.get("status") == PLACEHOLDER_STATUS
            for record in _records(entry)} - {None}


def _placeholder_files(entry, photos, known):
    """The files of one entry of the manifest, sorted by what is in the site folder today:
    -> (files that are a placeholder picture, files that hold something else)."""
    same, other = [], []
    for record in _records(entry):
        found = photos.sha256(record["file"])
        if found is not None:                           # a file that is not there is reported where a page uses it
            (same if found in known else other).append(record["file"])
    return same, other


def _placeholder_warnings(manifest, photos):
    """The steps of a photo swap that were forgotten (see the note above PLACEHOLDERS)."""
    images = manifest.get("images")
    if not isinstance(images, dict):
        raise BuildError('%s: key "images" must be an object with one entry per image' % MANIFEST_JSON)
    known = _placeholder_prints(images)
    warnings = []
    for name in PLACEHOLDERS:
        entry = images.get(name)
        status = entry.get("status") if isinstance(entry, dict) else None
        if entry is None:
            warnings.append('PLACEHOLDERS in tools/build_pages.py lists "%s", but %s has no image with that name.' % (name, MANIFEST_JSON))
        elif status != PLACEHOLDER_STATUS:
            warnings.append('PLACEHOLDERS in tools/build_pages.py lists "%s", but %s gives it the status "%s". The pages show it '
                            'without a description. If the real photo is in place, delete "%s" from PLACEHOLDERS.'
                            % (name, MANIFEST_JSON, status, name))
        elif all(_fingerprint(record) for record in _records(entry)):   # else the manifest holds nothing to compare with
            other = _placeholder_files(entry, photos, known)[1]
            if other:
                warnings.append('%s %s no longer the placeholder picture, but "%s" is still in the list PLACEHOLDERS in '
                                'tools/build_pages.py, so the pages show the photo without a description. If your photo is in '
                                'place, delete the line with "%s" from that list and run this script again.'
                                % (" and ".join(other), "is" if len(other) == 1 else "are", name, name))
    for name, entry in images.items():
        if isinstance(entry, dict) and entry.get("status") in (PLACEHOLDER_STATUS, OWNER_STATUS) and name not in PLACEHOLDERS:
            same = _placeholder_files(entry, photos, known)[0]
            if same:
                warnings.append('"%s" is not in the list PLACEHOLDERS in tools/build_pages.py, but %s %s still the beige '
                                'placeholder picture. Save your photo under that name (the large one in images, a small copy '
                                'in images/sm), or put the line with "%s" back into the list.'
                                % (name, " and ".join(same), "is" if len(same) == 1 else "are", name))
    return warnings


# ----------------------------------------------------------------------------------------------------------
# A photo that replaced a placeholder is written into image-manifest.json (contract, section 10, decision 27).
# This is the only thing the script ever changes in that file.
# ----------------------------------------------------------------------------------------------------------

def _measured(record, photos):
    """A copy of one manifest record with the pixel size (as a browser shows the photo), the number of bytes and
    the fingerprint of the file that is in the site folder now. Every other key, and the order of the keys, stays."""
    file = record["file"]
    size = photos.size(file)
    if size is None:
        return None
    new = dict(record)
    new.update(width=size[0], height=size[1], bytes=photos.bytes(file), sha256=photos.sha256(file))
    return new


def _record_owner_photos(manifest, names, photos, warnings):
    """-> (the manifest with the replaced photos written into it, their names), or None when nothing changes.

    names are the photos shown by the pages built in this run whose name is not in PLACEHOLDERS and which the
    manifest lists as a placeholder or as an owner-photo. Such a photo is written down when neither its full-size
    file nor its small copy is a placeholder picture: the status becomes owner-photo, and width, height, bytes and
    sha256 of both records become those of the two files. While one of the two files is still a placeholder
    picture nothing is written for that photo (the WARNING of _placeholder_warnings names the file).
    A photo that is written down already, with exactly these values, is not touched, so the manifest only ever
    changes when a photo did. The manifest handed in is left as it is."""
    images = manifest["images"]
    known = _placeholder_prints(images)
    changed = {}
    for name in sorted(names):
        entry = images[name]
        records = _records(entry)
        if _placeholder_files(entry, photos, known) != ([], [record["file"] for record in records]):
            continue
        new = _measured(entry, photos)
        small = _measured(entry["sm"], photos) if len(records) == 2 else None
        if new is None or (len(records) == 2 and small is None):
            continue                                    # not a JPG picture: the page that shows it was not built
        new["status"] = OWNER_STATUS
        if small is not None:
            new["sm"] = small
        if new == entry:
            continue
        if entry.get("status") == OWNER_STATUS and len(records) == 2:
            moved = [_fingerprint(record) != photos.sha256(record["file"]) for record in records]
            if moved[0] != moved[1]:
                warnings.append('%s was saved again since this script last ran, %s was not. Both must show the same photo: '
                                'if you changed the photo, save it under both names (the large one in images, a small copy '
                                'in images/sm).' % (records[not moved[0]]["file"], records[moved[0]]["file"]))
        changed[name] = new
    if not changed:
        return None
    result = dict(manifest)
    result["images"] = {name: changed.get(name, entry) for name, entry in images.items()}
    return result, sorted(changed)


def _manifest_bytes(manifest):
    """image-manifest.json as it is stored: two spaces per level, plain ASCII, LF line ends, a line break at the end."""
    return (json.dumps(manifest, indent=2, ensure_ascii=True) + "\n").encode("ascii")


def _replace_file(path, data):
    """Put data into the file at path in one step: it is written into a temporary file next to it, which is then
    moved over the old file. So a run that is stopped halfway never leaves half a file. Returns False, and writes
    nothing, when the file already holds exactly that."""
    try:
        with open(path, "rb") as f:
            if f.read() == data:
                return False
    except OSError:
        pass
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    temp = path + ".tmp"
    try:
        with open(temp, "wb") as f:
            f.write(data)
        os.replace(temp, path)
    except OSError:
        try:
            os.remove(temp)
        except OSError:
            pass
        raise
    return True


def _build_page(page, site_dir, pages_dir, pages_shown, raw_site, raw_manifest, year, warnings, photos, replaced=None):
    raw_content = _read_json(site_dir, page.content)
    content = _wrap(raw_content, page.content)
    for key in ("slug", "path", "title", "description", "h1"):
        _need(content, key, str)
    for key, wanted in (("slug", page.slug), ("path", page.path)):
        if content[key] != wanted:
            raise BuildError('%s is "%s", the page table in tools/build_pages.py says "%s"' % (_where(content, key), content[key], wanted))
    file_name = page.module.rsplit("/", 1)[-1]
    path = os.path.join(pages_dir, file_name)
    shown = "%s/%s" % (pages_shown, file_name)
    module = _load_module(path, shown, page.slug)
    ctx = Ctx(page, content, _wrap(raw_site, SITE_JSON), _wrap(raw_manifest, MANIFEST_JSON), photos, warnings, replaced)
    parts = _render(module, ctx, path, shown)
    jsonld = None
    if page.slug == JSONLD_SLUG:
        jsonld = _read_json(site_dir, JSONLD_JSON, optional=True, any_type=True)
        if jsonld is None:
            warnings.append("%s not found, the home page is built without the JSON-LD script." % JSONLD_JSON)
    # The shared layout works on its own fresh copies, so nothing a module did to ctx can reach it.
    site = _wrap(raw_site, SITE_JSON)
    layout = Ctx(page, _wrap(raw_content, page.content), site, _wrap(raw_manifest, MANIFEST_JSON), photos, warnings)
    text = _document(page, layout, parts, site, jsonld, year)
    problems, notes = _audit(text, _site_url(site), page, site_dir)
    if problems:
        raise BuildError("%s: the page %s was not written. %s" % (shown, page.output, " | ".join(problems)))
    warnings.extend(notes)
    return text


def _write(path, text):
    """Write the page as UTF-8 with LF line endings. Returns False when the file already holds exactly that."""
    data = text.encode("utf-8")
    try:
        with open(path, "rb") as f:
            if f.read() == data:
                return False
    except OSError:
        pass
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return True


def build(site_dir, pages_dir=None, out_dir=None, slugs=None, year=None, log=print, warn=None):
    """Build the pages named in slugs (all when None). Returns the number of things that went wrong: the pages
    that could not be built, plus one when the manifest could not be written."""
    if warn is None:
        def warn(message):
            print(message, file=sys.stderr)
    pages_shown = PAGES_DIR if pages_dir is None else _shown(pages_dir).rstrip("/")
    pages_dir = os.path.join(site_dir, *PAGES_DIR.split("/")) if pages_dir is None else pages_dir
    out_dir = site_dir if out_dir is None else out_dir
    year = datetime.date.today().year if year is None else year
    pages = [page for page in REGISTRY if slugs is None or page.slug in slugs]

    raw_site = _read_json(site_dir, SITE_JSON)
    raw_manifest = _read_json(site_dir, MANIFEST_JSON)
    photos = _Photos(site_dir)
    warnings = _placeholder_warnings(raw_manifest, photos)

    failed = 0
    replaced = set()                                # the replaced photos that the pages written in this run show
    for page in pages:
        shown = set()
        try:
            text = _build_page(page, site_dir, pages_dir, pages_shown, raw_site, raw_manifest, year, warnings, photos, shown)
            changed = _write(os.path.join(out_dir, *page.output.split("/")), text)
        except BuildError as e:
            failed += 1
            warn("ERROR    %s" % e)
            continue
        except OSError as e:
            failed += 1
            warn("ERROR    %s: cannot be written (%s)" % (page.output, e.strerror or e))
            continue
        replaced |= shown
        log("%s  %s" % ("written  " if changed else "unchanged", page.output))
    # A photo that replaced a placeholder is written into the manifest (decision 27). Like the pages, the
    # manifest goes into the folder given with --out when there is one. In every other case, and that is every
    # ordinary run, the manifest is not opened for writing at all.
    manifest_failed = 0
    recorded = _record_owner_photos(raw_manifest, replaced, photos, warnings)
    if recorded is not None:
        try:
            changed = _replace_file(os.path.join(out_dir, MANIFEST_JSON), _manifest_bytes(recorded[0]))
            log("%s  %s  (%s recorded as %s)" % ("written  " if changed else "unchanged", MANIFEST_JSON, ", ".join(recorded[1]), OWNER_STATUS))
        except OSError as e:
            manifest_failed = 1
            warn("ERROR    %s: cannot be written (%s). Not recorded in it yet: %s. Close any program that has the "
                 "file open and run this script again." % (MANIFEST_JSON, e.strerror or e, ", ".join(recorded[1])))
    for message in dict.fromkeys(warnings):         # every message once, in the order they came up
        warn("WARNING  %s" % message)
    done = len(pages) - failed
    where = "" if out_dir == site_dir else " in %s" % _shown(out_dir)
    if failed:
        warn("%d of %d pages could not be built, %d built%s." % (failed, len(pages), done, where))
    else:
        log("%d %s built%s." % (done, "page" if done == 1 else "pages", where))
    return failed + manifest_failed


def _print_registry():
    head = ("slug", "address", "content file", "page module", "output")
    rows = [head] + [tuple(page) for page in REGISTRY]
    widths = [max(len(row[i]) for row in rows) for i in range(len(head))]
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(
        prog="build_pages.py",
        description="Build the HTML pages of hairbygerta.com from content/*.json and tools/pages/*.py. "
                    "The long note at the top of this file explains everything else.")
    parser.add_argument("--only", metavar="SLUG[,SLUG]", help="build only these pages and write nothing else, for example --only home,gallery")
    parser.add_argument("--out", metavar="DIR", help="for testing: write the pages (and image-manifest.json, should a replaced photo "
                                                     "have to be recorded) into DIR instead of the site folder")
    parser.add_argument("--pages-dir", metavar="DIR", help="for testing: load the page modules from DIR instead of tools/pages")
    parser.add_argument("--list", action="store_true", help="show the page table and stop")
    args = parser.parse_args(argv)

    if args.list:
        _print_registry()
        return 0
    slugs = None
    if args.only is not None:
        slugs = [s.strip() for s in args.only.split(",") if s.strip()]
        known = [page.slug for page in REGISTRY]
        unknown = [s for s in slugs if s not in known]
        if unknown or not slugs:
            print('ERROR    --only: %s. The pages are: %s' % ('"%s" is not a page' % unknown[0] if unknown else "no page named", ", ".join(known)),
                  file=sys.stderr)
            return 1
    site_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        failed = build(site_dir, pages_dir=args.pages_dir, out_dir=args.out, slugs=slugs)
    except BuildError as e:
        print("ERROR    %s" % e, file=sys.stderr)
        print("Nothing was written.", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
