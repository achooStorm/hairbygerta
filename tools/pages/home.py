"""The home page, / (index.html), built as section 7 of tools/CONTRACT.md lists it:

    p.site-title.serif > a                  the business name, a link to the home page
    section.hero-box                        the beige box
      h1#hero-h                             "h1", what Gerta does and where, one small line
      p.tagline.serif                       "hero.tagline", the large italic line under the h1
      hr.dots                               the dotted rule
      p.welcome                             "hero.welcome"
      a.btn                                 "hero.button", goes to the Book Online page
      a.phone                               "hero.phone", calls the number
      p.salon                               "hero.salon"
      a.addr                                "hero.address" behind a map pin, opens the map in a new tab
      div.marquee > div.track > span x 6    "hero.hours", the line that scrolls
    section.photo-row > a x 3 > img         "photo_row", each photo a link to the Gallery
      a.row-cue > span                      "photo_row_cue", the small blue label that says so for a few seconds on
                                            phones and tablets, a link to the Gallery too (decision 72). Left out
                                            when the key is not there
    section.meet                            "meet"
      h2#meet-h.serif                       "meet.heading"
      p.t1, div.p1 > img                    "meet.paragraph_1", "meet.portrait"
      p.t2, div.p2 > img                    "meet.paragraph_2", "meet.large"
    p.more-links                            "more_links_html", the line of links to the three service pages
                                            (decision 73)
    section#book.reach                      "book", the beige box with the Text button and the Call button,
                                            built by ctx.reach (tools/build_pages.py):
      h2#reach-h.serif                      "book.heading"
      p.reach-line.serif                    "reach_line" of content/site.json with "book.phone" as a link:
                                            the one line a computer with a mouse shows instead (decision 75)
      div.reach-btns
        a.reach-btn.reach-text              "book.text": opens the text message app with Gerta's number and
                                            the first words already written (ctx.text_href())
        a.reach-btn.reach-call              "book.call": calls the number
      a.reach-num                           "book.phone", calls the number too. The stylesheet shows it on
                                            screens wider than a phone

Where the words come from
    content/home.json    every text of the page, the photos and the size each photo is shown at
    content/site.json    the addresses behind the phone number, the Text button and the street address
                         ("tel_href", "sms_href" with "sms_message", and "maps_href")

To change a text or a photo, edit content/home.json and run
    python tools/build_pages.py --only home
This module holds no text that a visitor reads. The only words typed here are the two labels below, which
screen readers speak and nobody sees.
"""
import math


SLUG = "home"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message

# Spoken by screen readers, never shown (contract, section 7). %s is the hours text.
HOURS_LABEL = "Hours: %s"
# "Featured work" until 21 November 2026: two of the three photos are licensed stock photos, not Gerta's own
# work (decision 73).
PHOTO_ROW_LABEL = "Featured photos"
# Each photo of the row is a link to the Gallery, because on a phone people tap a photo and expect more of
# them. A screen reader says what the photo shows and where the link leads. %s is the description of the
# photo. A photo without a description (a placeholder) is announced with GALLERY_LINK_LABEL alone.
PHOTO_LINK_LABEL = "%s. Open the Gallery"
GALLERY_LINK_LABEL = "Open the Gallery"
GALLERY_PATH = "/gallery/"

# The label on the photo row (decision 72): on a phone or a tablet nothing shows that the three photos are links,
# so a small blue label says it for a few seconds, "Tap for more photos" with a four-point star in front. Its text
# and the seconds it stays are "photo_row_cue" in content/home.json. js/site.js switches it on when the visitor has
# started to scroll and the photos are in view, and off again after the seconds of data-seconds, and css/style.css
# shows it on touch screens only. Screen readers skip it: every photo link already says "Open the Gallery".
# The star was drawn for this site (four curved points in a 24 px square), so it needs no license.
CUE_STAR = ('<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true" focusable="false">'
            '<path d="M12 1.5c.7 6.3 4.2 9.8 10.5 10.5-6.3.7-9.8 4.2-10.5 10.5-.7-6.3-4.2-9.8-10.5-10.5 6.3-.7 9.8-4.2 '
            '10.5-10.5z"/></svg>')
