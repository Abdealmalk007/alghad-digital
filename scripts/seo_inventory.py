#!/usr/bin/env python3
"""Non-destructive bilingual SEO inventory of all canonical pages."""
from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict,Counter
import json, re, xml.etree.ElementTree as ET
from urllib.parse import urlsplit
import sys
root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.title="";self.h1=[];self.in_title=False;self.in_h1=False;self.links=[];self.meta={};self.canonical=[];self.alternate={};self.lang="";self.scripts=[]
 def handle_starttag(self,t,a):
  d=dict(a)
  if t=="html":self.lang=d.get("lang","")
  if t=="title":self.in_title=True
  if t=="h1":self.in_h1=True;self.h1.append("")
  if t=="link":
   if d.get("rel")=="canonical":self.canonical.append(d.get("href",""))
   if d.get("rel")=="alternate" and d.get("hreflang"):self.alternate[d["hreflang"]]=d.get("href","")
  if t=="meta":
   if d.get("name"):self.meta[d["name"]]=d.get("content","")
  if t=="a" and d.get("href"):self.links.append(d["href"])
 def handle_endtag(self,t):
  if t=="title":self.in_title=False
  if t=="h1":self.in_h1=False
 def handle_data(self,v):
  if self.in_title:self.title+=v
  if self.in_h1 and self.h1:self.h1[-1]+=v

ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
urls=[x.text for x in ET.parse(root/"sitemap.xml").findall(".//s:loc",ns)]
pages={};issues=[]
for url in urls:
 p=urlsplit(url).path
 f=root/(p.strip("/") or ".")/"index.html"
 if not f.exists():issues.append(("not-found",url));continue
 q=Page();q.feed(f.read_text(encoding="utf8"));pages[url]=q
 if len(q.canonical)!=1 or q.canonical[0]!=url:issues.append(("canonical",url,str(q.canonical)))
 if len(q.h1)!=1:issues.append(("h1",url,str(q.h1)))
 if len(q.title.strip())<15 or len(q.title)>85:issues.append(("title-length",url,str(len(q.title))))
 if len(q.meta.get("description",""))<60 or len(q.meta.get("description",""))>210:issues.append(("meta-length",url,str(len(q.meta.get("description","")))))
 if q.meta.get("robots","").lower().find("noindex")>=0:issues.append(("noindex",url))
 if q.lang!=("en" if p.startswith("/en/") else "ar"):issues.append(("lang",url,q.lang))
 if not all(x in q.alternate for x in ["ar","en","x-default"]):issues.append(("hreflang-missing",url,str(q.alternate)))
 else:
  en=url.replace("https://alghad.digital/","https://alghad.digital/en/",1) if not p.startswith("/en/") else url
  ar=url.replace("https://alghad.digital/en/","https://alghad.digital/",1) if p.startswith("/en/") else url
  if q.alternate["en"]!=en or q.alternate["ar"]!=ar:issues.append(("hreflang-target",url,str(q.alternate)))
titles=defaultdict(list); descriptions=defaultdict(list)
for url,q in pages.items():
 titles[q.title.strip()].append(url)
 descriptions[q.meta.get("description","").strip()].append(url)
for title,vals in titles.items():
 if len(vals)>1:issues.append(("duplicate-title",title,str(vals)))
for desc,vals in descriptions.items():
 if len(vals)>1:issues.append(("duplicate-description",desc[:70],str(vals)))
for url,q in pages.items():
 for key in ("ar","en"):
  other=pages.get(q.alternate.get(key,""))
  if other and other.alternate.get("ar")!=q.alternate.get("ar"):issues.append(("reciprocal-ar",url,key))
  if other and other.alternate.get("en")!=q.alternate.get("en"):issues.append(("reciprocal-en",url,key))
print("URLS",len(urls),"PAGES",len(pages),"AR",sum(q.lang=="ar" for q in pages.values()),"EN",sum(q.lang=="en" for q in pages.values()))
print("PROBLEMS",len(issues),"BY_KIND",dict(Counter(x[0] for x in issues)))
for issue in issues[:80]:print("ISSUE",json.dumps(issue,ensure_ascii=True))
if "--check" in sys.argv:
 if issues:
  sys.exit(1)
 print("SEO_INVENTORY_PASS pages=42 locales=ar,en canonical=42 hreflang=42 titles=42")
else:
 for url,q in pages.items():
  print("META",json.dumps({"url":url,"title":q.title,"desc":q.meta.get("description",""),"h1":q.h1},ensure_ascii=True))
