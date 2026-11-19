"use strict";
/* Guard the intended program listing order on Alghad Digital. Node.js >= 22. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const root = path.resolve(__dirname, "..");
const context = { window: {} };
vm.runInNewContext(
  fs.readFileSync(path.join(root, "assets/products.js"), "utf8"),
  context, { filename: "assets/products.js", timeout: 1500 }
);
const products = context.window.AL_GHAD_PRODUCTS;
assert.ok(Array.isArray(products) && products.length === 10, "Preserve all ten program entries");

const ids = Array.from(products, (product) => product.id);
assert.equal(new Set(ids).size, products.length, "Do not duplicate product listings");
assert.deepEqual(ids, [
  "smart-excel", "stone", "marble", "reports", "hr",
  "kitchen", "download", "care", "quotes",
  "google-maps-reviews-tracker",
], "Google Maps must appear last while preserving all other program positions");

const maps = products.at(-1);
assert.equal(maps.title, "Google Maps Reviews Tracker");
assert.equal(maps.status, "public");
assert.equal(maps.github, "https://github.com/Abdealmalk007/GoogleMapsReviewsTracker");

const homepage = fs.readFileSync(path.join(root, "index.html"), "utf8");
assert.ok(homepage.includes('assets/products.js?v=3.4.1'),
  "Refresh catalog script URL to avoid stale cached ordering");
const app = fs.readFileSync(path.join(root, "assets/app.js"), "utf8");
assert.ok(app.includes("data.filter(p=>matches(p,term))"),
  "Main program list must follow products.js order without re-sorting");

console.log("GOOGLE_MAPS_LAST_PASS", JSON.stringify({
  total: products.length, last: ids.at(-1), previous: ids.at(-2)
}));
