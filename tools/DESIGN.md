# Design of hairbygerta.com

The look of the site since 12 November 2026 (build contract, decision 44). The owner's design brief of that day decides it. This file writes the brief down as tokens, a type scale, a grid and one sketch per page, so that anyone who changes `css/style.css` or a page module keeps the same look. The names that the HTML, the stylesheet and the script share are in `tools/CONTRACT.md`.

## Concept

Root to ends. The colors are a hair color chart taken from Gerta's own photos (g12 and g13), from the darkest root to the lightest end. Photos are shown tall, 9 to 16, the way she shoots them. Every page looks complete with the photos that exist today, and a photo that the owner adds later appears by itself.

The job of every page is trust in five seconds, then a call or a text to 347-671-5095. Visitors are local women on phones who come from Google or Instagram.

## Color

| Token | Hex | Use |
|---|---|---|
| Paper | `#fefefd` | page background |
| Blonde | `#efe6d8` | quiet surfaces (the Find me band, the call block of the Services page, the empty map, a photo while it loads) |
| Honey | `#c99b5f` | decoration (current page mark, the shade strip), and text on Espresso. Never text on a light color |
| Caramel | `#96663a` | small accents. As text only on Paper (4.9 to 1) |
| Chestnut | `#5a3a22` | secondary text, link hover, button hover (10.1 to 1 on Paper) |
| Espresso | `#1d1509` | text, buttons, footer (17.9 to 1 on Paper) |

Contrast was measured for every pair that carries text. Body text is Espresso on Paper or Blonde, at least 14.6 to 1. Footer text is Paper or Blonde on Espresso, Honey for the quieter footer lines (7.2 to 1). Caramel on Blonde (4.0 to 1) and Honey on any light color are never used for text.

## Type

Two fonts, both files of the site (folder `fonts`). Nothing else is ever loaded.

- Bodoni Moda Italic, weight 400, for the business name and every heading. Used big, with tight line height.
- Figtree, weights 400 to 600, for everything else.

Sentence case everywhere. No all caps, no small label above a heading, no single word set apart inside a headline.

| Role | Desktop | Phone | Line height |
|---|---|---|---|
| Business name, home page (h1) | 104 px, up to 136 px on wide screens | 50 px | 0.92 |
| Page title (h1 of the other pages) | 72 px | 48 px | 1.0 |
| Section heading (h2) | 56 px | 38 px | 1.05 |
| Group heading (h3) | 28 px | 26 px | 1.15 |
| Lead text | 21 px | 19 px | 1.5 |
| Body text | 18 px | 17 px | 1.6 |
| Buttons, navigation, service names | 16 to 17 px, weight 500 or 600 | 17 px | 1.3 |
| Small print (copyright, notes) | 15 px | 15 px | 1.5 |

Text blocks are at most 30 em wide (about 68 characters of Figtree at 18 px), the text of Meet Gerta at most 27 em (about 60 characters). The sizes follow the classic scale of The Elements of Typographic Style (15, 18, 21, 28, 38, 48, 56, 72, 104).

## Grid and spacing

- 12 columns, 24 px apart, at most 1200 px wide, centred in the window with at least 40 px on each side.
- From 1100 px down the columns are 20 px apart and the side margin is 32 px.
- From 760 px down there is one column and the side margin is 20 px.
- Spacing steps are 4, 8, 12, 16, 24, 32, 48, 64, 96 and 128 px. Sections are 96 px apart on desktop and 64 px on phones.
- Text is left aligned on every page. Nothing is centred.
- Square corners everywhere. No rounded card, no shadow, no gradient.

## The parts every page shares

