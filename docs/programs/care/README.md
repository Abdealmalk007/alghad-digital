# ProTech Windows Care

ProTech Windows Care 3.3.1 لصيانة Windows 11 بواجهة محسنة متجاوبة، وتصحيح الأزرار المخفية والنص العربي؛ نسخة Portable وSetup تجريبيتان وغير موقعتين.

إصدار 3.3.1 Responsive Portable Preview يحسن الأزرار والقائمة الجانبية العربية وGDI+ والأداء المرئي بأحجام مختلفة. يتوفر Portable مباشر دون تثبيت، ونسخة Setup منفصلة تفتح واجهة التثبيت الاختياري باستخدام --setup-ui؛ لم تُختبر عملية التثبيت الفعلية داخل VM. اجتاز 14 مجموعة اختبار و40 فحص واجهة على Windows 11 Pro x64؛ تبقى عمليات WinGet/AppX المؤثرة واستعادة بيانات البرامج غير معتمدة على VM، وWindows 10 وARM64 غير متحقق منهما. الملفان غير موقعين وقد يظهر SmartScreen، لذا استخدم نسخة احتياطية واختبر قبل التطبيق على أجهزة العمل.

## المزايا الرئيسية

- Portable: تشغيل مباشر من EXE دون تثبيت، مع Setup اختياري منفصل
- واجهة متجاوبة وأزرار مرتبة وأيقونات GDI+ ونص عربي سليم
- تحديد الكل والاختيار المتعدد والمعاينة قبل التنفيذ
- تشغيل WinGet وAppX عبر PowerShell مع موافقات وأذونات UAC
- نسخة احتياطية واشتراط نقطة استعادة Windows جديدة ومتحقق منها
- تقارير ونتائج مفصلة وواجهة عربية/إنجليزية

## الإصدار والمنصات

- الإصدار المعلن: 3.3.1.
- المنصات المعلنة: Windows.
- حالة الإتاحة: Beta / Preview — إصدار تجريبي.
- الحد الأدنى لإصدار النظام والذاكرة: غير متحقق؛ راجع ملاحظات الإصدار.

## التثبيت والتشغيل

- [Portable EXE مباشر — دون تثبيت (v3.3.1)](https://github.com/Abdealmalk007/ProTechWindowsCare/releases/download/v3.3.1-responsive-portable-preview/ProTech_Windows_Care_Setup.exe)
- [Setup EXE — واجهة التثبيت الاختياري (v3.3.1)](https://github.com/Abdealmalk007/ProTechWindowsCare/releases/download/v3.3.1-responsive-portable-preview/ProTech_Windows_Care_Installer_v3.3.1.exe)
- [Portable ZIP — البرنامج والشرح (v3.3.1)](https://github.com/Abdealmalk007/ProTechWindowsCare/releases/download/v3.3.1-responsive-portable-preview/ProTech_Windows_Care_Portable.zip)

اختر الملف الموافق لمنصتك من الروابط الرسمية. راجع تعليمات الإصدار، واحتفظ بنسخة من بياناتك قبل التحديث. قارن SHA-256 عند نشره؛ لا تعطّل حماية النظام لمعالجة تحذيرات التوقيع. لا توجد أوامر بناء أو تثبيت dependencies عامة تنطبق على جميع البرامج.

## المصدر ومتطلبات البناء

[README وLICENSE في المستودع الرسمي](https://github.com/Abdealmalk007/ProTechWindowsCare)

هذا دليل للمنتج، وليس إثباتًا لبناء مصدر البرنامج أو اجتياز اختباراته. اتبع تعليمات المستودع الخاصة بإصداره؛ لم يُفحص بناء هذا البرنامج ضمن تحسين الموقع.

## MCP وChatGPT

لم يتم التحقق من وجود خادم MCP أو تكامل ChatGPT لهذا البرنامج. لا توجد أوامر `start:mcp` أو أسماء tools موثّقة هنا. أدوات MCP المستخدمة لصيانة الموقع ليست ميزة مضمّنة في البرنامج.

## الصور والعرض

[صفحة التفاصيل العربية](https://alghad.digital/programs/care/) · [English details](https://alghad.digital/en/programs/care/)

الصور الموجودة على الموقع رسوم توضيحية؛ ليست لقطات شاشة فعلية معتمدة للتطبيق.

## الترخيص وحقوق الملكية

© 2026 ProTech · Alghad Digital. All Rights Reserved للمحتوى والأعمال الخاصة، مع احترام التراخيص المنشورة سابقًا وحقوق المكونات الخارجية.

All Rights Reserved للمصدر الحالي المملوك لـ ProTech؛ راجع LICENSE وإشعارات التبعيات. الإصدارات السابقة المنشورة تحت MIT تحتفظ بشروطها الأصلية. يلزم إذن كتابي للاستخدام أو النسخ أو التعديل أو التوزيع بموجب الترخيص الحالي.

## التواصل والدعم

[protech.2025.2026@gmail.com](mailto:protech.2025.2026@gmail.com) · [alghad.digital](https://alghad.digital/)
