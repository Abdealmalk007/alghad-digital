#!/usr/bin/env python3
"""Build the fully navigable English edition of Alghad Digital.

All published downloads, version numbers, release hashes and official news URLs
come from the existing Arabic edition's trusted source data. No network calls.
Arabic remains the default at /; the English edition is under /en/.
Python 3.12+, Node.js 22+ (reads existing products/downloads via build_seo).
"""
from __future__ import annotations

import html
import importlib.util
import json
import re
import urllib.parse
from software_sources import render as render_software_sources
from build_top5 import render_body as render_top5_body
from global_tech_editorial import publisher_highlights
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="https://alghad.digital"
EN=ROOT/"en"
EN.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location("alghad_seo",ROOT/"scripts/build_seo.py")
assert spec and spec.loader
seo=importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)

def esc(v:object)->str:
    return html.escape(str(v if v is not None else ""),quote=True)

CATALOG={
 "astool":("Fleet management for Windows","Manage vehicles, drivers, fuel, maintenance, expenses and reports. Unsigned Beta for test data only; full backup and operating cards remain incomplete.",["Dashboard and analytics","Vehicles and drivers","Fuel and maintenance logs","PDF, Excel and CSV reports","Recorded document expiry alerts"]),
 "protech-music":("Android audio and music player", "Offline audio library, automatic folder categories, customizable playlists, queue/shuffle/repeat and device-supported EQ, bass and bounded loudness. Signed Android Beta; not a final build.",
   ["Accessible audio discovery","WhatsApp, Downloads, Telegram and Recordings categories","Custom playlists and bulk sharing","Queue and repeat controls","Device-supported EQ/BassBoost with safe limits"]),
 "smart-excel":("Excel data analytics","Analyze spreadsheet data and present findings using desktop reports and visualizations.",
   ["Excel data import","Data analysis and statistics","Charts and reports","Integrated 30.7.2 setup","Local login screen removed in update"]),
 "stone":("Stone and porcelain operations","Manage stone and porcelain projects, customers, material selections and operational reports.",
   ["Customer and project records","Stone and porcelain selection","Inventory and production tracking","Invoices and job documents","Operational reports"]),
 "marble":("Marble delivery management","Track marble deliveries, project stages, client details and delivery documents.",
   ["Delivery schedules","Customer and project records","Materials and measurements","Delivery documentation","Exportable reports"]),
 "reports":("Daily work reports","Record daily activities, organize project updates and share structured reports.",
   ["Daily activity records","Structured report templates","Project progress tracking","Export and sharing","Team documentation"]),
 "hr":("Human resources management","Manage employee records, attendance, leave and HR workflows.",
   ["Employee records","Attendance and leave","Payroll management","Expiry reminders","Reports and filters"]),
 "kitchen":("Kitchen design and manufacturing","Design kitchens and plan cabinets, layouts, materials and production outputs.",
   ["Room layout and openings","Cabinet catalogues","Countertops and appliances","2D and 3D visualizations","Manufacturing documents"]),
 "download":("Android video and audio downloader","An Android media download and playback project with its release status shown transparently.",
   ["Video and audio downloads","Playback controls","Playlists and favorites","Format and quality options","Media library organization"]),
 "care":("Portable Windows maintenance preview","v3.3.1 fixes responsive toolbar, RTL sidebar and Arabic labels. Includes a no-install Portable download and separate Setup launcher; neither is digitally signed. Setup installation and WinGet/AppX destructive actions remain unverified in a disposable VM.",
   ["System information","Maintenance tools","Performance diagnostics","Optional Windows app cleanup","Recovery guidance"]),
  "google-maps-reviews-tracker":("Google Maps reviews and branch reputation",
    "Track branch ratings, customer feedback and reporting. Beta preview: Google Places returns limited review samples; verified owned branches require authorized Business Profile OAuth.",
    ["Branch rating monitoring","Historical trends and comparisons","Review follow-up tools","CSV, Excel and PDF export","Official Google API adapters with access controls"]),
 "quotes":("Quotations and contracts","Customer RC3 Beta.3 adds required customer name, normalized Saudi mobile number, required address, customer search and immutable issued-document snapshots. QA tests passed; unsigned installer and third-party LGPL review remain open.",
   ["Quotation templates","Customer name, Saudi mobile and address","Customer search and dossier","Immutable issued documents","Export and preview tools"]),
}
TOOLS={
 "everything":"Instant file and folder search for Windows.",
 "ventoy":"Create a multiboot USB drive using ISO files.",
 "rufus":"Prepare bootable USB drives for operating-system installation.",
 "irfanview":"Fast image viewer with basic editing and batch processing.",
 "fileconverter":"Convert common file formats through a simple Windows interface.",
 "vlc":"Open-source media player supporting many audio and video formats.",
 "fdm":"Download manager with queueing and browser integration.",
 "powertoys":"Microsoft productivity utilities for Windows."
}
TOPICS={
 "ai-news":("Artificial Intelligence News","AI","ai","Official AI announcements, research and model releases."),
 "tech-companies":("Technology Company News","Technology Companies","companies","Official announcements from NVIDIA, AMD, Apple, Samsung, Microsoft and more."),
 "cars":("Automotive News","Automotive","cars","Updates from official automobile manufacturers and technology newsrooms."),
 "news":("Technology News","Tech News","general","Technology updates with links to their original publishers."),
}
PAGES=[
 "/","/programs/","/news/","/top-5/","/free-windows-tools/","/ai-news/",
 "/tech-companies/","/cars/","/about/","/security/","/privacy/","/protech/",
]+["/programs/"+slug+"/" for slug in CATALOG]+["/windows-office/"]
assert len(PAGES)==13+len(CATALOG)