- **Header.** Sticky, 72 px tall on desktop and 64 px on phones, Paper with one Blonde line under it. Logo on the left (48 px, 40 px on phones), then the navigation, then the Call button on the right. On phones the navigation folds behind the menu button and the Call button of the header gives way to the call bar.
- **Logo.** A small JPG with a white box around it. Shown at 72 px or smaller, only on Paper or Blonde, with `mix-blend-mode: multiply` so the white box does not show. Never on Espresso.
- **Buttons.** A button says what it does. The Call button is Espresso with Paper text, 44 px tall or more, Chestnut under the mouse. "Text Gerta" is a text link (an sms link to the same number) with a 44 px tall tap area.
- **Shade strip.** The signature element. Five flat bands side by side, Espresso, Chestnut, Caramel, Honey, Blonde, 10 px tall, as wide as the window. Once per page, under the hero or the page title, and nowhere else. It replaces every dotted rule.
- **Footer.** Espresso, left aligned, the same content as before. Paper text, Honey for the quieter lines, links underlined.
- **Call bar.** Phones only (760 px and below). Espresso, fixed to the bottom of the screen, "Call 347-671-5095".
- **Focus.** A 2 px Espresso outline 3 px outside every link, button and field. Honey on Espresso.
- **Motion.** One only. On the home page the hero photos are revealed from top to bottom, root to ends, once when the page opens, in 600 ms. Skipped when the visitor prefers reduced motion. Nothing else moves.

## Photos

A photo sits in a tall frame, 9 to 16, with square corners, cropped to fill it. A name in `PLACEHOLDERS` (tools/build_pages.py) is never shown. Each page module leaves such a photo out and the layout closes up around the photos that are left. Today the real photos are g12 and g13.

## Pages

Sketches at 1280 px (desktop) and 390 px (phone). `####` is the shade strip, `::::` a Blonde band.

### Home

```
1280                                                                         72 px header
+--------------------------------------------------------------------------------------+
| (logo)  Home  Gallery  Services  About  Contact                  [ Call 347-671-5095 ] |
+--------------------------------------------------------------------------------------+
|  Hair & Makeup                                    +------------+                      |
|  by Gerta                                         |            |   +----------+       |
|                                                   |    g13     |   |          |       |
|  I'm Gerta Lila, a hair stylist and makeup        |    9:16    |   |   g12    |       |
|  artist in Staten Island, NY. I create fresh      |            |   |   9:16   |       |
|  cuts, color, extensions and soft, flattering     |            |   |          |       |
|  makeup that highlight your natural beauty ...    |            |   |          |       |
|                                                   |            |   |          |       |
|  [ Call 347-671-5095 ]   Text Gerta               |            |   |          |       |
|  Tuesday to Saturday, 9 AM to 5 PM                +------------+   +----------+       |
|######################################################################################|
|  Services            Cut and style               Smoothing and texture               |
|                      Haircut & Style             Keratin Treatment                   |
|                      Kids' Haircut               Brazilian Blowout                   |
|                                                  Perm & Texture Waves                |
|                      Color                                                           |
|                      Hair Coloring               Occasions                           |
|                      Highlights & Lowlights      Dream Bridal Hair                   |
|                      Balayage                    Makeup Session                      |
|                      More about each service                                         |
|                                                                                      |
|  Meet Gerta          I offer makeup that looks natural, photographs beautifully,     |
|                      and lasts all day. ...  (about 60 characters a line)            |
|::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::|
|  Find me             Le Vigne Hair Salon             Tuesday to Saturday,            |
|                      644 Forest Ave, Staten Island   9 AM to 5 PM                    |
|                      Open in Google Maps                                             |
|::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::|
|  Espresso footer, left aligned                                                       |
+--------------------------------------------------------------------------------------+

390                                   64 px header
+------------------------------------+
| (logo)                         [=] |
+------------------------------------+
| Hair & Makeup                      |   50 px, two lines
| by Gerta                           |
| I'm Gerta Lila, a hair stylist ... |
| [       Call 347-671-5095        ] |   full width, on the first screen
| Text Gerta                         |
| Tuesday to Saturday, 9 AM to 5 PM  |
| +--------------+ +--------------+  |
| |     g13      | |     g12      |  |   side by side
| +--------------+ +--------------+  |
|####################################|
| Services, the four groups          |
| Meet Gerta                         |
|:::: Find me :::::::::::::::::::::::|
| footer                             |
| [      Call 347-671-5095         ] |   call bar, fixed
+------------------------------------+
```

The photo row and the two Meet Gerta photos of the old page are placeholders today, so they are left out. When the owner adds them, the row shows under Services as tall frames, four across on desktop and two on phones, and the Meet Gerta photos show under her text.

### Services (`/book-online/`)

