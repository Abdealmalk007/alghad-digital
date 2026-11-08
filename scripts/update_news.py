#!/usr/bin/env python3
"""Refresh attributed public technology headlines. Python >= 3.11, no dependencies."""
import concurrent.futures,datetime as dt,email.utils,html,json,re,sys,urllib.parse,urllib.request,xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOW=dt.datetime.now(dt.timezone.utc)
FEEDS=[
 ("aitnews","البوابة التقنية","https://aitnews.com/feed/","aitnews.com",False),
 ("techwd","عالم التقنية","https://www.tech-wd.com/wd/feed/","tech-wd.com",False),
 ("hardware","عرب هاردوير","https://arabhardware.net/feed","arabhardware.net",False),
 ("techvoice","تيك فويس عربية","https://techvoicearabia.com/feed/","techvoicearabia.com",False),
 ("technologyarabia","مجلة التقنية العربية","https://technologyarabia.com/feed/","technologyarabia.com",False),
 ("arrafni","عرفني دوت كوم","https://3arrafni.com/feed.xml","3arrafni.com",False),
 ("almohtraf","مدونة المحترف","https://www.th3professional.com/feeds/posts/default?alt=rss","th3professional.com",False),
 ("aljazeera","الجزيرة نت","https://www.aljazeera.net/aljazeerarss/","aljazeera.net",True),
 ("bbc","BBC عربي","https://feeds.bbci.co.uk/arabic/rss.xml","bbc.com",True),
 ("unlimit","التقنية بلا حدود","https://www.unlimit-tech.com/feed/","unlimit-tech.com",False),
]
SITE_LINKS={"aitnews":"https://aitnews.com/","techwd":"https://www.tech-wd.com/wd/","hardware":"https://arabhardware.net/","techvoice":"https://techvoicearabia.com/","technologyarabia":"https://technologyarabia.com/","arrafni":"https://3arrafni.com/","almohtraf":"https://www.th3professional.com/","aljazeera":"https://www.aljazeera.net/","bbc":"https://www.bbc.com/arabic","unlimit":"https://www.unlimit-tech.com/"}
TECH=re.compile(r"ذكاء اصطناعي|الذكاء الاصطناعي|تقني|تكنولوج|برمج|سيبراني|الرقمي|اختراق|هاتف|هواتف|حواسيب|حاسوب|كمبيوتر|روبوت|ChatGPT|OpenAI|Gemini|Claude|آبل|أبل|أندرويد|جوجل|غوغل|مايكروسوفت|إنترنت|تطبيق|شريحة|رقائق|معالج|واتساب|تيك توك|الواقع المعزز|العملات المشفرة|شبكات الجيل|بيانات|تسلا",re.I)
NOT_TECH=re.compile(r"كرة القدم|دوري أبطال|كأس العالم|مباراة|حرب غزة|الانتخابات",re.I)
CATS=[
 ("الأمن السيبراني",r"سيبران|اختراق|ثغر|هجوم إلكتروني|الأمن الرقم|هاكر|تسريب بيانات"),
 ("الذكاء الاصطناعي",r"ذكاء اصطناعي|الذكاء الاصطناعي|ChatGPT|OpenAI|Gemini|Claude|روبوت"),
 ("الهواتف والأجهزة",r"هاتف|هواتف|جوال|آيفون|iPhone|سامسونج|آيباد|Android|أندرويد|رقائق|حاسوب|معالج|أجهزة"),
 ("البرامج والإنترنت",r"تطبيق|برمج|ويندوز|Windows|إنترنت|متصفح|منصة|مايكروسوفت|جوجل|غوغل")
]
def date_of(value):
 if not value:return None
 try:d=email.utils.parsedate_to_datetime(value)
 except (ValueError,TypeError,IndexError):
  try:d=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
  except ValueError:return None
 if not d:return None
 d=d.replace(tzinfo=d.tzinfo or dt.timezone.utc).astimezone(dt.timezone.utc)
 return d if NOW-dt.timedelta(days=28)<d<NOW+dt.timedelta(hours=36) else None