def safe(url:str)->bool:
    parsed=urllib.parse.urlsplit(url)
    return parsed.scheme=="https" and bool(parsed.hostname) and not parsed.username and not parsed.password

def internal(url:str,label:str,css:str="")->str:
    cls=f' class="{esc(css)}"' if css else ""
    return f'<a{cls} href="{esc(url)}">{esc(label)}</a>'

def external(url:str,label:str,css:str="")->str:
    if not safe(url):return ""
    cls=f' class="{esc(css)}"' if css else ""
    return f'<a{cls} href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'

def brand_card(product:dict,download:dict,wide:bool=False)->str:
    slug=product["id"]
    tagline,summary,features=CATALOG[slug]
    release=download.get(slug,{})
    repo=release.get("repository","")
    preferred=next((f for f in release.get("files",[]) if f.get("recommended") and seo.safe_release(f.get("url",""),repo)),None)
    published=product["status"]=="public"
    badge="Beta / Preview" if preferred and published else ("Repository published" if published else "Coming soon")
    action=(external(preferred["url"],"Download" if slug!="stone" else "Download Beta (UNSIGNED)","en-btn en-btn-primary")
            if preferred and published else '<span class="en-download-unavailable">Download coming soon</span>')
    preview=product.get("preview","")
    assert re.fullmatch(r"assets/previews/[a-z0-9-]+\.(?:svg|png)",preview) and (ROOT/preview).is_file()
    status_note=("In development / experimental only. Contact us on WhatsApp or by email to ask about availability."
        if not published else "Beta/Preview release — not a final certified version. For orders or enquiries, contact us via WhatsApp or email.")
    version=esc(release.get("version") or product.get("version") or "")
    version_text=f"<span>v{version}</span>" if version and version!="-" else ""
    return f"""<article class="en-product-card" data-product="{slug}" data-category="{esc(product['status'])}" data-search="{esc(' '.join([product['title'],tagline,summary]))}">
      <a class="en-product-image" href="/en/programs/{slug}/"><img src="/{esc(preview)}" alt="Illustration of {esc(product['title'])}" width="960" height="540" loading="lazy" decoding="async"></a>
      <div class="en-product-meta"><span class="en-state {'en-state-preview' if preferred else ''}">{esc(badge)}</span>{version_text}<span>{esc(", ".join(product.get("platforms",[])))}</span></div>
      <h3>{internal('/en/programs/'+slug+'/',product['title'])}</h3>
      <p class="en-product-tagline">{esc(tagline)}</p><p>{esc(summary)}</p><p class="en-product-preview-note">{esc(status_note)}</p>
      <div class="en-product-actions"><a class="program-details" href="/en/programs/{slug}/" aria-label="Details for {esc(product['title'])}">Details</a>{action}</div>
    </article>"""

def release_info(product:dict,download:dict,facts:dict)->str:
    slug=product["id"]
    entry=download.get(slug,{})
    repo=entry.get("repository","")
    files=[x for x in entry.get("files",[]) if seo.safe_release(x.get("url",""),repo)]
    if not files:
        if product["status"]=="public":
            return '<section class="en-detail-block"><h2>Download availability</h2><p>The repository is public, but a downloadable public release has not been verified. Visit the repository for updates.</p></section>'
        return '<section class="en-detail-block"><h2>Development status</h2><p>This product is still in development. A verified public installer or APK is not available.</p></section>'
    facts_releases=facts.get("releases",{}).get(slug,{})
    listings=[]
    for item in files:
        if not isinstance(item.get("url"),str) or not safe(item["url"]):continue
        size=item["bytes"]/1048576
        verified=next((f for f in facts_releases.get("assets",[]) if f.get("url")==item["url"]),None)
        digest=(verified or {}).get("sha256")
        sha=(f'<p class="en-sha"><strong>SHA-256</strong><code>{esc(digest)}</code></p>'
             if digest and re.fullmatch("[a-f0-9]{64}",digest) else '')
        filename=item["url"].rsplit("/",1)[-1]
        if slug=="care":
            labels={
                "ProTech_Windows_Care_Setup.exe":"Portable EXE — no installation",
                "ProTech_Windows_Care_Installer_v3.3.1.exe":"Setup EXE — optional installation",
                "ProTech_Windows_Care_Portable.zip":"Portable ZIP — app and documentation",
            }
            if filename not in labels:
                raise ValueError("Unexpected Windows Care asset: "+filename)
            display_label=labels[filename]
        else:
            display_label=item.get("name") or "Release file"
        listings.append(f'<div class="en-download-item"><div><strong>{esc(display_label)}</strong><p>{size:.1f} MiB · Preview / Beta</p>{sha}</div>{external(item["url"],"Get file","en-btn en-btn-primary")}</div>')
    if not listings:return ""
    checksum=external(entry.get("checksum",""),"Official checksums") if seo.safe_release(entry.get("checksum",""),repo) else ""
    return f'<section class="en-detail-block"><h2>Official preview downloads</h2><p>These are preview releases, not guaranteed stable versions. Verify file hashes when provided. A release file does not imply code-signing or malware certification.</p>{"".join(listings)}{checksum}</section>'

