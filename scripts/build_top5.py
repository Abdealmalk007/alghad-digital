#!/usr/bin/env python3
"""Generate the bilingual TOP 5 news hub from attributed, date-verified news.

Reads existing news snapshots and optionally verified external RSS feeds.
Only actual source titles and summaries are published; translations are reused
only from the existing verified translation cache. No generated/fake headlines.
All timestamps are original publisher dates, never fetch dates.
"""
from __future__ import annotations
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import html
import importlib.util
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://alghad.digital"
CONFIG = ROOT / "config/top5_categories.json"
DATA = ROOT / "assets/top5-news.json"
NOW = dt.datetime.now(dt.timezone.utc)
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_BYTES = 620000
# Curated RSS sources supplement (not replace) the site's existing publishers.
# Feed failure never manufactures an item; it only reduces the available count.
EXTRA_RSS = [
    ("windowsblog", "Microsoft Windows Blog", "https://blogs.windows.com/feed/", "blogs.windows.com", "windows"),
    ("androiddev", "Android Developers", "https://android-developers.googleblog.com/feeds/posts/default?alt=rss", "android-developers.googleblog.com", "android"),
    ("macrumors", "MacRumors", "https://www.macrumors.com/macrumors.xml", "macrumors.com", "apple"),
    ("bleeping", "BleepingComputer", "https://www.bleepingcomputer.com/feed/", "bleepingcomputer.com", "security"),
    ("neowin", "Neowin", "https://www.neowin.net/news/rss/", "neowin.net", "software"),
]
SOURCE_WEIGHT = {
    "openai": 16, "googleai": 16, "apple": 16, "microsoft": 16,
    "nvidia": 14, "amd": 14, "samsung": 14, "google": 14,
    "androiddev": 15, "windowsblog": 15,
    "arstechnica": 12, "theverge": 12, "techcrunch": 12,
    "wired": 12, "engadget": 12, "bleeping": 13,
}
ICONS = {
 "monitor": '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
 "smartphone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
 "app-window": '<rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 8h20M7 3v18"/>',
 "laptop": '<path d="M4 4h16v12H4zM2 20h20l-2-4H4z"/>',
 "newspaper": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h10M7 11h4M7 15h10M14 11h3"/>',
 "cpu": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 9h6v6H9zM9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
 "car-front": '<path d="m5 16 2-8h10l2 8v4h-2v-2H7v2H5zM5 13h14M8 16h1m6 0h1"/>',
 "download": '<path d="M12 3v13m-5-5 5 5 5-5M4 18v3h16v-3"/>',
 "brain": '<path d="M12 4c-3-3-8-1-8 3-3 2-2 6 0 7-1 4 3 7 8 5 5 2 9-1 8-5 2-1 3-5 0-7 0-4-5-6-8-3zM12 4v15M8 10l4 3 4-3"/>',
 "shield-check": '<path d="m12 2 9 4v6c0 5-4 8-9 10-5-2-9-5-9-10V6zM8 12l3 3 5-6"/>',
}
def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)
def clean(value: Any, limit: int = 205) -> str:
    t = html.unescape(re.sub(r"<[^>]{0,400}>", " ", str(value or "")))
    return re.sub(r"\s+", " ", t).strip()[:limit]
