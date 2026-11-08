#!/usr/bin/env python3
"""Build three factual, source-attributed news sections from verified OFFICIAL RSS feeds.
Python 3.11+, stdlib only. Read-only HTTP(S) from allowlisted publishers.
Do not copy full articles or copyrighted photographs; keep headlines, timestamps, links.
No titles, dates or availability are fabricated. Fail closed and preserve previous snapshot.
"""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import email.utils
import html
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOW = dt.datetime.now(dt.timezone.utc)
MAX_AGE = dt.timedelta(days=45)
UA = "AlghadDigitalNews/1.0 (+https://alghad.digital/; contact protech.2025.2026@gmail.com)"
ATOM = "{http://www.w3.org/2005/Atom}"
MAX_FEED_BYTES = 1_500_000
TOPIC_NAMES = {
    "ai": "الذكاء الاصطناعي",
    "companies": "الشركات التقنية الكبرى",
    "cars": "السيارات والتقنيات الحديثة",
}

# Sources that do not expose a working feed are deliberately marked directory-only.
# All metadata remains official, without claiming automated collection from them.
SOURCES = [
    # AI
    dict(id="openai",name="OpenAI · ChatGPT",site="https://openai.com/news/",rss="https://openai.com/news/rss.xml",host="openai.com",links=["openai.com"],topics=["ai"]),
    dict(id="googleai",name="Google AI · Gemini",site="https://blog.google/technology/ai/",rss="https://blog.google/technology/ai/rss/",host="blog.google",links=["blog.google"],topics=["ai"]),
    dict(id="anthropic",name="Anthropic · Claude",site="https://www.anthropic.com/news",rss=None,topics=["ai"]),
    dict(id="deepseek",name="DeepSeek",site="https://www.deepseek.com/en/news/",rss=None,topics=["ai"]),
    # Major technology corporations
    dict(id="nvidia",name="NVIDIA",site="https://nvidianews.nvidia.com/",rss="https://nvidianews.nvidia.com/rss.xml",host="nvidia.com",links=["nvidia.com"],topics=["companies"],ai_matching=True),
    dict(id="amd",name="AMD",site="https://ir.amd.com/news-events/press-releases",rss="https://ir.amd.com/news-events/press-releases/rss",host="amd.com",links=["amd.com"],topics=["companies"],ai_matching=True),
    dict(id="apple",name="Apple",site="https://www.apple.com/newsroom/",rss="https://www.apple.com/newsroom/rss-feed.rss",host="apple.com",links=["apple.com"],topics=["companies"]),
    dict(id="samsung",name="Samsung",site="https://news.samsung.com/global/",rss="https://news.samsung.com/global/feed",host="samsung.com",links=["samsung.com"],topics=["companies"],ai_matching=True),
    dict(id="microsoft",name="Microsoft",site="https://blogs.microsoft.com/",rss="https://blogs.microsoft.com/feed/",host="microsoft.com",links=["microsoft.com"],topics=["companies"],ai_matching=True),
    dict(id="google",name="Google",site="https://blog.google/",rss="https://blog.google/rss/",host="blog.google",links=["blog.google"],topics=["companies"],ai_matching=True),
    dict(id="huawei",name="Huawei",site="https://www.huawei.com/en/news",rss=None,topics=["companies"]),
    # Vehicle makers
    dict(id="toyota",name="Toyota USA",site="https://pressroom.toyota.com/",rss="https://pressroom.toyota.com/feed/",host="toyota.com",links=["toyota.com"],topics=["cars"]),
    dict(id="toyotaglobal",name="Toyota Global",site="https://global.toyota/en/newsroom/",rss="https://global.toyota/export/en/allnews_rss.xml",host="global.toyota",links=["global.toyota"],topics=["cars"]),
    dict(id="honda",name="Honda",site="https://hondanews.eu/eu/en/cars",rss="https://hondanews.eu/eu/en/cars/rss/pressreleases/feed.rss",host="hondanews.eu",links=["hondanews.eu"],topics=["cars"]),
    dict(id="porsche",name="Porsche",site="https://newsroom.porsche.com/en.html",rss="https://newsroom.porsche.com/rss/en/index.rss",host="porsche.com",links=["porsche.com"],topics=["cars"]),
    dict(id="subaru",name="Subaru",site="https://www.subaru.co.jp/en/",rss="https://www.subaru.co.jp/press/news-en/feed/",host="subaru.co.jp",links=["subaru.co.jp"],topics=["cars"]),
    dict(id="tesla",name="Tesla",site="https://www.tesla.com/blog",rss=None,topics=["cars"]),
    dict(id="bmw",name="BMW",site="https://www.press.bmwgroup.com/global",rss=None,topics=["cars"]),
    dict(id="mercedes",name="Mercedes-Benz",site="https://group.mercedes-benz.com/",rss=None,topics=["cars"]),
    dict(id="hyundai",name="Hyundai",site="https://org.hyundai.com/worldwide/en/newsroom",rss=None,topics=["cars"]),
    dict(id="kia",name="Kia",site="https://www.kiamedia.com/",rss=None,topics=["cars"]),
]
AI_MARKER = re.compile(
    r"\b(?:AI|ChatGPT|Claude|Gemini|Copilot|OpenAI|machine learning|deep learning|"
    r"artificial intelligence|agentic|generative|LLM|inference|foundation model|"
    r"neural network|GPU|accelerated computing|language model)\b|"
    r"الذكاء الاصطناعي|تعلم الآلة|نماذج لغوية",re.I
)

