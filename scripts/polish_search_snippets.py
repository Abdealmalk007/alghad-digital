#!/usr/bin/env python3
"""Curated bilingual metadata improvements after the canonical page generator."""
from __future__ import annotations
from html import escape, unescape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
titles = {
    "/": "الغد ديجتال (جيل الغد) | برامج Pro Tech لويندوز وأندرويد",
    "/en/": "Alghad Digital | ProTech Software for Windows & Android",
    "/ai-news/": "أخبار الذكاء الاصطناعي | جيل الغد",
    "/cars/": "أخبار السيارات والتقنيات الحديثة | جيل الغد",
    "/news/": "الأخبار التقنية العربية | جيل الغد",
    "/tech-companies/": "أخبار شركات التقنية العالمية | جيل الغد",
    "/protech/": "ProTech (بروتك) | مطور برامج وتطبيقات",
    "/en/free-windows-tools/": "Free Windows Utilities | Alghad Digital",
    "/en/programs/": "ProTech Software for Windows & Android",
    "/en/programs/care/": "ProTech Windows Care | Windows Maintenance",
    "/en/programs/download/": "Download Anything PRO | Android Downloads",
    "/en/programs/kitchen/": "Kitchen CAD Pro | Kitchen Design Software",
    "/en/programs/marble/": "Marble Delivery Pro | Delivery Management",
    "/en/programs/quotes/": "ProTech Quotes & Contracts | Business Software",
    "/en/programs/stone/": "ProTech Stone Manager | Stone Operations",
    "/programs/care/": "ProTech Windows Care | برنامج صيانة وتحسين نظام Windows",
    "/programs/download/": "Download Anything PRO | تطبيق تحميل الفيديو والصوت للأندرويد",
    "/programs/hr/": "ProTech HR | برنامج إدارة الموارد البشرية والموظفين",
    "/programs/kitchen/": "Kitchen CAD Pro | برنامج تصميم المطابخ ثنائي وثلاثي الأبعاد",
    "/programs/marble/": "Marble Delivery Pro | برنامج إدارة وتسليم أعمال الرخام",
    "/programs/quotes/": "ProTech Quotes & Contracts | برنامج عروض الأسعار والعقود",
    "/programs/reports/": "Daily Work Reports | برنامج تقارير العمل اليومية",
    "/programs/smart-excel/": "SmartExcelAnalyzer | برنامج تحليل بيانات Excel والإحصاءات",
    "/programs/stone/": "ProTech Stone Manager | برنامج إدارة الرخام والبورسلان",
}

descriptions = {
    "/": "الغد ديجتال (جيل الغد) يعرض برامج ProTech لويندوز وأندرويد: تحليل Excel وإدارة الموظفين والرخام والعقود، مع حالة الإصدار وروابطه الرسمية.",
    "/en/": "Explore ProTech software for Excel analysis, HR, contracts, stone management and reporting, with transparent release status and official downloads.",
    "/en/programs/": "Explore ProTech Windows and Android software for HR, quotations, contracts, stone management and reporting, with verified release information.",
    "/en/programs/care/": "ProTech Windows Care provides Windows maintenance and optimization utilities. Explore features, release status and available Portable or Setup downloads.",
    "/en/programs/download/": "Download Anything PRO is an Android media downloader project. Explore its supported features, current release status and official download options.",
    "/en/programs/quotes/": "ProTech Quotes & Contracts helps manage quotations, customer details, contracts and document templates. Review available beta features and releases.",
    "/en/programs/smart-excel/": "SmartExcelAnalyzer helps analyze Excel spreadsheets and visualize data in desktop reports. Explore features and the latest available release.",
    "/en/programs/stone/": "ProTech Stone Manager helps organize stone and porcelain jobs, customer records, inventory and reports. Review current release availability.",
    "/en/programs/marble/": "Marble Delivery Pro organizes marble deliveries, customer details and project documentation. Discover its features and release information.",
    "/en/programs/reports/": "Daily Work Reports helps organize daily tasks, project updates and printable reports. Explore its functionality and release status.",
    "/programs/care/": "ProTech Windows Care برنامج صيانة وتحسين نظام Windows، مع أدوات عملية وواجهة عربية. راجع الميزات وروابط إصدارات Portable وSetup.",
    "/programs/download/": "Download Anything PRO تطبيق تحميل الفيديو والصوت للأندرويد. تعرّف على أدوات التنزيل والتنظيم وحالة الإصدار والروابط الرسمية.",
    "/programs/hr/": "ProTech HR برنامج إدارة الموارد البشرية والموظفين والحضور والإجازات والرواتب والتقارير لويندوز. استعرض خصائصه وحالة الإصدار.",
    "/programs/kitchen/": "Kitchen CAD Pro برنامج تصميم المطابخ ثنائي وثلاثي الأبعاد، لتخطيط الخزائن والخامات ومخرجات التصنيع. المشروع قيد التطوير.",
    "/programs/marble/": "Marble Delivery Pro برنامج إدارة وتسليم أعمال الرخام والطلبات والعملاء والمستندات والتقارير. راجع الميزات وحالة الإصدار.",
    "/programs/quotes/": "ProTech Quotes & Contracts برنامج عروض الأسعار والعقود وقوالب المستندات وإدارة العملاء. تعرف على ميزات النسخ التجريبية.",
    "/programs/reports/": "Daily Work Reports برنامج تقارير العمل اليومية والأنشطة والمشاريع مع التصدير والطباعة. استعرض الخصائص وحالة الإصدار.",
    "/programs/smart-excel/": "SmartExcelAnalyzer برنامج تحليل بيانات Excel والإحصاءات وعرض المؤشرات والتقارير والرسوم على ويندوز. اطلع على الإصدار.",
    "/programs/stone/": "ProTech Stone Manager برنامج إدارة الرخام والبورسلان والعملاء والمخزون والعقود والتقارير. راجع الميزات وحالة الإصدار.",
}

