# Alghad Digital — برامج ProTech

الموقع الرسمي لعرض برامج ProTech للأعمال والتصميم والإنتاجية. واجهة عربية RTL ونسخة English، مع صفحات تفاصيل مستقلة ومزايا وروابط تنزيل رسمية وحالة واضحة لكل إصدار.

**License: All Rights Reserved** — راجع [LICENSE](LICENSE). لا تمثل هذه العبارة إعادة ترخيص للمكتبات الخارجية أو النسخ المنشورة سابقًا تحت MIT.

## المحتويات

- [البرامج والتوثيق](#البرامج-والتوثيق)
- [التشغيل والبناء](#التشغيل-والبناء)
- [الاختبارات](#الاختبارات)
- [MCP](#mcp)
- [حقوق الملكية والدعم](#حقوق-الملكية-والدعم)

## المزايا

- 8 برامج، لكل منها زر «تفاصيل» وصفحة دائمة ووصف و5 مزايا ودليل README.
- البحث والتصفية والترتيب، ومشاركة روابط البرامج والأخبار.
- العربية والإنجليزية، والجوال، ولوحة المفاتيح، ووضع تقليل الحركة.
- عرض 5 إصدارات Preview متاحة و3 برامج قادمة، دون اختلاق تنزيلات.
- صفحات HTML ثابتة تعمل دون JavaScript؛ تحسينات تفاعلية عند توفره.
- صور توضيحية محلية، وروابط GitHub Releases وبصمات SHA-256 عند توفرها.

## البرامج والتوثيق

| البرنامج | الدليل | حالة الإتاحة |
|---|---|---|
| ProTech Stone Manager | [README](docs/programs/stone/README.md) | Preview |
| Marble Delivery Pro | [README](docs/programs/marble/README.md) | Preview |
| Daily Work Reports | [README](docs/programs/reports/README.md) | Preview |
| ProTech HR | [README](docs/programs/hr/README.md) | Preview |
| Download Anything PRO | [README](docs/programs/download/README.md) | Preview |
| Kitchen CAD Pro | [README](docs/programs/kitchen/README.md) | قادم |
| ProTech Windows Care | [README](docs/programs/care/README.md) | قادم |
| Quotes & Contracts | [README](docs/programs/quotes/README.md) | قادم |

## التشغيل والبناء

الإنتاج: استضافة Static مثل GitHub Pages؛ لا يحتاج Node أو Python على الخادم.
للتوليد المحلي: Python 3.12+ وNode.js 22+، دون npm dependencies للمهام التالية.

```powershell
python scripts/prerender_home.py
python scripts/build_seo.py
python scripts/build_support_pages.py
python scripts/build_en.py
python -m http.server 8765 --bind 127.0.0.1
```

افتح `http://127.0.0.1:8765/`. لا يحتاج الموقع ملف `.env` أو مفاتيح API.
لا تُحرر الصفحات المولدة وحدها؛ عدّل المولدات والبيانات ثم أعد البناء.

## الاختبارات

```powershell
node tests/smoke-test.cjs
node tests/two-actions-test.cjs
node tests/program-documentation-test.cjs
node tests/bilingual-test.cjs
python scripts/test_seo.py
```

بقية اختبارات البيانات في `tests/`. نجاح اختبارات الموقع لا يثبت قبول برامج Windows/Android أو توقيع ملفاتها. فحوص المتصفح القديمة قد تتضمن توقعات لتصميم سابق؛ تُراجع نتائجها منفصلة عن اختبارات البيانات.

## MCP

هذا الموقع Static ولا يضم خادم MCP أو أوامر `start:mcp`. استخدام Abu Omar MCP وSerena وOpen Code Review وCodeView لصيانته لا يجعل هذه الأدوات جزءًا من المنتج. يُوثق أي تكامل مستقبلي بعد تنفيذه والتحقق منه فقط.

## الملفات الأساسية

- `assets/products.js`: تعريف البرامج ومزاياها.
- `assets/downloads.js` و`assets/release-facts.json`: روابط الإصدارات وحقائق الملفات.
- `assets/app.js`: العرض التفاعلي ونافذة التفاصيل.
- `assets/refinement.css`: تنسيق البطاقات والأزرار والوثائق.
- `scripts/build_seo.py`: صفحات البرامج العربية وأدلتها.
- `scripts/build_en.py`: النسخة الإنجليزية.
- `.github/workflows/update-tech-news.yml`: تحديث الأخبار وإعادة توليد الصفحات.

## حقوق الملكية والدعم

© 2026 Abu Omar / ProTech · Alghad Digital. **All Rights Reserved**.
يلزم إذن كتابي للاستخدام أو النسخ أو التعديل أو التوزيع وفق LICENSE. تحتفظ المكونات الخارجية والنسخ التي سبق نشرها بتراخيصها الأصلية. لم تُستبدل ملفات EXE/APK أو مفاتيح التوقيع بهذا التحديث.

[البريد الرسمي](mailto:protech.2025.2026@gmail.com) · [الموقع](https://alghad.digital/)

[توثيق الإصدارات السابقة](docs/README-history.md) مرجع تاريخي؛ تُقدّم عليه هذه الصفحة عند التعارض.
