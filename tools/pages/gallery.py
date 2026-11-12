"""The Gallery page, /gallery/, built as section 7 of tools/CONTRACT.md lists it (decision 47).

Where its parts come from
    content/gallery.json    the heading, the list of photos ("images"), the wording of the link labels and
                            the line that points to Instagram ("more_html")
    image-manifest.json     the file and the pixel size of every photo

What it writes between <main> and </main>
    <div class="page-head"> <h1>Gallery</h1> </div>
    <div class="shade"> ... </div>                      the shade strip, once, right under the page title
    <div class="gallery-page">
      <div class="gallery-grid">
        <div class="gallery">
          <a class="frame" href="../images/NAME.jpg" aria-label="View photo 1 of 2"><img src="../images/sm/NAME.jpg" ...></a>
          ... one link per photo that is no longer a placeholder, in the order of "images" in the content file
        </div>
        <p class="gallery-more"> ... </p>               only while the page shows fewer than six photos
      </div>
    </div>

A photo whose name is in PLACEHOLDERS (tools/build_pages.py) is never shown (decision 44). The page leaves it
out, and the numbers in the link labels count the photos that are shown. A photo put in with
tools/add_photo.py appears by itself.

Each photo is a link to its full-size file. With JavaScript, js/site.js opens that file in the photo viewer
(it finds the links as ".gallery a"). Without JavaScript the browser simply shows the file. Inside the link
sits the small copy of the photo (images/sm/NAME.jpg) with its real pixel width and height. The stylesheet
shows every photo in a tall frame, 9 to 16, three across on a wide screen and two across on a phone.

To add, remove or reorder photos, change the "images" list in content/gallery.json and run
    python tools/build_pages.py --only gallery
"""
SLUG = "gallery"

# The first photos are on screen as soon as the page opens, so the browser fetches them at once
# (loading="eager"). Every later photo is fetched only when the visitor scrolls near it (loading="lazy").
EAGER_PHOTOS = 3

# With fewer photos than this the page adds the line that points to Instagram (design brief of 12 November 2026).
FEW_PHOTOS = 6

# The stylesheet shows three photos in a row on a wide screen. The line that points to Instagram takes the
# next free place of the last row, or a row of its own when the last row is full.
COLUMNS = 3

# How wide a thumbnail is on screen: three columns of at most 384 px, two columns on a phone (760 px is the
# phone breakpoint of the stylesheet). The browser uses this only for a photo that has WebP copies, to pick
# the small or the full WebP file. It never changes how the page looks.
THUMB_SIZES = "(max-width: 760px) 46vw, (max-width: 1280px) 31vw, 384px"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message


def _label(template, n, total):
    """ "View photo {n} of {total}" -> "View photo 1 of 2" """
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
    for n, slot in enumerate(slots):
        if not isinstance(slot, dict):
            raise ValueError('%s: key "images[%d]" must be an object with "file" and "alt"' % (CONTENT_FILE, n))
    shown = [slot for slot in slots if not ctx.is_placeholder(slot["file"])]
    total = len(shown)
    links = []
    for n, slot in enumerate(shown, 1):
        name = slot["file"]
        # The small copy with its real pixel size. ctx.img also checks that the manifest knows the photo.
        thumb = ctx.img(name, slot["alt"], lazy=n > EAGER_PHOTOS, variant="sm", sizes=THUMB_SIZES)
        full = ctx.url("/" + ctx.manifest["images"][name]["file"])
        links.append('        <a class="frame" href="%s" aria-label="%s">%s</a>'
                     % (ctx.esc(full), ctx.esc(_label(template, n, total)), thumb))
    lines = [
        '<div class="page-head">',
        '  <div class="wrap">',
        "    <h1>%s</h1>" % ctx.esc(c["h1"]),
        "  </div>",
        "</div>",
        ctx.shade(),
        '<div class="gallery-page">',
        '  <div class="wrap">',
        '    <div class="gallery-grid">',
    ]
    if links:
        lines += ['      <div class="gallery">'] + links + ["      </div>"]
    if total < FEW_PHOTOS:
        own_row = " own-row" if total % COLUMNS == 0 else ""
        lines.append('      <p class="gallery-more%s">%s</p>' % (own_row, ctx.inline(c["more_html"])))
    lines += [
        "    </div>",
        "  </div>",
        "</div>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