def date(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        out = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        try: out = email.utils.parsedate_to_datetime(str(value))
        except (TypeError, ValueError): return None
    if out is None:
        return None
    return out.replace(tzinfo=out.tzinfo or dt.timezone.utc).astimezone(dt.timezone.utc)
def iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
def good_url(value: Any, expected_host: str | None = None) -> str:
    try:
        u = urllib.parse.urlsplit(str(value))
        host = (u.hostname or "").lower()
        if u.scheme != "https" or not host or u.username or u.password or u.port:
            return ""
        if expected_host and not (host == expected_host or host.endswith("." + expected_host)):
            return ""
        if host in ("localhost", "127.0.0.1") or host.endswith(".local"):
            return ""
        query = [(k,v) for k,v in urllib.parse.parse_qsl(u.query)
                 if not k.lower().startswith(("utm_", "fbclid", "gclid", "msclkid"))]
        return urllib.parse.urlunsplit(("https", u.netloc, u.path or "/", urllib.parse.urlencode(query), ""))
    except (ValueError, TypeError):
        return ""
def load(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))
def from_existing() -> list[dict]:
    out = []
    news = load("assets/news.json")
    industry = load("assets/industry-news.json")
    for source, items, topic in [
        ("general", news.get("articles", []), None),
        *[(t, industry.get("topics", {}).get(t, {}).get("articles", []), t)
          for t in ("ai", "companies", "cars")]
    ]:
        for a in items:
            url = good_url(a.get("url"))
            stamp = date(a.get("published_at"))
            title = clean(a.get("title"), 200)
            if not url or not stamp or len(title) < 12:
                continue
            # Source-language title is retained. Never silently translate Arabic to English.
            original_ar = bool(re.search(r"[\u0621-\u064a]", title))
            title_ar = clean(a.get("title_ar"), 205)
            if title_ar == title and not original_ar:
                title_ar = ""
            out.append({
                "url": url, "source": str(a.get("source", "")),
                "source_name": str(a.get("source_name", ""))[:100],
                "published_at": iso(stamp), "original_title": title,
                "title_en": "" if original_ar else title,
                "title_ar": title if original_ar else title_ar,
                "summary_en": clean(a.get("summary_en") or a.get("description_en"), 230),
                "summary_ar": clean(a.get("summary_ar") or a.get("description_ar"), 230),
                "topic": topic or "",
                "official": bool(a.get("official")),
                "fetched_at": str((industry if topic else news).get("generated_at", "")),
            })
    return out
def fetch_extra(entry: tuple[str,str,str,str,str]) -> list[dict]:
    source, name, rss, host, topic = entry
    try:
        req = urllib.request.Request(rss, headers={"User-Agent": "AlghadDigital-Top5/1.0 (protech.2025.2026@gmail.com)",
                "Accept": "application/rss+xml,application/atom+xml,application/xml;q=.9"})
        with urllib.request.urlopen(req, timeout=6) as response:
            if not good_url(response.url, host):
                return []
            raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            return []
        tree = ET.fromstring(raw)
        elements = tree.findall(".//item") or tree.findall(".//" + ATOM + "entry")
        results = []
        for item in elements[:60]:
            title = clean(item.findtext("title") or item.findtext(ATOM+"title"), 200)
            node = item.find(ATOM + "link")
            link = item.findtext("link") or (node.get("href", "") if node is not None else "")
            url = good_url(link, host)
            stamp = date(item.findtext("pubDate") or item.findtext(ATOM+"published") or item.findtext(ATOM+"updated"))
            if not url or not stamp or len(title) < 12:
                continue
            original_ar = bool(re.search(r"[\u0621-\u064a]", title))
            description = clean(item.findtext("description") or item.findtext(ATOM+"summary"), 225)
            results.append({
                "url":url,"source":source,"source_name":name,"published_at":iso(stamp),
                "original_title":title,"title_en":"" if original_ar else title,
                "title_ar":title if original_ar else "",
                "summary_en":"" if original_ar else description,
                "summary_ar":description if original_ar else "",
                "topic":topic,"official":source in ("windowsblog", "androiddev"),
                "fetched_at":iso(NOW)
            })
        return results
    except (OSError, ValueError, ET.ParseError, TimeoutError) as ex:
        print("TOP5_FEED_UNAVAILABLE", source, type(ex).__name__)
        return []
def normalized_title(title: str) -> str:
    return re.sub(r"[\W_]+", "", title.casefold(), flags=re.UNICODE)
def dedupe(items: list[dict]) -> list[dict]:
    seen_urls, seen_titles, accepted = set(), set(), []
    for item in sorted(items, key=lambda a:(a["official"],len(a["summary_en"] or a["summary_ar"])), reverse=True):
        uri = item["url"].rstrip("/").lower()
        name = normalized_title(item["original_title"])
        if uri in seen_urls or name in seen_titles:
            continue
        seen_urls.add(uri);seen_titles.add(name);accepted.append(item)
    return accepted
