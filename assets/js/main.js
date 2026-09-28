// Anino Welding Kenya: nav, gallery filters + lightbox, WhatsApp form. No dependencies.
(function () {
  "use strict";

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Header border once scrolled
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Gallery filters (also honours #gates, #doors… in the URL)
  var filterBar = document.querySelector(".filters");
  var items = Array.prototype.slice.call(document.querySelectorAll(".gallery__item"));
  function applyFilter(cat) {
    if (!filterBar) return;
    var btn = filterBar.querySelector('[data-filter="' + cat + '"]');
    if (!btn) { cat = "all"; btn = filterBar.querySelector('[data-filter="all"]'); }
    filterBar.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b === btn ? "true" : "false"); });
    items.forEach(function (it) { it.hidden = cat !== "all" && it.dataset.category !== cat; });
  }
  if (filterBar) {
    filterBar.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      applyFilter(b.dataset.filter);
      history.replaceState(null, "", b.dataset.filter === "all" ? location.pathname : "#" + b.dataset.filter);
    });
    if (location.hash) applyFilter(location.hash.slice(1));
  }

  // Lightbox
  var lb = document.querySelector(".lightbox");
  if (lb && items.length) {
    var img = lb.querySelector("img");
    var cap = lb.querySelector(".lb-caption");
    var current = 0;
    var visible = function () { return items.filter(function (i) { return !i.hidden; }); };
    var show = function (idx) {
      var list = visible();
      current = (idx + list.length) % list.length;
      var it = list[current];
      img.src = it.dataset.full;
      img.alt = it.querySelector("img").alt;
      cap.textContent = it.querySelector("img").alt;
    };
    var open = function (it) {
      show(visible().indexOf(it));
      lb.classList.add("open");
      document.body.style.overflow = "hidden";
      lb.querySelector(".lb-close").focus();
    };
    var close = function () { lb.classList.remove("open"); document.body.style.overflow = ""; img.src = ""; };
    items.forEach(function (it) {
      it.addEventListener("click", function () { open(it); });
      it.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(it); } });
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(current - 1);
      if (e.key === "ArrowRight") show(current + 1);
    });
    // Swipe on phones
    var x0 = null;
    lb.addEventListener("touchstart", function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }

  // Background video: desktop only, loaded when scrolled into view. Skipped for
  // reduced motion and data-saver so phones on mobile data never download it.
  var bgVideo = document.querySelector("video[data-src]");
  var saveData = navigator.connection && navigator.connection.saveData;
  if (bgVideo && "IntersectionObserver" in window && !saveData &&
      window.matchMedia("(min-width: 761px) and (prefers-reduced-motion: no-preference)").matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) { if (bgVideo.src) bgVideo.pause(); return; }
        if (!bgVideo.src) bgVideo.src = bgVideo.dataset.src;
        var p = bgVideo.play();
        if (p && p.catch) p.catch(function () {});
      });
    }, { rootMargin: "200px" });
    io.observe(bgVideo);
  }

  // Contact form → WhatsApp with the message pre-filled
  var waBtn = document.getElementById("send-wa");
  var form = document.getElementById("quote-form");
  if (waBtn && form) {
    waBtn.addEventListener("click", function () {
      if (!form.reportValidity()) return;
      var f = form.elements;
      var lines = [
        "Hello Anino Welding, I would like a quote.",
        "Name: " + f.name.value,
        "Phone: " + f.phone.value,
        "Need: " + f.service.value
      ];
      if (f.location.value) lines.push("Location: " + f.location.value);
      lines.push("", f.message.value);
      window.open("https://wa.me/" + form.dataset.wa + "?text=" + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
    });
  }
})();
