"""The About page, built as section 7 of tools/CONTRACT.md lists it (decision 47):

    div.page-head > h1
    div.shade                     the shade strip, once, right under the page title
    div.about
      div.about-text
        p.lead                    the first of "paragraphs"
        div.about-more > p        one per further paragraph, side by side on a wide screen
        p.actions                 a.btn.btn-call "actions.call" (calls the number) and
                                  a.text-link "actions.text" (starts a text message)
      div.about-photos            only when a photo of "photos" is no longer a placeholder
        div.frame > img           one per such photo, in the order of the content file

The page is led by its text. Every word comes from content/about.json. Where the Call button and the Text link
lead comes from content/site.json (tel_href).

A photo whose name is in PLACEHOLDERS (tools/build_pages.py) is never shown (decision 44). The page leaves it
out and the text stands alone. A photo put in with tools/add_photo.py shows beside the text by itself.

To change a text or a photo, edit the content file and run
    python tools/build_pages.py --only about
This module holds no text of its own.
"""
SLUG = "about"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message

# How wide a photo is on screen, so that the browser can pick between the small copy and the full file.
# The photos stand two across beside the text on a wide screen and under the text on a phone. These numbers
# only steer which file is fetched, never how the page looks.
SIZES = "(max-width: 760px) 46vw, 230px"


def render(ctx):
    c, site, esc = ctx.content, ctx.site, ctx.esc
    paragraphs, actions = c["paragraphs"], c["actions"]
    if not isinstance(paragraphs, list) or not paragraphs or not all(isinstance(p, str) and p.strip() for p in paragraphs):
        raise ValueError('%s: key "paragraphs" must be a list with at least one text' % CONTENT_FILE)
    if site["phone"] not in actions["call"]:
        raise ValueError('%s: key "actions.call" must show the phone number of content/site.json ("%s"), because the '
                         "button calls it" % (CONTENT_FILE, site["phone"]))
    photos = [slot for slot in c["photos"] if not ctx.is_placeholder(slot["file"])]

    lines = [
        '<div class="page-head">',
        '  <div class="wrap">',
        "    <h1>%s</h1>" % esc(c["h1"]),
        "  </div>",
        "</div>",
        ctx.shade(),
        '<div class="about">',
        '  <div class="wrap">',
        '    <div class="about-text">',
        '      <p class="lead">%s</p>' % esc(paragraphs[0]),
    ]
    if paragraphs[1:]:
        lines.append('      <div class="about-more">')
        lines += ["        <p>%s</p>" % esc(text) for text in paragraphs[1:]]
        lines.append("      </div>")
    lines += [
        '      <p class="actions"><a class="btn btn-call" href="%s">%s</a> <a class="text-link" href="%s">%s</a></p>'
        % (esc(site["tel_href"]), esc(actions["call"]), esc(ctx.sms_href), esc(actions["text"])),
        "    </div>",
    ]
    if photos:
        lines.append('    <div class="about-photos">')
        # The first two are on screen as soon as the page opens on a wide screen, so they load at once.
        lines += ['      <div class="frame">%s</div>'
                  % ctx.img(slot["file"], slot["alt"], slot["width"], slot["height"], lazy=position > 1, sizes=SIZES)
                  for position, slot in enumerate(photos)]
        lines.append("    </div>")
    lines += [
        "  </div>",
        "</div>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
