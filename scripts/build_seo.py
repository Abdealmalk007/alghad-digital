#!/usr/bin/env python3
"""Build crawlable Arabic pages and a complete sitemap for alghad.digital.
Python 3.11+ and Node.js 22+. No external dependencies or tokens.
This script is safe to run repeatedly from GitHub Actions.
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path
from html import unescape
from urllib.parse import quote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://alghad.digital"
PAGES_DIR = ROOT / "programs"
SOCIAL_IMAGE = DOMAIN + "/assets/social/alghad-digital.png"


def breadcrumbs_schema(canonical: str, title: str) -> dict:
    segments = canonical.removeprefix(DOMAIN).strip("/").split("/")
    items = [{"@type": "ListItem", "position": 1, "name": "الغد ديجتال", "item": DOMAIN + "/"}]
    if segments and segments[0] == "programs" and len(segments) == 2:
        items.append({"@type": "ListItem", "position": 2, "name": "برامج ProTech",
                      "item": DOMAIN + "/programs/"})
    items.append({"@type": "ListItem", "position": len(items) + 1,
                  "name": title.split("|")[0].strip(), "item": canonical})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": items}



def esc(v: object) -> str:
    return html.escape(str(v or ""), quote=True)


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_javascript_data(path: str, export_name: str):
    code = (
        "const fs=require('fs'); const vm=require('vm');"
        "const scope={window:{}};"
        "vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),scope,{timeout:1500});"
        "process.stdout.write(JSON.stringify(scope.window[process.argv[2]]));"
    )
    result = subprocess.run(
        ["node", "-e", code, str(ROOT / path), export_name],
        capture_output=True, text=True, encoding="utf-8", errors="strict", timeout=12, check=True,
    )
    return json.loads(result.stdout)


def safe_repo(url: str) -> bool:
    return bool(re.fullmatch(r"https://github\.com/Abdealmalk007/[A-Za-z0-9_.-]+", url or ""))


def safe_release(url: str, repository: str) -> bool:
    prefix = "https://github.com/Abdealmalk007/" + repository + "/releases/"
    return bool(url and url.startswith(prefix) and re.fullmatch(
        r"https://github\.com/Abdealmalk007/[A-Za-z0-9_.-]+/releases/(tag|download)/[^\s?#]+",
        url,
    ))


def schema_script(data: dict | list) -> str:
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    encoded = encoded.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return '<script type="application/ld+json">' + encoded + "</script>"


def page(*, title: str, description: str, canonical: str, content: str,
         schema: dict | list, asset_prefix: str = "../") -> str:
    description = description.strip()[:205]
    home = asset_prefix
    return f"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <meta name="description" content="{esc(description)}">
  <meta name="theme-color" content="#071522">
  <title>{esc(title)}</title>
  <link rel="canonical" href="{esc(canonical)}">
  <link rel="icon" href="/favicon.ico?v=4" sizes="any">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg?v=4">
  <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16.png?v=4">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png?v=4">
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png?v=4">
  <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=4">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="{home}assets/seo-pages.css">
  <meta property="og:type" content="website">
  <meta property="og:locale" content="ar_SA">
  <meta property="og:site_name" content="الغد ديجتال | Alghad Digital">
  <meta property="og:url" content="{esc(canonical)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{SOCIAL_IMAGE}">
  <meta property="og:image:secure_url" content="{SOCIAL_IMAGE}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Alghad Digital — ProTech Software">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{SOCIAL_IMAGE}">
  {schema_script(schema)}
  {schema_script(breadcrumbs_schema(canonical, title))}
</head>
<body>
  <a href="#main" class="skip">تجاوز إلى المحتوى</a>
  <header class="site-header">
    <nav class="shell header-inner" aria-label="التنقل الرئيسي">
      <a class="brand" href="{home}"><span class="brand-logo"><img src="{home}icon-192.png?v=4" alt="" width="38" height="38"></span><span>الغد <strong>ديجتال</strong><small>ALGHAD DIGITAL</small></span></a>
      <div class="nav-links"><a href="{home}programs/">برامج ProTech</a><a href="{home}news/">أخبار التقنية</a><a href="{home}free-windows-tools/">برامج Windows</a><a href="{home}#contact">تواصل معنا</a></div>
    </nav>
  </header>
  <main id="main" class="shell content">{content}</main>
  <footer class="site-footer">
    <div class="shell"><strong>الغد ديجتال — Alghad Digital</strong>
      <span>برامج وحلول تقنية وأخبار من مصادرها الأصلية.</span>
      <a href="mailto:protech.2025.2026@gmail.com">protech.2025.2026@gmail.com</a>
    </div>
  </footer>
</body>
</html>
"""


