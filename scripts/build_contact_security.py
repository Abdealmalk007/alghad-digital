#!/usr/bin/env python3
"""Harden available HTML CSP and publish collision-safe WhatsApp contacts.

Run after ALL page generators (including program experience) and BEFORE search.
Works on GitHub Pages without pretending to set real HTTP response headers.
No runtime JS required for the WhatsApp button, no network requests, no tracking.
"""
from __future__ import annotations
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PHONE = "966503276927"
BASE = "https://wa.me/" + PHONE
START = "<!-- PROTECH_CONTACT_SAFE_BEGIN -->"
END = "<!-- PROTECH_CONTACT_SAFE_END -->"
CSS = '<link rel="stylesheet" href="/assets/contact-safe.css?v=1">'
# HTML CSP supports these directives. Real HTTP-only protections (HSTS,
# frame-ancestors, X-Content-Type-Options and COOP) must be set by a CDN/proxy.
CSP = ("default-src 'self'; script-src 'self'; script-src-attr 'none'; "
       "style-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; "
       "img-src 'self' data:; font-src 'self' data:; "
       "connect-src 'self'; object-src 'none'; "
       "frame-src 'none'; worker-src 'none'; manifest-src 'self'; "
       "base-uri 'self'; form-action 'self'; upgrade-insecure-requests")
CSP_META = '<meta http-equiv="Content-Security-Policy" content="' + escape(CSP, quote=True).replace("&#x27;", "'") + '">'
CSP_RE = re.compile(r'<meta\s+http-equiv="Content-Security-Policy"\s+content="[^"]+"\s*/?>', re.I)
SITEMAP_RE = re.compile(r'<loc>https://alghad\.digital(/[^<]*)</loc>')
SVG = (
    '<svg aria-hidden="true" width="25" height="25" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="1.65" '
    'stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M20.4 11.6a8.4 8.4 0 0 1-12.2 7.5L3.7 20l1-4.3a8.4 8.4 '
    '0 1 1 15.7-4.1Z"/>'
    '<path d="M8.4 7.7c-.4.4-.7 1.1-.6 1.7.3 2 2.4 4.5 4.5 5.5 '
    '1.1.5 2.4.7 3.1-.2l.7-1.1-2.5-1.2-.9 1c-1.4-.7-2.2-1.7-2.7-2.9l1-.8-1.2-2.6-1.4.6Z"/>'
    '</svg>'
)

def catalog() -> dict[str,str]:
    source = (ROOT / "assets/products.js").read_text(encoding="utf-8")
    match = re.search(r"window\.AL_GHAD_PRODUCTS\s*=\s*(\[[\s\S]*?\]);", source)
    if not match:
        raise ValueError("Product data not found")
    records = json.loads(match.group(1))
    return {f"/programs/{p['id']}/": p["title"] for p in records}

def contact(lang: str, product_name: str | None) -> str:
    is_en = lang == "en"
    if is_en:
        message = (f"Hello ProTech, I would like to ask about {product_name}."
                   if product_name else "Hello ProTech, I have a question about Alghad Digital.")
        label = "Chat via WhatsApp"
        title = f"Ask about {product_name} on WhatsApp" if product_name else label
    else:
        message = (f"السلام عليكم، لدي استفسار عن برنامج {product_name} على موقع جيل الغد."
                   if product_name else "السلام عليكم، لدي استفسار عن موقع الغد ديجتال وبرامج ProTech.")
        label = "واتساب"
        title = f"الاستفسار عن {product_name} عبر واتساب" if product_name else "التواصل عبر واتساب"
    href = BASE + "?text=" + quote(message, safe="")
    return (START + '<a class="protech-whatsapp-float"'
            ' href="' + escape(href, quote=True) + '"'
            ' target="_blank" rel="noopener noreferrer"'
            ' aria-label="' + escape(title, quote=True) + '"'
            ' title="' + escape(title, quote=True) + '">'
            + SVG + '<span class="protech-whatsapp-label">' + label + '</span>'
            '</a>' + END)

