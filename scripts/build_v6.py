"""Idempotent V6 enhancement, rebuilt after bilingual pages on every news run."""
from pathlib import Path
import re,json,html
from xml.etree import ElementTree as ET
import build_seo as seo
from v6_content import tutorial
ROOT=Path(__file__).resolve().parents[1]
P=seo.read_javascript_data("assets/products.js","AL_GHAD_PRODUCTS")
D=seo.read_javascript_data("assets/downloads.js","AL_GHAD_DOWNLOADS")
F=json.loads((ROOT/"assets/release-facts.json").read_text(encoding="utf8"))["releases"]
priority=["smart-excel","reports","hr","download"]
assert [p["id"] for p in P[:4]]==priority
by={p["id"]:p for p in P}
def e(x):return html.escape(str(x),quote=True)
descs={"smart-excel":("تحليل جداول Excel والتقارير","Excel analysis and reporting"),"reports":("تقارير العمل اليومية المرنة","Flexible daily work reports"),"hr":("الموظفون والحضور والرواتب","Employees, attendance and payroll"),"download":("إدارة تنزيل وتشغيل الوسائط","Media downloads and playback")}
steps={
"smart-excel":(["استورد نسخة من ملف Excel.","حدد الأعمدة المناسبة للتحليل والتجميع.","راجع النتائج والتقارير قبل تصديرها."],["Import a copy of your Excel workbook.","Choose suitable columns for analysis and grouping.","Review results and reports before exporting."]),
"reports":(["حدد تاريخ التقرير وبيانات العمل.","سجّل الأنشطة والأقسام المطلوبة.","راجع التقرير قبل تصديره أو مشاركته."],["Choose the reporting date and work details.","Record activities and relevant sections.","Review the report before exporting or sharing."]),
"hr":(["ابدأ ببيانات موظفين تجريبية.","راجع سجلات الحضور والإجازات والرواتب.","تحقق من النتائج قبل استخدام بيانات حقيقية."],["Start with sample employee records.","Review attendance, leave and payroll records.","Check results before using real records."]),
"download":(["اختر إصدار APK الرسمي من صفحة التحميل.","استخدم مصادر الوسائط المصرح لك بتنزيلها.","راجع خيارات الدقة وإدارة الملفات المتاحة."],["Select the official APK from the downloads page.","Use media sources you are authorized to download.","Review available quality and file management options."])}
def wrap(name,content):return f'<!-- V6_{name}_BEGIN -->{content}<!-- V6_{name}_END -->'
def card(pid,en):
 p=by[pid]; d=D[pid]; a=next(x for x in d["files"] if x.get("recommended"))
 assert seo.safe_release(a["url"],d["repository"])
 prefix="/en" if en else ""
 return f'<article class="v6-card" data-v6-priority="{pid}"><img src="/{e(p["preview"])}" alt="{e(p["title"])} — {"illustration" if en else "صورة توضيحية"}" width="960" height="540" loading="lazy" decoding="async"><h3 dir="auto">{e(p["title"])}</h3><p>{e(descs[pid][en])}</p><span class="v6-meta">Beta · {e(d["version"])} · {e(", ".join(p["platforms"]))}</span><div class="v6-actions"><a href="{prefix}/programs/{pid}/">{"Details" if en else "التفاصيل"}</a><a class="v6-download" href="{e(a["url"])}" rel="noopener noreferrer" target="_blank">{"Download" if en else "تنزيل"}</a></div></article>'
def featured(en):
 title="Featured software" if en else "أبرز برامجنا"
 intro="Four tools for everyday productivity. All listed releases are experimental previews." if en else "أربع أدوات للإنتاجية اليومية؛ الإصدارات المتاحة نسخ تجريبية."
 return wrap("FEATURED",f'<section class="v6-panel {"en-shell" if en else "shell"}" aria-labelledby="v6-featured-title"><span class="v6-kicker">PROTECH / FEATURED</span><h2 id="v6-featured-title">{title}</h2><p>{intro}</p><div class="v6-grid">{"".join(card(x,en) for x in priority)}</div></section>')
