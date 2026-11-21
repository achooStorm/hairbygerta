/*
 * BOOK NOW BUTTONS
 *
 * Every Book Now button calls 347-671-5095.
 * The salon uses its own booking, so this site has no online booking link.
 * That is why BOOKING_URL, on the line right under this note, stays empty.
 *
 * If an online booking link is ever added, it goes between the two quote
 * marks on the line under this note. To add one, follow these steps.
 *   1. Copy the full link to the booking page. It starts with https://
 *   2. Paste it between the two quote marks on the line under this note.
 *   3. Change nothing else on that line. Both quote marks stay, and so does
 *      the ; at the very end.
 *
 * Once a link is there, every Book Now button opens the booking page in a
 * new tab instead.
 * To go back to phone calls, delete the link and leave the two quote marks
 * with nothing between them.
 */
var BOOKING_URL = "";

/*
 * Nothing below this note has to be changed to add the booking link.
 *
 * Site script for Hair & Makeup by Gerta. Every page loads this one file
 * with "defer". It has nine parts:
 *
 *   1. Book Now buttons       every element marked data-book
 *   2. Phone menu             .menu-btn and #main-nav
 *   3. Gallery photo viewer   the links inside .gallery
 *   4. Contact form           #contact-form, #email-error and .form-note
 *   5. Copyright year         every element marked data-year
 *   6. Map                    the iframe with data-src inside .map
 *   7. Short header           the class "compact" on <html>, and the pressed
 *                             look of links and buttons on an iPhone
 *   8. Text and Call box      .reach on the home page and on the Services
 *                             page: the class "reach-on-screen" on <body>
 *   9. Label on the photos    .row-cue on the home page: the class "on" for
 *                             a few seconds, on touch screens
 *
 * Each part looks for its own elements and does nothing on a page that does
 * not have them. A part that fails does not stop the other parts.
 *
 * The pages also work without this script: the Book Now buttons are phone
 * links, the menu is a plain list of links, each gallery photo opens on its
 * own, the year is the one the page was built with, the header keeps its
 * full height, and the Contact page hides its form (the sentence above it
 * gives the phone number and the email address as links) and offers the map
 * as a link to Google Maps. The bar at the bottom of a phone screen then
 * stays on the screen beside the Text and Call box of the home page and
 * of the Services page, and the label on the home photos never shows.
 */
