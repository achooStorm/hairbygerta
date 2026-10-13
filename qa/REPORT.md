# QA report: Hair & Makeup by Gerta

Written by `qa/run_all.py`. Every path in this report is relative to the site folder.

- Address tested: the site folder on this computer (local site folder). Each browser check serves it through its own local server (qa/serve.py) on a free port
- Time: 2026-10-13 07:38:19, the run took 114 seconds
- Pages: all 10
- Viewports: desktop (1280 x 900), phone (iPhone 13)
- Widths of the visual comparison: desktop-1265 (desktop layout, 1265 px wide), desktop (desktop layout, 1280 px wide), desktop-1440 (desktop layout, 1440 px wide), desktop-1920 (desktop layout, 1920 px wide), phone (phone layout, iPhone 13, 390 px wide)
- Checks run: html, page, content, behavior, a11y, visual, licensing, repo

**Result: PASS.** Every check of every family that was run passed (exit code 0).

## Check families

| Family | Script | Result | Checks | Failed | Exit code | Seconds | Address it tested |
| --- | --- | --- | --- | --- | --- | --- | --- |
| html | `qa/check_html.py` | pass | 42 | 0 | 0 | 8 | local site folder |
| page | `qa/check_page.py` | pass | 422 | 0 | 0 | 92 | local site folder |
| content | `qa/check_content.py` | pass | 253 | 0 | 0 | 2 | local site folder |
| behavior | `qa/check_behavior.py` | pass | 272 | 0 | 0 | 91 | local site folder |
| a11y | `qa/check_a11y.py` | pass | 36 | 0 | 0 | 74 | local site folder |
| visual | `qa/visual_compare.py` | pass | 404 | 0 | 0 | 114 | local site folder |
| licensing | `qa/licensing_check.py` | pass | 33 | 0 | 0 | 16 | local site folder |
| repo | `qa/check_repo.py` | pass | 29 | 0 | 0 | 2 | local site folder |

## Pages

One row per page. A check column says `pass`, or how many checks of that family failed on that page (all viewports together; the visual column counts every width it compares). `-` means the family has no check for that row. The screenshot columns show the page at 1280 px and on the phone.

