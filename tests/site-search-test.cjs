"use strict";
/* Verify whole-site search, daily news rebuild, sitemap and bilingual UI.
   Node 22+, no external dependencies. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const cp=require("node:child_process");
const root=path.resolve(__dirname,"..");
const read=name=>fs.readFileSync(path.join(root,name),"utf8");
const sitemap=read("sitemap.xml");
const paths=Array.from(sitemap.matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g),m=>m[1]);
assert.equal(paths.length,40,"All canonical pages remain in sitemap");
assert.equal(new Set(paths).size,40);
const scriptSrc="/assets/site-search.js?v=1";
const stylesheet="/assets/site-search.css?v=1";
for(const route of paths){
  const name=route.replace(/^\//,"")+"index.html";
  const html=read(name);
  assert.equal(html.split(scriptSrc).length-1,1,"Sitewide search script missing/duplicated: "+name);
  assert.equal(html.split(stylesheet).length-1,1,"Search CSS missing/duplicated: "+name);
}
const sandbox={window:{}};
vm.runInNewContext(read("assets/site-search-index.js"),sandbox,{timeout:1000});
const idx=sandbox.window.AL_GHAD_SITE_SEARCH;
assert.equal(idx.schema,1);
assert.equal(idx.page_count,40);
const nTech=JSON.parse(read("assets/news.json")).articles.length;
const industry=JSON.parse(read("assets/industry-news.json"));
const nIndustry=Object.values(industry.topics).reduce((sum,topic)=>sum+topic.articles.length,0);
const nNews=nTech+nIndustry;
assert.ok(nNews>=20,"Search index should reflect populated daily news feeds");
assert.equal(idx.news_count,nNews);
assert.equal(idx.records.length,40+nNews);
assert.equal(idx.records.filter(v=>v.kind==="page"||v.kind==="program").length,40);
assert.equal(idx.records.filter(v=>v.kind==="news").length,nNews);
assert.equal(idx.records.filter(v=>v.kind==="program").length,18);
assert.equal(new Set(idx.records.map(v=>v.id)).size,40+nNews,"No duplicate search record ids");
for(const v of idx.records) {
  assert.match(v.url,/^\/(?:[a-z0-9-]+\/)*$/,"Search results must stay inside our website");
  assert.ok(v.title && v.category && v.content,"Search result missing content: "+v.id);
}
const includes=(word,kind)=>idx.records.some(v=>(!kind||v.kind===kind)&&[v.title,v.description,v.content].join(" ").toLowerCase().includes(word.toLowerCase()));
assert.ok(includes("Quotes","program"),"Quotes page is searchable");
assert.ok(includes("عروض الأسعار","program"),"Arabic pricing pages are searchable");
assert.ok(includes(JSON.parse(read("assets/news.json")).articles[0].title,"news"),"Fresh daily tech headlines are searchable");
assert.ok(includes("سيارات","news")||includes("سيارات","page"),"Cars news discoverable");
assert.ok(includes("Marble","program"),"Marble app is searchable");
assert.ok(!idx.records.some(v=>v.url.includes("/programs/tv/")),"Removed TV app stays absent");
assert.ok(!idx.records.some(v=>v.title.includes("TV Clean Launcher")),"Removed TV app stays absent");
assert.ok(read("assets/site-search.js").includes("sitewide-search-trigger"));
assert.ok(read("assets/site-search.js").includes("ctrlKey"));
assert.ok(read("assets/site-search.js").includes("site-search-index.js"));
assert.ok(read("assets/site-search.css").includes("@media(max-width:600px)"));
cp.execFileSync(process.execPath,["--check",path.join(root,"assets/site-search.js")]);
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'),"Keep daily 07:30 Riyadh schedule");
assert.ok(workflow.includes("python scripts/build_site_search.py"),"Rebuild the index after each daily news update");
assert.ok(workflow.includes("node tests/site-search-test.cjs"),"Guard site search in CI");
assert.ok(workflow.includes("assets/site-search-index.js"),"Commit refreshed search data");
assert.ok(workflow.indexOf("python scripts/build_site_search.py")>workflow.indexOf("python scripts/build_en.py"),"Build after bilingual pages");
console.log("SITEWIDE_SEARCH_PASS",JSON.stringify({pages:40,software:18,news:nNews,records:40+nNews,cron:"07:30 Asia/Riyadh",languages:["ar","en"]}));
