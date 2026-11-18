"use strict";
/* Kitchen CAD Pro V5 CPU3D public Beta: verified GitHub release and bilingual links. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const read = file => fs.readFileSync(path.join(root, file), "utf8");
const tag = "v5.0.0-beta-ui-panels-20261118";
const repo = "https://github.com/Abdealmalk007/KitchenCADProV5";
const filename = "KitchenCADProV5_UI_PANELS_BETA_20261118_PORTABLE.zip";
const url = repo + "/releases/download/" + tag + "/" + filename;
const sha = "2a7fc416db1417c0dd42e4e0bb1cf7f0aeb1868bde75320be1e9067b31183791";
const context = {window: {}};
vm.runInNewContext(read("assets/products.js"), context, {timeout: 1500});
vm.runInNewContext(read("assets/downloads.js"), context, {timeout: 1500});

const products = context.window.AL_GHAD_PRODUCTS;
const config = context.window.AL_GHAD_DOWNLOADS.kitchen;
assert.equal(products.length, 9);
assert.equal(products.filter(p => p.status === "public").length, 9);
const product = products.find(p => p.id === "kitchen");
assert.ok(product);
assert.equal(product.github, repo);
assert.equal(product.status, "public");
assert.equal(product.release, repo + "/releases/tag/" + tag);
assert.equal(product.qaPublication, "KCAD_UI_PANELS_BETA_20261118");
assert.equal(product.version, "V5 UI Panels Beta");
assert.match(product.displayStatus, /Beta/);
assert.equal(config.repository, "KitchenCADProV5");
assert.equal(config.channel, "preview");
assert.equal(config.release, product.release);
assert.ok(config.checksum.endsWith("/SHA256SUMS_UI_PANELS_20261118.txt"));
assert.equal(config.files.length, 1);
assert.equal(config.files[0].recommended, true);
assert.equal(config.files[0].bytes, 94593206);
assert.equal(config.files[0].url, url);
assert.match(config.note, /CNC/);

const pages = [
  "index.html",
  "programs/index.html",
  "protech/index.html",
  "programs/kitchen/index.html",
  "en/index.html",
  "en/programs/index.html",
  "en/protech/index.html",
  "en/programs/kitchen/index.html"
];
for (const p of pages) {
  const html = read(p);
  assert.ok(html.includes(url), "Missing exact release download in " + p);
  assert.ok(!html.includes("javascript:" + url), "Unsafe URL in " + p);
}
for (const p of ["programs/kitchen/index.html", "en/programs/kitchen/index.html"]) {
  const html = read(p);
  assert.ok(html.includes("id=\"kcad-beta-download\""));
  assert.ok(html.includes(sha), "Missing SHA-256 in " + p);
  assert.ok(html.includes("overflow-wrap:anywhere"), "Long checksum could overflow on mobile: " + p);
  assert.ok(html.includes("Launch_KitchenCAD_UI_PANELS_QA.cmd"));
  assert.match(html, /CNC/);
  assert.match(html, /F9/);
  assert.ok(html.includes("لوحات") || html.includes("Panels"));
  assert.ok(html.includes('rel="noopener noreferrer"'));
}
assert.equal((read("index.html").match(/data-prerender-product=/g) || []).length, 9);
assert.ok(read("assets/downloads-ui.js").includes("validLink("));
console.log(JSON.stringify({
  state: "KCAD_UI_PANELS_BETA_SITE_RELEASE_QA_PASS",
  pages: pages.length,
  download: url,
  candidateBytes: config.files[0].bytes,
  checksum: sha,
  publishedStatus: "Beta / Preview"
}));
