/* Explicit-consent GA4 loader. No network request before the visitor opts in. */
(function () {
  "use strict";
  const tag = document.getElementById("protech-analytics");
  const id = tag && tag.getAttribute("data-ga4-id");
  if (!/^G-[A-Z0-9]{6,16}$/.test(id || "")) return;

  const key = "alghad_analytics_consent_v1";
  const en = /^en\b/i.test(document.documentElement.lang || "");
  const labels = en ? {
    settings: "Analytics preferences", title: "Visitor analytics",
    description: "Allow optional Google Analytics 4 to measure visits, approximate country, browser and device? Nothing is sent before you accept.",
    accept: "Allow analytics", decline: "Decline"
  } : {
    settings: "تفضيلات الإحصائيات", title: "إحصائيات زيارات الموقع",
    description: "هل توافق على استخدام Google Analytics 4 لقياس الزيارات والبلد التقريبي والمتصفح والجهاز؟ لا تُرسل بيانات قبل الموافقة.",
    accept: "أوافق", decline: "لا أوافق"
  };
  function decision() {
    try {
      const value = localStorage.getItem(key);
      return value === "yes" || value === "no" ? value : null;
    } catch (_) { return null; }
  }
  function save(value) {
    try { localStorage.setItem(key, value); } catch (_) { /* session only */ }
  }
  let active = false;
  function activate() {
    if (active) return;
    active = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", id, {
      anonymize_ip: true, allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    const script = document.createElement("script");
    script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(id);
    script.async = true;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    document.head.appendChild(script);
  }
  function revokeCookies() {
    for (const part of document.cookie.split(";")) {
      const name = part.trim().split("=")[0];
      if (!/^(_ga($|_)|_gid$)/.test(name)) continue;
      document.cookie = name + "=; Max-Age=0; Path=/; SameSite=Lax";
      document.cookie = name + "=; Max-Age=0; Path=/; Domain=.alghad.digital; SameSite=Lax";
    }
  }
  function showPreferences() {
    if (document.querySelector(".protech-analytics-consent")) return;
    const panel = document.createElement("section");
    panel.className = "protech-analytics-consent";
    panel.setAttribute("role", "region");
    panel.setAttribute("aria-label", labels.title);
    const heading = document.createElement("strong");
    heading.textContent = labels.title;
    const p = document.createElement("p");
    p.textContent = labels.description;
    const actions = document.createElement("div");
    actions.className = "protech-analytics-actions";
    for (const [value, label] of [["yes", labels.accept], ["no", labels.decline]]) {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = label;
      button.className = "protech-analytics-choice " + (value === "yes" ? "accept" : "decline");
      button.addEventListener("click", function () {
        const wasActive = decision() === "yes";
        save(value);
        panel.remove();
        if (value === "yes") activate();
        else if (wasActive) { revokeCookies(); location.reload(); }
      });
      actions.appendChild(button);
    }
    panel.append(heading, p, actions);
    document.body.appendChild(panel);
  }
  function initialize() {
    const footer = document.querySelector(".site-footer .shell") || document.querySelector("footer") || document.body;
    const settings = document.createElement("button");
    settings.type = "button";
    settings.className = "protech-analytics-preferences";
    settings.textContent = labels.settings;
    settings.addEventListener("click", showPreferences);
    footer.appendChild(settings);
    const selected = decision();
    if (selected === "yes") activate();
    else if (selected === null) showPreferences();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize, {once:true});
  else initialize();
})();
