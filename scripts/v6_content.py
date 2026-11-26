"""Original bilingual workflow tutorials; no unsupported feature or version claims."""
from html import escape
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
T={
"smart-excel":(
("تحليل جدول مبيعات دون تغيير الملف الأصلي",["أنشئ نسخة عمل من الملف. استخدم صف عناوين واحدًا بأسماء واضحة مثل التاريخ والفرع والمبلغ، واحتفظ بالبيانات الأصلية.","وحّد تنسيق التاريخ والأرقام، وراجع الصفوف الفارغة والإجماليات المكررة قبل التحليل. لا تستبدل القيمة المفقودة بصفر دون مبرر.","جرّب تجميع المبالغ حسب الفرع، ثم طابق مجموع النتائج مع مجموع العمود الأصلي. افحص عينة من السجلات قبل مشاركة التقرير."]),
("Analyze a sales workbook without changing the original",["Create a working copy. Use a single header row with clear names such as Date, Branch and Amount; keep the source untouched.","Normalize dates and numeric formats. Review blank rows and repeated subtotals; do not silently turn missing values into zeros.","Group amounts by branch, then reconcile the resulting total against the original column. Spot-check records before sharing the report."])),
"reports":(
("إعداد تقرير عمل يومي يمكن مراجعته",["ابدأ بتاريخ محدد واستخدم أسماء موحدة للأقسام والأنشطة. لا تخلط أعمال يومين في تقرير واحد.","سجّل ما أُنجز والكمية ووحدة القياس وأي عائق مؤثر. افصل المهام المكتملة عن الأعمال المعلقة.","راجع التقرير قبل التصدير، وقارن عينات من السجلات مع مصدرها. احفظ نسخة من البيانات والتقرير المعتمد."]),
("Prepare a daily work report that can be audited",["Start with one reporting date and consistent names for teams and activities. Do not mix two days in one report.","Record completed work, quantities, units and relevant blockers. Separate finished tasks from open work.","Review the report before exporting, reconcile a sample against the source, and retain the approved report and backup."])),
"hr":(
("تجهيز بيانات الموظفين ومراجعة الرواتب",["ابدأ ببيانات تجريبية، وحدد معرفًا فريدًا لكل موظف لتجنب تشابه الأسماء. لا تستخدم بيانات هوية حقيقية في التجربة.","راجع أيام الحضور والإجازات والساعات غير المكتملة، وتأكد من الفترة وقواعد احتساب الأجر المعتمدة في منشأتك.","طابق نتائج العينة يدويًا قبل الاعتماد، ثم احفظ نسخة احتياطية محمية وحدد من يملك صلاحية الوصول إلى بيانات الموظفين."]),
("Prepare employee records and review payroll",["Begin with sample records and a unique employee ID; do not use real identity data for testing.","Reconcile attendance, leave and incomplete time records with the correct payroll period and your organization's approved rules.","Manually verify a sample before approving results, retain a protected backup, and restrict access to employee data."])),
"download":(
("تنظيم ملفات الوسائط واختيار الجودة",["نزّل فقط الملفات التي تملك حق حفظها، واختر إصدار APK من صفحة الإصدار الرسمية. راجع الأذونات قبل التثبيت.","اختر الدقة والصيغة المناسبة لاستخدامك، وتحقق من المساحة المتاحة؛ زيادة الدقة لا تعني دائمًا تحسين جودة المصدر.","بعد الحفظ تأكد من تشغيل الملف، ثم نظّم الفيديو والصوت في مجلدات واضحة. لا تشارك رابطًا خاصًا أو بيانات تسجيل دخول."]),
("Organize media and choose a suitable quality",["Save only files you are authorized to download. Obtain the APK from the official release and review permissions before installation.","Select a format and resolution appropriate for your use and available storage. Higher resolution does not necessarily improve source quality.","Verify playback after saving and organize audio and video into clear folders. Never share private links or login credentials."]))
}
def tutorial(pid,en):
 if pid not in T:return ""
 title,items=T[pid][int(en)]; e=escape
 picture=""
 if pid=="download":
  src="/assets/screenshots/download-v6-tools-20261029.webp"
  assert (ROOT/src.lstrip("/")).is_file()
  caption="Actual Android V6 preview QA capture, 29 October 2026; current release may differ." if en else "لقطة فعلية من اختبار نسخة Android V6 التجريبية بتاريخ 29 أكتوبر 2026؛ قد تختلف الواجهة الحالية."
  picture=f'<figure class="v6-real-capture"><img src="{src}" width="720" height="1280" loading="lazy" decoding="async" alt="{e(caption)}"><figcaption>{e(caption)}</figcaption></figure>'
 return f'<!-- V6_TUTORIAL_BEGIN --><section class="v6-panel" data-v6-tutorial="{pid}"><span class="v6-kicker">PROTECH / PRACTICAL GUIDE</span><h2>{e(title)}</h2><ol class="v6-steps">{"".join("<li>"+e(x)+"</li>" for x in items)}</ol>{picture}</section><!-- V6_TUTORIAL_END -->'
