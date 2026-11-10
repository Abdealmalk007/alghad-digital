"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const context={window:{}};
vm.runInNewContext(read("assets/products.js"),context,{timeout:1000});
const products=context.window.AL_GHAD_PRODUCTS;
assert.equal(products.length,8,"Exactly eight distinct programs");
assert.equal(new Set(products.map(p=>p.id)).size,8,"No duplicate IDs");
assert.ok(products.some(p=>p.id==="stone"&&p.title==="ProTech Stone Manager"));
assert.ok(!products.some(p=>["porcelain","recorder","omar","reem","tv"].includes(p.id)));
for(const rel of ["programs/index.html","en/programs/index.html"]){
  const content=read(rel);
  assert.ok(!content.includes("Porcelain Manager"),rel+" duplicate listed");
  assert.ok(content.includes("/assets/share.js?v=1"),rel+" missing share function");
}
for(const [rel,target] of [
  ["programs/porcelain/index.html","https://alghad.digital/programs/stone/"],
  ["en/programs/porcelain/index.html","https://alghad.digital/en/programs/stone/"]]){
  const page=read(rel);
  assert.ok(page.includes('name="robots" content="noindex,follow"'),rel);
  assert.ok(page.includes('rel="canonical" href="'+target+'"'),rel);
}
for(const obsolete of ["programs/tv/index.html","en/programs/tv/index.html","assets/previews/tv.svg"]){
  assert.ok(!fs.existsSync(path.join(root,obsolete)),"Removed TV launcher must not be deployed: "+obsolete);
}
for(const page of ["index.html","en/index.html","programs/index.html","en/programs/index.html","protech/index.html","en/protech/index.html"]){
  const markup=read(page);
  assert.ok(!markup.includes("TV Clean Launcher")&&!markup.includes("/programs/tv/"),"Removed project resurfaced: "+page);
}
assert.ok(!read("assets/products.js").includes('"id": "tv"'),"TV launcher catalog entry reappeared");
const sitemap=read("sitemap.xml");
assert.equal((sitemap.match(/<loc>/g)||[]).length,38);
assert.ok(!sitemap.includes("/programs/porcelain/"));
assert.ok(!sitemap.includes("/programs/tv/"),"TV launcher must not appear in sitemap");
assert.ok(sitemap.includes("https://alghad.digital/programs/stone/"));
assert.ok(sitemap.includes("https://alghad.digital/en/programs/stone/"));
assert.ok(read("programs/stone/index.html").includes("ProTechStoneManager_Setup_v2.0.0_UNSIGNED.exe"),
 "Never drop the documented Stone preview build");
assert.ok(read(".github/workflows/update-tech-news.yml").includes('cron: "30 4 * * *"'));
console.log("DEDUP_REGRESSION_PASS: 8 programs, canonical redirects, 38 URLs, preserved Stone preview and daily news cron");
