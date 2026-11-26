"""Apply the V7 shared layer after existing page generators, preserving content/links."""
from pathlib import Path
from xml.etree import ElementTree as ET
import re
R=Path(__file__).resolve().parents[1]
urls=[e.text for e in ET.parse(R/'sitemap.xml').getroot().iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
for url in urls:
 route=url.removeprefix('https://alghad.digital').strip('/')
 p=R/route/'index.html';s=p.read_text(encoding='utf8');en=route=='en' or route.startswith('en/')
 s=re.sub(r'<!-- V7_(?:BOOT|ASSETS)_BEGIN -->[\s\S]*?<!-- V7_(?:BOOT|ASSETS)_END -->','',s)
 s=re.sub(r'<meta name="color-scheme" content="[^"]*">','<meta name="color-scheme" content="dark light">',s)
 s=s.replace("worker-src 'none'","worker-src 'self'")
 boot='<!-- V7_BOOT_BEGIN --><script src="/assets/v7-theme.js?v=7.0.0"></script><!-- V7_BOOT_END -->'
 assert s.count('</title>')==1
 s,n=re.subn(r'(<meta charset="utf-8">)',lambda m:m.group(1)+boot,s,count=1);assert n==1
 assets='<!-- V7_ASSETS_BEGIN --><link rel="stylesheet" href="/assets/fonts/plex.css?v=5.3.0"><link rel="stylesheet" href="/assets/v7.css?v=7.0.0"><script defer src="/assets/v7.js?v=7.0.0"></script><!-- V7_ASSETS_END -->'
 assert s.count('</head>')==1
 s=s.replace('</head>',assets+'</head>',1)
 if route=='':
  # Named generic containers need an accessible group role.
  for target in ('micro-strip','release-showcase','featured-cards','technology-news-grid','contact-points'):
   pat=r'<div\b[^>]*\baria-label="[^"]+"[^>]*>'
   def name_group(m):
    tag=m.group(0)
    if re.search(r'(?:id|class)="[^"]*\b'+re.escape(target)+r'\b[^"]*"',tag) and not re.search(r'\brole=',tag):
     return tag.replace('<div','<div role="group"',1)
    return tag
   s=re.sub(pat,name_group,s)
  s=re.sub(r'(<img[^>]*src="assets/previews/[^"]+"[^>]*?)loading="eager"',r'\g<1>loading="lazy"',s)
  if 'data-v7-about' not in s:
   s=s.replace('</nav>','<a data-v7-about class="nav-link" href="/about/">من نحن</a></nav>',1)
  s,n=re.subn(r'(<h1 id="hero-title">).*?(</h1>)',r'\g<1>تقنيات اليوم.<br><span class="gradient-text">حلول الغد.</span>\g<2>',s,count=1,flags=re.S);assert n==1
  s,n=re.subn(r'(<p class="hero-description">).*?(</p>)',r'\g<1>منصة رقمية تجمع الحلول البرمجية والأدوات التقنية المبتكرة وأحدث مستجدات التكنولوجيا في مكان واحد.\g<2>',s,count=1,flags=re.S);assert n==1
  s=s.replace('class="button button-secondary button-lg" href="#contact"','class="button button-secondary button-lg" href="/top-5/"',1)
  s=re.sub(r'(<a class="button button-secondary button-lg" href="/top-5/">).*?(</a>)',r'\g<1>أحدث الأخبار <span aria-hidden="true">←</span>\g<2>',s,count=1)
 elif route=='en':
  if 'data-v7-about' not in s:
   s=s.replace('</nav>','<a data-v7-about href="/en/about/">About</a></nav>',1)
  s=s.replace('href="/en/#downloads"','href="#downloads"',1)
  s,n=re.subn(r'(<div class="en-hero-copy">[\s\S]*?<h1>).*?(</h1>)',r'\g<1>Today’s technology.<br><span>Tomorrow’s solutions.</span>\g<2>',s,count=1);assert n==1
  s=s.replace('class="en-btn en-btn-outline" href="#downloads">Official downloads','class="en-btn en-btn-outline" href="/en/top-5/">Latest news',1)
 p.write_text(s,encoding='utf8',newline='\n')
print("V7_BUILD_PASS",len(urls))