def guide(pid,en):
 p=by[pid]; d=D.get(pid,{}); generic=(["راجع متطلبات المنصة وحالة الإصدار.","جرّب الوظائف على بيانات اختبار غير حساسة.","راجع النتائج واحفظ نسخة احتياطية قبل الاعتماد."],["Review platform requirements and release status.","Try the available features on non-sensitive sample data.","Review results and keep a backup before relying on the software."])
 items=steps.get(pid,generic)[en]; title="Quick start" if en else "دليل البدء السريع"
 platforms=", ".join(p["platforms"]); a=next((x for x in d.get("files",[]) if x.get("recommended")),None)
 channel="Beta" if a else ("In development / no public file" if en else "قيد التطوير / لا يوجد ملف عام")
 info=f'{e(platforms)} · {e(channel)} · {e(d.get("version",p["version"]))}'+(f' · {a["bytes"]/1048576:.1f} MiB' if a else '')
 f=F.get(pid,{})
 if f.get("version")==d.get("version") and f.get("published_at"):info+=" · "+e(f["published_at"][:10])
 note=("Preview release: use test data and check the official release notes." if en else "نسخة تجريبية: استخدم بيانات اختبار وراجع ملاحظات الإصدار الرسمية.") if a else ("No public installer is listed; check the program page for development status." if en else "لا يوجد مثبت عام؛ راجع صفحة البرنامج لمعرفة حالة التطوير.")
 return wrap("GUIDE",f'<section class="v6-panel"><span class="v6-kicker">PROTECH / QUICK START</span><h2>{title}</h2><p class="v6-meta">{info}</p><ol class="v6-steps">{"".join("<li>"+e(x)+"</li>" for x in items)}</ol><p>{e(note)}</p></section>')
def latest_releases(en):
 rows=[]
 for pid,f in sorted(F.items(),key=lambda kv:kv[1].get("published_at",""),reverse=True):
  d=D.get(pid,{})
  if pid not in by or d.get("version")!=f.get("version") or d.get("repository")!=f.get("repository"):continue
  url=f.get("tag_url","")
  if not url.startswith("https://github.com/Abdealmalk007/"+d["repository"]+"/releases/tag/"):continue
  date=f["published_at"][:10]
  a=next((x for x in d.get("files",[]) if x.get("recommended")),None)
  if not a or not seo.safe_release(a["url"],d["repository"]):continue
  title=e(by[pid]["title"]); version=e(f["version"]); prefix="/en" if en else ""
  rows.append(f'<li class="v6-release-row" data-v6-release="{e(pid)}"><time datetime="{e(date)}">{e(date)}</time><strong dir="auto">{title} · {version}</strong><span class="v6-meta">Beta · {a["bytes"]/1048576:.1f} MiB</span><a href="{prefix}/programs/{e(pid)}/">{"Program details" if en else "تفاصيل البرنامج"}</a><a href="{e(url)}" rel="noopener noreferrer" target="_blank">{"Official release notes" if en else "ملاحظات الإصدار الرسمية"}</a></li>')
 if not rows:return ""
 title="Latest verified releases" if en else "أحدث إصدارات برامجنا"
 desc="Publication dates from verified GitHub release data; these are preview builds." if en else "تواريخ النشر من بيانات إصدارات GitHub المتحققة؛ هذه نسخ تجريبية."
 return wrap("RELEASES",f'<section class="v6-panel {"en-shell" if en else "shell"}" id="v6-releases"><span class="v6-kicker">PROTECH / RELEASES</span><h2>{title}</h2><p>{desc}</p><ul class="v6-release-list">{"".join(rows)}</ul></section>')
ns={"s":"http://www.sitemaps.org/schemas/sitemap/0.9"}
urls=[x.text for x in ET.parse(ROOT/"sitemap.xml").findall("s:url/s:loc",ns)]
for url in urls:
 route=url.removeprefix("https://alghad.digital").strip("/")
 f=ROOT/route/"index.html"; s=f.read_text(encoding="utf8"); en=route=="en" or route.startswith("en/")
 s=re.sub(r"<!-- V6_([A-Z]+)_BEGIN -->[\s\S]*?<!-- V6_\1_END -->","",s)
 head=wrap("ASSETS",'<link rel="stylesheet" href="/assets/v6.css?v=6.3.0"><script defer src="/assets/v6.js?v=6.3.0"></script>')
 assert s.count("</head>")==1;s=s.replace("</head>",head+"</head>")
 if route in ("","en"):
  mark='<section class="en-section" id="programs">' if en else '<section class="products-section section" id="products"'
  assert s.count(mark)==1;s=s.replace(mark,featured(en)+mark,1)
  dl='<section class="en-section" id="downloads">' if en else '<section class="release-showcase-section" id="downloads"'
  assert s.count(dl)==1;s=s.replace(dl,latest_releases(en)+dl,1)
 m=re.fullmatch(r"(?:en/)?programs/([a-z0-9-]+)",route)
 if m and m[1] in by:
  assert s.count("</main>")==1;s=s.replace("</main>",guide(m[1],en)+tutorial(m[1],en)+"</main>")
 f.write_text(s,encoding="utf8",newline="\n")
print(f"V6_BUILD_PASS pages={len(urls)} priority={len(priority)} guides={len(P)*2}")