def render_product(product: dict, downloads: dict) -> None:
    slug = product["id"]
    assert re.fullmatch("[a-z0-9-]+", slug)
    title = str(product["title"])
    status = product["status"] == "public"
    canonical = DOMAIN + "/programs/" + slug + "/"
    platform = "، ".join(product.get("platforms", []))
    desc = product.get("description", "")
    details = product.get("details", "")
    features = product.get("features", [])
    image = product.get("preview", "")
    assert re.fullmatch(r"assets/previews/[a-z0-9-]+\.svg", image), image
    assert (ROOT / image).is_file(), image
    feature_html = "".join("<li>" + esc(feature) + "</li>" for feature in features[:5])
    repo = product.get("github", "")
    links = ""
    item = downloads.get(slug, {})
    release_url = item.get("release")
    if status and safe_repo(repo):
        links += f'<a class="button outline" href="{esc(repo)}" rel="noopener noreferrer" target="_blank">المستودع الرسمي على GitHub ↗</a>'
    if status and safe_release(release_url, item.get("repository", "")):
        links += f'<a class="button" href="{esc(release_url)}" rel="noopener noreferrer" target="_blank">الإصدار الرسمي وروابط التنزيل ↗</a>'
    elif status:
        links += '<span class="muted">المستودع منشور، لكن لا تتوفر نسخة تحميل عامة مؤكدة لهذا البرنامج حاليًا.</span>'
    else:
        links += '<span class="muted">هذا البرنامج قيد التطوير — قريبًا جدًا. لا توجد نسخة عامة متاحة للتنزيل.</span>'

    preferred=next((file for file in item.get("files",[]) if file.get("recommended")
                    and safe_release(file.get("url"),item.get("repository",""))),None)
    verified={}
    if preferred and (ROOT/"assets"/"release-facts.json").is_file():
        store=json.loads((ROOT/"assets"/"release-facts.json").read_text(encoding="utf-8"))
        release_fact=store.get("releases",{}).get(slug,{})
        if release_fact.get("version")==item.get("version") and release_fact.get("repository")==item.get("repository"):
            verified=next((x for x in release_fact.get("assets",[])
                           if x["url"]==preferred["url"] and x["bytes"]==preferred["bytes"]),{})
            if verified:
                verified={**verified,"published_at":release_fact["published_at"]}
    if preferred and verified.get("sha256") and re.fullmatch(r"[0-9a-f]{64}",verified["sha256"]):
        release_details=(
          '<section class="more release-facts">'
          '<h2>تحميل النسخة التجريبية والتحقق منها</h2>'
          '<p>حالة الإصدار: <strong>Beta / Preview</strong>. '
          'تاريخ النشر: '+esc(verified["published_at"][:10])+
          '. حجم ملف التحميل: '+str(round(preferred["bytes"]/1048576,1))+' MB.</p>'
          '<p><a class="button" target="_blank" rel="noopener noreferrer" href="'+esc(preferred["url"])+'">تحميل مباشر من GitHub Releases</a></p>'
          '<p>بصمة SHA-256 الصادرة من بيانات GitHub Releases:</p>'
          '<pre><code dir="ltr">'+esc(verified["sha256"])+'</code></pre>'
          + ('<p><a href="'+esc(item["checksum"])+'" rel="noopener noreferrer" target="_blank">ملف SHA256SUMS الرسمي</a></p>'
             if safe_release(item.get("checksum"),item.get("repository","")) else '')
          + '</section>'
        )
    elif preferred:
        release_details='<section class="more"><h2>معلومات الإصدار</h2><p>النسخة Beta متاحة عبر GitHub، ولم نتحقق من بصمة SHA-256 رقمية لعرضها حاليًا.</p></section>'
    else:
        release_details='<section class="more"><h2>حالة الإتاحة</h2><p>لا يتوفر ملف تثبيت عام مؤكَّد لهذا البرنامج حاليًا؛ تابع حالة المشروع في مستودعه عند نشره.</p></section>'

    info = ("Beta / Preview" if preferred else "مستودع منشور بلا تنزيل" if status else "قريبًا")
    keywords = ", ".join([title, "الغد ديجتال", "ProTech", platform, str(product.get("category", ""))])
    meta = f'{title} من برامج ProTech على الغد ديجتال. {desc} المنصات: {platform}. الحالة: {info}.'
    content = f"""
      <div class="breadcrumbs"><a href="../../">الغد ديجتال</a> / <a href="../">برامج ProTech</a> / {esc(title)}</div>
      <div class="product-layout">
        <section>
          <span class="eyebrow">PROTECH SOFTWARE / {esc(product.get("category", "برامج"))}</span>
          <h1>{esc(title)}</h1>
          <p class="hero-desc">{esc(desc)}</p>
          <div class="chips"><span>{esc(info)}</span><span>{esc(platform)}</span><span>الإصدار: {esc(product.get("version", "غير محدد"))}</span></div>
          <p class="long-description">{esc(details)}</p>
          <h2>مميزات {esc(title)}</h2>
          <ul class="features">{feature_html}</ul>
          <div class="actions">{links}</div>
          {release_details}
          <section class="more">
            <h2>متطلبات التشغيل</h2>
            <p>المنصات المعلنة: {esc(platform)}. تحقق من صفحة الإصدار الرسمية لمعرفة توافق الإصدار مع جهازك؛ لم يتم تأكيد الحد الأدنى لإصدارات النظام هنا.</p>
          </section>
          <section class="more">
            <h2>الأسئلة الشائعة</h2>
            <details><summary>هل النسخة جاهزة للاستخدام النهائي؟</summary>
              <p>{"الإصدار الحالي تجريبي (Beta/Preview)، وليس إصدارًا مستقرًا معتمدًا." if preferred else "لا يتوفر تنزيل عام موثَّق حاليًا."}</p></details>
            <details><summary>من أين أحمل البرنامج؟</summary>
              <p>{"اتبع رابط GitHub Releases المعروض أعلاه وتحقق من اسم الملف قبل تشغيله." if preferred else "انتظر نشر رابط الإصدار العام عبر صفحة المشروع الرسمية."}</p></details>
            <details><summary>كيف أتحقق من سلامة الملف؟</summary>
              <p>قارن قيمة SHA-256 عندما تتوفر، واطّلع على <a href="../../security/">إرشادات الأمان والتوقيع الرقمي</a>.</p></details>
          </section>
        </section>
        <aside><img class="cover" width="960" height="540" src="../../{esc(image)}" alt="رسم توضيحي لبرنامج {esc(title)}"><p>الصورة توضيحية وليست لقطة فعلية من التطبيق.</p></aside>
      </div>
      <section class="more"><h2>استكشف برامجنا الأخرى</h2><p>تصفح <a href="../">جميع برامج ProTech</a>، أو تابع <a href="../../news/">أخبار التقنية</a> و<a href="../../free-windows-tools/">برامج Windows المجانية</a>.</p></section>
    """
    app_schema = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": title,
        "description": desc,
        "url": canonical,
        "image": DOMAIN + "/" + image,
        "publisher": {"@type": "Organization", "name": "ProTech", "url": DOMAIN},
        "operatingSystem": platform,
        "applicationCategory": "BusinessApplication" if slug in {"stone", "marble", "reports", "hr", "porcelain", "quotes"} else "UtilitiesApplication",
    }
    if product.get("version") and product["version"] != "—":
        app_schema["softwareVersion"] = product["version"]
    if status and safe_release(release_url, item.get("repository", "")):
        app_schema["downloadUrl"] = release_url
    target = PAGES_DIR / slug / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page(title=f"{title} | الغد ديجتال — Alghad Digital",
        description=meta, canonical=canonical, content=content,
        schema=app_schema, asset_prefix="../../"), encoding="utf-8", newline="\n")


