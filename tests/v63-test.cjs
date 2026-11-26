"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const root=path.resolve(__dirname,".."),read=f=>fs.readFileSync(path.join(root,f),"utf8").replace(/\r\n/g,"\n");
const h=read("index.html");
const groups={core:["style.css","v2.css","v3.css","v3_1.css","downloads.css","v3_3.css","v3_4.css"],secondary:["seo-home.css","product-first.css","language.css","share.css","refinement.css"]};
for(const [name,files] of Object.entries(groups)){
 const payload=files.map(f=>"/* "+f+" */\n"+read("assets/"+f).trimEnd()+"\n").join("\n");
 const bundle=read("assets/home-"+name+".bundle.css");
 assert.equal(bundle,payload);
 const digest=crypto.createHash("sha256").update(payload).digest("hex").slice(0,12);
 assert.ok(h.includes("/assets/home-"+name+".bundle.css?v="+digest));
 for(const f of files)assert.ok(!new RegExp('<link rel="stylesheet" href="(?:/)?assets/'+f.replace(".","\\.")+'(?:\\?[^"]*)?"').test(h));
}
assert.equal((h.match(/rel="stylesheet"/g)||[]).length,14);
for(const prefix of ["","en/"])for(const id of ["smart-excel","reports","hr","download"]){
 const page=read(prefix+"programs/"+id+"/index.html");assert.equal((page.match(/V6_TUTORIAL_BEGIN/g)||[]).length,1);assert.ok(page.includes('data-v6-tutorial="'+id+'"'));
 if(id==="download")assert.ok(page.includes("/assets/screenshots/download-v6-tools-20261029.webp"));
}
const img=fs.readFileSync(path.join(root,"assets/screenshots/download-v6-tools-20261029.webp"));assert.equal(img.toString("ascii",0,4),"RIFF");assert.equal(img.toString("ascii",8,12),"WEBP");assert.ok(img.length<150000);
const w=read(".github/workflows/update-tech-news.yml");assert.ok(w.indexOf("bundle_home_css.py --restore")<w.indexOf("scripts/prerender_home.py"));assert.ok(w.indexOf("run: python scripts/bundle_home_css.py\n")>w.indexOf("scripts/polish_search_snippets.py"));
console.log("V63_PASS styles=14 tutorials=8 screenshotBytes="+img.length);
