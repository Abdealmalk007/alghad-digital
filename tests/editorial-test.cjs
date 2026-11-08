"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const ctx={window:{}};
vm.runInNewContext(read("assets/news-data.js"),ctx,{timeout:1000});
vm.runInNewContext(read("assets/tools-data.js"),ctx,{timeout:1000});
const news=ctx.window.AL_GHAD_NEWS,tools=ctx.window.AL_GHAD_TOOLS;
assert.ok(news&&news.version===1&&Array.isArray(news.articles));
assert.ok(news.articles.length>=5&&news.articles.length<=36);
assert.ok(!Number.isNaN(Date.parse(news.generated_at)));
let previous=Infinity;
const newsHosts=["aitnews.com","tech-wd.com","arabhardware.net","techvoicearabia.com",
"technologyarabia.com","3arrafni.com","th3professional.com","aljazeera.net","bbc.com","bbc.co.uk","unlimit-tech.com"];
const hostAllowed=(url,allowed)=>{
  const u=new URL(url);return u.protocol==="https:"&&!u.username&&!u.password&&
    allowed.some(x=>u.hostname===x||u.hostname.endsWith("."+x));
};
for(const item of news.articles) {
  assert.ok(item.title.length>=15&&item.title.length<=175);
  assert.ok(hostAllowed(item.url,newsHosts),item.url);
  const ms=Date.parse(item.published_at);
  assert.ok(Number.isFinite(ms));
  assert.ok(ms<=previous,"Articles must sort by date descending");
  previous=ms;
  assert.ok(item.source_name&&item.category);
}
assert.equal(tools.items.length,8);
const expected=["everything","ventoy","rufus","irfanview","fileconverter","vlc","fdm","powertoys"];
assert.deepEqual(Array.from(tools.items.map(x=>x.id)),expected);
const allowedVendors=["voidtools.com","ventoy.net","rufus.ie","irfanview.com",
 "file-converter.io","videolan.org","freedownloadmanager.org","github.com"];
for(const item of tools.items){
  assert.ok(hostAllowed(item.url,allowedVendors),item.url);
  assert.ok(item.description.length>25);
  assert.ok(Array.isArray(item.features)&&item.features.length>=3);
  assert.match(item.image,/^assets\/tools\/[a-z0-9-]+\.svg$/);
  assert.ok(fs.existsSync(path.join(root,item.image)),"Missing artwork: "+item.id);
  const art=read(item.image);
  assert.match(art,/<svg/);assert.match(art,/<\/svg>/);
}
const html=read("index.html");
for(const id of ["news","free-tools","technology-news-grid","windows-tools-grid","news-source-links",
                   "windows-tools-search","news-last-updated","news-freshness"]){
  assert.ok(html.includes('id="'+id+'"'),"Missing section: "+id);
}
for(const script of ["news-data.js","tools-data.js","editorial.js","editorial.css"]){
  assert.ok(fs.existsSync(path.join(root,"assets",script)),"Missing asset: "+script);
  assert.ok(html.includes("assets/"+script),"Unlinked asset: "+script);
}
for(const term of ["Call Recorder PRO","مطبخ ريم","عمر Kids"]){
 assert.ok(!html.includes(term),"Excluded project in HTML: "+term);
}
assert.ok(fs.existsSync(path.join(root,".github/workflows/update-tech-news.yml")));
assert.ok(read(".github/workflows/update-tech-news.yml").includes("schedule:"));
console.log("EDITORIAL_QA_PASS articles="+news.articles.length+" sources="+news.sources.length+" tools="+tools.items.length+" svg=8");
