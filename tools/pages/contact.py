"""Page module of /contact/ (Contact).

Contract, section 7, Contact:

    div.contact-head
      p.kicker.serif              the small line above the heading
      h1                          the heading of the page
      p.contact-intro             the intro sentence with its phone and email links
    div.contact
      div.info
        div.info-item             one per entry of "info", in the order of the content file
          svg.info-icon           a small line drawing, decoration only (aria-hidden)
          h2.serif                the name of the item
          p                       one per line of the item
          div.social              only in the Social Media item: the Facebook and Instagram links, each a
                                  bare sign (a letter f, the outline of a camera) in a link of 23 x 23 px
      form#contact-form.contact-form   no action: the script opens the visitor's email app (data-mailto)
        div.row                   First Name and Last Name side by side, each a div with label and input
        label + input#email       type email, required, described by p#email-error
        p#email-error.field-error empty and hidden; the script writes one of the two error messages into it
        label + textarea#message
        button[type=submit]
        p.form-note[role=status]  empty, the script writes the line shown after sending into it
    div.map
      iframe                      the Google map of the salon, its address in data-src: the script sets src when
                                  the visitor scrolls near it
      p.map-open > a              opens the salon in Google Maps (maps_href of content/site.json)

Every word a visitor reads comes from content/contact.json:
    kicker, h1, intro_html   the heading block
    info                     the items: "id" picks the drawing (see ICONS below), "heading" is the
                             name, "lines" are the lines under it (a plain text, or {"html": ...} for
                             a line with a link), "social" is the list of icon links of that item
    form.fields              the fields in reading order: id, label, type (text, email or textarea),
                             required (true or false), autocomplete
    form.required_mark       the star shown after the label of a required field
    form.button              the text of the button
    form.sent_message        the line the script shows after the visitor pressed Send (data-sent)
    form.errors              the two messages under the Email field: no address (data-missing) and an
                             address that cannot be one (data-invalid)
    map.title                what a screen reader calls the map
    map.query                what the map searches for: the salon name and its address
    map.open_label           the link under the map
The address the form writes to comes from content/site.json (mailto_href), the map link from maps_href.

How the form works: pressing Send opens the visitor's own email app with the message filled in
(js/site.js). Nothing is sent to a server. The form has no action: a form whose action is a mailto
address makes browsers warn that the page sends a form over an insecure connection (decision 41).
Without the script the stylesheet hides the form, and the sentence above it still gives the phone
number and the email address as links. The browser checks the Email field itself (type email,
required); the script shows its message in words under the field instead of the browser's bubble.
The script finds the form and its fields by the ids fixed in the contract (contact-form, first-name,
last-name, email, message), so this module stops the build when the content file renames or drops one.

To change a text, edit the content file and run:  python tools/build_pages.py --only contact
"""
import urllib.parse

SLUG = "contact"

CONTENT_FILE = "content/contact.json"

# The address of a Google map that can be shown inside a page. The search text from the content file goes
# in the middle.
MAP_EMBED = "https://www.google.com/maps?q=%s&output=embed"

# The two fields that share one line on a wide screen (contract, section 7: div.row).
ROW_FIELDS = ("first-name", "last-name")

# The fields js/site.js reads by id (contract, sections 7 and 8).
CONTRACT_FIELDS = ("first-name", "last-name", "email", "message")

# The drawings of the info items, one per "id" in the content file. Simple line drawings, made for this
# site. They take the colour of the text around them, and the stylesheet gives each one a box of
# 28 x 28 px that starts at the left edge of its column (class info-icon). The width and height written
# here only keep them small should the stylesheet not load.
#
# Each drawing has three parts: its viewBox, its stroke width and its shapes. The viewBox is the window
# the 28 x 28 box looks through. It is chosen so that the drawing starts at the left edge of the box,
# stands on its bottom edge and is as large as the icon on the old site (pin 21 x 28 px, handset 23 x 23,
# envelope 23 x 16 and 2 px in from both edges, thumbs-up 23 x 22, clock 23 x 23). The stroke width is
# chosen so that every line is 1.5 px thick on screen. To change a drawing, keep its shapes inside the
# same outline, or work the two numbers out again.
ICON_OPEN = ('<svg class="info-icon" viewBox="%s" width="28" height="28" fill="none" stroke="currentColor" '
             'stroke-width="%s" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">')
