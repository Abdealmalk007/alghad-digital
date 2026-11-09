"use strict";
/* Alghad Digital v3.2 — direct downloads for verified published releases. */
(() => {
  const manifest = window.AL_GHAD_DOWNLOADS || {};
  const products = Array.isArray(window.AL_GHAD_PRODUCTS) ? window.AL_GHAD_PRODUCTS : [];
  const catalog = document.getElementById("catalog");
  const modal = document.getElementById("product-modal");
  if (!catalog || !modal) return;
  const byId = new Map(products.map(p => [p.id, p]));
  const owner = "Abdealmalk007";

  function configFor(id) {
    const product = byId.get(id);
    const config = Object.prototype.hasOwnProperty.call(manifest, id) ? manifest[id] : null;
    if (!product || product.status !== "public" || !config ||
        !/^[A-Za-z0-9._-]+$/.test(config.repository)) return null;
    if (product.github !== "https://github.com/" + owner + "/" + config.repository) return null;
    return config;
  }

  function validLink(value, config, kind) {
    if (typeof value !== "string" || !config) return "";
    try {
      const url = new URL(value);
      if (url.protocol !== "https:" || url.hostname !== "github.com" ||
          url.port || url.username || url.password || url.search || url.hash) return "";
      const path = "/" + owner + "/" + config.repository + "/releases/";
      const parts = url.pathname.slice(path.length).split("/");
      if (!url.pathname.startsWith(path)) return "";
      if (kind === "release") return parts.length === 2 && parts[0] === "tag" &&
        /^[A-Za-z0-9._-]+$/.test(parts[1]) ? url.href : "";
      if (kind === "asset") return parts.length === 3 && parts[0] === "download" &&
        /^[A-Za-z0-9._-]+$/.test(parts[1]) &&
        /^[A-Za-z0-9._-]+\.(apk|exe|zip|txt)$/i.test(parts[2]) ? url.href : "";
      return "";
    } catch (_) { return ""; }
  }
  const megabytes = bytes => Number.isFinite(bytes) && bytes > 0
    ? (bytes / 1048576).toLocaleString("ar-SA", {maximumFractionDigits: 1}) + " MB" : "";

  function link(text, url, className, label) {
    const a = document.createElement("a");
    a.textContent = text;
    a.href = url;
    a.className = className;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    if (label) a.setAttribute("aria-label", label);
    return a;
  }
  function fileList(config) {
    return (Array.isArray(config.files) ? config.files : []).filter(f => validLink(f.url, config, "asset"));
  }
  function updateCardDownloads() {
    catalog.querySelectorAll(".product-card[data-id]").forEach(card => {
      if (card.querySelector(".direct-download-card")) return;
      const config = configFor(card.dataset.id);
      if (!config) return;
      const files = fileList(config);
      const primary = files.find(f => f.recommended) || files[0];
      if (!primary) return;
      const actions = card.querySelector(".card-actions");
      if (!actions) return;
      const a = link("↓ تحميل مباشر", validLink(primary.url, config, "asset"),
        "direct-download-card", "تحميل " + byId.get(card.dataset.id).title + " — " + primary.label);
      a.title = primary.platform + " — " + megabytes(primary.bytes);
      actions.prepend(a);
    });
  }
  function node(tag, className, text) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    if (text !== undefined) el.textContent = text;
    return el;
  }

  function renderDownloadPanel(id) {
    const config = configFor(id);
    if (!config) return;
    const content = modal.querySelector(".modal-content");
    if (!content || content.querySelector(".download-section")) return;
    const product = byId.get(id);
    const files = fileList(config);
    const section = node("section", "download-section");
    section.setAttribute("aria-label", "خيارات تحميل البرنامج");
    const heading = node("div", "download-heading");
    const headingText = node("div", "download-heading-text");
    headingText.appendChild(node("span", "download-eyebrow", "OFFICIAL GITHUB RELEASES"));
    headingText.appendChild(node("h3", "", files.length ? "تحميل " + product.title : "حالة تحميل " + product.title));
    heading.appendChild(headingText);
    heading.appendChild(node("span", files.length ? "download-release-tag" : "download-release-tag unavailable",
      files.length ? "v" + config.version + " · Preview" : "لم يُنشر إصدار عام"));
    section.appendChild(heading);

    if (!files.length) {
      section.appendChild(node("p", "download-unavailable",
        config.note || "لا تتوفر ملفات تثبيت عامة لهذا البرنامج حتى الآن."));
    } else {
      section.appendChild(node("p", "download-intro",
        "اختر النسخة المناسبة لجهازك. الملفات تُحمّل مباشرة من مستودع المطور على GitHub؛ وليست مستضافة على موقع وسيط."));
      const list = node("div", "download-variants");
      files.forEach(file => {
        const row = node("div", "download-variant");
        const details = node("div", "download-variant-info");
        details.appendChild(node("strong", "", file.label));
        details.appendChild(node("small", "",
          [file.platform, megabytes(file.bytes)].filter(Boolean).join(" · ")));
        if (file.recommended) details.appendChild(node("span", "recommended-download", "النسخة المقترحة"));
        row.appendChild(details);
        row.appendChild(link("تنزيل ↗", validLink(file.url, config, "asset"),
          "download-variant-link" + (file.recommended ? " download-primary" : ""),
          "تنزيل " + product.title + " — " + file.label));
        list.appendChild(row);
      });
      section.appendChild(list);
      section.appendChild(node("p", "download-caution",
        config.note || "هذه نسخة معاينة. تحقق من التوافق قبل التثبيت."));
      section.appendChild(node("p", "download-trust-note",
        "ملاحظة أمنية: نشر الملف على GitHub لا يضمن توقيع ملف التثبيت؛ لا تعطّل SmartScreen أو الحماية لتجاوز أي تحذير."));
    }
    const before = content.querySelector(".modal-section-title");
    if (before) content.insertBefore(section, before);
    else content.appendChild(section);
  }

  new MutationObserver(updateCardDownloads).observe(catalog, {childList: true});
  updateCardDownloads();
  document.addEventListener("click", event => {
    const target = event.target.closest("[data-detail]");
    if (target) renderDownloadPanel(target.dataset.detail);
  });
})();
