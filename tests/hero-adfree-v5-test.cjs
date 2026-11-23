"use strict";
/* Product hero: language, UI clarity, ad-free claim qualification and no visible counters. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const ar=read("index.html"),en=read("en/index.html");
const hero=ar.slice(ar.indexOf('<section class="hero"'),ar.indexOf("PROTECH_TOPIC_TAGS_BEGIN"));
const englishHero=en.slice(en.indexOf('<section class="en-hero"'),en.indexOf('<section class="en-section" id="programs"'));
const generator=read("scripts/build_en.py");
const css=read("assets/hero-adfree-v5.css");
assert.ok(hero.includes("hero-portfolio-panel v5-showcase"));
assert.ok(englishHero.includes("v4-en-portfolio v5-showcase"));
assert.ok(hero.includes("مجموعة واحدة، حلول أكثر."));
assert.ok(hero.includes("اختر المجال المناسب، واستكشف برامج ProTech العملية وميزاتها وإصداراتها المتاحة."));
assert.ok(hero.includes("بدون إعلانات مزعجة. بدون تشتيت."));
assert.ok(englishHero.includes("No intrusive ads. No distractions."));
assert.ok(hero.includes("نحرص في ProTech") && englishHero.includes("design goal"));
assert.ok(hero.includes("نتحقق من خصائص كل إصدار") && englishHero.includes("require verification"));
assert.ok(hero.includes("USER-FIRST · AD-FREE DESIGN GOAL"));
assert.ok(englishHero.includes("USER-FIRST · AD-FREE DESIGN GOAL"));
for(const [doc,categories] of [
 [hero,["الموارد البشرية","البيانات والتحليل","العقود والتقارير","المواد والإنتاج"]],
 [englishHero,["People &amp; HR","Data &amp; analytics","Contracts &amp; reports","Materials &amp; production"]],
]){
 for(const name of categories) assert.ok(doc.includes(name),"Missing category: "+name);
 const tileCount=(doc.match(/class="v4-panel-tile"/g)||[]).length;
 assert.equal(tileCount,4,"Four clear categories without clutter");
 const symbolCount=(doc.match(/<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">/g)||[]).length;
 assert.ok(symbolCount>=5,"Four vector icons and a clean-use shield");
 assert.doesNotMatch(doc,/<span class="v4-panel-symbol"[^>]*>[♙▧▦≡]/);
}
assert.match(hero,/<span id="gallery-portfolio-count" hidden aria-hidden="true">/);
assert.match(hero,/<div class="shell hero-stats v5-counts-accessibility-only" hidden aria-hidden="true">/);
assert.doesNotMatch(hero,/>\s*11\s+PROTECH APPLICATIONS/);
assert.ok(englishHero.includes("PROTECH APPLICATIONS"));
assert.doesNotMatch(englishHero,/>\s*(10|11)\s+products/);
assert.ok(en.includes('class="en-stat">Software collection'));
assert.ok(css.includes("#home .v5-counts-accessibility-only") && css.includes("#gallery-portfolio-count[hidden]"));
assert.ok(ar.includes('href="/assets/hero-adfree-v5.css?v=1"'));
assert.ok(en.includes('href="/assets/hero-adfree-v5.css?v=1"'));
assert.ok(generator.includes('href="/assets/hero-adfree-v5.css?v=1"'));
assert.ok(generator.includes("No intrusive ads. No distractions."));
assert.ok(generator.includes("Software collection"));
assert.ok(css.includes("@media(max-width:620px)") && css.includes("@media(prefers-reduced-motion:reduce)"));
assert.ok(css.includes(".v5-panel-all:focus-visible"));
const source=read("assets/v3_4.js");
assert.ok(source.includes('document.getElementById("gallery-portfolio-count")'),"Internal counts retained");
const apps=read("assets/app.js");
assert.ok(apps.includes('get("stat-apps")'),"Catalog metrics internally retained");
assert.ok(englishHero.includes('href="/en/programs/"')&&hero.includes('href="#products"'),"Category navigation retained");
console.log("HERO_ADFREE_V5_PASS",JSON.stringify({ar:true,en:true,categories:4,svgIcons:true,internalCountsPreserved:true,visibleCountsHidden:true,claimQualified:true}));
