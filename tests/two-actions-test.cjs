"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=file=>fs.readFileSync(path.join(root,file),"utf8");
const context={window:{}};
vm.runInNewContext(read("assets/products.js"),context,{timeout:1000});
vm.runInNewContext(read("assets/downloads.js"),context,{timeout:1000});
const products=context.window.AL_GHAD_PRODUCTS;
const downloads=context.window.AL_GHAD_DOWNLOADS;
assert.equal(products.length,8);
const allowed=new Map(products.map(p=>{
  const m=downloads[p.id];
  const recommended=m?.files?.find(f=>f.recommended);
  assert.ok(!recommended || recommended.url.startsWith("https://github.com/Abdealmalk007/"+m.repository+"/releases/download/"));
  return [p.id,recommended?.url||null];
}));
const archive="https://github.com/Abdealmalk007/ProTechStoneManager/archive/refs/heads/main.zip";
const setup="https://github.com/Abdealmalk007/ProTechStoneManager/releases/download/v2.0.0-unsigned-preview/ProTechStoneManager_Setup_v2.0.0_UNSIGNED.exe";
assert.equal(allowed.get("stone"),setup);
const pages=["index.html","en/index.html","programs/index.html","en/programs/index.html",
             "protech/index.html","en/protech/index.html","programs/stone/index.html","en/programs/stone/index.html"];
for(const file of pages){
 const html=read(file);
 assert.ok(!html.includes(archive),file+" has redundant Stone source download");
 assert.ok(html.includes("/assets/share.js?v=1"),file+" missing sharing support");
 assert.ok(!html.includes('id="compare-tray"')&&!html.includes("compare-toggle"),file+" compare UI still present");
}
function actionBlocks(file,cardMarker,actionsMarker){
 const html=read(file);
 const expressions=new RegExp('<article class="[^"]*'+cardMarker+'[^"]*"[^>]*[\\s\\S]*?<\\/article>','g');
 const blocks=[...html.matchAll(expressions)].map(m=>m[0]);
 assert.equal(blocks.length,8,file+" requires eight cards");
 for(const block of blocks){
   const id=block.match(/(?:data-prerender-product|data-product)="([a-z-]+)"/)?.[1]||
            block.match(/href="(?:\.\.\/)?(?:\/en\/)?programs\/([a-z-]+)\//)?.[1];
   const action=block.match(new RegExp('<div class="'+actionsMarker+'">([\\s\\S]*?)<\\/div>'))?.[1];
   assert.ok(action,file+" missing actions");
   assert.ok(!/source-download|source ZIP|compare|brand-card-link|pre-product-details|Features and details|Visit GitHub|GitHub repository/i.test(action),
             file+" contains forbidden shortcut");
   assert.match(action,/class="program-details"/ ,file+" missing explicit details action");
   const hrefs=[...action.matchAll(/href="([^"]+)"/g)].map(x=>x[1]).filter(url=>url.startsWith("https://github.com/"));
   assert.ok(hrefs.length<=1,file+" more than one download action");
   if(id && allowed.has(id)){
     if(allowed.get(id)) assert.ok(hrefs.includes(allowed.get(id)),file+" missing direct download "+id);
     else assert.equal(hrefs.length,0,file+" must not invent a download for "+id);
   }
 }
}
actionBlocks("index.html","pre-product-card","pre-product-actions");
actionBlocks("en/index.html","en-product-card","en-product-actions");
const arCatalog=read("programs/index.html");
assert.equal((arCatalog.match(/class="directory-actions"/g)||[]).length,8);
assert.equal((arCatalog.match(/href="https:\/\/github\.com\/Abdealmalk007\/[^"]+\/releases\/download\//g)||[]).length,5);
const brand=read("protech/index.html");
assert.equal((brand.match(/class="brand-card-actions"/g)||[]).length,8);
assert.ok(!read("assets/v3.js").includes("hydrateCompareButtons"));
assert.ok(!read("assets/app.js").includes("stone-source-download"));
const share=read("assets/share.js");
assert.ok(share.includes("showcase-release[data-release-id]"));
assert.ok(share.includes("brand-card-actions,.directory-actions"));
assert.ok(share.includes("navigator.share")&&share.includes("navigator.clipboard"));
console.log("PROGRAM_ACTIONS_PASS: 8 explicit details links, 5 official downloads, 3 unavailable states, sharing preserved");
