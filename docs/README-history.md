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

## v3.6.0 — Daily News + Search Discoverability (SEO)
- News ingestion runs automatically once per day at 07:37 Asia/Riyadh (GitHub Actions, 04:37 UTC), only if repo Actions and write permissions work.
- The workflow safely rebuilds a human-readable static /news/ page and validates indexable pages before committing the daily snapshot.
- 10 unique crawlable /programs/<slug>/ pages plus /programs/, /news/, /free-windows-tools/.
- 14 canonical URLs listed in sitemap.xml, and sitemap referenced by robots.txt.
- Proper Arabic and English names of the platform and program names included in title/description, visible content, and structured metadata.
- Site adds internal links to program pages and news, and keeps all download links pointing only to supported official releases.
- Google Search Console and Bing Webmaster Tools verification/submission require access to the appropriate owner accounts. Sitemaps and schema do not guarantee indexing or rank.
- Daily autonomous site improvement is managed by a separate ChatGPT scheduled task with tests and guarded publishing.

## v3.7.0 — Search and link previews
- Original 1200×630 Open Graph image for sharing official website links on messaging and social platforms.
- Added og:image, og:image:alt, twitter:card to the homepage and 13 static pages; all values use the verified HTTPS site host.
- Added accurate BreadcrumbList structured data to program and directory pages.
- Static schema avoids invented reviews, star ratings, downloads or software prices.
- Kept social-media handles unlinked until confirmed; registration statuses are stored privately outside the public repository.
- Verified the publicly accessible property and Google HTML ownership token. The Search Console Sitemaps report still requires the owner to submit sitemap.xml in the correct property.

## v3.8.0 — Official AI, major-company and automotive news
- Three official-news editorial sections: artificial intelligence, technology companies, cars.
- 54 dated headlines initially (18 per topic) from publishers' public official RSS sources.
- Direct official feeds include OpenAI, Google, NVIDIA, AMD, Apple, Samsung, Microsoft, Toyota, Honda, Porsche and Subaru.
- Official site directory links include Claude / Anthropic, DeepSeek, Huawei, Tesla, BMW, Mercedes-Benz, Hyundai and Kia where no verified public RSS was available. These links must NOT be described as automated feeds.
- The daily GitHub Actions job fetches official feeds, rejects unsafe links, checks article dates and counts, regenerates three static SEO pages, and publishes only after validation. It retains the prior snapshot if a section has too little trustworthy information.
- Publication uses ONLY official original-language headlines and links, with publisher attribution. It does not reproduce full articles, photographs, or claim independent reporting.
- New indexable pages: /ai-news/, /tech-companies/, /cars/. Sitemap now has 17 URLs.
- The user's previously approved ProTech programs (10) and excluded apps remain unchanged.

## v3.9.0 — Daily Automatic Arabic News Translations
- English headlines from the verified publisher feeds are machine-translated to Arabic at the same daily 07:30 Asia/Riyadh GitHub Actions update.
- The unmodified original source title, publisher attribution, date and official HTTPS link are retained alongside the Arabic translation on the homepage and all four crawlable news category pages.
- Translation provider: MyMemory Translation API, free service with published quota. Only public source headlines are sent for translation, using the site's already-public contact email. No API token or password stored.
- An on-repo translation cache avoids repeating API requests for unchanged headlines. The daily job uses the cache automatically.
- Fail-safe: if an item cannot be accurately translated or the API rate-limit/availability fails, its original English title remains visible with a translation-unavailable notice. A failed translator does not invent an Arabic title.
- Translation quality is automated and can be imperfect; these translations are not authored or endorsed by the original publishers.
- New files: scripts/translate_news.py, assets/translation-cache.json, tests/translation-test.cjs.

