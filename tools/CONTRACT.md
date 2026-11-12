# Build contract for hairbygerta.com

The shared agreement between the people (or agents) who work on this site: who owns which file, and the exact element names, classes and data attributes that the HTML, the stylesheet and the script all rely on. Change this file first, then the code.

## 1. Who owns what (only the owner edits a file)

| Area | Owns |
|---|---|
| ASSETS | `images/`, `images/sm/`, `favicon.ico`, `image-manifest.json`, `tools/make_placeholders.py`, `tools/make_icons.py`, `fonts/`, `tools/make_fonts.py`, `tools/make_share_image.py`, `tools/add_photo.py` |
| CONTENT | `content/*.json` |
| DESIGN | `css/style.css` |
| PAGES | `tools/build_pages.py`, `tools/pages/*.py`, every `index.html`, `404.html` (HTML is only ever produced by the generator, never edited by hand) |
| INTERACTION | `js/site.js` |
| SEO | `sitemap.xml`, `robots.txt`, `.nojekyll`, `seo/jsonld-home.json`, `redirects-check.md` |
| QA | `qa/` (edits no site file, files change requests instead) |
| DEPLOY | `.gitignore`, `.git/`, `tools/hooks/pre-commit`, `tools/licensing_check.py`, `tools/restricted-hashes.txt` |
| RUNBOOK | `MIGRATION.md`, `README.md` |

No committed file may contain an absolute path from this computer. All paths inside the site are relative and use forward slashes.

## 2. Pages

| slug | address | content file | page module | output |
|---|---|---|---|---|
| home | `/` | `content/home.json` | `tools/pages/home.py` | `index.html` |
| gallery | `/gallery/` | `content/gallery.json` | `tools/pages/gallery.py` | `gallery/index.html` |
| book-online | `/book-online/` | `content/book-online.json` | `tools/pages/book_online.py` | `book-online/index.html` |
| about | `/about/` | `content/about.json` | `tools/pages/about.py` | `about/index.html` |
| contact | `/contact/` | `content/contact.json` | `tools/pages/contact.py` | `contact/index.html` |
| english-refund-policy | `/english-refund-policy/` | `content/english-refund-policy.json` | `tools/pages/english_refund_policy.py` | `english-refund-policy/index.html` |
| accessibility-statement | `/accessibility-statement/` | `content/accessibility-statement.json` | `tools/pages/accessibility_statement.py` | `accessibility-statement/index.html` |
| english-privacy-policy | `/english-privacy-policy/` | `content/english-privacy-policy.json` | `tools/pages/english_privacy_policy.py` | `english-privacy-policy/index.html` |
| terms-conditions | `/terms-conditions/` | `content/terms-conditions.json` | `tools/pages/terms_conditions.py` | `terms-conditions/index.html` |
| 404 | `/404.html` | `content/404.json` | `tools/pages/not_found.py` | `404.html` |

Shared text (navigation, footer, business facts, social links, the font files to preload, Open Graph image) lives in `content/site.json`.

## 3. Content files (`content/*.json`)

- UTF-8 JSON. Every page file has `slug`, `path`, `title` (the title tag), `description` (the meta description), `h1`, then the page's text in reading order with self-describing keys, then `notes` (a list, holds any `ASK` items).
- Strings are plain text with real characters (’ – &), never HTML entities. The generator escapes them.
- The only exception is a key ending in `_html` or a block with an `html` field. Those may contain `<a>`, `<br>`, `<strong>`, `<em>` only. An internal link there is written `href="{{root}}english-privacy-policy/"` and the generator swaps `{{root}}` for the right relative prefix.
- Policy pages use `"blocks": [...]`, each block one of `{"type":"h2","text":…}`, `{"type":"h3","text":…}` (a sub-heading under an h2), `{"type":"p","text":…}` or `{"type":"p","html":…}`, `{"type":"ul","items":[…]}` where an item is a plain string or `{"html":…}`.
- An image slot is `{"slot":…, "file":"g12", "alt":…, "alt_original":…}`. `file` is the name without folder or extension. `alt` is what the page shows and is `""` for every placeholder. `alt_original` keeps the description of the old Wix photo for reference only.

## 4. Image manifest (`image-manifest.json`)

