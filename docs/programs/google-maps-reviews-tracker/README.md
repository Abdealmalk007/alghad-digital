# Google Maps Reviews Tracker

Google Maps Reviews Tracker v44 لنظام Windows، إصدار Beta مع لوحة تحكم تعرض مصدر الأرقام وتغطية الفروع وتاريخ آخر جلب. تنبّه عند نقص البيانات أو قدمها، وتتطلب مراجعات Google Business Profile تفويض OAuth مصرحًا به.

واجهة عربية RTL وإنجليزية مع جداول جميع الفروع وترتيب ثابت وفلاتر واضحة وتصدير CSV/PDF. يحتسب متوسط التقييم من الفروع ذات القيم المعروفة، ويعرض تغطية أعداد المراجعات بشكل جزئي عندما تنقص البيانات. تُميّز تواريخ المراجعات النسبية عن تاريخ الاستيراد، ولا تُختلق اتجاهات تاريخية من لقطة واحدة. يتطلب جلب مراجعات الفروع المملوكة صلاحية Google Business Profile OAuth؛ يعرض Places API عينة مراجعات محدودة فقط. نسخة Beta غير موقّعة رقميًا.

## المزايا الرئيسية

- واجهة عربية RTL وإنجليزية ولوحة مؤشرات
- سجل تاريخي لتقييمات الفروع ومؤشرات تحليلية
- إدارة المراجعات ومتابعة الملاحظات والتنبيهات
- تصدير بيانات إلى Excel وCSV وPDF مع حماية النصوص
- Places API وBusiness Profile API مع صلاحيات Google الرسمية
- تغطية البيانات ومؤشرات توضح المفقود والقديم
- عرض كل الفروع وفرزها وتصحيح المتوسطات والفلاتر
- حفظ بيانات المستخدم خارج ملفات تثبيت البرنامج

## الإصدار والمنصات

- الإصدار المعلن: 43.0.0-beta.1.
- المنصات المعلنة: Windows.
- حالة الإتاحة: Beta / Preview — إصدار تجريبي.
- الحد الأدنى لإصدار النظام والذاكرة: غير متحقق؛ راجع ملاحظات الإصدار.

## التثبيت والتشغيل

- [تحميل Reviews Tracker v44 — Windows Setup (Beta)](https://github.com/Abdealmalk007/GoogleMapsReviewsTracker/releases/download/v46.0.0-beta.1/GoogleMapsReviewsTracker_v46_Setup.exe)

اختر الملف الموافق لمنصتك من الروابط الرسمية. راجع تعليمات الإصدار، واحتفظ بنسخة من بياناتك قبل التحديث. قارن SHA-256 عند نشره؛ لا تعطّل حماية النظام لمعالجة تحذيرات التوقيع. لا توجد أوامر بناء أو تثبيت dependencies عامة تنطبق على جميع البرامج.

## المصدر ومتطلبات البناء

[README وLICENSE في المستودع الرسمي](https://github.com/Abdealmalk007/GoogleMapsReviewsTracker)

هذا دليل للمنتج، وليس إثباتًا لبناء مصدر البرنامج أو اجتياز اختباراته. اتبع تعليمات المستودع الخاصة بإصداره؛ لم يُفحص بناء هذا البرنامج ضمن تحسين الموقع.

## MCP وChatGPT

لم يتم التحقق من وجود خادم MCP أو تكامل ChatGPT لهذا البرنامج. لا توجد أوامر `start:mcp` أو أسماء tools موثّقة هنا. أدوات MCP المستخدمة لصيانة الموقع ليست ميزة مضمّنة في البرنامج.

## الصور والعرض

[صفحة التفاصيل العربية](https://alghad.digital/programs/google-maps-reviews-tracker/) · [English details](https://alghad.digital/en/programs/google-maps-reviews-tracker/)

الصور الموجودة على الموقع رسوم توضيحية؛ ليست لقطات شاشة فعلية معتمدة للتطبيق.

## الترخيص وحقوق الملكية

© 2026 ProTech · Alghad Digital. All Rights Reserved للمحتوى والأعمال الخاصة، مع احترام التراخيص المنشورة سابقًا وحقوق المكونات الخارجية.

All Rights Reserved للمصدر الحالي المملوك لـ ProTech؛ راجع LICENSE وإشعارات التبعيات. الإصدارات السابقة المنشورة تحت MIT تحتفظ بشروطها الأصلية. يلزم إذن كتابي للاستخدام أو النسخ أو التعديل أو التوزيع بموجب الترخيص الحالي.

## التواصل والدعم

[protech.2025.2026@gmail.com](mailto:protech.2025.2026@gmail.com) · [alghad.digital](https://alghad.digital/)


## v44 Search UI and responsiveness

- إصلاح الأزرار الداكنة وإظهار جميع النصوص بوضوح
- حقول بحث عربية واضحة دون تداخل النص الإرشادي
- تسريع الفرز وفلترة النتائج المكتملة عبر Cached analysis

QA verified readable controls and Arabic input across three desktop viewports.


## v45 Desktop UI and Portable release

- New icon, dashboard feature cards, clean results and right-to-left responsive layout
- Windows Setup: https://github.com/Abdealmalk007/GoogleMapsReviewsTracker/releases/download/v46.0.0-beta.1/GoogleMapsReviewsTracker_v46_Setup.exe
- Windows Portable (unzip first): https://github.com/Abdealmalk007/GoogleMapsReviewsTracker/releases/download/v46.0.0-beta.1/GoogleMapsReviewsTracker_v46_Portable_Windows_x64.zip
- The portable app writes to its own Data/ directory; this is not a copy of installed user data
- Unsigned Beta release. Google Business Profile OAuth requires authorized account access

- أيقونة جديدة وواجهة بطاقات احترافية Responsive
- نتائج بحث مختصرة ودقيقة مع إظهار بيانات المصدر
- نسخة Windows Portable بدون تثبيت وبيانات محلية مستقلة
- تنزيل Setup وPortable من صفحة البرنامج

## v46 Reviews and comments interface

- عرض جميع التعليقات المحفوظة وبطاقات حديثة
- فلترة حسب الفرع والتقييم والمشاعر والردود والفترة والنص
- التبديل بين البطاقات والجدول وتصدير CSV
- الفرز بتوقيت الاستيراد الحقيقي وحماية القيم المجهولة

- Windows Setup: https://github.com/Abdealmalk007/GoogleMapsReviewsTracker/releases/download/v46.0.0-beta.1/GoogleMapsReviewsTracker_v46_Setup.exe
- Windows Portable: https://github.com/Abdealmalk007/GoogleMapsReviewsTracker/releases/download/v46.0.0-beta.1/GoogleMapsReviewsTracker_v46_Portable_Windows_x64.zip

Live Google account sync requires authorized OAuth. Beta unsigned.