def render_catalog(products: list) -> None:
    items = []
    for product in products:
        slug = product["id"]
        name = product["title"]
        category = product.get("category", "")
        state = "منشور" if product["status"] == "public" else "قريبًا جدًا"
        items.append(f'<article class="directory-card"><h2><a href="{esc(slug)}/">{esc(name)}</a></h2><p>{esc(product.get("description", ""))}</p><span>{esc(category)} · {esc(state)}</span></article>')
    text = f"""<div class="breadcrumbs"><a href="../">الغد ديجتال</a> / برامج ProTech</div>
      <span class="eyebrow">ALGHAD DIGITAL / PROTECH SOFTWARE</span>
      <h1>برامج ProTech على الغد ديجتال</h1>
      <p class="hero-desc">تصفح أسماء البرامج ووصفها ومميزاتها وروابط التنزيل الرسمية عند توفرها. تظهر البرامج قيد التطوير بحالة «قريبًا جدًا» دون تحميل غير موثق.</p>
      <div class="directory-grid">{''.join(items)}</div>"""
    schema = {"@context": "https://schema.org", "@type": "CollectionPage",
        "name": "برامج ProTech | الغد ديجتال",
        "url": DOMAIN + "/programs/",
        "mainEntity": {"@type": "ItemList", "itemListElement": [
            {"@type":"ListItem","position":i+1,"url":DOMAIN+"/programs/"+p["id"]+"/","name":p["title"]} for i,p in enumerate(products)
        ]}}
    target = PAGES_DIR / "index.html"
    target.write_text(page(title="برامج ProTech | الغد ديجتال — تحميل برامج Windows وAndroid",
        description="تصفح برامج ProTech على موقع الغد ديجتال: Download Anything PRO وProTech HR وKitchen CAD Pro وبرامج Windows وAndroid الأخرى.",
        canonical=DOMAIN+"/programs/", content=text, schema=schema), encoding="utf-8", newline="\n")


