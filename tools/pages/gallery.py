"""The Gallery page, /gallery/.

Where its parts come from
    content/gallery.json    the heading, the list of photos ("images") and the wording of the link labels
    image-manifest.json     the file and the pixel size of every photo
    tools/CONTRACT.md       section 7, "Gallery": the elements and classes written below

What it writes between <main> and </main>

    <div class="page">
      <h1 class="page-title">Gallery</h1>
      <div class="gallery">
        <a href="../images/NAME.jpg" data-webp="../images/NAME.webp" aria-label="View photo 1 of 21: WHAT IT SHOWS"><img src="../images/sm/NAME.jpg" ...></a>
        ... one link per photo, in the order of "images" in the content file
      </div>
    </div>

Each photo is a link to its full-size file. With JavaScript, js/site.js opens that file in the photo viewer.
Without JavaScript the browser simply shows the file. Inside the link sits the small copy of the photo
(images/sm/NAME.jpg) with its real pixel width and height, so the page does not jump while the photos load.

To add, remove or reorder photos, change the "images" list in content/gallery.json and run
    python tools/build_pages.py --only gallery
The numbers in the link labels ("View photo 3 of 21: ...") follow by themselves, and so does the choice of
the photos that are fetched at once (those at the top of each column, see COLUMN_LAYOUTS below).
"""

import re

SLUG = "gallery"

# Which photos are on screen as soon as the page opens. Those are fetched at once (loading="eager"), every
# other photo only when the visitor scrolls near it (loading="lazy").
# The stylesheet lays the gallery out in columns, and the photos run down the first column, then down the
# second, and so on. So the top of the page does not show photos 1, 2, 3 side by side: on a phone (two
# columns) it shows photos 1 and 2 on the left and, with 21 photos, photos 12 and 13 on the right. A photo
# that tops a column and waits for the visitor to scroll leaves a hole in the first screen, and on a phone
# it was the last and heaviest thing to arrive.
# COLUMN_LAYOUTS lists the layouts of css/style.css as (columns, width of a column in px, gap in px), each
# at its narrowest and its widest. EAGER_PER_COLUMN says how many photos from the top of each column are
# fetched at once in a layout with that many columns. render() works out where the browser breaks the
# columns (it makes them as even as it can) and collects those photos. If the number of columns or the gaps
# in the stylesheet change, bring these numbers in line with it.
# A phone screen is tall and narrow, so it shows three photos of each of its two columns. A wide screen
# shows the first photo of each of its three columns in full. The four columns of a very wide desktop
# screen (1600 px and more) are left out on purpose: such a screen sits on a fast connection, and every
# photo fetched at once for it would be fetched early on a phone too.
# Checked against Chrome on 18 November 2026 at 17 widths from 320 to 1599 px: the columns start at photos
# 1 and 12 (two columns) and at 1, 8 and 14 (three columns), exactly where this works them out.
COLUMN_LAYOUTS = (
    (2, 134, 12), (2, 204, 12),         # phones, 320 to 440 px wide
    (3, 229, 20), (3, 340, 20),         # tablets and small laptops, 761 to 1100 px
    (3, 334, 24), (3, 500, 24),         # desktop, 1101 to 1599 px
)
EAGER_PER_COLUMN = {2: 3, 3: 1}

# How wide a thumbnail is on screen, for the browser to pick the small or the full WebP file. It never
# changes how the page looks. The gallery has three columns, so a thumbnail is about a third of the window
# (33vw). On a phone there are two columns and a thumbnail is nearer 43 % of the window, but the number
# stays at a third on purpose: an iPhone has 3 screen pixels to every px, and told the true width it fetched
# the full-size file (up to 150 kB) for every tall photo, because the small copy of such a photo is only
# 450 px wide. Told a third, it takes the small copy for all of them, which still gives a thumbnail 2.7
# screen pixels per px. If the number of columns in css/style.css changes, bring this in line with it.
THUMB_SIZES = "33vw"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message


