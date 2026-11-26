/* Alghad Digital first-party sitewide search (Arabic and English). */
(function () {
  "use strict";
  if (window.__alghadSiteSearchMounted) return;
  window.__alghadSiteSearchMounted = true;

  function mount() {
    var isEn = /^en/i.test(document.documentElement.lang || "");
    var L = isEn ? {
      open: "Search the site", title: "Search all of Alghad Digital",
      placeholder: "Find software, Windows, Office, news, guides, features…",
      all: "Everything", program: "Software", news: "News", page: "Pages",
      close: "Close search", loading: "Loading site search…",
      empty: "Enter at least two characters to search the website.",
      none: "No matching results. Try another word.",
      failed: "Could not load the site index. Please try again.",
      found: " results", more: "Show more", footer: "Site search · Software, headlines and pages",
      source: "Source", programLabel: "Software", newsLabel: "News", pageLabel: "Page"
    } : {
      open: "بحث في الموقع", title: "ابحث في جميع محتويات الغد الرقمي",
      placeholder: "اكتب بالعربية أو الإنجليزية: البرامج، الأخبار، الأدلة، الميزات…",
      all: "الكل", program: "البرامج", news: "الأخبار", page: "صفحات الموقع",
      close: "إغلاق البحث", loading: "جارٍ تحميل فهرس البحث…",
      empty: "اكتب حرفين على الأقل للبحث في جميع محتويات الموقع.",
      none: "لا توجد نتائج مطابقة. جرّب عبارة أخرى.",
      failed: "تعذر تحميل فهرس البحث، حاول مرة أخرى.",
      found: " نتيجة", more: "عرض المزيد", footer: "بحث داخلي · البرامج والأخبار والصفحات",
      source: "المصدر", programLabel: "برنامج", newsLabel: "خبر", pageLabel: "صفحة"
    };

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.id = "sitewide-search-trigger";
    trigger.className = "sitewide-search-trigger";
    trigger.setAttribute("aria-label", L.open);
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-controls", "sitewide-search-dialog");
    trigger.setAttribute("aria-keyshortcuts", "Control+K Meta+K");
    trigger.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><path d="m16.5 16.5 4 4"></path></svg>';
    trigger.append(document.createTextNode(L.open));

    var layer = document.createElement("div");
    layer.className = "sitewide-search-layer";
    layer.id = "sitewide-search-layer";
    layer.hidden = true;
    layer.dir = isEn ? "ltr" : "rtl";
    layer.innerHTML = [
      '<section id="sitewide-search-dialog" class="sitewide-search-dialog" role="dialog" aria-modal="true" aria-labelledby="sitewide-search-title">',
      '<div class="sitewide-search-top"><h2 id="sitewide-search-title" class="sitewide-search-title"></h2>',
      '<button class="sitewide-search-close" type="button"></button></div>',
      '<div class="sitewide-search-searchbox"><input class="sitewide-search-input" type="search" autocomplete="off" spellcheck="false" enterkeyhint="search"/></div>',
      '<div class="sitewide-search-quick" role="group"></div>',
      '<div class="sitewide-search-filters" role="group"></div>',
      '<p class="sitewide-search-count" role="status" aria-live="polite"></p>',
      '<div class="sitewide-search-results"><ul class="sitewide-search-list"></ul>',
      '<button class="sitewide-search-more" type="button" hidden></button></div>',
      '<div class="sitewide-search-footer"></div>',
      '</section>'
    ].join("");

    var input = layer.querySelector(".sitewide-search-input");
    var closeButton = layer.querySelector(".sitewide-search-close");
    var tabs = layer.querySelector(".sitewide-search-filters");
    var quick = layer.querySelector(".sitewide-search-quick");
    var count = layer.querySelector(".sitewide-search-count");
    var list = layer.querySelector(".sitewide-search-list");
    var more = layer.querySelector(".sitewide-search-more");
    layer.querySelector(".sitewide-search-title").textContent = L.title;
    closeButton.setAttribute("aria-label", L.close);
    closeButton.textContent = "\u00d7";
    input.placeholder = L.placeholder;
    input.setAttribute("aria-label", L.title);
    layer.querySelector(".sitewide-search-footer").textContent = L.footer;
    more.textContent = L.more;
    tabs.setAttribute("aria-label", isEn ? "Result type" : "نوع النتائج");
    quick.setAttribute("aria-label", isEn ? "Suggested bilingual searches" : "اقتراحات للبحث بالعربية والإنجليزية");

    var active = "all", dataPromise = null, cache = null;
    var matches = [], limit = 20, previousFocus = null, debounce = null;
    var kinds = [["all",L.all],["program",L.program],["news",L.news],["page",L.page]];

    function normalize(value) {
      return String(value || "").normalize("NFKD")
        .replace(/[\u0300-\u036f\u064B-\u065F\u0670\u0640\u200B-\u200F]/g, "")
        .replace(/[إأآٱ]/g,"ا").replace(/ى/g,"ي").replace(/ة/g,"ه")
        .replace(/[٠-٩]/g, function (digit) {return String(digit.charCodeAt(0)-0x0660);})
        .replace(/[۰-۹]/g, function (digit) {return String(digit.charCodeAt(0)-0x06f0);})
        .toLowerCase().replace(/\s+/g," ").trim();
    }
    // Curated search equivalents; not a machine translation service.
    // Each group matches *either* language against the indexed bilingual pages.
    var synonymGroups = [
      ["windows","ويندوز","وندوز"],
      ["office","اوفيس","اوفيس365"],
      ["download","downloads","تحميل","تنزيل"],
      ["excel","اكسل","xlsx","xls","spreadsheets","جداول"],
      ["quotation","quotations","quotes","اسعار","عروض"],
      ["contract","contracts","عقود","عقد"],
      ["customer","customers","عملاء","عميل"],
      ["privacy","خصوصيه","الخصوصيه"],
      ["security","امن","امان","حمايه"],
      ["news","اخبار"],
      ["ai","artificial","intelligence","ذكاء","الذكاء","اصطناعي"],
      ["cars","car","سيارات","سياره"],
      ["kitchen","مطابخ","مطبخ"],
      ["stone","marble","رخام","porcelain","بورسلان"],
      ["hr","human","resources","موظفين","موظف"],
      ["payroll","رواتب","راتب"],
      ["report","reports","تقارير","تقرير"],
      ["portable","محمول","بدون","تثبيت"],
      ["setup","installer","مثبت","تثبيت"],
      ["3d","ثلاثي","ثلاثيه"],
      ["pdf","بي","دي","اف"]
    ];
    var equivalent = Object.create(null);
    synonymGroups.forEach(function (group) {
      var normalized = group.map(normalize);
      normalized.forEach(function (word) {equivalent[word] = normalized;});
    });
    function alternatives(token) {
      return equivalent[token] || [token];
    }
    function hasTerm(field,term) {
      if (!field || !term) return false;
      if (/^[a-z0-9]{1,2}$/.test(term)) {
        return (" "+field.replace(/[^a-z0-9]+/g," ")+" ").includes(" "+term+" ");
      }
      return field.includes(term);
    }
    function includesAny(field,terms) {
      return terms.some(function (word) {return hasTerm(field,word);});
    }
    function prepare(records) {
      return records.map(function (entry) {
        return Object.assign({}, entry, {
          keyTitle: normalize(entry.title),
          keyDesc: normalize(entry.description),
          keyBody: normalize([entry.content,entry.category,entry.source].join(" ")),
          keyAliases: normalize(entry.aliases)
        });
      });
    }
    function loadIndex() {
      if (cache) return Promise.resolve(cache);
      if (dataPromise) return dataPromise;
      dataPromise = new Promise(function (resolve,reject) {
        if (window.AL_GHAD_SITE_SEARCH && window.AL_GHAD_SITE_SEARCH.schema===1 &&
            Array.isArray(window.AL_GHAD_SITE_SEARCH.records)) {
          cache=prepare(window.AL_GHAD_SITE_SEARCH.records);
          resolve(cache); return;
        }
        var s=document.createElement("script");
        s.src="/assets/site-search-index.js?v="+new Date().toISOString().slice(0,13);
        s.async=true;
        s.onload=function () {
          var data=window.AL_GHAD_SITE_SEARCH;
          if (!data || data.schema!==1 || !Array.isArray(data.records) || data.records.length<20) {
            reject(new Error("Invalid first-party index"));return;
          }
          cache=prepare(data.records);resolve(cache);
        };
        s.onerror=function () {reject(new Error("Unable to download search index"));};
        document.head.append(s);
      }).catch(function (error) {dataPromise=null;throw error;});
      return dataPromise;
    }
    function highlight(element,value,query) {
      var source=String(value||""), term=String(query||"").trim();
      var start=term.length>1 ? source.toLocaleLowerCase().indexOf(term.toLocaleLowerCase()) : -1;
      if (start<0) {element.textContent=source;return;}
      element.append(document.createTextNode(source.slice(0,start)));
      var mark=document.createElement("mark");
      mark.textContent=source.slice(start,start+term.length);
      element.append(mark,document.createTextNode(source.slice(start+term.length)));
    }
    function message(value) {
      list.replaceChildren();
      var p=document.createElement("p");
      p.className="sitewide-search-empty";p.textContent=value;
      list.append(p);more.hidden=true;
    }
    function score(item,groups,phrase) {
      var fields=[item.keyTitle,item.keyDesc,item.keyBody,item.keyAliases];
      if (!groups.every(function (terms) {
        return fields.some(function (field) {return includesAny(field,terms);});
      })) return -1;
      var n=0;
      if (item.keyTitle===phrase) n+=130;
      else if (item.keyTitle.includes(phrase)) n+=90;
      if (item.keyDesc.includes(phrase)) n+=35;
      groups.forEach(function (terms) {
        if (includesAny(item.keyTitle,terms)) n+=30;
        if (includesAny(item.keyDesc,terms)) n+=15;
        if (includesAny(item.keyBody,terms)) n+=6;
        if (includesAny(item.keyAliases,terms)) n+=5;
      });
      if (item.kind==="program") n+=8;
      if (item.kind==="news") n+=3;
      if (item.lang===(isEn?"en":"ar")) n+=12;
      return n;
    }
    function render() {
      list.replaceChildren();
      count.textContent=isEn ? String(matches.length)+L.found : String(matches.length)+L.found;
      if (!matches.length) {message(L.none);return;}
      matches.slice(0,limit).forEach(function (item) {
        var li=document.createElement("li");
        li.className="sitewide-search-result";
        var card=document.createElement("article");
        card.className="sitewide-search-card";
        var meta=document.createElement("p");
        meta.className="sitewide-search-meta";
        var type=item.kind==="program"?L.programLabel:item.kind==="news"?L.newsLabel:L.pageLabel;
        meta.textContent=type+" \u00b7 "+(item.category||"")+
          (item.source?" \u00b7 "+L.source+": "+item.source:"")+
          (item.date?" \u00b7 "+item.date:"");
        var link=document.createElement("a");
        var href=item.url;
        if (isEn && item.kind==="news" && !href.startsWith("/en/")) href="/en"+href;
        // The published index only contains first-party paths.
        if (!/^\/(?:[a-z0-9-]+\/)*$/i.test(href)) return;
        link.href=href;
        highlight(link,item.title,input.value);
        var description=document.createElement("p");
        description.className="sitewide-search-summary";
        var text=String(item.description||item.content||"");
        description.textContent=text.length>205?text.slice(0,205).trimEnd()+"\u2026":text;
        card.append(meta,link,description);li.append(card);list.append(li);
      });
      more.hidden=matches.length<=limit;
    }
    function calculate() {
      if (!cache) return;
      var q=normalize(input.value);limit=20;
      if (q.length<2) {matches=[];count.textContent="";message(L.empty);return;}
      var tokens=Array.from(new Set(q.split(" ").filter(Boolean))).slice(0,12);
      var groups=tokens.map(alternatives);
      matches=cache.filter(function (item) {
          return active==="all" || item.kind===active;
        }).map(function (item) {
          return {item:item,value:score(item,groups,q)};
        }).filter(function (entry) {
          return entry.value>=0;
        }).sort(function (a,b) {
          return b.value-a.value||(b.item.date||"").localeCompare(a.item.date||"");
        }).map(function (entry) {return entry.item;});
      render();
    }
    function selectKind(kind) {
      active=kind;
      tabs.querySelectorAll("button").forEach(function (button) {
        button.setAttribute("aria-pressed",String(button.dataset.kind===kind));
      });
      calculate();
    }
    var examples=isEn
      ? [["Windows ISO","windows"],["Excel analysis","excel"],["AI news","ai"],["Contracts","contracts"]]
      : [["ملفات Windows ISO","ويندوز"],["تحليل Excel","اكسل"],["أخبار الذكاء الاصطناعي","ذكاء"],["عروض الأسعار والعقود","عقود"]];
    examples.forEach(function (pair) {
      var button=document.createElement("button");
      button.type="button";button.className="sitewide-search-example";
      button.textContent=pair[0];
      button.addEventListener("click",function () {
        input.value=pair[1];active="all";
        tabs.querySelectorAll("button").forEach(function (b) {
          b.setAttribute("aria-pressed",String(b.dataset.kind==="all"));
        });
        input.focus();calculate();
      });
      quick.append(button);
    });
    kinds.forEach(function (pair) {
      var btn=document.createElement("button");
      btn.type="button";btn.dataset.kind=pair[0];btn.className="sitewide-search-filter";
      btn.textContent=pair[1];btn.setAttribute("aria-pressed",String(pair[0]==="all"));
      btn.addEventListener("click",function () {selectKind(pair[0]);});
      tabs.append(btn);
    });
    function open() {
      if (!layer.hidden) return;
      previousFocus=document.activeElement;
      layer.hidden=false;trigger.setAttribute("aria-expanded","true");document.body.classList.add("sitewide-search-open");
      count.textContent=L.loading;message(L.loading);input.focus();
      loadIndex().then(calculate).catch(function (error) {
        console.error("Alghad search:",error);
        count.textContent="";message(L.failed);
      });
    }
    function close() {
      if (layer.hidden) return;
      layer.hidden=true;trigger.setAttribute("aria-expanded","false");document.body.classList.remove("sitewide-search-open");
      if (previousFocus && previousFocus.isConnected && typeof previousFocus.focus==="function") previousFocus.focus({preventScroll:true});
      else trigger.focus({preventScroll:true});
    }
    trigger.addEventListener("click",open);
    closeButton.addEventListener("click",close);
    layer.addEventListener("click",function (e) {if(e.target===layer)close();});
    input.addEventListener("input",function () {
      clearTimeout(debounce);
      debounce=setTimeout(calculate,80);
    });
    input.addEventListener("keydown",function(e) {
      if (e.key==="Enter" && matches.length) {
        var first=list.querySelector("a[href]");
        if (first) {e.preventDefault();first.click();}
      }
    });
    more.addEventListener("click",function () {limit+=20;render();});
    document.addEventListener("keydown",function (e) {
      if ((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==="k") {
        e.preventDefault();layer.hidden?open():close();
      } else if (!layer.hidden && e.key==="Escape") {
        e.preventDefault();close();
      } else if (!layer.hidden && e.key==="Tab") {
        var focusable=Array.from(layer.querySelectorAll('input,button:not([hidden]),a[href]'))
          .filter(function (el) {return el.getClientRects().length>0;});
        var first=focusable[0],last=focusable[focusable.length-1];
        if (e.shiftKey && document.activeElement===first) {e.preventDefault();last.focus();}
        else if (!e.shiftKey && document.activeElement===last) {e.preventDefault();first.focus();}
      }
    });
    document.body.append(trigger,layer);
  }
  if (document.readyState==="loading") document.addEventListener("DOMContentLoaded",mount,{once:true});
  else mount();
})();