def translated_article_html(item: dict, url: str) -> str:
    """Use a translated headline when verified; retain original for transparency."""
    original = str(item.get("title", ""))
    translated = (
        item.get("translation_status") == "machine"
        and isinstance(item.get("title_ar"), str)
        and len(item["title_ar"]) >= 4
    )
    title = item["title_ar"] if translated else original
    language = "ar" if translated else ("en" if item.get("language") == "en" else "ar")
    result = ('<h2><a lang="' + language + '" dir="auto" '
              'rel="noopener noreferrer" target="_blank" href="' + esc(url) + '">'
              + esc(title) + ' ↗</a></h2>')
    if translated:
        result += ('<p class="original-news-title" lang="en" dir="ltr">'
                   + esc(original) + '</p><p class="translation-disclaimer">'
                   + "ترجمة آلية من الغد ديجتال، والعنوان الأصلي أعلاه للمراجعة."
                   + '</p>')
    elif item.get("translation_status") == "unavailable":
        result += ('<p class="translation-disclaimer">'
                   + "الترجمة العربية غير متاحة، ويظهر العنوان الأصلي."
                   + '</p>')
    return result


def render_news(news: dict) -> None:
    items = []
    for item in news.get("articles", [])[:25]:
        title = item.get("title", "")
        url = item.get("url", "")
        if not re.fullmatch(r"https://[^\s<>\"']+", url or ""):
            continue
        items.append(
            '<article class="directory-card news-article"><span>'
            + esc(item.get("source_name", "")) + " · "
            + esc(item.get("published_at", "")[:10]) + " · "
            + esc(item.get("category", "")) + "</span>"
            + translated_article_html(item, url) + "</article>"
        )
    text = f"""<div class="breadcrumbs"><a href="../">الغد ديجتال</a> / الأخبار التقنية</div>
      <span class="eyebrow">TECH NEWS / ARABIC SOURCES</span>
      <h1>آخر الأخبار التقنية والتكنولوجيا</h1>
      <p class="hero-desc">عناوين أخبار التقنية من مواقع عربية موثوقة، تتجدد عند نجاح عملية التحديث اليومي. نعرض العنوان والمصدر والتاريخ فقط؛ الخبر الكامل محفوظ لناشره الأصلي.</p>
      <p class="updated">آخر تحديث بيانات: {esc(news.get("generated_at", "")[:16].replace("T"," "))} UTC</p>
      <div class="directory-grid news-grid">{''.join(items) if items else '<p>الأخبار غير متاحة حاليًا، يرجى مراجعة المصادر مباشرة.</p>'}</div>"""
    schema = {"@context":"https://schema.org","@type":"CollectionPage",
        "name":"آخر الأخبار التقنية العربية | الغد ديجتال","url":DOMAIN+"/news/"}
    out = ROOT/"news"/"index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(title="آخر الأخبار التقنية العربية اليوم | الغد ديجتال — Alghad Digital",
        description="آخر أخبار الذكاء الاصطناعي والأمن السيبراني والهواتف والتكنولوجيا العربية، مع روابط المصادر الأصلية والتحديث اليومي على موقع الغد ديجتال.",
        canonical=DOMAIN+"/news/",content=text,schema=schema), encoding="utf-8", newline="\n")


