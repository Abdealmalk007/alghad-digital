#!/usr/bin/env python3
"""Idempotent, evidence-based SEO enrichment for the Arabic/English site.

Run after all HTML generators and before build_site_search.py.
No invented review ratings, no artificial indexing promises, no keyword stuffing.
Python 3.12+, stdlib only.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://alghad.digital"
AR_TITLE = "الغد ديجتال (جيل الغد) | برامج Pro Tech لويندوز وأندرويد"
AR_DESCRIPTION = (
    "الغد ديجتال (جيل الغد) يعرض برامج ProTech (بروتك) لويندوز وأندرويد: "
    "تحليل Excel والموارد البشرية والرخام والبورسلان والعقود والتقارير، "
    "مع روابط الإصدارات التجريبية الرسمية."
)
EN_TITLE = "Alghad Digital | ProTech Software for Windows & Android"
EN_DESCRIPTION = (
    "Explore ProTech software on Alghad Digital (Jil Al Ghad): "
    "Excel analytics, HR, stone operations, quotations, contracts and reports, "
    "with clearly labeled Windows and Android preview downloads."
)
AR_HERO_IDENTITY = "الغد ديجتال (جيل الغد) هو موقع برامج ProTech (بروتك). "
EN_HERO_NOTE = (
    "Alghad Digital (Jil Al Ghad / جيل الغد) showcases ProTech applications "
    "with clearly labeled previews and official GitHub downloads."
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, source: str) -> bool:
    target = ROOT / path
    original = target.read_text(encoding="utf-8")
    if original == source:
        return False
    target.write_text(source, encoding="utf-8", newline="\n")
    return True


def replace_single(source: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, lambda _: replacement, source, count=1, flags=re.S)
    if count != 1:
        raise ValueError(f"{label}: expected one target, got {count}")
    return updated


def patch_head_meta(html: str, *, title: str, description: str) -> str:
    head, rest = html.split("</head>", 1)
    enc_title, enc_description = escape(title, quote=True), escape(description, quote=True)
    head = replace_single(head, r"<title>[^<]*</title>", f"<title>{enc_title}</title>", "title")
    for name, value in (
        ("description", enc_description),
        ("og:title", enc_title),
        ("og:description", enc_description),
        ("twitter:title", enc_title),
    ):
        field = "name" if name in {"description", "twitter:title"} else "property"
        pattern = rf'<meta {field}="{re.escape(name)}" content="[^"]*">'
        head = replace_single(head, pattern,
                              f'<meta {field}="{name}" content="{value}">',
                              f"head {name}")
    if '<meta name="twitter:description"' in head:
        head = replace_single(
            head,
            r'<meta name="twitter:description" content="[^"]*">',
            f'<meta name="twitter:description" content="{enc_description}">',
            "twitter description",
        )
    return head + "</head>" + rest


def change_arabic_home() -> None:
    source = read("index.html")
    source = patch_head_meta(source, title=AR_TITLE, description=AR_DESCRIPTION)
    if AR_HERO_IDENTITY not in source:
        source, count = re.subn(
            r'(<p class="hero-description">)([^<]*)(</p>)',
            lambda m: m.group(1) + escape(AR_HERO_IDENTITY, quote=False) + m.group(2) + m.group(3),
            source, count=1,
        )
        if count != 1:
            raise ValueError("Arabic hero brand: missing unique introduction")

    match = re.search(
        r'<!-- SEO JSONLD START --><script type="application/ld\+json">(.*?)</script><!-- SEO JSONLD END -->',
        source,
        flags=re.S,
    )
    if not match:
        raise ValueError("Arabic WebSite + Organization schema not found")
    graph = json.loads(match.group(1))
    website = next((x for x in graph["@graph"] if x["@type"] == "WebSite"), None)
    if website is None:
        raise ValueError("Arabic primary WebSite identity not found")
    if website["name"] != "الغد ديجتال" or website["url"] != DOMAIN + "/":
        raise ValueError("Unexpected canonical brand; refusing to rename")
    aliases = list(website.get("alternateName", []))
    for alias in ("جيل الغد", "Jil Al Ghad", "Alghad Digital", "alghad.digital"):
        if alias not in aliases:
            aliases.insert(-1 if aliases and aliases[-1] == "alghad.digital" else len(aliases), alias)
    website["alternateName"] = aliases
    serial = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    source = source[:match.start(1)] + serial + source[match.end(1):]
    print("AR_HOME_BRAND_SYNC", "changed" if write("index.html", source) else "unchanged")


def change_english_home() -> None:
    source = read("en/index.html")
    source = patch_head_meta(source, title=EN_TITLE, description=EN_DESCRIPTION)
    source = replace_single(
        source, r'<p class="en-hero-note">[^<]*</p>',
        f'<p class="en-hero-note">{escape(EN_HERO_NOTE, quote=False)}</p>',
        "English visible site identity",
    )
    # Only the root domain declares WebSite schema. /en/ describes its localized WebPage.
    pattern = r'<script type="application/ld\+json">(\{[^<]*"@type":"(?:WebSite|WebPage)"[^<]*\})</script>'
    matches = list(re.finditer(pattern, source, flags=re.S))
    if len(matches) != 1:
        raise ValueError("English homepage identity schema missing or ambiguous")
    page = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": DOMAIN + "/en/#webpage",
        "url": DOMAIN + "/en/",
        "name": EN_TITLE,
        "description": EN_DESCRIPTION,
        "inLanguage": "en",
        "isPartOf": {"@id": DOMAIN + "/#website"},
        "about": {"@id": DOMAIN + "/#protech"},
        "publisher": {"@id": DOMAIN + "/#protech"},
    }
    serial = json.dumps(page, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    source = source[:matches[0].start(1)] + serial + source[matches[0].end(1):]
    print("EN_HOME_BRAND_SYNC", "changed" if write("en/index.html", source) else "unchanged")


def newest_date(entries: list[dict]) -> str | None:
    now = datetime.now(timezone.utc)
    valid = []
    for entry in entries:
        value = entry.get("published_at")
        if not value:
            continue
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            continue
        if stamp.tzinfo is None or stamp > now:
            continue
        valid.append(stamp)
    return max(valid).date().isoformat() if valid else None


def topical_sitemap_lastmod() -> None:
    # Real source article publish dates, rather than the time the generator ran.
    general = json.loads(read("assets/news.json"))
    specialized = json.loads(read("assets/industry-news.json"))
    topics = specialized["topics"]
    topic_dates = {"/news/": newest_date(general["articles"])}
    topic_dates["/ai-news/"] = newest_date(topics["ai"]["articles"])
    topic_dates["/tech-companies/"] = newest_date(topics["companies"]["articles"])
    topic_dates["/cars/"] = newest_date(topics["cars"]["articles"])
    all_official = [x for topic in ("ai", "companies", "cars") for x in topics[topic]["articles"]]
    topic_dates["/en/news/"] = newest_date(all_official)
    for slug in ("/ai-news/", "/tech-companies/", "/cars/"):
        topic_dates["/en" + slug] = topic_dates[slug]
    # The homepage shows a dynamic news digest, so it also changes on new articles.
    topic_dates["/"] = newest_date(general["articles"] + all_official)
    topic_dates["/en/"] = newest_date(all_official)

    sitemap = ROOT / "sitemap.xml"
    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    tree = ET.parse(sitemap)
    urls = tree.findall(f"./{ns}url")
    if len(urls) != 42:
        raise ValueError("Expected exactly 42 canonical URLs")
    updated = 0
    for node in urls:
        loc = node.findtext(f"{ns}loc", "")
        route = loc.removeprefix(DOMAIN)
        date = topic_dates.get(route)
        old = node.find(f"{ns}lastmod")
        if date:
            if old is None:
                old = ET.SubElement(node, f"{ns}lastmod")
            old.text = date
            updated += 1
        elif old is not None:
            node.remove(old)
    ET.indent(tree, space="  ")
    text = ET.tostring(tree.getroot(), encoding="unicode")
    result = "<?xml version='1.0' encoding='utf8'?>\n" + text + "\n"
    print("SITEMAP_REAL_PUBLISHED_DATES", updated, "changed" if write("sitemap.xml", result) else "unchanged")


def main() -> None:
    change_arabic_home()
    change_english_home()
    topical_sitemap_lastmod()
    print("SEO_BRAND_VISIBILITY_READY")


if __name__ == "__main__":
    main()
