#!/usr/bin/env python3
"""Build and inject first-party sitewide search across all canonical pages and news.
Pure Python 3.12+, no external dependencies. Safe to run on every daily refresh.
"""
from __future__ import annotations
from pathlib import Path
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urlparse
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://alghad.digital"
ASSETS = ROOT / "assets"
STYLE_TAG = '<link rel="stylesheet" href="/assets/site-search.css?v=1">'
SCRIPT_TAG = '<script defer src="/assets/site-search.js?v=1"></script>'
NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class MainText(HTMLParser):
    """Extract visible main-section text, skipping scripts/navigation and footer."""
    VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img",
                 "input", "link", "meta", "param", "source", "track", "wbr"}
    SKIP_TAGS = {"script", "style", "noscript", "svg", "form", "nav", "footer", "header"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.ignore_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.in_main = True
            return
        if not self.in_main:
            return
        if self.ignore_depth:
            if tag not in self.VOID_TAGS:
                self.ignore_depth += 1
        elif tag in self.SKIP_TAGS or dict(attrs).get("aria-hidden") == "true":
            self.ignore_depth = 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
            self.ignore_depth = 0
        elif self.in_main and self.ignore_depth:
            self.ignore_depth -= 1

    def handle_data(self, data):
        if self.in_main and not self.ignore_depth:
            word = " ".join(data.split())
            if word:
                self.parts.append(word)


def clean(value: str, limit: int = 15000) -> str:
    return " ".join(unescape(value).split())[:limit]


def extract_meta(source: str, name: str) -> str:
    for tag in re.findall(r"<meta\s+[^>]*>", source[:15000], re.I):
        if re.search(r'\bname=["\']' + re.escape(name) + r'["\']', tag, re.I):
            m = re.search(r'\bcontent=["\']([^"\']*)', tag, re.I)
            if m:
                return clean(m.group(1), 850)
    return ""


def page_record(url: str, filename: Path) -> dict:
    raw = filename.read_text(encoding="utf-8")
    title_match = re.search(r"<title>(.*?)</title>", raw, re.S | re.I)
    if not title_match:
        raise ValueError(f"Missing page title: {filename}")
    title = clean(re.sub(r"<[^>]+>", "", title_match.group(1)), 240)
    desc = extract_meta(raw, "description")
    parser = MainText()
    parser.feed(raw)
    text = clean(" ".join(parser.parts), 19000)
    if not text:
        raise ValueError(f"Missing main content: {filename}")
    path = urlparse(url).path
    kind = "program" if re.match(r"^/(?:en/)?programs/[^/]+/$", path) else "page"
    category = "البرامج / Software" if kind == "program" else "صفحات الموقع / Site pages"
    return {
        "id": "page:" + path,
        "kind": kind,
        "lang": "en" if path.startswith("/en/") else "ar",
        "title": title,
        "description": desc,
        "content": text,
        "url": path,
        "category": category,
    }


# Search terminology is confined to canonical public pages, their translations
# and already-public program README files. No private files or external crawl.
TOPIC_TERMS: dict[str, str] = {
    "/windows-office/": "ويندوز وندوز Windows Windows 11 Office اوفيس أوفيس ISO IMG ملف تنزيل تحميل Arabic English Microsoft",
    "/free-windows-tools/": "أدوات ويندوز Windows tools صيانة إصلاح تنظيف برامج مجانية free utility tools",
    "/news/": "أخبار news technology تقنية تحديثات releases reports",
    "/ai-news/": "ذكاء اصطناعي artificial intelligence AI models GPT OpenAI",
    "/tech-companies/": "شركات companies technology big tech Microsoft Google Apple",
    "/cars/": "سيارات سيارات كهربائية cars automotive vehicles",
    "/security/": "أمان أمن حماية security privacy خصوصية",
    "/privacy/": "خصوصية privacy data protection بيانات",
    "/programs/": "البرامج software apps applications التطبيقات downloads تحميل",
    "/programs/smart-excel/": "اكسل إكسل excel spreadsheet جداول تحليل analysis xlsx xls csv",
    "/programs/care/": "ويندوز windows صيانة cleaning maintenance repair تحسين تحسين الأداء",
    "/programs/quotes/": "عقد عقود contract contracts عروض عرض أسعار quotations quotes عملاء customers",
    "/programs/kitchen/": "مطابخ مطبخ kitchen CAD تصميم ثلاثي 3D 2D خزائن cabinets CNC",
    "/programs/hr/": "موظفين موظف موارد بشرية human resources payroll رواتب الحضور attendance HR",
    "/programs/stone/": "رخام بورسلان stone marble porcelain inventory stock مخزون",
    "/programs/marble/": "رخام بورسلان marble porcelain تسليم delivery",
    "/programs/reports/": "تقارير reports daily اليومية",
    "/programs/download/": "تحميل تنزيل download downloader video فيديو صوت audio Android",
}

def enrich_translations_and_guides(records: list[dict]) -> int:
    """Add bilingual counterpart content and published program-guide text.

    Keep each result linked to a real canonical page, preventing broken URLs.
    """
    pages = {item["url"]: item for item in records}
    indexed_guides = 0
    for item in records:
        route = item["url"]
        base = route[3:] if route.startswith("/en/") else route
        equivalent = base if route.startswith("/en/") else "/en" + base
        sibling = pages.get(equivalent)
        if sibling is None:
            raise ValueError(f"Missing bilingual canonical pair: {route}")
        # Pair titles, descriptions and body excerpts so Arabic and English
        # queries work from *either* locale without sending users off-site.
        aliases = [
            sibling["title"],
            sibling["description"],
            sibling["content"][:3200],
            TOPIC_TERMS.get(base, ""),
        ]
        program = re.fullmatch(r"/programs/([a-z0-9-]+)/", base)
        if program:
            guide = ROOT / "docs" / "programs" / program.group(1) / "README.md"
            if not guide.is_file():
                raise FileNotFoundError(f"Published program guide is missing: {guide}")
            guide_text = guide.read_text(encoding="utf-8-sig", errors="replace")
            if len(guide_text) > 35000:
                raise ValueError(f"Unexpectedly large public guide: {guide}")
            # Plain text only, indexed but never interpolated into HTML.
            aliases.append(clean(guide_text, 8000))
            indexed_guides += 1
        item["aliases"] = clean(" ".join(aliases), 13500)
    return indexed_guides


def article_record(article: dict, topic: str, index: int) -> dict:
    category = {
        "tech": "أخبار التقنية / Technology news",
        "ai": "الذكاء الاصطناعي / Artificial intelligence",
        "companies": "شركات التقنية / Technology companies",
        "cars": "السيارات / Cars",
    }[topic]
    path = {
        "tech": "/news/",
        "ai": "/ai-news/",
        "companies": "/tech-companies/",
        "cars": "/cars/",
    }[topic]
    title = clean(article.get("title_ar") or article.get("title") or "", 270)
    original = clean(article.get("title") or "", 270)
    source = clean(article.get("source_name") or article.get("source") or "", 130)
    if not title or not source:
        raise ValueError(f"Invalid news headline or publisher: {topic}/{index}")
    date = str(article.get("published_at") or "")[:10]
    return {
        "id": f"news:{topic}:{index}",
        "kind": "news",
        "lang": "all",
        "title": title,
        "description": original if title != original else source,
        "content": clean(" ".join([original, title, source, str(article.get("category") or "")]), 1100),
        "url": path,
        "category": category,
        "source": source,
        "date": date,
    }


def main() -> None:
    tree = ET.parse(ROOT / "sitemap.xml")
    locs = [e.findtext(NS + "loc") for e in tree.findall("./" + NS + "url")]
    if not locs or len(set(locs)) != len(locs):
        raise ValueError("Invalid, duplicate or empty sitemap")
    page_files: list[Path] = []
    results: list[dict] = []
    for url in locs:
        if not url or not url.startswith(SITE + "/"):
            raise ValueError(f"Foreign site in sitemap: {url}")
        route = urlparse(url).path
        filename = ROOT / route.lstrip("/") / "index.html"
        if not filename.is_file():
            raise FileNotFoundError(filename)
        results.append(page_record(url, filename))
        page_files.append(filename)

    guide_count = enrich_translations_and_guides(results)

    raw_news = json.loads((ASSETS / "news.json").read_text(encoding="utf-8"))
    raw_industry = json.loads((ASSETS / "industry-news.json").read_text(encoding="utf-8"))
    news = raw_news.get("articles") or []
    topics = raw_industry.get("topics") or {}
    if len(news) < 5 or set(topics) != {"ai", "companies", "cars"}:
        raise ValueError("News sources unavailable; refusing stale/incomplete search index")
    for i, item in enumerate(news):
        results.append(article_record(item, "tech", i))
    for topic in ("ai", "companies", "cars"):
        for i, item in enumerate(topics[topic]["articles"]):
            results.append(article_record(item, topic, i))

    if len(results) < len(locs) + 40:
        raise ValueError("Unexpectedly few search records")
    manifest = {
        "schema": 1,
        "site": SITE,
        "news_updated": raw_news.get("generated_at"),
        "industry_updated": raw_industry.get("generated_at"),
        "page_count": len(locs),
        "guide_count": guide_count // 2,
        "news_count": len(results) - len(locs),
        "records": results,
    }
    json_payload = json.dumps(manifest, ensure_ascii=False, separators=(",", ":"))
    json_payload = json_payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028")
    # A JavaScript payload allows loading on demand without weakening CSP connect-src 'none'.
    index_path = ASSETS / "site-search-index.js"
    index_path.write_text("window.AL_GHAD_SITE_SEARCH = " + json_payload + ";\n", encoding="utf-8", newline="\n")

    patched = 0
    for file in page_files:
        html = file.read_text(encoding="utf-8")
        original = html
        if STYLE_TAG not in html:
            if html.count("</head>") != 1:
                raise ValueError(f"Could not insert search stylesheet: {file}")
            html = html.replace("</head>", "  " + STYLE_TAG + "\n</head>", 1)
        if SCRIPT_TAG not in html:
            if html.count("</body>") != 1:
                raise ValueError(f"Could not insert search script: {file}")
            html = html.replace("</body>", "  " + SCRIPT_TAG + "\n</body>", 1)
        if html != original:
            file.write_text(html, encoding="utf-8", newline="\n")
            patched += 1
    print(
        f"SITE_SEARCH_READY PAGES={len(locs)} GUIDES={guide_count // 2} NEWS={len(results)-len(locs)} "
        f"INDEX_RECORDS={len(results)} INDEX_BYTES={index_path.stat().st_size} "
        f"PATCHED={patched}",
        flush=True,
    )


if __name__ == "__main__":
    main()
