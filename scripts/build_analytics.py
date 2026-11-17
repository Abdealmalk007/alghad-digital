#!/usr/bin/env python3
"""Optional consent-gated GA4 setup for static GitHub Pages (Python 3.12+)."""
from __future__ import annotations
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"G-[A-Z0-9]{6,16}\Z")
BLOCK_RE = re.compile(r"\s*<!-- PROTECH_ANALYTICS_BEGIN -->.*?<!-- PROTECH_ANALYTICS_END -->", re.S)
PRIVACY_RE = re.compile(r"\s*<!-- PROTECH_ANALYTICS_PRIVACY_BEGIN -->.*?<!-- PROTECH_ANALYTICS_PRIVACY_END -->", re.S)
CSP_RE = re.compile(r'(<meta\s+http-equiv="Content-Security-Policy"\s+content=")([^"]+)(">)', re.I)

def extend_csp(original: str) -> str:
    replacements = {
        "script-src 'self';": "script-src 'self'; script-src-elem 'self' https://www.googletagmanager.com;",
        "img-src 'self' data:;": "img-src 'self' data: https://www.googletagmanager.com https://*.google-analytics.com;",
        "connect-src 'self';": "connect-src 'self' https://www.googletagmanager.com https://*.google-analytics.com https://*.google.com;",
    }
    for old, new in replacements.items():
        if new in original:
            continue  # Already compatible; allow repeatable builds.
        if original.count(old) != 1:
            raise ValueError(f"Unexpected CSP directive: {old}")
        original = original.replace(old, new, 1)
    return original

def notice(en: bool) -> str:
    if en:
        content = ('<section class="more"><h2>Optional visitor analytics</h2>'
                   '<p>With your permission, Google Analytics 4 measures visits, viewed pages,'
                   ' approximate country, device and browser. It is disabled until you choose to accept.'
                   ' You can change your decision using Analytics preferences in the footer.'
                   ' Google processes measurement data under its own privacy terms.</p></section>')
    else:
        content = ('<section class="more"><h2>إحصائيات الزيارات الاختيارية</h2>'
                   '<p>بعد موافقتك فقط، يستخدم الموقع Google Analytics 4 لقياس الزيارات'
                   ' والصفحات والبلد التقريبي ونوع الجهاز والمتصفح. لا يتم تحميل الخدمة'
                   ' قبل الموافقة، ويمكن تغيير الاختيار من زر تفضيلات الإحصائيات أسفل الصفحة.'
                   ' تخضع معالجة البيانات من Google لسياسة خصوصيتها.</p></section>')
    return "\n<!-- PROTECH_ANALYTICS_PRIVACY_BEGIN -->" + content + "<!-- PROTECH_ANALYTICS_PRIVACY_END -->\n"

def main() -> None:
    measurement_id = os.environ.get("GA4_MEASUREMENT_ID", "").strip().upper()
    if measurement_id and not ID_RE.fullmatch(measurement_id):
        raise SystemExit("Invalid GA4_MEASUREMENT_ID (expected G- plus 6-16 ASCII letters/digits)")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    routes = re.findall(r"<loc>https://alghad\.digital(/[^<]*)</loc>", sitemap)
    if len(routes) != 42 or len(set(routes)) != 42:
        raise RuntimeError("Unexpected sitemap routes")
    for route in routes:
        target = ROOT / route.lstrip("/") / "index.html"
        source = target.read_text(encoding="utf-8")
        html = BLOCK_RE.sub("", source)
        html = PRIVACY_RE.sub("", html)
        css = '<link rel="stylesheet" href="/assets/analytics-consent.css?v=1">'
        matches = list(CSP_RE.finditer(html))
        if len(matches) != 1:
            raise ValueError(f"Missing/duplicate CSP: {target}")
        match = matches[0]
        # Prepare CSP independently of GA4 stream creation, without loading Google scripts.
        html = html[:match.start(2)] + extend_csp(match.group(2)) + html[match.end(2):]
        if measurement_id:
            if css not in html:
                if html.count("</head>") != 1: raise ValueError(f"Invalid head: {target}")
                html = html.replace("</head>", css + "\n</head>", 1)
            snippet = ('\n<!-- PROTECH_ANALYTICS_BEGIN -->'
                       '<script id="protech-analytics" defer src="/assets/analytics-consent.js?v=1"'
                       ' data-ga4-id="' + measurement_id + '"></script>'
                       '<!-- PROTECH_ANALYTICS_END -->\n')
            if html.count("</body>") != 1: raise ValueError(f"Invalid body: {target}")
            html = html.replace("</body>", snippet + "</body>", 1)
            if route in ("/privacy/", "/en/privacy/"):
                if html.count("</main>") != 1: raise ValueError(f"Invalid privacy page: {target}")
                html = html.replace("</main>", notice(route.startswith("/en/")) + "</main>", 1)
        else:
            html = html.replace(css, "")
        if html != source:
            target.write_text(html, encoding="utf-8", newline="\n")
    print(f"ANALYTICS_CONFIGURED={bool(measurement_id)} PAGES={len(routes)} CONSENT_REQUIRED=True")

if __name__ == "__main__":
    main()
