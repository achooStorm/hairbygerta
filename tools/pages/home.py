"""The home page, / (index.html), built as section 7 of tools/CONTRACT.md lists it (decision 45):

    section.hero                            the first screen
      div.hero-text
        h1#hero-h                           "h1", the business name, in three spans (the stylesheet decides
                                            where the lines break)
        p.lead                              "hero.welcome"
        p.actions                           a.btn.btn-call "hero.call" (calls the number) and
                                            a.text-link "hero.text" (starts a text message)
        p.hours                             "hero.hours"
      div.hero-photos > div.frame x 2       "hero.photos", tall frames, revealed from top to bottom
    div.shade                               the shade strip, once, right under the hero
    section.svc-list                        "services": h2, four groups (h3 + ul), the link to the Services page
    section.work                            "photo_row", only the photos that are no longer placeholders
    section.meet                            "meet": h2, two paragraphs, and its photos once they are real
    section.find                            "find": h2, salon, address, hours, the Google Maps link

Where the words come from
    content/home.json    every text of the page, the photos and the shape of each frame
    content/site.json    the phone link (tel_href), the Maps link (maps_href), and the business facts the page
                         is checked against (phone, hours, salon, address_one_line)

A photo whose name is in PLACEHOLDERS (tools/build_pages.py) is never shown (decision 44). The page leaves it
out and the layout closes up, so a photo put in with tools/add_photo.py appears by itself.

To change a text or a photo, edit content/home.json and run
    python tools/build_pages.py --only home
This module holds no text that a visitor reads. The only words typed here are the label below, which screen
readers speak and nobody sees.
"""
SLUG = "home"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message

# Spoken by screen readers, never shown (contract, section 7): the name of the row of photos.
PHOTO_ROW_LABEL = "Featured work"

# The content file holds four photos for the row (the old page showed four).
PHOTOS_IN_ROW = 4

# How wide a photo is on screen, for the browser to pick between the small copy and the full file. These
# texts never change how the page looks, they only steer which file is fetched. 760 px is the phone breakpoint
# of the stylesheet, "vw" is one hundredth of the width of the window. The two hero photos stand side by side
# on every screen, a little under half the window wide on a phone. On a wider screen the larger one is at most
# about 380 px wide and the smaller one about 290 px. The row and the Meet Gerta photos are two across on a
# phone and four across on a wide screen.
HERO_SIZES = ("(max-width: 760px) 46vw, 380px", "(max-width: 760px) 46vw, 290px")
ROW_SIZES = "(max-width: 760px) 46vw, 282px"


def _wrong(key, problem):
    """The error that stops the build and names the content file and the key."""
    return ValueError('%s: key "%s" %s' % (CONTENT_FILE, key, problem))


def _real(ctx, slots):
    """The image slots whose photo is no longer a placeholder, in the order of the content file."""
    return [slot for slot in slots if not ctx.is_placeholder(slot["file"])]


def _frame(ctx, slot, lazy=True, sizes=None):
    """One photo in a tall frame."""
    return '<div class="frame">%s</div>' % ctx.img(slot["file"], slot["alt"], slot["width"], slot["height"],
                                                  lazy=lazy, sizes=sizes)


def _name(ctx, name):
    """The business name in three spans: "Hair &", "Makeup" and "by Gerta". The stylesheet shows the first two on
    one line on most screens. The spaces between the spans keep the name one text for search engines and
    screen readers."""
    head, sep, tail = name.partition(" by ")
    if not sep:
        return "<span>%s</span>" % ctx.esc(name)
    first, space, second = head.rpartition(" ")
    parts = [first, second] if space else [head]
    parts.append("by " + tail)
    return " ".join("<span>%s</span>" % ctx.esc(part) for part in parts)


