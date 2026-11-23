"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const read = name => fs.readFileSync(path.join(root,name),"utf8");
const cfg = JSON.parse(read("config/top5_categories.json"));
const data = JSON.parse(read("assets/top5-news.json"));
const categories = cfg.categories.filter(c => c.enabled !== false);
assert.equal(categories.length,11,"Approved category set");
assert.equal(new Set(categories.map(c=>c.id)).size,categories.length);
assert.equal(data.max_items,5);
assert.equal(cfg.scheduled_target,"07:30");
assert.equal(data.timezone,"Asia/Riyadh");
assert.equal(Object.keys(data.topics).length,categories.length);
const now=Date.now();
let total=0;
for(const c of categories) {
 assert.ok(c.id.match(/^[a-z0-9-]+$/));
 const records=data.topics[c.id];
 assert.ok(Array.isArray(records)&&records.length<=5);
 const urls=new Set();
 for(const [i,a] of records.entries()){
   assert.equal(a.category,c.id);
   assert.equal(a.rank,i+1);
   assert.ok(!urls.has(a.url),"Repeated article "+c.id);
   urls.add(a.url);
   assert.ok(a.url.startsWith("https://") && new URL(a.url).hostname);
   assert.ok(a.original_title.length>=12);
   assert.ok(a.source_name);
   const age=(now-Date.parse(a.published_at))/3600000;
   assert.ok(age>=-0.51 && age<=24*7+1,"Stale or future article");
   assert.ok(!a.image_url,"No unlicensed image imports");
   assert.ok(!a.title_en || a.title_en.length>=5);
   assert.ok(!a.title_ar || a.title_ar.length>=5);
 }
 total+=records.length;
}
const arabic=read("top-5/index.html");
const english=read("en/top-5/index.html");
for(const [lang,code,url] of [["ar",arabic,"/top-5/"],["en",english,"/en/top-5/"]]){
  assert.ok(code.includes('<html lang="'+lang+'" dir="'+(lang==="ar"?"rtl":"ltr")+'">'));
  assert.ok(code.includes('<link rel="canonical" href="https://alghad.digital'+url+'">'));
  assert.equal((code.match(/class="top5-tab"/g)||[]).length,categories.length);
  assert.equal((code.match(/class="top5-panel"/g)||[]).length,categories.length);
  assert.equal((code.match(/class="top5-story"/g)||[]).length,total);
  assert.equal((code.match(/class="top5-read"/g)||[]).length,total);
  assert.ok(code.includes('src="/assets/top5-hub.js?v=1"'));
  assert.ok(code.includes('href="/assets/top5-hub.css?v=1"'));
  assert.ok(code.includes('role="tablist"')&&code.includes('role="tabpanel"'));
  assert.ok(code.includes('type="button" role="tab"'));
  assert.ok(code.includes('data-top5-back')&&code.includes('data-top5-top'));
  assert.ok(!/src="https:\/\//.test(code),"No third-party image hotlinks or scripts");
}
assert.ok(arabic.includes("TOP 5")&&english.includes("TOP 5"));
const sitemap=read("sitemap.xml");
assert.equal((sitemap.match(/<loc>/g)||[]).length,48);
assert.ok(sitemap.includes("<loc>https://alghad.digital/top-5/</loc>"));
assert.ok(sitemap.includes("<loc>https://alghad.digital/en/top-5/</loc>"));
const homepage=read("index.html");
assert.ok(homepage.includes('href="/top-5/" class="nav-link"'));
assert.ok(homepage.includes('class="top5-home-primary" href="/top-5/"'));
for(const legacy of ["news","cars","ai-news","tech-companies"]){
 assert.ok(fs.existsSync(path.join(root,legacy,"index.html")));
 assert.ok(fs.existsSync(path.join(root,"en",legacy,"index.html")));
}
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'));
assert.ok(workflow.includes("python scripts/build_top5.py"));
assert.ok(workflow.includes("node tests/top5-hub-test.cjs"));
assert.ok(workflow.includes("git add -- assets/news.json assets/news-data.js assets/top5-news.json"));
const css=read("assets/top5-hub.css");
const script=read("assets/top5-hub.js");
assert.ok(css.includes("@media(max-width:520px)"));
assert.ok(css.includes("@media(prefers-reduced-motion:reduce)"));
assert.ok(script.includes("ArrowDown")&&script.includes("aria-selected")&&script.includes("hashchange"));
console.log("TOP5_HUB_TEST_PASS",JSON.stringify({categories:categories.length,storySlots:total,ar:true,en:true,canonical:48,schedule:"07:30 Asia/Riyadh"}));