```
1280
|  Our services                                                                     |
|  Prices are given by phone. Call or text 347-671-5095.                            |
|##################################################################################|
|  Cut and style                                         +-----------------------+ |
|  Haircut & Style ............................ 45 min   | [ Call 347-671-5095 ] | |
|  Transform your hair with precision cutting ...        | Text Gerta            | |
|  Kids' Haircut ............................... 45 min   | Tuesday to Saturday,  | |
|  Friendly, patient cuts just for kids.                  | 9 AM to 5 PM          | |
|  Color                                                  +-----------------------+ |
|  Smoothing and texture                                    stays in view (Blonde)  |
|  Occasions                                                                        |

390
| Our services                       |
| Prices are given by phone. ...     |
|####################################|
| Cut and style                      |
| Haircut & Style            45 min  |
| Transform your hair with ...       |
| ...                                |
| [ call bar ]                       |
```

A typeset menu with no photos and no cards. Each row shows the name, its one line and its time. The dots above only mark the row, the page has no dot leaders.

### Gallery

```
1280
|  Gallery                                                       |
|################################################################|
|  +----------+  +----------+   More of my work is on            |
|  |   g12    |  |   g13    |   Instagram.                       |
|  |   9:16   |  |   9:16   |                                    |
|  +----------+  +----------+                                    |

390
| Gallery                            |
|####################################|
| +-------------+ +-------------+    |
| |    g12      | |    g13      |    |
| +-------------+ +-------------+    |
| More of my work is on Instagram.   |
```

Three columns on desktop, two on phones, tall frames, the photo viewer opens on a tap. With fewer than six photos one line points to her Instagram.

### About

```
1280
|  About Gerta                                                   |
|################################################################|
|  I offer hair and makeup services designed to make you        |
|  look polished and still like yourself. ...  (lead, 21 px)    |
|                                                                |
|  Every visit starts with a short consultation ...             |
|  Before you leave, I show you how to care for your hair ...   |
|  [ Call 347-671-5095 ]   Text Gerta                            |

390   the same, one column
```

Led by text. Her one long paragraph is split into three short ones, her words unchanged. A photo shows beside the text only when a real one exists.

### Contact

```
1280
|  Contact                                                       |
|  Have a question about a service or price? Call ...           |
|################################################################|
|  Address                         First name      Last name     |
|  Le Vigne Hair Salon             Email                         |
|  Phone                           Message                       |
|  Email                           [ Send ]                      |
|  Social media                                                  |
|  Hours                                                         |
|  +----------------------------------------------------------+ |
|  |                     map (Blonde while empty)              | |
|  +----------------------------------------------------------+ |
|  Open in Google Maps                                           |

390   info list, then the form, then the map
```

### Policy pages and the 404 page

```
1280
|  Privacy Policy                                                |
|################################################################|
|  Body text, at most 30 em wide, headings in Bodoni Italic.    |

390   the same, one column
```

The wording stays word for word. Only the styling is new.

## Checked against the generic looks

Before any code was written, the plan was held against the looks that show up whatever the subject (the list in the Frontend Design skill). What matched, and what changed.

- A warm cream page with a high contrast serif and a terracotta accent. The serif is the brief's own choice, and it stays. The page is Paper, near white, not cream. Blonde is kept to one quiet band per page, never the whole page. There is no single accent color. The warm tones come as the full shade strip, the colors of her photos.
- A broadsheet with hairline rules everywhere. The square corners are the brief's choice. The first plan had a thin line between the services. Those lines are gone, the rows are told apart by space. The one line left is under the sticky header, where it separates the header from the page that scrolls under it.
- The kit of identical rounded cards with shadows. The Services page had ten cards. It is now a typeset menu. The call block of the Services page is one flat Blonde surface, not a card.
- Template chrome. The first plan had a small label above each heading and numbers in front of the home sections (01, 02, 03). Both are gone, because the sections are not a sequence. No middle dots between facts, no arrows after link text, no monospace labels.
- The usual salon page (cream, a slogan in a serif, three rounded service cards with icons, a carousel of reviews). Nothing of it is here. There are no reviews, because the site invents none.

What makes the site its own is in three places. The shade strip, once per page. The photos, tall and uncropped in shape, revealed from root to ends. The business name set very big in Bodoni Italic. Everything around them stays quiet.