| Page | Desktop screenshot | Phone screenshot | html | page | content | behavior | a11y | visual | licensing | repo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| home | [qa/screenshots/home-desktop.png](screenshots/home-desktop.png) | [qa/screenshots/home-phone.png](screenshots/home-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| gallery | [qa/screenshots/gallery-desktop.png](screenshots/gallery-desktop.png) | [qa/screenshots/gallery-phone.png](screenshots/gallery-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| book-online | [qa/screenshots/book-online-desktop.png](screenshots/book-online-desktop.png) | [qa/screenshots/book-online-phone.png](screenshots/book-online-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| about | [qa/screenshots/about-desktop.png](screenshots/about-desktop.png) | [qa/screenshots/about-phone.png](screenshots/about-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| contact | [qa/screenshots/contact-desktop.png](screenshots/contact-desktop.png) | [qa/screenshots/contact-phone.png](screenshots/contact-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| english-refund-policy | [qa/screenshots/english-refund-policy-desktop.png](screenshots/english-refund-policy-desktop.png) | [qa/screenshots/english-refund-policy-phone.png](screenshots/english-refund-policy-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| accessibility-statement | [qa/screenshots/accessibility-statement-desktop.png](screenshots/accessibility-statement-desktop.png) | [qa/screenshots/accessibility-statement-phone.png](screenshots/accessibility-statement-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| english-privacy-policy | [qa/screenshots/english-privacy-policy-desktop.png](screenshots/english-privacy-policy-desktop.png) | [qa/screenshots/english-privacy-policy-phone.png](screenshots/english-privacy-policy-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| terms-conditions | [qa/screenshots/terms-conditions-desktop.png](screenshots/terms-conditions-desktop.png) | [qa/screenshots/terms-conditions-phone.png](screenshots/terms-conditions-phone.png) | pass | pass | pass | pass | pass | pass | pass | pass |
| 404 | [qa/screenshots/404-desktop.png](screenshots/404-desktop.png) | [qa/screenshots/404-phone.png](screenshots/404-phone.png) | pass | pass | pass | pass | pass | - | pass | pass |
| (whole site) | - | - | pass | - | pass | - | - | pass | pass | pass |

## Licensing

**Pass: zero matches.** No file of the site is identical to a restricted file, and every image that is not on the allowed list is a placeholder.

- Site files hashed: 308 (plus 0 archive members, 0 embedded pictures, 0 git objects)
- Different restricted hashes they were compared with: 150
- Images checked: 242 (3 allowed, 9 allowed-derivative, 52 placeholder, 178 site screenshot)
- SHA-256 matches with a restricted file: 0
- Licensing checks in the report: 33, failed: 0
- The script's own, longer report: [qa/reports/licensing.md](reports/licensing.md)

## Visual comparison with the Wix reference

404 comparisons, 0 outside the tolerance.

One row per width that was compared:

| Viewport | What it is | Comparisons | Outside tolerance | Pages with a difference | Biggest difference (px) |
| --- | --- | --- | --- | --- | --- |
| desktop-1265 | desktop layout, 1265 px wide | 111 | 0 | 0 | - |
| desktop | desktop layout, 1280 px wide | 62 | 0 | 0 | - |
| desktop-1440 | desktop layout, 1440 px wide | 62 | 0 | 0 | - |
| desktop-1920 | desktop layout, 1920 px wide | 62 | 0 | 0 | - |
| phone | phone layout, iPhone 13, 390 px wide | 106 | 0 | 0 | - |
| - | a check without a viewport | 1 | 0 | 0 | - |

Nothing is outside the tolerance.

Notes from the script: desktop_note = Each desktop width is compared with the Wix reference taken at that width, and only the Wix value passes (decision 17). The entries named brief-... test the brief's measurement list on our pages at 12 [... 19 more characters, see the JSON report]; phone_note = Phone: font size, letter spacing and line height are compared with the Wix numbers as written (decision 16). Places and sizes are listed with ok true against the Wix numbers times 390 / 320 (from 4 px [... 79 more characters, see the JSON report]; screenshots = qa/screenshots/visual_compare/; script = qa/visual_compare.py; side_by_side = ../hairbygerta-env/qa-private/side-by-side/ (outside the site folder, never commit); tolerance_brief_px = 2.0; tolerance_desktop_px = 2.0; wix_reference_measured = 2026-10-12

## Failed checks, grouped by who has to fix them

None.

## Not automated

A pass above says nothing about these requirements. No script of the suite tests them; they were last checked by hand in the QA review rounds and have to be checked by hand again after a change that touches them.

- **Visible focus on every link, button and field.** Tab through each page at 1280 px and on a phone and look for the outline on every stop (qa/check_a11y.py runs axe, which does not read outlines).
- **No sideways scroll at every width from 320 to 1920 px.** The suite tests 390, 1265, 1280, 1440 and 1920 px only. Drag the window from 320 px upwards, slowly past 760 and 1100 px, on every page.
- **README.md and MIGRATION.md say the right things.** The suite counts the lines of README.md and looks for em dashes, nothing else. Read both: the nine sections of the guide, its sources, and every command typed as written.
- **The commit guard really stops a commit.** After the repository exists: python tools/licensing_check.py --install-hook, then try to commit a copy of a restricted photo. The commit has to be refused.
- **tools/restricted-hashes.txt covers every restricted file.** Compare the fingerprints of every file in the private photo folder (and inside its zip files) with the list. Decision 30 says how many there are.
- **redirects-check.md.** Read it against the Wix sitemaps in the tools folder: every old address is listed with where it ends on the new site. The suite tests two old booking addresses only.
- **The phone layout on a real phone.** The suite uses a desktop browser set to the size of an iPhone 13. Open the published address on a real phone once.
- **The contact form opens the visitor's mail program.** The suite tests the mailto address the page builds, not what a mail program does with it. Send one message from a phone and one from a computer.

## Where the details are

- One JSON file per check family in `qa/reports/` with every check, passed or failed, and the full expected and actual values.
- Screenshots of our site in `qa/screenshots/`.
- Anything that shows the live Wix site (reference screenshots, side-by-side images) stays outside the site folder and is never committed.
