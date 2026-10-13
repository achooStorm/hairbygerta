/*
 * ONLINE BOOKING LINK
 *
 * The line right under this note is where the link to your Square Appointments
 * online booking page goes.
 *
 * How to add it:
 *   1. Copy the full link to your booking page. It starts with https://
 *   2. Paste it between the two quote marks on the line under this note.
 *   3. Change nothing else on that line. Both quote marks stay, and so does
 *      the ; at the very end.
 *
 * Example only. This address is made up, your real link will look different:
 *   https://book.squareup.com/appointments/EXAMPLE-ONLY/location/EXAMPLE-ONLY/services
 *
 * Until a link is there, every Book Now button calls 347-671-5095.
 * Once a link is there, every Book Now button opens your booking page in a
 * new tab instead.
 * To go back to phone calls, delete the link and leave the two quote marks
 * with nothing between them.
 */
var BOOKING_URL = "";

/*
 * Nothing below this note has to be changed to add the booking link.
 *
 * Site script for Hair & Makeup by Gerta. Every page loads this one file
 * with "defer". It has five parts:
 *
 *   1. Book Now buttons       every element marked data-book
 *   2. Phone menu             .menu-btn and #main-nav
 *   3. Gallery photo viewer   the links inside .gallery
 *   4. Contact form           #contact-form and .form-note
 *   5. Copyright year         every element marked data-year
 *
 * Each part looks for its own elements and does nothing on a page that does
 * not have them. A part that fails does not stop the other parts.
 *
 * The pages also work without this script: the Book Now buttons are phone
 * links, the menu is a plain list of links, each gallery photo opens on its
 * own, the contact form is a plain email form and the year is the one the
 * page was built with.
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
    var swipe = null;       // start point of a one-finger touch
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
    var img = document.createElement("img");
    img.className = "lb-img";
    img.alt = "";
    var nextBtn = makeButton("lb-next", "Next photo", "\u203a");
    var count = document.createElement("p");
    count.className = "lb-count";
    count.setAttribute("aria-live", "polite");

    box.appendChild(closeBtn);
    box.appendChild(prevBtn);
    box.appendChild(img);
    box.appendChild(nextBtn);
    box.appendChild(count);
    document.body.appendChild(box);

    var stops = [closeBtn, prevBtn, nextBtn];

    function show(i) {
      index = ((i % total) + total) % total;
      var link = links[index];
      var thumb = link.querySelector("img");
      img.alt = thumb ? thumb.alt : "";
      img.src = link.getAttribute("href");
      count.textContent = (index + 1) + " / " + total;
    }

    function step(by) {
      direction = by;
      show(index + by);
    }

    function isBackdrop(node) {
      return node === box || node === count;
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
        step(1);
      } else if (key === "ArrowLeft" || key === "Left") {
        e.preventDefault();
        step(-1);
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
      img.removeAttribute("src");   // the next opening must not flash the old photo
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
        step(-1);
      }
    });
    nextBtn.addEventListener("click", function (e) {
      if (!leftoverClick(e)) {
        step(1);
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
      if (isBackdrop(e.target) && (from === null || isBackdrop(from))) {
        closeViewer();
      }
    });

    // Once a photo is in, fetch the one the visitor is most likely to ask for next.
    img.addEventListener("load", function () {
      var connection = navigator.connection;
      if (!isOpen || total < 2 || (connection && connection.saveData)) {
        return;
      }
      preloaded = new Image();
      preloaded.src = links[(index + direction + total) % total].href;
    });

    // Swipe: left = next photo, right = previous photo. One finger only, mostly sideways,
    // and not while the visitor has pinch-zoomed into the photo.
    // A second finger fires touchstart again, which drops the swipe, so a pinch never counts.
    var passive = { passive: true };
    box.addEventListener("touchstart", function (e) {
      swipe = e.touches.length === 1 ? { x: e.touches[0].clientX, y: e.touches[0].clientY } : null;
    }, passive);
    box.addEventListener("touchcancel", function () {
      swipe = null;
    }, passive);
    box.addEventListener("touchend", function (e) {
      var start = swipe;
      var end = e.changedTouches[0];
      var view = window.visualViewport;
      swipe = null;
      if (!start || !end || (view && view.scale > 1.05)) {
        return;
      }
      var dx = end.clientX - start.x;
      var dy = end.clientY - start.y;
      if (Math.abs(dx) >= 40 && Math.abs(dx) > 1.5 * Math.abs(dy)) {
        step(dx < 0 ? 1 : -1);
      }
    }, passive);
  }

  // ---------------------------------------------------------------------------
  // 4. Contact form
  // ---------------------------------------------------------------------------

  /*
   * Contact form (#contact-form on the Contact page).
   * Pressing Send opens the visitor's own email app with a new message to
   * info@hairbygerta.com: subject, text, name and email address already filled
   * in. The visitor then presses send in the email app.
   * Nothing is stored and nothing is sent to any server.
   * The line shown under the button afterwards is the form's data-sent text.
   * Without this script the form is a plain mailto form and still works.
   */
  function initContactForm() {
    var form = document.getElementById("contact-form");
    if (!form) {
      return;
    }

    var salonEmail = "info@hairbygerta.com";
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

    // The status line only ever speaks about the send that just happened.
    // It is emptied as soon as the visitor types again, and when the browser
    // stops a send because the email address is missing or mistyped (the
    // browser then shows its own message and never reaches the code below).
    // "invalid" does not travel up to the form by itself, hence the "true".
    function clearNote() {
      setNote("");
    }
    form.addEventListener("invalid", clearNote, true);
    form.addEventListener("input", clearNote);
    form.addEventListener("reset", clearNote);

    form.addEventListener("submit", function (event) {
      // Never post the form itself. This script opens the email app instead.
      event.preventDefault();

      // A missing or mistyped email address: the browser shows its own message
      // next to the field and nothing else happens.
      if (typeof form.reportValidity === "function" && !form.reportValidity()) {
        clearNote();
        return;
      }

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
