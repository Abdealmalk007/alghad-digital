#!/usr/bin/env python3
"""Generate factually grounded About, Security and Privacy pages for Alghad Digital."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("seo",ROOT/"scripts"/"build_seo.py")
assert spec and spec.loader
seo=importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)
DOMAIN="https://alghad.digital"
CONTACT="protech.2025.2026@gmail.com"
PAGES=[
 ("about","من نحن — الغد ديجتال",
  "الغد ديجتال هو موقع برامج ProTech وحلول Windows وAndroid للمصانع والمعارض وفرق التصميم والإدارة.",
  """<span class="eyebrow">ALGHAD DIGITAL / PROTECH</span>
<h1>من نحن — الغد ديجتال</h1>
<p class="hero-desc">الغد ديجتال مساحة تعريفية لبرامج ProTech الموجّهة للإنتاجية وإدارة الأعمال والتصميم، مع متابعة تقنية مختصرة.</p>
<section class="more"><h2>ما الذي نقدمه؟</h2>
<p>نطوّر ونعرض برامج عملية مثل Marble Delivery Pro وProTech HR وDaily Work Reports وDownload Anything PRO، وننشر حالة كل مشروع وروابط الإصدارات المتاحة فعلًا.</p>
<p>نهدف إلى تقديم أدوات مفيدة للمصانع والمعارض وفرق الإدارة والتصميم، إلى جانب تطبيقات تخدم مستخدمي Windows وAndroid.</p></section>
<section class="more"><h2>من يطوّر البرامج؟</h2>
<p>ProTech — المطوّر المسؤول عن مجموعة البرامج المعروضة في الموقع. نسعى إلى وضوح الميزات، وعرض حالة الإصدارات دون وصف نسخة تجريبية بأنها مستقرة ما لم تثبت الاختبارات ذلك.</p>
<p>لم نُضف شهادات عملاء أو عدد مستخدمين غير موثق أو صورًا شخصية لم يوافق صاحبها على نشرها.</p></section>
<section class="more"><h2>مشاريعنا</h2>
<p><a href="../programs/">عرض جميع برامج ProTech</a> · <a href="../#downloads">الإصدارات المتاحة</a> ·
<a href="../security/">الأمان والتحقق من التنزيلات</a></p></section>
<section class="more"><h2>التواصل</h2><p>البريد الرسمي الحالي للتواصل:
<a href="mailto:protech.2025.2026@gmail.com">protech.2025.2026@gmail.com</a>.</p></section>"""),
 ("security","الأمان والتحقق من الملفات",
  "كيف تتحقق من التنزيلات الرسمية لبرامج ProTech، وحدود التوقيع الرقمي وWindows SmartScreen والملفات المنشورة.",
  """<span class="eyebrow">SOFTWARE RELEASE SAFETY</span>
<h1>الأمان والتحقق من الإصدارات</h1>
<p class="hero-desc">نحرص على توضيح مصادر ملفات برامج ProTech. تنزيل الملفات من روابط GitHub الرسمية لا يعادل تلقائيًا توقيعها رقميًا أو ضمان خلوها من العيوب.</p>
<section class="more"><h2>روابط التحميل الرسمية</h2>
<p>تُعرض روابط الإصدارات المنشورة من مستودعات المطوّر على
<a href="https://github.com/Abdealmalk007" rel="noopener noreferrer" target="_blank">GitHub</a>.
نوضح إذا كان الإصدار تجريبيًا (Beta/Preview) أو لا يتوفر ملف تثبيت عام.</p></section>
<section class="more"><h2>التحقق باستخدام SHA-256</h2>
<p>عند نشر ملف <code>SHA256SUMS.txt</code> مع الإصدار، يمكنك مقارنة بصمة الملف الذي نزّلته مع القيمة المنشورة في نفس Release.
على Windows يمكنك استخدام الأمر:</p>
<pre><code>Get-FileHash -Algorithm SHA256 "C:\\Path\\To\\Installer.exe"</code></pre>
<p>ملف البصمات الصادر عن المطوّر لا يحل محل تدقيق أمني مستقل. لا نعرض بصمة محسوبة أو تقرير فحص ما لم نتحقق منه.</p></section>
<section class="more"><h2>التوقيع الرقمي وSmartScreen</h2>
<p>لا نؤكد أن جميع ملفات EXE وAPK موقّعة بتوقيع تجاري معتمد. قد تظهر تحذيرات Microsoft SmartScreen حتى مع ملفات منشورة من مصدر رسمي. السمعة الرقمية والتوقيع يحتاجان إلى إعدادات وشهادات مستقلة؛ لا ننصح بتعطيل وسائل الحماية لتثبيت البرامج.</p></section>
<section class="more"><h2>إذا وجدت مشكلة</h2>
<p>امتنع عن تشغيل الملف عند وجود شك في مصدره أو سلامته. يمكنك إرسال اسم البرنامج والإصدار ووصف المشكلة إلى
<a href="mailto:protech.2025.2026@gmail.com">البريد الرسمي للمطور</a>.</p></section>"""),
 ("privacy","سياسة الخصوصية",
  "شرح جمع البيانات وروابط الأطراف الخارجية في موقع الغد ديجتال وبرامج ProTech، والتمييز بين الموقع والتطبيقات.",
  """<span class="eyebrow">PRIVACY / ALGHAD DIGITAL</span>
