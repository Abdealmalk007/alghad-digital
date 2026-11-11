#!/usr/bin/env python3
"""Validate crawlability, metadata and generated pages before deployment."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import re
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE="https://alghad.digital"
ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
root=ET.parse(ROOT/"sitemap.xml").getroot()
urls=[x.text for x in root.findall("s:url/s:loc",ns)]
assert len(urls)==38,urls
assert len(set(urls))==len(urls)
assert urls[0]==BASE+"/"
assert all(urlsplit(url).scheme=="https" and urlsplit(url).netloc=="alghad.digital" for url in urls)
all_pages=[]
for url in urls[:19]:
    path=(urlsplit(url).path or "/").lstrip("/")
    document=ROOT/path/"index.html"
    assert document.is_file(),str(document)
    raw=document.read_text(encoding="utf-8")
    assert len(raw)>900 and '<html lang="ar" dir="rtl">' in raw
    assert raw.count("<h1")==1
    assert raw.count("<title>")==1
    assert "<meta name=\"description\"" in raw
    assert f'<link rel="canonical" href="{url}">' in raw
    assert "noindex" not in raw.lower()
    assert "Call Recorder PRO" not in raw and "مطبخ ريم" not in raw
    script=re.search(r'<script type="application/ld\+json">(.+?)</script>',raw,re.S)
    assert script,document
    structured=json.loads(script.group(1))
    assert structured.get("@context")=="https://schema.org"
    assert '<meta property="og:image" content="https://alghad.digital/assets/social/alghad-digital.png">' in raw,document
    assert '<meta name="twitter:card" content="summary_large_image">' in raw,document
    schemas=[json.loads(a) for a in re.findall(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S)]
    breadcrumbs=[a for a in schemas if a.get("@type")=="BreadcrumbList"]
    if document != ROOT/"index.html":
        assert len(breadcrumbs)==1,document
        assert breadcrumbs[0]["itemListElement"][-1]["item"]==url,document
    all_pages.append(raw)
text="\n".join(all_pages)
assert "الغد ديجتال" in all_pages[0]
assert "Download Anything PRO" in text and "Kitchen CAD Pro" in text
for slug in ("ai-news","tech-companies","cars","about","security","privacy","protech"):
    assert BASE+"/"+slug+"/" in urls,slug
    assert (ROOT/slug/"index.html").is_file(),slug
assert "ProTech HR" in text and "ProTech Stone Manager" in text
assert "Everything" in text and "Microsoft PowerToys" in text
assert "التقنية" in text
assert '<a href="programs/download/">' in all_pages[0]
assert (ROOT/"robots.txt").read_text(encoding="utf8").strip().endswith("Sitemap: https://alghad.digital/sitemap.xml")
assert (ROOT/"assets/seo-pages.css").is_file()
assert (ROOT/"assets/seo-home.css").is_file()
import struct
image_data=(ROOT/"assets/social/alghad-digital.png").read_bytes()
assert image_data[:8]==bytes.fromhex("89504e470d0a1a0a")
assert struct.unpack(">II",image_data[16:24])==(1200,630)
assert not any(("Call Recorder PRO" in s or 'instagram.com/ProTechAlghad' in s) for s in all_pages)
# Every software page must expose unique crawlable intent content and factual SoftwareApplication data.
program_files=[path for path in sorted((ROOT/"programs").glob("*/index.html"))
               if '"@type":"SoftwareApplication"' in path.read_text(encoding="utf8")]
assert len(program_files)==8
titles=set()
descriptions=set()
for program_file in program_files:
    markup=program_file.read_text(encoding="utf8")
    assert '<section class="more search-use-cases">' in markup,program_file
    assert "ماذا ينجز" in markup,program_file
    title_match=re.search(r"<title>(.*?)</title>",markup,re.S)
    description_match=re.search(r'<meta name="description" content="([^"]+)">',markup)
    app_match=re.search(r'<script type="application/ld\+json">(.*?)</script>',markup,re.S)
    assert title_match and description_match and app_match,program_file
    titles.add(title_match.group(1).strip())
    descriptions.add(description_match.group(1))
    app=json.loads(app_match.group(1))
    assert app["@type"]=="SoftwareApplication",program_file
    assert len(app.get("featureList",[]))==5,program_file
    assert len(app.get("keywords",[]))==3,program_file
assert len(titles)==8 and len(descriptions)==8
# FAQPage must describe the same real questions/answers visible to visitors.
from html import unescape
faq_markup=all_pages[0]
block=re.search(r'<!-- FAQ JSONLD START --><script type="application/ld\+json">(.*?)</script><!-- FAQ JSONLD END -->',faq_markup,re.S)
assert block,"Missing factual homepage FAQ schema"
schema=json.loads(block.group(1))
assert schema["@context"]=="https://schema.org"
assert schema["@type"]=="FAQPage"
visible_section=re.search(r'<section class="faq-section[^"]*"\s+id="faq".*?</section>',faq_markup,re.S)
assert visible_section,"Missing user-visible FAQ"
visible_entries=re.findall(r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>',visible_section.group(0),re.S)
assert len(visible_entries)==len(schema["mainEntity"])
assert len(visible_entries)>=3
def plain(markup):
    return re.sub(r'\s+',' ',unescape(re.sub(r'<[^>]+>',' ',markup)).replace('+',' ')).strip()
for (question_html,answer_html),question in zip(visible_entries,schema["mainEntity"]):
    assert question["@type"]=="Question"
    assert question["name"]==plain(question_html)
    assert question["acceptedAnswer"]["@type"]=="Answer"
    assert question["acceptedAnswer"]["text"]==plain(answer_html)
assert faq_markup.count("<!-- FAQ JSONLD START -->")==1
print("FAQ_SCHEMA_PASS VISIBLE_QUESTIONS="+str(len(visible_entries)))
print(f"SEO_TEST_PASS INDEXABLE_PAGES={len(urls)} PROGRAM_PAGES=10 GENERATOR=OK")
