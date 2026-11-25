"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const read = file => fs.readFileSync(path.join(root, file), "utf8");
const routes = [...read("sitemap.xml").matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g)].map(m => m[1]);
assert.equal(routes.length,50);
let active = 0;
for (const route of routes) {
  const html = read(route.replace(/^\//, "") + "index.html");
  const scripts = [...html.matchAll(/<script id="protech-analytics"[^>]*data-ga4-id="(G-[A-Z0-9]+)"[^>]*><\/script>/g)];
  const csp = html.match(/http-equiv="Content-Security-Policy" content="([^"]+)"/)?.[1];
  assert.ok(csp, route);
  assert.ok(scripts.length <= 1, route);
  if (scripts.length === 1) {
    active++;
    assert.ok(html.includes("/assets/analytics-consent.css?v=2"), route);
    assert.equal((html.match(/\/assets\/analytics-consent\.css\?v=\d+/g) || []).length, 1, route);
    assert.ok(html.includes("/assets/analytics-consent.js?v=3"), route);
    assert.ok(csp.includes("https://www.googletagmanager.com"), route);
    assert.ok(csp.includes("https://*.google-analytics.com"), route);
    assert.ok(!csp.includes("connect-src 'none'"), route);
    assert.ok(/^G-[A-Z0-9]{6,16}$/.test(scripts[0][1]), route);
  } else {
    assert.ok(csp.includes("connect-src 'self'"), route);
    assert.ok(csp.includes("https://www.googletagmanager.com"), route);
    assert.ok(csp.includes("https://*.google-analytics.com"), route);
    assert.ok(!html.includes("PROTECH_ANALYTICS_BEGIN"), route);
  }
}
assert.ok(active === 0 || active === routes.length);
if (active) {
  assert.ok(read("privacy/index.html").includes("PROTECH_ANALYTICS_PRIVACY_BEGIN"));
  assert.ok(read("en/privacy/index.html").includes("PROTECH_ANALYTICS_PRIVACY_BEGIN"));
}
const js = read("assets/analytics-consent.js");
assert.ok(js.includes("function activate()"));
assert.ok(js.includes("function showPreferences()"));
assert.ok(!js.includes("eval("));
assert.ok(!js.includes("innerHTML"));
assert.ok(read(".github/workflows/update-tech-news.yml").includes("python scripts/build_analytics.py"));
console.log("ANALYTICS_CONSENT_TEST_PASS", { pages: routes.length, active });
