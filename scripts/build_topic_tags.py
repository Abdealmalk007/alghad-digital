#!/usr/bin/env python3
"""Add useful, crawlable topic links and concise metadata to existing SEO pages.
This is a post-build step because build_seo.py and build_en.py rewrite pages daily.
It does not change sitemap URL counts or create keyword-stuffed thin landing pages.
Python 3.12+, standard library only.
"""
from __future__ import annotations
from pathlib import Path
from html import escape
import json
import re

ROOT=Path(__file__).resolve().parents[1]
CATALOG=ROOT/"assets/products.js"
START="<!-- PROTECH_TOPIC_TAGS_BEGIN -->"
END="<!-- PROTECH_TOPIC_TAGS_END -->"
CSS='<link rel="stylesheet" href="/assets/topic-tags.css?v=1">'
TAGS={
 "software":("برامج","Software","/programs/"),
 "windows":("ويندوز","Windows","/programs/#windows-software"),
 "android":("أندرويد","Android","/programs/#android-software"),
 "hr":("HR","HR","/programs/hr/"),
 "employees":("الموارد_البشرية","HumanResources","/programs/hr/"),
 "attendance":("الحضور_والانصراف","Attendance","/programs/hr/"),
 "payroll":("الرواتب","Payroll","/programs/hr/"),
 "stone":("الرخام","Stone","/programs/stone/"),
 "porcelain":("البورسلان","Porcelain","/programs/stone/"),
 "delivery":("التوصيل","Delivery","/programs/marble/"),
 "reports":("التقارير","Reports","/programs/reports/"),
 "kitchen":("تصميم_المطابخ","KitchenDesign","/programs/kitchen/"),
 "cad":("CAD","CAD","/programs/kitchen/"),
 "maintenance":("صيانة_ويندوز","WindowsMaintenance","/programs/care/"),
 "tools":("أدوات_ويندوز","WindowsTools","/free-windows-tools/"),
 "quotes":("عروض_الأسعار","Quotations","/programs/quotes/"),
 "contracts":("العقود","Contracts","/programs/quotes/"),
 "business":("إدارة_الأعمال","BusinessSoftware","/programs/quotes/"),
 "apk":("APK","APK","/programs/download/"),
 "video":("تنزيل_الفيديو","VideoDownload","/programs/download/"),
 "news":("أخبار_التقنية","TechNews","/news/"),
 "ai":("الذكاء_الاصطناعي","AI","/ai-news/"),
 "companies":("شركات_التقنية","TechCompanies","/tech-companies/"),
 "cars":("السيارات","Cars","/cars/"),
}
PER_PRODUCT={
 "stone":("software","windows","stone","porcelain","business"),
 "marble":("software","windows","stone","delivery","reports"),
 "reports":("software","windows","android","reports"),
 "hr":("software","windows","hr","employees","attendance","payroll"),
 "kitchen":("software","windows","kitchen","cad"),
 "download":("software","android","apk","video"),
 "care":("software","windows","maintenance","tools"),
 "quotes":("software","windows","quotes","contracts","business"),
}
HOMEPAGE=("software","windows","android","hr","employees","stone","quotes","kitchen","news","ai","cars")
CATALOG_TAGS=("software","windows","android","hr","stone","reports","contracts","kitchen","video")
NEWS_TAGS={
 "news":("news","ai","companies","cars"),
 "ai-news":("ai","news","companies"),
 "tech-companies":("companies","ai","news"),
 "cars":("cars","companies","news"),
}
SEO_TITLES={
 "index.html":(
  "الغد ديجتال | برامج ويندوز وأندرويد وHR - Pro Tech",
  "تعرّف على برامج ProTech لنظام Windows وأندرويد: الموارد البشرية HR، إدارة الرخام، عروض الأسعار والعقود، التقارير وتصميم المطابخ، مع روابط الإصدارات الرسمية."
 ),
 "en/index.html":(
  "Windows & Android Business Apps | ProTech - Alghad Digital",
  "Explore ProTech Windows and Android software: HR and payroll management, stone operations, quotations and contracts, reports, and kitchen design. Official download links."
 ),
 "programs/index.html":(
  "برامج ويندوز وأندرويد: HR والعقود والرخام | ProTech",
  "تصفح برامج ويندوز وأندرويد من ProTech مع ميزات إدارة الموارد البشرية HR والرواتب، العقود وعروض الأسعار، الرخام والبورسلان والتقارير، وحالة كل إصدار."
 ),
 "en/programs/index.html":(
  "Windows & Android Software: HR, Contracts & Stone | ProTech",
  "Browse ProTech Windows and Android applications for human resources, payroll, quotations, contracts, stone management, reports and media downloads, with verified release status."
 ),
}

