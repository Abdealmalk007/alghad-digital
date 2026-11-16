# إحصائيات زيارات alghad.digital

## الحالة
موقع GitHub Pages لا يعرض إحصائيات الزوار الفعلية من المستودع. لا يمكن استرجاع عدد زيارات سابق لم يُقَس. تكامل Google Analytics 4 جاهز لكنه لا يرسل بيانات قبل توفير Measurement ID الصالح وموافقة الزائر.

## خطوات التفعيل
1. افتح https://analytics.google.com/ وسجّل الدخول بحسابك.
2. أنشئ GA4 Property وحدّد Asia/Riyadh ثم Web data stream لموقع https://alghad.digital/.
3. من Admin > Data streams انسخ Measurement ID (يبدأ بـ G-).
4. في GitHub افتح Abdealmalk007/alghad-digital > Settings > Secrets and variables > Actions > Variables، وأنشئ المتغير GA4_MEASUREMENT_ID.
5. شغّل workflow update-tech-news.yml يدويًا بعد حفظ المتغير.
6. افتح موقعك على جهاز جديد ووافق على القياس ثم راجع Realtime في Google Analytics للتأكد من استقبال البيانات.

## التقارير
إجمالي الزوار، الجلسات، مشاهدات الصفحات، الزوار الجدد والمتكررون، وقت التفاعل، الدولة والمنطقة والمدينة التقريبية، نوع الجهاز، المتصفح، نظام التشغيل، اللغة، مصادر الزيارات والصفحات الأكثر مشاهدة. يمكن تفعيل Enhanced Measurement لقياس تنزيل الملفات والنقرات الصادرة.

## أمن وخصوصية
لا يبدأ تحميل Google tag إلا بعد موافقة الزائر ويمكنه تغييرها من تفضيلات الإحصائيات في تذييل الصفحة. يُعدَّل CSP فقط عند وجود Measurement ID صالح، ولا يُجمع المحتوى النصي للنماذج كأحداث مخصصة. Measurement ID ليس سرًا؛ لا تنشر Google API secret أو Service Account credentials في كود الواجهة. بيانات التحليلات لا يمكن عرضها آمنًا من GitHub Pages دون اتصال تحليلات مصادق عليه.