def _label(template, n, total, alt):
    """ "View photo {n} of {total}" -> "View photo 3 of 21: Applying highlights with foils".
    The description of the photo follows the number, so that a visitor who hears the page instead of seeing
    it learns what each photo shows. A photo without a description keeps the number alone."""
    label = template.replace("{n}", str(n)).replace("{total}", str(total))
    return "%s: %s" % (label, alt.strip()) if alt and alt.strip() else label


def _column_starts(heights, columns):
    """Where the browser starts each column: the positions (0 = first photo) of the photos that top a column.
    heights are the heights of the photos in one column, each with the gap below it. The browser makes the
    columns as low as it can while every photo stays whole and in order, which is the lowest height at which
    filling one column after the other needs no more than the given number of columns."""
    def fill(limit):
        starts, used = [0], 0.0
        for i, height in enumerate(heights):
            if used and used + height > limit + 1e-6:
                starts.append(i)
                used = 0.0
            used += height
        return starts

    # Every height a column can end at is a sum of photos that follow each other. Try them from the lowest.
    sums = sorted(set(round(sum(heights[a:b]), 4) for a in range(len(heights)) for b in range(a + 1, len(heights) + 1)))
    for limit in sums:
        if limit + 1e-6 >= max(heights):
            starts = fill(limit)
            if len(starts) <= columns:
                return starts
    return [0]


def _first_screen(shapes):
    """The positions of the photos that are fetched at once. shapes are the photos as height divided by width."""
    eager = {0}
    for columns, width, gap in COLUMN_LAYOUTS:
        starts = _column_starts([shape * width + gap for shape in shapes], columns)
        for start in starts:
            eager.update(range(start, min(start + EAGER_PER_COLUMN.get(columns, 1), len(shapes))))
    return eager


def render(ctx):
    c = ctx.content
    slots = c["images"]
    template = c["link_label"]
    if not isinstance(slots, list) or not slots:
        raise ValueError('%s: key "images" must be a list with at least one photo' % CONTENT_FILE)
    if not isinstance(template, str) or "{n}" not in template:
        raise ValueError('%s: key "link_label" must be a text that holds {n} where the number of the photo goes '
                         '({total} stands for the number of photos)' % CONTENT_FILE)

    total = len(slots)
    for n, slot in enumerate(slots, 1):
        if not isinstance(slot, dict):
            raise ValueError('%s: key "images[%d]" must be an object with "file" and "alt"' % (CONTENT_FILE, n - 1))

    # The small copy of every photo first, with its real pixel size: the shape of the photos decides which
    # of them top a column. ctx.img also checks that the manifest knows the photo and gives every
    # placeholder alt="" and class="ph". It is asked twice per photo, because whether a photo is fetched at
    # once is only known when the shapes of all of them are.
    shapes = []
    for slot in slots:
        probe = ctx.img(slot["file"], "-", variant="sm", sizes=THUMB_SIZES)     # "-": only its size is read
        width, height = re.search(r'width="(\d+)" height="(\d+)"', probe).groups()
        shapes.append(int(height) / int(width))
    eager = _first_screen(shapes)

    links = []
    for n, slot in enumerate(slots, 1):
        name = slot["file"]
        thumb = ctx.img(name, slot["alt"], lazy=(n - 1) not in eager, variant="sm", sizes=THUMB_SIZES)
        entry = ctx.manifest["images"][name]
        full = ctx.url("/" + entry["file"])
        # A photo that has a WebP copy names it in data-webp. The photo viewer shows that copy to a browser
        # that reads WebP, because it is the same picture in a much smaller file. The link itself stays the
        # JPG, which every browser and every program can open.
        webp = entry.get("webp")
        light = ' data-webp="%s"' % ctx.esc(ctx.url("/" + webp["file"])) if webp and webp.get("file") else ""
        described = "" if ctx.is_placeholder(name) else slot["alt"]
        links.append('    <a href="%s"%s aria-label="%s">%s</a>'
                     % (ctx.esc(full), light, ctx.esc(_label(template, n, total, described)), thumb))

    body = "\n".join([
        '<div class="page">',
        '  <h1 class="page-title">%s</h1>' % ctx.esc(c["h1"]),
        '  <div class="gallery">',
        "\n".join(links),
        "  </div>",
        "</div>",
    ])
    return {"body": body, "head_extra": ""}
