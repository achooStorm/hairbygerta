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