def load_products()->list[dict]:
    text=CATALOG.read_text(encoding="utf-8")
    match=re.search(r"window\.AL_GHAD_PRODUCTS\s*=\s*(\[[\s\S]*?\]);",text)
    if not match:raise ValueError("Cannot parse product catalog")
    products=json.loads(match.group(1))
    ids={p["id"] for p in products}
    if ids!=set(PER_PRODUCT):raise ValueError(f"Catalog/topic mismatch: {ids}")
    return products

def localized(path:str, lang:str)->str:
    if lang=="ar":return path
    if not path.startswith("/"):raise ValueError(path)
    return "/en"+path

def chips(keys:tuple[str,...],lang:str)->str:
    parts=[]
    for key in keys:
        ar,en,target=TAGS[key]
        label=ar if lang=="ar" else en
        url=localized(target,lang)
        parts.append(f'<a class="protech-topic-chip" href="{escape(url,quote=True)}">#{escape(label)}</a>')
    return '<nav class="protech-topic-chips" aria-label="'+("الوسوم والتصنيفات" if lang=="ar" else "Topics and categories")+'">'+"".join(parts)+"</nav>"

def section(title:str,description:str,keys:tuple[str,...],lang:str,extra:str="")->str:
    return (START+'<section class="protech-topic-section" aria-label="'
      +("موضوعات ذات صلة" if lang=="ar" else "Related topics")+'"><h2>'+escape(title)+'</h2><p>'
      +escape(description)+'</p>'+chips(keys,lang)+extra+'</section>'+END)

def discover_sections(products:list[dict],lang:str)->str:
    windows=[p for p in products if "Windows" in p["platforms"]]
    android=[p for p in products if "Android" in p["platforms"]]
    assert len(windows)==7 and len(android)==2
    def links(rows):
        out=[]
        for p in rows:
            slug=p["id"]
            # Every link points to a real canonical product page, not a download guess.
            state=("متاح للمعاينة" if p["status"]=="public" else "قيد التطوير") if lang=="ar" else ("Published preview" if p["status"]=="public" else "In development")
            url=localized(f"/programs/{slug}/",lang)
            out.append(f'<li><a href="{escape(url)}">{escape(p["title"])}</a> — {escape(state)}</li>')
        return '<ul class="protech-topic-links">'+"".join(out)+"</ul>"
    win_title="برامج ويندوز لإدارة الأعمال والتصميم" if lang=="ar" else "Windows software for business and design"
    win_desc=("تطبيقات Windows من ProTech للموارد البشرية HR، إدارة الرخام والبورسلان، التقارير، عروض الأسعار والعقود وتصميم المطابخ. تحقق من حالة كل إصدار قبل التنزيل."
       if lang=="ar" else
       "Explore ProTech Windows applications for HR, stone management, reports, quotations, contracts and kitchen design. Check the published status of each application.")
    and_title="تطبيقات أندرويد وتنزيل الوسائط" if lang=="ar" else "Android applications and media downloads"
    and_desc=("برامج ProTech المعلنة لمنصة أندرويد، بما فيها Download Anything PRO والتقارير؛ تتفاوت ملفات التثبيت المتاحة بحسب الإصدار."
      if lang=="ar" else
      "Browse ProTech projects listing Android support, including Download Anything PRO and reporting. Installer availability depends on each release.")
    return (
     '<div class="protech-topic-categories">'
     +'<section id="windows-software"><h3>'+win_title+'</h3><p>'+win_desc+'</p>'+links(windows)+'</section>'
     +'<section id="android-software"><h3>'+and_title+'</h3><p>'+and_desc+'</p>'+links(android)+'</section>'
     +'</div>')

def update_metadata(html:str,path:str)->str:
    if path not in SEO_TITLES:return html
    title,description=SEO_TITLES[path]
    assert 30<len(description)<205
    def change(pattern:str,replacement:str,expected:int=1)->None:
        nonlocal html
        html,n=re.subn(pattern,lambda _:replacement,html,count=expected,flags=re.I)
        if n!=expected:raise ValueError(f"Metadata not found {path}: {pattern}")
    change(r"<title>[^<]*</title>","<title>"+escape(title)+"</title>")
    change(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+escape(description,quote=True)+'">')
    for property_tag,value in (("og:title",title),("og:description",description)):
        if '<meta property="'+property_tag+'"' in html:
            change(r'<meta property="'+re.escape(property_tag)+r'" content="[^"]*">',
                   '<meta property="'+property_tag+'" content="'+escape(value,quote=True)+'">')
    if '<meta name="twitter:title"' in html:
        change(r'<meta name="twitter:title" content="[^"]*">',
            '<meta name="twitter:title" content="'+escape(title,quote=True)+'">')
    if '<meta name="twitter:description"' in html:
        change(r'<meta name="twitter:description" content="[^"]*">',
            '<meta name="twitter:description" content="'+escape(description,quote=True)+'">')
    return html