def page(path:str,title:str,description:str,content:str,structured:dict|None=None)->None:
    assert path in PAGES,path
    relative=path.lstrip("/")
    en_url=DOMAIN+"/en/"+relative
    ar_url=DOMAIN+path
    filename=EN/relative/"index.html" if relative else EN/"index.html"
    filename.parent.mkdir(parents=True,exist_ok=True)
    schema_json=""
    if structured:
        schema_json=('<script type="application/ld+json">'
            +json.dumps(structured,ensure_ascii=False,separators=(",",":")).replace("<","\\u003c")
            +'</script>')
    nav=''.join([
        internal("/en/","Home"),
        internal("/en/programs/","Our Software"),
        internal("/en/windows-office/","Windows & Office Programs"),
        internal("/en/#downloads","Downloads"),
        internal("/en/free-windows-tools/","Free Windows Tools"),
        internal("/en/top-5/","TOP 5"),
        internal("/en/protech/","ProTech"),
    ])
    extra_css = '<link rel="stylesheet" href="/assets/top5-hub.css?v=1">' if path == "/top-5/" else ""
    html_doc=f"""<!doctype html>
<html lang="en" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="color-scheme" content="dark">
  <meta name="theme-color" content="#071725">
  <meta name="description" content="{esc(description[:185])}">
  <meta name="author" content="ProTech">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
  <title>{esc(title)}</title>
  <link rel="canonical" href="{esc(en_url)}">
  <link rel="alternate" hreflang="en" href="{esc(en_url)}">
  <link rel="alternate" hreflang="ar" href="{esc(ar_url)}">
  <link rel="alternate" hreflang="x-default" href="{esc(ar_url)}">
  <link rel="icon" href="/favicon.ico?v=4" sizes="any">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg?v=4">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=4">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/assets/en.css">{extra_css}
  <link rel="stylesheet" href="/assets/global-tech-sources.css?v=1"><link rel="stylesheet" href="/assets/home-redesign-v4.css?v=1"><link rel="stylesheet" href="/assets/hero-adfree-v5.css?v=1">
  <link rel="stylesheet" href="/assets/share.css?v=1">
  <link rel="stylesheet" href="/assets/refinement.css?v=1">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Alghad Digital">
  <meta property="og:locale" content="en_US">
  <meta property="og:url" content="{esc(en_url)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description[:185])}">
  <meta property="og:image" content="{DOMAIN}/assets/social/alghad-digital.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:image" content="{DOMAIN}/assets/social/alghad-digital.png">
  {schema_json}
</head>
<body>
  <a class="en-skip" href="#content">Skip to content</a>
  <header class="en-header">
    <div class="en-shell en-topbar">
      <a href="/en/" class="en-brand" aria-label="Alghad Digital English home">
        <img src="/icon-192.png?v=4" width="46" height="46" alt="">
        <span>ALGHAD <em>DIGITAL</em><small>PROTECH SOFTWARE</small></span>
      </a>
      <nav class="en-nav" aria-label="Primary navigation">{nav}</nav>
      <a class="en-lang-switch" href="{esc(ar_url)}" hreflang="ar" lang="ar" dir="rtl" aria-label="العربية - switch to Arabic">AR <span aria-hidden="true">🌐</span></a>
    </div>
  </header>
  <main class="en-shell en-main" id="content">{content}</main>
  <footer class="en-footer"><div class="en-shell en-footer-inner">
    <div><strong>Alghad Digital</strong><p>ProTech software for business, design and productivity.</p></div>
    <nav aria-label="Footer navigation">{internal("/en/about/","About")} {internal("/en/privacy/","Privacy")} {internal("/en/security/","Software safety")} {internal("/en/protech/","Developer")} {internal("/","العربية (AR)")}</nav>
    <a href="mailto:protech.2025.2026@gmail.com">protech.2025.2026@gmail.com</a>
    <p class="program-rights">© 2026 ProTech · Alghad Digital. All Rights Reserved. Existing open-source licenses remain applicable.</p>
  </footer>
  <script defer src="/assets/share.js?v=1"></script>
</body>
</html>
"""
    filename.write_text(html_doc,encoding="utf8",newline="\n")

