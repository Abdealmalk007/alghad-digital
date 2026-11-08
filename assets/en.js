"use strict";
(() => {
  const search=document.getElementById("en-search");
  const catalog=document.getElementById("en-catalog");
  if(!search||!catalog)return;
  const cards=[...catalog.querySelectorAll("[data-product]")];
  const buttons=[...document.querySelectorAll("[data-en-filter]")];
  const empty=document.getElementById("en-empty");
  let filter="all";
  const refresh=()=>{
    const query=search.value.toLocaleLowerCase("en").trim();
    let showing=0;
    for(const card of cards){
      const state=card.dataset.category;
      const matchesStatus=filter==="all"||(filter==="public"?state==="public":state==="dev");
      const matchesQuery=!query||card.dataset.search.toLocaleLowerCase("en").includes(query);
      card.hidden=!(matchesStatus&&matchesQuery);
      if(!card.hidden)showing++;
    }
    if(empty)empty.hidden=showing!==0;
  };
  search.addEventListener("input",refresh);
  buttons.forEach(button=>button.addEventListener("click",()=>{
    filter=button.dataset.enFilter;
    for(const el of buttons){
      const active=el===button;
      el.classList.toggle("is-selected",active);
      el.setAttribute("aria-pressed",String(active));
    }
    refresh();
  }));
})();
