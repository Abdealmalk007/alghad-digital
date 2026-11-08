"use strict";
/* Three attributed official newsrooms. No third-party JavaScript, HTML injection,
 * tracking or client-side scraping. News comes from a prevalidated daily snapshot. */
(() => {
  const snap=window.AL_GHAD_INDUSTRY_NEWS;
  const roots=[...document.querySelectorAll("[data-industry-topic]")];
  const hosts=["openai.com","blog.google","nvidia.com","amd.com","apple.com","samsung.com",
    "microsoft.com","toyota.com","global.toyota","hondanews.eu","porsche.com",
    "subaru.co.jp","anthropic.com","deepseek.com","huawei.com","tesla.com",
    "bmwgroup.com","mercedes-benz.com","hyundai.com","kiamedia.com"];
  const formatter=new Intl.DateTimeFormat("ar-SA-u-ca-gregory",{
    year:"numeric",month:"short",day:"numeric",timeZone:"Asia/Riyadh"});
  const allowed=url=>{
    try{
      const parsed=new URL(url);
      return parsed.protocol==="https:"&&!parsed.username&&!parsed.password&&!parsed.port&&
        hosts.some(host=>parsed.hostname===host||parsed.hostname.endsWith("."+host));
    }catch(_){return false;}
  };
  const elt=(tag,className,value)=>{
    const e=document.createElement(tag);
    if(className)e.className=className;
    if(value!==undefined)e.textContent=String(value);
    return e;
  };
  const link=(label,url,className)=>{
    const a=elt("a",className,label);
    a.href=url;a.target="_blank";a.rel="noopener noreferrer";
    return a;
  };
  const stamp=value=>{
    const date=new Date(value);
    return Number.isNaN(date.getTime())?"":formatter.format(date);
  };
  for(const root of roots){
    const topic=root.dataset.industryTopic;
    const listing=root.querySelector("[data-industry-list]");
    const sources=root.querySelector("[data-industry-sources]");
    const summary=root.querySelector("[data-industry-count]");
    const updated=root.querySelector("[data-industry-updated]");
    const more=root.querySelector("[data-industry-more]");
    const info=snap?.topics?.[topic];
    const articles=Array.isArray(info?.articles)?info.articles.filter(x=>
      x&&x.topic===topic&&x.official===true&&typeof x.title==="string"&&
      x.title.length>=12&&allowed(x.url)&&Number.isFinite(Date.parse(x.published_at))):[];
    let visible=6;
    const createCard=(entry,index)=>{
      const article=elt("article","industry-story");
      const head=elt("div","industry-story-top");
      head.append(elt("span","industry-story-counter",String(index+1).padStart(2,"0")),
        elt("span","industry-story-source",entry.source_name),
        elt("span","industry-verified","مصدر رسمي"));
      const title=elt("h3","industry-story-title");
      const translated=entry.translation_status==="machine" &&
        typeof entry.title_ar==="string" && entry.title_ar.length>=4;
      const translatedTitle=translated?entry.title_ar:entry.title;
      const a=link(translatedTitle,entry.url,"industry-title-link");
      a.dir=translated?"rtl":"auto";
      a.lang=translated?"ar":entry.language==="en"?"en":"ar";
      title.appendChild(a);
      if(translated){
        const original=elt("span","industry-original-headline",entry.title);
        original.lang="en";original.dir="ltr";
        title.appendChild(original);
        title.appendChild(elt("span","industry-machine-note","ترجمة آلية · العنوان الأصلي معروض للمراجعة"));
      }else if(entry.translation_status==="unavailable"){
        title.appendChild(elt("span","industry-machine-note","الترجمة العربية غير متاحة حاليًا"));
      }
      const footer=elt("div","industry-story-bottom");
      const date=elt("time","industry-time",stamp(entry.published_at));
      date.dateTime=entry.published_at;
      footer.append(date,link("قراءة الخبر الأصلي ↗",entry.url,"industry-story-link"));
      article.append(head,title,footer);
      return article;
    };
    const render=()=>{
      if(!listing)return;
      listing.replaceChildren();
      if(!articles.length){
        listing.appendChild(elt("p","industry-empty","لا تتوفر عناوين حديثة موثقة حاليًا. يمكنك زيارة المصادر الرسمية أدناه."));
      }else{
        const frag=document.createDocumentFragment();
        articles.slice(0,visible).forEach((item,i)=>frag.appendChild(createCard(item,i)));
        listing.appendChild(frag);
      }
      if(more)more.hidden=visible>=articles.length;
    };
    if(more)more.addEventListener("click",()=>{visible+=6;render();});
    render();
    if(summary)summary.textContent=articles.length+" خبرًا من المصادر الرسمية";
    if(updated){
      const old=Date.now()-Date.parse(snap?.generated_at||"");
      updated.textContent=Number.isFinite(old) ?
        "آخر فحص للمصادر: "+stamp(snap.generated_at)+(old>36*3600*1000?" — التحديث متأخر":""):
        "لا تتوفر بيانات تحديث موثقة";
    }
    if(sources){
      sources.replaceChildren();
      const trustedSources=Array.isArray(snap?.sources)?snap.sources:[];
      const frag=document.createDocumentFragment();
      for(const source of trustedSources.filter(src=>src.topics?.includes(topic))){
        if(!allowed(source.url))continue;
        const a=link(source.name+" ↗",source.url,
          "industry-source-link"+(!source.feed_available?" is-directory-only":""));
        if(!source.feed_available){
          a.title="رابط رسمي للمتابعة؛ لا تتوفر خلاصة أخبار متحقّق منها لهذا المصدر";
        }else{
          a.title="الأخبار مستمدة من خلاصة RSS رسمية متحقّق منها";
        }
        frag.appendChild(a);
      }
      sources.appendChild(frag);
    }
  }
})();
