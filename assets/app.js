"use strict";
/* Alghad Digital v2 — static, secure, responsive product catalog */
(function () {
  const data = Array.isArray(window.AL_GHAD_PRODUCTS) ? window.AL_GHAD_PRODUCTS : [];
  const get = id => document.getElementById(id);
  const catalog = get("catalog");
  const search = get("search");
  const filters = get("filters");
  const modal = get("product-modal");
  const modalBody = get("modal-body");
  const modalClose = get("modal-close");
  const menu = get("nav");
  const menuToggle = get("menu-toggle");
  const featured = get("featured-cards");
  const statusNames = {public: "مكتمل", dev: "قريبًا جدًا"};
  let filter = "all";
  let lastFocus = null;

  const escapeHtml = value => String(value == null ? "" : value).replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
  const tx = escapeHtml;
  const urlFor = value => {
    if (typeof value !== "string") return "";
    try {
      const url = new URL(value);
      return url.protocol === "https:" &&
        url.hostname === "github.com" &&
        /^\/Abdealmalk007\/[a-zA-Z0-9._-]+(?:\/releases(?:\/tag\/[a-zA-Z0-9._-]+)?)?$/.test(url.pathname)
        ? value : "";
    } catch (_) { return ""; }
  };
  const isComplete = p => p.status === "public" && !!urlFor(p.github);
  const releases = window.AL_GHAD_DOWNLOADS || {};
  const publicPreview = p => {
    const item = releases[p.id];
    return p.status==="public" && item?.channel==="preview" &&
      Array.isArray(item.files) && item.files.some(f=>f.recommended &&
        typeof f.url==="string" &&
        f.url.startsWith("https://github.com/Abdealmalk007/"+item.repository+"/releases/download/"));
  };
  const readinessText = p => p.id==="stone" ? (publicPreview(p) ? "Preview · مثبت غير موقّع" : "المصدر متاح · المثبت قيد التوقيع") : publicPreview(p) ? "Beta · نسخة تجريبية" :
    isComplete(p) ? "مستودع منشور" : "قريبًا";
  const tag = p => '<span class="status ' + (isComplete(p) ? 'status-public' : 'status-dev') +
    '"><span class="status-dot" aria-hidden="true"></span>' + readinessText(p) + "</span>";
  const previewFor = p => {
    const path = String(p.preview || "");
    return /^assets\/previews\/[a-z0-9_-]+\.svg$/.test(path) ? path : "favicon.svg";
  };
  const label = p => tx(p.previewAlt || ("صورة توضيحية لبرنامج " + p.title));
  const searchable = p => [p.title,p.english,p.category,p.description,p.keywords,p.version,p.summary,p.features.join(" ")].concat(p.platforms).join(" ").toLocaleLowerCase();
  const matches = (p, term) => {
    const inGroup = filter === "all" ||
      filter === "public" && isComplete(p) ||
      filter === "dev" && !isComplete(p) ||
      filter === "windows" && p.platforms.includes("Windows") ||
      filter === "android" && p.platforms.some(x => x.startsWith("Android"));
    return inGroup && (!term || searchable(p).includes(term));
  };
  function card(p, index) {
    const gh = urlFor(p.github);
    const chips = p.features.slice(0, 2).map(feature => '<li>' + tx(feature) + "</li>").join("");
    return [
      '<article class="product-card neo-card" data-id="', tx(p.id),'" style="--item-index:', index, '">',
      '<div class="card-cover"><img class="card-preview" src="',previewFor(p),'" alt="',label(p),'" loading="lazy" decoding="async" width="960" height="540">',
      '<span class="image-disclaimer">تصميم توضيحي</span><span class="card-top-badge">',tag(p),'</span></div>',
      '<div class="card-main"><div class="card-serial"><span>ALGHAD / ',tx(p.english),'</span><span class="card-serial-number">',String(index+1).padStart(2,"0"),'</span></div>',
      '<span class="card-category">',tx(p.category),'</span>',
      '<h3 class="card-title">',tx(p.title),'</h3><p class="card-description">',tx(p.description),'</p>',
      '<ul class="card-highlights">',chips,'</ul>',
      '<div class="card-meta">',p.platforms.map(x=>'<span class="meta-chip" dir="auto">'+tx(x)+'</span>').join(""),
      '<span class="meta-chip">',tx(p.version==="—"?"قيد التحديد":"v"+p.version),'</span></div></div>',
      '<div class="card-actions"><button class="card-detail" type="button" data-detail="',tx(p.id),'" aria-label="تفاصيل ',tx(p.title),'">اكتشف البرنامج <span aria-hidden="true">↗</span></button>',
      gh ? '<a class="card-link" href="'+gh+'" target="_blank" rel="noopener noreferrer" aria-label="مستودع GitHub لـ '+tx(p.title)+'">GitHub <span aria-hidden="true">↗</span></a>' :
        '<span class="card-unavailable">الإطلاق قريبًا</span>',
      p.id==="stone" ? '<a class="card-link stone-source-download" href="https://github.com/Abdealmalk007/ProTechStoneManager/archive/refs/heads/main.zip" target="_blank" rel="noopener noreferrer">↓ تنزيل المصدر ZIP</a>' : '',
      '</div></article>'
    ].join("");
  }
  function render() {
    const term=(search.value||"").trim().toLocaleLowerCase();
    const subset=data.filter(p=>matches(p,term));
    catalog.innerHTML=subset.map(card).join("");
    get("visible-count").textContent=subset.length.toLocaleString("ar-SA");
    get("empty-state").hidden=subset.length>0;
  }
  function openDetails(id) {
    const p=data.find(item=>item.id===id);
    if(!p)return;
    lastFocus=document.activeElement;
    const gh=urlFor(p.github);
    const release=urlFor(p.release);
    modalBody.innerHTML=[
      '<div class="modal-hero"><img src="',previewFor(p),'" alt="',label(p),'" width="960" height="540"><span class="modal-image-note">صورة توضيحية للتصميم</span></div>',
      '<div class="modal-content"><div class="modal-breadcrumb"><span>ALGHAD DIGITAL</span><span>/</span><span>',tx(p.category),'</span></div>',
      '<div class="modal-heading"><div><h2 id="modal-title">',tx(p.title),'</h2><p>',tx(p.summary || p.description),'</p></div>',tag(p),'</div>',
      '<p class="modal-description">',tx(p.details),'</p>',
      '<h3 class="modal-section-title">المميزات والخصائص</h3><ul class="modal-features">',
      p.features.map(feature=>'<li><span aria-hidden="true">✓</span>'+tx(feature)+'</li>').join(""),'</ul>',
      '<div class="modal-facts"><span>المنصة: ',tx(p.platforms.join(" / ")),'</span><span>الإصدار: ',tx(p.version),'</span><span>',isComplete(p)?"المصدر منشور على GitHub":"الإطلاق قريبًا جدًا",'</span></div>',
      '<div class="modal-actions">',
      gh?'<a class="button button-primary" href="'+gh+'" target="_blank" rel="noopener noreferrer">زيارة مستودع GitHub ↗</a>':'',
      release?'<a class="button button-secondary" href="'+release+'" target="_blank" rel="noopener noreferrer">استعراض الإصدار المنشور ↗</a>':'',
      '<button class="button button-secondary" id="modal-back" type="button">العودة للبرامج</button>',
      '</div><p class="modal-disclaimer">',
      isComplete(p)?
        'تعني علامة «مكتمل» اكتمال رفع المشروع إلى GitHub، وليس اجتياز جميع اختبارات الإنتاج. تحقق من تعليمات الإصدار قبل التثبيت.' :
        'هذا المشروع قيد التطوير ولم يُنشر مستودعه العام بعد.',
      '</p></div>'
    ].join("");
    get("modal-back").addEventListener("click",closeDetails);
    if(typeof modal.showModal==="function")modal.showModal();
    else modal.setAttribute("open","");
    modalClose.focus();
  }
  function closeDetails() {
    if(typeof modal.close==="function")modal.close();
    else modal.removeAttribute("open");
    if(lastFocus&&document.contains(lastFocus)&&typeof lastFocus.focus==="function")lastFocus.focus();
  }
  function renderFeatured(){
    if(!featured)return;
    const ids=["kitchen","stone","download"];
    featured.innerHTML=ids.map((id,index)=>{
      const p=data.find(x=>x.id===id);
      if(!p)return "";
      return '<button class="spotlight-card spotlight-'+tx(id)+'" type="button" data-detail="'+tx(id)+'" aria-label="استعرض '+tx(p.title)+'">'+
        '<span class="spotlight-art"><img src="'+previewFor(p)+'" alt="'+label(p)+'" loading="'+(index?"lazy":"eager")+'" width="960" height="540"></span>'+
        '<span class="spotlight-text"><span class="spotlight-index">0'+(index+1)+' / SELECTED WORK</span>'+
        '<span class="spotlight-name">'+tx(p.title)+'</span>'+
        '<span class="spotlight-sub">'+tx(p.summary||p.description)+'</span>'+
        '<span class="spotlight-open"><span>'+ (publicPreview(p)?"نسخة Beta للتجربة":isComplete(p)?"مستودع منشور":"قريبًا") +'</span><span aria-hidden="true">↗</span></span></span></button>';
    }).join("");
  }
  document.addEventListener("click",event=>{
    const target=event.target.closest("[data-detail]");
    if(target)openDetails(target.dataset.detail);
  });
  modalClose.addEventListener("click",closeDetails);
  modal.addEventListener("click",event=>{if(event.target===modal)closeDetails();});
  modal.addEventListener("close",()=>{
    if(lastFocus&&document.contains(lastFocus))lastFocus.focus();
  });
  search.addEventListener("input",render);
  filters.addEventListener("click",event=>{
    const button=event.target.closest("[data-filter]");
    if(!button)return;
    filter=button.dataset.filter;
    filters.querySelectorAll("[data-filter]").forEach(item=>{
      const active=item===button;
      item.classList.toggle("active",active);
      item.setAttribute("aria-pressed",String(active));
    });
    render();
  });
  get("reset-filters").addEventListener("click",()=>{
    search.value="";
    filters.querySelector('[data-filter="all"]').click();
    search.focus();
  });
  document.addEventListener("keydown",event=>{
    if(event.key!=="/"||event.ctrlKey||event.altKey||event.metaKey||modal.open)return;
    if(["INPUT","TEXTAREA"].includes(document.activeElement.tagName)||document.activeElement.isContentEditable)return;
    event.preventDefault();search.focus();
  });
  menuToggle.addEventListener("click",()=>{
    const opened=menu.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded",String(opened));
  });
  menu.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>{
    menu.classList.remove("open");
    menuToggle.setAttribute("aria-expanded","false");
  }));
  const toggle=get("theme-toggle");
  function setTheme(value) {
    document.documentElement.dataset.theme=value;
    toggle.setAttribute("aria-label",value==="dark"?"تفعيل المظهر الفاتح":"تفعيل المظهر الداكن");
    try{localStorage.setItem("alghad-theme",value);}catch(_){}
  }
  let theme="dark";
  try{theme=localStorage.getItem("alghad-theme")==="light"?"light":"dark";}catch(_){}
  setTheme(theme);
  toggle.addEventListener("click",()=>setTheme(document.documentElement.dataset.theme==="dark"?"light":"dark"));
  get("year").textContent=new Date().getFullYear();
  get("stat-apps").textContent=String(data.length).padStart(2,"0");
  get("stat-github").textContent=String(data.filter(isComplete).length).padStart(2,"0");
  const upcoming=get("stat-upcoming");
  if(upcoming)upcoming.textContent=String(data.filter(p=>!isComplete(p)).length).padStart(2,"0");
  renderFeatured();
  render();
})();