# ربط نطاق alghad.digital بموقع Alghad Digital v3.0.0

## الحالة المؤكدة — 2026-11-07
- تم رفع 31 ملفًا إلى المستودع العام Abdealmalk007/alghad-digital على الفرع main (commit 4636f09 في النشر الأول).
- تم تفعيل GitHub Pages، وإعداد النطاق المخصص alghad.digital.
- أثبت اختبار الوصول المباشر إلى GitHub Pages أن index.html وملفات assets/products.js وassets/v3.js تعمل بنجاح.
- النطاق نفسه لا يزال موجها إلى خوادم DNS التابعة لـ Hostinger: atlas.dns-parking.com وhyperion.dns-parking.com.
- سجل A الحالي كان 2.57.91.91، وصفحة الدومين العلنية صفحة Hostinger Parked Domain.
- لم يتم تغيير DNS أو المساس بخدمات البريد أو سجلات MX/TXT. تفعيل HTTPS الإجباري ينتظر اكتمال DNS والشهادة.

## الخطوة المطلوبة مرة واحدة في Hostinger

1. افتح https://hpanel.hostinger.com/profile/api وأنشئ Hostinger API token بصلاحيات نطاق alghad.digital.
2. لا ترسل الرمز في محادثة أو تحفظه في ملفات عامة.
3. على جهاز Windows شغّل PowerShell المحلي وانفذ:

    powershell.exe -NoProfile -File "E:\ProTech\AlghadDigitalSite_QA\Connect_Alghad_Domain.ps1"

4. الصق الرمز في مدخل كلمة السر المخفي داخل PowerShell (لن يظهر النص).
5. راجع تغييرات سجلات الموقع فقط، ثم اكتب YES للموافقة.

يقوم السكربت بما يلي:
- قراءة سجل DNS بالكامل ونسخه إلى ملف backup خاص ضمن E:\ProTech\AlghadDigitalSite_QA.
- التأكد من عدم وجود سجلات ويب متضاربة قد تجعل التعديل غير آمن.
- تحديث سجلات A وAAAA للجذر @ وسجل CNAME الخاص بـ www فقط.
- التحقق من السجلات عبر Hostinger API.
- عدم تعديل سجلات MX/TXT/SPF/DKIM/DMARC أو إعدادات البريد.

## إعدادات DNS المستهدفة

| Type | Host | Value |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| AAAA | @ | 2606:50c0:8000::153 |
| AAAA | @ | 2606:50c0:8001::153 |
| AAAA | @ | 2606:50c0:8002::153 |
| AAAA | @ | 2606:50c0:8003::153 |
| CNAME | www | Abdealmalk007.github.io. |

لا تغير Nameservers؛ أبقها لدى Hostinger. بعد تحديث DNS وانتشاره، افتح https://github.com/Abdealmalk007/alghad-digital/settings/pages وفعل Enforce HTTPS عندما تصبح الشهادة جاهزة.

## التحقق
- https://alghad.digital/
- https://www.alghad.digital/
- https://alghad.digital/?app=kitchen
- https://github.com/Abdealmalk007/alghad-digital

## المراجع الرسمية
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://developers.hostinger.com/ — DNS Zone API
- https://www.hostinger.com/support/10840865-what-is-hostinger-api/

ملاحظة: صفحة GitHub Pages متاحة بالفعل عبر GitHub، ولكن اسم النطاق لن يعرضها بشكل عام حتى يكتمل تحديث Hostinger DNS.
