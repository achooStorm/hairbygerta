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
    section.meet                            "meet"
      h2#meet-h.serif                       "meet.heading"
      p.t1, div.p1 > img                    "meet.paragraph_1", "meet.portrait"
      p.t2, div.p2 > img                    "meet.paragraph_2", "meet.large"
    section.reach                           "book", the beige box with the Text button and the Call button
      h2#reach-h.serif                      "book.heading"
      div.reach-btns
        a.reach-btn.reach-text              "book.text": opens the text message app with Gerta's number and
                                            "book.text.message" already written
        a.reach-btn.reach-call              "book.call": calls the number
      a.reach-num                           "book.phone", calls the number too. The stylesheet shows it on
                                            screens wider than a phone

Where the words come from
    content/home.json    every text of the page, the photos and the size each photo is shown at
    content/site.json    the three addresses behind the phone number, the Text button and the street
                         address ("tel_href", "sms_href" and "maps_href")

To change a text or a photo, edit content/home.json and run
    python tools/build_pages.py --only home
This module holds no text that a visitor reads. The only words typed here are the two labels below, which
screen readers speak and nobody sees.
"""
import urllib.parse

SLUG = "home"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message

# Spoken by screen readers, never shown (contract, section 7). %s is the hours text.
HOURS_LABEL = "Hours: %s"
PHOTO_ROW_LABEL = "Featured work"
# Each photo of the row is a link to the Gallery, because on a phone people tap a photo and expect more of
# them. A screen reader says what the photo shows and where the link leads. %s is the description of the
# photo. A photo without a description (a placeholder) is announced with GALLERY_LINK_LABEL alone.
PHOTO_LINK_LABEL = "%s. Open the Gallery"
GALLERY_LINK_LABEL = "Open the Gallery"
GALLERY_PATH = "/gallery/"

# The map pin in front of the street address. It is decoration, so screen readers skip it.
PIN = '<span class="pin" aria-hidden="true">&#128205;</span>'

# The two drawings of the Text button and the Call button (section.reach). Decoration: the words of a button say
# what it does. Both are Phosphor icons in the Bold style, a speech bubble (ph:chat-circle-dots-bold) and the
# handset of the Call bar (ph:phone-bold, the very path of CALL_ICON in tools/build_pages.py), with the paths of
# the set unchanged. License: tools/licenses/MIT-PhosphorIcons.txt.
_REACH_SVG = ('<svg class="reach-icon" viewBox="0 0 256 256" width="20" height="20" fill="currentColor" aria-hidden="true" '
              'focusable="false"><path d="%s"/></svg>')
REACH_ICONS = {
    "text": _REACH_SVG % (
        "M120 128a16 16 0 1 1-16-16a16 16 0 0 1 16 16m32-16a16 16 0 1 0 16 16a16 16 0 0 0-16-16m84 16a108 108 0 0 1-"
        "157.23 96.15L46.34 235A20 20 0 0 1 21 209.66l10.81-32.43A108 108 0 1 1 236 128m-24 0a84 84 0 1 0-156.73 42."
        "06a12 12 0 0 1 1 9.81l-9.93 29.79l29.79-9.93a12.1 12.1 0 0 1 3.8-.62a12 12 0 0 1 6 1.62A84 84 0 0 0 212 128"),
    "call": _REACH_SVG % (
        "m224 154.8l-47.09-21.11l-.18-.08a19.94 19.94 0 0 0-19 1.75a13 13 0 0 0-1.12.84l-22.31 19c-13-7.05-26.43-20."
        "37-33.49-33.21l19.06-22.66a12 12 0 0 0 .85-1.15a20 20 0 0 0 1.66-18.83a1.4 1.4 0 0 1-.08-.18L101.2 32a20.06 "
        "20.06 0 0 0-20.78-11.85A60.27 60.27 0 0 0 28 80c0 81.61 66.39 148 148 148a60.27 60.27 0 0 0 59.85-52.42A20."
        "06 20.06 0 0 0 224 154.8M176 204A124.15 124.15 0 0 1 52 80a36.29 36.29 0 0 1 28.48-35.54l18.82 42l-19.16 22."
        "82a12 12 0 0 0-.86 1.16A20 20 0 0 0 78 130.08c9.42 19.28 28.83 38.56 48.31 48a20 20 0 0 0 19.69-1.45a12 12 0 "
        "0 0 1.11-.85l22.43-19.07l42 18.81A36.29 36.29 0 0 1 176 204"),
}

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


def _text_href(sms_href, message):
    """The address of the Text button: the text message app, Gerta's number, the message already written.

    "sms:NUMBER?&body=MESSAGE" is the one form that both an iPhone and an Android phone understand, and the
    form the script uses for the text link of the Contact page (js/site.js). Every character of the message
    that is not a letter or a digit is written as a percent code, so nothing in it can end the address early.
    """
    if not sms_href.lower().startswith("sms:") or "?" in sms_href or "&" in sms_href:
        raise ValueError('content/site.json: key "sms_href" must be "sms:" and the phone number, nothing after it '
                         '(it is "%s"). The message of the Text button is "book.text.message" in %s'
                         % (sms_href, CONTENT_FILE))
    if not message.strip():
        raise _wrong("book.text.message", "is empty. Write the few words the text message starts with")
    return "%s?&body=%s" % (sms_href, urllib.parse.quote(message.strip(), safe=""))


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
    lines += [
        "</section>",
        '<section class="meet" aria-labelledby="meet-h">',
        '  <h2 id="meet-h" class="serif">%s</h2>' % esc(meet["heading"]),
        '  <p class="t1">%s</p>' % esc(meet["paragraph_1"]),
        '  <div class="p1">%s</div>' % _photo(ctx, meet["portrait"], sizes=PORTRAIT_SIZES),
        '  <p class="t2">%s</p>' % esc(meet["paragraph_2"]),
        '  <div class="p2">%s</div>' % _photo(ctx, meet["large"], sizes=LARGE_PHOTO_SIZES),
        "</section>",
        # The beige box with the two ways to reach Gerta (21 November 2026, decision 68). It took the place of
        # Gerta's own text, which the helper found too long. Text comes first: it is the button the box was made
        # for. Each button is a plain link, so both work without the script.
        '<section class="reach" aria-labelledby="reach-h">',
        '  <h2 id="reach-h" class="serif">%s</h2>' % esc(book["heading"]),
        '  <div class="reach-btns">',
        '    <a class="reach-btn reach-text" href="%s">%s<span>%s</span></a>'
        % (esc(_text_href(site["sms_href"], book["text"]["message"])), REACH_ICONS["text"], esc(book["text"]["label"])),
        '    <a class="reach-btn reach-call" href="%s">%s<span>%s</span></a>'
        % (esc(site["tel_href"]), REACH_ICONS["call"], esc(book["call"]["label"])),
        "  </div>",
        '  <a class="reach-num" href="%s">%s</a>' % (esc(site["tel_href"]), esc(book["phone"])),
        "</section>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
