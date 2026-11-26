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
  // V7 search is in the header; never force geometry for that case.
  const refresh = () => {
    const modalOpen = !!document.getElementById("product-modal")?.open;
    const searchOpen = document.body.classList.contains("sitewide-search-open");
    const hide = window.scrollY < 650 || modalOpen || searchOpen;
    if (back.hidden !== hide) back.hidden = hide;
    if (!hide) {
      const blockers=document.querySelectorAll(".sitewide-search-trigger:not(.v7-header-search)");
      if (blockers.length) {
        const a=back.getBoundingClientRect();
        for (const blocker of blockers) {
          const b=blocker.getBoundingClientRect(), margin=8;
          if(b.width>0 && b.height>0 && a.left<b.right+margin && a.right+margin>b.left &&
             a.top<b.bottom+margin && a.bottom+margin>b.top) {back.hidden=true;break;}
        }
      }
    }
    scheduled=false;
  };
  const onScroll = () => {
    if(scheduled)return;
    scheduled=true;
    requestAnimationFrame(refresh);
  };
  window.addEventListener("scroll",onScroll,{passive:true});
  window.addEventListener("resize",onScroll,{passive:true});
  window.addEventListener("orientationchange",onScroll,{passive:true});
  new MutationObserver(onScroll).observe(document.body,{attributes:true,attributeFilter:["class"]});
  const dialog=document.getElementById("product-modal");
  if(dialog)new MutationObserver(onScroll).observe(dialog,{attributes:true,attributeFilter:["open"]});
  // Startup uses the generated hidden state; check restored scroll after first paint.
  window.addEventListener("pageshow",()=>requestAnimationFrame(()=>requestAnimationFrame(onScroll)));
  back.addEventListener("click", () => {
    window.scrollTo({top:0, behavior:reduceMotion ? "instant" : "smooth"});
  });
})();
