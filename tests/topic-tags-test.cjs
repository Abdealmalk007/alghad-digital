"use strict";
/* Source-backed, crawler-visible SEO topic navigation checks. Node >=22. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=name=>fs.readFileSync(path.join(root,name),"utf8");
const sitemap=read("sitemap.xml");
const pageUrls=[...sitemap.matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(pageUrls.length,40);
assert.equal(new Set(pageUrls).size,40);
const featured=["smart-excel","stone","marble","reports","hr","kitchen","download","care","quotes"];
const news=["news","ai-news","tech-companies","cars"];
const tagged=new Set(["/","/en/","/programs/","/en/programs/",
  "/free-windows-tools/","/en/free-windows-tools/",
  ...featured.flatMap(id=>["/programs/"+id+"/","/en/programs/"+id+"/"]),
  ...news.flatMap(id=>["/"+id+"/","/en/"+id+"/"])]);
assert.equal(tagged.size,32);
const css="/assets/topic-tags.css?v=1";
for(const url of pageUrls) {
  const name=url.replace(/^\//,"")+"index.html";
  const markup=read(name);
  assert.ok(markup.includes('<link rel="canonical" href="https://alghad.digital'+url+'"'),"canonical changed "+name);
  assert.ok(!markup.includes('<meta name="keywords"'),"Google ignores meta keywords "+name);
  assert.ok(!markup.includes("TV Clean Launcher"),"Removed launcher restored "+name);
  if(!tagged.has(url)) continue;
  assert.equal(markup.split("PROTECH_TOPIC_TAGS_BEGIN").length-1,1,"Duplicate/missing tag section "+name);
  assert.equal(markup.split("PROTECH_TOPIC_TAGS_END").length-1,1);
  assert.equal(markup.split(css).length-1,1,"CSS duplicated/missing "+name);
  const matches=[...markup.matchAll(/<a class="protech-topic-chip" href="([^"]+)">(#.*?)<\/a>/g)];
  assert.ok(matches.length>=3,"Too few crawlable tags "+name+": "+matches.length);
  assert.equal(new Set(matches.map(x=>x[2])).size,matches.length,"Duplicate hashtags "+name);
  for(const [,href,tag] of matches) {
    assert.ok(href.startsWith("/"),"Hashtag must be internal "+href);
    assert.ok(tag.startsWith("#") && tag.length>2,"Missing real hashtag "+tag);
    const pathOnly=href.split("#")[0];
    assert.ok(pageUrls.includes(pathOnly),"Tag destination must be canonical in sitemap: "+href);
    if(url.startsWith("/en/"))assert.ok(href.startsWith("/en/"),"EN pages link to EN topics: "+href);
    else assert.ok(!href.startsWith("/en/"),"AR pages link to AR topics: "+href);
  }
}
const home=read("index.html"),enHome=read("en/index.html");
const catalog=read("programs/index.html"),enCatalog=read("en/programs/index.html");
for(const keyword of ["#برامج","#ويندوز","#أندرويد","#HR","#الذكاء_الاصطناعي"])assert.ok(home.includes(keyword),"Missing main homepage topic "+keyword);
for(const keyword of ["#Software","#Windows","#Android","#HR","#AI"])assert.ok(enHome.includes(keyword),"Missing English homepage topic "+keyword);
for(const content of [catalog,enCatalog]){
  assert.ok(content.includes('id="windows-software"'));
  assert.ok(content.includes('id="android-software"'));
  const prefix=content===enCatalog?"/en":"";
  assert.ok(content.includes('href="'+prefix+'/programs/hr/"'));
  assert.ok(content.includes('href="'+prefix+'/programs/download/"'));
}
const hr=read("programs/hr/index.html"), android=read("programs/download/index.html");
assert.ok(hr.includes("#HR") && hr.includes("#الموارد_البشرية") && hr.includes("#الرواتب"));
assert.ok(!hr.includes("#أندرويد"),"HR Windows-only listing must not claim Android");
assert.ok(android.includes("#أندرويد") && android.includes("#APK") && android.includes("#تنزيل_الفيديو"));
assert.ok(!android.includes("#ويندوز"),"Android app must not be misrepresented as Windows");
for(const name of ["index.html","en/index.html","programs/index.html","en/programs/index.html"]) {
 const title=read(name).match(/<title>([^<]+)<\/title>/);
 const desc=read(name).match(/<meta name="description" content="([^"]+)"/);
 assert.ok(title&&desc&&desc[1].length>=100);
 assert.ok(title[1].length<95,"Title should be concise");
}
assert.match(read("index.html"),/<title>[^<]*ويندوز[^<]*أندرويد[^<]*<\/title>/);
assert.match(read("en/index.html"),/<title>[^<]*Windows[^<]*Android[^<]*<\/title>/);
assert.ok(read(".github/workflows/update-tech-news.yml").includes('cron: "30 4 * * *"'));
const wf=read(".github/workflows/update-tech-news.yml");
assert.ok(wf.indexOf("scripts/build_topic_tags.py")>wf.indexOf("scripts/build_en.py"));
assert.ok(wf.indexOf("scripts/build_site_search.py")>wf.indexOf("scripts/build_topic_tags.py"));
assert.ok(wf.includes("node tests/topic-tags-test.cjs"),"Daily news refresh should validate topic SEO");
assert.ok(read("assets/site-search-index.js").includes("الوسوم والتخصصات المتوفرة"),"Search index rebuilt after crawlable topic content");
console.log("SEO_TOPIC_TAGS_PASS",JSON.stringify({canonicalPages:pageUrls.length,taggedPages:tagged.size,productPages:featured.length*2,newsPages:news.length*2,dailyNewsCron:"07:30 Asia/Riyadh",languages:["ar","en"]}));
