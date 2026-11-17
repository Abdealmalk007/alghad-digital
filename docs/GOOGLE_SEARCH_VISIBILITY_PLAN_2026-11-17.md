# خطة الظهور في Google — الغد ديجتال / جيل الغد / ProTech

التاريخ: 17 نوفمبر 2026
الموقع: https://alghad.digital
اللغات: العربية (الجذر) والإنجليزية (/en/)
الأولوية: برامج ProTech أولًا، الأخبار ثانيًا

## الهدف القابل للقياس
أن يتمكن الزائر من العثور على الموقع باسم «الغد ديجتال»، «جيل الغد»، «ProTech»، «Pro Tech»، «بروتك»، «Alghad Digital» و«Jil Al Ghad»، بالإضافة إلى أسماء البرامج والبحث الوصفي المرتبط بوظيفة كل برنامج. لا يوجد ضمان لظهور فوري أو ترتيب محدد؛ Google تختار الفهرسة والترتيب واسم الموقع المعروض.

## خطة التنفيذ — 12 مهمة

| # | المهمة | المعيار | الحالة |
|---|---|---|---|
| 01 | فحص حالة ملفات الموقع والفهرسة | استجابة الموقع، robots.txt وsitemap.xml وملف التحقق | مُنجز محليًا |
| 02 | جرد الصفحات واللغات | 42 صفحة: 21 عربي و21 إنجليزي | مُنجز |
| 03 | مراجعة Canonical وHreflang وH1 | 0 أخطاء في الفحص الآلي | مُنجز |
| 04 | تقوية اسم الموقع بالعربية | وصف وعنوان يربطان «جيل الغد» و«Pro Tech» بالموقع | مُنجز |
| 05 | تحسين مدخل البحث الإنجليزي | عنوان ووصف ومحتوى مرئي يستخدم Alghad Digital وProTech وJil Al Ghad | مُنجز |
| 06 | توحيد تعريف WebSite وOrganization | WebSite واحد في جذر النطاق وWebPage خاص بالنسخة الإنجليزية | مُنجز |
| 07 | ضبط Sitemap للتحديثات | lastmod للمحتوى الإخباري المتغير من تواريخ المقالات الأصلية فقط | مُنجز |
| 08 | حماية الهوية والروابط | الحفاظ على كتالوج البرامج، التنزيلات، WhatsApp، البحث والأمان | اختبار آلي |
| 09 | استمرار البناء الآلي | تشغيل تحسينات SEO قبل بناء فهرس البحث في كل تحديث أخبار | مدمج في GitHub Actions |
| 10 | تدقيق SEO المستمر | فحص 42 عنوانًا ووصفًا وcanonical وhreflang واختبار Structured Data | مدمج في CI |
| 11 | التحقق من الواجهة | متصفح حقيقي + المقاسات المختلفة + اختبار عدم تداخل العناصر | اختبار قبل الإصدار |
| 12 | النشر وقياس النتيجة | GitHub Pages + Google Search Console + مراجعة مؤشرات الأداء | نشر الموقع وإجراء Search Console بحسب توفر وصول الحساب |

## البيانات المنظمة المعتمدة
- الموقع الرئيسي يحتفظ بـ WebSite باسم «الغد ديجتال» وبأسماء بديلة «جيل الغد»، «Alghad Digital»، «Jil Al Ghad» و«alghad.digital».
- ProTech / Pro Tech / بروتك هو اسم المطور Organization، وليس اسم موقع ثانٍ.
- صفحة /en/ تُعرَّف WebPage مرتبطة بـ WebSite الأساسي، بدل إنشاء هوية WebSite ثانية للمجلد.
- لا تتم إضافة تقييمات أو أسعار أو شهادات أو مراجعات غير موثقة.

## الإجراء المطلوب في Google Search Console
1. افتح https://search.google.com/search-console وحدد ملكية https://alghad.digital أو ملكية النطاق alghad.digital.
2. موقع التحقق موجود بالفعل في ملفات الموقع: google3f39246447a165d6.html. وجوده لا يؤكد وحده حالة التحقق في حساب Google.
3. اختر Indexing > Sitemaps، ثم أدخل https://alghad.digital/sitemap.xml، وتحقق من الحالة «Success» وظهور الصفحات.
4. عبر URL Inspection تحقق من الروابط الرئيسية: / و/en/ و/programs/ و/en/programs/ و/protech/ و/en/protech/.
5. عند الحاجة، اطلب Request Indexing للصفحات الأساسية؛ لا ترسل كل صفحات الموقع بشكل متكرر.
6. بعد توفر البيانات قارن Search Results Performance على 28 يومًا بآخر 28 يومًا: total clicks, impressions, CTR, average position.
7. قس الاستعلامات بالعربية والإنجليزية منفصلةً وراقب Indexing > Pages والأخطاء.
8. استخدم PageSpeed Insights / Core Web Vitals لمراقبة LCP وINP وCLS وتحديد الملفات المسببة لأي تراجع.

## الكلمات والصفحات المقصودة
- العلامة (عربي): الغد ديجتال، جيل الغد، بروتك، برو تك، برامج بروتك → الصفحة الرئيسية وصفحة /protech/.
- العلامة (إنجليزي): Alghad Digital، Jil Al Ghad، ProTech، Pro Tech، ProTech software → /en/ و/en/protech/.
- برامج Windows/Android → /programs/ و/en/programs/.
- تحليل ملفات Excel → /programs/smart-excel/، Excel data analysis → /en/programs/smart-excel/.
- الموارد البشرية والحضور والرواتب → /programs/hr/، Human Resources software → /en/programs/hr/.
- الرخام والبورسلان → /programs/stone/ و/programs/marble/، Stone and porcelain management → النسخ الإنجليزية المناظرة.
- عروض الأسعار والعقود → /programs/quotes/، quotations and contracts → /en/programs/quotes/.
- الأخبار: /news/ و/en/news/ وروابط أقسام التقنية المتخصصة.

## الضمانات
- لا يتم استخدام Meta Keywords المحشوة أو صفحات Doorway أو أسماء حزم/منتجات مختلقة.
- لا يتم الاعتماد على sitemap وحده لإثبات الفهرسة؛ نتائج Google Search Console هي المرجع الفعلي.
- لا يتم تغيير الملفات التنفيذية أو أحكام الترخيص أو حالات Beta/Preview.
- لا يتم تعديل إعدادات DNS أو ملكية Google دون التفويض المباشر والوصول الموثق.
- التغييرات صالحة لإعادة البناء Idempotent وتحميها اختبارات CI.

## مراجع Google Search Central
- https://developers.google.com/search/docs/essentials
- https://developers.google.com/search/docs/appearance/site-names
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/appearance/title-link
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