(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // 1. Book Now buttons
  // ---------------------------------------------------------------------------

  /*
   * Book Now buttons (every element marked data-book).
   * No booking link at the top of this file (empty or only spaces): each
   * button calls 347-671-5095.
   * A booking link at the top of this file: each button opens that link in a
   * new tab.
   * Without this script the buttons are plain phone links and still work.
   */
  function initBooking(bookingUrl) {
    var phoneHref = "tel:+1-347-671-5095";
    var buttons = document.querySelectorAll("[data-book]");
    var link = typeof bookingUrl === "string" ? bookingUrl.trim() : "";
    var i;

    // A link pasted without "https://" in front would otherwise be read as a
    // page of this site and lead to "page not found".
    if (link && !/^https?:\/\//i.test(link)) {
      link = "https://" + link.replace(/^\/+/, "");
    }

    for (i = 0; i < buttons.length; i++) {
      if (link) {
        buttons[i].setAttribute("href", link);
        buttons[i].setAttribute("target", "_blank");
        buttons[i].setAttribute("rel", "noopener");
      } else {
        buttons[i].setAttribute("href", phoneHref);
        buttons[i].removeAttribute("target");
      }
    }
  }

  // ---------------------------------------------------------------------------
  // 2. Phone menu
  // ---------------------------------------------------------------------------

  /*
   * Phone menu.
   * The button .menu-btn opens and closes the navigation #main-nav.
   * Open means: class "open" on the nav, aria-expanded="true" on the button and
   * class "menu-open" on body (the stylesheet uses that one to stop page scroll).
   * The stylesheet shows the button only on screens up to 760 px wide and only
   * when the script runs, so on wide screens this function changes nothing.
   */
  function initMenu() {
    var btn = document.querySelector(".menu-btn");
    var nav = document.getElementById("main-nav");
    if (!btn || !nav) {
      return;
    }

    var body = document.body;
    // Same breakpoint as the stylesheet: the phone layout ends above 760 px.
    var phone = window.matchMedia ? window.matchMedia("(max-width: 760px)") : null;

    function isOpen() {
      return nav.classList.contains("open");
    }

    function setOpen(open) {
      if (open) {
        nav.classList.add("open");
        body.classList.add("menu-open");
      } else {
        nav.classList.remove("open");
        body.classList.remove("menu-open");
      }
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    }

    // Closes only an open menu, so a closed menu (every wide screen) is never touched.
    function closeMenu() {
      if (isOpen()) {
        setOpen(false);
      }
    }

    // False where the stylesheet hides the button (wide screens).
    function buttonShown() {
      return btn.getClientRects().length > 0;
    }

    // The button toggles the menu. Enter and Space arrive here as clicks too.
    btn.addEventListener("click", function () {
      if (isOpen()) {
        setOpen(false);
      } else if (buttonShown()) {
        setOpen(true);
      }
    });

    // A click on any link inside the nav closes the menu. The link still works.
    nav.addEventListener("click", function (event) {
      var target = event.target;
      var link = target && target.closest ? target.closest("a") : null;
      if (link && nav.contains(link)) {
        closeMenu();
      }
    });

    // Escape closes the menu and puts focus back on the button.
    document.addEventListener("keydown", function (event) {
      if (!isOpen()) {
        return;
      }
      if (event.key === "Escape" || event.key === "Esc" || event.keyCode === 27) {
        closeMenu();
        btn.focus();
      }
    });

    // When keyboard focus moves out of the menu (Tab past the last link, or
    // Shift+Tab back from the button) the menu closes, so focus never ends up
    // on something hidden behind the open menu. A tap on an empty spot has no
    // new focus target and leaves the menu open.
    function onFocusOut(event) {
      var next = event.relatedTarget;
      if (next && next !== btn && !nav.contains(next)) {
        closeMenu();
      }
    }
    btn.addEventListener("focusout", onFocusOut);
    nav.addEventListener("focusout", onFocusOut);

    // The window became wider than 760 px (a turned phone, a resized window):
    // the button is gone there, so an open menu closes.
    function onWidthChange() {
      if (!phone.matches) {
        closeMenu();
      }
    }
    if (phone) {
      if (phone.addEventListener) {
        phone.addEventListener("change", onWidthChange);
      } else if (phone.addListener) {
        phone.addListener(onWidthChange);
      }
    }
  }

  // ---------------------------------------------------------------------------
  // 3. Gallery photo viewer
  // ---------------------------------------------------------------------------

  /*
   * Gallery photo viewer.
   * Each link in .gallery opens its photo in a full-screen viewer with next and previous
   * buttons, arrow keys, swipe and Escape. Without this script every link is still a plain
   * link that opens its photo, so nothing is lost when the script does not run.
   *
   * On a touch screen the photo follows the finger. A swipe to the left or right goes to
   * the next or previous photo, and the old photo glides out while the new one glides in.
   * A swipe down closes the viewer. A drag that ends too early lets the photo glide back.
   *
   * What the viewer shows, in this order:
   *   1. at once, the small copy of the photo that the gallery has loaded already
   *      (img.lb-ph, the stand-in), so the viewer never opens onto a dark screen;
   *   2. the full photo (img.lb-img), which fades in over the stand-in when it has arrived.
   *      Its src is the JPG of the gallery link. A link with data-webp also offers the
   *      WebP copy of the same photo, a much smaller file, and a browser that reads WebP
   *      takes that one (the picture element with its source does the choosing).
   */
  function initLightbox() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".gallery a[href]"));
    if (!links.length || document.querySelector(".lightbox")) {
      return;
    }

    var total = links.length;
    var index = 0;          // photo on show, counted from 0
    var direction = 1;      // 1 after "next", -1 after "previous" (used to preload the likely next photo)
    var opener = null;      // the link that opened the viewer, gets the focus back on close
    var isOpen = false;
    var opening = false;    // true while the click or key press that opened the viewer may not be over yet
    var pressedOn = null;   // where the mouse button went down, see the click handler of the viewer
    var drag = null;        // a one-finger touch on the viewer: where it began and which way it goes
    var ghost = null;       // the old photo while it glides out of the viewer
    var ghostTimer = 0;
    var shape = 0;          // width / height of the stand-in picture, 0 while there is none
    var preloaded = null;

    function makeButton(className, label, glyph) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = className;
      button.setAttribute("aria-label", label);
      button.textContent = glyph;
      return button;
    }

    // The viewer is built once and reused. It carries "hidden" whenever it is closed,
    // so neither the Tab key nor a screen reader can reach it.
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Photo viewer");
    // tabindex -1: the Tab key never stops on the viewer itself, but a press on the photo
    // leaves the focus on the viewer instead of dropping it onto the page behind.
    box.setAttribute("tabindex", "-1");
    box.hidden = true;

    var closeBtn = makeButton("lb-close", "Close", "\u00d7");
    var prevBtn = makeButton("lb-prev", "Previous photo", "\u2039");
    // The stage is the part that moves with the finger. It holds the stand-in and, in a
    // picture element, the photo. The source for the WebP copy is put into the picture
    // only for a photo that has one.
    var stage = document.createElement("div");
    stage.className = "lb-stage";
    var standIn = document.createElement("img");
    standIn.className = "lb-ph";
    standIn.alt = "";
    standIn.setAttribute("aria-hidden", "true");
    standIn.hidden = true;
    var picture = document.createElement("picture");
    var webp = document.createElement("source");
    webp.type = "image/webp";
    var img = document.createElement("img");
    img.className = "lb-img";
    img.alt = "";
    picture.appendChild(img);
    stage.appendChild(standIn);
    stage.appendChild(picture);
    var nextBtn = makeButton("lb-next", "Next photo", "\u203a");
    var count = document.createElement("p");
    count.className = "lb-count";
    count.setAttribute("aria-live", "polite");

    box.appendChild(closeBtn);
    box.appendChild(prevBtn);
    box.appendChild(stage);
    box.appendChild(nextBtn);
    box.appendChild(count);
    document.body.appendChild(box);

    var stops = [closeBtn, prevBtn, nextBtn];

    function show(i) {
      index = ((i % total) + total) % total;
      var link = links[index];
      var thumb = link.querySelector("img");
      var light = link.getAttribute("data-webp");

      // The photo of before is gone at once. The new one is drawn when its file is in.
      img.classList.remove("lb-loaded");

      // The stand-in: the file the gallery shows for this photo, if the browser has it.
      // shape is its width divided by its height, see onStandIn.
      var small = thumb && thumb.complete && thumb.naturalWidth > 0 ? (thumb.currentSrc || thumb.src) : "";
      if (small) {
        if (standIn.getAttribute("src") !== small) {
          standIn.src = small;
        }
        standIn.hidden = false;
        shape = thumb.naturalWidth / thumb.naturalHeight;
      } else {
        standIn.hidden = true;
        standIn.removeAttribute("src");
        shape = 0;
      }

      img.alt = thumb ? thumb.alt : "";
      if (light) {
        webp.setAttribute("srcset", light);
        if (webp.parentNode !== picture) {
          picture.insertBefore(webp, img);
        }
      } else if (webp.parentNode === picture) {
        picture.removeChild(webp);
      }
      img.src = link.getAttribute("href");
      count.textContent = (index + 1) + " / " + total;
    }

    function step(by) {
      direction = by;
      show(index + by);
    }

    // ---- moving the stage

    // Puts the stage x px to the right and y px down of its place (0, 0 = in its place).
    function place(x, y) {
      stage.style.transform = x || y ? "translate3d(" + x + "px," + y + "px,0)" : "";
    }

    // Back in its place and the dark layer solid again. glide = true: it glides there.
    function rest(glide) {
      if (glide) {
        stage.classList.add("lb-move");
      } else {
        stage.classList.remove("lb-move");
      }
      place(0, 0);
      box.style.removeProperty("--lb-dim");
    }

    function clearGhost() {
      window.clearTimeout(ghostTimer);
      if (ghost && ghost.parentNode) {
        ghost.parentNode.removeChild(ghost);
      }
      ghost = null;
    }

    // A copy of the picture that is on show right now (the photo, or its stand-in while
    // the photo is still on its way), standing where the stage stands. Nothing to copy: null.
    function makeGhost(x) {
      var loaded = img.classList.contains("lb-loaded");
      var standing = !standIn.hidden && standIn.offsetWidth > 0;
      var src = loaded ? (img.currentSrc || img.src) : (standing ? standIn.src : "");
      clearGhost();
      if (!src) {
        return null;
      }
      var copy = document.createElement("img");
      copy.className = loaded ? "lb-ghost-img" : "lb-ghost-fit";
      copy.alt = "";
      copy.src = src;
      ghost = document.createElement("div");
      ghost.className = "lb-ghost";
      ghost.setAttribute("aria-hidden", "true");
      ghost.style.transform = x ? "translate3d(" + x + "px,0,0)" : "";
      ghost.appendChild(copy);
      box.insertBefore(ghost, stage);
      return ghost;
    }

    // On to the next (by = 1) or the previous (by = -1) photo with a glide: the old
    // photo leaves on one side while the new one comes in from the other. from is how
    // far the finger has moved the photo already (0 for a button or a key).
    // The photo, the counter and the alt text change at once. Only the picture glides.
    function glideTo(by, from) {
      var width = box.clientWidth || window.innerWidth;
      var old = makeGhost(from);
      step(by);
      stage.classList.remove("lb-move");
      place(from + by * width, 0);
      box.style.removeProperty("--lb-dim");
      void stage.offsetWidth;   // the browser notes where both start before they glide
      stage.classList.add("lb-move");
      place(0, 0);
      if (old) {
        old.classList.add("lb-move");
        old.style.transform = "translate3d(" + (-by * width) + "px,0,0)";
        ghostTimer = window.setTimeout(clearGhost, 400);
      }
    }

    // An empty spot of the stage is the dark layer too.
    function isBackdrop(node) {
      return node === box || node === count || node === stage;
    }

    // The stand-in takes no clicks itself and fills more room than its picture. While
    // it stands in for the photo, this says whether a click fell on the picture.
    function onStandIn(e) {
      if (standIn.hidden || !shape || img.classList.contains("lb-loaded")) {
        return false;
      }
      var room = standIn.getBoundingClientRect();
      if (!room.width || !room.height) {
        return false;   // the stylesheet does not use the stand-in on this screen
      }
      // The picture is as large as fits into the room without changing its shape.
      var width = Math.min(room.width, room.height * shape);
      var height = width / shape;
      var left = room.left + (room.width - width) / 2;
      var top = room.top + (room.height - height) / 2;
      return e.clientX >= left && e.clientX <= left + width && e.clientY >= top && e.clientY <= top + height;
    }

    // The press that opened the viewer can still be going on when the viewer is already
    // there: the second click of a double-click on a thumbnail, or an Enter key that is
    // held down and repeats. Such a leftover lands on the viewer (dark layer, arrow, Close
    // button) and would close it again at once or jump to another photo, so it is ignored.
    // The first new click or key press ends this.
    function leftoverClick(e) {
      if (opening && e.detail > 1) {
        return true;
      }
      opening = false;
      return false;
    }

    function onKey(e) {
      if (e.altKey || e.ctrlKey || e.metaKey) {
        return;
      }
      var key = e.key;
      if (opening && e.repeat && key === "Enter") {
        e.preventDefault();
        return;
      }
      opening = false;
      if (key === "Escape" || key === "Esc") {
        e.preventDefault();
        closeViewer();
      } else if (key === "ArrowRight" || key === "Right") {
        e.preventDefault();
        glideTo(1, 0);
      } else if (key === "ArrowLeft" || key === "Left") {
        e.preventDefault();
        glideTo(-1, 0);
      } else if (key === "Tab") {
        // Tab and Shift+Tab go round the three buttons and never leave the viewer.
        var at = stops.indexOf(document.activeElement);
        if (at === -1) {
          at = e.shiftKey ? 0 : stops.length - 1;
        }
        at = (at + (e.shiftKey ? -1 : 1) + stops.length) % stops.length;
        e.preventDefault();
        stops[at].focus();
      }
    }

    // Safety net for focus that arrives from outside by another route than the Tab key.
    function onFocusIn(e) {
      if (!box.contains(e.target)) {
        closeBtn.focus();
      }
    }

    function openViewer(i, link) {
      opener = link;
      direction = 1;
      clearGhost();
      rest(false);
      show(i);
      if (isOpen) {
        return;
      }
      isOpen = true;
      opening = true;
      box.hidden = false;
      box.classList.add("open");
      document.body.classList.add("lightbox-open");
      document.addEventListener("keydown", onKey);
      document.addEventListener("focusin", onFocusIn);
      closeBtn.focus();
    }

    function closeViewer() {
      if (!isOpen) {
        return;
      }
      isOpen = false;
      opening = false;
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("focusin", onFocusIn);
      box.classList.remove("open");
      box.hidden = true;
      document.body.classList.remove("lightbox-open");
      // The next opening must not flash the old photo, and a closed viewer loads nothing.
      img.classList.remove("lb-loaded");
      if (webp.parentNode === picture) {
        picture.removeChild(webp);
      }
      img.removeAttribute("src");
      standIn.hidden = true;
      standIn.removeAttribute("src");
      drag = null;
      clearGhost();
      rest(false);
      var back = opener;
      opener = null;
      if (back) {
        back.focus();
      }
    }

    links.forEach(function (link, i) {
      link.addEventListener("click", function (e) {
        // Ctrl, Cmd, Shift, Alt and the middle button keep what the browser does with a link.
        if (e.defaultPrevented || e.button || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) {
          return;
        }
        e.preventDefault();
        openViewer(i, link);
      });
    });

    closeBtn.addEventListener("click", function (e) {
      if (!leftoverClick(e)) {
        closeViewer();
      }
    });
    prevBtn.addEventListener("click", function (e) {
      if (!leftoverClick(e)) {
        glideTo(-1, 0);
      }
    });
    nextBtn.addEventListener("click", function (e) {
      if (!leftoverClick(e)) {
        glideTo(1, 0);
      }
    });

    // A click on the dark backdrop closes the viewer, a click on the photo or on a button does not.
    // A press that starts on the photo or a button and is released over the backdrop does not count.
    box.addEventListener("mousedown", function (e) {
      pressedOn = e.target;
    });
    box.addEventListener("click", function (e) {
      var from = pressedOn;
      pressedOn = null;
      if (leftoverClick(e)) {
        return;
      }
      if (isBackdrop(e.target) && (from === null || isBackdrop(from)) && !onStandIn(e)) {
        closeViewer();
      }
    });

    // The photo has arrived: it fades in over its stand-in. Then fetch the one the
    // visitor is most likely to ask for next, as WebP if this browser took the WebP
    // copy of the photo on show, so that the very file it will show is the one fetched.
    img.addEventListener("load", function () {
      // Not complete: this is late news of the photo before, and the one on show is
      // still on its way. Its own news follows.
      if (!img.complete) {
        return;
      }
      img.classList.add("lb-loaded");
      var connection = navigator.connection;
      if (!isOpen || total < 2 || (connection && connection.saveData)) {
        return;
      }
      var next = links[(index + direction + total) % total];
      var readsWebp = /\.webp(\?|#|$)/i.test(img.currentSrc || "");
      preloaded = new Image();
      preloaded.src = (readsWebp && next.getAttribute("data-webp")) || next.href;
    });

    // A file did not arrive. If it was the WebP copy, the source is taken out and the
    // browser fetches the JPG of the link instead. If it was the JPG, there is nothing
    // more to wait for: the img is drawn, and the browser shows its alt text.
    img.addEventListener("error", function () {
      if (webp.parentNode === picture) {
        picture.removeChild(webp);
      } else {
        img.classList.add("lb-loaded");
      }
    });

    // ---- touch: the photo follows one finger
    //
    // Sideways: left = next photo, right = previous photo. Down: close the viewer.
    // One finger only, and not while the visitor has pinch-zoomed into the photo: then
    // a finger moves the enlarged page, which is the browser's business.
    // A second finger fires touchstart again, which drops the drag, so a pinch never counts.
    // The swipe itself is judged from where the finger went down and where it came up:
    // at least 40 px sideways and mostly sideways, or at least 90 px down and mostly down.
    var passive = { passive: true };

    function zoomedIn() {
      var view = window.visualViewport;
      return !!view && view.scale > 1.05;
    }

    box.addEventListener("touchstart", function (e) {
      if (e.touches.length === 1 && !zoomedIn()) {
        drag = { x: e.touches[0].clientX, y: e.touches[0].clientY, way: "" };
      } else {
        if (drag && drag.way) {
          rest(true);
        }
        drag = null;
      }
    }, passive);

    // Not passive: once the finger is dragging the photo, the browser must not also
    // scroll, bounce or pull the page under it.
    box.addEventListener("touchmove", function (e) {
      if (!drag || e.touches.length !== 1) {
        return;
      }
      var dx = e.touches[0].clientX - drag.x;
      var dy = e.touches[0].clientY - drag.y;
      if (!drag.way) {
        if (zoomedIn() || (Math.abs(dx) < 8 && Math.abs(dy) < 8)) {
          return;   // not yet clear where the finger is going
        }
        drag.way = Math.abs(dx) >= Math.abs(dy) ? "x" : "y";
        stage.classList.remove("lb-move");
        clearGhost();
      }
      if (e.cancelable) {
        e.preventDefault();
      }
      if (drag.way === "x") {
        place(dx, 0);
      } else {
        // Only downwards. The further down, the more of the page shows through.
        var down = Math.max(0, dy);
        place(0, down);
        box.style.setProperty("--lb-dim", String(Math.max(0.35, 1 - down / 450)));
      }
    }, { passive: false });

    box.addEventListener("touchcancel", function () {
      drag = null;
      rest(true);
    }, passive);

    box.addEventListener("touchend", function (e) {
      var start = drag;
      var end = e.changedTouches[0];
      drag = null;
      if (!start || !end || zoomedIn()) {
        if (start && start.way) {
          rest(true);
        }
        return;
      }
      var dx = end.clientX - start.x;
      var dy = end.clientY - start.y;
      if (Math.abs(dx) >= 40 && Math.abs(dx) > 1.5 * Math.abs(dy)) {
        glideTo(dx < 0 ? 1 : -1, start.way === "x" ? dx : 0);
      } else if (dy >= 90 && dy > 1.5 * Math.abs(dx)) {
        closeViewer();
      } else if (start.way) {
        rest(true);
      }
    }, passive);
  }

  // ---------------------------------------------------------------------------
  // 4. Contact form
  // ---------------------------------------------------------------------------

  /*
   * Contact form (#contact-form on the Contact page).
   * Pressing Send opens the visitor's own email app with a new message to
   * the address in the form's data-mailto (info@hairbygerta.com): subject,
   * text, name and email address already filled in. The visitor then presses
   * send in the email app.
   * Nothing is stored and nothing is sent to any server.
   * The line shown under the button afterwards is the form's data-sent text.
   * The browser checks the Email field (required, type email). When it finds
   * a problem, this script shows the matching message from #email-error
   * (data-missing or data-invalid) under the field, in words, instead of the
   * browser's own bubble, marks the field and puts the cursor into it.
   * Without this script the stylesheet hides the form.
   */
  function initContactForm() {
    var form = document.getElementById("contact-form");
    if (!form) {
      return;
    }

    var salonEmail = (form.getAttribute("data-mailto") || "").replace(/^mailto:/i, "").trim() ||
      "info@hairbygerta.com";
    var emailField = form.elements.email;
    var errorLine = document.getElementById("email-error");
    // Used only when the form has no data-sent text.
    var sentFallback = "Thanks! Your email app should open so you can send the message.";

    // What the visitor typed into one field, without spaces around it.
    // An empty string when the form has no such field.
    function read(name) {
      var field = form.elements[name];
      return field && typeof field.value === "string" ? field.value.trim() : "";
    }

    // encodeURIComponent stops with an error on half of a broken emoji.
    // In that rare case the broken halves are dropped and the rest is kept.
    function encode(text) {
      try {
        return encodeURIComponent(text);
      } catch (error) {
        return encodeURIComponent(text.replace(/[\uD800-\uDBFF][\uDC00-\uDFFF]|[\uD800-\uDFFF]/g, function (found) {
          return found.length === 2 ? found : "";
        }));
      }
    }

    // The status line under the Send button.
    function setNote(text) {
      var note = form.querySelector(".form-note") || document.querySelector(".form-note");
      if (note && note.textContent !== text) {
        note.textContent = text;
      }
    }

    // The line under the status line, for a phone without an email app
    // (.form-alt): it holds a link that opens the text message app. Shown
    // after a send, with the visitor's message written into the link, so the
    // text message app opens with the message already in it. The link in
    // the page names the number only ("sms:+1..."). The message is added as
    // "?&body=...", the one form both iPhone and Android understand.
    var altLine = form.querySelector(".form-alt");

    function showAlt(text) {
      var link = altLine ? altLine.querySelector("a.sms-link") : null;
      if (!altLine) {
        return;
      }
      if (link) {
        var number = (link.getAttribute("href") || "").split("?")[0];
        link.setAttribute("href", number + "?&body=" + encode(text));
      }
      altLine.hidden = false;
    }

    // The status line only ever speaks about the send that just happened.
    // It is emptied as soon as the visitor types again, and when the browser
    // stops a send because the email address is missing or mistyped (the
    // browser then shows its own message and never reaches the code below).
    // "invalid" does not travel up to the form by itself, hence the "true".
    // The line for a phone without an email app goes with it.
    function clearNote() {
      setNote("");
      if (altLine) {
        altLine.hidden = true;
      }
    }
    form.addEventListener("invalid", clearNote, true);
    form.addEventListener("input", clearNote);
    form.addEventListener("reset", clearNote);

    // The message under the Email field. Shown when the browser finds the
    // field empty or not an email address, hidden again once it is right.
    function showError(text) {
      if (!errorLine || !emailField) {
        return;
      }
      errorLine.textContent = text;
      errorLine.hidden = !text;
      if (text) {
        emailField.setAttribute("aria-invalid", "true");
      } else {
        emailField.removeAttribute("aria-invalid");
      }
    }

    if (emailField && errorLine) {
      emailField.addEventListener("invalid", function (event) {
        var missing = emailField.validity.valueMissing;
        var text = errorLine.getAttribute(missing ? "data-missing" : "data-invalid") || "";
        if (!text) {
          return;                 // no message of our own: the browser shows its bubble
        }
        event.preventDefault();   // our message in place of the browser's bubble
        showError(text);
        emailField.focus();
      });
      // While the visitor corrects the address the message stays, and it goes
      // as soon as the address is a possible one.
      emailField.addEventListener("input", function () {
        if (!errorLine.hidden && emailField.validity.valid) {
          showError("");
        }
      });
    }

    // While the form is on the screen, the Call bar of the phone layout steps
    // aside (class "form-on-screen" on body, the stylesheet slides the bar
    // away): it lay over the Send button while the page scrolled. The form
    // counts as on the screen once it has come 90 px up from the bottom edge,
    // which is where the bar sits. On a wide screen there is no bar and the
    // class changes nothing.
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        var last = entries[entries.length - 1];
        if (last.isIntersecting) {
          document.body.classList.add("form-on-screen");
        } else {
          document.body.classList.remove("form-on-screen");
        }
      }, { rootMargin: "0px 0px -90px 0px" }).observe(form);
    }

    form.addEventListener("submit", function (event) {
      // Never post the form itself. This script opens the email app instead.
      event.preventDefault();

      // A missing or mistyped email address: the browser shows its own message
      // next to the field and nothing else happens.
      if (typeof form.reportValidity === "function" && !form.reportValidity()) {
        clearNote();
        return;
      }
      showError("");

      var first = read("first-name");
      var last = read("last-name");
      var name = first && last ? first + " " + last : first || last;
      var sender = read("email");

      // The message, a blank line, the name, the sender's email address.
      // No name given: no name line. Line breaks go out as CR LF, which is
      // what email apps expect inside a mailto link.
      var lines = [read("message").replace(/\r\n|\r|\n/g, "\r\n"), ""];
      if (name) {
        lines.push(name);
      }
      if (sender) {
        lines.push(sender);
      }

      // A link that exists only for this one click.
      var link = document.createElement("a");
      link.href = "mailto:" + salonEmail +
        "?subject=" + encode("Website message from " + (name || "a visitor")) +
        "&body=" + encode(lines.join("\r\n"));
      document.body.appendChild(link);
      link.click();
      if (link.parentNode) {
        link.parentNode.removeChild(link);
      }

      setNote((form.getAttribute("data-sent") || "").trim() || sentFallback);
      // The same message for the text message app, with plain line breaks.
      showAlt(lines.join("\n").replace(/\r\n/g, "\n").replace(/^\n+/, ""));
    });
  }

  // ---------------------------------------------------------------------------
  // 5. Copyright year
  // ---------------------------------------------------------------------------

  /*
   * Copyright year in the footer (every element marked data-year).
   * Each page is saved with the year it was built in. This puts in the year
   * from the visitor's own clock, so the line stays right after New Year
   * without anyone rebuilding the site.
   * Without this script the year the page was built with stays in place.
   */
  function initYear() {
    var spots = document.querySelectorAll("[data-year]");
    var year = new Date().getFullYear();
    var built;
    var i;

    for (i = 0; i < spots.length; i++) {
      built = parseInt(spots[i].textContent, 10);
      // A page cannot be older than the year it was built in. A clock that says
      // an earlier year is wrong (never set, flat battery), so the built year
      // stays. The same year needs no change either.
      if (isNaN(built) || year > built) {
        spots[i].textContent = String(year);
      }
    }
  }

  // ---------------------------------------------------------------------------
  // 6. Map
  // ---------------------------------------------------------------------------

  /*
   * The Google map of the Contact page. Its address waits in data-src and is
   * moved into src when the map comes within about one screen of the window,
   * so a visitor who never scrolls down sends nothing to Google. A browser
   * without IntersectionObserver gets the map at once.
   * Without this script the frame stays empty and the link under it opens
   * the map in Google Maps.
   */
  function initMap() {
    var frames = Array.prototype.slice.call(document.querySelectorAll(".map iframe[data-src]"));
    if (!frames.length) {
      return;
    }

    function load(frame) {
      var src = frame.getAttribute("data-src");
      if (src) {
        frame.removeAttribute("data-src");
        frame.setAttribute("src", src);
      }
    }

    if (!("IntersectionObserver" in window)) {
      frames.forEach(load);
      return;
    }
    var watcher = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          watcher.unobserve(entry.target);
          load(entry.target);
        }
      });
    }, { rootMargin: "600px 0px" });
    frames.forEach(function (frame) {
      watcher.observe(frame);
    });
  }

  // ---------------------------------------------------------------------------
  // 7. Short header and pressed look
  // ---------------------------------------------------------------------------

  /*
   * The short header of the phone layout (class "compact" on <html>).
   * On a phone the header and the Call bar stay on the screen while the page
   * scrolls. Once the visitor has scrolled about 50 px down, the header draws
   * only its upper 64 px (smaller logo, the menu button beside it), which
   * leaves more of the screen to the page. Back at the top it is its full
   * 96 px again. On a screen that is 500 px tall or lower (a phone lying on
   * its side) it is short all the time.
   * This function only sets or removes the class. What the class looks like
   * is in the stylesheet, which uses it in the phone layout alone, so on a
   * wide screen nothing changes. The header keeps its place and size in the
   * page either way, so the page never jumps.
   * Without this script the header is never short.
   */
  function initHeader() {
    var root = document.documentElement;
    if (!root.classList || !document.querySelector(".site-header")) {
      return;
    }

    var low = window.matchMedia ? window.matchMedia("(max-height: 500px)") : null;
    var compact = false;
    var waiting = false;

    function update() {
      waiting = false;
      var y = window.pageYOffset || root.scrollTop || 0;
      // Short after 48 px, full again above 8 px: two marks, so the header does
      // not flicker when the page rests near one of them.
      var next = (low && low.matches) || (compact ? y > 8 : y > 48);
      if (next !== compact) {
        compact = next;
        if (compact) {
          root.classList.add("compact");
        } else {
          root.classList.remove("compact");
        }
      }
    }

    // At most one look per picture the browser draws, however often it reports scrolling.
    function later() {
      if (waiting) {
        return;
      }
      waiting = true;
      if (window.requestAnimationFrame) {
        window.requestAnimationFrame(update);
      } else {
        window.setTimeout(update, 50);
      }
    }

    window.addEventListener("scroll", later, { passive: true });
    if (low) {
      if (low.addEventListener) {
        low.addEventListener("change", later);
      } else if (low.addListener) {
        low.addListener(later);
      }
    }
    update();
  }

  /*
   * The pressed look of links and buttons on an iPhone.
   * The stylesheet gives a button a darker look while a finger is on it
   * (:active). Safari on the iPhone shows that look only on a page that
   * listens for touches, and this empty listener is all it takes.
   */
  function initPressed() {
    document.addEventListener("touchstart", function () {}, { passive: true });
  }

  // ---------------------------------------------------------------------------
  // 8. Text and Call box of the home page and of the Services page
  // ---------------------------------------------------------------------------

  /*
   * The beige box under Meet Gerta and the one under the cards of the
   * Services page (.reach) hold a Text button and a Call button, and so does the bar at the bottom of a phone screen (.call-bar).
   * While the box is on the screen the bar steps aside (class
   * "reach-on-screen" on body, the stylesheet slides the bar away), so the
   * visitor never sees the same two buttons twice. The box counts as on the
   * screen once it has come 90 px up from the bottom edge, which is where
   * the bar sits. When the box has left the screen, the bar comes back.
   * On a wide screen there is no bar and the class changes nothing.
   * A page without the box, and a browser without IntersectionObserver,
   * keep the bar where it is.
   */
  function initReach() {
    var box = document.querySelector(".reach");
    if (!box || !("IntersectionObserver" in window)) {
      return;
    }
    new IntersectionObserver(function (entries) {
      var last = entries[entries.length - 1];
      if (last.isIntersecting) {
        document.body.classList.add("reach-on-screen");
      } else {
        document.body.classList.remove("reach-on-screen");
      }
    }, { rootMargin: "0px 0px -90px 0px" }).observe(box);
  }

  // ---------------------------------------------------------------------------
  // 9. Label on the home photos
  // ---------------------------------------------------------------------------

  /*
   * The three photos of the home page are links to the Gallery. On a touch
   * screen nothing shows that, so a small blue label on the photos says it,
   * "Tap for more photos" (.row-cue inside .photo-row, itself a link to the
   * Gallery). The stylesheet keeps it away until it carries the class "on",
   * and never shows it under a mouse.
   * This part puts the class on once two things are true: the visitor has
   * started to scroll, and the label is in view. It takes the class away
   * again after the seconds written on the label (data-seconds, from
   * content/home.json, 4 when nothing usable is there).
   * Started to scroll: the page has moved at all. On most phones the photos
   * come into view with that first movement. On a tall screen they are in
   * view from the start, and there the label waits for the first movement
   * too, so it does not play while the visitor still reads the top of the
   * page. A page that opens already scrolled (a reload) counts as scrolled.
   * In view means: 140 px or more under the upper edge of the screen, so the
   * header is not over it and a good piece of the photos shows above it, and
   * 90 px or more above the lower edge, clear of the bar of a phone.
   * The label waits 0.4 seconds before it comes, so it does not flash up on a
   * page that is only scrolled past. When the photos leave the screen before
   * its seconds are over, it goes at once and starts over the next time they
   * come into view. Once it has had its full time it never comes again on
   * this page view.
   * A page without the label, and a browser without IntersectionObserver,
   * never show it.
   */
  function initRowCue() {
    var cue = document.querySelector(".photo-row .row-cue");
    if (!cue || !cue.classList || !("IntersectionObserver" in window)) {
      return;
    }
    var seconds = parseFloat(cue.getAttribute("data-seconds"));
    if (!(seconds > 0)) {
      seconds = 4;
    }
    var scrolled = (window.pageYOffset || document.documentElement.scrollTop || 0) > 0;
    var inView = false;
    var coming = null;  // the timer of the 0.4 seconds before the label comes
    var staying = null; // the timer of the seconds it stays
    var watcher = null;

    // Called whenever one of the two things may have changed.
    function look() {
      if (!inView) {
        window.clearTimeout(coming);
        window.clearTimeout(staying);
        coming = staying = null;
        cue.classList.remove("on");
        return;
      }
      if (!scrolled || coming !== null || staying !== null) {
        return;
      }
      coming = window.setTimeout(function () {
        coming = null;
        cue.classList.add("on");
        staying = window.setTimeout(function () {
          staying = null;
          cue.classList.remove("on");
          watcher.disconnect();
        }, seconds * 1000);
      }, 400);
    }

    function onFirstScroll() {
      window.removeEventListener("scroll", onFirstScroll);
      scrolled = true;
      look();
    }

    watcher = new IntersectionObserver(function (entries) {
      var last = entries[entries.length - 1];
      // In view: nine tenths of the label or more. Browsers do not agree on what
      // isIntersecting says below that mark, so the share is asked for as well.
      inView = last.isIntersecting && last.intersectionRatio >= 0.9;
      look();
    }, { rootMargin: "-140px 0px -90px 0px", threshold: 0.9 });
    watcher.observe(cue);
    if (!scrolled) {
      window.addEventListener("scroll", onFirstScroll, { passive: true });
    }
  }

  // ---------------------------------------------------------------------------
  // Start
  // ---------------------------------------------------------------------------

  // Runs one part. A part that fails is reported in the browser console and
  // does not stop the parts after it.
  function run(name, part) {
    try {
      part();
    } catch (error) {
      if (window.console && typeof window.console.error === "function") {
        window.console.error("site.js: the part \"" + name + "\" did not start.", error);
      }
    }
  }

  function start() {
    run("Book Now buttons", function () {
      // The link from the top of this file.
      initBooking(BOOKING_URL);
    });
    run("Phone menu", initMenu);
    run("Gallery photo viewer", initLightbox);
    run("Contact form", initContactForm);
    run("Copyright year", initYear);
    run("Map", initMap);
    run("Short header", initHeader);
    run("Pressed look", initPressed);
    run("Text and Call box", initReach);
    run("Label on the home photos", initRowCue);
  }

  // The pages load this file with "defer", so the whole page has been read
  // by the time this line runs. The wait is only there for a page that loads
  // the file some other way.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