```
{
  "images": { "<name>": { "status": "allowed" | "placeholder",
                          "file": "images/<name>.jpg", "width": 0, "height": 0, "bytes": 0, "sha256": "",
                          "sm": { "file": "images/sm/<name>.jpg", "width": 0, "height": 0, "bytes": 0, "sha256": "" },
                          "webp": null } },
  "icons": [ { "file": "favicon.ico", "status": "allowed-derivative", "derived_from": "images/logo.jpg", "bytes": 0, "sha256": "" } ],
  "restricted_originals": [ { "name": "", "file": "<name>.jpg", "where": "folder" | "folder/sm" | "zip", "width": 0, "height": 0, "bytes": 0, "sha256": "", "status": "restricted" } ],
  "restricted_sha256": [ "every hash of every restricted file, one flat list" ],
  "composites": [ { "file": "images/share.jpg", "status": "allowed-derivative", "width": 1200, "height": 630, "bytes": 0, "sha256": "",
                    "parts": [ { "source": "images/g13.jpg", "kind": "photo" | "artwork", "box": [x0, y0, x1, y1], "source_box": [...] },
                               { "kind": "text", "box": [x0, y0, x1, y1] } ], "text": [ "..." ], "made_by": "tools/make_share_image.py" } ]
}
```

`images` has 29 entries: `logo`, `g12`, `g13` (allowed) and the 26 placeholders. `icons` has four entries (decision 39 added `images/icon-192.png`). `composites` (decision 39) lists pictures made from several allowed ones; `tools/make_share_image.py` writes its entry.

## 5. Generator (`tools/build_pages.py`, Python standard library only)

- `python tools/build_pages.py` builds every page. `--only home,gallery` builds just those pages and writes nothing else.
- Each page module defines `SLUG` and `render(ctx)` and returns `{"body": "<html for inside main>", "head_extra": ""}`.
- `ctx` gives the module `ctx.content` (its own JSON), `ctx.site`, `ctx.manifest`, `ctx.root` (`""` at the top, `"../"` one folder down), and the helpers `ctx.esc(text)`, `ctx.url("/gallery/")`, `ctx.inline(html)`, `ctx.blocks(blocks)`, `ctx.img(name, alt, width, height, lazy, variant, sizes)`, `ctx.is_placeholder(name)`.
- `PLACEHOLDERS` near the top of `build_pages.py` is the list of placeholder photo names. A name in that list always gets `alt=""` and `class="ph"`.
- `ctx.img` writes `<img src srcset sizes alt width height loading decoding>`. Only when the manifest lists a WebP copy for that image it wraps it as `<picture><source type="image/webp" srcset=…><img …></picture>`, so the stylesheet must not assume that an `img` is a direct child of its container.
- The generator does not write `sitemap.xml` or `robots.txt` (SEO owns them). It embeds `seo/jsonld-home.json` in the home page head.

## 6. HTML every page shares

```
<html lang="en"> <head>  charset, viewport, title, meta description,
  [home only] the two search engine verification metas (google-site-verification, msvalidate.01), canonical (https://www.hairbygerta.com/…),
  og:type og:locale og:site_name og:title og:description og:url og:image (https://www.hairbygerta.com/images/share.jpg) og:image:width og:image:height og:image:alt,
  twitter:card (summary_large_image) twitter:title twitter:description twitter:image twitter:image:alt,
  favicon.ico, images/favicon.png, images/icon-192.png (sizes 192x192), images/apple-touch-icon.png, meta theme-color, the two font preloads (fonts/figtree-latin.woff2 and fonts/bodoni-moda-italic-latin.woff2, as=font, crossorigin),
  css/style.css, <script>document.documentElement.classList.add("js")</script>, [home only] the JSON-LD script
<body class="page-<slug>">
<a class="skip" href="#main">Skip to main content</a>
<header class="site-header"><div class="inner">
  <a class="logo" href="…home…" aria-label="Hair &amp; Makeup by Gerta home"><img src="…images/logo.jpg" alt="" width="134" height="138"></a>
  <button class="menu-btn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="main-nav"><span></span><span></span><span></span></button>
  <nav class="main-nav" id="main-nav" aria-label="Main"><ul><li><a href="…" aria-current="page">Home</a></li> … Gallery, Book Online, About, Contact</ul></nav>
</div></header>
<main id="main"> … </main>
<footer class="site-footer">
  <div class="call-bar"><a class="call-bar-call" href="tel:+1-347-671-5095"> svg.call-bar-icon <span class="call-bar-label">Call to book</span> <span class="call-bar-num">347-671-5095</span></a></div>
  <div class="inner">
  <hr class="foot-rule">
  <div class="foot-cols">
    <div class="foot-brand"><p class="foot-name serif">Gerta Lila</p><p class="foot-role serif">Hair Stylist &amp; Makeup Artist</p><div class="social"> Facebook link, Instagram link (svg icons, aria-label, target=_blank rel=noopener) </div></div>
    <div class="foot-contact"><p> tel link </p><p> mailto link </p><p class="foot-addr">Le Vigne Hair Salon<br>644 Forest Ave<br>Staten Island, NY 10310</p></div>
    <ul class="foot-links"> the four policy links </ul>
  </div>
  <p class="copy">&copy; <span data-year>2026</span> Hair &amp; Makeup by Gerta</p>
</div></footer>
<script src="…js/site.js" defer></script>
```

