"""Page module of /english-privacy-policy/ (Privacy Policy).

Contract, section 7, policy pages: article.legal holding the h1, then the h2, p and ul
elements made from the "blocks" list of the content file.

Every word on the page comes from content/english-privacy-policy.json:
    h1       the heading of the page
    blocks   the text in reading order (see section 3 of tools/CONTRACT.md for the block types).
             The two blocks with the contact details are "html" blocks: they hold the line
             breaks and the email and phone links, and ctx.blocks escapes the text in them.

Nothing is typed into this file. To change the text, edit the content file and run:
    python tools/build_pages.py --only english-privacy-policy
"""

SLUG = "english-privacy-policy"


def _indent(markup, spaces=2):
    """Shift finished markup to the right, one nesting level is two spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in markup.split("\n"))


def render(ctx):
    c = ctx.content
    body = "\n".join([
        '<article class="legal">',
        "  <h1>%s</h1>" % ctx.esc(c["h1"]),
        _indent(ctx.blocks(c["blocks"])),
        "</article>",
    ])
    return {"body": body, "head_extra": ""}
