"""Page module of /book-online/ (Our Services).

Contract, section 7, Book Online:

    div.page
      h1.services-title.serif
      div.services
        article.card              one per service, in the order of the content file
          img                     the small copy of the photo, 290 x 195
          div.body
            h2.serif              the name of the service
            p.desc                one sentence about it
            div.meta
              p.duration
              p.price
            a.pill[data-book]     the Book Now button
      p.book-note                 the closing line under the cards

Every word a visitor reads comes from content/book-online.json:
    h1                  the heading of the page
    services            the cards, each with title, description, duration, price and image
                        (image is an image slot, see section 3 of tools/CONTRACT.md)
    button_label        the text of the button in every card
    closing_note_html   the line under the cards, with the phone number as a link
The phone link of the buttons comes from content/site.json (tel_href).

The Book Now button calls the phone number. The script js/site.js sends every link marked data-book
to the booking page once BOOKING_URL in that file is filled in, so nothing has to change here on that
day. A screen reader reads each button as the button text, a colon and the name of the service
("Book Now: Balayage"), so that ten buttons with the same text can be told apart. That label is put
together here from button_label and the title of the service.

To add, remove, reorder or reword a service, edit "services" in the content file and run:
    python tools/build_pages.py --only book-online
"""

SLUG = "book-online"

# The size a card photo is shown at on the desktop page (contract, section 7). The stylesheet crops the
# photo to fill this box.
PHOTO_WIDTH = 290
PHOTO_HEIGHT = 195

# The desktop page shows three cards side by side and the first row is on screen as soon as the page
# opens, so the photos of that row load right away. Every later photo loads when the visitor gets near it.
FIRST_ROW = 3


def _indent(markup, spaces):
    """Shift finished markup to the right, one nesting level is two spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def _card(ctx, service, button, tel_href, on_screen):
    """One service card, starting at the left edge."""
    title = service["title"]
    photo = service["image"]
    return "\n".join([
        '<article class="card">',
        "  " + ctx.img(photo["file"], photo["alt"], PHOTO_WIDTH, PHOTO_HEIGHT, lazy=not on_screen, variant="sm"),
        '  <div class="body">',
        '    <h2 class="serif">%s</h2>' % ctx.esc(title),
        '    <p class="desc">%s</p>' % ctx.esc(service["description"]),
        '    <div class="meta">',
        '      <p class="duration">%s</p>' % ctx.esc(service["duration"]),
        '      <p class="price">%s</p>' % ctx.esc(service["price"]),
        "    </div>",
        '    <a class="pill" data-book href="%s" aria-label="%s">%s</a>'
        % (ctx.esc(tel_href), ctx.esc("%s: %s" % (button, title)), ctx.esc(button)),
        "  </div>",
        "</article>",
    ])


def render(ctx):
    c = ctx.content
    services = c["services"]
    if not isinstance(services, list) or not services:
        raise ValueError('content/book-online.json: key "services" must be a list with at least one service')
    for number, service in enumerate(services, 1):
        if not isinstance(service, dict):
            raise ValueError('content/book-online.json: service %d in "services" must be an object with title, '
                             "description, duration, price and image" % number)
    button = c["button_label"]
    tel_href = ctx.site["tel_href"]
    cards = [_card(ctx, service, button, tel_href, on_screen=position < FIRST_ROW)
             for position, service in enumerate(services)]
    body = "\n".join([
        '<div class="page">',
        '  <h1 class="services-title serif">%s</h1>' % ctx.esc(c["h1"]),
        '  <div class="services">',
        _indent("\n".join(cards), 4),
        "  </div>",
        '  <p class="book-note">%s</p>' % ctx.inline(c["closing_note_html"]),
        "</div>",
    ])
    return {"body": body, "head_extra": ""}
