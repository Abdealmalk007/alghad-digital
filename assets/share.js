"use strict";
/* Site-wide sharing: no third-party SDKs, no tracking, no external scripts. */
(() => {
  const english = document.documentElement.lang.toLowerCase().startsWith("en");
  const labels = english
    ? {share:"Share", news:"Share news", copy:"Copy link", copied:"Link copied", whats:"WhatsApp", telegram:"Telegram", x:"X", system:"Share on device"}
    : {share:"مشاركة", news:"مشاركة الخبر", copy:"نسخ الرابط", copied:"تم نسخ الرابط", whats:"واتساب", telegram:"تيليجرام", x:"X", system:"مشاركة عبر الجهاز"};
  const base = "https://alghad.digital";
  let active = null;
  let panel = null;
  let status = null;

  function safeUrl(value) {
    if (typeof value !== "string" || !value) return "";
    try {
      const url = new URL(value, document.baseURI);
      if (!["https:","http:"].includes(url.protocol) || url.username || url.password) return "";
      if (url.protocol === "http:" && !["localhost","127.0.0.1"].includes(url.hostname)) return "";
      return url.href;
    } catch (_) { return ""; }
  }
  function create(tag,className,text) {
    const element=document.createElement(tag);
    if (className) element.className=className;
    if (text !== undefined) element.textContent=text;
    return element;
  }
  function titleOf(card,selector) {
    const e=card.querySelector(selector);
    return (e?.textContent||"").trim();
  }
  function meta(card,kind) {
    if (kind==="news") {
      const headline=card.querySelector(".editorial-headline-link,h2 a,h3 a");
      const url=safeUrl(headline?.getAttribute("href"));
      return url ? {url,title:(headline.textContent||"").trim(),news:true}:null;
    }
    const id=card.dataset.id||card.dataset.prerenderProduct||card.dataset.product||card.dataset.prerenderRelease;
    if (id && /^[a-z0-9-]+$/.test(id)) {
      const title=titleOf(card,".card-title,.pre-product-title,h3 a,h3");
      const en=english?"/en":"";
      return {url:base+en+"/programs/"+id+"/",title:title||id,news:false};
    }
    const link=card.querySelector('h2 a[href],h3 a[href]');
    const url=safeUrl(link?.getAttribute("href"));
    return url ? {url,title:(link.textContent||"").trim(),news:false}:null;
  }

  function register(target,details,buttonLabel) {
    if (!target || !details?.url || !details.title || target.querySelector(".alghad-share-button")) return;
    const button=create("button","alghad-share-button",buttonLabel||labels.share);
    button.type="button";
    button.dataset.shareUrl=details.url;
    button.dataset.shareTitle=details.title;
    button.setAttribute("aria-label",(buttonLabel||labels.share)+": "+details.title);
    button.setAttribute("aria-haspopup","true");
    button.setAttribute("aria-expanded","false");
    target.appendChild(button);
  }

  function scan() {
    const cards=document.querySelectorAll(
      ".product-card[data-id],.pre-product-card[data-prerender-product],"+
      ".en-product-card[data-product],.pre-release-card[data-prerender-release],"+
      ".directory-grid:not(.news-grid) .directory-card,.editorial-story,"+
      ".news-article,.en-news-card"
    );
    cards.forEach(card => {
      const isNews=card.matches(".editorial-story,.news-article,.en-news-card");
      const target=isNews
        ?(card.querySelector(".editorial-story-footer")||card)
        :(card.querySelector(".card-actions,.pre-product-actions,.en-product-actions,.pre-release-actions")||card);
      register(target,meta(card,isNews?"news":"program"),isNews?labels.news:labels.share);
    });
    if (/^\/(?:en\/)?programs\/[a-z0-9-]+\/?$/.test(location.pathname)) {
      const detail=document.querySelector(".product-layout .actions,.en-detail-layout .en-actions");
      const title=(document.querySelector(".product-layout h1,.en-detail-layout h1")?.textContent||"").trim();
      if (title) register(detail,{title,url:base+location.pathname,news:false});
    }
    const modal=document.querySelector("#product-modal .modal-actions");
    const productId=document.querySelector("#product-modal")?.dataset.currentProduct;
    if (modal && productId && /^[a-z0-9-]+$/.test(productId)) {
      const name=(document.querySelector("#modal-title")?.textContent||productId).trim();
      register(modal,{title:name,url:base+"/programs/"+productId+"/",news:false});
    }
  }
  function setStatus(text) {
    if (!status) return;
    status.textContent=text;
  }
  function ensurePanel() {
    if (panel) return;
    panel=create("div","alghad-share-panel");
    panel.hidden=true;
    panel.setAttribute("role","group");
    panel.setAttribute("aria-label",english?"Sharing options":"خيارات المشاركة");
    status=create("span","alghad-share-status","");
    status.setAttribute("role","status");
    status.setAttribute("aria-live","polite");
    panel.appendChild(status);
    document.body.appendChild(panel);
  }
  function hidePanel() {
    if (panel) panel.hidden=true;
    if (active) active.setAttribute("aria-expanded","false");
    active=null;
  }
  function shareLink(label,url) {
    const a=create("a","alghad-share-option",label);
    a.href=url;
    a.target="_blank";
    a.rel="noopener noreferrer";
    return a;
  }
  async function copyLink(value) {
    try {
      if (!navigator.clipboard?.writeText) throw Error("Clipboard unavailable");
      await navigator.clipboard.writeText(value);
      setStatus(labels.copied);
    } catch (_) {
      const field=create("textarea","","");
      field.value=value;
      field.setAttribute("readonly","");
      field.style.position="fixed";
      field.style.opacity="0";
      document.body.appendChild(field);
      field.select();
      let succeeded=false;
      try { succeeded=document.execCommand("copy"); } catch (_) {/* fallback below */}
      field.remove();
      if (succeeded) setStatus(labels.copied);
      else window.prompt(english?"Copy this link:":"انسخ هذا الرابط:",value);
    }
  }
  function showPanel(button) {
    ensurePanel();
    if (active===button && !panel.hidden) {hidePanel();return;}
    if (active) active.setAttribute("aria-expanded","false");
    active=button;
    active.setAttribute("aria-expanded","true");
    const title=button.dataset.shareTitle||document.title;
    const url=safeUrl(button.dataset.shareUrl);
    if (!url) {hidePanel();return;}
    const txt=encodeURIComponent(title+" "+url);
    const encodedUrl=encodeURIComponent(url);
    panel.replaceChildren();
    status=create("span","alghad-share-status","");
    status.setAttribute("role","status");
    status.setAttribute("aria-live","polite");
    panel.append(
      shareLink(labels.whats,"https://api.whatsapp.com/send?text="+txt),
      shareLink(labels.telegram,"https://t.me/share/url?url="+encodedUrl+"&text="+encodeURIComponent(title)),
      shareLink(labels.x,"https://twitter.com/intent/tweet?url="+encodedUrl+"&text="+encodeURIComponent(title))
    );
    const copy=create("button","alghad-share-option alghad-share-copy",labels.copy);
    copy.type="button";
    copy.addEventListener("click",()=>copyLink(url));
    panel.append(copy,status);
    panel.hidden=false;
    const rect=button.getBoundingClientRect();
    const width=230;
    const left=Math.min(Math.max(12,rect.left),Math.max(12,innerWidth-width-12));
    panel.style.left=left+"px";
    const expectedHeight=205;
    const bottomAvailable=innerHeight-rect.bottom;
    panel.style.top=(bottomAvailable>expectedHeight?rect.bottom+6:Math.max(8,rect.top-expectedHeight-6))+"px";
    copy.focus({preventScroll:true});
  }
  document.addEventListener("click",async event=>{
    const button=event.target.closest(".alghad-share-button");
    if (!button) {
      if (panel && !panel.hidden && !panel.contains(event.target)) hidePanel();
      return;
    }
    event.preventDefault();
    const url=safeUrl(button.dataset.shareUrl);
    if (!url) return;
    if (typeof navigator.share==="function") {
      try {
        await navigator.share({title:button.dataset.shareTitle,url});
        return;
      } catch (error) {
        if (error?.name==="AbortError") return;
      }
    }
    showPanel(button);
  });
  document.addEventListener("keydown",event=>{
    if (event.key==="Escape" && panel && !panel.hidden) {
      hidePanel();
      event.stopPropagation();
    }
  });
  let queued=false;
  function scheduleScan() {
    if (queued) return;
    queued=true;
    queueMicrotask(()=>{queued=false;scan();});
  }
  scan();
  const observer=new MutationObserver(scheduleScan);
  observer.observe(document.body,{childList:true,subtree:true});
})();
