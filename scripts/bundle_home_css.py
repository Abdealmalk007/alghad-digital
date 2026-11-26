"""Bundle only contiguous, same-directory stylesheets; preserve exact cascade.
Restore source tags before generators; build after generators, before tests."""
from pathlib import Path
import re, hashlib, sys
R=Path(__file__).resolve().parents[1]
P=R/"index.html"
GROUPS=[
 ("core",["assets/style.css","assets/v2.css","assets/v3.css","assets/v3_1.css","assets/downloads.css","assets/v3_3.css","assets/v3_4.css"]),
 ("secondary",["assets/seo-home.css","assets/product-first.css","assets/language.css","/assets/share.css?v=1","/assets/refinement.css?v=1"]),
]
def tags(items):return "\n".join(f'  <link rel="stylesheet" href="{x}">' for x in items)
def restore(s):
 for name,items in GROUPS:
  s=re.sub(r'<!-- CSS_BUNDLE_'+name+r'_BEGIN -->.*?<!-- CSS_BUNDLE_'+name+r'_END -->',lambda _:tags(items),s,flags=re.S)
 return s
s=restore(P.read_text(encoding="utf8"))
if "--restore" not in sys.argv:
 for name,items in GROUPS:
  original=tags(items)
  assert s.count(original)==1, name
  chunks=[]
  for src in items:
   path=R/src.split("?")[0].lstrip("/")
   content=path.read_text(encoding="utf8")
   assert not re.search(r'@import\b|@charset\b|url\s*\(',content,re.I),path
   chunks.append("/* "+path.name+" */\n"+content.rstrip()+"\n")
  payload="\n".join(chunks)
  target=R/"assets"/("home-"+name+".bundle.css")
  target.write_text(payload,encoding="utf8",newline="\n")
  digest=hashlib.sha256(payload.encode()).hexdigest()[:12]
  s=s.replace(original,f'<!-- CSS_BUNDLE_{name}_BEGIN --><link rel="stylesheet" href="/assets/{target.name}?v={digest}"><!-- CSS_BUNDLE_{name}_END -->',1)
P.write_text(s,encoding="utf8",newline="\n")
print("HOME_CSS_"+("RESTORED" if "--restore" in sys.argv else "BUNDLED"),s.count('rel="stylesheet"'))
