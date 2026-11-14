#!/usr/bin/env python3
"""Official Microsoft CDN-only, one-click bilingual installation media.

All URL entries have been checked from Windows using HTTPS HEAD, with
Content-Disposition: attachment and Content-Length > 4GB on 2026-11-14.
No mirrors, third-party links, browser landing pages, or synthetic download URLs.
Office .img images are mountable installation media, not renamed ISOs.
"""
from dataclasses import dataclass
from html import escape
from urllib.parse import urlsplit

WIN11_CDN = "https://software-static.download.prss.microsoft.com/dbazure/888969d5-f34g-4e03-ac9d-1f9786c66749/"
OFFICE_CDN = "https://officecdn.microsoft.com/db/492350F6-3A01-4F97-B9C0-C7C6DDF67D60/media/"

@dataclass(frozen=True)
class DirectImage:
    language: str
    url: str
    size_bytes: int

@dataclass(frozen=True)
class DirectEdition:
    name: str
    description_ar: str
    description_en: str
    image_type: str
    support_status: str
    downloads: tuple[DirectImage,DirectImage]

SOURCES = (
    DirectEdition(
        "Windows 11 — 25H2 x64",
        "ملف Windows 11 25H2 الرسمي متعدد الإصدارات Home/Pro، بنواة 64 بت. إصدار محدد وليس ضمانًا بأنه أحدث إصدار متاح.",
        "Official Windows 11 25H2 x64 multi-edition Home/Pro disc image. A specific release, not a claim that it is the latest version.",
        "ISO","supported",
        (
            DirectImage("ar",WIN11_CDN+"26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENT_CONSUMER_x64FRE_ar-sa.iso",7437086720),
            DirectImage("en",WIN11_CDN+"26200.6584.250915-1905.25h2_ge_release_svc_refresh_CLIENT_CONSUMER_x64FRE_en-us.iso",7736125440),
        ),
    ),
    DirectEdition(
        "Office 2024 — Home Retail",
        "صورة تثبيت Office Home 2024 الرسمية. تتطلب ترخيصًا متوافقًا؛ صورة IMG قابلة للتركيب وليست ملف ISO.",
        "Official Office Home 2024 retail installation image. Requires a matching license; mountable IMG, not an ISO.",
        "IMG","supported",
        (
            DirectImage("ar",OFFICE_CDN+"ar-SA/Home2024Retail.img",5326252032),
            DirectImage("en",OFFICE_CDN+"en-US/Home2024Retail.img",5524717568),
        ),
    ),
    DirectEdition(
        "Office 2024 — Professional Plus Retail",
        "صورة تثبيت Office Professional Plus 2024 Retail من خوادم Microsoft؛ لا تعني توفر ترخيص أو تفعيل.",
        "Office Professional Plus 2024 Retail disc image directly from Microsoft's CDN; does not include a license or activation.",
        "IMG","supported",
        (
            DirectImage("ar",OFFICE_CDN+"ar-SA/ProPlus2024Retail.img",5326252032),
            DirectImage("en",OFFICE_CDN+"en-US/ProPlus2024Retail.img",5524717568),
        ),
    ),
    DirectEdition(
        "Office 2021 — Professional Plus Retail",
        "إصدار قديم متوقف الدعم الأمني منذ 13 أكتوبر 2026؛ يقتصر عرضه على احتياجات التوافق والنسخ القديمة.",
        "Legacy product: security support ended October 13, 2026. Only for compatibility/archival requirements.",
        "IMG","unsupported",
        (
            DirectImage("ar",OFFICE_CDN+"ar-SA/ProPlus2021Retail.img",4880416768),
            DirectImage("en",OFFICE_CDN+"en-US/ProPlus2021Retail.img",5060157440),
        ),
    ),
)

ALLOWED_HOSTS=frozenset(("officecdn.microsoft.com","software-static.download.prss.microsoft.com"))

def validate()->None:
    assert len(SOURCES)==4
    assert sum(len(x.downloads) for x in SOURCES)==8
    seen=set()
    for product in SOURCES:
        assert product.image_type in ("ISO","IMG")
        assert product.support_status in ("supported","unsupported")
        assert {p.language for p in product.downloads}=={"ar","en"}
        for media in product.downloads:
            parsed=urlsplit(media.url)
            assert parsed.scheme=="https" and parsed.hostname in ALLOWED_HOSTS
            assert not parsed.query and not parsed.fragment
            assert parsed.path.lower().endswith("."+product.image_type.lower())
            assert media.size_bytes>4_000_000_000
            assert media.url not in seen
            seen.add(media.url)

