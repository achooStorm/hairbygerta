"""Page module of /terms-conditions/ (Terms & Conditions).

Contract, section 7, policy pages: article.legal holding the h1, then the h2, p and ul
elements made from the "blocks" list of the content file.

Every word on the page comes from content/terms-conditions.json:
    h1       the heading of the page
    blocks   the text in reading order (see section 3 of tools/CONTRACT.md for the block types)

The two links to the Privacy Policy and to the Refund & Cancellation Policy are written in that file
as href="{{root}}english-privacy-policy/" and href="{{root}}english-refund-policy/". ctx.blocks swaps
{{root}} for the way up to the top of the site, so both come out as relative links.

To change the text, edit that file and run:  python tools/build_pages.py --only terms-conditions
"""

SLUG = "terms-conditions"


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
