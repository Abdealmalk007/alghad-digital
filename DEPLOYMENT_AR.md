# دليل نشر Alghad Digital v3.0.0 على alghad.digital

## ما تم التحقق منه
- ملفات الموقع مبنية ومختبرة محليًا داخل E:\ProTech\AlghadDigitalSite_v3.0.0.
- وجود 5 مستودعات GitHub عامة للبرامج المذكورة في الكتالوج.
- ملف CNAME يحتوي alghad.digital.
- **المستودع Abdealmalk007/alghad-digital غير موجود في حساب GitHub حاليًا**، ولذلك لم يتم رفع الموقع إليه.
- **لم يُغيّر DNS للدومين ولم يُفعّل GitHub Pages أو HTTPS للدومين**.
- لم يمكن الجزم بالصفحة التي يقدمها الدومين حاليًا من أداة التحقق الخارجية.

## الخيار الموصى به: GitHub Pages
1. أنشئ مستودعًا عامًا فارغًا على https://github.com/new باسم alghad-digital، تحت الحساب Abdealmalk007.
2. داخل PowerShell انتقل إلى مجلد النسخة v3.0.0:
   
       cd E:\ProTech\AlghadDigitalSite_v3.0.0
       node .\tests\smoke-test.cjs
       .\Publish_To_GitHub.ps1

3. بعد نجاح الدفع، افتح https://github.com/Abdealmalk007/alghad-digital/settings/pages.
4. اختر **Build and deployment > Deploy from a branch > main > /(root)**.
5. في **Custom domain** أدخل alghad.digital واحفظه، وتأكد من التحقق من الملكية إن طلب GitHub ذلك.
6. قبل تغيير أي DNS، راجع سجلات A/CNAME الحالية واستضافة البريد الإلكترونية والتوجيهات الأخرى.
7. إذا قررت أن يوجّه النطاق إلى GitHub Pages، استخدم سجلات GitHub القياسية:

| Type | Host | Value |
| --- | --- | --- |
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | Abdealmalk007.github.io |

8. لا تحذف MX أو TXT أو SPF أو DKIM أو سجلات البريد. ولا تحذف A أخرى قبل التحقق من دورها الحالي.
9. بعد اكتمال ربط النطاق وإصدار الشهادة، فعّل **Enforce HTTPS**.
10. جرّب https://alghad.digital وhttps://www.alghad.digital و رابطًا مثل https://alghad.digital/?app=kitchen.

قد يتأخر انتشار DNS أو الشهادة. GitHub Pages يستضيف الملفات العامة فقط؛ لا ترفع مفاتيح التوقيع أو قواعد بيانات خاصة أو معلومات عملاء.

## البديل: Hostinger
إذا كانت لديك استضافة Web Hosting لنفس النطاق، ارفع **محتوى المجلد** إلى public_html بعد اختبار النسخة، بدون ملفات اختبارات أو توثيق غير مطلوب. في هذه الحالة لا تُغيّر DNS إلى عناوين GitHub Pages.

## مراجع رسمية
- https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site

حالة النشر الآن: ملفات جاهزة محليًا / مستودع الموقع غير منشأ / ربط الدومين معلق.