No inline `style` attributes anywhere. Exactly one `h1` per page.

## 7. HTML per page (inside `main`)

- Home
  `p.site-title.serif > a` · `section.hero-box[aria-labelledby=hero-h]` holding `h1#hero-h.serif`, `hr.dots`, `p.welcome`, `a.btn` (to the Book Online page, no `data-book`), `a.phone` (tel), `p.salon`, `a.addr` (maps link, new tab, starts with `<span class="pin" aria-hidden="true">&#128205;</span>`), then
  `div.marquee[role=img][aria-label="Hours: Tuesday - Saturday, 9 AM - 5 PM"] > div.track[aria-hidden=true] > span × 6` ·
  `section.photo-row[aria-label="Featured work"] > img × 4` (home-styling, foils-highlights, home-smile, home-waves, each 288 × 545) ·
  `section.meet[aria-labelledby=meet-h]` holding `h2#meet-h.serif`, `p.t1`, `div.p1 > img` (makeup-red-lips, 313 × 422), `p.t2`, `div.p2 > img` (meet-extensions, 424 × 637).
- Gallery
  `div.page > h1.page-title` + `div.gallery > a × 21`, each `<a href="…images/NAME.jpg" aria-label="View photo N of 21"><img src="…images/sm/NAME.jpg" alt="…" width height loading="lazy" decoding="async"></a>`.
- Book Online
  `div.page > h1.services-title.serif` + `div.services > article.card × 10`, each `img` (sm copy, 290 × 195, `alt=""`) and `div.body` holding `h2.serif`, `p.desc`, `div.meta > p.duration + p.price`, `a.pill[data-book][href="tel:+1-347-671-5095"][aria-label="Book Now: SERVICE"]` with the text `Book Now`. Then `p.book-note`.
- About
  `div.about` holding `div.col.left > img × 2` (brunette-balayage, about-salon), `div.text > h1.serif + p`, `div.col.right > img × 2` (g10, copper-waves).
- Contact
  `div.contact-head` holding `p.kicker.serif`, `h1`, `p.contact-intro` (the intro sentence with its tel and mailto links) · `div.contact` holding `div.info > div.info-item × 5` (each `svg.info-icon[aria-hidden=true]` + `h2.serif` + lines; the Social Media one holds `div.social`) and
  `form#contact-form.contact-form[data-mailto="mailto:info@hairbygerta.com"][data-sent="the status line shown after sending"]` (no action, decision 41) with `div.row` (inputs `#first-name`, `#last-name`), `input#email[type=email][required][aria-describedby=email-error]`, `p#email-error.field-error[data-missing][data-invalid][hidden]`, `textarea#message`, `button[type=submit]` "Send", `p.form-note[role=status]`. Field `name` equals its `id`. Every field has a `label[for]`. ·
  `div.map > iframe[title][data-src][loading=lazy]` + `p.map-open > a[href=maps_href][target=_blank][rel=noopener]`.
- Policy pages
  `article.legal` holding `h1`, then `h2`, `p`, `ul` from the blocks.
- 404
  `div.notfound` holding `h1`, `p`, `a.btn` back to Home. The head also carries `<meta name="robots" content="noindex">` and a tiny inline script that sets a `<base>` so the page still finds its stylesheet when shown for a deep broken address.

## 8. What the script may touch (`js/site.js`, loaded with `defer`)

