# Google Analytics 4 — Activation Record

Date: 2026-11-18 (Asia/Riyadh)
Website: https://alghad.digital
OpenSEO project: `d5521ec0-b6ec-414e-a08e-3611f918f611`

## Activated in Google Analytics
- Existing GA4 Property: `properties/564845731`
- Created Web Data Stream: `16364323782`
- Stream name: `Alghad Digital Website`
- Measurement ID: `G-9EPCJ5J4QZ`
- Stream URL: `https://alghad.digital`
- GA4 Admin read-back: `dataStreamCount=1`, `webStreamCount=1`, `issues=[]`.
- Enhanced Measurement enabled: page views, scrolls, outbound clicks, site search, video interactions, file downloads, history page changes, and form interactions.
- OpenSEO: property already selected and linked.

## Site deployment
- GitHub repository `Abdealmalk007/alghad-digital`.
- GitHub Actions variable `GA4_MEASUREMENT_ID=G-9EPCJ5J4QZ` created and read back successfully; the scheduled news regeneration runs `scripts/build_analytics.py` using the repository variable.
- The GA4 consent loader is present on all **42** sitemap pages (21 Arabic, 21 English), and loads Google's `gtag.js` **only after visitor consent**.
- The existing CSP permits the required tag-manager and analytics endpoints without allowing unrestricted inline scripts.
- Privacy pages contain a bilingual analytics notice and visitors can revoke consent via footer preferences.
- Never use a synthetic ID on the public site.

## Tests before publish
- `node tests/analytics-consent-test.cjs`: 42 of 42 pages active.
- `node tests/analytics-consent-runtime-test.cjs`: six consent scenarios passed, including localStorage-blocked revocation and no network request before consent.
- `node tests/contact-security-test.cjs`: CSP and privacy checks passed.
- `python scripts/test_seo.py` and `python scripts/seo_inventory.py --check`: 42 of 42 pages passed.
- All 27 Node tests listed in `.github/workflows/update-tech-news.yml` passed.
- Deployment verification: review public HTML for exact GA4 ID on both home pages and a product page, verify script and stylesheet reachability, and confirm GA4 Realtime or DebugView receives a consenting visit. **GA4 collection cannot be declared verified until this final live check succeeds**.

## Maintenance
- The next successful scheduled news refresh should preserve GA4 Tag via the GitHub Actions variable.
- IndexNow verification key remains available from `/1d845c3408a44669a715acccafd2a160.txt`.
