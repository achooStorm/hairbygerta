"""The home page, / (index.html), built as section 7 of tools/CONTRACT.md lists it:

    p.site-title.serif > a                  the business name, a link to the home page
    section.hero-box                        the beige box
      h1#hero-h.serif                       "h1" (the same text as "hero.heading")
      hr.dots                               the dotted rule
      p.welcome                             "hero.welcome"
      a.btn                                 "hero.button", goes to the Book Online page
      a.phone                               "hero.phone", calls the number
      p.salon                               "hero.salon"
      a.addr                                "hero.address" behind a map pin, opens the map in a new tab
      div.marquee > div.track > span x 6    "hero.hours", the line that scrolls
    section.photo-row > img x 4             "photo_row"
    section.meet                            "meet"
      h2#meet-h.serif                       "meet.heading"
      p.t1, div.p1 > img                    "meet.paragraph_1", "meet.portrait"
      p.t2, div.p2 > img                    "meet.paragraph_2", "meet.large"

Where the words come from
    content/home.json    every text of the page, the photos and the size each photo is shown at
    content/site.json    the two addresses behind the phone number and the street address
                         ("tel_href" and "maps_href")

To change a text or a photo, edit content/home.json and run
    python tools/build_pages.py --only home
This module holds no text that a visitor reads. The only words typed here are the two labels below, which
screen readers speak and nobody sees.
"""
SLUG = "home"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message

# Spoken by screen readers, never shown (contract, section 7). %s is the hours text.
HOURS_LABEL = "Hours: %s"
PHOTO_ROW_LABEL = "Featured work"

# The map pin in front of the street address. It is decoration, so screen readers skip it.
PIN = '<span class="pin" aria-hidden="true">&#128205;</span>'

# The stylesheet lays the photo row out as four columns, so the row holds four photos.
PHOTOS_IN_ROW = 4

# How wide a photo is on screen, for the browser to pick between the small copy and the full file. These
# two texts never change how the page looks, they only steer which file is fetched. 760 px is the phone
# breakpoint of the stylesheet, and "vw" is one hundredth of the width of the window.
# The photo row: on a phone it is two photos wide, so a photo is at most half the window wide. On a wider
# screen the four photos share the width of the window, each is a little under a quarter of it.
PHOTO_ROW_SIZES = "(max-width: 760px) 50vw, 24vw"
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


def render(ctx):
    c, site, esc = ctx.content, ctx.site, ctx.esc
    hero, meet, row = c["hero"], c["meet"], c["photo_row"]

    # The heading is in the content file twice and on the page once.
    if hero["heading"] != c["h1"]:
        raise _wrong("hero.heading", 'must be the very same text as "h1". The page shows this heading once, '
                                     "so when one of the two is edited the other needs the same change")
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
        '  <h1 id="hero-h" class="serif">%s</h1>' % esc(c["h1"]),
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
    lines += ["  " + _photo(ctx, slot, lazy=False, sizes=PHOTO_ROW_SIZES) for slot in row]
    lines += [
        "</section>",
        '<section class="meet" aria-labelledby="meet-h">',
        '  <h2 id="meet-h" class="serif">%s</h2>' % esc(meet["heading"]),
        '  <p class="t1">%s</p>' % esc(meet["paragraph_1"]),
        '  <div class="p1">%s</div>' % _photo(ctx, meet["portrait"]),
        '  <p class="t2">%s</p>' % esc(meet["paragraph_2"]),
        '  <div class="p2">%s</div>' % _photo(ctx, meet["large"], sizes=LARGE_PHOTO_SIZES),
        "</section>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