def accessible_meta(text: str, lang: str) -> str:
    """Postprocess generated pages once; preserve fixes across scheduled rebuilds."""
    # The visible EN/AR token must appear in the accessible name.
    text = text.replace('aria-label="Switch to English">EN</a>',
                        'aria-label="EN — Switch to English">EN</a>')
    text = text.replace('aria-label="Switch to Arabic">AR</a>',
                        'aria-label="AR — Switch to Arabic">AR</a>')
    # Brand and email already have meaningful visible text. Avoid overriding it
    # with a label that omits the on-screen words.
    for classname in ("logo", "contact-email-link"):
        pat = r'(<a\b[^>]*\bclass="' + re.escape(classname) + r'"[^>]*?)\s+aria-label="[^"]*"'
        text = re.sub(pat, r'\1', text, flags=re.I)
    # Add a safe, factual crawl directive to pages that have a robots meta.
    def robots(match: re.Match[str]) -> str:
        val = match.group(1)
        if "max-image-preview:" not in val:
            val += ",max-image-preview:large"
        return '<meta name="robots" content="' + val + '">'
    text = re.sub(r'<meta name="robots" content="([^"]+)">', robots, text, count=1)
    # Social previews should identify the other available translation.
    primary,alternate = ("ar_SA", "en_US") if lang=="ar" else ("en_US","ar_SA")
    locale = '<meta property="og:locale" content="' + primary + '">'
    alt = '<meta property="og:locale:alternate" content="' + alternate + '">'
    # Repair a literal backslash-n left by older generated metadata, if present.
    text = text.replace(locale + r"\n  " + alt, locale + "\n  " + alt)
    if locale in text and alt not in text:
        text = text.replace(locale, locale + "\n  " + alt, 1)
    return text


def patch(route: str, products: dict[str,str]) -> None:
    relative = route.lstrip("/") + "index.html"
    page = ROOT / relative
    if not page.is_file():
        raise FileNotFoundError(page)
    text = page.read_text(encoding="utf-8")
    count = len(CSP_RE.findall(text))
    if count > 1:
        raise ValueError(f"Duplicate CSP meta in {relative}: {count}")
    if count == 1:
        text = CSP_RE.sub(CSP_META, text, count=1)
    else:
        # Some generated catalog pages lacked CSP entirely; add it at the
        # beginning of <head> so it applies before later resource loading.
        head = re.search(r"<head(?:\\s[^>]*)?>", text, flags=re.I)
        if not head:
            raise ValueError(f"Missing HTML head in {relative}")
        text = text[:head.end()] + "\\n" + CSP_META + text[head.end():]
    existing_contacts = list(re.finditer(re.escape(START) + r"[\s\S]*?" + re.escape(END), text))
    if len(existing_contacts) > 1:
        raise ValueError(f"Multiple WhatsApp contact blocks in {relative}")
    if CSS not in text:
        if text.count("</head>") != 1:
            raise ValueError(f"Missing head end: {relative}")
        text = text.replace("</head>", CSS + "\n</head>", 1)
    if text.count(CSS) != 1:
        raise ValueError("Duplicate contact stylesheet in " + relative)
    if text.count("</body>") != 1:
        raise ValueError("Invalid body in " + relative)
    lang = "en" if route.startswith("/en/") else "ar"
    base_route = route[3:] if lang == "en" else route
    marker = contact(lang, products.get(base_route))
    if existing_contacts:
        match = existing_contacts[0]
        text = text[:match.start()] + marker + text[match.end():]
    else:
        text = text.replace("</body>", marker + "\n</body>", 1)
    text = accessible_meta(text, lang)
    assert text.count(START) == text.count(END) == 1
    assert text.count(CSP_META) == 1
    page.write_text(text, encoding="utf-8", newline="\n")

def main() -> None:
    urls = SITEMAP_RE.findall((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    if len(urls) != 42 or len(urls) != len(set(urls)):
        raise ValueError("Sitemap routes differ from expected canonical URLs")
    products = catalog()
    for url in urls:
        patch(url, products)
    print("CONTACT_SECURITY_PAGES_PASS",
          json.dumps({"pages":len(urls),"floating_contact_links":len(urls),
                      "program_context_pages":len(products)*2,
                      "wa_contact":BASE,"csp_meta":len(urls),
                      "response_headers_status":"GitHub Pages not configurable"},
                      ensure_ascii=False), flush=True)

if __name__ == "__main__":
    main()
