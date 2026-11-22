"""Write the QR code of the Book with Gerta banner into content/site.json (decision 75).

On a computer the banner shows a QR code: a visitor scans it with the phone camera and the text
message app opens with Gerta's number and the first words already written ("sms_href" and
"sms_message" of content/site.json). The generator (tools/build_pages.py) uses the Python standard
library only, so it cannot draw a QR code: this tool draws it once and stores it in "reach_qr" of
content/site.json, as the text it holds, its size in modules and one SVG path. The generator stops
when "reach_qr" no longer holds the number and words of content/site.json; then run

    pip install segno
    python tools/make_qr.py

and build again.
"""
import json
import os
import re
import sys

import segno

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "content", "site.json")


def qr_text(site):
    """SMSTO:<number>:<message>, the form the camera apps of iPhone and Android read as a text message."""
    number = re.sub(r"^sms:", "", site["sms_href"]).split("?")[0]
    return "SMSTO:%s:%s" % (number, site["sms_message"])


def main():
    with open(SITE, encoding="utf-8") as f:
        raw = f.read()
    site = json.loads(raw)
    text = qr_text(site)
    qr = segno.make(text, error="m", micro=False)
    rows = list(qr.matrix_iter(scale=1, border=0))
    parts = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            if row[x]:
                start = x
                while x < len(row) and row[x]:
                    x += 1
                parts.append("M%d %dh%dv1h-%dz" % (start, y, x - start, x - start))
            else:
                x += 1
    value = {"text": text, "modules": len(rows), "path": "".join(parts)}
    line = '  "reach_qr": %s,\n' % json.dumps(value, ensure_ascii=False)
    if '"reach_qr"' in raw:
        raw = re.sub(r'  "reach_qr": \{.*?\},\n', lambda m: line, raw, count=1, flags=re.S)
    else:
        raw = raw.replace('  "reach_line"', line + '  "reach_line"', 1)
    with open(SITE, "w", encoding="utf-8") as f:
        f.write(raw)
    print("reach_qr: %d x %d modules for %s" % (len(rows), len(rows), text))


if __name__ == "__main__":
    sys.exit(main())