ICONS = {
    # a map pin
    "address": ("4.991 2.991 19.019 19.019", "1.019",
                '<path d="M12 21.5c-3.9-4.3-6.5-8-6.5-11.5a6.5 6.5 0 0 1 13 0c0 3.5-2.6 7.2-6.5 11.5z"/>'
                '<circle cx="12" cy="10" r="2.5"/>'),
    # a telephone handset
    "phone": ("3.942 -0.779 20.837 20.837", "1.116",
              '<path d="M6.6 3.5h2.6a1 1 0 0 1 .95.68l1.1 3.3a1 1 0 0 1-.3 1.07L9.3 9.9a11.5 11.5 0 0 0 4.8 4.8'
              'l1.35-1.65a1 1 0 0 1 1.07-.3l3.3 1.1a1 1 0 0 1 .68.95v2.6a2.1 2.1 0 0 1-2.1 2.1'
              'C10.6 19.5 4.5 13.4 4.5 5.6a2.1 2.1 0 0 1 2.1-2.1z"/>'),
    # an envelope
    "email": ("0.531 -3.628 25.135 25.135", "1.347",
              '<rect x="3" y="5.5" width="19.3" height="13" rx="1"/><path d="M3.5 6.5l9.15 6.5 9.15-6.5"/>'),
    # a thumbs-up
    "social": ("2.917 -1.196 21.780 21.780", "1.167",
               '<path d="M3.5 10.5H7V20H3.5z"/>'
               '<path d="M7 11l3.6-7.2c1.5 0 2.6 1.1 2.6 2.6v3.1h5.1a1.9 1.9 0 0 1 1.9 2.2l-1.1 6.7'
               'a1.9 1.9 0 0 1-1.9 1.6H7"/>'),
    # a clock
    "hours": ("2.907 -1.047 22.140 22.140", "1.186",
              '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.2V12l3.2 2"/>'),
}


