"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const root = path.resolve(__dirname, "..");
const read = file => fs.readFileSync(path.join(root, file), "utf8");
const context = {window:{}};
vm.runInNewContext(read("assets/products.js"), context, {timeout:1000});
for (const product of context.window.AL_GHAD_PRODUCTS) {
  const guide = read(`docs/programs/${product.id}/README.md`);
  assert.ok(guide.includes(product.title));
  assert.ok(guide.includes("All Rights Reserved"));
  assert.ok(guide.includes("لم يتم التحقق من وجود خادم MCP"));
  for (const feature of product.features) assert.ok(guide.includes(feature));
  for (const prefix of ["", "en/"]) {
    const page = read(`${prefix}programs/${product.id}/index.html`);
    assert.ok(page.includes(`href="/docs/programs/${product.id}/README.md"`));
    assert.ok(page.includes("All Rights Reserved"));
    assert.ok(page.includes('id="documentation"'));
    assert.doesNotMatch(page, /Build-Passing|MCP-Compatible/);
  }
}
assert.ok(read("LICENSE").startsWith("ProTech Proprietary License"));
assert.ok(read("LICENSE").includes("does not revoke previously granted"));
console.log("PROGRAM_DOCUMENTATION_PASS: 8 guides, 16 detail pages, 40 features, rights and MCP transparency");