def hero(kicker:str,title:str,summary:str)->str:
    return f'<div class="en-heading"><span class="en-kicker">{esc(kicker)}</span><h1>{esc(title)}</h1><p>{esc(summary)}</p></div>'

def section(title:str,text:str)->str:
    return f'<section class="en-info-block"><h2>{esc(title)}</h2><p>{esc(text)}</p></section>'

def news_cards(items:list[dict],limit:int=18)->str:
    entries=[]
    seen=set()
    for item in items:
        url=item.get("url","")
        title=item.get("title","")
        if not safe(url) or not title or url in seen:continue
        # Preserve official English as-is; Arabic-only source stories belong to the Arabic edition.
        if not re.search(r"[A-Za-z]{3}",title) or len(re.findall(r"[\u0621-\u064a]",title))>10:continue
        seen.add(url)
        source=item.get("source_name","Original publisher")
        date=str(item.get("published_at",""))[:10]
        entries.append(f'<article class="en-news-card"><div class="en-product-meta"><span>{esc(source)}</span><time datetime="{esc(date)}">{esc(date)}</time></div><h3>{external(url,title)}</h3><p>Read the original article on the publisher’s website.</p></article>')
        if len(entries)>=limit:break
    return '<div class="en-news-grid">' + "".join(entries) + '</div>' if entries else "<p>No recent English headlines from verified sources are available at the moment.</p>"