def allowed(url: str, hosts: list[str]) -> bool:
    try:
        part=urllib.parse.urlsplit(url.strip())
        h=(part.hostname or "").lower()
        return (part.scheme=="https" and bool(h) and not part.username and
                not part.password and part.port is None and
                any(h==base or h.endswith("."+base) for base in hosts))
    except (ValueError,AttributeError):
        return False

def safe_article_link(raw: str, source: dict) -> str | None:
    if not raw or not allowed(raw, source["links"]):
        return None
    u=urllib.parse.urlsplit(raw.strip())
    qs=[(k,v) for k,v in urllib.parse.parse_qsl(u.query,keep_blank_values=False)
        if not k.lower().startswith(("utm_","fbclid","gclid","msclkid"))]
    return urllib.parse.urlunsplit(("https",u.netloc,u.path,urllib.parse.urlencode(qs),""))

def when(raw: str | None) -> dt.datetime | None:
    if not raw:return None
    try: timestamp=email.utils.parsedate_to_datetime(raw)
    except (ValueError,TypeError,IndexError):
        try:timestamp=dt.datetime.fromisoformat(raw.strip().replace("Z","+00:00"))
        except ValueError:return None
    if timestamp is None:return None
    timestamp=timestamp.replace(tzinfo=timestamp.tzinfo or dt.timezone.utc).astimezone(dt.timezone.utc)
    if timestamp > NOW+dt.timedelta(hours=12) or NOW-timestamp > MAX_AGE:return None
    return timestamp

def get_text(element: ET.Element, field: str) -> str:
    return element.findtext(field) or element.findtext(ATOM+field) or ""

