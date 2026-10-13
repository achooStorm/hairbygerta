"""Page module of /english-refund-policy/ (Refund & Cancellation Policy).

Contract, section 7, policy pages: article.legal holding the h1, then the h2, p and ul
elements made from the "blocks" list of the content file.

Every word on the page comes from content/english-refund-policy.json:
    h1       the heading of the page
    blocks   the text in reading order (see section 3 of tools/CONTRACT.md for the block types)

To change the text, edit that file and run:  python tools/build_pages.py --only english-refund-policy
"""

SLUG = "english-refund-policy"


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