def render_home(products:list[dict],downloads:dict,industry:dict,tools:dict)->None:
    cards=''.join(brand_card(p,downloads) for p in products)
    releases=[]
    for p in products:
        slug=p["id"]
        entry=downloads.get(slug,{})
        preferred=next((f for f in entry.get("files",[]) if f.get("recommended") and seo.safe_release(f.get("url",""),entry.get("repository",""))),None)
        if preferred:
            releases.append(f'<article class="en-release-card"><div><strong>{esc(p["title"])}</strong><p>Preview v{esc(entry.get("version",""))} · {esc(", ".join(p.get("platforms",[])))}</p></div>{external(preferred["url"],"Download preview","en-btn en-btn-primary")}</article>')
    expected_releases = sum(
        any(f.get("recommended") and seo.safe_release(
            f.get("url", ""), downloads.get(p["id"], {}).get("repository", "")
        ) for f in downloads.get(p["id"], {}).get("files", []))
        for p in products
    )
    assert len(releases) == expected_releases
    from_news=industry["topics"]["ai"]["articles"][:3]+industry["topics"]["companies"]["articles"][:3]
    home=f"""
    <section class="en-hero">
      <div class="en-hero-copy"><span class="en-kicker">DESIGN · BUILD · PRODUCTIVITY</span>
        <h1>Software that helps you <span>work smarter.</span></h1>
        <p>Discover practical tools for business management, data analytics, teams and everyday operations. Compare products and find clearly labeled preview releases.</p>
        <div class="v5-clean-experience" role="note" aria-label="Focused software experience"><span class="v5-clean-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2 4 5v7c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V5l-8-3z"/><path d="m8 12 3 3 5-6"/></svg></span><div><strong>No intrusive ads. No distractions.</strong><p>Our design goal is focused, easy-to-use software without disruptive in-app advertising. Ad-free claims for individual releases require verification.</p><span class="v5-clean-kicker">USER-FIRST · AD-FREE DESIGN GOAL</span></div></div>
        <div class="en-actions">{internal("/en/programs/","Explore our software","en-btn en-btn-primary")}{internal("#downloads","Official downloads","en-btn en-btn-outline")}</div>
        <p class="en-hero-note">Clearly labeled preview releases · Official GitHub downloads</p>
      </div>
      <div class="en-hero-visual v4-en-portfolio v5-showcase" aria-label="ProTech software categories">
        <div class="v4-panel-heading"><span class="v4-panel-eyebrow">PROTECH SOFTWARE COLLECTION</span><strong>One collection. Many possibilities.</strong><p>Choose an area and explore ProTech software, features and available releases.</p></div>
        <div class="v4-panel-grid">
          <a class="v4-panel-tile" href="/en/programs/" aria-label="Explore People &amp; HR software"><span class="v4-panel-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 5v1"/></svg></span><span><b>People &amp; HR</b><small>TEAMS &amp; WORKFORCE</small></span></a>
          <a class="v4-panel-tile" href="/en/programs/" aria-label="Explore Data &amp; analytics software"><span class="v4-panel-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 3v18M12 17l3-4 2 1 2-3"/></svg></span><span><b>Data &amp; analytics</b><small>DATA &amp; INSIGHTS</small></span></a>
          <a class="v4-panel-tile" href="/en/programs/" aria-label="Explore Contracts &amp; reports software"><span class="v4-panel-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 2h7l5 5v15H7zM14 2v6h5M10 12h6M10 16h5M3 7v14"/></svg></span><span><b>Contracts &amp; reports</b><small>DOCUMENTS &amp; REPORTS</small></span></a>
          <a class="v4-panel-tile" href="/en/programs/" aria-label="Explore Materials &amp; production software"><span class="v4-panel-symbol" aria-hidden="true"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="m12 2 10 5-10 5L2 7l10-5zm-10 10 10 5 10-5M2 17l10 5 10-5"/></svg></span><span><b>Materials &amp; production</b><small>OPERATIONS</small></span></a>
        </div><div class="v4-en-portfolio-foot"><span class="v5-panel-label">PROTECH APPLICATIONS</span><a class="v5-panel-all" href="/en/programs/">EXPLORE ALL <span aria-hidden="true">↗</span></a></div>
      </div>
    </section>
    <section class="en-section" id="programs">
      <div class="en-section-heading"><div><span class="en-kicker">01 / OUR PRODUCTS</span><h2>Explore ProTech software</h2><p>All available projects, clearly labeled by release status.</p></div><span class="en-stat">Software collection</span></div>
      <div class="en-toolbar"><label for="en-search">Search software <input id="en-search" type="search" placeholder="Search by name or feature" autocomplete="off"></label>
      <div class="en-filter" role="group" aria-label="Filter by status"><button type="button" class="is-selected" data-en-filter="all" aria-pressed="true">All</button><button type="button" data-en-filter="public" aria-pressed="false">Published</button><button type="button" data-en-filter="dev" aria-pressed="false">In development</button></div></div>
      <p class="en-no-results" id="en-empty" hidden>No products match your search.</p>
      <div class="en-grid" id="en-catalog">{cards}</div>
    </section>
    <section class="en-section" id="downloads"><div class="en-section-heading"><div><span class="en-kicker">02 / VERIFIED RELEASES</span><h2>Official downloads</h2><p>Download files from our verified GitHub Releases. All listed builds are preview releases, not certified stable editions.</p></div></div><div class="en-release-grid">{"".join(releases)}</div></section>
    <section class="en-section" id="trust"><div class="en-section-heading"><div><span class="en-kicker">03 / TRANSPARENCY</span><h2>Know what you install</h2></div></div><div class="en-info-grid">{section("Verified release links","Download from official GitHub Releases and review checksums where available.")}{section("Transparent statuses","Published projects without verified files are never presented as downloadable.")}{section("Windows and Android","The portfolio covers desktop, mobile and design workflows without claiming every project is complete.")}</div></section>
    <section class="en-section en-news-secondary" id="news"><div class="en-section-heading"><div><span class="en-kicker">04 / TOP 5 NEWS</span><h2>TOP 5 — technology by category</h2><p>A short selection of official English headlines. Articles belong to their original publishers.</p></div></div>{news_cards(from_news,6)}
      <div class="en-news-links">{internal("/en/ai-news/","AI updates")}{internal("/en/tech-companies/","Tech companies")}{internal("/en/cars/","Automotive")}{internal("/en/top-5/","Explore all TOP 5 categories")}</div>
    </section>
    <section class="en-section en-contact" id="contact"><h2>Need more information?</h2><p>Contact ProTech about a product, release status or business software.</p><a class="en-btn en-btn-primary" href="mailto:protech.2025.2026@gmail.com">Email ProTech</a></section>
    <script defer src="/assets/en.js"></script>
    """
    page("/","ProTech Software for Business & Design | Alghad Digital",
         "Discover ProTech software, verified preview downloads, kitchen design, stone management and productivity tools. Official English website.",home,
         {"@context":"https://schema.org","@type":"WebSite","name":"Alghad Digital","url":DOMAIN+"/en/","inLanguage":"en","publisher":{"@type":"Organization","name":"ProTech"}})

def render_top5_page()->None:
    cfg=json.loads((ROOT/"config/top5_categories.json").read_text(encoding="utf8"))
    data=json.loads((ROOT/"assets/top5-news.json").read_text(encoding="utf8"))
    body=render_top5_body("en",cfg,data)
    title="TOP 5 Technology News by Category | Alghad Digital"
    desc="Explore top five verified tech stories by category: Android, Windows, macOS, computers, AI, cybersecurity, software, emerging technology, cars and smartphones."
    schema={"@context":"https://schema.org","@type":"CollectionPage","name":title,
            "url":DOMAIN+"/en/top-5/","inLanguage":"en","description":desc}
    page("/top-5/",title,desc,body,schema)

def render_catalog(products:list[dict],downloads:dict)->None:
    body=hero("OUR SOFTWARE / PROTECH","Software library","Explore ProTech applications across the full catalog. Published preview downloads are distinguished from projects still under development.")
    body+='<div class="en-grid">' + ''.join(brand_card(p,downloads) for p in products)+'</div>'
    page("/programs/","ProTech Software Library | Alghad Digital","Explore ProTech Windows and Android products, download availability and development status.",body,{"@context":"https://schema.org","@type":"CollectionPage","name":"ProTech Software Library","url":DOMAIN+"/en/programs/"})

