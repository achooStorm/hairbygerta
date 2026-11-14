# Old Wix addresses and what happens to them on the new site

This list answers one question: when someone follows an old link, a bookmark or a Google result of the Wix site, what do they get on the new site?

Checked on 12 October 2026. The addresses come from three places: the links on the nine live Wix pages, the seven Wix sitemaps, and a slow, read-only crawl of the live Wix site that followed internal links two levels deep from every page, from `/blog` and from one service page. Only text and status codes were read. No image was downloaded.

## Summary

| Decision | Addresses |
|---|---|
| SAME | 11 |
| REDIRECTED | 20 |
| GONE | 27 |
| Total found | 58 |

- All 58 addresses answer on Wix today (status 200). None was already broken.
- SAME (11): the nine pages, plus `robots.txt` and `sitemap.xml`.
- REDIRECTED (20): the ten Wix booking calendar addresses and the ten Wix service detail addresses. Both groups lead to Book Online.
- GONE (27): the blog page, its three posts and its feed (5), the shop category page and its 12 sample products (13), a Wix member profile (2) and the seven partial Wix sitemaps (7). None of them needs a fix, the table says why for each one.
- No address is left broken without a fix or a reason.
- Checked on the built site (12 October 2026): all 58 addresses behave as the table says, 0 are broken. See the result lines under "How this was checked".

## What the three decisions mean

- SAME: the new site has a page at the same address. Wix writes addresses without a slash at the end (`/gallery`), the new site writes them with one (`/gallery/`). GitHub Pages passes the first form on to the second by itself, so old links keep working.
- REDIRECTED: the new site has no page at this address. GitHub Pages shows the 404 page, and a short script in that page sends the visitor straight on to `/book-online/`.
- GONE: the new site has no page at this address. The visitor sees the 404 page ("Page not found") with a Back to Home button.

Addresses are written from the root of the site, the way they will be on www.hairbygerta.com. On the test address https://achoostorm.github.io/hairbygerta/ each one sits behind `/hairbygerta`, for example `/hairbygerta/gallery/`.

## All 58 addresses

