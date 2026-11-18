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

## 2026-11-18 Consent Mode v2 live-browser QA
- First public-browser smoke test: Google tag script loaded (200) only after consent, but GA event was blocked by CSP when the tag attempted a DoubleClick endpoint; this exposed a gap not covered by static unit tests.
- Tested a corrected consent loader using browser response interception (without changing the public script): explicitly `analytics_storage=granted` after opt-in, while `ad_storage`, `ad_user_data`, and `ad_personalization` remain `denied`.
- The isolated browser test returned `HTTP 204` from `https://www.google-analytics.com/g/collect` and zero CSP errors. The existing restrictive CSP can remain intact.
- Bumped the consent JS asset URL to `/assets/analytics-consent.js?v=2` on all 42 pages to avoid stale browser caching.
- All 27 Node workflow tests, SEO tests, and inventory checks passed after the patch. Recheck the public site after deployment.

## Final public-site GA4 verification — 2026-11-18
- Verified the published home page includes the real `G-9EPCJ5J4QZ` measurement ID and loads consent script `/assets/analytics-consent.js?v=2`.
- Tested a fresh, temporary headless Chrome profile against the **published** `https://alghad.digital/` page.
- Before opt-in: **0** requests to Google Analytics or Google Tag Manager.
- After explicit opt-in: `gtag.js` loaded with `HTTP 200`, and an analytics collection request to `https://www.google-analytics.com/g/collect` returned `HTTP 204`.
- Browser CSP errors: **0**. Google Ads consent remains denied. One subsequent browser teardown beacon was marked `ERR_ABORTED` after the accepted collection response; this did not invalidate the confirmed `HTTP 204` event.
- **Conclusion:** GA4 live event transport and consent gating are verified. GA4 dashboard totals and realtime visualization are separate reporting checks and may have processing delay; the test generates one synthetic consented visit.

## Visitor-friendly cookie notice — 2026-11-18
- Replaced the lengthy, potentially alarming consent message with a short, plain-language cookie notice in Arabic and English.
- The notice says optional analytics cookies are used to understand visits and improve the website; visitors can choose **Accept** or **Continue without** equally easily. The Arabic choices are **موافق** and **المتابعة بدونها**.
- Redesigned the consent surface as a discreet, light-colored compact panel at the bottom-left, with a privacy policy link. Mobile spacing keeps it above bottom navigation; it does not block the page.
- The footer allows later changes to cookie settings. Existing saved choices continue to be respected; the localStorage key remains unchanged.
- No change to GA4 measurement ID or the rule that Google Analytics loads only after explicit consent. Advertising consent remains denied.
- New assets are cache-busted to `analytics-consent.css?v=2` and `analytics-consent.js?v=3`. The builder strips old stylesheet tags to avoid duplication across regenerations.
- Validated the consent runtime (six scenarios), all 42 pages, all 27 Node tests, SEO tests, and repeated static builds.