def render_windows_office()->None:
    title="Windows & Office Programs"
    body=hero("WINDOWS & OFFICE / MICROSOFT DIRECT MEDIA",title,
        "Download verified original Windows ISO and Office IMG files in Arabic or English, "
        "directly from Microsoft CDNs with no third-party landing pages.")
    body+=render_software_sources("en")
    page("/windows-office/",title+" | Alghad Digital",
        "Direct official Microsoft ISO and IMG files for Windows 11 and Office in Arabic and English. No third-party redirects.",
        body,{"@context":"https://schema.org","@type":"CollectionPage",
              "name":title,"url":DOMAIN+"/en/windows-office/","inLanguage":"en"})
    destination=ROOT/"en/windows-office/index.html"
    html=destination.read_text(encoding="utf-8")
    html=html.replace("</head>",
        '<link rel="stylesheet" href="/assets/microsoft-direct.css?v=1">\n</head>', 1)
    destination.write_text(html,encoding="utf-8",newline="\n")

def render_product(product:dict,downloads:dict,facts:dict)->None:
    slug=product["id"]
    tagline,summary,features=CATALOG[slug]
    image=product["preview"]
    facts_html=release_info(product,downloads,facts)
    state="Published — preview release" if downloads.get(slug,{}).get("files") else "In development" if product["status"]=="dev" else "Published repository; no verified public installer"
    if slug in ("stone","quotes") and downloads.get(slug,{}).get("files"):state="Beta / Preview — UNSIGNED Windows installer"
    if slug=="care" and downloads.get(slug,{}).get("files"):state="Portable + Setup — UNSIGNED Preview"
    preview_note=("Under development and experimental; no final production-ready edition is available. For requests or enquiries, contact us via WhatsApp or email."
        if product["status"]=="dev" else
        "Experimental Beta/Preview — not a final certified release. For orders or enquiries about this program, contact us via WhatsApp or email.")
    features_html="".join(f"<li>{esc(v)}</li>" for v in features)
    entry=downloads.get(slug,{})
    preferred=next((f for f in entry.get("files",[]) if f.get("recommended") and seo.safe_release(f.get("url",""),entry.get("repository",""))),None)
    direct=external(preferred["url"],"Download Beta (UNSIGNED)" if slug in ("stone","quotes") else "Download Portable EXE" if slug=="care" else "Download","en-btn en-btn-primary") if preferred else '<span class="en-download-unavailable">Download coming soon</span>'
    content=f"""
      <div class="en-breadcrumbs">{internal("/en/","Home")} / {internal("/en/programs/","Software")} / {esc(product['title'])}</div>
      <div class="en-detail-layout"><div>{hero("PROTECH SOFTWARE · "+", ".join(product["platforms"]),product["title"],summary)}
        <div class="en-chips"><span>{esc(state)}</span><span>{esc(", ".join(product["platforms"]))}</span></div>
        <h2>What it does</h2><p>{esc(tagline)} — {esc(summary)}</p><p class="en-detail-beta-note">{esc(preview_note)}</p>
        <h2>Key capabilities</h2><ul class="en-features">{features_html}</ul>
        <div class="en-actions">{direct}</div>
      </div><aside class="en-detail-image"><img src="/{esc(image)}" alt="Illustration of {esc(product['title'])}" width="960" height="540" loading="lazy"><p>Illustrative project artwork; not a verified application screenshot.</p></aside></div>
      {facts_html}
      {seo.program_documentation(product, english=True)}
      <section class="en-info-block"><h2>Questions and release information</h2>
        <details><summary>Is this a final stable release?</summary><p>Current publicly downloadable files are marked Preview/Beta. Check release notes and test before production use.</p></details>
        <details><summary>How can I verify the download?</summary><p>Read the <a href="/en/security/">software safety guide</a> for SHA-256 verification and release checks.</p></details>
        <details><summary>How do I request a program or ask questions?</summary><p>Use the WhatsApp contact button or email ProTech on this page. All programs are currently experimental or under development.</p></details>
        <details><summary>Where can I follow development?</summary><p>Use the official <a href="/en/programs/">software library</a> and the <a href="/en/protech/">ProTech developer page</a>.</p></details>
      </section>"""
    schema={"@context":"https://schema.org","@type":"SoftwareApplication","name":product["title"],
        "description":summary,"url":DOMAIN+"/en/programs/"+slug+"/","image":DOMAIN+"/"+image,
        "publisher":{"@type":"Organization","name":"ProTech","url":DOMAIN+"/en/protech/"},
        "operatingSystem":", ".join(product["platforms"]),
        "applicationCategory":"BusinessApplication" if slug in {"stone","marble","reports","hr","quotes"} else "UtilitiesApplication",
        "featureList":features}
    if product.get("version") and product["version"]!="—":schema["softwareVersion"]=product["version"]
    if seo.safe_repo(product.get("github","")):schema["sameAs"]=product["github"]
    release=downloads.get(slug,{})
    preferred=next((x for x in release.get("files",[]) if x.get("recommended") and seo.safe_release(x.get("url",""),release.get("repository",""))),None)
    if preferred:schema["downloadUrl"]=preferred["url"]
    page("/programs/"+slug+"/",product["title"]+" — "+tagline+" | ProTech",
         f"{product['title']}: {summary} Release status, key features and official download links.",content,schema)