| Address | What it is | Decision | Fix |
|---|---|---|---|
| `/` | Home page | SAME | None needed. `index.html` exists. |
| `/gallery` | Gallery page | SAME | None needed. `gallery/index.html` exists. The address now ends with a slash (`/gallery/`), the old form is passed on to it. |
| `/book-online` | Book Online page (the ten services) | SAME | None needed. `book-online/index.html` exists. The address now ends with a slash (`/book-online/`), the old form is passed on to it. |
| `/about` | About page | SAME | None needed. `about/index.html` exists. The address now ends with a slash (`/about/`), the old form is passed on to it. |
| `/contact` | Contact page | SAME | None needed. `contact/index.html` exists. The address now ends with a slash (`/contact/`), the old form is passed on to it. |
| `/english-refund-policy` | Refund & Cancellation Policy page | SAME | None needed. `english-refund-policy/index.html` exists. The address now ends with a slash (`/english-refund-policy/`), the old form is passed on to it. |
| `/accessibility-statement` | Accessibility Statement page | SAME | None needed. `accessibility-statement/index.html` exists. The address now ends with a slash (`/accessibility-statement/`), the old form is passed on to it. |
| `/english-privacy-policy` | Privacy Policy page | SAME | None needed. `english-privacy-policy/index.html` exists. The address now ends with a slash (`/english-privacy-policy/`), the old form is passed on to it. |
| `/terms-conditions` | Terms and Conditions page | SAME | None needed. `terms-conditions/index.html` exists. The address now ends with a slash (`/terms-conditions/`), the old form is passed on to it. |
| `/robots.txt` | Instructions for search engines | SAME | None needed. The new file allows every page and names the new sitemap. |
| `/sitemap.xml` | List of pages for search engines. On Wix it is an index of seven partial lists. | SAME | None needed. The new file is one list with the nine pages. |
| `/booking-calendar/haircut-style` | Wix Bookings calendar for Haircut & Style. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/hair-coloring` | Wix Bookings calendar for Hair Coloring. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/makeup-session` | Wix Bookings calendar for Makeup Session. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/dream-bridal-hair` | Wix Bookings calendar for Dream Bridal Hair. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/highlights-lowlights` | Wix Bookings calendar for Highlights & Lowlights. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/balayage` | Wix Bookings calendar for Balayage. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/keratin-treatment` | Wix Bookings calendar for Keratin Treatment. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/brazilian-blowout-1` | Wix Bookings calendar for Brazilian Blowout. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/perm-texture-waves` | Wix Bookings calendar for Perm & Texture Waves. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. |
| `/booking-calendar/kids-haircut` | Wix Bookings calendar for Kids’ Haircut. On the Wix Book Online page the photo, the title and the Book Now button of this service lead to it. Wix hides it from search engines (noindex). | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. Kids’ Haircut is no longer listed there since 13 November 2026 (contract decision 60). |
| `/service-page/haircut-style` | Wix Bookings detail page for Haircut & Style. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/hair-coloring` | Wix Bookings detail page for Hair Coloring. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/makeup-session` | Wix Bookings detail page for Makeup Session. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/dream-bridal-hair` | Wix Bookings detail page for Dream Bridal Hair. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/highlights-lowlights` | Wix Bookings detail page for Highlights & Lowlights. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/balayage` | Wix Bookings detail page for Balayage. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/keratin-treatment` | Wix Bookings detail page for Keratin Treatment. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/brazilian-blowout-1` | Wix Bookings detail page for Brazilian Blowout. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/perm-texture-waves` | Wix Bookings detail page for Perm & Texture Waves. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`, where the same service is listed. See notes 2 and 3. |
| `/service-page/kids-haircut` | Wix Bookings detail page for Kids’ Haircut. Listed in the Wix sitemap and open to search engines. | REDIRECTED | The 404 page sends the visitor on to `/book-online/`. Kids’ Haircut is no longer listed there since 13 November 2026 (contract decision 60). See notes 2 and 3. |
| `/blog` | Blog page of the Wix blog app with three posts. Not in the menu, not linked from any of the nine pages, only listed in the Wix sitemap. | GONE | None needed. The new site has no blog. The three posts are general filler articles, see the next rows. If the owner wants to keep one, its text can be copied from Wix while the Wix site is live. |
| `/post/expert-hair-styling-tips-for-every-occasion` | Blog post "Expert Hair Styling Tips for Every Occasion" | GONE | None needed. The text is a general hair article, dated Nov 26, 2025 like the sample shop products. It does not name Gerta, the salon, the address or the phone number, and none of the nine pages links to it. |
| `/post/top-trends-in-hair-styling-for-2023` | Blog post "Top Trends in Hair Styling for 2023" | GONE | None needed. The text is a general hair article, dated Nov 26, 2025 like the sample shop products. It does not name Gerta, the salon, the address or the phone number, and none of the nine pages links to it. |
| `/post/transform-your-look-with-professional-hair-services` | Blog post "Transform Your Look with Professional Hair Services" | GONE | None needed. The text is a general hair article, dated Nov 26, 2025 like the sample shop products. It does not name Gerta, the salon, the address or the phone number, and none of the nine pages links to it. |
| `/blog-feed.xml` | News feed (RSS) of the Wix blog. The head of the Wix home page, of the blog page and of the three posts names it. No visible link leads to it. | GONE | None needed. No blog means no feed, and the new pages do not name one. |
| `/profile/(member name)/profile` | Member profile page of the Wix members app for the administrator account of the Wix site. The author name on the blog page and on the posts links to it. | GONE | None needed. The new site has no member accounts, and the page says nothing about the salon. |
| `/profile/(member name)/profile?disableScrollToTop=true` | The same profile page, opened through its own Profile tab | GONE | None needed, same reason as the row above. |
| `/category/all-products` | Shop page "All Products" of the Wix store app: 12 sample products from the Wix template, priced from $20 to $690. Not in the menu, only listed in the Wix sitemap. | GONE | None needed. These are Wix sample products, not things the salon sells. The new site has no shop. |
| `/product-page/baseball-cap` | Wix sample shop product "Baseball Cap" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/ceramic-flower-vase` | Wix sample shop product "Ceramic Flower Vase" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/crew-t-shirt` | Wix sample shop product "Crew T-Shirt" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/essential-oil-diffuser` | Wix sample shop product "Essential Oil Diffuser" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/foaming-facial-cleanser` | Wix sample shop product "Foaming Facial Cleanser" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/hydrating-eye-serum` | Wix sample shop product "Hydrating Eye Serum - Pre Order" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/knitted-golf-sweater` | Wix sample shop product "Knitted Golf Sweater" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/minimalist-tote-bag` | Wix sample shop product "Minimalist Tote Bag" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/round-eyeglasses` | Wix sample shop product "Round Eyeglasses" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/solid-wood-chair` | Wix sample shop product "Solid Wood Chair" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/stainless-steel-water-bottle` | Wix sample shop product "Stainless Steel Water Bottle" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/product-page/textured-loop-earrings` | Wix sample shop product "Textured Loop Earrings" with the Wix placeholder description | GONE | None needed. Sample product from the Wix template, nothing to do with the salon. |
| `/pages-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists the nine pages and `/blog`. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/booking-services-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists the ten service addresses. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/store-products-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists the 12 sample shop products. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/store-categories-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists the shop category page. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/blog-posts-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists the three blog posts. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/blog-categories-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists `/blog`. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |
| `/member-profiles_p_first-chunk-sitemap.xml` | Partial Wix sitemap, named in the Wix `/sitemap.xml`. It lists nothing, the list is empty. | GONE | None needed. Search engines find sitemaps through `/robots.txt`, and the new one names only `/sitemap.xml`, which is now a single list of the nine pages. |

The member name in the two profile addresses is left out on purpose, because this file is public. It is the login name of the administrator account of the Wix site.

## Notes

1. Anything after a question mark in an address (for example `?lightbox=...`) is ignored by GitHub Pages. The page in front of the question mark decides what is shown.
2. What REDIRECTED can and cannot do. GitHub Pages cannot redirect on the server. For these 20 addresses the server first answers "not found" (status 404) and the 404 page then moves the visitor on. People arrive at Book Online within a moment. Search engines see the 404 and will drop these addresses from their results over time. For the ten booking calendar addresses that changes nothing, because Wix already hides them from search engines. The ten service addresses are open to search engines on Wix, so they may show up in Google today. Their place is taken by the Book Online page, which lists all ten services. Optional stronger fix: ten very small real pages, one at each old service address, that pass visitors and search engines on to `/book-online/` (an instant refresh plus a canonical link). Visitors do not need this. It only matters if those ten old Google results are worth keeping.
3. Text that exists only on the old service pages. Each of the ten Wix service pages has one more sentence under the heading Service Description, and a line that says where the service takes place (Forest Avenue for nine services, Customer's Place for Dream Bridal Hair). The new Book Online page shows the short description, the duration and the price of each service, exactly like the Wix Book Online page. If the owner wants the longer sentences on the new site, they have to be added to the Book Online content. The ten texts were saved during this check, outside this repository.
4. Any old address that is not in this list (for example a Wix cart or checkout page, which no page links to) shows the 404 page. After the domain has moved, Google Search Console (Page indexing report, reason "Not found (404)") shows which missing addresses Google still asks for. If a sitemap was ever submitted there by hand, submit `/sitemap.xml` again.
5. Other forms of the domain. Today Wix passes `http://hairbygerta.com`, `https://hairbygerta.com` and `http://www.hairbygerta.com` on to `https://www.hairbygerta.com` (status 301). That belongs to the domain setup, not to this list, and has to work again once the domain is connected to GitHub Pages. The domain is not connected in this step.