def matching(text: str, patterns: list[str]) -> int:
    s = text.casefold()
    return sum(bool(re.search(r"(?<!\w)"+re.escape(p.casefold())+r"(?!\w)",s)) for p in patterns)
def select(items: list[dict], cfg: dict) -> dict:
    categories = [c for c in cfg["categories"] if c.get("enabled", True)]
    cutoff = NOW - dt.timedelta(days=cfg["max_age_days"])
    good = []
    promo = re.compile(r"\b(?:black friday|cyber monday|sale|deals?|save \d+%|discount|sponsored|coupon|giveaway)\b|عرض ترويجي|تخفيضات|خصم", re.I)
    for a in items:
        if promo.search(a["original_title"]):
            continue
        pub = date(a["published_at"])
        if not pub or pub < cutoff or pub > NOW+dt.timedelta(minutes=30):
            continue
        good.append(a)
    result={}
    for cat in categories:
        candidates=[]
        for article in good:
            # Match headline, not broad article text: keeps categories topically precise.
            points=matching(article["original_title"],cat["patterns"])
            if cat["id"]=="tech":
                points = 1 if article["topic"] != "cars" else 0
            elif cat["id"]=="cars" and article["topic"]=="cars" and points:
                points += 2
            elif cat["id"]=="ai" and article["topic"]=="ai":
                points += 2
            elif cat["id"]=="emerging" and article["topic"] in ("ai","companies") and points:
                points += 1
            if not points:
                continue
            published=date(article["published_at"])
            age_h=max(0,(NOW-published).total_seconds()/3600)
            importance = 27 if article["official"] else SOURCE_WEIGHT.get(article["source"],9)
            freshness = max(0,40-min(40,age_h/4.2))
            score=round(importance+freshness+min(points*8,24),2)
            age_bucket = 0 if age_h <= 24 else 1 if age_h <= 72 else 2
            candidates.append((age_bucket,score,published,article))
        candidates.sort(key=lambda t:(t[0],-t[1],-t[2].timestamp(),t[3]["url"]))
        chosen=[]
        used_sources={}
        # Prioritize the most recent bucket and diversify reliable publishers.
        for bucket,score,pub,a in candidates:
            if used_sources.get(a["source"],0)>=2:
                continue
            used_sources[a["source"]]=used_sources.get(a["source"],0)+1
            if len(chosen)>=cfg["max_items"]:
                break
            val={k:a.get(k, "") for k in ("url","source","source_name","published_at","fetched_at","original_title",
                "title_en","title_ar","summary_en","summary_ar")}
            val["id"]=hashlib.sha256(a["url"].encode()).hexdigest()[:16]
            val["category"]=cat["id"];val["rank"]=len(chosen)+1;val["ranking_score"]=score
            val["image_url"]=None # No image license is assumed.
            chosen.append(val)
        result[cat["id"]]=chosen
    return result
def validate(cfg: dict, data: dict) -> None:
    cats=[c for c in cfg["categories"] if c.get("enabled",True)]
    assert len({c["id"] for c in cats})==len(cats)>=1
    assert all(re.fullmatch("[a-z0-9-]+",c["id"]) for c in cats)
    assert set(data["topics"])=={c["id"] for c in cats}
    for cat in cats:
        group=data["topics"][cat["id"]]
        assert len(group)<=5 and len({a["url"] for a in group})==len(group)
        for i,a in enumerate(group,1):
            assert a["rank"]==i and a["category"]==cat["id"]
            assert good_url(a["url"])==a["url"]
            published=date(a["published_at"])
            assert published and NOW-dt.timedelta(days=cfg["max_age_days"])<=published<=NOW+dt.timedelta(minutes=30)
            assert a["original_title"] and a["source_name"]
def icon(name: str) -> str:
    path = ICONS.get(name,ICONS["newspaper"])
    return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'+path+'</svg>'
