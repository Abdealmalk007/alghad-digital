"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),vm=require("node:vm");
const root=path.resolve(__dirname,".."),read=f=>fs.readFileSync(path.join(root,f),"utf8");
const ctx={window:{}};for(const f of ["assets/products.js","assets/downloads.js"])vm.runInNewContext(read(f),ctx);
const priority=["smart-excel","reports","hr","download"],products=ctx.window.AL_GHAD_PRODUCTS,downloads=ctx.window.AL_GHAD_DOWNLOADS;
assert.deepEqual(Array.from(products.slice(0,4),p=>p.id),priority);
for(const prefix of ["","en/"]){const h=read(prefix+"index.html");assert.deepEqual([...h.matchAll(/data-v6-priority="([^"]+)"/g)].map(m=>m[1]),priority);assert.equal(h.split("V6_FEATURED_BEGIN").length-1,1);for(const id of priority){const block=h.match(new RegExp('data-v6-priority="'+id+'"[\\s\\S]*?</article>'))[0];assert.ok(block.includes(downloads[id].files.find(f=>f.recommended).url));assert.ok(block.includes('/'+prefix+'programs/'+id+'/'));}for(const p of products){const page=read(prefix+"programs/"+p.id+"/index.html");assert.equal(page.split("V6_GUIDE_BEGIN").length-1,1);assert.ok(page.includes("v6-steps"));}}
const sitemap=read("sitemap.xml"),urls=[...sitemap.matchAll(/<loc>https:\/\/alghad\.digital\/([^<]*)<\/loc>/g)].map(x=>x[1]);for(const url of urls){const h=read(url+"index.html");assert.equal(h.split("V6_ASSETS_BEGIN").length-1,1);assert.ok(h.includes('/assets/v6.css?v=6.3.0'));assert.ok(h.includes('/assets/v6.js?v=6.3.0'));}
const work=read(".github/workflows/update-tech-news.yml");assert.ok(work.indexOf("scripts/build_v6.py")>work.indexOf("scripts/build_en.py"));assert.ok(work.indexOf("scripts/build_v6.py")<work.indexOf("scripts/build_site_search.py"));assert.ok(work.includes("node tests/v6-test.cjs"));
const js=read("assets/v6.js");assert.ok(js.includes("alghad_analytics_consent_v1"));assert.ok(js.includes("protech_download_click"));assert.ok(js.includes("alghad-theme"));
console.log("V6_PASS",JSON.stringify({pages:urls.length,priority,guidePages:products.length*2,consentRequired:true}));
// V6.2: identical vector mark, release data parity, bilingual brand cache invalidation.
const facts=JSON.parse(read("assets/release-facts.json")).releases;
assert.equal(read("favicon.svg"),read("assets/brand/dawn-g.svg"));
for(const route of urls){const h=read(route+"index.html");assert.ok(h.includes("/favicon.svg?v=6"),route);assert.ok(h.includes("/favicon.ico?v=6"),route);}
for(const prefix of ["","en/"]){
 const h=read(prefix+"index.html");
 const actual=[...h.matchAll(/data-v6-release="([^"]+)"/g)].map(m=>m[1]);
 const expected=Object.entries(facts).sort((a,b)=>b[1].published_at.localeCompare(a[1].published_at)).filter(([id,f])=>downloads[id]?.version===f.version&&downloads[id]?.repository===f.repository&&downloads[id]?.files.some(a=>a.recommended)).map(([id])=>id);
 assert.deepEqual(actual,expected);
 for(const id of actual){assert.ok(h.includes(facts[id].tag_url));}
 assert.equal(h.split("V6_RELEASES_BEGIN").length-1,1);
}
console.log("V6_2_BRAND_RELEASE_PASS",JSON.stringify({pages:urls.length,releaseFacts:Object.keys(facts).length}));