def render(ctx):
    c, site, esc = ctx.content, ctx.site, ctx.esc
    hero, services, meet, find, row = c["hero"], c["services"], c["meet"], c["find"], c["photo_row"]

    # The page shows the business facts of content/site.json in its own words, so check that they agree.
    if site["phone"] not in hero["call"]:
        raise _wrong("hero.call", 'must show the phone number of content/site.json ("%s"), because the button calls it'
                     % site["phone"])
    for key, value in (("hero.hours", hero["hours"]), ("find.hours", find["hours"])):
        if value != site["hours"]:
            raise _wrong(key, 'must be the hours of content/site.json, word for word ("%s")' % site["hours"])
    if find["salon"] != site["salon"]:
        raise _wrong("find.salon", 'must be the salon of content/site.json ("%s")' % site["salon"])
    if find["address"] != site["address_one_line"]:
        raise _wrong("find.address", 'must be address_one_line of content/site.json ("%s")' % site["address_one_line"])
    if not isinstance(row, list) or len(row) != PHOTOS_IN_ROW:
        raise _wrong("photo_row", "must be a list of exactly %d photos" % PHOTOS_IN_ROW)

    hero_photos = _real(ctx, hero["photos"])
    lines = [
        '<section class="hero" aria-labelledby="hero-h">',
        '  <div class="wrap">',
        '    <div class="hero-text">',
        '      <h1 id="hero-h">%s</h1>' % _name(ctx, c["h1"]),
        '      <p class="lead">%s</p>' % esc(hero["welcome"]),
        '      <p class="actions"><a class="btn btn-call" href="%s">%s</a> <a class="text-link" href="%s">%s</a></p>'
        % (esc(site["tel_href"]), esc(hero["call"]), esc(ctx.sms_href), esc(hero["text"])),
        '      <p class="hours">%s</p>' % esc(hero["hours"]),
        "    </div>",
    ]
    if hero_photos:
        # On screen as soon as the page opens, so fetched at once (loading="eager").
        lines.append('    <div class="hero-photos">')
        lines += ["      " + _frame(ctx, slot, lazy=False, sizes=HERO_SIZES[min(i, 1)])
                  for i, slot in enumerate(hero_photos)]
        lines.append("    </div>")
    lines += [
        "  </div>",
        "</section>",
        ctx.shade(),
        '<section class="svc-list" aria-labelledby="services-h">',
        '  <div class="wrap">',
        '    <h2 id="services-h">%s</h2>' % esc(services["heading"]),
        '    <div class="groups">',
    ]
    for group in services["groups"]:
        lines += [
            '      <div class="group">',
            "        <h3>%s</h3>" % esc(group["heading"]),
            "        <ul>",
        ]
        lines += ["          <li>%s</li>" % esc(name) for name in group["items"]]
        lines += ["        </ul>", "      </div>"]
    more = services["more"]
    lines += [
        "    </div>",
        '    <p class="more"><a href="%s">%s</a></p>' % (esc(ctx.url(more["path"])), esc(more["label"])),
        "  </div>",
        "</section>",
    ]

    work = _real(ctx, row)
    if work:
        lines += ['<section class="work" aria-label="%s">' % esc(PHOTO_ROW_LABEL), '  <div class="wrap">']
        lines += ["    " + _frame(ctx, slot, sizes=ROW_SIZES) for slot in work]
        lines += ["  </div>", "</section>"]

    meet_photos = _real(ctx, [meet["portrait"], meet["large"]])
    lines += [
        '<section class="meet" aria-labelledby="meet-h">',
        '  <div class="wrap">',
        '    <h2 id="meet-h">%s</h2>' % esc(meet["heading"]),
        '    <div class="meet-text">',
        "      <p>%s</p>" % esc(meet["paragraph_1"]),
        "      <p>%s</p>" % esc(meet["paragraph_2"]),
        "    </div>",
    ]
    if meet_photos:
        lines.append('    <div class="meet-photos">')
        lines += ["      " + _frame(ctx, slot, sizes=ROW_SIZES) for slot in meet_photos]
        lines.append("    </div>")
    lines += [
        "  </div>",
        "</section>",
        '<section class="find" aria-labelledby="find-h">',
        '  <div class="wrap">',
        '    <h2 id="find-h">%s</h2>' % esc(find["heading"]),
        '    <div class="find-place">',
        '      <p class="salon">%s</p>' % esc(find["salon"]),
        '      <p class="addr">%s</p>' % esc(find["address"]),
        "    </div>",
        '    <p class="find-hours">%s</p>' % esc(find["hours"]),
        '    <p class="find-map"><a href="%s" target="_blank" rel="noopener">%s</a></p>'
        % (esc(site["maps_href"]), esc(find["map_label"])),
        "  </div>",
        "</section>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