## v3.10.0 — Alghad A visual identity and favicon package
- Approved icon concept #1: refined Alghad A monogram in mint and white on a midnight-navy rounded square.
- Standalone SVG favicon plus 16/32/48px PNG fallbacks, true multi-size favicon.ico, Apple Touch 180px, and 192/512px icons for Android and browsers.
- Manifest at site.webmanifest, using the main domain's brand and theme colors; no service worker or unrelated install behavior added.
- Homepage header and all generated program/news landing pages use the same Alghad A icon.
- All icon asset references are cache-busted at v=4 to force refresh across the website while preserving the canonical URLs.
- Added deterministic Pillow-only generator scripts/generate_brand_icons.py and tests/favicon-test.cjs to deployment QA.

## v4.0.0 — Product-first redesign
- The site's identity remains Alghad Digital (الغد ديجتال), while ProTech is the software developer. Primary audience: factories, showrooms and design/admin teams; secondary audience: individual Windows/Android users.
- Homepage priority: hero and software catalog -> four verified public Beta releases -> about/why us -> illustrative gallery -> free Windows tools -> security -> FAQ -> brief secondary technology news -> contact.
- Removed three long specialized-news modules from the homepage; their full, attributed daily feeds remain accessible at /ai-news/, /tech-companies/ and /cars/.
- True server-built no-JavaScript fallbacks: 10 product cards, four official downloadable releases, four dated source-attributed headlines. The interactive catalog enhancements remain intact.
- All published binaries are labeled Beta/Preview; Stone Manager's source repository is public but its direct installer is not. Five in-development products remain clearly marked Coming Soon.
- Verified seven GitHub Releases asset SHA-256 digests and four publication dates from GitHub's official API, displayed with official links on the site and the product pages.
- Added canonical /about/, /security/, /privacy/ pages. All 20 canonical indexable URLs are in sitemap.xml.
- Improved homepage RTL navigation, headlines, keyboard focus states and responsive layouts, including source code wrapping on narrow mobile screens.
- Kept the original approved favicon and all prior programs/downloads, and preserved the daily 07:30 Asia/Riyadh news and Arabic translation job.
- Verified in real Chrome that disabling JavaScript leaves all ten program cards, four official downloads and four news links functional.
- Domain-specific info@alghad.digital email is **not** displayed until mail routing actually works; the verified contact email remains protech.2025.2026@gmail.com. Personal telephone numbers are not disclosed on the website.
- Follow-up work requiring owner assets/accounts: real app screenshots and sanitized demo videos; production mail routing; independent code signing; live Search Console and PageSpeed baselines; consent-based testimonials; measurement provider setup.

## v4.0.1 — Factual FAQ schema for program-first landing page
- FAQPage JSON-LD is assembled from the visible homepage FAQ and validated against its exact four questions and answers.
- The product-first structure remains in place; official news remains secondary and updated daily at 07:30 Riyadh.
- A private implementation gap report is retained in AlghadDigitalSite_QA; external-service tasks are not represented as completed.

## v4.1.0 — ProTech brand search SEO
- One preferred WebSite identity: الغد ديجتال, and search phrase جيل الغد visibly explained; developer Organization ProTech separated from the WebSite entity.
- Dedicated /protech/ landing page with all ten projects, accurate published/download availability and links.
- Unique Arabic search-intent titles and visible copy for ten program landing pages; no invented ratings or prices.
- Site map now has 21 URLs, with brand SEO integrity tests incorporated into publish and daily update pipelines.
- Avoid obsolete meta keywords: Google does not use them for SEO.

## v4.2.0 — Arabic-first bilingual English edition
- Arabic remains the default at /; English pages are available at /en/ with a visible EN/AR link on every corresponding page.
- Complete 21-page static English website covering the home, all 10 products, downloads, developer, news, tools, about, privacy and software safety.
- Both editions use the same verified product/release/news data; no replicated or invented installers.
- HTML lang and dir are accurate: ar/rtl by default, en/ltr in English.
- Reciprocal hreflang ar/en/x-default and canonical tags; 42 URL bilingual sitemap.
- No machine-translation network requirement: existing program metadata is interpreted with reviewed English product descriptions. News headlines from official English-language publishers remain in their original wording.
- Both versions work without JS; a lightweight English product filter enhances the English homepage when JS is enabled.
- The 07:30 Riyadh GitHub Actions news workflow regenerates both editions and runs bilingual QA.
