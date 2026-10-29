(() => {
  const grid = document.getElementById("gallery");
  const statusEl = document.getElementById("status");
  document.getElementById("year").textContent = new Date().getFullYear();

  let works = [];

  // Decide how big a tile should be from the artwork's shape.
  function sizeClass(w) {
    if (w.featured) return "big";
    const r = w.w / w.h;
    if (r >= 1.55) return "wide";
    if (r <= 0.68) return "tall";
    return "";
  }

  // The "sizes" attribute tells the browser which file to pick from srcset
  // before layout, so it only downloads what it needs.
  function sizesFor(cls) {
    const cols = cls === "big" || cls === "wide" ? 2 : 1;
    return `(max-width: 560px) ${cols * 50}vw, ${cols * 25}vw`;
  }

  function build(w, i) {
    const cls = sizeClass(w);
    const fig = document.createElement("figure");
    fig.className = "tile" + (cls ? " " + cls : "");
    fig.tabIndex = 0;
    fig.dataset.index = i;

    const mat = document.createElement("span");
    mat.className = "mat";
    mat.style.background = w.color || "#ece8df";

    const img = document.createElement("img");
    img.src = w.sizes[0].src;
    img.srcset = w.sizes.map(s => `${s.src} ${s.w}w`).join(", ");
    img.sizes = sizesFor(cls);
    img.width = w.w;
    img.height = w.h;
    img.alt = w.alt || w.title || "Artwork";
    img.decoding = "async";
    // First screenful loads eagerly; everything else waits until near the viewport.
    img.loading = i < 8 ? "eager" : "lazy";
    if (i < 3) img.fetchPriority = "high";
    const done = () => img.classList.add("loaded");
    if (img.complete) done(); else img.addEventListener("load", done, { once: true });
    img.addEventListener("error", done, { once: true });

    mat.appendChild(img);
    fig.appendChild(mat);

    if (w.title) {
      const cap = document.createElement("figcaption");
      cap.innerHTML = "<strong></strong><span></span>";
      cap.firstChild.textContent = w.title;
      cap.lastChild.textContent = [w.artist, w.year].filter(Boolean).join(", ");
      fig.appendChild(cap);
    }
    return fig;
  }

  function render() {
    const frag = document.createDocumentFragment();
    works.forEach((w, i) => frag.appendChild(build(w, i)));
    grid.appendChild(frag);
    statusEl.textContent = works.length ? "" : "No artwork yet. Add images and run the build script.";
  }

  // ---------- Lightbox ----------
  const lb = document.getElementById("lightbox");
  const lbImg = document.getElementById("lb-img");
  const lbCap = document.getElementById("lb-caption");
  let current = 0;
  let lastFocus = null;

  function show(i) {
    current = (i + works.length) % works.length;
    const w = works[current];
    const biggest = w.sizes[w.sizes.length - 1];
    lbImg.src = biggest.src;
    lbImg.alt = w.alt || w.title || "Artwork";
    lbCap.innerHTML = "";
    if (w.title) {
      const t = document.createElement("strong");
      t.textContent = w.title;
      lbCap.appendChild(t);
    }
    const meta = [w.artist, w.year, w.medium].filter(Boolean).join(" · ");
    if (meta) lbCap.appendChild(document.createTextNode(meta));
    // warm the neighbours so next/prev feels instant
    [current + 1, current - 1].forEach(n => {
      const nw = works[(n + works.length) % works.length];
      new Image().src = nw.sizes[nw.sizes.length - 1].src;
    });
  }
  function open(i) {
    lastFocus = document.activeElement;
    lb.hidden = false;
    document.body.style.overflow = "hidden";
    show(i);
    lb.querySelector(".lb-close").focus();
  }
  function close() {
    lb.hidden = true;
    document.body.style.overflow = "";
    lbImg.removeAttribute("src");
    if (lastFocus) lastFocus.focus();
  }

  grid.addEventListener("click", e => {
    const t = e.target.closest(".tile");
    if (t) open(+t.dataset.index);
  });
  grid.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") {
      const t = e.target.closest(".tile");
      if (t) { e.preventDefault(); open(+t.dataset.index); }
    }
  });
  lb.addEventListener("click", e => {
    if (e.target === lb || e.target.closest(".lb-close")) close();
    else if (e.target.closest(".lb-prev")) show(current - 1);
    else if (e.target.closest(".lb-next")) show(current + 1);
  });
  document.addEventListener("keydown", e => {
    if (lb.hidden) return;
    if (e.key === "Escape") close();
    else if (e.key === "ArrowLeft") show(current - 1);
    else if (e.key === "ArrowRight") show(current + 1);
  });

  // simple swipe support on touch devices
  let sx = null;
  lb.addEventListener("touchstart", e => { sx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener("touchend", e => {
    if (sx === null) return;
    const dx = e.changedTouches[0].clientX - sx;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    sx = null;
  });

  // ---------- Load ----------
  fetch("gallery.json")
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => { works = data; render(); })
    .catch(() => {
      statusEl.textContent = "Couldn't load gallery.json. If you opened index.html directly from disk, run a local server (python3 -m http.server).";
    });
})();
