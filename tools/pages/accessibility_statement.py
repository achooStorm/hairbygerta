"""Page module of /accessibility-statement/ (Accessibility Statement).

Contract, section 7, policy pages: article.legal holding the h1, then the h2, p and ul
elements made from the "blocks" list of the content file.

Every word on the page comes from content/accessibility-statement.json:
    h1       the heading of the page
    blocks   the text in reading order (see section 3 of tools/CONTRACT.md for the block types).
             Two of them are "html" blocks: the paragraph in italics (it is wrapped in <em>) and
             the last paragraph, which holds the line breaks and the phone and email links of
             the accessibility coordinator. ctx.blocks escapes the text in them.

Nothing is typed into this file. To change the text, edit the content file and run:
    python tools/build_pages.py --only accessibility-statement

This page shows "h1" and "blocks" and nothing else. A key in the content file that this module
does not know stops the build of this page with a message that names the key, so a text can
never go missing from the page without anyone noticing.
"""

SLUG = "accessibility-statement"

# Every key content/accessibility-statement.json may have.
HEAD_KEYS = ("slug", "path", "title", "description")    # read by build_pages.py (page table, head of the page)
PAGE_KEYS = ("h1", "blocks")                            # shown on the page, by this module
EDITOR_KEYS = ("notes",)                                # notes for the people who edit the file, never shown


def _indent(markup, spaces=2):
    """Shift finished markup to the right, one nesting level is two spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def render(ctx):
    c = ctx.content
    known = HEAD_KEYS + PAGE_KEYS + EDITOR_KEYS
    unknown = [key for key in c if key not in known]
    if unknown:
        raise ValueError('content/%s.json: this page does not show the key "%s". Its text belongs in "h1" or '
                         'in "blocks" (other keys this page knows: %s)'
                         % (ctx.slug, unknown[0], ", ".join(HEAD_KEYS + EDITOR_KEYS)))
    body = "\n".join([
        '<article class="legal">',
        "  <h1>%s</h1>" % ctx.esc(c["h1"]),
        _indent(ctx.blocks(c["blocks"])),
        "</article>",
    ])
    return {"body": body, "head_extra": ""}
