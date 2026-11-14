"use strict";
/* Alghad Digital 3.4 — synced catalog metrics and lightweight navigation. */
(() => {
  const products = Array.isArray(window.AL_GHAD_PRODUCTS) ? window.AL_GHAD_PRODUCTS : [];
  const ids = new Set(products.map(product => product.id));
  const galleryCount = document.getElementById("gallery-portfolio-count");
  if (galleryCount) galleryCount.textContent = String(products.length).padStart(2, "0");

  // Discard stale deep links to products no longer present in the catalog.
  try {
    const url = new URL(location.href);
    if (url.searchParams.has("app") && !ids.has(url.searchParams.get("app"))) {
      url.searchParams.delete("app");
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    }
  } catch (_) { /* Browsing and catalog remain functional without history access. */ }

  const back = document.getElementById("back-to-top-floating");
  if (!back) return;
  let scheduled = false;
  const reduceMotion = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const refresh = () => {
    const modalOpen = ["product-modal"].some(id => {
      const dialog = document.getElementById(id);
      return dialog && dialog.open;
    });
    const searchOpen=document.body.classList.contains("sitewide-search-open");
    back.hidden = window.scrollY < 650 || modalOpen || searchOpen;
    if (!back.hidden) {
      const a=back.getBoundingClientRect();
      const blockers=document.querySelectorAll(".sitewide-search-trigger");
      for (const blocker of blockers) {
        const style=getComputedStyle(blocker);
        if(style.display==="none" || style.visibility==="hidden")continue;
        const b=blocker.getBoundingClientRect();
        const margin=8;
        if(a.left<b.right+margin && a.right+margin>b.left &&
           a.top<b.bottom+margin && a.bottom+margin>b.top) {
          back.hidden=true;
          break;
        }
      }
    }
    scheduled = false;
  };
  const onScroll = () => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(refresh);
  };
  window.addEventListener("scroll", onScroll, {passive:true});
  window.addEventListener("resize", onScroll, {passive:true});
  window.addEventListener("orientationchange", onScroll, {passive:true});
  new MutationObserver(onScroll).observe(document.body,{attributes:true,attributeFilter:["class"]});
  document.addEventListener("click", event => {
    const button = event.target.closest("[data-detail]");
    if (button) requestAnimationFrame(refresh);
  });
  for (const id of ["product-modal"]) {
    const dialog = document.getElementById(id);
    if (dialog) dialog.addEventListener("close", refresh);
  }
  back.addEventListener("click", () => {
    window.scrollTo({top:0, behavior:reduceMotion ? "instant" : "smooth"});
  });
  refresh();
})();