<h1>سياسة الخصوصية</h1>
<p class="hero-desc">توضح هذه الصفحة طريقة عمل الموقع التعريفي الثابت. تختلف معالجة البيانات داخل التطبيقات نفسها بحسب البرنامج وإعداداته.</p>
<section class="more"><h2>بيانات الموقع</h2>
<p>موقع الغد ديجتال يعرض صفحات HTML وملفات أخبار متحقَّقًا منها مسبقًا. لا يحتوي الموقع حاليًا على نموذج تسجيل حساب أو قاعدة بيانات لتخزين بيانات الزوار. قد تستخدم واجهة العرض مساحة التخزين المحلية لتذكر تفضيلات شكل الموقع.</p>
<p>قد يحتفظ مقدم الاستضافة GitHub Pages بسجلات الوصول التقنية وفق سياساته الخاصة، ولا تعني سياسة هذا الموقع التحكم في سجلاته.</p></section>
<section class="more"><h2>الروابط والخدمات الخارجية</h2>
<p>عند فتح GitHub أو WhatsApp أو مواقع الأخبار الرسمية أو روابط التنزيل، ستنتقل إلى خدمات مستقلة تحكمها سياسات الخصوصية الخاصة بها. التواصل بالبريد الإلكتروني يرسل المعلومات التي تختار مشاركتها مع المطور.</p></section>
<section class="more"><h2>الأخبار الآلية</h2>
<p>يتم جمع العناوين من مصادرها العامة عبر مهام تحديث على GitHub، ثم ترجمة بعض العناوين الإنجليزية آليًا. قد تُرسل العناوين العامة إلى خدمة الترجمة، وليس بيانات زوار الموقع.</p></section>
<section class="more"><h2>خصوصية برامج ProTech</h2>
<p>قد تختلف صلاحيات وتخزين بيانات العملاء بين تطبيق وآخر. تحقق من وصف التطبيق ومستودعه وشاشة الأذونات قبل استخدامه. لا تنطبق هذه الصفحة تلقائيًا بوصفها سياسة خصوصية مفصلة لكل برنامج.</p></section>
<section class="more"><h2>التواصل بشأن الخصوصية</h2>
<p>راسلنا على <a href="mailto:protech.2025.2026@gmail.com">protech.2025.2026@gmail.com</a>.</p></section>""")
]
for slug,name,description,content in PAGES:
    canonical=f"{DOMAIN}/{slug}/"
    schema={"@context":"https://schema.org","@type":"WebPage",
            "name":name,"description":description,"url":canonical,"inLanguage":"ar",
            "isPartOf":{"@type":"WebSite","name":"الغد ديجتال","url":DOMAIN}}
    out=ROOT/slug/"index.html"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(seo.page(title=name+" | Alghad Digital",
                            description=description,canonical=canonical,
                            content='<div class="breadcrumbs"><a href="../">الرئيسية</a> / '+name+'</div>'+content,
                            schema=schema),
                   encoding="utf-8",newline="\n")
    print("PUBLIC_INFORMATION_PAGE="+str(out.relative_to(ROOT)))