# How long the label may stay, in seconds. Under 2 nobody could read it, and over 20 it is no longer a hint.
CUE_SECONDS_MIN, CUE_SECONDS_MAX = 2, 20

# The map pin in front of the street address. It is decoration, so screen readers skip it.
PIN = '<span class="pin" aria-hidden="true">&#128205;</span>'

# The stylesheet lays the photo row out as three columns, so the row holds three photos (decision 56).
PHOTOS_IN_ROW = 3

# How wide a photo is on screen, for the browser to pick between the small copy and the full file. These
# two texts never change how the page looks, they only steer which file is fetched. 760 px is the phone
# breakpoint of the stylesheet, and "vw" is one hundredth of the width of the window.
# The photo row: three photos share the width of the window on every screen, so each is a little under a
# third of it.
PHOTO_ROW_SIZES = "(max-width: 760px) 34vw, 32vw"
# The makeup photo of Meet Gerta: as wide as the text on a phone, 313 px up to 1100 px, and from there about
# a quarter of the window (26 %, at most 440 px, decision 58).
PORTRAIT_SIZES = "(max-width: 760px) 100vw, (max-width: 1100px) 313px, 26vw"
# The large photo of Meet Gerta: on a phone it runs from one edge of the screen to the other. Up to 1100 px
# (the second breakpoint of the stylesheet) it is at most 424 px wide, which is up to half of such a window.
# On a wider screen it grows with the window and takes about a third of its width (35 % of the room between
# the side margins). If the stylesheet changes these shares, bring the numbers in line with it.
LARGE_PHOTO_SIZES = "(max-width: 760px) 100vw, (max-width: 1100px) 424px, 35vw"


def _wrong(key, problem):
    """The error that stops the build and names the content file and the key."""
    return ValueError('%s: key "%s" %s' % (CONTENT_FILE, key, problem))


def _photo(ctx, slot, lazy=True, sizes=None):
    """The img of one image slot of the content file, at the size the slot gives."""
    return ctx.img(slot["file"], slot["alt"], slot["width"], slot["height"], lazy=lazy, sizes=sizes)


def _row_cue(ctx, gallery):
    """The label on the photo row, or nothing when content/home.json has no "photo_row_cue". gallery is the
    address of the Gallery page, ready for the HTML."""
    cue = ctx.content.get("photo_row_cue")
    if cue is None:
        return None
    if not isinstance(cue, dict):
        raise _wrong("photo_row_cue", 'must hold "label" and "seconds" between curly brackets (or be deleted, then '
                                      "the photo row has no label)")
    label, seconds = cue.get("label"), cue.get("seconds")
    if not isinstance(label, str) or not label.strip():
        raise _wrong("photo_row_cue.label", "must be the words of the label, for example Tap for more photos")
    if (isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds)
            or not CUE_SECONDS_MIN <= seconds <= CUE_SECONDS_MAX):
        raise _wrong("photo_row_cue.seconds", "must be a number from %d to %d, the seconds the label stays (it is 4 on "
                                              "the finished page)" % (CUE_SECONDS_MIN, CUE_SECONDS_MAX))
    # The label is a link to the Gallery itself: it is wider than the photo under it and reaches over the gaps
    # between the photos, and a tap anywhere on it has to open the Gallery. The a is the place of the label and
    # never moves, which is what js/site.js watches. The span inside it is the blue label, which slides and fades.
    # tabindex="-1" keeps the Tab key away from it, as aria-hidden keeps screen readers away: both already have
    # the three photo links.
    return ('  <a class="row-cue" href="%s" aria-hidden="true" tabindex="-1" data-seconds="%s"><span>%s%s</span></a>'
            % (gallery, ctx.esc("%g" % seconds), CUE_STAR, ctx.esc(label.strip())))