def safe_url(link,host):
 try:
  u=urllib.parse.urlsplit(link.strip());h=(u.hostname or "").lower()
  valid=(h==host or h.endswith("."+host) or (host=="bbc.com" and (h=="bbc.co.uk" or h.endswith(".bbc.co.uk"))))
  if u.scheme!="https" or not valid or u.username or u.password or u.port:return None
  qs=[(k,v) for k,v in urllib.parse.parse_qsl(u.query) if not k.lower().startswith(("utm_","fbclid","gclid"))]
  return urllib.parse.urlunsplit(("https",u.netloc,u.path,urllib.parse.urlencode(qs),""))
 except (ValueError,AttributeError):return None
def gather(feed):
 ident,name,url,host,general=feed;articles=[];error=""
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"AlghadDigitalTechNews/1.0 (protech.2025.2026@gmail.com)","Accept":"application/rss+xml, application/atom+xml, application/xml;q=.9, */*;q=.5"})
  with urllib.request.urlopen(req,timeout=11) as response:
   final=urllib.parse.urlsplit(response.url);origin=urllib.parse.urlsplit(url)
   if final.scheme!="https" or not final.hostname or not final.hostname.endswith(origin.hostname.replace("www.","")):raise ValueError("feed redirect changed host")
   data=response.read(470001)
   if len(data)>470000:raise ValueError("feed too large")
  tree=ET.fromstring(data)
  items=tree.findall(".//item")
  if not items:items=tree.findall(".//{http://www.w3.org/2005/Atom}entry")
  for item in items[:65]:
   title=html.unescape(re.sub(r"<[^>]{0,240}>"," ",item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title") or ""))
   title=re.sub(r"\s+"," ",title).strip()[:175]
   link=item.findtext("link") or ""
   if not link:
    node=item.find("{http://www.w3.org/2005/Atom}link")
    if node is not None:link=node.attrib.get("href","")
   link=safe_url(link,host)
   date=date_of(item.findtext("pubDate") or item.findtext("{http://www.w3.org/2005/Atom}published") or item.findtext("{http://www.w3.org/2005/Atom}updated") or "")
   if not link or not date or len(title)<15:continue
   if general and (not TECH.search(title) or NOT_TECH.search(title)):continue
   category=next((c for c,p in CATS if re.search(p,title,re.I)),"أخبار التقنية")
   articles.append({"title":title,"url":link,"source":ident,"source_name":name,"published_at":date.isoformat().replace("+00:00","Z"),"category":category})
 except (OSError,ET.ParseError,ValueError,TimeoutError) as e:error=type(e).__name__+":"+str(e)[:100]
 return ident,name,url,len(articles),articles,error
def main():
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  feeds=list(pool.map(gather,FEEDS))
 ordered=sorted((a for x in feeds for a in x[4]),key=lambda a:a["published_at"],reverse=True)
 accepted=[];seen=set();per_source={}
 for item in ordered:
  key=re.sub(r"\W","",item["title"]).casefold()
  if key in seen or per_source.get(item["source"],0)>=5:continue
  accepted.append(item);seen.add(key);per_source[item["source"]]=per_source.get(item["source"],0)+1
  if len(accepted)>=36:break
 if len(accepted)<5:
  print("Not enough reliable feeds; preserve previous news.json",file=sys.stderr)
  return 2
 data={"version":1,"generated_at":NOW.isoformat(timespec="seconds").replace("+00:00","Z"),
       "articles":accepted,"sources":[{"id":x[0],"name":x[1],"url":SITE_LINKS[x[0]],"active":x[3]>0} for x in feeds],
       "copyright":"Headlines, dates, attribution and links only; read full articles on original publishers."}
 f=ROOT/"assets"/"news.json";tmp=f.with_suffix(".tmp")
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 tmp.replace(f)
 data_js=ROOT/"assets"/"news-data.js"
 data_js.write_text("window.AL_GHAD_NEWS = "+json.dumps(data,ensure_ascii=True,separators=(",",":"))+";\n",encoding="utf-8")
 print(f"NEWS_COUNT={len(accepted)} ACTIVE_FEEDS={sum(x[3]>0 for x in feeds)} OUTPUT={f}")
 for x in feeds:print("SOURCE=",x[0],"ITEMS=",x[3],"ERROR=",x[5])
 return 0
if __name__=="__main__":raise SystemExit(main())