def render_industry(data: dict, topic: str) -> None:
    mapping={
      "ai":("ai-news","أخبار الذكاء الاصطناعي الرسمية","ChatGPT وOpenAI وClaude وDeepSeek وGemini",
            "أخبار الذكاء الاصطناعي من OpenAI وGoogle وغيرها، مع روابط المصدر الرسمي وتاريخ نشر الخبر."),
      "companies":("tech-companies","أخبار الشركات التقنية الكبرى","NVIDIA وAMD وApple وSamsung وHuawei",
            "أحدث أخبار شركات NVIDIA وAMD وApple وSamsung وGoogle وMicrosoft، وأخبار الشركات من مصادرها الرسمية."),
      "cars":("cars","أخبار السيارات والتقنيات الحديثة","Toyota وHonda وPorsche وSubaru",
            "عناوين أخبار السيارات الجديدة والكهربائية والقيادة الذكية من المواقع الرسمية لشركات السيارات.")
    }
    slug,title,brands,description=mapping[topic]
    canonical=DOMAIN+"/"+slug+"/"
    content_data=data["topics"][topic]
    news=[]
    for item in content_data["articles"][:18]:
        link=item["url"]
        assert link.startswith("https://") and item["official"] is True
        news.append(
            '<article class="directory-card news-article"><span>'
            + esc(item["source_name"]) + " · "
            + esc(item["published_at"][:10]) + " · "
            + "مصدر رسمي</span>"
            + translated_article_html(item, link) + "</article>"
        )
    sites=[]
    for source in data["sources"]:
        if topic not in source["topics"]:continue
        text=source["name"]+("" if source["feed_available"] else " (رابط متابعة فقط)")
        sites.append('<a href="'+esc(source["url"])+'" target="_blank" rel="noopener noreferrer">'+esc(text)+" ↗</a>")
    body=f"""<div class="breadcrumbs"><a href="../">الغد ديجتال</a> / {esc(title)}</div>
      <span class="eyebrow">OFFICIAL NEWSROOM HEADLINES / ALGHAD DIGITAL</span>
      <h1>{esc(title)}</h1>
      <p class="hero-desc">{esc(description)} نحتفظ بالعناوين بلغتها الأصلية؛ قراءة التفاصيل تتم عبر موقع الناشر.</p>
      <p class="updated">آخر فحص للخلاصات: {esc(data["generated_at"][:16].replace("T"," "))} UTC</p>
      <div class="directory-grid news-grid">{''.join(news) if news else '<p>لا تتوفر أخبار حديثة مؤكدة لهذا القسم حاليًا.</p>'}</div>
      <section class="more"><h2>غرف الأخبار والمصادر الرسمية</h2>
      <p>المصادر التي لا تتوفر منها تغذية RSS معتمدة تظهر كرابط متابعة، دون اختلاق أخبار أو نسبها إلى الشركة.</p>
      <nav class="industry-static-source-list" aria-label="روابط المصادر الرسمية">{' '.join(sites)}</nav></section>
      <section class="more"><h2>أقسام إخبارية أخرى</h2>
      <p><a href="../ai-news/">أخبار الذكاء الاصطناعي</a> · <a href="../tech-companies/">أخبار الشركات التقنية</a> ·
      <a href="../cars/">أخبار السيارات</a> · <a href="../news/">الأخبار التقنية العربية</a></p></section>
    """
    schema={"@context":"https://schema.org","@type":"CollectionPage",
        "name":title,"description":description,
        "url":canonical,"inLanguage":"ar"}
    out=ROOT/slug/"index.html"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(page(title=title+" | الغد ديجتال — Alghad Digital",
        description=description+" "+brands,
        canonical=canonical,content=body,schema=schema),
        encoding="utf-8",newline="\n")


