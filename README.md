# hairbygerta.com

The website of Hair & Makeup by Gerta as a plain static site: finished HTML pages, one stylesheet, one script and the images. It is made to take the place of the Wix site, with the same look, the same text and the same page addresses, hosted for free on GitHub Pages. This file is for whoever looks after the folder. The owner's step by step guide is `MIGRATION.md`. The official GitHub help pages behind what is said here about GitHub are listed at its end.

## What is where

| Where | What |
|---|---|
| `content/` | All the text. `site.json` holds what every page shares (menu, footer, phone, email, address, social links). The other files hold one page each. The opening hours are in `home.json`, `contact.json` and `book-online.json`. |
| `tools/` | `build_pages.py` makes the pages. `pages/` has one layout file per page. `CONTRACT.md` lists the names that the HTML, the stylesheet and the script share. The other files make the placeholders and icons and guard the photo rule. |
| `index.html`, `404.html`, `gallery/`, `book-online/`, `about/`, `contact/` and the four policy folders | The finished pages, one `index.html` per folder, at the same addresses as on Wix. Made by the build script. |
| `css/style.css` | All the styling. |
| `js/site.js` | The booking link, the phone menu, the gallery photo viewer, the contact form and the year in the footer. The contact form opens the visitor's own email program. The site itself sends nothing. |
| `images/`, `images/sm/`, `favicon.ico` | The pictures in full size, their small copies (at most 800 px on the long side) and the icons. `image-manifest.json` lists each picture with its size and status. |
| `seo/`, `sitemap.xml`, `robots.txt` | What search engines read. The build script copies `seo/jsonld-home.json` into the home page. |
| `qa/` | The test scripts and their last report, `qa/REPORT.md`. They need the Python setup in `hairbygerta-env`, a folder next to this one. `qa/run_all.py` says how to start them. A run takes about two minutes. Exit code 2 means a licensing match (a Wix-only photo was found in this folder): do not commit. A replaced photo is listed in the class `owner-photo`. A copy of a Wix photo stays a LICENSING MATCH whatever the manifest says. With `--base` it tests a published address, and it refuses an address that still shows the Wix site. |
| `redirects-check.md` | What happens to each old Wix address on this site. |

## The photo rule

- Only `images/logo.jpg`, `images/g12.jpg` and `images/g13.jpg` are licensed for use outside Wix, together with the copies and icons made from them.
- The other 26 photos are placeholders: beige pictures with a faint logo, each with the file name and pixel size of the photo it stands for.
- The original Wix photos live outside this folder, in the private folder `hairbygerta-wix-only-photos` next to it. They are never copied in, committed or uploaded.
- To put a real photo in place of a placeholder, follow `MIGRATION.md`, section 6. Both files must be replaced, `images/NAME.jpg` and `images/sm/NAME.jpg`. The build then records the photo in `image-manifest.json` with the status `owner-photo`, so that file needs no hand edit. `g12` and `g13` also have `.webp` copies in `images/` and `images/sm/`, which browsers show first: whoever replaces one of these two photos replaces its `.webp` copies too.
- `tools/make_placeholders.py` makes the placeholder files again. It needs Pillow, which the Python setup in `hairbygerta-env` has. It leaves real photos alone, lists them as kept and then ends with status 2, which is expected. `--check` writes nothing. Never use `--force` once real photos are in: it overwrites them.

Before every upload run `python tools/licensing_check.py` in this folder. Go on only when it answers "Photo licensing check passed". The check knows only exact copies of the Wix files, so a pass is no proof that a new photo may be used. `tools/hooks/pre-commit` runs the same check before each commit, in GitHub Desktop too. Switch it on with `python tools/licensing_check.py --install-hook`, once after the repository is created (`git init`) and once after every clone. Do not copy the hook file by hand. Never get around it: no `git commit --no-verify`, and in GitHub Desktop no "Bypass Commit Hooks" and no "Commit anyway".

## Changing a page

1. Edit the text in `content/`. Change only what stands between the quote marks. The `notes` at the end of a file are remarks and never show on the site. A fact that shows in several places is written in several files, so search all of `content/` for it. The phone number is also in `js/site.js` (the line with `var phoneHref`, the number the **Book Now** buttons call) and in `seo/jsonld-home.json`, which holds the address and the opening hours for search engines too. Change them there as well.
2. Run `python tools/build_pages.py` in this folder. It needs Python 3 and nothing else.
3. Read what it prints: `written` or `unchanged` for each page. A line that starts with `ERROR` or `WARNING` names the file and says what to fix. A page with an error is left as it was.

Never edit an `index.html` or `404.html` by hand, because the next run overwrites it. The layout of a page is in `tools/pages/`. The head, header and footer of every page are in `tools/build_pages.py`.

## Looking at the site on this computer

    python -m http.server 8000 --bind 127.0.0.1

Run this in the folder, then open http://localhost:8000/ in a browser. Ctrl + C stops it. No setup is needed, because every address inside the site is relative. A broken address shows Python's own error page here. On GitHub it shows `404.html`.

## Hosting on GitHub Pages

- The GitHub account `achooStorm` belongs to Gerta's helper, the person who built the site, not to Gerta. The helper signs in for everything on GitHub. Gerta cannot do those steps alone.
- Repository: `achooStorm/hairbygerta`, public. Everything that is committed is published, not only the pages, so nothing private belongs in this folder. The name and email address in the Git settings show with every commit.
- Settings, Pages: Source "Deploy from a branch", Branch `main`, folder `/ (root)`.
- Address: https://achoostorm.github.io/hairbygerta/. A push to `main` can take up to 10 minutes to show there.
- No custom domain yet: the Custom domain field stays empty and there is no `CNAME` file. The canonical tags and `sitemap.xml` already name https://www.hairbygerta.com/, the final address. When the domain is set (`MIGRATION.md`, section 4), GitHub adds a file `CNAME` to the repository. Always pull before a push, never force a push and never delete that file. Verifying the domain on GitHub ties hairbygerta.com to the helper's account. That is Gerta's decision, explained in section 4.
- The empty file `.nojekyll` tells GitHub to publish the files as they are. Keep it.
- First publishing, done by the helper: create the public repository without a README, `git init -b main`, switch on the commit hook, run the licensing check, commit, push `main`, choose the Pages settings above, wait for the build (up to 10 minutes) and open the address. The steps and their sources are in `MIGRATION.md`, section 1, part 4.

## The booking link

Every **Book Now** button calls 347-671-5095. The first line of code in `js/site.js` is `var BOOKING_URL = "";` and it stays empty, because the salon uses its own booking and has no online booking link. If an online booking link is ever added, it goes between the two quote marks. Nothing else changes and no page has to be rebuilt.

## Everything else

`MIGRATION.md` has the steps for the owner and her helper: the first publishing (section 1, part 4), what to check and save at Wix first (section 2), moving the domain away from Wix (section 3) and pointing it at this site (section 4), email forwarding for info@hairbygerta.com (section 5), replacing a placeholder with a real photo (section 6), booking by phone and where the phone number is written (section 7), what cannot be undone (section 8) and the yearly cost (section 9).
