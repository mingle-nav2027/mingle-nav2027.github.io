/* MINGLE project page — video view switching, lazy playback, filtering */
(function () {
  "use strict";

  var prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------- video cards ---------------- */

  function srcFor(card, view) {
    return card.dataset.base + "/" + view + ".mp4";
  }
  function posterFor(card, view) {
    return card.dataset.base + "/" + view + ".jpg";
  }

  function load(card, view, autoplay) {
    var video = card.querySelector("video");
    var stage = card.querySelector(".vstage");
    var want = srcFor(card, view);
    if (video.dataset.view === view && video.getAttribute("src")) {
      if (autoplay) play(video);
      return;
    }
    video.dataset.view = view;
    video.setAttribute("poster", posterFor(card, view));
    stage.classList.add("busy");
    video.setAttribute("src", want);
    video.load();
    if (autoplay) play(video);
  }

  function play(video) {
    if (prefersReducedMotion) return;
    var p = video.play();
    if (p && p.catch) p.catch(function () { /* autoplay blocked — poster stays */ });
  }

  function setupCard(card) {
    var video = card.querySelector("video");
    var stage = card.querySelector(".vstage");
    var buttons = card.querySelectorAll(".views button");

    video.addEventListener("loadedmetadata", function () {
      stage.classList.remove("busy");
      if (video.videoWidth && video.videoHeight) {
        stage.style.setProperty("--ar", video.videoWidth + " / " + video.videoHeight);
      }
    });
    video.addEventListener("error", function () { stage.classList.remove("busy"); });

    Array.prototype.forEach.call(buttons, function (btn) {
      btn.addEventListener("click", function () {
        Array.prototype.forEach.call(buttons, function (b) {
          b.setAttribute("aria-pressed", String(b === btn));
        });
        load(card, btn.dataset.view, true);
      });
    });
  }

  var cards = document.querySelectorAll(".vcard");
  Array.prototype.forEach.call(cards, setupCard);

  /* Play only what is on screen; keep bandwidth down elsewhere. */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var card = entry.target;
        var video = card.querySelector("video");
        if (entry.isIntersecting) {
          var active = card.querySelector('.views button[aria-pressed="true"]');
          load(card, active ? active.dataset.view : "third", true);
        } else if (!video.paused) {
          video.pause();
        }
      });
    }, { rootMargin: "120px 0px", threshold: 0.25 });
    Array.prototype.forEach.call(cards, function (c) { io.observe(c); });
  } else {
    Array.prototype.forEach.call(cards, function (c) { load(c, "third", false); });
  }

  /* ---------------- gallery filters ---------------- */

  var filterBar = document.querySelector(".filters");
  if (filterBar) {
    var buttons = filterBar.querySelectorAll("button");
    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      var key = btn.dataset.filter;
      Array.prototype.forEach.call(buttons, function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });
      Array.prototype.forEach.call(document.querySelectorAll(".vcard"), function (card) {
        var tags = (card.dataset.tags || "").split(" ");
        card.hidden = key !== "all" && tags.indexOf(key) === -1;
      });
      /* hide group headings that lost every card */
      Array.prototype.forEach.call(document.querySelectorAll("[data-group]"), function (group) {
        var visible = group.querySelectorAll(".vcard:not([hidden])").length;
        group.hidden = visible === 0;
        var count = group.querySelector(".count");
        if (count) count.textContent = visible + (visible === 1 ? " clip" : " clips");
      });
    });
  }

  /* ---------------- nav highlighting ---------------- */

  var navLinks = document.querySelectorAll(".nav-links a[href^='#']");
  if (navLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    Array.prototype.forEach.call(navLinks, function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var navIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        Array.prototype.forEach.call(navLinks, function (a) { a.classList.remove("active"); });
        var link = byId[entry.target.id];
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-40% 0px -55% 0px" });
    Object.keys(byId).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) navIO.observe(el);
    });
  }
})();