def fetch_one(source: dict) -> tuple[dict,list[dict],str|None]:
    if not source["rss"]:return source,[],"no_verified_public_rss"
    try:
        req=urllib.request.Request(source["rss"],headers={"User-Agent":UA,
            "Accept":"application/rss+xml, application/atom+xml, application/xml, text/xml;q=.9, */*;q=.4"})
        with urllib.request.urlopen(req,timeout=14) as resp:
            if resp.status != 200 or not allowed(resp.url,[source["host"]]):
                raise ValueError("Unexpected redirect or response status")
            buf=resp.read(MAX_FEED_BYTES+1)
        if len(buf)>MAX_FEED_BYTES:raise ValueError("Feed exceeds maximum safe size")
        root=ET.fromstring(buf)
        items=root.findall(".//item")
        if not items:items=root.findall(".//"+ATOM+"entry")
        results=[]
        for item in items[:160]:
            title=html.unescape(re.sub(r"<[^>]*>"," ",get_text(item,"title")))
            title=re.sub(r"\s+"," ",title).strip()[:180]
            if len(title)<12:continue
            link=get_text(item,"link")
            if not link:
                candidate=item.find(ATOM+"link")
                if candidate is not None:link=candidate.get("href","")
            link=safe_article_link(link,source)
            published=when(get_text(item,"pubDate") or get_text(item,"published") or get_text(item,"updated"))
            if not link or not published:continue
            normalized={"title":title,"url":link,"source":source["id"],
                "source_name":source["name"],"published_at":published.isoformat().replace("+00:00","Z"),
                "language":"en","official":True}
            for topic in source["topics"]:
                results.append({**normalized,"topic":topic})
            if source.get("ai_matching") and AI_MARKER.search(title):
                results.append({**normalized,"topic":"ai"})
        return source,results,None
    except (OSError,ET.ParseError,ValueError,TimeoutError) as error:
        return source,[],type(error).__name__+": "+str(error)[:115]

def curate(all_records: list[dict], topic: str, limit: int=18) -> list[dict]:
    ordered=sorted((item for item in all_records if item["topic"]==topic),
                   key=lambda item:item["published_at"],reverse=True)
    count={};seen=set();out=[]
    for item in ordered:
        key=item["url"].split("?")[0]
        if key in seen or count.get(item["source"],0)>=5:continue
        seen.add(key)
        count[item["source"]]=count.get(item["source"],0)+1
        out.append(item)
        if len(out)>=limit:break
    return out

def main() -> int:
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as executor:
        results=list(executor.map(fetch_one,SOURCES))
    all_items=[item for source,items,error in results for item in items]
    sections={topic:curate(all_items,topic) for topic in TOPIC_NAMES}
    if any(len(articles)<3 for articles in sections.values()):
        print("ERROR: Not enough dated official stories per group. Existing snapshot preserved.",file=sys.stderr)
        for topic,articles in sections.items():print(f"{topic}={len(articles)}",file=sys.stderr)
        return 2
    statuses={x["id"]:{"active":len(items)>0,"count":len(items),"error":error}
              for x,items,error in results}
    meta=[]
    for spec in SOURCES:
        entry={"id":spec["id"],"name":spec["name"],"url":spec["site"],
               "topics":spec["topics"],"feed_available":statuses[spec["id"]]["active"],
               "directory_only":not statuses[spec["id"]]["active"]}
        meta.append(entry)
    payload={"version":1,"generated_at":NOW.isoformat(timespec="seconds").replace("+00:00","Z"),
        "topics":{k:{"title":v,"articles":sections[k]} for k,v in TOPIC_NAMES.items()},
        "sources":meta,"rights":"Official publisher headlines, timestamps and links only; articles remain with their owners.",
        "language_note":"Official source headlines are kept in their original language; not automatically translated."}
    json_file=ROOT/"assets"/"industry-news.json"
    js_file=ROOT/"assets"/"industry-news-data.js"
    staged=json_file.with_suffix(".json.tmp")
    staged.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    staged_js=js_file.with_suffix(".js.tmp")
    staged_js.write_text("window.AL_GHAD_INDUSTRY_NEWS = "+json.dumps(payload,ensure_ascii=True,separators=(",",":"))+";\n",encoding="utf-8")
    staged.replace(json_file)
    staged_js.replace(js_file)
    print("OFFICIAL_HEADLINES="+str(sum(map(len,sections.values()))))
    for topic,articles in sections.items():
        print("TOPIC="+topic+" ARTICLES="+str(len(articles))+" SOURCES="+",".join(sorted(set(i["source"] for i in articles))))
    for spec,items,error in results:
        print("FEED="+spec["id"]+" ITEMS="+str(len(items))+" ERROR="+str(error))
    return 0

if __name__=="__main__":raise SystemExit(main())
