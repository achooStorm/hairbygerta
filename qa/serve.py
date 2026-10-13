"""Serve the site folder the way GitHub Pages does for a project site.

  http://127.0.0.1:<port>/hairbygerta/            -> index.html
  http://127.0.0.1:<port>/hairbygerta/gallery/    -> gallery/index.html
  http://127.0.0.1:<port>/hairbygerta/gallery     -> 301 to /hairbygerta/gallery/
  any missing address under /hairbygerta/         -> 404.html with status 404
  /hairbygerta/Gallery/ (wrong capitals)          -> 404.html with status 404, as on GitHub Pages

--prefix / serves the site at the top of the host, the way www.hairbygerta.com will.

Only the site folder is reachable (nothing next to it), and only on 127.0.0.1.
Usage: python qa/serve.py --port 8000
Then open http://127.0.0.1:8000/hairbygerta/"""
import argparse, http.server, os, posixpath, socketserver, urllib.parse

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIDDEN = (".git", "_tmp")


def clean_prefix(value):
    """'/hairbygerta/', 'hairbygerta' -> '/hairbygerta/'. '/' or '' -> '/' (the site at the top of the host,
    the layout of www.hairbygerta.com)."""
    inner = (value or "").strip("/")
    return "/" + inner + "/" if inner else "/"


def exact_case(root, parts):
    """Does every part of the path exist under root with exactly this spelling, capitals included?
    Windows finds Gallery/ when the folder is gallery/. GitHub Pages does not: there it is a 404."""
    here = root
    for part in parts:
        try:
            if part not in os.listdir(here):
                return False
        except OSError:
            return False
        here = os.path.join(here, part)
    return True


class Handler(http.server.SimpleHTTPRequestHandler):
    root = SITE
    prefix = "/hairbygerta/"

    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _send(self, path, status):
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404)
            return None
        size = os.fstat(f.fileno()).st_size
        self.send_response(status)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(size))
        self.end_headers()
        return f

    def _missing(self):
        page = os.path.join(self.root, "404.html")
        if os.path.isfile(page):
            return self._send(page, 404)
        self.send_error(404)
        return None

    def send_head(self):
        raw = urllib.parse.urlsplit(self.path).path
        path = urllib.parse.unquote(raw)
        if self.prefix != "/" and path == self.prefix.rstrip("/"):
            self.send_response(301)
            self.send_header("Location", self.prefix)
            self.end_headers()
            return None
        if not path.startswith(self.prefix):
            self.send_error(404)
            return None
        rel = posixpath.normpath("/" + path[len(self.prefix):]).lstrip("/")
        parts = [s for s in rel.split("/") if s not in ("", ".", "..")]
        if any(s in HIDDEN for s in parts):
            return self._missing()
        if not exact_case(self.root, parts):
            return self._missing()
        target = os.path.join(self.root, *parts) if parts else self.root
        if os.path.isdir(target):
            if not path.endswith("/"):
                self.send_response(301)
                self.send_header("Location", raw + "/")
                self.end_headers()
                return None
            target = os.path.join(target, "index.html")
        if not os.path.isfile(target):
            return self._missing()
        return self._send(target, 200)


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    # The default listen queue of 5 overflows when several browsers load pages at once: Chromium then reports
    # net::ERR_CONNECTION_REFUSED for local files, which looks like a missing asset but is not a site defect.
    request_queue_size = 128


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--root", default=SITE)
    ap.add_argument("--prefix", default="/hairbygerta/")
    a = ap.parse_args()
    Handler.root = os.path.abspath(a.root)
    Handler.prefix = clean_prefix(a.prefix)
    with Server(("127.0.0.1", a.port), Handler) as srv:
        print(f"serving at http://127.0.0.1:{a.port}{Handler.prefix}", flush=True)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