| Hook | Behaviour |
|---|---|
| `var BOOKING_URL = "";` first statement in the file | empty → every `[data-book]` gets `href="tel:+1-347-671-5095"`; filled → `href` = the link, `target="_blank"`, `rel="noopener"` |
| `.menu-btn`, `#main-nav` | toggles class `open` on the nav, `aria-expanded` on the button, class `menu-open` on `body`; closes on Escape (focus back to the button) and on any nav link click |
| `.gallery a` | builds once `div.lightbox[role=dialog][aria-modal=true][aria-label="Photo viewer"]` holding `button.lb-close`, `button.lb-prev`, `img.lb-img`, `button.lb-next`, `p.lb-count`; open = class `open` on it + class `lightbox-open` on `body`; arrows, Escape, click on the backdrop, focus trapped, focus returned to the opening link, `alt` copied from the thumbnail |
| `#contact-form`, `#email-error`, `.form-note` | on submit builds `mailto:` + the address of `data-mailto` + `?subject=Website message from NAME&body=…`, opens it by clicking a temporary `<a>` element, writes a short status line into `.form-note`; when the browser finds `#email` empty or not an email address it shows the `data-missing` or `data-invalid` text of `#email-error` under the field (in place of the browser's bubble), sets `aria-invalid="true"` and focuses the field; the message goes once the address is valid |
| `.map iframe[data-src]` | moves `data-src` into `src` when the map comes within 600 px of the window (IntersectionObserver; without it at once) |
| `[data-year]` | current year |

Stylesheet side of the same deal: `body.menu-open` and `body.lightbox-open` stop page scroll, `html.js` marks that the script is running (without it the phone menu shows as a plain list and `.menu-btn` is hidden).

## 9. Stylesheet

One file, `css/style.css`, CSS variables in one `:root` block at the top, breakpoints `@media (max-width: 1100px)` and `@media (max-width: 760px)`, a `prefers-reduced-motion` block, visible `:focus-visible` on every link, button and field. Every class named in sections 6 to 8 is styled there and nowhere else.

## 10. Decisions taken during the build (these win over older task text where the two differ)

1. **Which width the measurements belong to.** The measurement list in the brief was taken in a 1280 px wide browser window that had a 15 px scrollbar, so the page itself was 1265 px wide. Checked against the live Wix site: at 1265 px the photo row images are 288 x 545 and the footer columns start at 30, 397 and 890; at 1280 px without a scrollbar they are 292 x 545 and 30, 401 and 901. So the list is checked at a 1265 x 900 viewport. Comparisons with the Wix reference files use the width those files were taken at (`measure-<slug>-desktop.json` is 1280, `measure-<slug>-w1265.json`, `-w1440.json` and `-w1920.json` are the other widths).
2. **The Wix desktop layout is fluid, and so is ours.** On Wix the page keeps a 26 px side margin and stretches: the four home photos share the full width (fixed 545 px height, about 20 px gaps), the large Meet Gerta photo is 637 px tall and grows towards the right edge, the gallery fills the width, the right-hand About photos and the third footer column follow the right side, while the beige box (778 px), the service cards (290 px) and the text columns keep their size and stay centred. The stylesheet follows this from 1101 px upwards, so it matches the brief at 1265 px and the Wix reference at 1280, 1440 and 1920 px. No fixed 1213 px cap on those rows.
3. **Values that the brief lists as 0.8 px** (dotted rule, pill border) are 1 px on Wix; 0.8 is what a 1 px line reports on a screen set to 125 percent. Use 1 px. **Service card text** (description, duration, price, Book Now) is 16 px on Wix at both widths (24 px and 32 px line heights); use 16 px, which is also within the 2 px tolerance of the 14 px in the brief.
4. **The beige box is centred** as the brief says (Wix sits it 4 px right of centre).
5. **About page, top right photo** is `g10` as the brief says. (The live Wix page shows the photo we call `foils-highlights` there. Open question for the owner.)
6. **Accessibility Statement.** The markup keeps the `h1` first. The stylesheet shows the first paragraph as the dark full-width band above the title, as on Wix (`body.page-accessibility-statement`).
7. **Terms page.** The numbered lines 1 to 9 are plain paragraphs, as on Wix. A `h3` block stays allowed in policy pages (`article.legal` may hold `h1`, `h2`, `h3`, `p`, `ul`).
8. **Contact info order** is Address, Phone, Email, Social Media, Hours. The required mark is `<span aria-hidden="true">*</span>` inside the Email label.
9. **`og:site_name`** is the business name, Hair & Makeup by Gerta.
10. **Ampersands in `html` fields** of content files are plain `&`; the generator escapes them and leaves the allowed tags alone.
11. **WebP copies.** A non-null `webp` in the manifest is `{file, width, height, bytes, sha256, sm: {file, width, height, bytes, sha256}}`. Only `g12` and `g13` have one. Whoever replaces `g12.jpg` or `g13.jpg` must replace the matching `.webp` files too (deleting them breaks the picture, because the page still names them).
12. **Lightbox.** The three buttons are `type="button"` with `aria-label` Close, Previous photo, Next photo; the stylesheet draws their signs. The dialog has the `hidden` attribute while closed. The counter reads `N / TOTAL`. A swipe moves to the next or previous photo.
13. **Mobile menu** also closes when the window grows wider than 760 px.
14. **404 page.** `body.page-404`. Its inline script sets the site root for deep broken addresses and sends old Wix booking addresses (`booking-calendar/...`, `service-page/...`) to the Book Online page.
15. **A replaced photo.** A name taken out of `PLACEHOLDERS` must still build while the manifest still lists it as a placeholder: the generator then reads the size from the image file itself and uses the `alt` from the content file.
16. **Phone sizes are the Wix numbers as written.** Wix draws its phone page 320 px wide and lets the phone enlarge it, so its 14 px text shows about 17 px tall on a 390 px screen. The brief gives the phone sizes as written (header 96 px, logo 80 px, address and hours line 14 px), so the whole phone layout uses the written sizes, not the enlarged ones. QA compares phone font sizes as written and judges phone layout by the order of the blocks and by everything fitting the screen, not by pixel positions. (Open question for the owner: text on a phone is about a fifth smaller than on the Wix phone page.)
17. **Desktop comparisons.** At 1280 px our page is compared with the Wix reference taken at 1280 px, and only the Wix value passes. The brief's measurement list is checked at 1265 px. The Wix references at 1440 and 1920 px are compared too.
18. **Links inside a sentence are underlined** on our site (they are not on Wix). This is deliberate, so that a link can be told from the text around it.
19. **`BOOKING_URL`.** The first statement of `js/site.js` is `var BOOKING_URL = "";` today, and `var BOOKING_URL = "https://...";` once the owner has pasted her link. Both are valid.
20. **Nothing temporary lives in the site folder.** The old `_tmp` folder was moved out to the tools folder.
21. **Centred means centred.** The site title, the welcome paragraph, the dotted rule, the Book Online button and the address line on the home page are centred, as the brief says. On Wix they sit 3 to 18 px right of centre (hand placed in the editor); those offsets are not copied and count as intended differences.
22. **Privacy Policy on the phone** keeps the order of the desktop page (each paragraph under its heading). The Wix phone page moves eleven paragraphs to the end; that is not copied.
23. **Apostrophes** follow the live Wix text: the curly one in Kids’ Haircut and I’m, the straight one in It's Your Day to Shine! and Let's Connect.
24. **Policy pages keep one text edge.** On the four policy pages the text keeps one column edge and the titles stay centred. The Wix offsets of 7 to 28 px between blocks on those pages are editor drift and are not copied (same reasoning as decision 21).
25. **Service card text on phones.** The 16 px of decision 3 applies from 761 px up. On phones the cards use the Wix phone sizes as written (decision 16).
26. **What the generator and the script do beyond sections 5 to 8** (recorded here so nobody removes it by accident): `ctx` also has `ctx.slug`, `ctx.path` and `ctx.social()`; a page module may also return `robots` and `head_first`; the generator prints a WARNING that names the forgotten step when a photo and the `PLACEHOLDERS` list disagree; gallery photos 1 to 3 load eagerly and the rest lazily; the small script in the head that adds the `js` class also removes it again if `js/site.js` fails to load, so the phone menu never stays hidden; a booking link pasted without `https://` gets it added; the lightbox carries `tabindex="-1"` and ignores the second click of a double-click and a held Enter key; the menu also closes when focus leaves it; each manifest icon entry has a `sizes` list and the manifest has a `checks` list.
27. **A replaced photo needs no extra step.** When the generator builds a page with a photo whose name has been taken out of `PLACEHOLDERS` and whose file is no longer a placeholder, it also updates that photo's entry in `image-manifest.json`: status `owner-photo`, with the size, byte count and SHA-256 of the files now on disk (full size and 800 px copy). The QA licensing check accepts an `owner-photo` entry when its hash is not a restricted one. Nothing else writes to the manifest.
28. **The GitHub account achooStorm belongs to Gerta's helper, not to Gerta.** The helper signs in for everything on GitHub (publishing, Pages settings, the custom domain). Verifying the domain on GitHub ties hairbygerta.com to the helper's account, so the guide says that in plain words and marks it as Gerta's decision.
29. **Manifest status values** are `allowed` (only logo, g12, g13), `placeholder` and `owner-photo`. For an `owner-photo` the QA check also requires that the recorded SHA-256 equals the file (full size and 800 px copy each) and that the file is no longer a placeholder. The `checks` list in the manifest is the record of the day the manifest was first written.
30. **Deploy rules.** `tools/restricted-hashes.txt` holds 60 fingerprints (58 restricted pictures and the two backup zip files) and is never trimmed. Git ignores every picture under `qa/`. The commit guard is switched on with `python tools/licensing_check.py --install-hook`, once after the repository is created and once after every clone. After GitHub has added a `CNAME` file, always pull before pushing and never force push.
31. **Social icons.** `ctx.social` takes `icons="disc"` (footer) or `icons="bare"` (Contact page). With `--out` the generator writes a changed manifest into the `--out` folder, never into the site folder.
32. **Gallery columns.** Two columns on phones, as the brief says (the Wix phone page shows mostly one photo per row; not copied). Three columns on desktop, and a fourth from about 1600 px wide so that tiles are never drawn wider than their 800 px files and the page is about as tall as on Wix.
33. **Contact page title** is the new one, as the brief asks (the Wix one, "Contact | Hairbygerta", is the automatic default).
34. **This contract** is kept by the director of the build; nobody else edits it.
35. **The 404 page** is noindex and carries no canonical link and no Open Graph tags.
36. **Corrections to decision 30.** The 60 fingerprints are 53 restricted pictures, the two backup zip files, and 5 old copies of files made from the allowed logo, g12 and g13 (kept on purpose: any doubt means restricted). `.gitattributes` is a DEPLOY file: all text is stored and checked out with LF, pictures are binary.
37. **QA suite.** Eight check families; the eighth, `qa/check_repo.py`, checks the folder itself (pages equal a fresh generator run, line endings, no local paths, no leftovers). The gallery photo area may be up to 20 percent taller than on Wix. The fourth gallery column starts at 1600 px without a media rule.
38. **The fonts are files of the site (9 November 2026).** Bodoni Moda Italic and Figtree, the same two fonts as before, now come from the folder `fonts/` and no longer from Google Fonts. Each font is two WOFF2 files (latin and latin-ext, as Google cuts them), made by `tools/make_fonts.py` from github.com/google/fonts and listed with their SHA-256 in `fonts/fonts.json`, next to the two license texts. The Bodoni file has the optical size 14 built in and keeps weights 400 to 700; the letters are drawn exactly as before. The section "05 Fonts" of `css/style.css` holds one `@font-face` rule per file (`font-weight: 400 700`, `font-display: swap`, the `unicode-range` of fonts.json). Every page preloads the two latin files. What this changes: no page and no stylesheet asks a font server for anything (`qa/check_repo.py`, font-preload, fonts-folder, font-face-rules), the Privacy Policy no longer names Google Fonts (`qa/check_content.py`), the QA network rule lets no font host through any more (`qa/common.py`, `FONT_HOSTS` is empty), and `content/site.json` has `font_preloads` in place of `fonts_href`.
39. **Share image, search data, home screen icon (9 November 2026).** Link previews show `images/share.jpg`, 1200 x 630 px: g13 and g12 at full height on the left and right, the logo, the business name, the role and the place between them, on the beige, in the site's fonts. `tools/make_share_image.py` makes it and records it in the manifest under `composites` with the box of each part. `qa/licensing_check.py` accepts a composite only when its SHA-256 is the recorded one, every photo or logo part shows the allowed image it names, and everything else is the plain beige of the site or a line of text (a planted photo in the middle or inside a line of text is refused). Every indexable page also carries og:image:width, og:image:height, og:image:alt (`og_image_alt` in `content/site.json`), og:locale and the five twitter tags. `seo/jsonld-home.json` now also gives `hasMap` (the maps link of the site), `containedInPlace` (Le Vigne Hair Salon and its address), `employee` (Gerta Lila, Hair Stylist & Makeup Artist), the ten services as `hasOfferCatalog` (names and descriptions of the Book Online page, no prices) and three images. `tools/make_icons.py` makes a fourth icon, `images/icon-192.png`, linked with `sizes="192x192"` for Android home screens, and every page has `<meta name="theme-color" content="#fefefd">` (`theme_color` in `content/site.json`).
40. **Call bar and tap targets on phones (9 November 2026).** Every page has a Call button that stays at the bottom of the screen up to 760 px wide (`div.call-bar` at the start of the footer, hidden on wider screens and in print). Its words are `call_bar_label` in `content/site.json`, then the phone number, and it calls `tel_href`. It sits under the open phone menu and under the photo viewer, it steps aside while a form field has the focus (the phone keyboard needs the room), and the dark footer runs on under it. On phones the footer phone, email and policy links, the Contact page phone and email links and the social icons are 44 px tap targets, and the Book Online button of the home page is 44 px tall. QA: the bar's words are an intended difference from Wix (`qa/check_content.py`), and on the phone the bar is intended and pushes nothing down (`qa/visual_compare.py`).
41. **Contact form and map (9 November 2026).** The form has no `action` any more: a form whose action is a mailto address makes Chrome report the Contact page as sending a form over an insecure connection (PageSpeed best practices 77). The address is in `data-mailto` and the script opens the email app as before. Without the script the stylesheet hides the form (`html:not(.js)`), and the sentence above it still links the phone number and the email address. The browser still checks the Email field (`required`, `type=email`), and the script shows its finding in words under the field (`content/contact.json`, `form.errors`). The status line after Send now also says what to do when no email app opens. The map frame carries its address in `data-src` and gets it only when the visitor scrolls near it, so a visitor who never does sends nothing to Google; under it `p.map-open` links the Maps address of `content/site.json` ("Open in Google Maps", `map.open_label`), which also serves visitors without the script. The beige stands on the frame itself while it is empty. QA: `qa/check_behavior.py` tests the messages and the case without the script, `qa/check_content.py` reads the address from `data-mailto` and refuses an action, the map link is intended in `qa/check_content.py` and `qa/visual_compare.py`.
42. **Own photos in one step (9 November 2026).** `tools/add_photo.py PHOTO NAME --alt "..."` puts one of the owner's photos in the place of the placeholder NAME (`--list` shows the 26 places, `--batch LIST.csv` takes many, `--dry-run` writes nothing). It turns the photo upright, converts it to sRGB, writes `images/NAME.jpg` (at most 1600 px), `images/sm/NAME.jpg` (at most 800 px) and a WebP copy of each, with no metadata. It writes the alt text into every content slot of NAME, takes NAME out of `PLACEHOLDERS`, records the WebP copies under `webp` in the manifest entry and builds the pages, which record the photo as owner-photo (decision 27). It refuses HEIC files, photos under 800 px and any file whose SHA-256 is in `tools/restricted-hashes.txt`. A folder named `new-photos`, where the originals wait, is kept out like `source-photos`: `.gitignore`, the commit guard (`FORBIDDEN_FOLDERS`), the git checks of `qa/licensing_check.py` and the leftover check of `qa/check_repo.py`. The originals belong outside the site folder, because phone photos carry the place where they were taken.
43. **Policy page titles, phone booking in the Terms, the date of the Accessibility Statement (12 November 2026).** The titles of the four policy pages end with "Hair & Makeup by Gerta", the name the other pages use in their titles (the Wix ones end with "Hairbygerta"). Online booking was dropped on 2 November 2026, so three sentences of the Terms & Conditions no longer speak of booking online or through the site: "booking an appointment" without "through it", "Appointments can be requested by phone or in person." and "Requesting an appointment does not guarantee availability" with "a confirmation from us" at its end. The Accessibility Statement says it was last updated on 11/12/2026, the day it was read again. Each change is in the notes of its content file, and all eight are on the fixed list of intended differences from the Wix wording (`qa/check_content.py`: `POLICY_TITLES`, `TERMS_PHONE_BOOKING`, `ACCESSIBILITY_UPDATED`).
48. **Back to the Wix look (12 November 2026).** The owner withdrew the redesign of the same day (decisions 44 to 47, commits f4b042e to 5449172, merged into `main` as pull request #1) and asked for the Wix look of decision 43 again. Every file is back to its state after decision 43; those four decisions stay in the git history only and their numbers are not used again. The empty photo places are filled one by one with the owner's own or newly licensed photos through `tools/add_photo.py` (decision 42).
