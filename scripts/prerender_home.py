#!/usr/bin/env python3
"""HTML pre-rendering of ProTech's homepage products, releases and four latest stories.

Python 3.11+, Node.js 22+. Uses only verified local product and release manifests.
Headlines are sourced from the current, attributed daily RSS JSON snapshot.
Search engines and visitors with JS disabled can read products and download links.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit
import html
import json
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"index.html"

node_script=r'''
const fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const root=process.argv[1],sandbox={window:{}};
for(const file of ["assets/products.js","assets/downloads.js"]){
  vm.runInNewContext(fs.readFileSync(path.join(root,file),"utf8"),sandbox,{timeout:1800});
}
process.stdout.write(JSON.stringify({products:sandbox.window.AL_GHAD_PRODUCTS,
  downloads:sandbox.window.AL_GHAD_DOWNLOADS}));
'''
res=subprocess.run(["node","-e",node_script,str(ROOT)],capture_output=True,
                   text=True,encoding="utf-8",timeout=25,check=True)
manifest=json.loads(res.stdout)
products=manifest["products"]
downloads=manifest["downloads"]
news=json.loads((ROOT/"assets"/"news.json").read_text(encoding="utf-8"))
release_facts=json.loads((ROOT/"assets"/"release-facts.json").read_text(encoding="utf-8"))
assert release_facts["version"]==1 and set(release_facts["releases"])=={"marble","hr","reports","download"}
# The browser only receives already-approved public release information.
(ROOT/"assets"/"release-facts-data.js").write_text(
    "window.AL_GHAD_RELEASE_FACTS = "+json.dumps(release_facts,ensure_ascii=True,separators=(",",":"))+";\n",
    encoding="utf-8")
assert len(products)==10
byid={p["id"]:p for p in products}
assert len(byid)==10
live_order=["marble","hr","reports","download","stone"]
ids=live_order+[p["id"] for p in products if p["id"] not in live_order]
assert len(ids)==10

def esc(s)->str:
    return html.escape(str(s if s is not None else ""),quote=True)

def safe_release(url:str|None)->bool:
    if not isinstance(url,str):return False
    try:
        parts=urlsplit(url)
    except ValueError:return False
    return (parts.scheme=="https" and parts.hostname=="github.com"
            and parts.username is None and parts.password is None and
            re.fullmatch(r"/Abdealmalk007/[A-Za-z0-9_.-]+/releases/(?:tag|download)/[^?#\s]+",parts.path) is not None)

def anchor(url,label,css="",external=False):
    attrs=(' target="_blank" rel="noopener noreferrer"' if external else "")
    return f'<a href="{esc(url)}" class="{esc(css)}"{attrs}>{esc(label)}</a>'

def recommended(pid):
    entry=downloads.get(pid,{})
    for file in entry.get("files",[]):
        if file.get("recommended") and safe_release(file.get("url")) and file.get("bytes",0)>100000:
            return entry,file
    return entry,None

catalog=[]
for i,id in enumerate(ids):
    p=byid[id]
    entry,featured=recommended(id)
    status=("Beta · نسخة عامة للتجربة" if featured else
            "مستودع منشور · التنزيل غير متاح" if p["status"]=="public" else "قريبًا")
    label=(f"الإصدار {entry['version']} · تجريبي" if featured else
           "المستودع منشور على GitHub" if p["status"]=="public" else "قيد التطوير")
    links=anchor(f"programs/{id}/","تفاصيل البرنامج","pre-product-details")
    if featured:
        links+=anchor(featured["url"],"تنزيل الإصدار الرسمي","pre-product-download",True)
    card=f'''<article class="pre-product-card" data-prerender-product="{esc(id)}">
      <div class="pre-product-cover">
        <img src="{esc(p["preview"])}" alt="{esc(p["previewAlt"])} — صورة توضيحية للبرنامج" width="960" height="540" decoding="async" loading="{'eager' if i<2 else 'lazy'}">
      </div>
      <div class="pre-product-content">
        <span class="pre-product-badge">{esc(status)}</span>
        <h3>{anchor(f"programs/{id}/",p["title"],"pre-product-title")}</h3>
        <p class="pre-product-description">{esc(p["description"])}</p>
        <small>{esc(label)}</small>
        <div class="pre-product-actions">{links}</div>
      </div>
    </article>'''
    catalog.append(card)
assert len(catalog)==10

release_cards=[]
for id in ["marble","hr","reports","download"]:
    p=byid[id]
    entry,file=recommended(id)
    assert entry.get("channel")=="preview" and file
    checksum=(anchor(entry["checksum"],"ملف SHA-256","pre-release-checksum",True)
              if safe_release(entry.get("checksum")) else "")
    label=esc(file["platform"])
    size=round(file["bytes"]/1048576,1)
    verified=release_facts["releases"][id]
    assert verified["repository"]==entry["repository"] and verified["version"]==entry["version"]
    selected=next((x for x in verified["assets"] if x["url"]==file["url"] and x["bytes"]==file["bytes"]),None)
    assert selected and re.fullmatch(r"[a-f0-9]{64}",selected["sha256"])
    published=esc(verified["published_at"][:10])
    digest=esc(selected["sha256"])
    release_cards.append(
      '<article class="pre-release-card" data-prerender-release="'+esc(id)+'">'
      '<span class="pre-release-status">Beta / Preview</span>'
      '<h3>'+esc(p["title"])+'</h3>'
      f'<p>الإصدار {esc(entry["version"])} · {label} · {size} MB</p>'
      '<div class="pre-release-actions">'+anchor(file["url"],"تحميل مباشر","pre-release-download",True)
      +anchor(entry["release"],"سجل الإصدار","pre-release-source",True)+checksum
      +f'<div class="pre-release-verified"><span>تاريخ النشر: {published}</span>'
      +f'<code dir="ltr" aria-label="SHA-256 من GitHub">SHA-256: {digest}</code></div>'
      +'</div></article>')
assert len(release_cards)==4

trusted=["aitnews.com","tech-wd.com","arabhardware.net","techvoicearabia.com",
         "technologyarabia.com","3arrafni.com","th3professional.com",
         "aljazeera.net","bbc.com","bbc.co.uk","unlimit-tech.com"]
def safe_news(url):
    try:
        u=urlsplit(url)
        return u.scheme=="https" and bool(u.hostname) and any(u.hostname==base or u.hostname.endswith("."+base) for base in trusted)
    except (ValueError,TypeError):return False

items=[p for p in news["articles"] if isinstance(p.get("title"),str)
       and safe_news(p.get("url")) and re.fullmatch(r"\d{4}-\d{2}-\d{2}.*",p.get("published_at",""))][:4]
assert len(items)==4
brief=[]
for item in items:
    translated=(item.get("translation_status")=="machine" and
                isinstance(item.get("title_ar"),str) and len(item["title_ar"])>=4)
    name=item["title_ar"] if translated else item["title"]
    original=(f'<small lang="en" dir="ltr" class="pre-news-original">{esc(item["title"])}</small>'
              if translated else "")
    brief.append('<article class="pre-news-row"><span class="pre-news-date">'
        +esc(item.get("source_name","المصدر الأصلي"))+" · "+esc(item["published_at"][:10])
        +'</span><h3>'+anchor(item["url"],name,"pre-news-link",True)
        +'</h3>'+original+'</article>')

body=PAGE.read_text(encoding="utf-8")
for label,markup in (("PRODUCTS","\n".join(catalog)),
                     ("DOWNLOADS","\n".join(release_cards)),
                     ("NEWS","\n".join(brief))):
    pat=re.compile(r"<!-- PRE_RENDER_"+label+r"_START -->[\s\S]*?<!-- PRE_RENDER_"+label+r"_END -->")
    assert len(pat.findall(body))==1,f"Missing or duplicated prerender marker {label}"
    body=pat.sub(lambda _:f"<!-- PRE_RENDER_{label}_START -->\n{markup}\n<!-- PRE_RENDER_{label}_END -->",body,count=1)
PAGE.write_text(body,encoding="utf-8",newline="\n")
print("PRERENDERED_PROGRAMS="+str(len(catalog)))
print("PRERENDERED_VERIFIED_DOWNLOADS="+str(len(release_cards)))
print("PRERENDERED_NEWS_HEADLINES="+str(len(brief)))
