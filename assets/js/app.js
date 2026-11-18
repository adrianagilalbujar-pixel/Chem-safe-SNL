/* CHEM SAFE — interacción del sitio (sin dependencias) */
(function () {
  "use strict";
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---- Tema claro / oscuro ---- */
  function isDark() {
    var t = root.getAttribute("data-theme");
    if (t) return t === "dark";
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }
  $$("[data-theme-toggle]").forEach(function (b) {
    b.addEventListener("click", function () {
      var next = isDark() ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("chemsafe-theme", next); } catch (e) {}
    });
  });

  /* ---- Imprimir ---- */
  $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });

  /* ---- Aparición suave ---- */
  var reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    var ro = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); ro.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -6% 0px" });
    reveals.forEach(function (el) { ro.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  /* ---- Buscador y filtros (portada) ---- */
  var q = $("#q"), cards = $$(".sub[data-search]"), filter = "all";
  function norm(s) { return (s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[₀-₉]/g, function (c) { return String(c.charCodeAt(0) - 8320); }); }
  function applyFilter() {
    var term = norm(q ? q.value.trim() : "");
    var shown = 0;
    cards.forEach(function (c) {
      var okTerm = !term || norm(c.getAttribute("data-search")).indexOf(term) !== -1;
      var tags = c.getAttribute("data-tags").split(" ");
      var okTag = filter === "all" || tags.indexOf(filter) !== -1;
      c.hidden = !(okTerm && okTag);
      if (!c.hidden) { shown++; c.classList.add("in"); }
    });
    var empty = $("#empty");
    if (empty) empty.classList.toggle("show", shown === 0);
  }
  if (q) q.addEventListener("input", applyFilter);
  $$("[data-filter]").forEach(function (b) {
    b.addEventListener("click", function () {
      filter = b.getAttribute("data-filter");
      $$("[data-filter]").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
      applyFilter();
    });
  });

  /* ---- Matriz cruzada interactiva ---- */
  var ICON = { ok: "✓", bad: "✕", nd: "?" };
  $$(".xwrap").forEach(function (wrap) {
    var panel = $(".xdetail", wrap);
    $$("td button", wrap).forEach(function (b) {
      b.addEventListener("click", function () {
        $$("td button", wrap).forEach(function (o) { o.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        var st = b.getAttribute("data-state");
        panel.innerHTML = "";
        var head = document.createElement("div");
        head.innerHTML = '<span class="pill ' + (st === "ok" ? "ok" : st === "bad" ? "bad" : "") + '" style="' +
          (st === "nd" ? "background:var(--nd-bg);color:var(--nd)" : "") + '"></span>';
        head.firstChild.textContent = ICON[st] + "  " + b.getAttribute("data-label");
        var pair = document.createElement("div"); pair.className = "pair"; pair.textContent = b.getAttribute("data-pair");
        var p = document.createElement("p"); p.textContent = b.getAttribute("data-detail");
        panel.appendChild(head); panel.appendChild(pair); panel.appendChild(p);
      });
    });
  });

  /* ---- Índice de la ficha: sección activa ---- */
  var tocLinks = $$(".toc a[href^='#']");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var map = {};
    tocLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var current = null;
    var so = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) {
          if (current) current.classList.remove("active");
          current = map[e.target.id];
          if (current) {
            current.classList.add("active");
            var ol = current.closest("ol");
            if (ol && ol.scrollWidth > ol.clientWidth) {
              ol.scrollTo({ left: current.offsetLeft - 16, behavior: "smooth" });
            }
          }
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) so.observe(el); });
  }

  /* ---- Barra de progreso y volver arriba ---- */
  var bar = $(".progress"), top = $(".totop");
  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var r = max > 0 ? h.scrollTop / max : 0;
    if (bar) bar.style.transform = "scaleX(" + r + ")";
    if (top) top.classList.toggle("show", h.scrollTop > 700);
  }
  if (bar || top) { window.addEventListener("scroll", onScroll, { passive: true }); onScroll(); }
  if (top) top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });

  /* ---- Resalta la sección a la que se llega por enlace ---- */
  function flash() {
    var id = decodeURIComponent(location.hash.slice(1));
    var el = id && document.getElementById(id);
    if (!el || !el.classList.contains("sec") || !el.animate) return;
    el.animate([{ boxShadow: "0 0 0 4px color-mix(in srgb, var(--accent) 40%, transparent)" }, { boxShadow: "0 0 0 0 transparent" }],
      { duration: 1000, easing: "ease-out" });
  }
  window.addEventListener("hashchange", flash);
  flash();
})();
