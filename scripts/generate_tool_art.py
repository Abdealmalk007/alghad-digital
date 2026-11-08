#!/usr/bin/env python3
"""Build locally owned preview artwork and verified vendor-directory metadata."""
from pathlib import Path
import json
from html import escape
root=Path(__file__).resolve().parents[1]
rows=[
 {"id":"everything","name":"Everything","english":"EVERYTHING","category":"بحث وملفات","license":"مجاني","url":"https://www.voidtools.com/downloads/","description":"محرك بحث فوري عن الملفات والمجلدات في Windows، مع تصفية النتائج بسرعة وبواجهة خفيفة.","features":["فهرسة سريعة لأسماء الملفات","بحث متقدم وفلاتر","استهلاك منخفض للموارد"],"gradient":["#0f4b6e","#0b1229"],"accent":"#7fe5ff","shape":"search"},
 {"id":"ventoy","name":"Ventoy","english":"VENTOY","category":"USB وأنظمة","license":"مفتوح المصدر","url":"https://www.ventoy.net/en/download.html","description":"لإعداد USB متعدد الإقلاع: انسخ ملفات ISO وWIM إلى وحدة واحدة واستخدم قائمة الإقلاع.","features":["عدة أنظمة على USB واحد","إضافة ISO دون إعادة التهيئة كل مرة","دعم UEFI وLegacy"],"gradient":["#255b77","#171330"],"accent":"#84f5df","shape":"usb"},
 {"id":"rufus","name":"Rufus","english":"RUFUS","category":"USB وأنظمة","license":"مفتوح المصدر","url":"https://rufus.ie/ar/","description":"أداة صغيرة لإنشاء وسائط USB قابلة للإقلاع لتثبيت Windows أو Linux من صور ISO.","features":["إنشاء USB من ISO","خيارات GPT/MBR وUEFI","إصدار محمول متاح"],"gradient":["#20415c","#0b1933"],"accent":"#ffd28e","shape":"boot"},
 {"id":"irfanview","name":"IrfanView","english":"IRFANVIEW","category":"صور ووسائط","license":"مجاني للاستخدام غير التجاري","url":"https://www.irfanview.com/","description":"عارض صور سريع وخفيف مع تحرير أساسي وتحويل صيغ ومعالجة مجموعات من الصور.","features":["عرض سريع للصيغ الشائعة","Batch Rename وBatch Convert","مجاني للاستخدام الشخصي غير التجاري"],"gradient":["#574365","#1a1c34"],"accent":"#e0b0ff","shape":"image"},
 {"id":"fileconverter","name":"File Converter","english":"FILE CONVERTER","category":"صور ووسائط","license":"مفتوح المصدر GPL-3.0","url":"https://file-converter.io/","description":"تحويل وضغط الملفات من قائمة النقر بالزر الأيمن في File Explorer مع دعم عدة تنسيقات.","features":["تكامل مع قائمة Windows","تحويل صور وصوت وفيديو","إعدادات تحويل قابلة للتخصيص"],"gradient":["#164c53","#11283e"],"accent":"#93f1d7","shape":"convert"},
 {"id":"vlc","name":"VLC media player","english":"VLC MEDIA PLAYER","category":"صور ووسائط","license":"مفتوح المصدر","url":"https://www.videolan.org/vlc/","description":"مشغّل وسائط متعدد الصيغ للتسجيلات والصوت والفيديو، دون الحاجة إلى حزم ترميز إضافية غالبًا.","features":["تشغيل غالبية صيغ الوسائط","قوائم تشغيل وترجمة","متاح لعدة أنظمة"],"gradient":["#5b4627","#1c2336"],"accent":"#ffd17c","shape":"play"},
 {"id":"fdm","name":"Free Download Manager","english":"FREE DOWNLOAD MANAGER","category":"إنترنت وإنتاجية","license":"برنامج مجاني","url":"https://www.freedownloadmanager.org/","description":"مدير لتنزيل الملفات مع استكمال التحميل وتنظيم التنزيلات وإدارة سرعة الاتصال.","features":["استئناف عمليات التنزيل","تنظيم قوائم الملفات","إدارة وتحديد السرعة"],"gradient":["#13547a","#142544"],"accent":"#94d6ff","shape":"download"},
 {"id":"powertoys","name":"Microsoft PowerToys","english":"MICROSOFT POWERTOYS","category":"إنترنت وإنتاجية","license":"مفتوح المصدر","url":"https://github.com/microsoft/PowerToys","description":"مجموعة أدوات مجانية من Microsoft لرفع إنتاجية Windows مثل إدارة النوافذ وإعادة تسمية الملفات.","features":["FancyZones لتنظيم النوافذ","PowerRename لإعادة التسمية","PowerToys Run وKeyboard Manager"],"gradient":["#1b4c7f","#161b44"],"accent":"#9abaff","shape":"tiles"},
]
icons={
"search":'<circle cx="442" cy="231" r="100"/><path d="M516 309l93 94"/><path d="M407 231h70"/>',
"usb":'<rect x="380" y="130" width="160" height="248" rx="30"/><path d="M420 127v-52h80v52M430 75v26m40-26v26M421 210h78M438 290h45"/>',
"boot":'<rect x="353" y="110" width="220" height="288" rx="30"/><path d="M417 148h92M433 260h59M461 220v95"/><path d="M427 280l34 35 34-35"/>',
"image":'<rect x="329" y="138" width="272" height="228" rx="24"/><circle cx="518" cy="197" r="25"/><path d="M359 328l67-79 54 56 35-36 55 59"/><path d="M350 110h220"/>',
"convert":'<rect x="334" y="153" width="127" height="183" rx="15"/><rect x="510" y="153" width="127" height="183" rx="15"/><path d="M442 198h100l-31-30m31 30-31 31M531 294H431l30 30m-30-30 30-30"/>',
"play":'<circle cx="465" cy="263" r="125"/><path d="M437 207l103 56-103 56z" fill="none" stroke-width="13"/>',
"download":'<path d="M462 105v235m-73-76 73 76 73-76M343 362v28h235v-28"/><circle cx="463" cy="225" r="130" stroke-dasharray="22 30" opacity=".25"/>',
"tiles":'<rect x="330" y="143" width="122" height="112" rx="15"/><rect x="478" y="143" width="122" height="112" rx="15"/><rect x="330" y="277" width="122" height="112" rx="15"/><rect x="478" y="277" width="122" height="112" rx="15"/>'
}
out=root/"assets"/"tools"
out.mkdir(parents=True,exist_ok=True)
for item in rows:
 item["image"]="assets/tools/"+item["id"]+".svg"
 a,b=item["gradient"];color=item["accent"];icon=icons[item["shape"]]
 label=escape(item["english"])
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="رسمة توضيحية لبرنامج {label}">
 <defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient><radialGradient id="r"><stop stop-color="{color}" stop-opacity=".21"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>
 <rect width="960" height="540" fill="url(#g)"/><circle cx="760" cy="105" r="320" fill="url(#r)"/>
 <g stroke="{color}" opacity=".12" stroke-width="1"><path d="M0 108h960M0 216h960M0 324h960M0 432h960M160 0v540M320 0v540M480 0v540M640 0v540M800 0v540"/></g>
 <rect x="260" y="72" width="410" height="356" rx="50" fill="#071420" fill-opacity=".26" stroke="{color}" stroke-opacity=".28"/>
 <g fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
 <text x="56" y="474" fill="#f0fafc" font-family="Arial,sans-serif" font-size="26" font-weight="700" letter-spacing="4">{label}</text>
 <text x="906" y="475" fill="{color}" font-family="Arial,sans-serif" font-size="12" text-anchor="end" letter-spacing="2">WINDOWS UTILITIES</text>
 </svg>'''
 (out/(item["id"]+".svg")).write_text(svg,encoding="utf-8")
 del item["gradient"];del item["accent"];del item["shape"]
f=root/"assets"/"tools.json"
f.write_text(json.dumps({"version":1,"items":rows},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(root/"assets"/"tools-data.js").write_text("window.AL_GHAD_TOOLS = "+json.dumps({"version":1,"items":rows},ensure_ascii=True,separators=(",",":"))+";\n",encoding="utf-8")
print("TOOLS="+str(f)+" COUNT="+str(len(rows))+" SVG="+str(len(list(out.glob("*.svg")))))
