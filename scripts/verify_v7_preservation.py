"""Compare V7 page/download/link preservation against the immutable baseline."""
import re,subprocess,urllib.parse,json
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
R=Path(__file__).resolve().parents[1]
BASE='7de1fd473648b09983a654849e96f3c9ca3df676'
def old(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=R).decode('utf8')
def routes(data):return {e.text for e in ET.fromstring(data).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')}
urls=routes((R/'sitemap.xml').read_bytes());assert urls==routes(old('sitemap.xml'))
base_files=set(subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=R).decode().splitlines())
def links(src):
 class P(HTMLParser):
  def __init__(self):super().__init__();self.links=[]
  def handle_starttag(self,tag,attrs):
   for k,v in attrs:
    if k in ('href','src') and v:self.links.append(v)
 p=P();p.feed(src);return p.links
def broken(src,url,baseline):
 out=set()
 for raw in links(src):
  u=urllib.parse.urlsplit(urllib.parse.urljoin(url,raw))
  if u.netloc!='alghad.digital' or u.scheme!='https':continue
  p=urllib.parse.unquote(u.path).strip('/')
  if not p or u.path.endswith('/'):p=(p+'/' if p else '')+'index.html'
  exists=p in base_files if baseline else (R/p).is_file()
  if not exists:out.add(p)
 return out
pat=r'https://github\.com/Abdealmalk007/[^"\s<>]+/releases/download/[^"\s<>]+'
count=0;oldbroken=set();newbroken=set()
for u in sorted(urls):
 rel=u.removeprefix('https://alghad.digital').strip('/')
 p=(rel+'/' if rel else '')+'index.html'
 b=old(p);n=(R/p).read_text(encoding='utf8')
 before=set(re.findall(pat,b));after=set(re.findall(pat,n))
 assert before<=after,(p,before-after)
 count+=len(before)
 oldbroken|={(p,x) for x in broken(b,u,True)}
 newbroken|={(p,x) for x in broken(n,u,False)}
for f in ['assets/products.js','assets/downloads.js','assets/release-facts.json','assets/brand/dawn-g.svg','favicon.svg']:
 assert (R/f).read_text(encoding='utf8')==old(f).replace('\r\n','\n'),f
assert not newbroken-oldbroken,sorted(newbroken-oldbroken)
print(json.dumps({'status':'PASS','canonical_pages':len(urls),'download_link_occurrences_preserved':count,'preexisting_broken_links':sorted(oldbroken),'new_broken_links':sorted(newbroken-oldbroken)},ensure_ascii=True))
