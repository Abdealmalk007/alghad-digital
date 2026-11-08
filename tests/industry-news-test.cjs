"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const json=JSON.parse(fs.readFileSync(path.join(root,"assets/industry-news.json"),"utf8"));
const runtime={window:{}};
vm.runInNewContext(fs.readFileSync(path.join(root,"assets/industry-news-data.js"),"utf8"),runtime,{timeout:1300});
const official=runtime.window.AL_GHAD_INDUSTRY_NEWS;
assert.deepEqual(Object.keys(official.topics).sort(),["ai","cars","companies"]);
assert.equal(official.version,1);
assert.equal(official.generated_at,json.generated_at);
assert.ok(Array.isArray(official.sources)&&official.sources.length>=18);
const known=new Set(official.sources.map(x=>x.id));
assert.equal(known.size,official.sources.length);
const hosts=[
"openai.com","blog.google","nvidia.com","amd.com","apple.com","samsung.com",
"microsoft.com","toyota.com","global.toyota","hondanews.eu","porsche.com",
"subaru.co.jp","anthropic.com","deepseek.com","huawei.com","tesla.com",
"bmwgroup.com","mercedes-benz.com","hyundai.com","kiamedia.com"];
function valid(u) {
  const parsed=new URL(u);
  return parsed.protocol==="https:"&&!parsed.username&&!parsed.password&&!parsed.port&&
      hosts.some(h=>parsed.hostname===h||parsed.hostname.endsWith("."+h));
}
for(const spec of official.sources){
  assert.ok(valid(spec.url),spec.id+" official directory must use HTTPS official domain");
  assert.equal(typeof spec.feed_available,"boolean");
  assert.ok(Array.isArray(spec.topics)&&spec.topics.length>=1);
  if(["anthropic","deepseek","huawei","tesla","bmw"].includes(spec.id))assert.equal(spec.feed_available,false);
}
for(const topic of ["ai","companies","cars"]){
 const articles=official.topics[topic].articles;
 assert.ok(Array.isArray(articles)&&articles.length>=3,topic);
 assert.ok(articles.length<=18,topic);
 let previous=Infinity;
 const bySource={};
 const seen=new Set();
 for(const article of articles){
  assert.equal(article.topic,topic);
  assert.equal(article.official,true);
  assert.equal(article.language,"en");
  assert.ok(known.has(article.source));
  assert.ok(valid(article.url),article.url);
  assert.ok(article.title.length>=12&&article.title.length<=180);
  const time=Date.parse(article.published_at);
  assert.ok(Number.isFinite(time));
  assert.ok(time<=previous,topic+" news not sorted chronologically");
  assert.ok(time<=Date.now()+12*3600*1000);
  assert.ok(time>=Date.now()-46*24*3600*1000,"Only dated recent articles");
  previous=time;
  assert.ok(!seen.has(article.url),topic+" duplicate article");
  seen.add(article.url);
  bySource[article.source]=(bySource[article.source]||0)+1;
  assert.ok(bySource[article.source]<=5,"No single publisher dominates");
 }
}
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
for(const id of ["ai-news","tech-companies","car-news"]){
 assert.ok(!html.includes('id="'+id+'"'),id+" should not dominate the product-first homepage");
}
for(const href of ["/ai-news/","/tech-companies/","/cars/"]){
 assert.ok(html.includes('href="'+href+'"'),href+" missing from secondary news links");
}
for(const f of ["assets/industry-news.js","assets/industry-news.css","assets/industry-news-data.js"]){
 assert.ok(fs.existsSync(path.join(root,f)),f+" missing from news feed inventory");
}
for(const f of ["ai-news/index.html","tech-companies/index.html","cars/index.html"]){
 assert.ok(fs.existsSync(path.join(root,f)),f+" not generated");
 const page=fs.readFileSync(path.join(root,f),"utf8");
 assert.ok(page.includes('BreadcrumbList'),f+" missing SEO schema");
 assert.ok(page.includes('property="og:image"'),f+" missing preview");
 assert.ok(page.includes('target="_blank" rel="noopener noreferrer"'));
}
const client=fs.readFileSync(path.join(root,"assets/industry-news.js"),"utf8");
assert.ok(client.includes("textContent")&&client.includes("noopener noreferrer"));
assert.doesNotMatch(client,/innerHTML\s*=/);
console.log("PASS OFFICIAL_INDUSTRY_NEWS AI="+official.topics.ai.articles.length+
            " COMPANIES="+official.topics.companies.articles.length+
            " CARS="+official.topics.cars.articles.length+
            " OFFICIAL_SOURCES="+official.sources.filter(x=>x.feed_available).length);
