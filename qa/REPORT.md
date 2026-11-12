# QA report: Hair & Makeup by Gerta

Written by `qa/run_all.py`. Every path in this report is relative to the site folder.

- Address tested: the site folder on this computer (local site folder). Each browser check serves it through its own local server (qa/serve.py) on a free port
- Time: 2026-11-12 14:06:48, the run took 31 seconds
- Pages: all 10
- Viewports: desktop (1280 x 900), phone (iPhone 13)
- Checks run: html, page, content, behavior, a11y
- Checks NOT run this time: licensing, repo
- Open questions for the owner: see the section Open questions below

**Result: PASS.** Every check of every family that was run passed (exit code 0).

Licensing was not checked in this run. Run the full suite before any commit.

## Check families

| Family | Script | Result | Checks | Failed | Exit code | Seconds | Address it tested |
| --- | --- | --- | --- | --- | --- | --- | --- |
| html | `qa/check_html.py` | pass | 42 | 0 | 0 | 31 | local site folder |
| page | `qa/check_page.py` | pass | 422 | 0 | 0 | 24 | local site folder |
| content | `qa/check_content.py` | pass | 379 | 0 | 0 | 1 | local site folder |
| behavior | `qa/check_behavior.py` | pass | 279 | 0 | 0 | 31 | local site folder |
| a11y | `qa/check_a11y.py` | pass | 36 | 0 | 0 | 29 | local site folder |
| licensing | `qa/licensing_check.py` | not run | - | - | - | - | last report on disk (2026-10-13 07:40:36): pass |
| repo | `qa/check_repo.py` | not run | - | - | - | - | last report on disk (2026-11-12 20:05:48): pass |

## Pages

One row per page. A check column says `pass`, or how many checks of that family failed on that page (all viewports together; the visual column counts every width it compares). `-` means the family has no check for that row. The screenshot columns show the page at 1280 px and on the phone.

| Page | Desktop screenshot | Phone screenshot | html | page | content | behavior | a11y | licensing | repo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| home | [qa/screenshots/home-desktop.png](screenshots/home-desktop.png) | [qa/screenshots/home-phone.png](screenshots/home-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| gallery | [qa/screenshots/gallery-desktop.png](screenshots/gallery-desktop.png) | [qa/screenshots/gallery-phone.png](screenshots/gallery-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| book-online | [qa/screenshots/book-online-desktop.png](screenshots/book-online-desktop.png) | [qa/screenshots/book-online-phone.png](screenshots/book-online-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| about | [qa/screenshots/about-desktop.png](screenshots/about-desktop.png) | [qa/screenshots/about-phone.png](screenshots/about-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| contact | [qa/screenshots/contact-desktop.png](screenshots/contact-desktop.png) | [qa/screenshots/contact-phone.png](screenshots/contact-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| english-refund-policy | [qa/screenshots/english-refund-policy-desktop.png](screenshots/english-refund-policy-desktop.png) | [qa/screenshots/english-refund-policy-phone.png](screenshots/english-refund-policy-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| accessibility-statement | [qa/screenshots/accessibility-statement-desktop.png](screenshots/accessibility-statement-desktop.png) | [qa/screenshots/accessibility-statement-phone.png](screenshots/accessibility-statement-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| english-privacy-policy | [qa/screenshots/english-privacy-policy-desktop.png](screenshots/english-privacy-policy-desktop.png) | [qa/screenshots/english-privacy-policy-phone.png](screenshots/english-privacy-policy-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| terms-conditions | [qa/screenshots/terms-conditions-desktop.png](screenshots/terms-conditions-desktop.png) | [qa/screenshots/terms-conditions-phone.png](screenshots/terms-conditions-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| 404 | [qa/screenshots/404-desktop.png](screenshots/404-desktop.png) | [qa/screenshots/404-phone.png](screenshots/404-phone.png) | pass | pass | pass | pass | pass | not run | not run |
| (whole site) | - | - | pass | - | pass | - | - | not run | not run |

## Open questions

Copied from [qa/open-questions.md](open-questions.md). Not a result of a check and not counted in the result above.

Written on 12 November 2026, after the redesign (build contract, decisions 44 to 47).

**Where the checks ran.** The builder worked in a sandbox, so no single machine could run all seven check families.

- html, page, content, behavior and a11y are the checks of this report. They ran in a cloud workspace on a byte for byte copy of this folder (Chrome for Testing 153, Java 21). They need Playwright and Java 17 or newer, which the sandbox on this computer does not have.
- repo ran on this computer the same day, against the real repository, and passed (`qa/reports/check_repo.json`).
- licensing is not part of this report. Its last check, `restricted_folder`, reads the private folder with the Wix-only photos, and the builder was not allowed to open that folder. Run without the folder, the other 32 checks passed. The commit guard (`tools/licensing_check.py`) ran before every commit of the redesign and passed.

Before the site is published, run the whole suite once on the Windows setup in `hairbygerta-env`, as `qa/run_all.py` says in its first lines.

**Questions for the owner.**

1. The Gallery has one new sentence, "See more of my work on Instagram." The design brief asked for a line that points to Instagram while the page has fewer than six photos. Is the wording right?
2. Sentence case is a rule of the new look, so five texts changed their capital letters. They read Our services, Let's connect, Social media, First name and Last name. Is that fine?
3. The hours read "Tuesday to Saturday, 9 AM to 5 PM" on every page, as the brief writes them. The Wix site had "Tuesday - Saturday, 9 AM - 5 PM". This was left to the builder (decision 46). Say so if the hyphens should come back.
4. `svc-haircut` and `svc-bridal` were photo places of the Services page only. That page shows no photos now, so no page shows these two. Their files stay. Should one of them get a place on another page?
5. The picture that link previews show (`images/share.jpg`) still has the beige of the old look. Its tags are unchanged. Should `tools/make_share_image.py` make it again in the new colors?
6. The logo is a small JPG, 225 px. A larger file or an SVG from whoever drew it would look sharper in the header.

**Look at these by hand before publishing.** The pages on a real phone, the Call button and the Text Gerta link on that phone (one tap each), and the contact form with a real email app.

## Licensing

Not run this time.

## Visual comparison with the Wix reference

Not run. `qa/visual_compare.py` was retired on 12 November 2026 by decision 44 of tools/CONTRACT.md. The site no longer copies the Wix look, so a measurement against the Wix reference says nothing about whether the pages are right.

## Failed checks, grouped by who has to fix them

None.

## Other reports found in qa/reports

Not started by `qa/run_all.py` and not counted in the result above.

| Report | Written | Result |
| --- | --- | --- |
| qa/reports/visual_compare.json | 2026-10-13 07:40:13 | pass (404 checks) (last report of the retired visual comparison with Wix (decision 44), no longer written or read) |

## Not automated

A pass above says nothing about these requirements. No script of the suite tests them; they were last checked by hand in the QA review rounds and have to be checked by hand again after a change that touches them.

- **Visible focus on every link, button and field.** Tab through each page at 1280 px and on a phone and look for the outline on every stop (qa/check_a11y.py runs axe, which does not read outlines).
- **No sideways scroll at every width from 320 to 1920 px.** The suite tests 390 and 1280 px only. Drag the window from 320 px upwards, slowly past 760 and 1100 px, on every page.
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
