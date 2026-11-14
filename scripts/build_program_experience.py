#!/usr/bin/env python3
"""Post-build product benefits with email-only developer contact.
Run AFTER build_en.py + build_topic_tags.py; BEFORE build_site_search.py.
Pure Python 3.12 stdlib. No runtime JavaScript, tracking, or remote assets.
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json,re,subprocess

ROOT=Path(__file__).resolve().parents[1]
EMAIL="protech.2025.2026@gmail.com"
CSS='<link rel="stylesheet" href="/assets/program-experience.css?v=1">'
START="<!-- PROTECH_PROGRAM_EXPERIENCE_BEGIN -->"
END="<!-- PROTECH_PROGRAM_EXPERIENCE_END -->"
FLOAT_START="<!-- PROTECH_WHATSAPP_BEGIN -->"
FLOAT_END="<!-- PROTECH_WHATSAPP_END -->"
# Descriptive outcomes backed by the already published features, not promised savings.
# Format: (Arabic heading, Arabic explanation, English heading, English explanation)
BENEFITS={
 "smart-excel":[
  ("قراءة أوضح للجداول","تجميع أدوات استعراض ملفات Excel وتحليلها في مساحة عمل واحدة.","Clearer spreadsheet review","Examine Excel datasets through a dedicated desktop workflow."),
  ("اكتشاف الأنماط","استخدم المؤشرات والتحليلات لمراجعة توزيع البيانات واتجاهاتها.","Explore data patterns","Review patterns and trends through data analysis tools."),
  ("نتائج سهلة للمشاركة","استفد من الرسوم ومخرجات التقارير عند مراجعة النتائج.","Communicate findings","Use reports and charts to explain analytical findings."),
  ("إطلاق أبسط محليًا","يلغي تحديث 30.7.2 تسجيل الدخول المحلي، مع التوصية بحماية ملفاتك ونسخها احتياطيًا.","Simpler local launch","The 30.7.2 update removes the login gate; protect local data and keep backups.")
 ],
 "stone":[
  ("ملفات العمل في مكان واحد","تجميع العملاء والعقود والمواد والمرفقات يسهل الرجوع إلى تفاصيل كل طلب.","One organized workspace","Keep clients, contracts, materials and attachments together for faster lookup."),
  ("متابعة أوضح للمخزون","حركة الوارد والصرف والجرد تمنحك صورة أدق عن المواد المستخدمة والمتاحة.","Clearer stock tracking","Review receipts, stock movements and counts in one workflow."),
  ("تقارير مناسبة للتواصل","تصدير PDF وExcel يساعد في تجهيز تقارير قابلة للمشاركة والطباعة.","Shareable records","Produce PDF and Excel reports for review, printing and sharing."),
  ("تنظيم المواد والخيارات","كتالوجات الرخام والبورسلان والألوان تساعد على توثيق اختيارات المشروع.","Materials in context","Record stone, porcelain and related material choices with each project.")
 ],
 "marble":[
  ("متابعة التسليم خطوة بخطوة","اجمع بيانات الطلب والعقد وحالة التسليم في سجل موحد.","Follow deliveries clearly","Keep order, contract and delivery details in a coherent record."),
  ("الاستفادة من الملفات الموجودة","استيراد Excel وCSV يسهل نقل السجلات المتوفرة بدل كتابتها يدويًا من جديد.","Reuse existing data","Import Excel and CSV records instead of re-entering the same details."),
  ("مخرجات تناسب عملك","تجهيز التقارير بصيغ PDF وExcel وCSV وغيرها لتسهيل المشاركة.","Flexible reporting","Export useful delivery reports to PDF, Excel, CSV and other supported formats."),
  ("بيانات مستقلة ومنظمة","قاعدة البيانات وإعدادات الشركة توفر مساحة واضحة لمتابعة العمل.","A structured workspace","Use a dedicated local workspace for delivery records and company settings.")
 ],
 "reports":[
  ("نماذج تتناسب مع فريقك","أنشئ أسماء الحقول والأقسام بدل الالتزام بعناوين ثابتة لا تناسب طبيعة العمل.","Reports that fit your team","Customize fields and headings rather than adapting to fixed forms."),
  ("توثيق العمل اليومي","تنظيم السجلات يساعد في مراجعة ما أُنجز ومتابعة الأعمال.","Document daily progress","Maintain clear daily records of work and follow-up items."),
  ("بدء استخدام دون بيانات مفروضة","التهيئة المرنة لا تضع أسماء أو أقسامًا افتراضية خاصة بجهة أخرى.","Start with your own structure","Set up your own labels and teams without predefined employee names."),
  ("قراءة أسهل للمتابعة","تقديم المعلومات بطريقة مرتبة يساعد على مراجعتها ومناقشتها.","Clarity for reviews","Readable, structured reports help teams discuss completed work.")
 ],
 "hr":[
  ("ملفات موظفين منظمة","يسهل جمع المعلومات الأساسية والسجلات الإدارية ضمن نظام واحد.","Organized employee records","Keep core employee details and administrative records in one place."),
  ("متابعة الحضور والإجازات","رؤية أكثر وضوحًا للسجلات ومواعيد الموظفين بدل تشتتها.","Attendance and leave overview","Review attendance, leave and important employee dates more easily."),
  ("الرواتب والتقارير","ربط بيانات الموارد البشرية بالتقارير يدعم المراجعة الإدارية.","Payroll reporting","Support payroll reviews with HR data and structured reports."),
  ("تقليل تشتت الأعمال الإدارية","الاعتماد على شاشة عمل مخصصة يسهل الوصول إلى الملفات المطلوبة.","Less scattered administration","Use a dedicated HR workspace rather than disconnected files.")
 ],
 "kitchen":[
  ("مسار تصميم متكامل مستهدف","الخطة تجمع الغرفة والفتحات والخزائن والمواد في خطوات مترابطة.","Planned end-to-end design","The roadmap connects rooms, openings, cabinets and materials in one flow."),
  ("تصوّر بصري قبل التصنيع","يستهدف المشروع عرض المخططات ونماذج 2D و3D لتوضيح أفكار التصميم.","Planned visual previews","Targeted 2D and 3D previews help communicate design ideas."),
  ("معلومات أقرب لاحتياجات الورشة","من أهداف المشروع ربط تصميم الخزائن بقوائم القص والمخرجات الفنية.","Manufacturing-oriented outputs","The roadmap aims to connect cabinet layouts with cut lists and workshop drawings."),
  ("تطوير تحت الاختبار","هذه إمكانات مخطط لها وقيد التطوير، وليست وعدًا بإصدار جاهز حاليًا.","Development in progress","These are planned capabilities, not an assertion of a ready public release.")
 ],
 "download":[
  ("ملفات الوسائط في مكان واحد","تجميع التنزيلات والصوت والفيديو يسهّل الوصول إلى ملفاتك.","Media in one place","Organize downloaded audio and video files in a single library."),
  ("تشغيل دون مغادرة التطبيق","مشغل الوسائط يختصر التنقل بين أدوات تشغيل متعددة.","Integrated playback","Use the included media player rather than jumping between apps."),
  ("تنظيم القوائم والمكتبة","المكتبة والقوائم المحلية تجعل متابعة الوسائط أكثر ترتيبًا.","Organize your library","Keep media and local playlists organized for easier browsing."),
  ("إصدار Android تجريبي","تحقق من وظائف التنزيل والتوافق مع المصدر والجهاز قبل الاعتماد عليه.","Android preview status","Check source compatibility and playback behavior before relying on this preview.")
 ],
 "care":[
  ("اعرف ما سيتغير قبل التنفيذ","معاينة المهام توضح العناصر المختارة وآثار الأوامر قبل الموافقة.","See changes before applying","Review selected operations and their intended effects before approval."),
  ("خيارات مرنة للتشغيل","استخدم نسخة Portable مباشرة، أو افتح واجهة التثبيت الاختياري.","Flexible launch modes","Run the Portable edition directly or use the optional Setup interface."),
  ("تحكم أدق في العمليات","تحديد العناصر ومراجعة السجل يساعدان على تنفيذ المهام بوضوح.","Controlled task selection","Select specific items and review logged actions before proceeding."),
  ("السلامة أولًا — Preview","عمليات WinGet وAppX المؤثرة لم تُعتمد باختبارات VM كاملة؛ استخدم جهازًا تجريبيًا.","Preview safety warning","Destructive WinGet/AppX operations are not fully VM-validated; test on non-production machines.")
 ],
 "quotes":[
  ("قوالب قابلة لإعادة الاستخدام","تجهيز عروض الأسعار والعقود من قوالب يسهل الحفاظ على أسلوب موحد.","Reusable templates","Use editable quotation and contract templates for consistent documents."),
  ("بيانات عميل مكتملة","إدارة اسم العميل ورقم جواله السعودي وعنوانه والبحث في ملفاته تقلل تشتت المعلومات.","Complete customer records","Manage customer names, normalized Saudi mobile numbers and addresses with searchable records."),
  ("متابعة التسعير والدفعات","إدارة البنود والتكلفة والدفعات تجعل العرض أو العقد أوضح.","Pricing and payments","Track quotation items, costs and payment records in one workflow."),
  ("معاينة وتقارير جاهزة","الطباعة والتصدير إلى صيغ متعددة تسهّل إرسال المستندات الرسمية.","Ready-to-share documents","Preview, print and export business documents in supported formats.")
 ]
}

def email_link(lang:str, product:str|None=None)->str:
    is_en=lang=="en"
    subject=(f"Question about {product} - Alghad Digital" if product and is_en
             else f"استفسار عن برنامج {product} - الغد ديجتال" if product
             else "ProTech software enquiry - Alghad Digital" if is_en
             else "استفسار عن برامج ProTech - الغد ديجتال")
    href="mailto:"+EMAIL+"?subject="+quote(subject,safe="")
    title="Contact by email" if is_en else "التواصل عبر البريد الإلكتروني"
    return ('<a class="protech-program-email" href="'+escape(href,quote=True)+
            '" aria-label="'+title+'"><span aria-hidden="true">✉</span><span>'+
            title+' <small dir="ltr">'+EMAIL+'</small></span></a>')

def product_experience(slug:str,title:str,lang:str,available:bool)->str:
    is_en=lang=="en"
    headline=("What will you gain from "+title+"?" if is_en else "كيف سيفيدك "+title+"؟")
    intro=("Four practical reasons to explore this software. Actual availability depends on the published release and limitations."
           if is_en else "فوائد عملية مرتبطة بخصائص المشروع، مع مراعاة حالة الإصدار والقيود المعلنة.")
    status=("In development — planned outcomes" if slug=="kitchen" and is_en
            else "قيد التطوير — فوائد مستهدفة" if slug=="kitchen"
            else "Preview release — test before production" if is_en
            else "إصدار تجريبي — اختبر قبل الاعتماد")
    cards=[]
    for index,(ar_name,ar_text,en_name,en_text) in enumerate(BENEFITS[slug],1):
        name=en_name if is_en else ar_name
        text=en_text if is_en else ar_text
        cards.append('<article class="protech-benefit-card"><span class="protech-benefit-index" aria-hidden="true">'+
                     f'{index:02d}</span><h3>'+escape(name)+'</h3><p>'+escape(text)+'</p></article>')
    status_html='<span class="protech-benefit-status">'+escape(status)+'</span>'
    call_to_action=(
      '<div class="protech-benefit-contact"><div><strong>'+
      ("Questions before downloading?" if is_en else "هل تحتاج توضيحًا قبل التحميل؟")+
      '</strong><p>'+("Contact ProTech directly about this specific application."
                     if is_en else "اسأل عن الميزات أو حالة الإصدار أو التوافق عبر البريد الإلكتروني.")+
      '</p></div>'+email_link(lang,title)+'</div>')
    return (START+'<section class="protech-program-experience" aria-label="'+
      ("Benefits of this program" if is_en else "مميزات وفوائد البرنامج")+
      '"><div class="protech-benefit-head"><div><span class="protech-benefit-kicker">'+
      ("WHY THIS SOFTWARE" if is_en else "ما الذي سيوفره لك؟")+
      '</span><h2>'+escape(headline)+'</h2><p>'+escape(intro)+'</p></div>'+
      status_html+'</div><div class="protech-benefit-grid">'+''.join(cards)+
      '</div>'+call_to_action+'</section>'+END)

def load_catalog()->list[dict]:
    s=(ROOT/"assets/products.js").read_text(encoding="utf-8")
    m=re.search(r"window\.AL_GHAD_PRODUCTS\s*=\s*(\[[\s\S]*?\]);",s)
    if not m:raise RuntimeError("Missing product source")
    records=json.loads(m.group(1))
    assert len(records)==9 and {p["id"] for p in records}==set(BENEFITS)
    return records

def update_one(relative:str,lang:str,product:dict|None):
    filepath=ROOT/relative
    if not filepath.is_file():raise FileNotFoundError(filepath)
    s=filepath.read_text(encoding="utf-8")
    s=re.sub(re.escape(START)+r".*?"+re.escape(END),"",s,flags=re.S)
    s=re.sub(re.escape(FLOAT_START)+r".*?"+re.escape(FLOAT_END),"",s,flags=re.S)
    if CSS not in s:
        if s.count("</head>")!=1:raise ValueError("Invalid head in "+relative)
        s=s.replace("</head>",CSS+"\n</head>",1)
    if product:
        block=product_experience(product["id"],product["title"],lang,product["status"]=="public")
        if lang=="ar":
            # After the real description, before the technical features/use-case list.
            marker=re.search(r'<p class="long-description">.*?</p>',s,flags=re.S)
            if not marker:raise ValueError("Arabic detail marker absent: "+relative)
            pos=marker.end()
        else:
            marker=re.search(r'<h2>What it does</h2><p>.*?</p>',s,flags=re.S)
            if not marker:raise ValueError("English detail marker absent: "+relative)
            pos=marker.end()
        s=s[:pos]+"\n"+block+"\n"+s[pos:]
        # Existing feature and use-case lists remain unchanged, providing factual detail and accessibility.
    if s.count("</body>")!=1:raise ValueError("Body marker invalid: "+relative)
    filepath.write_text(s,encoding="utf-8",newline="\n")
    print("ENHANCED",relative,"PRODUCT",product["id"] if product else "-",flush=True)

def main():
    records=load_catalog()
    product_urls={}
    for p in records:
        product_urls["/programs/"+p["id"]+"/"]=p
    sitemap=(ROOT/"sitemap.xml").read_text(encoding="utf-8")
    urls=re.findall(r"<loc>https://alghad\.digital(/[^<]*)</loc>",sitemap)
    assert len(urls)==len(set(urls))==42
    for url in urls:
        lang="en" if url.startswith("/en/") else "ar"
        normalized=url[3:] if lang=="en" else url
        product=product_urls.get(normalized)
        relative=url.lstrip("/")+"index.html"
        update_one(relative,lang,product)
    print("PROTECH_PROGRAM_EXPERIENCE_PASS",json.dumps({
      "pages":len(urls),"product_pages":len(records)*2,"benefit_cards":len(records)*2*4,
      "email_contact_links":len(records)*2,"contact":EMAIL,"languages":["ar","en"]
    }),flush=True)
if __name__=="__main__":main()
