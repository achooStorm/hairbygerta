"""Page module of /contact/ (Contact).

Contract, section 7, Contact:

    div.contact-head
      p.kicker.serif              the small line above the heading
      h1                          the heading of the page
      p.contact-intro             the intro sentence with its phone and email links
    div.contact
      div.info
        div.info-item             one per entry of "info", in the order of the content file
          svg.info-icon.icon-ID   a small two-tone drawing, decoration only (aria-hidden)
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

# The drawings of the info items, one per "id" in the content file. One set, made for this site
# (18 November 2026, decision 64): every drawing sits in the same box of 24 x 24 units, is drawn with the
# same line (1.5 units, round ends and corners) and is about 17 units large, so the five look like one
# family and line up in a column. They have two tones: the lines take the colour of the text around them,
# and the shapes marked class="tone" are filled with the beige of the site by the stylesheet (the dot of
# the map pin, class="hole", is filled with the page colour again). Without the stylesheet nothing is
# filled and they are plain line drawings.
# The stylesheet sets their size (class info-icon) and gives each a second class, icon-ID, which it uses
# on a wide screen to start every drawing exactly at the left edge of its column. The width and height
# written here only keep them small should the stylesheet not load.
# To change a drawing, keep it inside the 24 x 24 box, 3.5 units clear of the edges, and keep the line.
ICON_OPEN = ('<svg class="info-icon icon-%s" viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" '
             'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">')
ICONS = {
    # a map pin
    "address": ('<path class="tone" d="M12 21.25c-3.75-4.1-6.25-7.6-6.25-11a6.25 6.25 0 0 1 12.5 0c0 3.4-2.5 6.9-6.25 11z"/>'
                '<circle class="hole" cx="12" cy="10.25" r="2.25"/>'),
    # a telephone handset
    "phone": ('<path class="tone" d="M6.6 3.5h2.6a1 1 0 0 1 .95.68l1.1 3.3a1 1 0 0 1-.3 1.07L9.3 9.9a11.5 11.5 0 0 0 4.8 4.8'
              'l1.35-1.65a1 1 0 0 1 1.07-.3l3.3 1.1a1 1 0 0 1 .68.95v2.6a2.1 2.1 0 0 1-2.1 2.1'
              'C10.6 19.5 4.5 13.4 4.5 5.6a2.1 2.1 0 0 1 2.1-2.1z"/>'),
    # an envelope
    "email": ('<rect class="tone" x="3.5" y="5.5" width="17" height="13" rx="1.5"/><path d="M4.2 7.1l7.8 5.65 7.8-5.65"/>'),
    # an at sign, the mark in front of every name on Facebook and Instagram
    "social": ('<circle class="tone" cx="12" cy="12" r="3.5"/>'
               '<path d="M15.5 8.6v4.4a2.5 2.5 0 0 0 5 0V12a8.5 8.5 0 1 0-3.3 6.72"/>'),
    # a clock
    "hours": ('<circle class="tone" cx="12" cy="12" r="8.5"/><path d="M12 7.25V12l3.25 2"/>'),
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
