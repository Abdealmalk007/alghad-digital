"use strict";
/* Progressive enhancement of the server-rendered bilingual TOP 5 hub. */
(() => {
  const root = document.getElementById("top5-hub");
  if (!root) return;
  const tabs = [...root.querySelectorAll('[role="tab"][data-top5-id]')];
  const panels = new Map([...root.querySelectorAll('[role="tabpanel"]')].map(node => [node.id.slice(11), node]));
  if (!tabs.length) return;
  const select = (id, focus = false, updateHash = false) => {
    const tab = tabs.find(x => x.dataset.top5Id === id);
    if (!tab || !panels.has(id)) return false;
    for (const option of tabs) {
      const active = option === tab;
      option.setAttribute("aria-selected", String(active));
      option.tabIndex = active ? 0 : -1;
      const panel = panels.get(option.dataset.top5Id);
      if (panel) panel.hidden = !active;
    }
    if (focus) tab.focus({preventScroll: true});
    if (updateHash) {
      try {
        const url = new URL(location.href);
        url.hash = "category-" + id;
        history.replaceState(null, "", url.pathname + url.search + url.hash);
      } catch (_) { /* Categorized stories work without History API. */ }
    }
    return true;
  };
  for (let i = 0; i < tabs.length; i++) {
    const tab = tabs[i];
    tab.addEventListener("click", () => select(tab.dataset.top5Id, false, true));
    tab.addEventListener("keydown", event => {
      const rtl = document.documentElement.dir === "rtl";
      const delta = event.key === "ArrowDown" || event.key === (rtl ? "ArrowLeft" : "ArrowRight") ? 1
        : event.key === "ArrowUp" || event.key === (rtl ? "ArrowRight" : "ArrowLeft") ? -1 : 0;
      let index = delta ? (i + delta + tabs.length) % tabs.length : -1;
      if (event.key === "Home") index = 0;
      if (event.key === "End") index = tabs.length - 1;
      if (index < 0) return;
      event.preventDefault();
      select(tabs[index].dataset.top5Id, true, true);
    });
  }
  const back = root.querySelector("[data-top5-back]");
  if (back) back.addEventListener("click", () => {
    const target = root.querySelector("#top5-categories");
    if (target) target.scrollIntoView({behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth", block:"start"});
    const active = tabs.find(x => x.getAttribute("aria-selected") === "true");
    if (active) active.focus({preventScroll:true});
  });
  const top = root.querySelector("[data-top5-top]");
  if (top) top.addEventListener("click", () => window.scrollTo({
    top: 0, behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "instant" : "smooth"
  }));
  const hash = decodeURIComponent(location.hash.replace(/^#category-/, ""));
  select(hash && hash !== location.hash ? hash : tabs[0].dataset.top5Id);
  window.addEventListener("hashchange", () => {
    if (location.hash.startsWith("#category-")) select(location.hash.slice(10));
  });
})();
