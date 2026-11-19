"use strict";
/* Read published release facts from approved site data, not hard-coded counts. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");

function releaseFacts(root){
  const sandbox={window:{}};
  for(const file of ["products.js","downloads.js"]){
    vm.runInNewContext(
      fs.readFileSync(path.join(root,"assets",file),"utf8"),
      sandbox,{timeout:2500,filename:file}
    );
  }
  const products=sandbox.window.AL_GHAD_PRODUCTS;
  const downloads=sandbox.window.AL_GHAD_DOWNLOADS;
  assert.ok(Array.isArray(products)&&products.length>0);
  assert.ok(downloads&&typeof downloads==="object");
  const safeRelease=(url,repo)=>typeof url==="string"&&
    typeof repo==="string"&&
    url.startsWith("https://github.com/Abdealmalk007/"+repo+"/releases/")&&
    /^https:\/\/github\.com\/Abdealmalk007\/[A-Za-z0-9_.-]+\/releases\/(?:tag|download)\/[^\s?#]+$/.test(url);
  const knownFiles=new Set();
  const recommendedUrls=new Map();
  let recommendedProducts=0, publicReleases=0;
  for(const p of products){
    const d=downloads[p.id]||{};
    if(p.status==="public"&&safeRelease(d.release,d.repository))publicReleases++;
    let hasPreferred=false;
    for(const f of d.files||[]){
      if(safeRelease(f.url,d.repository)){
        knownFiles.add(f.url);
        if(f.recommended){hasPreferred=true;recommendedUrls.set(p.id,f.url);}
      }
    }
    if(hasPreferred)recommendedProducts++;
  }
  assert.ok(recommendedProducts<=products.length);
  assert.ok(publicReleases<=products.length);
  return {recommendedProducts,publicReleases,knownFiles,recommendedUrls,productCount:products.length};
}
module.exports=releaseFacts;