def render_body(locale: str, cfg: dict, data: dict) -> str:
    ar=locale=="ar"
    cats=[c for c in cfg["categories"] if c.get("enabled", True)]
    tab=[]
    panels=[]
    for index,cat in enumerate(cats):
        cid=cat["id"]
        name=cat["ar"] if ar else cat["en"]
        items=data["topics"][cid]
        label = ("TOP 5 — " if ar else "TOP 5 — ") + name
        tab.append(f'<button class="top5-tab" id="top5-tab-{cid}" type="button" role="tab" '
                   f'aria-controls="top5-panel-{cid}" aria-selected="{"true" if index==0 else "false"}" '
                   f'tabindex="{0 if index==0 else -1}" data-top5-id="{cid}">'
                   f'<span class="top5-tab-icon">{icon(cat["icon"])}</span>'
                   f'<span class="top5-tab-name">{esc(label)}</span>'
                   f'<span class="top5-tab-count" aria-label="{"عدد الأخبار" if ar else "articles"}">{len(items)}</span></button>')
        rows=[]
        for a in items:
            title=(a["title_ar"] if ar else a["title_en"]) or a["original_title"]
            if not title:
                continue
            text_ar=bool(re.search(r"[\u0621-\u064a]",title))
            source_lang="ar" if text_ar else "en"
            summary = (a["summary_ar"] if ar else a["summary_en"]) or ""
            # Never pretend original-language text is a professional translation.
            date_visible=esc(a["published_at"][:10])
            read_label="قراءة الخبر من المصدر" if ar else "Read at publisher"
            untrans = (not a["title_ar"] if ar else not a["title_en"])
            badge='<span class="top5-original">نص أصلي</span>' if untrans and ar else '<span class="top5-original">Original language</span>' if untrans else ""
            if not untrans and a.get("translation_status_"+locale):
                badge='<span class="top5-original">' + ("ترجمة آلية" if ar else "Machine translated") + '</span>'
            rows.append(f'<article class="top5-story"><div class="top5-story-num" aria-hidden="true">{icon(cat["icon"])}</div>'
                f'<div class="top5-story-body"><div class="top5-story-meta"><span class="top5-story-rank">#{a["rank"]}</span><span>{esc(a["source_name"])}</span>'
                f'<time datetime="{esc(a["published_at"])}">{date_visible}</time>{badge}</div>'
                f'<h3 lang="{source_lang}" dir="{"rtl" if text_ar else "ltr"}">{esc(title)}</h3>'
                +(f'<p>{esc(summary)}</p>' if summary else "")
                +f'<a class="top5-read" href="{esc(a["url"])}" target="_blank" rel="noopener noreferrer">'
                f'{read_label} <span aria-hidden="true">↗</span></a></div></article>')
        if not rows:
            empty="لا توجد أخبار موثقة وحديثة في هذا التخصص خلال آخر 7 أيام." if ar else "No verified recent stories in this category within the last seven days."
            rows.append(f'<p class="top5-empty">{empty}</p>')
        panels.append(f'<section class="top5-panel" id="top5-panel-{cid}" role="tabpanel" '
            f'aria-labelledby="top5-tab-{cid}" {"hidden" if index else ""}>'
            f'<div class="top5-section-title"><div><p class="top5-label">{esc(label)}</p>'
            f'<h2>{esc(name)}</h2></div><p>{len(items)} {"أخبار موثقة" if ar else "verified stories"}</p></div>'
            +''.join(rows)+'</section>')
    total=sum(map(len,data["topics"].values()))
    title="TOP 5 — مركز الأخبار التقنية" if ar else "TOP 5 — Technology News Hub"
    desc=("أهم الأخبار في تخصصك، من المصادر الأصلية. يعتمد الاختيار على الأهمية والحداثة، وليس فقط ترتيب النشر."
        if ar else "The leading stories in each technology field, selected from attributed publishers by relevance and recency.")
    note=("يتم تحديث الأخبار آليًا يوميًا الساعة 7:30 صباحًا بتوقيت الرياض. قد تحتوي بعض الفئات على أقل من خمسة أخبار إذا لم تتوفر مصادر حديثة موثوقة."
          if ar else "Daily automatic updates target 07:30 Asia/Riyadh. Categories may contain fewer than five items if verified recent news is unavailable.")
    back="العودة إلى الفئات" if ar else "Back to categories"
    top="أعلى الصفحة" if ar else "Back to top"
    return (f'<div class="top5-root" id="top5-hub" data-top5-language="{locale}">'
         f'<div class="top5-intro"><span class="top5-kicker">ALGHAD DIGITAL / PROTECH</span><h1>{title}</h1>'
         f'<p>{desc}</p><div class="top5-facts"><span>{len(cats)} {"مجالًا تقنيًا" if ar else "technology categories"}</span>'
         f'<span>{"تاريخ الخبر الأصلي" if ar else "Original publication dates"}</span>'
         f'<span>{"مصادر موثوقة" if ar else "Attributed publishers"}</span></div></div>'
         f'<div class="top5-layout"><nav class="top5-categories" id="top5-categories" role="tablist"'
         f' aria-label="{"فئات TOP 5" if ar else "TOP 5 categories"}">'
         +''.join(tab)+'</nav><div class="top5-content">'
         +''.join(panels)+f'<div class="top5-actions"><button type="button" data-top5-back>{back}</button>'
         f'<button type="button" data-top5-top>{top} ↑</button></div></div></div>'
         f'<p class="top5-method">{note}</p></div>'
         '<script defer src="/assets/top5-hub.js?v=1"></script>')
