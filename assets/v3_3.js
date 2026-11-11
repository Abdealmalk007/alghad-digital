"use strict";
/* Alghad Digital 3.3: releases showcase and honest site-security guidance. */
(() => {
  const root = document.getElementById("release-showcase");
  if (!root || !Array.isArray(window.AL_GHAD_PRODUCTS)) return;

  const releases = window.AL_GHAD_DOWNLOADS || {};
  const releaseFacts = window.AL_GHAD_RELEASE_FACTS?.releases || {};
  const products = window.AL_GHAD_PRODUCTS;
  const owner = "Abdealmalk007";
  const featured = ["quotes", "download", "hr", "marble", "reports", "stone"];
  const byId = new Map(products.map(item => [item.id, item]));

  function safeAsset(raw, config, extension) {
    if (!raw || !config) return null;
    try {
      const url = new URL(raw);
      if (url.protocol !== "https:" || url.host !== "github.com" ||
          url.username || url.password || url.search || url.hash) return null;
      const base = "/" + owner + "/" + config.repository + "/releases/download/";
      if (!url.pathname.startsWith(base)) return null;
      const suffix = url.pathname.slice(base.length);
      if (!/^[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+\.(apk|exe|zip)$/i.test(suffix)) return null;
      if (extension && !suffix.toLowerCase().endsWith(extension)) return null;
      return url.href;
    } catch (_) { return null; }
  }

  function el(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }
  function link(text, url, css) {
    const item = el("a", css, text);
    item.href = url;
    item.target = "_blank";
    item.rel = "noopener noreferrer";
    return item;
  }

  const frag = document.createDocumentFragment();
  let releaseCount = 0;
  featured.forEach((id, i) => {
    const product = byId.get(id);
    const config = releases[id];
    if (!product || product.status !== "public" || !config ||
        product.github !== "https://github.com/" + owner + "/" + config.repository) return;
    const assets = (config.files || []).map(f => ({
      ...f, safeUrl:safeAsset(f.url, config)
    })).filter(f => Boolean(f.safeUrl));
    const primary = assets.find(f => f.recommended) || assets[0];

    const article = el("article", "showcase-release");
    article.dataset.releaseId = id;
    const art = el("div", "showcase-release-art");
    const preview = el("img");
    preview.src = /^assets\/previews\/[a-z0-9_-]+\.svg$/.test(product.preview)
      ? product.preview : "favicon.svg";
    preview.alt = product.previewAlt || product.title;
    preview.loading = "lazy";
    preview.decoding = "async";
    preview.width = 960; preview.height = 540;
    art.appendChild(preview);
    art.appendChild(el("span", "showcase-art-number", String(i + 1).padStart(2, "0")));
    article.appendChild(art);

    const body = el("div", "showcase-release-content");
    const kicker = el("div", "showcase-release-kicker");
    kicker.appendChild(el("span", primary ? "showcase-release-channel" : "showcase-release-channel unavailable",
      primary ? "PREVIEW RELEASE" : "NO PUBLIC RELEASE"));
    kicker.appendChild(el("span", "showcase-release-platform", product.platforms.join(" / ")));
    body.appendChild(kicker);
    body.appendChild(el("h3", "", product.title));
    body.appendChild(el("p", "showcase-release-desc", product.summary || product.description));
    const meta = el("div", "showcase-release-meta");
    meta.appendChild(el("span", "", primary
      ? "v" + config.version + " · " + assets.length + (assets.length === 1 ? " نسخة" : " خيارات")
      : "لم تُنشر نسخة تثبيت عامة"));
    const facts=releaseFacts[id];
    if(primary && facts?.version===config.version && facts?.repository===config.repository){
      const match=Array.isArray(facts.assets)?facts.assets.find(x=>x.url===primary.safeUrl && x.bytes===primary.bytes):null;
      if(match && /^[a-f0-9]{64}$/.test(match.sha256)){
        meta.appendChild(el("span","showcase-release-date","تاريخ النشر: "+facts.published_at.slice(0,10)));
        const digest=el("code","showcase-release-sha","SHA-256: "+match.sha256);
        digest.dir="ltr";meta.appendChild(digest);
      }
    }
    body.appendChild(meta);

    const actions = el("div", "showcase-release-actions");
    if (primary) {
      actions.appendChild(link("تحميل مباشر ↗", primary.safeUrl, "showcase-release-cta"));
      releaseCount++;
    } else {
      actions.appendChild(el("span", "showcase-release-unavailable", "ملف التثبيت غير متاح"));
    }
    body.appendChild(actions);
    article.appendChild(body);
    frag.appendChild(article);
  });
  root.replaceChildren(frag);
  const total = document.getElementById("release-showcase-count");
  if (total) total.textContent = String(releaseCount) + " إصدارات متاحة للتنزيل";

  // A site certificate and an executable's publisher signature are different
  // controls. Avoid claiming that all installer files are digitally signed.
  const tls = document.getElementById("trust-current-connection");
  if (tls) tls.textContent =
    location.protocol === "https:" && window.isSecureContext
      ? "اتصال هذه الصفحة مشفّر عبر HTTPS"
      : "للاتصال المشفّر، افتح https://alghad.digital";
})();