def render_tools(tools: dict) -> None:
    items = []
    for tool in tools.get("items", [])[:20]:
        url=tool.get("url","")
        if not url.startswith("https://"):continue
        items.append(f"""<article class="directory-card tool-card">
            <img width="960" height="540" loading="lazy" src="../{esc(tool.get('image',''))}" alt="صورة توضيحية لأداة {esc(tool.get('name',''))}">
            <h2>{esc(tool.get('name',''))}</h2><p>{esc(tool.get('description',''))}</p>
            <span>{esc(tool.get('license',''))} · {esc(tool.get('category',''))}</span>
            <p><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">الموقع الرسمي وتحميل البرنامج ↗</a></p></article>""")
    text = f"""<div class="breadcrumbs"><a href="../">الغد ديجتال</a> / برامج Windows</div>
      <span class="eyebrow">FREE WINDOWS TOOLS</span>
      <h1>أفضل برامج Windows المجانية والمفيدة</h1>
      <p class="hero-desc">أدوات Windows موصى بتجربتها من مواقعها الرسمية، منها Rufus وVentoy وEverything وVLC وMicrosoft PowerToys. تراخيص البرامج تختلف، وبعضها مجاني للاستخدام غير التجاري فقط.</p>
      <div class="directory-grid">{''.join(items)}</div>"""
    schema={"@context":"https://schema.org","@type":"CollectionPage",
        "name":"أفضل برامج ويندوز المجانية | الغد ديجتال","url":DOMAIN+"/free-windows-tools/"}
    out=ROOT/"free-windows-tools"/"index.html"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(page(title="أفضل برامج Windows المجانية | الغد ديجتال — تحميل رسمي",
        description="أدوات Windows مجانية ومفيدة: Everything، Rufus، Ventoy، IrfanView، VLC، File Converter، FDM، Microsoft PowerToys مع شرح وروابط رسمية.",
        canonical=DOMAIN+"/free-windows-tools/",content=text,schema=schema),encoding="utf-8",newline="\n")


