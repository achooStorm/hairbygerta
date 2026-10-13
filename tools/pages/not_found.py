"""Page module of the 404 page (404.html, the page GitHub Pages shows for every address that does not exist).

The text comes from content/404.json: "h1", "message" and "button" (label and path). The markup inside main
is the one section 7 of tools/CONTRACT.md lists for this page: div.notfound holding h1, p and a.btn.

THE SMALL SCRIPT IN THE HEAD

GitHub Pages answers every broken address, at any depth, with this one file. The addresses in the file are
relative (css/style.css, gallery/, ./), so seen from /some/old/address they would lead to the wrong place.
The script sits right after the viewport meta, before the browser reads any other address, and does this:

  1. It works out where the top of the site is. That is "/" (www.hairbygerta.com), and "/hairbygerta/" when
     the host name ends with .github.io or is 127.0.0.1 or localhost and the first folder of the address is
     hairbygerta (the test address achoostorm.github.io/hairbygerta/ and a test server on this computer).
  2. It adds <base href="the top of the site"> to the head, so every relative address on the page starts
     there. Because of that base a link like href="#main" (the skip link) would lead to the home page, so
     once the page is read the script points every such link back at the address the visitor is on.
  3. Old Wix booking addresses, anything under booking-calendar/ or service-page/, have no page of their
     own on this site. The script sends them on to the Book Online page with location.replace, so the Back
     button does not return to the broken address. The page stays hidden for that short moment.

A page opened straight from a folder on a computer (file:) is left alone, its relative addresses are right.
Without JavaScript the page still shows its text, and its links work for a broken address one level deep
(/nope), because that is the level 404.html itself sits at.
"""
import json

SLUG = "404"

PROJECT_FOLDER = "hairbygerta"                          # first folder of the test address on github.io
OLD_BOOKING = ("booking-calendar/", "service-page/")    # old Wix addresses that now lead to Book Online
BOOK_PATH = "/book-online/"                             # the Book Online page (page table, contract section 2)

_SCRIPT = """<script>
(function () {
  var loc = location, path = loc.pathname, host = loc.hostname, root = "/", old = %(old)s, base, rest, i;
  if (!/^https?:$/.test(loc.protocol)) { return; }
  if ((/\\.github\\.io$/.test(host) || host === "127.0.0.1" || host === "localhost") && path.toLowerCase().indexOf(%(folder)s) === 0) {
    root = %(folder)s;
  }
  base = document.createElement("base");
  base.href = root;
  document.head.appendChild(base);
  rest = path.slice(root.length).toLowerCase();
  for (i = 0; i < old.length; i++) {
    if (rest.indexOf(old[i]) === 0) {
      document.documentElement.hidden = true;
      loc.replace(root + %(book)s);
      return;
    }
  }
  document.addEventListener("DOMContentLoaded", function () {
    var links = document.querySelectorAll('a[href^="#"]'), n;
    for (n = 0; n < links.length; n++) {
      links[n].setAttribute("href", path + loc.search + links[n].getAttribute("href"));
    }
  });
})();
</script>"""


def _js(value):
    """A text or a list of texts as a JavaScript value that is safe inside a script element."""
    return json.dumps(value).replace("<", "\\u003c")


def render(ctx):
    c = ctx.content
    button = c["button"]
    body = "\n".join([
        '<div class="notfound">',
        "  <h1>%s</h1>" % ctx.esc(c["h1"]),
        "  <p>%s</p>" % ctx.esc(c["message"]),
        '  <a class="btn" href="%s">%s</a>' % (ctx.esc(ctx.url(button["path"])), ctx.esc(button["label"])),
        "</div>",
    ])
    script = _SCRIPT % {
        "old": _js(list(OLD_BOOKING)),
        "folder": _js("/%s/" % PROJECT_FOLDER),
        "book": _js(ctx.url(BOOK_PATH)),
    }
    return {"body": body, "head_extra": "", "head_first": script, "robots": "noindex"}