## How this was checked

- SAME: the nine `index.html` files and the two text files exist in the site folder. On a local copy of the site that is served the way GitHub Pages serves a project site, each address without a slash answers with a redirect to the address with a slash, and that address answers 200.
- REDIRECTED and GONE: every address was requested from the same local copy (expected: status 404 and the 404 page) and then opened in a browser (expected for REDIRECTED: the browser lands on `/book-online/`; expected for GONE: the browser stays, the 404 page finds its stylesheet, logo and script, and its button leads to the home page).
- Checked on the built site, 12 October 2026: all 58 addresses behave as the table says, 0 are broken, and no row had to be corrected. Every address was requested the way Wix writes it (no slash at the end) from the finished site folder, once behind `/hairbygerta/` (as on the test address) and once at the top of the host (as on www.hairbygerta.com).
  - SAME, 11 of 11: the nine pages answer 200 after the slash redirect, open complete in a browser and name the right address in their canonical tag. `robots.txt` and `sitemap.xml` answer 200.
  - REDIRECTED, 20 of 20: the server answers 404 with the 404 page, and a real browser (Chromium) ends on the Book Online page with its ten services. The same happens when the old address has a slash at the end or something after a question mark. The Back button then returns to the page the visitor came from, it does not bounce to Book Online again.
  - GONE, 27 of 27: the server answers 404 with the 404 page, the browser stays on the address and shows "Page not found" with stylesheet and logo, the page is marked noindex, and pressing its Back to Home button opens the home page.
- First check, earlier the same day, before the 404 page was rebuilt: the 11 SAME addresses passed, but the first version of the 404 page did not send the 20 REDIRECTED addresses on, and on the 18 GONE addresses that sit one folder deep or deeper (for example `/post/...` and `/product-page/...`) it lost its stylesheet and its Back to Home button pointed at a folder that does not exist. The rebuilt 404 page fixes both.
- Left as it is: on an address that sits one folder deep or deeper, the browser asks for the stylesheet, the logo and the script once in the wrong folder before the 404 page has told it where the site starts. Those three requests answer 404, then the files load from the right place. Visitors do not notice.
- Not checked: the real GitHub Pages server, because nothing is published in this step. The local server copies its three rules: `index.html` for a folder, a redirect that adds the missing slash, and `404.html` for everything that does not exist.
