"use strict";
// Keep the nine revised icons distinct, accessible and linked from both languages.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const {createHash} = require("node:crypto");
const root = path.resolve(__dirname, "..");
const read = file => fs.readFileSync(path.join(root, file), "utf8");

const scope = {window: {}};
vm.runInNewContext(read("assets/products.js"), scope, {timeout: 1500});
const products = Array.from(scope.window.AL_GHAD_PRODUCTS);
const byId = new Map(products.map(p => [p.id, p]));
assert.equal(products.length,12);
const ids = [
  "smart-excel", "stone", "marble", "reports", "hr",
  "kitchen", "download", "care", "quotes"
];
const hashes = new Set();
for (const id of ids) {
  const product = byId.get(id);
  assert.ok(product, "Missing product " + id);
  const asset = "assets/previews/" + id + "-clear.svg";
  assert.equal(product.preview, asset, id + " has stale artwork");
  assert.ok(product.previewAlt.startsWith("أيقونة"), id + " needs accessible icon alt");
  const svg = read(asset);
  assert.ok(svg.length > 1000 && svg.length < 12000, asset);
  for (const token of ['xmlns="http://www.w3.org/2000/svg"', 'viewBox="0 0 960 540"', "<title>", "<desc>", "<linearGradient", "<g "]) {
    assert.ok(svg.includes(token), asset + " lacks " + token);
  }
  assert.doesNotMatch(svg, /<script\b|<foreignObject\b|\sonload\s*=/i, asset);
  hashes.add(createHash("sha256").update(svg).digest("hex"));
  for (const sitePage of [
    "index.html", "en/index.html", "en/programs/index.html",
    "en/protech/index.html", "programs/" + id + "/index.html",
    "en/programs/" + id + "/index.html"
  ]) {
    assert.ok(read(sitePage).includes(asset), sitePage + " does not use " + asset);
  }
}
assert.equal(hashes.size, ids.length, "Every program should have a unique icon");
assert.equal(byId.get("protech-music").preview, "assets/previews/protech-music.svg");
assert.equal(byId.get("google-maps-reviews-tracker").preview, "assets/previews/reviews-tracker-v45.png");
assert.ok(read("index.html").includes("assets/products.js?v=3.4.3"), "Old JS cache key");
console.log("PROGRAM_ICONS_PASS", JSON.stringify({redesigned:ids.length,products:products.length,bilingual:true,unique:hashes.size,cacheBusted:true}));
