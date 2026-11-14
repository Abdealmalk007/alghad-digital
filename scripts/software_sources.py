#!/usr/bin/env python3
"""Bilingual, source-labeled Windows/Office resource links for ProTech software catalog.
The website links to external providers; it never mirrors Microsoft binaries.
"""
from html import escape

SOURCES=(
 ("Windows 11","Windows 11",
  "تنزيل ISO وأداة إنشاء USB من Microsoft باللغة العربية.",
  "Official Microsoft download page for ISO and installation media.",
  "https://www.microsoft.com/ar-sa/software-download/windows11",
  "https://www.microsoft.com/en-us/software-download/windows11","official"),
 ("Windows 10","Windows 10",
  "النسخة الرسمية وأداة إنشاء وسائط التثبيت. تحقق من حالة دعم النظام.",
  "Official installation media; check the operating system support status.",
  "https://www.microsoft.com/ar-sa/software-download/windows10",
  "https://www.microsoft.com/en-us/software-download/windows10","official"),
 ("Windows 10 ISO","Windows 10 ISO",
  "صفحة Microsoft لاختيار لغة وإصدار ملف ISO عندما يكون متاحًا.",
  "Select the language and edition of an ISO when Microsoft offers it.",
  "https://www.microsoft.com/ar-sa/software-download/windows10ISO",
  "https://www.microsoft.com/en-us/software-download/windows10ISO","official"),
 ("Microsoft 365 / Office 2024","Microsoft 365 / Office 2024",
  "دليل عربي رسمي للتنزيل وإعادة التثبيت باستخدام حساب وترخيص صالحين.",
  "Official installation/reinstallation guidance using a licensed account.",
  "https://support.microsoft.com/ar-sa/office/lifecycle/officeinstall/download-install-or-reinstall-microsoft-365-or-office-2024-on-a-pc-or-mac",
  "https://support.microsoft.com/en-us/office/lifecycle/officeinstall/download-install-or-reinstall-microsoft-365-or-office-2024-on-a-pc-or-mac","official"),
 ("Office 2021 / 2019 / 2016","Office 2021 / 2019 / 2016",
  "تعليمات Microsoft العربية لتثبيت النسخ المرتبطة بحسابك؛ بعض الإصدارات انتهى دعمها.",
  "Microsoft's reinstall guide for licensed editions; some versions are unsupported.",
  "https://support.microsoft.com/ar-sa/office/lifecycle/officeinstall/download-and-install-or-reinstall-office-2021-office-2019-or-office-2016",
  "https://support.microsoft.com/en-us/office/lifecycle/officeinstall/download-and-install-or-reinstall-office-2021-office-2019-or-office-2016","official"),
 ("Windowstan — Windows archive","Windowstan — Windows archive",
  "أرشيف خارجي لأنظمة Windows القديمة والجديدة، غير تابع لـ Microsoft؛ لم نتحقق من سلامة كل ملف.",
  "External archive of Windows editions, not affiliated with Microsoft. Files not independently verified.",
  "https://windowstan.com/win/","https://windowstan.com/win/","third-party"),
 ("Windowstan — Office archive","Windowstan — Office archive",
  "قسم Office في الموقع المقترح؛ تحقق من المصدر والبصمة والترخيص قبل تنزيل الملفات.",
  "Office archive on the suggested website. Verify file integrity, origin and license.",
  "https://windowstan.com/microsoft-office/","https://windowstan.com/microsoft-office/","third-party"),
)
assert len(SOURCES)==7

def render(lang: str)->str:
    if lang not in {"ar","en"}:raise ValueError("Unsupported locale")
    en=lang=="en"
    title="Windows & Office download sources" if en else "مصادر تنزيل Windows وMicrosoft Office"
    intro=("Choose official Microsoft downloads first. For older editions, the external archive below is a third-party website, not a verified Microsoft distributor."
           if en else "ابدأ بمصادر Microsoft الرسمية باللغة العربية. وللنسخ القديمة يوجد أرشيف خارجي غير تابع لـ Microsoft؛ لا نضمن سلامة ملفاته أو توفر كل إصدار.")
    guide=("Downloading installation media does not include a product license. Avoid modified installers and activation bypass tools. Unsupported versions may carry security risks."
           if en else "تنزيل ملف التثبيت لا يمنح ترخيص استخدام. تجنب النسخ المعدلة وأدوات تجاوز التفعيل، وانتبه إلى أن الأنظمة والبرامج المنتهية الصلاحية الأمنية قد تكون غير آمنة.")
    official="Official Microsoft • Arabic available" if en else "Microsoft رسمي • شرح عربي"
    third="External third-party archive • unverified" if en else "أرشيف خارجي • ملفات غير متحقق منها"
    follow="Open provider site" if en else "فتح صفحة المصدر"
    cards=[]
    for ar_name,en_name,ar_description,en_description,ar_url,en_url,tier in SOURCES:
        name=en_name if en else ar_name
        desc=en_description if en else ar_description
        url=en_url if en else ar_url
        badge=official if tier=="official" else third
        rel='noopener noreferrer'+(' nofollow' if tier=="third-party" else '')
        if en:
            cards.append(
                '<article class="external-software-source">'
                '<h3>'+escape(name)+'</h3>'
                '<p>'+escape(desc)+'</p>'
                '<p class="source-provenance">'+escape(badge)+'</p>'
                '<a class="en-btn en-btn-outline" href="'+escape(url,quote=True)+'" target="_blank" rel="'+rel+'">'+escape(follow)+'</a></article>'
            )
        else:
            cards.append(
                '<article class="external-software-source">'
                '<h3>'+escape(name)+'</h3>'
                '<p>'+escape(desc)+'</p>'
                '<p class="source-provenance">'+escape(badge)+'</p>'
                '<a class="button" href="'+escape(url,quote=True)+'" target="_blank" rel="'+rel+'">'+escape(follow)+'</a></article>'
            )
    cls="en-section" if en else "more"
    grid="external-sources-grid"
    return (
        '<section id="windows-office-downloads" class="'+cls+' external-software-sources" aria-labelledby="windows-office-sources-title">'
        '<h2 id="windows-office-sources-title">'+escape(title)+'</h2>'
        '<p>'+escape(intro)+'</p>'
        '<div class="'+grid+'">' + ''.join(cards) + '</div>'
        '<p class="external-software-notice">'+escape(guide)+'</p>'
        '<p><a href="https://windowstan.com/" target="_blank" rel="noopener noreferrer nofollow">'+
        escape("Windowstan home (external archive)" if en else "زيارة موقع Windowstan الخارجي")+'</a></p>'
        '</section>'
    )

if __name__=="__main__":
    for lang in ("ar","en"):
        code=render(lang)
        assert code.count("external-software-source")>=7
        print(lang,len(code))