def render_news(industry:dict)->None:
    for slug,(title,label,key,desc) in TOPICS.items():
        if key=="general":
            articles=industry["topics"]["ai"]["articles"][:8]+industry["topics"]["companies"]["articles"][:8]+industry["topics"]["cars"]["articles"][:8]
            note="The Arabic edition additionally covers news from Arabic-language technology publishers. Original-language articles are available through the Arabic version."
        else:
            articles=industry["topics"][key]["articles"]
            note="All headlines are from original publisher websites. Some newsrooms offer links only, with no confirmed RSS feed."
        body=hero("OFFICIAL NEWSROOMS / TECH UPDATES",title,desc)
        if key=="general":
            general=json.loads((ROOT/"assets/news.json").read_text(encoding="utf8"))
            global_ids=("theverge","techcrunch","arstechnica","wired","engadget")
            directory=[s for sid in global_ids for s in general.get("sources",[]) if s["id"]==sid]
            links="".join('<a href="'+esc(s["url"])+'" target="_blank" rel="noopener noreferrer">'+esc(s["name"])+' ↗</a>' for s in directory)
            body+='<section class="global-tech-sources"><h2>Five leading global tech news sources</h2><p>Original publisher links; headlines are collected when their official feeds respond.</p><nav class="global-tech-source-links" aria-label="Global technology publishers">'+links+'</nav></section>'
            top_stories=publisher_highlights(general.get("articles",[]),each=2)
            if top_stories:
                body+='<section class="global-tech-headlines"><h2>Top stories from global technology publishers</h2><p>Headlines with publisher, publication date and direct links to the original reports. Arabic translations are available in the Arabic edition.</p>'+news_cards(top_stories,limit=10)+'</section>'
        body+=f'<p class="en-explainer">{esc(note)}</p>'+news_cards(articles)
        body+='<div class="en-news-links">'+''.join(internal("/en/"+s+"/",name) for s,name in [("ai-news","AI news"),("tech-companies","Tech companies"),("cars","Automotive news"),("news","All news")])+'</div>'
        page("/"+slug+"/",title+" | Alghad Digital",desc+" Latest original English-language headlines and official sources.",body,{"@context":"https://schema.org","@type":"CollectionPage","name":title,"url":DOMAIN+"/en/"+slug+"/","inLanguage":"en"})

def render_tools(tools:dict)->None:
    entries=[]
    for tool in tools["items"]:
        url=tool.get("url","")
        if not safe(url):continue
        desc=TOOLS.get(tool["id"],"Free Windows software; refer to the official site for details.")
        image=tool.get("image","")
        if not re.fullmatch(r"assets/tools/[a-z0-9-]+\.svg",image):continue
        entries.append(f'<article class="en-product-card"><img src="/{esc(image)}?v=vendor-1" alt="Official app icon: {esc(tool['name'])}" width="960" height="540" loading="lazy" decoding="async"><h3>{esc(tool["name"])}</h3><p>{esc(desc)}</p>{external(url,"Official website","en-inline-link")}</article>')
    assert len(entries)==8
    body=hero("FREE WINDOWS UTILITIES","Useful free Windows software","A curated directory with links to the official publishers. Authentic app icons identify their respective software; all trademarks and logo rights belong to their publishers.")
    body+='<div class="en-grid vendor-tool-grid">'+''.join(entries)+'</div>'
    page("/free-windows-tools/","Free Windows Utilities & Official Downloads | Alghad Digital",
         "Eight useful Windows applications with official website links: Everything, Ventoy, Rufus, VLC, PowerToys and more.",body)

