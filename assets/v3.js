"use strict";
/* Alghad Digital: sorting and shareable product details; no compare interface. */
(function () {
  const products=Array.isArray(window.AL_GHAD_PRODUCTS)?window.AL_GHAD_PRODUCTS:[];
  const byId=new Map(products.map(p=>[p.id,p]));
  const originalOrder=new Map(products.map((p,i)=>[p.id,i]));
  const search=document.getElementById("search");
  const sorter=document.getElementById("sort-products");
  const modal=document.getElementById("product-modal");
  if (!search||!sorter||!modal) return;
  const published=p=>p.status==="public"&&/^https:\/\/github\.com\/Abdealmalk007\/[A-Za-z0-9._-]+$/.test(p.github||"");
  sorter.addEventListener("change",()=>{
    const mode=sorter.value;
    products.sort((a,b)=>{
      if(mode==="name")return a.title.localeCompare(b.title,"ar");
      if(mode==="published")return Number(published(b))-Number(published(a))||originalOrder.get(a.id)-originalOrder.get(b.id);
      if(mode==="upcoming")return Number(published(a))-Number(published(b))||originalOrder.get(a.id)-originalOrder.get(b.id);
      return originalOrder.get(a.id)-originalOrder.get(b.id);
    });
    search.dispatchEvent(new Event("input",{bubbles:true}));
  });
  document.addEventListener("click",event=>{
    const button=event.target.closest("[data-detail]");
    if(!button||!byId.has(button.dataset.detail))return;
    modal.dataset.currentProduct=button.dataset.detail;
    const url=new URL(location.href);
    url.searchParams.set("app",button.dataset.detail);
    history.replaceState(null,"",url);
  });
  modal.addEventListener("close",()=>{
    delete modal.dataset.currentProduct;
    const url=new URL(location.href);
    if(url.searchParams.has("app")){
      url.searchParams.delete("app");
      history.replaceState(null,"",url);
    }
  });
  window.addEventListener("keydown",event=>{
    if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==="k"){
      event.preventDefault();
      if(!modal.open)search.focus();
    }
    if(event.key==="Escape"&&document.activeElement===search&&search.value){
      search.value="";
      search.dispatchEvent(new Event("input",{bubbles:true}));
    }
  });
  const param=new URL(location.href).searchParams.get("app");
  if(param&&byId.has(param)){
    const ready=()=>document.querySelector('[data-detail="'+param+'"]');
    const button=ready();
    if(button)requestAnimationFrame(()=>button.click());
  }
})();
