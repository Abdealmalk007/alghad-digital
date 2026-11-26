# Signature Premium Experience V7 — implementation checkpoint

Source of truth: ALGHAD_DIGITAL_V7_MASTER_EXECUTION_PLAN_AR.md, approved by owner.
Baseline: 7de1fd473648b09983a654849e96f3c9ca3df676; backup/pre-v7-designer-20261126 is unchanged.
Architecture: static bilingual HTML, CSS, vanilla JS, Python generators, GitHub Pages.
Implementation: shared V7 tokens, licensed IBM Plex Sans Arabic WOFF2 (Fontsource 5.3.0; Arabic/Latin/Latin-ext, 400/500/600/700), preserved Dawn G, shared early theme bootstrap and persisted user choice, responsive header/navigation/search, concise hero, responsive featured grid, product and editorial styling, existing release/download data and consent-aware analytics, bounded public PWA service worker and offline fallback.
Security: existing CSP preserved except same-origin worker-src required for PWA; no external font scripts or new runtime dependencies. No secrets or personal data in PWA cache. The offline fallback intentionally does not present stale pages as live content.
Rebuild: scripts/build_v7.py runs after V6 and before search index generation in the existing daily workflow. Independent read-only V7 CI must not run the daily workflow on feature branches because the latter publishes generated main snapshots.
Rollback: revert only V7 commit(s) on main if deployed; preserve later unrelated news commits. Existing baseline bundle verified and remote backup ref matches.
Gate: RC until all required tests and production deployment are verified; no claim of full WCAG conformance, field INP, Safari/Firefox coverage, or final status without evidence.
