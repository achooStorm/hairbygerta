"""Page module of /contact/ (Contact).

Contract, section 7, Contact:

    div.contact-head
      p.kicker.serif              the small line above the heading
      h1                          the heading of the page
      p.contact-intro             the intro sentence with its phone and email links
    div.contact
      div.info
        div.info-item             one per entry of "info", in the order of the content file
          svg.info-icon.icon-ID   a small two-tone icon of the Phosphor set, decoration only (aria-hidden)
          h2.serif                the name of the item
          p                       one per line of the item. The street line of the Address item is a link
                                  to the map (a.map-link, maps_href of content/site.json)
          div.social              only in the Social Media item: the Facebook and Instagram links, each a
                                  bare sign (a letter f, the outline of a camera) in a link of 23 x 23 px
                                  (on a phone the stylesheet draws a round 44 px button around each)
      form#contact-form.contact-form   no action: the script opens the visitor's email app (data-mailto)
        h2#form-heading.form-heading   the name of the form, shown on a phone as the heading of its panel
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
    form.heading             the name of the form ("Send a Message")
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

# The "autocomplete" values of a field that takes a name. On a phone the keyboard starts each word of such a
# field with a capital letter (autocapitalize="words").
NAME_FIELDS = ("name", "given-name", "family-name", "additional-name")

# The drawings of the info items, one per "id" in the content file. They are five icons of the Phosphor
# set in its Duotone style (phosphoricons.com, taken from icon-sets.iconify.design on 18 November 2026,
# decision 65): map-pin, phone, envelope-simple, at and clock. Phosphor Icons are free to use under the
# MIT License, and its text has to travel with them: tools/licenses/MIT-PhosphorIcons.txt.
# Every drawing sits in the same box of 256 x 256 units and is drawn with the same line (16 units), so
# the five look like one family and line up in a column. They have two tones: the lines take the colour
# of the text around them, and the shape marked class="tone" is filled with the beige of the site by the
# stylesheet. Without the stylesheet that shape is a light tint of the text colour (opacity 0.2, as the
# set draws it).
# The stylesheet sets their size (class info-icon) and gives each a second class, icon-ID, which it uses
# on a wide screen to start every drawing exactly at the left edge of its column. The width and height
# written here only keep them small should the stylesheet not load.
# To change a drawing, take the Duotone icon of the same set, so the line and the box stay the same, mark
# its light shape class="tone", and set the air on its left side in the stylesheet (.info-icon.icon-ID).
ICON_OPEN = ('<svg class="info-icon icon-%s" viewBox="0 0 256 256" width="28" height="28" fill="currentColor" '
             'aria-hidden="true" focusable="false">')
_TONE = '<path class="tone" opacity=".2" d="%s"/><path d="%s"/>'
ICONS = {
    # a map pin (ph:map-pin-duotone)
    "address": _TONE % (
        "M128 24a80 80 0 0 0-80 80c0 72 80 128 80 128s80-56 80-128a80 80 0 0 0-80-80m0 112a32 32 0 1 1 32-32a32 32 0 "
        "0 1-32 32",
        "M128 64a40 40 0 1 0 40 40a40 40 0 0 0-40-40m0 64a24 24 0 1 1 24-24a24 24 0 0 1-24 24m0-112a88.1 88.1 0 0 0-88 "
        "88c0 31.4 14.51 64.68 42 96.25a254.2 254.2 0 0 0 41.45 38.3a8 8 0 0 0 9.18 0a254.2 254.2 0 0 0 41.37-38.3c27."
        "45-31.57 42-64.85 42-96.25a88.1 88.1 0 0 0-88-88m0 206c-16.53-13-72-60.75-72-118a72 72 0 0 1 144 0c0 57.23-55."
        "47 105-72 118"),
    # a telephone handset (ph:phone-duotone)
    "phone": _TONE % (
        "M223.94 174.08A48.33 48.33 0 0 1 176 216A136 136 0 0 1 40 80a48.33 48.33 0 0 1 41.92-47.94a8 8 0 0 1 8.3 4.8l"
        "21.13 47.2a8 8 0 0 1-.66 7.53L89.32 117a7.93 7.93 0 0 0-.54 7.81c8.27 16.93 25.77 34.22 42.75 42.41a7.92 7.92 "
        "0 0 0 7.83-.59l25-21.3a8 8 0 0 1 7.59-.69l47.16 21.13a8 8 0 0 1 4.83 8.31",
        "m222.37 158.46l-47.11-21.11l-.13-.06a16 16 0 0 0-15.17 1.4a8 8 0 0 0-.75.56L134.87 160c-15.42-7.49-31.34-23."
        "29-38.83-38.51l20.78-24.71c.2-.25.39-.5.57-.77a16 16 0 0 0 1.32-15.06v-.12L97.54 33.64a16 16 0 0 0-16.62-9.52"
        "A56.26 56.26 0 0 0 32 80c0 79.4 64.6 144 144 144a56.26 56.26 0 0 0 55.88-48.92a16 16 0 0 0-9.51-16.62M176 208"
        "A128.14 128.14 0 0 1 48 80a40.2 40.2 0 0 1 34.87-40a.6.6 0 0 0 0 .12l21 47l-20.67 24.74a6 6 0 0 0-.57.77a16 "
        "16 0 0 0-1 15.7c9.06 18.53 27.73 37.06 46.46 46.11a16 16 0 0 0 15.75-1.14a8 8 0 0 0 .74-.56L168.89 152l47 21."
        "05h.11A40.21 40.21 0 0 1 176 208"),
    # an envelope (ph:envelope-simple-duotone)
    "email": _TONE % (
        "m224 56l-96 88l-96-88Z",
        "M224 48H32a8 8 0 0 0-8 8v136a16 16 0 0 0 16 16h176a16 16 0 0 0 16-16V56a8 8 0 0 0-8-8m-20.57 16L128 133.15L52."
        "57 64ZM216 192H40V74.19l82.59 75.71a8 8 0 0 0 10.82 0L216 74.19z"),
    # an at sign, the mark in front of every name on Facebook and Instagram (ph:at-duotone)
    "social": _TONE % (
        "M224 128a96 96 0 1 1-96-96a96 96 0 0 1 96 96",
        "M128 24a104 104 0 0 0 0 208c21.51 0 44.1-6.48 60.43-17.33a8 8 0 0 0-8.86-13.33C166 210.38 146.21 216 128 216"
        "a88 88 0 1 1 88-88c0 26.45-10.88 32-20 32s-20-5.55-20-32V88a8 8 0 0 0-16 0v4.26a48 48 0 1 0 5.93 65.1c6 12 16."
        "35 18.64 30.07 18.64c22.54 0 36-17.94 36-48A104.11 104.11 0 0 0 128 24m0 136a32 32 0 1 1 32-32a32 32 0 0 1-32 "
        "32"),
    # a clock (ph:clock-duotone)
    "hours": _TONE % (
        "M224 128a96 96 0 1 1-96-96a96 96 0 0 1 96 96",
        "M128 24a104 104 0 1 0 104 104A104.11 104.11 0 0 0 128 24m0 192a88 88 0 1 1 88-88a88.1 88.1 0 0 1-88 88m64-88a8 "
        "8 0 0 1-8 8h-56a8 8 0 0 1-8-8V72a8 8 0 0 1 16 0v48h48a8 8 0 0 1 8 8"),
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
    return ICON_OPEN % name + ICONS[name] + "</svg>"


def _info_item(ctx, item):
    """One item of the info grid, starting at the left edge."""
    lines = [
        '<div class="info-item">',
        "  " + _icon(item["id"]),
        '  <h2 class="serif">%s</h2>' % ctx.esc(item["heading"]),
    ]
    for line in item["lines"]:
        if isinstance(line, dict):
            text = ctx.inline(line["html"])
        elif item["id"] == "address" and line == ctx.site.get("address_one_line"):
            # The street address opens the map, as it does on the home page, so a visitor on a phone can
            # tap it and be led to the salon. The words stay those of the content file. Where the line is
            # too long for a phone it breaks after the street and never inside the name of the town:
            # everything after the first comma stays together.
            street, comma, town = line.partition(", ")
            words = ctx.esc(street) + (', <span class="nowrap">%s</span>' % ctx.esc(town) if comma else "")
            text = ('<a class="map-link" href="%s" target="_blank" rel="noopener">%s</a>'
                    % (ctx.esc(ctx.site["maps_href"]), words))
        else:
            text = ctx.esc(line)
        lines.append("  <p>%s</p>" % text)
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
    # What a phone keyboard does with the first letter. A name starts every word with a capital, an email
    # address never gets one and is not "corrected" by the spelling check either.
    if kind == "email":
        attrs += ' autocapitalize="none" spellcheck="false"'
    elif field.get("autocomplete") in NAME_FIELDS:
        attrs += ' autocapitalize="words"'
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
        '<form id="contact-form" class="contact-form" data-mailto="%s" data-sent="%s"%s>'
        % (ctx.esc(action), ctx.esc(form["sent_message"]),
           ' aria-labelledby="form-heading"' if form.get("heading") else ""),
    ]
    # The name of the form. On a phone it is the heading of the beige panel the form sits in. On a wide
    # screen, where the form stands beside the details as on the old site, the stylesheet keeps it for
    # screen readers only. A content file without "heading" has no such line.
    if form.get("heading"):
        lines.append('  <h2 class="form-heading serif" id="form-heading">%s</h2>' % ctx.esc(form["heading"]))
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
    ]
    # The way out for a phone without an email app: a line with a link that opens the text message app.
    # It waits hidden until Send was pressed, and js/site.js writes the visitor's message into the link.
    # The stylesheet shows it on touch screens only. A content file without "no_app_html" has no such line.
    if form.get("no_app_html"):
        lines.append('  <p class="form-alt" hidden>%s</p>' % ctx.inline(form["no_app_html"]))
    lines.append("</form>")
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
