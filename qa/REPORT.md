# QA report: Hair & Makeup by Gerta

Written by `qa/run_all.py`. Every path in this report is relative to the site folder.

- Address tested: the site folder on this computer (local site folder). Each browser check serves it through its own local server (qa/serve.py) on a free port
- Time: 2026-11-13 00:03:55, the run took 7 seconds
- Pages: all 10
- Viewports: desktop (1280 x 900), phone (iPhone 13)
- Checks run: content, repo
- Checks NOT run this time: html, page, behavior, a11y, visual, licensing

**Result: PASS.** Every check of every family that was run passed (exit code 0).

Licensing was not checked in this run. Run the full suite before any commit.

## Check families

| Family | Script | Result | Checks | Failed | Exit code | Seconds | Address it tested |
| --- | --- | --- | --- | --- | --- | --- | --- |
| html | `qa/check_html.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:38:26): pass |
| page | `qa/check_page.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:39:51): pass |
| content | `qa/check_content.py` | pass | 272 | 0 | 0 | 1 | local site folder |
| behavior | `qa/check_behavior.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:39:49): pass |
| a11y | `qa/check_a11y.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:39:32): pass |
| visual | `qa/visual_compare.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:40:13): pass |
| licensing | `qa/licensing_check.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:40:36): pass |
| repo | `qa/check_repo.py` | pass | 31 | 0 | 0 | 6 | local site folder |

## Pages

One row per page. A check column says `pass`, or how many checks of that family failed on that page (all viewports together; the visual column counts every width it compares). `-` means the family has no check for that row. The screenshot columns show the page at 1280 px and on the phone.

| Page | Desktop screenshot | Phone screenshot | html | page | content | behavior | a11y | visual | licensing | repo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| home | [qa/screenshots/home-desktop.png](screenshots/home-desktop.png) (from an earlier run) | [qa/screenshots/home-phone.png](screenshots/home-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| gallery | [qa/screenshots/gallery-desktop.png](screenshots/gallery-desktop.png) (from an earlier run) | [qa/screenshots/gallery-phone.png](screenshots/gallery-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| book-online | [qa/screenshots/book-online-desktop.png](screenshots/book-online-desktop.png) (from an earlier run) | [qa/screenshots/book-online-phone.png](screenshots/book-online-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| about | [qa/screenshots/about-desktop.png](screenshots/about-desktop.png) (from an earlier run) | [qa/screenshots/about-phone.png](screenshots/about-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| contact | [qa/screenshots/contact-desktop.png](screenshots/contact-desktop.png) (from an earlier run) | [qa/screenshots/contact-phone.png](screenshots/contact-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| english-refund-policy | [qa/screenshots/english-refund-policy-desktop.png](screenshots/english-refund-policy-desktop.png) (from an earlier run) | [qa/screenshots/english-refund-policy-phone.png](screenshots/english-refund-policy-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| accessibility-statement | [qa/screenshots/accessibility-statement-desktop.png](screenshots/accessibility-statement-desktop.png) (from an earlier run) | [qa/screenshots/accessibility-statement-phone.png](screenshots/accessibility-statement-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| english-privacy-policy | [qa/screenshots/english-privacy-policy-desktop.png](screenshots/english-privacy-policy-desktop.png) (from an earlier run) | [qa/screenshots/english-privacy-policy-phone.png](screenshots/english-privacy-policy-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| terms-conditions | [qa/screenshots/terms-conditions-desktop.png](screenshots/terms-conditions-desktop.png) (from an earlier run) | [qa/screenshots/terms-conditions-phone.png](screenshots/terms-conditions-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| 404 | [qa/screenshots/404-desktop.png](screenshots/404-desktop.png) (from an earlier run) | [qa/screenshots/404-phone.png](screenshots/404-phone.png) (from an earlier run) | not run | not run | pass | not run | not run | not run | not run | pass |
| (whole site) | - | - | not run | not run | pass | not run | not run | not run | not run | pass |

## Licensing

Not run this time.

## Visual comparison with the Wix reference

Not run this time.

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
