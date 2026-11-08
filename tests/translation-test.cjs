"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const crypto=require("node:crypto");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const newsroom=JSON.parse(read("assets/news.json"));
const industry=JSON.parse(read("assets/industry-news.json"));
const cache=JSON.parse(read("assets/translation-cache.json"));
const context={window:{}};
vm.runInNewContext(read("assets/news-data.js"),context,{timeout:1200});
vm.runInNewContext(read("assets/industry-news-data.js"),context,{timeout:1200});
assert.equal(context.window.AL_GHAD_NEWS.generated_at,newsroom.generated_at);
assert.equal(context.window.AL_GHAD_INDUSTRY_NEWS.generated_at,industry.generated_at);
assert.equal(context.window.AL_GHAD_NEWS.articles.length,newsroom.articles.length);
assert.deepEqual([...Object.keys(context.window.AL_GHAD_INDUSTRY_NEWS.topics)].sort(),["ai","cars","companies"]);
assert.equal(cache.version,1);
assert.equal(cache.language_pair,"en|ar");

const records=[
  ...newsroom.articles,
  ...Object.values(industry.topics).flatMap(section=>section.articles)
];
assert.ok(records.length>=65);
const arabic=/[\u0621-\u064a]/g;
const english=/[A-Za-z]{2,}/g;
const stats={machine:0,original_ar:0,unavailable:0};
for(const row of records){
  assert.ok(typeof row.title==="string"&&row.title.length>=12);
  assert.ok(row.url.startsWith("https://"));
  assert.ok(Number.isFinite(Date.parse(row.published_at)));
  assert.ok(["machine","original_ar","unavailable"].includes(row.translation_status));
  stats[row.translation_status]++;
  if(row.translation_status==="original_ar"){
    assert.equal(row.title_ar,row.title);
    assert.ok((row.title.match(arabic)||[]).length>0);
  }else if(row.translation_status==="machine"){
    assert.ok(typeof row.title_ar==="string");
    assert.ok((row.title_ar.match(arabic)||[]).length>=4);
    assert.notEqual(row.title_ar,row.title);
    assert.equal(row.translation_provider,"MyMemory");
    const key=crypto.createHash("sha256").update(row.title.trim(),"utf8").digest("hex");
    assert.equal(cache.entries[key],row.title_ar);
    assert.ok((row.title.match(english)||[]).length>0);
  }else{
    assert.equal(row.title_ar,null);
    assert.ok((row.title.match(english)||[]).length>0);
    assert.equal(row.translation_provider,undefined);
  }
}
assert.ok(stats.machine>=1,"At least one machine translation required in initial snapshot");
assert.ok(stats.original_ar>=1,"Original Arabic news must remain untouched");
const source=read("scripts/translate_news.py");
for(const token of ["api.mymemory.translated.net/get","MAX_DAILY_CHARS","translation_status","unavailable","title_ar","translation-cache.json"]){
  assert.ok(source.includes(token),token);
}
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'));
assert.ok(workflow.includes("python scripts/translate_news.py"));
assert.ok(workflow.includes("node tests/translation-test.cjs"));
assert.ok(workflow.includes("assets/translation-cache.json"));
const seo=read("ai-news/index.html");
assert.ok(seo.includes("original-news-title")&&seo.includes('lang="ar"'));
assert.ok(seo.includes("translation-disclaimer"));
const newsHtml=read("news/index.html");
const firstNewsHaveTranslation=newsroom.articles.slice(0,25).some(x=>x.translation_status==="machine");
if(firstNewsHaveTranslation)assert.ok(newsHtml.includes("translation-disclaimer"),"Original and translated titles must appear in crawlable news pages");
for(const client of ["assets/industry-news.js","assets/editorial.js"]){
 const text=read(client);
 assert.ok(text.includes("translation_status"));
 assert.ok(text.includes("title_ar"));
 assert.ok(text.includes("lang"));
}
console.log("TRANSLATION_QA_PASS "+JSON.stringify(stats)+" CACHE="+Object.keys(cache.entries).length);
