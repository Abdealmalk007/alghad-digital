# Alghad Digital v3.2.0 — alghad.digital

موقع عرض برامج وتطبيقات حديث، عربي RTL، يعمل مباشرة كـ Static Website على GitHub Pages أو أي استضافة ملفات ثابتة.

## ما يحتويه الإصدار
- 10 برامج مع صور SVG توضيحية محلية ووصف ومميزات وتفاصيل وأنظمة التشغيل.
- 5 مستودعات عامة منشورة تحت حساب Abdealmalk007، و5 مشاريع بحالة «قريبًا جدًا».
- استبعاد كامل لبرنامجي عُمر ومطبخ ريم من واجهة الموقع والكتالوج.
- معرض بصري حي في الصفحة الرئيسية يُظهر نماذج من برامج Kitchen CAD Pro وStone Manager وDownload PRO.
- بحث فوري، فلاتر Windows/Android وحالة النشر، وترتيب حسب الاسم أو حالة النشر.
- مقارنة جانبية تفاعلية بين برنامجين أو ثلاثة مع الإصدارات والمنصات والمميزات.
- مشاركة رابط مباشر لكل برنامج بصيغة https://alghad.digital/?app=stone (مع تغيير ID حسب البرنامج).
- مظهر داكن وفاتح، تصميم متجاوب، دعم لوحة المفاتيح، وشاشات التفاصيل القابلة للوصول.
- واجهة لا تتطلب React أو Node في الإنتاج، ولا تتصل بأي خدمات تتبع أو تجمع بيانات مستخدم.

## توضيح حالة البرامج
«مكتمل» تعني أن مستودع البرنامج العام منشور على GitHub، لا أنها شهادة نجاح الاختبارات النهائية أو صلاحية جميع ملفات التنفيذ. روابط الإصدارات Preview موضحة في تفاصيل المنتج، ولا تُعرض روابط تنزيل مختلقة.
الصور المنشورة توضيحية، وليست صور شاشة فعلية مأخوذة من البرامج.

## التشغيل المحلي
افتح index.html أو Start_Preview.cmd، أو شغّل خادمًا محليًا من مجلد الموقع:

    python -m http.server 8080

ثم افتح http://localhost:8080

## الاختبارات
يتطلب اختبار البيانات Node.js:

    node tests/smoke-test.cjs

اختبار المتصفح الفعلي (Windows مع Chrome وNode.js 22+):

    node tests/browser-test.cjs

يوثق اختبار Chrome البحث والتصفية والترتيب والمقارنة والروابط المباشرة والاستجابة بعرض 390px ويُنشئ تقريرًا وصورة خارج مجلد الموقع في AlghadDigitalSite_QA.

