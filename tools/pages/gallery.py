"""The Gallery page, /gallery/.

Where its parts come from
    content/gallery.json    the heading, the list of photos ("images") and the wording of the link labels
    image-manifest.json     the file and the pixel size of every photo
    tools/CONTRACT.md       section 7, "Gallery": the elements and classes written below

What it writes between <main> and </main>

    <div class="page">
      <h1 class="page-title">Gallery</h1>
      <div class="gallery">
        <a href="../images/NAME.jpg" aria-label="View photo 1 of 21"><img src="../images/sm/NAME.jpg" ...></a>
        ... one link per photo, in the order of "images" in the content file
      </div>
    </div>

Each photo is a link to its full-size file. With JavaScript, js/site.js opens that file in the photo viewer.
Without JavaScript the browser simply shows the file. Inside the link sits the small copy of the photo
(images/sm/NAME.jpg) with its real pixel width and height, so the page does not jump while the photos load.

To add, remove or reorder photos, change the "images" list in content/gallery.json and run
    python tools/build_pages.py --only gallery
The numbers in the link labels ("View photo 3 of 21") follow by themselves.
"""

SLUG = "gallery"

# The first photos are on screen as soon as the page opens, so the browser fetches them at once
# (loading="eager"). Every later photo is fetched only when the visitor scrolls near it (loading="lazy").
EAGER_PHOTOS = 3

# How wide a thumbnail is on screen: the stylesheet shows the gallery in three columns, and in two columns
# on a phone (760 px is its phone breakpoint). The browser uses this only for a photo that has WebP copies
# (g12 and g13 today), to pick the small or the full WebP file. It never changes how the page looks. If the
# number of columns in css/style.css changes, bring these numbers in line with it.
THUMB_SIZES = "(max-width: 760px) 50vw, 33vw"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message


def _label(template, n, total):
    """ "View photo {n} of {total}" -> "View photo 3 of 21" """
    return template.replace("{n}", str(n)).replace("{total}", str(total))


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
    links = []
    for n, slot in enumerate(slots, 1):
        if not isinstance(slot, dict):
            raise ValueError('%s: key "images[%d]" must be an object with "file" and "alt"' % (CONTENT_FILE, n - 1))
        name = slot["file"]
        # The small copy with its real pixel size. ctx.img also checks that the manifest knows the photo
        # and gives every placeholder alt="" and class="ph".
        thumb = ctx.img(name, slot["alt"], lazy=n > EAGER_PHOTOS, variant="sm", sizes=THUMB_SIZES)
        full = ctx.url("/" + ctx.manifest["images"][name]["file"])
        links.append('    <a href="%s" aria-label="%s">%s</a>'
                     % (ctx.esc(full), ctx.esc(_label(template, n, total)), thumb))

    body = "\n".join([
        '<div class="page">',
        '  <h1 class="page-title">%s</h1>' % ctx.esc(c["h1"]),
        '  <div class="gallery">',
        "\n".join(links),
        "  </div>",
        "</div>",
    ])
    return {"body": body, "head_extra": ""}
