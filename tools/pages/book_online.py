"""Page module of /book-online/ (Our services), built as section 7 of tools/CONTRACT.md lists it (decision 47):

    div.page-head
      h1                          the heading of the page
      p.lead                      "intro_html": prices are given by phone, and how to book
    div.shade                     the shade strip, once, right under the page title
    div.services
      div.menu
        section.menu-group        one per group of "groups", in the order of the content file
          h2                      the name of the group
          ul > li.svc             one per service of the group
            h3                    the name of the service
            p.desc                its one line
            p.duration            its time
      div.svc-call                the call block, it stays in view on a wide screen
        p.actions                 a.btn.btn-call "call_block.call" (calls the number) and
                                  a.text-link "call_block.text" (starts a text message)
        p.hours                   "call_block.hours"

The page is a typeset menu. It has no photos and no cards, and no button inside a service.

Every word a visitor reads comes from content/book-online.json. Where the Call button and the Text link lead
comes from content/site.json (tel_href). The salon takes bookings by phone, so the site has no online booking
link and nothing on this page is marked data-book.

To add, remove, reorder or reword a service or a group, edit "groups" in the content file and run
    python tools/build_pages.py --only book-online
The home page lists the same services by name (content/home.json), so change both files.
"""

SLUG = "book-online"

CONTENT_FILE = "content/%s.json" % SLUG     # only used to name the file in an error message


def _wrong(key, problem):
    """The error that stops the build and names the content file and the key."""
    return ValueError('%s: key "%s" %s' % (CONTENT_FILE, key, problem))


def _group(ctx, number, group):
    """One group of services, starting at the left edge."""
    services = group["services"]
    if not isinstance(services, list) or not services:
        raise _wrong("groups[%d].services" % (number - 1), "must be a list with at least one service")
    anchor = "group-%d" % number
    lines = [
        '<section class="menu-group" aria-labelledby="%s">' % anchor,
        '  <h2 id="%s">%s</h2>' % (anchor, ctx.esc(group["heading"])),
        "  <ul>",
    ]
    for service in services:
        lines += [
            '    <li class="svc">',
            "      <h3>%s</h3>" % ctx.esc(service["title"]),
            '      <p class="desc">%s</p>' % ctx.esc(service["description"]),
            '      <p class="duration">%s</p>' % ctx.esc(service["duration"]),
            "    </li>",
        ]
    lines += ["  </ul>", "</section>"]
    return lines


def render(ctx):
    c, site, esc = ctx.content, ctx.site, ctx.esc
    groups, block = c["groups"], c["call_block"]
    if not isinstance(groups, list) or not groups:
        raise _wrong("groups", "must be a list with at least one group of services")
    # The call block shows two business facts of content/site.json in its own words, so check that they agree.
    if site["phone"] not in block["call"]:
        raise _wrong("call_block.call", 'must show the phone number of content/site.json ("%s"), because the button calls it'
                     % site["phone"])
    if block["hours"] != site["hours"]:
        raise _wrong("call_block.hours", 'must be the hours of content/site.json, word for word ("%s")' % site["hours"])

    lines = [
        '<div class="page-head">',
        '  <div class="wrap">',
        "    <h1>%s</h1>" % esc(c["h1"]),
        '    <p class="lead">%s</p>' % ctx.inline(c["intro_html"]),
        "  </div>",
        "</div>",
        ctx.shade(),
        '<div class="services">',
        '  <div class="wrap">',
        '    <div class="menu">',
    ]
    for number, group in enumerate(groups, 1):
        lines += ["      " + line for line in _group(ctx, number, group)]
    lines += [
        "    </div>",
        '    <div class="svc-call">',
        '      <p class="actions"><a class="btn btn-call" href="%s">%s</a> <a class="text-link" href="%s">%s</a></p>'
        % (esc(site["tel_href"]), esc(block["call"]), esc(ctx.sms_href), esc(block["text"])),
        '      <p class="hours">%s</p>' % esc(block["hours"]),
        "    </div>",
        "  </div>",
        "</div>",
    ]
    return {"body": "\n".join(lines), "head_extra": ""}
