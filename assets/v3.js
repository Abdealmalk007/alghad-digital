"use strict";
/* Alghad Digital v3: progressive enhancements; no backend or tracking. */
(function () {
  const products = Array.isArray(window.AL_GHAD_PRODUCTS) ? window.AL_GHAD_PRODUCTS : [];
  const byId = new Map(products.map(p => [p.id, p]));
  const originalOrder = new Map(products.map((p, i) => [p.id, i]));
  const selected = new Set();
  const catalog = document.getElementById("catalog");
  const search = document.getElementById("search");
  const sorter = document.getElementById("sort-products");
  const tray = document.getElementById("compare-tray");
  const trayCount = document.getElementById("compare-count");
  const trayNames = document.getElementById("compare-names");
  const trayMessage = document.getElementById("compare-message");
  const compareOpen = document.getElementById("compare-open");
  const compareClear = document.getElementById("compare-clear");
  const compareDialog = document.getElementById("compare-dialog");
  const modal = document.getElementById("product-modal");
  if (!catalog || !search || !sorter || !tray || !compareDialog || !modal) return;

  const escapeHtml = value => String(value == null ? "" : value).replace(/[&<>"']/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const previewFor = p => /^assets\/previews\/[a-z0-9_-]+\.svg$/.test(p.preview || "") ? p.preview : "favicon.svg";
  const statusFor = p => p.status === "public" && /^https:\/\/github\.com\/Abdealmalk007\/[A-Za-z0-9._-]+$/.test(p.github || "")
    ? "مكتمل النشر" : "قريبًا جدًا";
  const appUrl = id => {
    const u = new URL(window.location.href);
    u.searchParams.set("app", id);
    u.hash = "";
    return u.toString();
  };

  function hydrateCompareButtons() {
    catalog.querySelectorAll(".product-card[data-id]").forEach(card => {
      const p = byId.get(card.dataset.id);
      if (!p) return;
      const actions = card.querySelector(".card-actions");
      if (!actions) return;
      let button = actions.querySelector(".compare-toggle");
      if (!button) {
        button = document.createElement("button");
        button.type = "button";
        button.className = "compare-toggle";
        button.dataset.compare = p.id;
        actions.appendChild(button);
      }
      const active = selected.has(p.id);
      button.textContent = active ? "✓ ضمن المقارنة" : "⊕ قارن";
      button.setAttribute("aria-pressed", String(active));
      button.setAttribute("aria-label", (active ? "إزالة " : "مقارنة ") + p.title);
    });
  }
  new MutationObserver(hydrateCompareButtons).observe(catalog, {childList: true});
  hydrateCompareButtons();

  function updateTray(message) {
    hydrateCompareButtons();
    tray.hidden = selected.size === 0;
    trayCount.textContent = String(selected.size);
    trayNames.textContent = Array.from(selected, id => byId.get(id).title).join(" · ");
    trayMessage.textContent = message || (selected.size < 2 ? "اختر برنامجًا آخر للمقارنة" : "المقارنة جاهزة");
    compareOpen.disabled = selected.size < 2;
  }

  document.addEventListener("click", event => {
    const target = event.target.closest("[data-compare]");
    if (!target) return;
    const id = target.dataset.compare;
    if (!byId.has(id)) return;
    if (selected.has(id)) selected.delete(id);
    else if (selected.size >= 3) return updateTray("يمكن مقارنة ثلاثة برامج كحد أقصى");
    else selected.add(id);
    updateTray();
  });
  compareClear.addEventListener("click", () => { selected.clear(); updateTray(); });

  function renderComparison() {
    if (selected.size < 2) return;
    const chosen = Array.from(selected, id => byId.get(id));
    const panels = chosen.map(p =>
      '<article class="compare-panel">' +
      '<img src="' + previewFor(p) + '" alt="' + escapeHtml(p.previewAlt || p.title) + '" width="960" height="540">' +
      '<div class="compare-panel-body"><span class="compare-platform">' + escapeHtml(p.platforms.join(" / ")) + '</span>' +
      '<h3>' + escapeHtml(p.title) + '</h3>' +
      '<span class="compare-status">' + statusFor(p) + '</span>' +
      '<p>' + escapeHtml(p.description) + '</p>' +
      '<p class="compare-version">الإصدار: ' + escapeHtml(p.version) + '</p>' +
      '<h4>أبرز المميزات</h4><ul>' +
      p.features.map(feature => '<li>' + escapeHtml(feature) + '</li>').join("") +
      '</ul><button class="button button-secondary compare-details" type="button" data-compare-detail="' +
      escapeHtml(p.id) + '">تفاصيل البرنامج</button></div></article>').join("");
    compareDialog.innerHTML =
      '<div class="compare-dialog-head"><div><span class="section-kicker">SIDE BY SIDE</span><h2 id="compare-title">مقارنة البرامج</h2>' +
      '<p>مقارنة المعلومات المعلنة لكل مشروع، وليست تقييمًا لأداء الإصدارات.</p></div>' +
      '<button class="compare-close icon-button" type="button" data-compare-close aria-label="إغلاق المقارنة">✕</button></div>' +
      '<div class="compare-grid" style="--compare-columns:' + chosen.length + '">' + panels + '</div>';
    if (typeof compareDialog.showModal === "function") compareDialog.showModal();
    else compareDialog.setAttribute("open", "");
  }
  compareOpen.addEventListener("click", renderComparison);
  compareDialog.addEventListener("click", event => {
    if (event.target === compareDialog || event.target.closest("[data-compare-close]")) compareDialog.close();
    const detail = event.target.closest("[data-compare-detail]");
    if (detail) {
      compareDialog.close();
      const button = document.querySelector('[data-detail="' + detail.dataset.compareDetail + '"]');
      if (button) button.click();
    }
  });

  sorter.addEventListener("change", () => {
    const mode = sorter.value;
    const status = p => statusFor(p) === "مكتمل النشر" ? 0 : 1;
    products.sort((a, b) => {
      if (mode === "name") return a.title.localeCompare(b.title, "ar");
      if (mode === "published") return status(a) - status(b) || originalOrder.get(a.id) - originalOrder.get(b.id);
      if (mode === "upcoming") return status(b) - status(a) || originalOrder.get(a.id) - originalOrder.get(b.id);
      return originalOrder.get(a.id) - originalOrder.get(b.id);
    });
    search.dispatchEvent(new Event("input", {bubbles: true}));
  });

  // A shareable query parameter opens the existing accessible product dialog.
  function addShareAction() {
    const actions = modal.querySelector(".modal-actions");
    if (!actions || actions.querySelector("[data-share-app]")) return;
    const button = document.createElement("button");
    button.type = "button";
    button.className = "button button-secondary share-product";
    button.dataset.shareApp = modal.dataset.currentProduct;
    button.textContent = "نسخ رابط البرنامج";
    actions.appendChild(button);
  }
  document.addEventListener("click", event => {
    const detail = event.target.closest("[data-detail]");
    if (detail && byId.has(detail.dataset.detail)) {
      modal.dataset.currentProduct = detail.dataset.detail;
      const u = new URL(location.href);
      u.searchParams.set("app", detail.dataset.detail);
      history.replaceState(null, "", u);
      requestAnimationFrame(addShareAction);
    }
  });
  modal.addEventListener("close", () => {
    delete modal.dataset.currentProduct;
    const u = new URL(location.href);
    if (u.searchParams.has("app")) {
      u.searchParams.delete("app");
      history.replaceState(null, "", u);
    }
  });
  modal.addEventListener("click", async event => {
    const share = event.target.closest("[data-share-app]");
    if (!share) return;
    const link = appUrl(share.dataset.shareApp);
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw Error("Clipboard unavailable");
      await navigator.clipboard.writeText(link);
      share.textContent = "✓ تم نسخ الرابط";
      setTimeout(() => { if (share.isConnected) share.textContent = "نسخ رابط البرنامج"; }, 2300);
    } catch (_) {
      window.prompt("انسخ رابط البرنامج:", link);
    }
  });

  window.addEventListener("keydown", event => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      if (!modal.open && !compareDialog.open) search.focus();
    }
    if (event.key === "Escape" && document.activeElement === search && search.value) {
      search.value = "";
      search.dispatchEvent(new Event("input", {bubbles:true}));
    }
  });
  const paramId = new URL(location.href).searchParams.get("app");
  if (paramId && byId.has(paramId)) {
    const openButton = document.querySelector('[data-detail="' + paramId + '"]');
    if (openButton) requestAnimationFrame(() => openButton.click());
  }
})();
