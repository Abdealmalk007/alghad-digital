"use strict";
/* Ensure founder attribution remains visible and machine-readable after daily rebuilds. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const name = "Abdulmalik Ali Hamza";
const credit = name + " — Founder of Alghad Digital (Jeel Alghad) and ProTech.";
const targets = [
  ["about/index.html", "Alghad Digital"],
  ["protech/index.html", "ProTech"],
  ["en/about/index.html", "Alghad Digital"],
  ["en/protech/index.html", "ProTech"],
];

for (const [file, brand] of targets) {
  const html = fs.readFileSync(path.join(root, file), "utf8");
  assert.ok(html.includes(credit), "Visible English founder attribution missing: " + file);
  assert.ok(html.includes('lang="en"') || file.startsWith("en/"),
    "English founder attribution language missing: " + file);
  assert.ok(!html.includes("عبدالملك علي حمزة"),
    "Name must not be transliterated into Arabic: " + file);
  const schemas = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)]
    .map(match => JSON.parse(match[1]));
  assert.ok(schemas.some(schema =>
    schema.mainEntity?.["@type"] === "Organization" &&
    schema.mainEntity.name === brand &&
    schema.mainEntity.founder?.["@type"] === "Person" &&
    schema.mainEntity.founder.name === name
  ), "Structured founder data missing: " + file);
}
console.log("FOUNDER_CREDIT_PASS pages=4 language=en name=" + name);