def render_ar(cfg: dict,data: dict) -> None:
    spec=importlib.util.spec_from_file_location("seo",ROOT/"scripts/build_seo.py")
    assert spec and spec.loader
    import sys
    seo=importlib.util.module_from_spec(spec);sys.modules["seo"]=seo
    spec.loader.exec_module(seo)
    title="TOP 5 | أهم الأخبار التقنية حسب التخصص | الغد ديجتال"
    desc="مركز TOP 5 من الغد ديجتال: أهم خمسة أخبار موثقة لكل تخصص، من Android وWindows وApple والذكاء الاصطناعي إلى السيارات والأمن السيبراني."
    url=DOMAIN+"/top-5/"
    schema={"@context":"https://schema.org","@type":"CollectionPage","name":title,"url":url,
            "inLanguage":"ar","description":desc}
    output=seo.page(title=title,description=desc,canonical=url,content=render_body("ar",cfg,data),
                    schema=schema,asset_prefix="../")
    output=output.replace("</head>",'<link rel="stylesheet" href="/assets/top5-hub.css?v=1"></head>',1)
    dest=ROOT/"top-5/index.html";dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(output,encoding="utf-8",newline="\n")
def main() -> None:
    cfg=load("config/top5_categories.json")
    assert cfg["max_items"]==5 and 1<=cfg["max_age_days"]<=7
    articles=from_existing()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        for extra in pool.map(fetch_extra,EXTRA_RSS):
            articles.extend(extra)
    articles=dedupe(articles)
    # Existing translation cache is reused, without contacting a new translation service.
    cache=load("assets/translation-cache.json").get("entries",{})
    for item in articles:
        if item["title_en"] and not item["title_ar"]:
            key=hashlib.sha256(item["title_en"].strip().encode("utf-8")).hexdigest()
            translated=cache.get(key,"")
            if isinstance(translated,str) and re.search(r"[\u0621-\u064a]",translated):
                item["title_ar"]=clean(translated,205)
    groups=select(articles,cfg)
    from top5_translate import enrich
    groups=enrich(groups)
    data={"version":1, "generated_at":iso(NOW), "source_news_updated":load("assets/news.json").get("generated_at"),
          "source_industry_updated":load("assets/industry-news.json").get("generated_at"),
          "timezone":"Asia/Riyadh","max_items":5,
          "max_age_days":cfg["max_age_days"],"topics":groups}
    validate(cfg,data)
    if DATA.is_file():
        previous=json.loads(DATA.read_text(encoding="utf-8"))
        def visible(topics):
            return {k:[{key:val for key,val in article.items() if key not in ("ranking_score","fetched_at")}
                       for article in rows] for k,rows in topics.items()}
        if visible(previous.get("topics",{}))==visible(data["topics"]) and previous.get("max_age_days")==data["max_age_days"]:
            data=previous
    DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    render_ar(cfg,data)
    print("TOP5_BUILD_PASS",json.dumps({"categories":len(groups),"stories":sum(map(len,groups.values())),
        "category_counts":{c:len(v) for c,v in groups.items()}},ensure_ascii=True))
if __name__=="__main__":
    main()