def render(ctx):
    c, site, esc = ctx.content, ctx.site, ctx.esc
    hero, meet, row, book = c["hero"], c["meet"], c["photo_row"], c["book"]

    # Since 21 November 2026 the h1 says what Gerta does and where, and "It's Your Day to Shine!" is the tagline.
    if hero["tagline"] == c["h1"]:
        raise _wrong("hero.tagline", 'must differ from "h1": the h1 is the small line above the tagline, the page '
                                     "would show the same words twice")
    # The stylesheet slides the hours line to the left by half of its length and starts over. That only
    # looks seamless when the line is made of two equal halves, so the number of copies must be even.
    copies = hero["marquee_repeat"]
    if isinstance(copies, bool) or not isinstance(copies, int) or copies < 2 or copies % 2:
        raise _wrong("hero.marquee_repeat", "must be an even whole number, 2 or more (it is 6 on the finished page)")
    if not isinstance(row, list) or len(row) != PHOTOS_IN_ROW:
        raise _wrong("photo_row", "must be a list of exactly %d photos, because the row is %d photos wide"
                     % (PHOTOS_IN_ROW, PHOTOS_IN_ROW))

    hours = hero["hours"]
    lines = [
        '<p class="site-title serif"><a href="%s">%s</a></p>' % (esc(ctx.url("/")), esc(c["site_title"])),
        '<section class="hero-box" aria-labelledby="hero-h">',
        '  <h1 id="hero-h">%s</h1>' % esc(c["h1"]),
        '  <p class="tagline serif">%s</p>' % esc(hero["tagline"]),
        '  <hr class="dots">',
        '  <p class="welcome">%s</p>' % esc(hero["welcome"]),
        '  <a class="btn" href="%s">%s</a>' % (esc(ctx.url(hero["button"]["path"])), esc(hero["button"]["label"])),
        '  <a class="phone" href="%s">%s</a>' % (esc(site["tel_href"]), esc(hero["phone"])),
        '  <p class="salon">%s</p>' % esc(hero["salon"]),
        '  <a class="addr" href="%s" target="_blank" rel="noopener">%s%s</a>'
        % (esc(site["maps_href"]), PIN, esc(hero["address"])),
        # Screen readers hear the hours once, from the label. The moving copies are hidden from them. The
        # copies stand in one line with nothing between them, so the scrolling line has no uneven gaps.
        '  <div class="marquee" role="img" aria-label="%s">' % esc(HOURS_LABEL % hours),
        '    <div class="track" aria-hidden="true">%s</div>' % (("<span>%s</span>" % esc(hours)) * copies),
        "  </div>",
        "</section>",
        '<section class="photo-row" aria-label="%s">' % esc(PHOTO_ROW_LABEL),
    ]
    # The row is high on the page and on screen as soon as the page opens, so these four are fetched at
    # once (loading="eager"). The two photos of Meet Gerta are further down and are fetched when the
    # visitor scrolls near them (loading="lazy").
    gallery = esc(ctx.url(GALLERY_PATH))
    for slot in row:
        described = "" if ctx.is_placeholder(slot["file"]) else (slot["alt"] or "").strip()
        label = PHOTO_LINK_LABEL % described if described else GALLERY_LINK_LABEL
        lines.append('  <a href="%s" aria-label="%s">%s</a>'
                     % (gallery, esc(label), _photo(ctx, slot, lazy=False, sizes=PHOTO_ROW_SIZES)))
    # The label comes after the three links, so the order of the Tab key and of a screen reader stays as it was.
    cue = _row_cue(ctx, gallery)
    if cue:
        lines.append(cue)
    lines += [
        "</section>",
        '<section class="meet" aria-labelledby="meet-h">',
        '  <h2 id="meet-h" class="serif">%s</h2>' % esc(meet["heading"]),
        '  <p class="t1">%s</p>' % esc(meet["paragraph_1"]),
        '  <div class="p1">%s</div>' % _photo(ctx, meet["portrait"], sizes=PORTRAIT_SIZES),
        '  <p class="t2">%s</p>' % esc(meet["paragraph_2"]),
        '  <div class="p2">%s</div>' % _photo(ctx, meet["large"], sizes=LARGE_PHOTO_SIZES),
        "</section>",
        # One line of links to the three service pages (decision 73), right above the box. The menu keeps its
        # five links, so this line is the way to those pages from the home page.
        '<p class="more-links">%s</p>' % ctx.inline(c["more_links_html"]),
        # The beige box with the two ways to reach Gerta (21 November 2026, decision 68). It took the place of
        # Gerta's own text, which the helper found too long. The box itself is ctx.reach, because the Services
        # page ends with the same one (decision 70).
        ctx.reach(book),
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
