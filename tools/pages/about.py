"""The About page, built as section 7 of tools/CONTRACT.md lists it:

    div.about
      div.col.left     two photos   (brunette-balayage, about-salon)
      div.text         h1.serif and one p
      div.col.right    two photos   (g10, copper-waves)

Every word comes from content/about.json: the heading is "h1", the text is "paragraph", and the photos are
the slots in "photos_left" and "photos_right", in the order they are listed there. A slot names the file,
the alt text and the size the photo is shown at on the desktop page ("width" and "height"), and those two
numbers become the width and height attributes of the img. To change a text or a photo, edit the content
file and run tools/build_pages.py again. This module holds no text of its own.
"""
SLUG = "about"

# The stylesheet places exactly a first and a last photo in each column, so a column holds two photos.
PHOTOS_PER_COLUMN = 2

# The sizes attribute: how wide a photo is on screen, so that the browser can pick between the small copy
# and the full file. It follows the three layouts of the About page in css/style.css (breakpoints 760 px
# and 1100 px). On a phone the two photo columns stand side by side under the text, each a little under
# half the screen. On a tablet a photo column stands on each side of the text, about a fifth of the screen.
# On a desktop screen a photo is at most its desktop size, the "width" of its slot in the content file.
# These numbers only steer which file is fetched, never how the page looks. If the About layout in the
# stylesheet changes, bring them in line with it.
SIZES = "(max-width: 760px) 45vw, (max-width: 1100px) 20vw, %spx"


def _column(ctx, side, key):
    """The lines of one photo column. side is "left" or "right", key the list of slots in the content file."""
    slots = ctx.content[key]
    if not isinstance(slots, list) or len(slots) != PHOTOS_PER_COLUMN:
        raise ValueError('content/about.json: key "%s" must be a list of exactly %d photos, because the page '
                         'has a place for %d photos on each side of the text'
                         % (key, PHOTOS_PER_COLUMN, PHOTOS_PER_COLUMN))
    lines = ['  <div class="col %s">' % side]
    for position, slot in enumerate(slots):
        # The first photo of a column is on screen as soon as the page opens, so it loads at once. The
        # second one starts further down (on a phone and on a small laptop below the first screen).
        lines.append("    " + ctx.img(slot["file"], slot["alt"], slot["width"], slot["height"],
                                      lazy=position > 0, sizes=SIZES % slot["width"]))
    lines.append("  </div>")
    return lines


def render(ctx):
    c = ctx.content
    lines = ['<div class="about">']
    lines += _column(ctx, "left", "photos_left")
    lines += [
        '  <div class="text">',
        '    <h1 class="serif">%s</h1>' % ctx.esc(c["h1"]),
        "    <p>%s</p>" % ctx.esc(c["paragraph"]),
        "  </div>",
    ]
    lines += _column(ctx, "right", "photos_right")
    lines.append("</div>")
    return {"body": "\n".join(lines), "head_extra": ""}