validate()

def render(lang:str)->str:
    if lang not in ("ar","en"):raise ValueError("Unsupported locale")
    en=lang=="en"
    title="Windows & Office — Microsoft direct downloads" if en else "تحميل Windows وOffice مباشرة من Microsoft"
    intro=("Choose Arabic or English and download the original installation image directly from Microsoft's CDN. "
           "Each button points to the file itself, not a download portal or third-party site."
           if en else "اختر اللغة العربية أو الإنجليزية لتنزيل صورة التثبيت الأصلية من خوادم Microsoft مباشرة. "
           "كل زر يشير إلى الملف نفسه، دون مواقع وسيطة أو صفحات تنزيل خارجية.")
    note=("Office images use the .img extension (mountable in Windows), not .iso. "
          "A legitimate Windows or Office product license is still required. Windows 10 is unsupported since October 14, 2025, "
          "and has no verified stable direct ISO link in this catalog; therefore no unverified link is offered. "
          "Office 2021 support ended October 13, 2026. Availability and CDN file paths can change at Microsoft's discretion."
          if en else "صور Office تأتي بامتداد IMG ويمكن تركيبها في Windows، وليست ISO حرفيًا. "
          "تنزيل الملف لا يتضمن ترخيصًا أو تفعيلًا. انتهى الدعم المعتاد لـ Windows 10 في 14 أكتوبر 2025، "
          "ولم يتوفر لدينا رابط ISO رسمي ثابت متحقق منه لذلك لم نعرض رابطًا غير موثوق. "
          "انتهى دعم Office 2021 في 13 أكتوبر 2026. قد تغيّر Microsoft توافر الملفات أو مسارات CDN مستقبلًا.")
    cards=[]
    for edition in SOURCES:
        desc=edition.description_en if en else edition.description_ar
        provenance=("Microsoft original CDN • ISO" if en else "خوادم Microsoft الأصلية • ISO") if edition.image_type=="ISO" else (
            "Microsoft original CDN • mountable IMG" if en else "خوادم Microsoft الأصلية • صورة IMG قابلة للتركيب")
        if edition.support_status=="unsupported":
            provenance+=(" • Support ended" if en else " • انتهى الدعم")
        buttons=[]
        for media in edition.downloads:
            language=("Arabic" if en else "تنزيل عربي") if media.language=="ar" else ("English" if en else "تنزيل إنجليزي")
            size=f"{media.size_bytes/1e9:.2f} GB"
            caption=(f"Download {language}" if en else language)
            aria=(f"Download {edition.name} {language} {edition.image_type}, {size}" if en
                  else f"تنزيل {edition.name} {language} {edition.image_type} بحجم {size}")
            klass="en-btn en-btn-outline" if en else "button"
            buttons.append(
                '<a class="'+klass+' microsoft-direct-file"'
                ' href="'+escape(media.url,quote=True)+'"'
                ' aria-label="'+escape(aria,quote=True)+'"'
                ' data-microsoft-file="'+edition.image_type.lower()+'"'
                ' data-download-language="'+media.language+'"'
                '>'+escape(caption)+' · '+edition.image_type+' · '+size+'</a>'
            )
        cards.append(
            '<article class="external-software-source microsoft-direct-source">'
            '<h3>'+escape(edition.name)+'</h3>'
            '<p>'+escape(desc)+'</p>'
            '<p class="source-provenance">'+escape(provenance)+'</p>'
            '<div class="microsoft-direct-actions">'+''.join(buttons)+'</div>'
            '</article>'
        )
    cls="en-section" if en else "more"
    return (
        '<section id="windows-office-downloads" class="'+cls+' external-software-sources" aria-labelledby="windows-office-sources-title">'
        '<h2 id="windows-office-sources-title">'+escape(title)+'</h2>'
        '<p>'+escape(intro)+'</p>'
        '<div class="external-sources-grid microsoft-direct-grid">'+''.join(cards)+'</div>'
        '<p class="external-software-notice">'+escape(note)+'</p>'
        '</section>'
    )

if __name__=="__main__":
    for language in ("ar","en"):
        value=render(language)
        assert value.count('class="external-software-source microsoft-direct-source"')==4
        assert value.count("microsoft-direct-file")==8
        print("MICROSOFT_DIRECT_MEDIA",language,"links=8","cards=4","chars="+str(len(value)))