def inject(relative:str,html_section:str,placement:str)->None:
    filename=ROOT/relative
    assert filename.is_file(),relative
    html=filename.read_text(encoding="utf-8")
    # Regenerated pages may contain old injection on repeated invocations.
    html,n=re.subn(re.escape(START)+r".*?"+re.escape(END),"",html,flags=re.S)
    if n>1:raise ValueError(f"Duplicate tag sections in {relative}")
    html=update_metadata(html,relative)
    if CSS not in html:
        if html.count("</head>")!=1:raise ValueError(f"No unique head in {relative}")
        html=html.replace("</head>","  "+CSS+"\n</head>",1)
    if placement=="after_hero":
        main=re.search(r"<main\b[^>]*>",html)
        if not main:raise ValueError(f"No main in {relative}")
        first_end=html.find("</section>",main.end())
        if first_end<0:raise ValueError(f"No hero section in {relative}")
        pos=first_end+len("</section>")
        html=html[:pos]+"\n"+html_section+"\n"+html[pos:]
    elif placement=="before_catalog":
        marker='<div class="directory-grid">' if relative=="programs/index.html" else '<div class="en-grid">'
        if html.count(marker)!=1:raise ValueError(f"Missing catalog grid in {relative}")
        html=html.replace(marker,html_section+"\n"+marker,1)
    elif placement=="before_main_end":
        if html.count("</main>")!=1:raise ValueError(f"No unique main end in {relative}")
        html=html.replace("</main>",html_section+"\n</main>",1)
    else:raise ValueError(placement)
    # The content generators leave indented blank lines when the prior injected block is removed.
    html=re.sub(r"(?m)^[ \t]+(?=\r?$)", "", html)
    filename.write_text(html,encoding="utf-8",newline="\n")
    print("TAGGED",relative,flush=True)

def main():
    products=load_products()
    # Main public navigation (Arabic and English) remains unchanged.
    for lang,home in (("ar","index.html"),("en","en/index.html")):
        heading="تصفح برامجنا حسب الوسوم والاختصاص" if lang=="ar" else "Explore software and news by topic"
        description=("روابط مباشرة إلى برامج ويندوز وأندرويد، نظام الموارد البشرية HR، الرخام، العقود، تصميم المطابخ وأخبار التقنية. اختر الوسم لزيارة الصفحة التي تتناول الموضوع."
          if lang=="ar" else
          "Browse Windows and Android apps, HR software, stone operations, quotations, kitchen design and technology news through direct topic links.")
        inject(home,section(heading,description,HOMEPAGE,lang),"after_hero")
    for lang,route in (("ar","programs/index.html"),("en","en/programs/index.html")):
        heading="الوسوم والتخصصات المتوفرة" if lang=="ar" else "Topics and software categories"
        description=("ابحث عن برامج ويندوز وأندرويد وإدارة الموارد البشرية HR أو تصفح القائمة حسب المهمة؛ الروابط تقود إلى صفحات البرامج وحالة إصدارها الفعلية."
           if lang=="ar" else
           "Find Windows, Android, HR, contracts and stone-management apps. Each link shows the actual product and its release status.")
        inject(route,section(heading,description,CATALOG_TAGS,lang,discover_sections(products,lang)),"before_catalog")
    for p in products:
        slug=p["id"]
        for lang,route in (("ar",f"programs/{slug}/index.html"),("en",f"en/programs/{slug}/index.html")):
            heading=("وسوم مرتبطة ببرنامج "+p["title"]) if lang=="ar" else ("Topics related to "+p["title"])
            description=("تصفح البرامج والمجالات المتصلة بهذا التطبيق عبر روابط داخل موقع الغد ديجتال."
               if lang=="ar" else
               "Explore related software categories and specific topics through linked site pages.")
            inject(route,section(heading,description,PER_PRODUCT[slug],lang),"before_main_end")
    for slug,keys in NEWS_TAGS.items():
        for lang,route in (("ar",f"{slug}/index.html"),("en",f"en/{slug}/index.html")):
            heading="تصفح موضوعات الأخبار" if lang=="ar" else "Explore news topics"
            description=("الوسوم التالية تقود إلى صفحات الأخبار المتخصصة، ومصادر الأخبار الأصلية مذكورة داخل كل خبر."
                 if lang=="ar" else
                 "Use these links to browse related news categories. Each headline includes its original publisher.")
            inject(route,section(heading,description,keys,lang),"before_main_end")
    for lang,route in (("ar","free-windows-tools/index.html"),("en","en/free-windows-tools/index.html")):
        heading="وسوم أدوات Windows" if lang=="ar" else "Windows tools topics"
        description=("أدوات وبرامج ويندوز مع روابط المشاريع الأخرى من ProTech."
             if lang=="ar" else "Browse Windows tools and related ProTech applications.")
        inject(route,section(heading,description,("windows","tools","software"),lang),"before_main_end")
    print("TOPIC_TAGS_GENERATED PAGES=30 CATALOG_PRODUCTS=8 NEWS_TOPICS=4 LANGUAGES=2",flush=True)

if __name__=="__main__":
    main()