def update_home(products: list) -> None:
    path=ROOT/"index.html"
    html_text=path.read_text(encoding="utf-8")
    def replace(pattern: str,replacement: str) -> None:
        nonlocal html_text
        html_text,count=re.subn(pattern, lambda _:replacement, html_text, count=1, flags=re.S)
        if count != 1:raise RuntimeError("Could not find unique homepage SEO target: "+pattern[:70])

    replace(r'<title>.*?</title>',
        '<title>برامج ProTech للأعمال والتصميم | الغد ديجتال - Alghad Digital</title>')
    replace(r'<meta name="description" content="[^"]*">',
        '<meta name="description" content="الغد ديجتال: برامج ProTech لإدارة الرخام والمطابخ والموارد البشرية والتقارير، مع روابط الإصدارات الرسمية وتنزيلات تجريبية موثقة. أخبار التقنية قسم إضافي.">')
    replace(r'<meta property="og:title" content="[^"]*">',
        '<meta property="og:title" content="الغد ديجتال | Alghad Digital — البرامج والأخبار التقنية">')
    replace(r'<meta property="og:description" content="[^"]*">',
        '<meta property="og:description" content="برامج ProTech مع صفحات مستقلة للتحميل، أخبار التقنية اليومية، ومكتبة برامج Windows المجانية.">')
    social_meta = f"""<!-- SOCIAL PREVIEW START -->
  <meta property="og:image" content="{SOCIAL_IMAGE}">
  <meta property="og:image:secure_url" content="{SOCIAL_IMAGE}">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Alghad Digital — ProTech Software">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="الغد ديجتال | Alghad Digital">
  <meta name="twitter:description" content="برامج ProTech وأخبار التقنية ومكتبة برامج Windows.">
  <meta name="twitter:image" content="{SOCIAL_IMAGE}">
<!-- SOCIAL PREVIEW END -->"""
    if "<!-- SOCIAL PREVIEW START -->" in html_text:
        replace(r"<!-- SOCIAL PREVIEW START -->.*?<!-- SOCIAL PREVIEW END -->", social_meta)
    else:
        replace(r"</head>", social_meta + "\n</head>")

    cards = ''.join(f'<a href="programs/{esc(p["id"])}/">{esc(p["title"])}</a>' for p in products)
    directory = f"""<!-- SEO DIRECTORY START -->
    <section class="seo-home-directory" aria-labelledby="seo-directory-title">
      <div class="shell">
        <span class="section-kicker">PROTECH / SOFTWARE INDEX</span>
        <h2 id="seo-directory-title">دليل برامج الغد ديجتال</h2>
        <p>صفحات مستقلة لكل برنامج تساعدك على العثور على المميزات وحالة التطوير وروابط التنزيل المعتمدة.</p>
        <nav class="seo-directory-links" aria-label="صفحات برامج ProTech">
          {cards}
        </nav>
        <div class="seo-directory-extras"><a href="programs/">جميع البرامج</a><a href="news/">أخبار التقنية</a><a href="ai-news/">أخبار الذكاء الاصطناعي</a><a href="tech-companies/">أخبار الشركات</a><a href="cars/">أخبار السيارات</a><a href="free-windows-tools/">برامج Windows المجانية</a></div>
      </div>
    </section>
<!-- SEO DIRECTORY END -->"""
    if "<!-- SEO DIRECTORY START -->" in html_text:
        replace(r"<!-- SEO DIRECTORY START -->.*?<!-- SEO DIRECTORY END -->", directory)
    else:
        replace(r"</main>",directory+"\n</main>")
    organization={
        "@context":"https://schema.org",
        "@graph":[
          {"@type":"Organization","name":"الغد ديجتال — Alghad Digital",
           "alternateName":["الغد الرقمي","Alghad Digital","ProTech"],
           "url":DOMAIN+"/","email":"protech.2025.2026@gmail.com",
           "sameAs":["https://github.com/Abdealmalk007"]},
          {"@type":"WebSite","name":"الغد ديجتال | Alghad Digital",
           "inLanguage":"ar","url":DOMAIN+"/",
           "description":"برامج تقنية وأخبار تكنولوجيا عربية وأدوات Windows"}
        ]}
    script = "<!-- SEO JSONLD START -->"+schema_script(organization)+"<!-- SEO JSONLD END -->"
    if "<!-- SEO JSONLD START -->" in html_text:
        replace(r"<!-- SEO JSONLD START -->.*?<!-- SEO JSONLD END -->",script)
    else:
        replace(r"</head>", script+"\n</head>")
    # Schema must always match real, visible FAQ questions and answers.
    faq_match = re.search(
        r'<section class="faq-section[^"]*"\s+id="faq".*?</section>',
        html_text, flags=re.S,
    )
    if faq_match is None:
        raise RuntimeError("Homepage visible FAQ is missing")
    qa_list = re.findall(
        r'<details>\s*<summary>(.*?)</summary>\s*<p>(.*?)</p>\s*</details>',
        faq_match.group(0), flags=re.S,
    )
    if not 3 <= len(qa_list) <= 12:
        raise RuntimeError("Unexpected FAQ entry count")
    faq_entities = []
    for question_html, answer_html in qa_list:
        question = unescape(re.sub(r'<[^>]*>', ' ', question_html)).replace('+', ' ')
        answer = unescape(re.sub(r'<[^>]*>', ' ', answer_html))
        question = re.sub(r'\s+', ' ', question).strip()
        answer = re.sub(r'\s+', ' ', answer).strip()
        if len(question) < 15 or len(answer) < 30:
            raise RuntimeError("FAQ entry is too short for accurate structured data")
        faq_entities.append({
            "@type": "Question",
            "name": question,
            "acceptedAnswer": {"@type": "Answer", "text": answer},
        })
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_entities,
    }
    faq_script = (
        "<!-- FAQ JSONLD START -->"
        + schema_script(faq_schema)
        + "<!-- FAQ JSONLD END -->"
    )
    if "<!-- FAQ JSONLD START -->" in html_text:
        replace(r"<!-- FAQ JSONLD START -->.*?<!-- FAQ JSONLD END -->", faq_script)
    else:
        replace(r"</head>", faq_script + "\n</head>")
    path.write_text(html_text,encoding="utf-8",newline="\n")