heading_pages = {
    "/en/ai-news/", "/en/cars/", "/en/free-windows-tools/", "/en/tech-companies/"
}
def replace_meta(source: str, name: str, value: str, attr: str) -> str:
    encoded = escape(value, quote=True)
    pattern = re.compile(r'(<meta '+re.escape(attr)+r'="'+re.escape(name)+r'" content=")([^"]*)(")', re.I)
    return pattern.sub(lambda m:m.group(1)+encoded+m.group(3), source)

def process(route: str) -> dict:
    rel = route.lstrip("/") + "index.html"
    file = ROOT / rel
    src = file.read_text(encoding="utf-8")
    out = src
    if route in titles:
        title = titles[route]
        assert len(title) <= 68, (route, len(title))
        out, count = re.subn(r'<title>[\s\S]*?</title>',
            lambda m: "<title>"+escape(title,quote=False)+"</title>",out,count=1)
        assert count==1,route
        out=replace_meta(out,"og:title",title,"property")
        out=replace_meta(out,"twitter:title",title,"name")
    if route in descriptions:
        desc=descriptions[route]
        assert 70 <= len(desc) <= 155,(route,len(desc))
        out=replace_meta(out,"description",desc,"name")
        out=replace_meta(out,"og:description",desc,"property")
        out=replace_meta(out,"twitter:description",desc,"name")
    if route in heading_pages:
        opens=len(re.findall(r"<h3\b",out,re.I))
        closes=len(re.findall(r"</h3>",out,re.I))
        if opens==0:
            assert len(re.findall(r"<h2\b",out,re.I))>=2,route
        else:
            assert opens==closes,(route,opens,closes)
        out=re.sub(r"<h3\b","<h2",out,flags=re.I)
        out=re.sub(r"</h3>","</h2>",out,flags=re.I)
    if route == "/en/about/" and 'id="about-download-guidance"' not in out:
        # Adds substantive product / download guidance rather than keyword stuffing.
        section = (
          '<section class="en-info-block" id="about-download-guidance">'
          '<h2>How to explore and verify our releases</h2>'
          '<p>Start with the <a href="/en/programs/">software catalog</a> to compare the '
          'purpose of each application. A program page explains the supported workflow, '
          'the current release state and, when available, the official download destination. '
          'Some products are marked Beta, Preview or in development; those labels are '
          'not interchangeable with a stable or independently certified release.</p>'
          '<p>When a download is available, check that it links to the project\'s official '
          'GitHub release rather than an unrelated mirror. The '
          '<a href="/en/security/">software safety page</a> explains installer checks '
          'and security limitations, including what unsigned software warnings can mean. '
          'If an application has no public release yet, its page should make that status '
          'clear instead of displaying an invented download.</p>'
          '<p>Alghad Digital publishes technology news as a secondary section. '
          'For software questions, use the contact options on the relevant program page. '
          'These distinctions help visitors decide whether a tool suits their work '
          'before downloading or installing anything.</p></section>'
        )
        assert out.count("</main>")==1
        out=out.replace("</main>",section+"</main>",1)
    if out!=src:file.write_text(out,encoding="utf-8",newline="\n")
    return {"route":route,"changed":out!=src}

def main() -> None:
    tree=ET.parse(ROOT/"sitemap.xml")
    routes=[]
    for element in tree.findall("s:url/s:loc",NS):
        url=element.text
        assert url and url.startswith("https://alghad.digital/")
        routes.append(url[len("https://alghad.digital"):])
    assert len(routes)==42 and len(set(routes))==42
    assert set(titles).issubset(routes),set(titles)-set(routes)
    assert set(descriptions).issubset(routes),set(descriptions)-set(routes)
    changed=sum(process(route)["changed"] for route in routes)
    print(f"SEO_METADATA_IMPROVED routes={len(routes)} changed={changed} titles={len(titles)} descriptions={len(descriptions)} headings={len(heading_pages)}")
if __name__=="__main__":
    main()