def _indent(markup, spaces):
    """Shift finished markup to the right, one nesting level is two spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def _icon(name):
    """The drawing of one info item."""
    if name not in ICONS:
        raise ValueError('%s: key "info": there is no drawing for the id "%s" in tools/pages/contact.py (drawings: %s)'
                         % (CONTENT_FILE, name, ", ".join(ICONS)))
    view_box, stroke_width, shapes = ICONS[name]
    return ICON_OPEN % (view_box, stroke_width) + shapes + "</svg>"


def _info_item(ctx, item):
    """One item of the info grid, starting at the left edge."""
    lines = [
        '<div class="info-item">',
        "  " + _icon(item["id"]),
        '  <h2 class="serif">%s</h2>' % ctx.esc(item["heading"]),
    ]
    for line in item["lines"]:
        lines.append("  <p>%s</p>" % (ctx.inline(line["html"]) if isinstance(line, dict) else ctx.esc(line)))
    if item.get("social"):
        # The bare signs, a letter f and the outline of a camera, as on the old Contact page. The footer of
        # every page shows the same two links as filled discs.
        lines.append(_indent(ctx.social(item["social"], icons="bare"), 2))
    lines.append("</div>")
    return "\n".join(lines)


def _check_fields(fields):
    """Stop the build when the fields no longer match what the contract and the script rely on."""
    if not isinstance(fields, list) or not fields:
        raise ValueError('%s: key "form.fields" must be a list with at least one field' % CONTENT_FILE)
    ids = [field["id"] for field in fields]
    for wanted in CONTRACT_FIELDS:
        if ids.count(wanted) != 1:
            raise ValueError('%s: key "form.fields" must hold the field "%s" exactly once (the script js/site.js '
                             'reads it by that id)' % (CONTENT_FILE, wanted))
    if len(set(ids)) != len(ids):
        raise ValueError('%s: key "form.fields": two fields share one id' % CONTENT_FILE)
    by_id = {field["id"]: field for field in fields}
    if by_id["email"]["type"] != "email" or by_id["email"].get("required") is not True:
        raise ValueError('%s: key "form.fields": the field "email" must have "type": "email" and "required": true '
                         "(contract, section 7)" % CONTENT_FILE)
    if by_id["message"]["type"] != "textarea":
        raise ValueError('%s: key "form.fields": the field "message" must have "type": "textarea" '
                         "(contract, section 7)" % CONTENT_FILE)


# The line under the Email field that the script fills with an error message (contract, section 7).
ERROR_ID = "email-error"


def _field(ctx, field, required_mark, errors=None):
    """The label and the field that belongs to it, two lines starting at the left edge (three for the Email
    field: its error line follows)."""
    name = ctx.esc(field["id"])
    kind = field["type"]
    required = field.get("required") is True
    label = ctx.esc(field["label"])
    if required:
        # The star is for the eye only. A screen reader learns from the field itself that it is required.
        label += ' <span aria-hidden="true">%s</span>' % ctx.esc(required_mark)
    attrs = ' id="%s" name="%s"' % (name, name)
    if kind != "textarea":
        attrs += ' type="%s"' % ctx.esc(kind)
    if field.get("autocomplete"):
        attrs += ' autocomplete="%s"' % ctx.esc(field["autocomplete"])
    if kind == "textarea":
        attrs += ' rows="4"'
    if required:
        attrs += " required"
    error = ""
    if field["id"] == "email" and errors is not None:
        attrs += ' aria-describedby="%s"' % ERROR_ID
        error = '\n<p class="field-error" id="%s" data-missing="%s" data-invalid="%s" hidden></p>' % (
            ERROR_ID, ctx.esc(errors["email_missing"]), ctx.esc(errors["email_invalid"]))
    if kind == "textarea":
        control = "<textarea%s></textarea>" % attrs
    elif kind in ("text", "email", "tel"):
        control = "<input%s>" % attrs
    else:
        raise ValueError('%s: key "form.fields": the field "%s" has the type "%s", this page knows text, email, '
                         "tel and textarea" % (CONTENT_FILE, field["id"], kind))
    return '<label for="%s">%s</label>\n%s%s' % (name, label, control, error)


def _form(ctx, form, action):
    """The contact form, starting at the left edge."""
    fields = form["fields"]
    _check_fields(fields)
    mark = form["required_mark"]
    errors = form["errors"]
    lines = [
        '<form id="contact-form" class="contact-form" data-mailto="%s" data-sent="%s">'
        % (ctx.esc(action), ctx.esc(form["sent_message"])),
    ]
    row = []                # the fields of the row that is being collected

    def close_row():
        if row:
            lines.extend(['  <div class="row">'] + row + ["  </div>"])
            del row[:]

    for field in fields:
        if field["id"] in ROW_FIELDS:
            row.extend(["    <div>", _indent(_field(ctx, field, mark), 6), "    </div>"])
        else:
            close_row()
            lines.append(_indent(_field(ctx, field, mark, errors), 2))
    close_row()
    lines += [
        '  <button type="submit">%s</button>' % ctx.esc(form["button"]),
        '  <p class="form-note" role="status"></p>',
        "</form>",
    ]
    return "\n".join(lines)


def _map(ctx, place):
    """The Google map of the salon and the link under it. The frame carries its address in data-src, and
    js/site.js moves it into src when the visitor scrolls near the map: until then the page asks Google for
    nothing. Without the script the frame stays empty and the link still opens the map."""
    # Spaces become +, commas stay as they are, the same way content/site.json writes its maps link.
    src = MAP_EMBED % urllib.parse.quote_plus(place["query"], safe=",")
    return "\n".join([
        '<div class="map">',
        '  <iframe data-src="%s" title="%s" loading="lazy"></iframe>' % (ctx.esc(src), ctx.esc(place["title"])),
        '  <p class="map-open"><a href="%s" target="_blank" rel="noopener">%s</a></p>'
        % (ctx.esc(ctx.site["maps_href"]), ctx.esc(place["open_label"])),
        "</div>",
    ])


def render(ctx):
    c = ctx.content
    info = c["info"]
    if not isinstance(info, list) or not info:
        raise ValueError('%s: key "info" must be a list with at least one item' % CONTENT_FILE)
    body = "\n".join([
        '<div class="contact-head">',
        '  <p class="kicker serif">%s</p>' % ctx.esc(c["kicker"]),
        "  <h1>%s</h1>" % ctx.esc(c["h1"]),
        '  <p class="contact-intro">%s</p>' % ctx.inline(c["intro_html"]),
        "</div>",
        '<div class="contact">',
        '  <div class="info">',
        "\n".join(_indent(_info_item(ctx, item), 4) for item in info),
        "  </div>",
        _indent(_form(ctx, c["form"], ctx.site["mailto_href"]), 2),
        "</div>",
        _map(ctx, c["map"]),
    ])
    return {"body": body, "head_extra": ""}
