# GA4 activation handoff — Alghad Digital

Status checked: 2026-11-18 (Asia/Riyadh).

## Confirmed
- OpenSEO project `d5521ec0-b6ec-414e-a08e-3611f918f611` has GA4 property `properties/564845731` selected.
- GA4 Admin API reports `dataStreamCount=0`, `webStreamCount=0`, issue `no_web_stream`.
- The website's CSP already allows the required Google domains on published Arabic and English pages.
- `scripts/build_analytics.py` installs a consent-gated GA4 script on all 42 sitemap pages **only when** `GA4_MEASUREMENT_ID` is set.
- `.github/workflows/update-tech-news.yml` reads repository variable `GA4_MEASUREMENT_ID` for every regeneration.
- 2026-11-18 isolated full build: all 11 site generators passed using `G-TEST123456` solely as a local test ID. `tests/analytics-consent-test.cjs` passed with 42 active pages; `scripts/test_seo.py` passed with 42 indexable pages. No synthetic ID was published.

## External prerequisite
1. In Google Analytics, open Admin → Data streams → Add stream → Web for existing property `564845731`.
2. Website URL: `https://alghad.digital`; stream name: `Alghad Digital Website`. Enable enhanced measurement.
3. Copy the real `Measurement ID`, which starts with `G-` (do not use the GA4 property number).
4. Set the GitHub Actions repository variable `GA4_MEASUREMENT_ID` to the exact measurement ID.
5. Run the existing `update-tech-news.yml` workflow manually, or allow its next successful scheduled run.
6. Verify both `https://alghad.digital/` and `https://alghad.digital/en/` include `data-ga4-id` with the real value; verify CSP, consent UI and GA4 Realtime after visitor opt-in.

## Operator notes
- Do not fake a measurement ID or report visit tracking as active until the Google Admin data stream exists, the real tag is published, and a consenting visit is observed.
- GitHub workflow now issues an explicit warning when `GA4_MEASUREMENT_ID` is unset.
- Preserve opt-in consent, privacy disclosure and the existing CSP; avoid broad `unsafe-inline` exceptions.

## Follow-up: consent safety and SEO QA (2026-11-18)
- Fixed GA4 consent withdrawal when the visitor's browser blocks localStorage: an active analytics session now triggers cookie clearing and page reload even when the stored decision is inaccessible.
- Added `tests/analytics-consent-runtime-test.cjs` to exercise six scenarios including pre-consent request suppression, accept, decline, re-accept, revoke, and restricted storage. Included it in the daily GitHub Actions test suite.
- Re-ran `scripts/polish_search_snippets.py` to repair nine existing generated pages with stale search descriptions; `search-snippet-quality-test.cjs` now passes.
- Validated all 27 workflow Node test invocations, `scripts/test_seo.py`, `scripts/seo_inventory.py --check`, and GitHub Actions YAML: zero failures on this checkout.
- Web Data Stream is still missing in GA4 property `564845731` at last OpenSEO Admin API inspection; no synthetic measurement identifier was published.