def render_support()->None:
    content={
      "about":("About Alghad Digital","Alghad Digital showcases ProTech software, official release information and a secondary technology-news section.",
        [("Founder", seo.FOUNDER_CREDIT),
         ("What we build","ProTech develops and plans practical applications for business administration, kitchen design, stone and porcelain operations, Windows and Android."),
         ("Software first","Our primary purpose is to help visitors explore software and understand what can currently be downloaded."),
         ("Honest project status","We label preview releases and work-in-progress projects transparently. Website illustrations are not claimed to be screenshots of a finished product.")]),
      "security":("Software Download Safety","Check the publisher and available file hashes before installing downloadable software.",
        [("Official downloads","Download ProTech preview files only through the verified GitHub Releases links shown on each product page."),
         ("SHA-256 checksums","When a SHA-256 value is published, compare it with the downloaded file. On Windows, run Get-FileHash -Algorithm SHA256 against the downloaded file."),
         ("Preview releases and warnings","Beta/Preview does not mean stable. A checksum establishes file integrity against the listed digest, not that a file has been code-signed or malware-certified."),
         ("Security notices","For questions about downloads, contact protech.2025.2026@gmail.com. Do not bypass security warnings automatically.")]),
      "privacy":("Privacy Policy","Understand how this static website presents information and links to third-party destinations.",
        [("Static website","Alghad Digital is served as static pages through GitHub Pages. This site does not require an account to browse the software catalog."),
         ("Third-party destinations","Clicking GitHub release links or external publisher articles takes you to their websites, which have their own terms and privacy policies."),
         ("Contact","If you email ProTech, your message and contact information are processed through the email service for handling your inquiry."),
         ("Changes","We may update the content of this page as the website changes. No claim is made that external services collect no technical logs.")]),
      "protech":("ProTech — Software Developer","ProTech (also written Pro Tech or بروتك) is the developer behind the software showcased on Alghad Digital.",
        [("Founder", seo.FOUNDER_CREDIT),
         ("Official publisher","Alghad Digital is the website; ProTech is the developer's identity. All verified software links point to their corresponding GitHub repositories or releases."),
         ("Get in touch","For application support or inquiries: protech.2025.2026@gmail.com."),
         ("Follow the projects","Browse the official software directory for ten projects and their current release availability.")])
    }
    for slug,(title,desc,blocks) in content.items():
        body=hero("ALGHAD DIGITAL / PROTECH",title,desc)
        body+='<div class="en-info-grid">' +''.join(section(a,b) for a,b in blocks)+'</div>'
        if slug=="protech":
            body+='<h2 class="en-section-title">Software projects</h2><div class="en-grid">'+''.join(brand_card(p,downloads) for p in products)+'</div>'
        if slug=="security":
            body+='<pre class="en-code">Get-FileHash -Algorithm SHA256 "C:\\Path\\To\\Installer.exe"</pre>'
        schema = {"@context": "https://schema.org", "@type": "AboutPage",
                  "name": title, "url": DOMAIN + "/en/" + slug + "/", "inLanguage": "en"}
        if slug in ("about", "protech"):
            schema["mainEntity"] = {
                "@type": "Organization",
                "name": "Alghad Digital" if slug == "about" else "ProTech",
                "founder": seo.FOUNDER_PERSON,
            }
        page("/"+slug+"/",title+" | Alghad Digital",desc,body,schema)

def extend_sitemap()->None:
    file=ROOT/"sitemap.xml"
    ns="http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("",ns)
    tree=ET.parse(file)
    top=tree.getroot()
    assert top.tag=="{"+ns+"}urlset"
    original=[e.findtext("{"+ns+"}loc") for e in top.findall("{"+ns+"}url")]
    expected_ar={DOMAIN+x for x in PAGES}
    if set(original)!=expected_ar or len(original)!=len(PAGES):
        raise ValueError("Arabic sitemap must match generated English page count")
    for path in PAGES:
        sub=ET.SubElement(top,"{"+ns+"}url")
        ET.SubElement(sub,"{"+ns+"}loc").text=DOMAIN+"/en/"+path.lstrip("/")
    ET.indent(tree,space="  ")
    tree.write(file,encoding="utf8",xml_declaration=True)
    print("BILINGUAL_SITEMAP_URLS="+str(len(PAGES)*2))

def main()->None:
    global products,downloads
    products=seo.read_javascript_data("assets/products.js","AL_GHAD_PRODUCTS")
    downloads=seo.read_javascript_data("assets/downloads.js","AL_GHAD_DOWNLOADS")
    assert set(p["id"] for p in products)==set(CATALOG)
    product_ids = {product["id"] for product in products}
    assert len(products) == len(CATALOG) and len(product_ids) == len(CATALOG)
    assert set(downloads).issubset(product_ids), "Release entries must reference known products"
    industry=json.loads((ROOT/"assets/industry-news.json").read_text(encoding="utf8"))
    tools=json.loads((ROOT/"assets/tools.json").read_text(encoding="utf8"))
    facts=json.loads((ROOT/"assets/release-facts.json").read_text(encoding="utf8"))
    render_home(products,downloads,industry,tools)
    render_catalog(products,downloads)
    render_windows_office()
    for product in products:render_product(product,downloads,facts)
    render_news(industry)
    render_top5_page()
    render_tools(tools)
    render_support()
    created=[p for p in EN.rglob("index.html") if p != EN/"programs"/"porcelain"/"index.html"]
    assert len(created)==len(PAGES),(len(created),created)
    extend_sitemap()
    print("ENGLISH_PAGES="+str(len(created))+" ARABIC_DEFAULT=True")

if __name__=="__main__":main()
