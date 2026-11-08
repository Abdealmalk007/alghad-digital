"use strict";
/* Alghad Digital v3.5 — Arabic editorial UI; no third-party scripts or news scraping in browsers. */
(() => {
  const newsRoot=document.getElementById("technology-news-grid");
  const toolsRoot=document.getElementById("windows-tools-grid");
  const newsData=window.AL_GHAD_NEWS;
  const toolsData=window.AL_GHAD_TOOLS;
  const dateFormat=new Intl.DateTimeFormat("ar-SA-u-ca-gregory", {year:"numeric",month:"short",day:"numeric",timeZone:"Asia/Riyadh"});
  const NEWS_HOSTS=["aitnews.com","tech-wd.com","arabhardware.net","techvoicearabia.com",
    "technologyarabia.com","3arrafni.com","th3professional.com","aljazeera.net",
    "bbc.com","bbc.co.uk","unlimit-tech.com"];
  const VENDOR_HOSTS=["voidtools.com","ventoy.net","rufus.ie","irfanview.com",
    "file-converter.io","videolan.org","freedownloadmanager.org","github.com"];
  function isAllowed(url,hosts){
    try {
      const u=new URL(url);
      return u.protocol==="https:"&&!u.username&&!u.password&&!u.port&&
        hosts.some(h=>u.hostname===h||u.hostname.endsWith("."+h));
    } catch (_) {return false}
  }
  function node(tag,css,text){
    const el=document.createElement(tag);
    if(css)el.className=css;
    if(text!==undefined)el.textContent=String(text);
    return el;
  }
  function externalLink(label,url,css){
    const a=node("a",css,label);
    a.href=url;a.target="_blank";a.rel="noopener noreferrer";
    return a;
  }
  function localizedDate(value){
    const parsed=new Date(value);
    return Number.isNaN(parsed.getTime())?"":dateFormat.format(parsed);
  }
  function setStatus(id,msg){
    const e=document.getElementById(id);
    if(e)e.textContent=msg;
  }

  const newsItems=Array.isArray(newsData?.articles)
    ?newsData.articles.filter(a=>a&&typeof a.title==="string"&&a.title.length>=12&&
      isAllowed(a.url,NEWS_HOSTS)&&Number.isFinite(Date.parse(a.published_at)))
    :[];
  let selectedNews="الكل",newsVisible=9;
  function makeStory(item,index){
    const card=node("article","editorial-story"+(index===0?" editorial-lead":""));
    const art=node("div","editorial-story-art");
    art.setAttribute("aria-hidden","true");
    const number=node("span","editorial-issue",String(index+1).padStart(2,"0"));
    const symbol=node("span","editorial-symbol",{
      "الذكاء الاصطناعي":"AI","الأمن السيبراني":"<>","الهواتف والأجهزة":"▣",
      "البرامج والإنترنت":"{ }","أخبار التقنية":"✦"
    }[item.category]||"✦");
    art.append(number,symbol,node("span","editorial-art-label","ALGHAD  /  TECH NEWS"));
    const content=node("div","editorial-story-content");
    const meta=node("div","editorial-story-meta");
    meta.append(node("span","editorial-source",item.source_name),node("span","editorial-dot","•"));
    const date=node("time","editorial-date",localizedDate(item.published_at));
    date.dateTime=item.published_at;meta.append(date);
    const headline=node("h3","editorial-headline");
    headline.appendChild(externalLink(item.title,item.url,"editorial-headline-link"));
    const footer=node("div","editorial-story-footer");
    footer.append(node("span","editorial-category",item.category),
      externalLink("اقرأ الخبر من المصدر ↗",item.url,"editorial-read"));
    content.append(meta,headline,footer);
    card.append(art,content);return card;
  }
  const categoryButtons=[...document.querySelectorAll("[data-news-category]")];
  function renderNews(){
    if(!newsRoot)return;
    newsRoot.replaceChildren();
    let data=selectedNews==="الكل"?newsItems:newsItems.filter(item=>item.category===selectedNews);
    if(!data.length){
      newsRoot.appendChild(node("div","editorial-empty","لا توجد أخبار موثقة ضمن هذا التصنيف حاليًا. اختر «الكل» أو تفقّد المصادر الرسمية."));
    }else{
      const frag=document.createDocumentFragment();
      data.slice(0,newsVisible).forEach((item,i)=>frag.appendChild(makeStory(item,i)));
      newsRoot.appendChild(frag);
    }
    categoryButtons.forEach(button=>{
      const on=button.dataset.newsCategory===selectedNews;
      button.classList.toggle("is-selected",on);
      button.setAttribute("aria-pressed",String(on));
    });
    const more=document.getElementById("news-more");
    if(more)more.hidden=data.length<=newsVisible;
    setStatus("news-count-label",newsItems.length+" عنوانًا من مصادر مستقلة");
  }
  categoryButtons.forEach(button=>button.addEventListener("click",()=>{
    selectedNews=button.dataset.newsCategory||"الكل";newsVisible=9;renderNews();
  }));
  const moreNews=document.getElementById("news-more");
  if(moreNews)moreNews.addEventListener("click",()=>{newsVisible+=9;renderNews();});
  if(newsRoot)renderNews();

  if(newsData?.generated_at){
    setStatus("news-last-updated","آخر تحديث للمصادر: "+localizedDate(newsData.generated_at));
    const stale=(Date.now()-Date.parse(newsData.generated_at)>36*3600*1000);
    const badge=document.getElementById("news-freshness");
    if(badge){badge.textContent=stale?"التحديث متأخر — راجع المصدر":"تحديث آلي";badge.classList.toggle("is-stale",stale);}
  }else setStatus("news-last-updated","تحديث الأخبار غير متاح حاليًا");

  // A newsroom source directory includes publishers that do not allow RSS fetches.
  // A directory link never implies that articles were fetched from that publisher.
  const additional=[
    ["العربية — التقنية","https://www.alarabiya.net/technology"],
    ["الشرق للأخبار","https://asharq.com/technology/"],
    ["أراجيك تك","https://www.arageek.com/tech"]
  ];
  const sourcesRoot=document.getElementById("news-source-links");
  if(sourcesRoot){
    const all=(Array.isArray(newsData?.sources)?newsData.sources:[])
      .map(source=>[source.name,source.url]).filter(item=>isAllowed(item[1],NEWS_HOSTS));
    [...all,...additional].forEach(item=>{
      const anchor=externalLink(item[0]+" ↗",item[1],"source-directory-link");
      sourcesRoot.appendChild(anchor);
    });
  }

  const tools=Array.isArray(toolsData?.items)
    ?toolsData.items.filter(x=>x&&typeof x.name==="string"&&isAllowed(x.url,VENDOR_HOSTS)
      &&/^assets\/tools\/[a-z0-9-]+\.svg$/.test(x.image))
    :[];
  let activeGroup="الكل";
  let search="";
  const toolsFilters=[...document.querySelectorAll("[data-tool-category]")];
  function makeTool(tool,i){
    const article=node("article","windows-tool-card");
    const imgLink=externalLink("",tool.url,"windows-tool-picture");
    const img=document.createElement("img");
    img.src=tool.image;img.alt="رسم توضيحي لأداة "+tool.name;
    img.loading="lazy";img.decoding="async";img.width=960;img.height=540;
    imgLink.appendChild(img);
    const body=node("div","windows-tool-body");
    const eyebrow=node("div","windows-tool-eyebrow");
    eyebrow.append(node("span","windows-tool-num",String(i+1).padStart(2,"0")),
      node("span","windows-tool-category",tool.category));
    body.append(eyebrow,node("h3","windows-tool-title",tool.name),
      node("p","windows-tool-description",tool.description));
    const list=node("ul","windows-tool-features");
    (tool.features||[]).slice(0,3).forEach(feature=>list.appendChild(node("li","",feature)));
    body.appendChild(list);
    const foot=node("div","windows-tool-footer");
    foot.append(node("span","windows-license",tool.license),
      externalLink("الموقع والتحميل الرسمي ↗",tool.url,"windows-tool-button"));
    body.appendChild(foot);
    article.append(imgLink,body);return article;
  }
  function renderTools(){
    if(!toolsRoot)return;
    const values=tools.filter(t=>(activeGroup==="الكل"||t.category===activeGroup)&&
      (!search||[t.name,t.english,t.description,t.category,...(t.features||[])].join(" ").toLocaleLowerCase().includes(search)));
    toolsRoot.replaceChildren();
    if(values.length){
      const frag=document.createDocumentFragment();
      values.forEach((tool,i)=>frag.appendChild(makeTool(tool,i)));
      toolsRoot.appendChild(frag);
    }else toolsRoot.appendChild(node("div","editorial-empty","لا توجد برامج تطابق البحث. جرّب اسمًا آخر أو اختر «الكل»."));
    setStatus("windows-tools-count",values.length+" من "+tools.length+" أدوات");
    toolsFilters.forEach(button=>{
      const on=button.dataset.toolCategory===activeGroup;
      button.classList.toggle("is-selected",on);
      button.setAttribute("aria-pressed",String(on));
    });
  }
  toolsFilters.forEach(button=>button.addEventListener("click",()=>{
    activeGroup=button.dataset.toolCategory||"الكل";
    renderTools();
  }));
  const searchInput=document.getElementById("windows-tools-search");
  if(searchInput)searchInput.addEventListener("input",()=>{
    search=searchInput.value.trim().toLocaleLowerCase();
    renderTools();
  });
  if(toolsRoot)renderTools();
})();