def update_sitemap(products: list) -> None:
    urls=["/","/programs/","/news/","/free-windows-tools/","/ai-news/","/tech-companies/","/cars/","/about/","/security/","/privacy/"]+[
        "/programs/"+p["id"]+"/" for p in products]
    ns="http://www.sitemaps.org/schemas/sitemap/0.9"
    ET.register_namespace("",ns)
    top=ET.Element(f"{{{ns}}}urlset")
    for url in urls:
        element=ET.SubElement(top,f"{{{ns}}}url")
        ET.SubElement(element,f"{{{ns}}}loc").text=DOMAIN+url
    tree=ET.ElementTree(top)
    ET.indent(tree,space="  ")
    tree.write(ROOT/"sitemap.xml",encoding="utf-8",xml_declaration=True)
    (ROOT/"robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: "+DOMAIN+"/sitemap.xml\n",encoding="utf-8")
    print("SITEMAP_URLS="+str(len(urls)))


def main() -> None:
    products = read_javascript_data("assets/products.js","AL_GHAD_PRODUCTS")
    downloads=read_javascript_data("assets/downloads.js","AL_GHAD_DOWNLOADS")
    news=read_json("assets/news.json")
    tools=read_json("assets/tools.json")
    industry=read_json("assets/industry-news.json")
    assert len(products)==10 and len(set(x["id"] for x in products))==10
    assert not {"recorder","omar","reem"} & {x["id"] for x in products}
    for product in products:render_product(product,downloads)
    render_catalog(products)
    render_news(news)
    for topic in ("ai","companies","cars"):
        render_industry(industry,topic)
    render_tools(tools)
    update_home(products)
    update_sitemap(products)
    print("SEO_PAGES="+str(9+len(products))+" PROGRAMS="+str(len(products)))


if __name__=="__main__":
    main()
