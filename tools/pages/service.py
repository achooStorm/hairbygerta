"""Page module of the three service pages (decision 73), one layout for the three:

    /balayage-staten-island/                   content/balayage-staten-island.json
    /bridal-hair-makeup-staten-island/         content/bridal-hair-makeup-staten-island.json
    /keratin-brazilian-blowout-staten-island/  content/keratin-brazilian-blowout-staten-island.json

Contract, section 7, Service pages:

    div.service
      h1.service-title.serif      "h1", the name of the page
      p.service-intro             "intro", two sentences under it
      div.service-photos          "photos", 1 to 4 of Gerta's own photos side by side. Left out when the list is
        img (or picture > img)    empty: a page without a photo of her own work shows none rather than a stock photo
      div.service-text            "blocks", the text in Gerta's voice: h2, h3, p and ul, exactly as the blocks of a
                                  policy page (ctx.blocks). The FAQ is an h2 with one h3 per question and a p per
                                  answer. The last part is How to book, with its links to the Services page and the
                                  Gallery
      section.reach               "book", the beige box "Book with Gerta" with the Text button and the Call button,
                                  built by ctx.reach (tools/build_pages.py), the box that ends the home page and the
                                  Services page

Every word a visitor reads comes from the content file of the page. The photo slots are image slots (section 3
of tools/CONTRACT.md). The data for search engines (a Service whose provider is Gerta as a Person) is not made
here: it is seo/jsonld-<slug>.json, and tools/build_pages.py puts it into the head.

To change a text or a photo, edit the content file of the page and run
    python tools/build_pages.py --only balayage-staten-island
(or the slug of the other page). Only photos of Gerta's own work belong on these pages, never a licensed stock
photo (decision 49 lists the ten stock photos).
"""

SLUGS = ("balayage-staten-island", "bridal-hair-makeup-staten-island", "keratin-brazilian-blowout-staten-island")

# The photos stand side by side in the text column, which is 640 px wide on a computer, 16 px apart, each cut to
# the shape 3 x 4 by the stylesheet. width and height of each img are that size on a computer (they keep the room
# free while the photo loads). On a phone the row is as wide as the screen less the two gutters.
COLUMN = 640
GAP = 16
MAX_PHOTOS = 4


def _indent(markup, spaces):
    """Shift finished markup to the right, one nesting level is two spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def render(ctx):
    c, esc = ctx.content, ctx.esc
    where = "content/%s.json" % ctx.slug
    photos = c["photos"]
    if not isinstance(photos, list) or len(photos) > MAX_PHOTOS:
        raise ValueError('%s: key "photos" must be a list of at most %d photos (it may be empty)' % (where, MAX_PHOTOS))
    for number, slot in enumerate(photos, 1):
        if not isinstance(slot, dict):
            raise ValueError('%s: photo %d in "photos" must be an object with slot, file, alt and alt_original' % (where, number))

    lines = [
        '<div class="service">',
        '  <h1 class="service-title serif">%s</h1>' % esc(c["h1"]),
        '  <p class="service-intro">%s</p>' % esc(c["intro"]),
    ]
    if photos:
        count = len(photos)
        width = round((COLUMN - GAP * (count - 1)) / count)
        height = round(width * 4 / 3)
        # On a phone the row shares the width of the screen the same way. The photos are close to the top of
        # the page, so they are fetched at once.
        sizes = "(max-width: 760px) %dvw, %dpx" % (round(100 / count) + 1, width)
        lines.append('  <div class="service-photos">')
        for slot in photos:
            lines.append("    " + ctx.img(slot["file"], slot["alt"], width, height, lazy=False, variant="sm", sizes=sizes))
        lines.append("  </div>")
    lines += [
        '  <div class="service-text">',
        _indent(ctx.blocks(c["blocks"]), 4),
        "  </div>",
        # The same box as at the end of the home page and of the Services page (decisions 68 and 70).
        _indent(ctx.reach(c["book"]), 2),
        "</div>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