## الملفات المهمة
- index.html: الصفحة الرئيسية
- assets/products.js: مصدر بيانات الكتالوج الوحيد
- assets/style.css وassets/v2.css وassets/v3.css وassets/v3_1.css: التصميم
- assets/app.js وassets/v3.js وassets/v3_1.js: وظائف العرض والمقارنة والمشاركة والتواصل
- assets/previews/*.svg: 10 صور توضيحية
- CNAME: النطاق المخصص
- DEPLOYMENT_AR.md: تعليمات النشر الآمن
- Publish_To_GitHub.ps1: نشر الملفات المصرح بها إلى مستودع موجود

## الخصوصية
لا يتضمن الموقع بيانات العملاء أو الموظفين أو مفاتيح API أو بيانات تسجيل الدخول، وينشر فقط بريد التواصل الرسمي المصرح به للموقع: protech.2025.2026@gmail.com، دون نشر رقم الهاتف.

© Alghad Digital 2026.

## التحسينات في v3.2.0
- إضافة قسم تواصل مباشر بعنوان ProTech وبريد رسمي ورابط mailto مع زر نسخ العنوان.
- نظام بصري مطوّر للواجهات وبطاقات البرامج مع خطوط عربية عصرية وحركات بسيطة تراعي تقليل الحركة.
- تحسين تنقل الجوال، وتنسيق الصفحة الرئيسية، وسطر المجالات، وشريط تقدم التصفح.
- الحفاظ على 10 برامج والكتالوج الأصلي وروابط GitHub مع اختبارات تشغيل ومراجعة خصوصية.

## v3.2.0 — التحميل المباشر والتحقق الأمني
- يظهر لكل إصدار منشور زر تحميل مباشر في بطاقة البرنامج وفي نافذة التفاصيل.
- الإصدار التجريبي له حالة Preview واضحة، مع خيارات ARM64/Universal أو Setup/Portable حسب الملفات المنشورة.
- روابط التحميل مأخوذة من GitHub Releases العامة فقط؛ ملف Android Debug لا يُعرض كتوزيع عام.
- لا يظهر Stone Manager برابط تنزيل غير صالح: لم ينشر Release عام حتى تاريخ التحقق.
- روابط SHA256SUMS مرفقة للإصدارات التي نشرتها على GitHub.
- جرى تفعيل Content Security Policy على صفحة HTML، ومراجعة روابط التحميل باستخدام allowlist لنطاق GitHub.
- **حالة أمان الموقع HTTPS تختلف عن توقيع ملفات EXE/APK**: إصدار توقيع رقمي موثوق وتطوير سمعة التوقيع مطلوبان لمعالجة تحذيرات SmartScreen للمستخدمين؛ لا يمكن إزالتهما بتغيير CSS أو إعدادات الدومين.
- ملفات واجهة التحميل: assets/downloads.js وassets/downloads-ui.js وassets/downloads.css.

## v3.3.0 — واجهة الإصدارات ومركز الثقة
- قسم الإصدارات المتاحة يقدم روابط تنزيل رسمية مباشرة لـ 4 برامج، ويصرح بأن Stone Manager ليس له إصدار عام حاليًا.
- مركز الثقة يوضح اتصال HTTPS وفصل أمان الدومين عن توقيع الملفات وملف security.txt للتبليغ الأمني.
- فحص Chrome clean-profile عبر CDP أظهر TLS 1.3 و secure=true دون أخطاء، رغم وجود تبويبات قديمة للموقع.
- أزرار القائمة أصبحت تبرز الإصدارات المتاحة.
- التصميم محسن للجوال وتقليل المسافات الزائدة بين الأقسام.
- تنبيه: تبويب قديم تجاوز تحذير الشهادة خلال إعداد SSL يمكن أن يحتفظ بعرض «غير آمن» حتى إعادة تحميله أو فتح تبويب جديد. لا يمكن للموقع إخفاء تحذيرات المتصفح.

## v3.4.0 — تحديث الكتالوج
- إزالة Call Recorder PRO نهائيًا من واجهة الموقع والكتالوج والصورة المنشورة (مع الاحتفاظ بنسخة احتياطية محلية خارج موقع النشر).
- إجمالي الكتالوج الآن: 10 برامج؛ 5 بمستودعات عامة، و5 قادمة قريبًا، مع الاحتفاظ بروابط التحميل الأربعة المتاحة.
- تحديث العدادات وتحسين تجربة البحث والتنقل للأجهزة الصغيرة.

## v3.5.0 — Tech News + Free Windows Utilities
- Arabic news section with direct credited news links, Gregorian dates, category filters and source directory.
- Technology headlines sourced as limited metadata from publishers' RSS, never cloned article bodies or photos.
- scripts/update_news.py refreshes JSON plus prebuilt JS safely; a GitHub Actions workflow schedules requests every four hours. Actual scheduling depends on repo settings and GitHub queues.
- Source-only links for Al Arabiya, Asharq and Arageek when feed access is unavailable.
- Eight Windows utility cards with original vector illustrations, features, license conditions and official vendor download pages.
- Files: assets/editorial.js, assets/editorial.css, assets/news-data.js, assets/news.json, assets/tools-data.js, assets/tools.json, assets/tools/*.svg.
- Existing ten ProTech programs, exclusions and direct GitHub release links are preserved.
