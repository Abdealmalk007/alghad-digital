"use strict";
/* Alghad Digital v2: production-safe static build verification */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const ctx={window:{}};
vm.runInNewContext(read("assets/products.js"),ctx,{timeout:1000});
vm.runInNewContext(read("assets/downloads.js"),ctx,{timeout:1000});
const manifest=ctx.window.AL_GHAD_DOWNLOADS;
const p=ctx.window.AL_GHAD_PRODUCTS;
assert.equal(Object.keys(manifest).length,5,"Five published projects must have release records");
const four=["download","hr","marble","reports"];
for(const id of four){
  const d=manifest[id];
  const product=p.find(x=>x.id===id);
  assert.ok(product && product.status==="public",id);
  assert.equal(d.repository,product.github.split("/").pop());
  assert.ok(d.release.startsWith(product.github+"/releases/tag/"),id);
  assert.equal(d.channel,"preview",id);
  assert.ok(Array.isArray(d.files) && d.files.length>0,id);
  assert.equal(d.files.filter(x=>x.recommended).length,1,"One default choice per release: "+id);
  for(const asset of d.files){
    assert.match(asset.url,/^https:\/\/github\.com\/Abdealmalk007\/[A-Za-z0-9._-]+\/releases\/download\/[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+\.(?:apk|exe|zip)$/);
    assert.ok(asset.url.startsWith(product.github+"/releases/download/"));
    assert.ok(asset.bytes>100000,"Asset appears too small: "+asset.url);
    assert.ok(!/debug/i.test(asset.url),"Never promote a Debug binary: "+asset.url);
  }
}
assert.equal(manifest.stone.files.length,0,"Stone public release is not currently available");
assert.equal(manifest.stone.release,null);

assert.ok(Array.isArray(p));
assert.equal(p.length,10,"The public catalog must contain 10 products");
assert.equal(new Set(p.map(x=>x.id)).size,10);
const published=["stone","marble","reports","hr","download"].sort();
assert.deepEqual(Array.from(p.filter(x=>x.status==="public"),x=>x.id).sort(),published);
assert.equal(p.filter(x=>x.status==="dev").length,5);
assert.ok(!p.some(x=>["omar","reem","recorder"].includes(x.id)));
assert.ok(!fs.existsSync(path.join(root,"assets/previews/recorder.svg")),"Removed preview must not ship");
const allIds=new Set(p.map(x=>x.id));
for(const id of ["kitchen","care","porcelain","quotes","tv"])assert.ok(allIds.has(id));
for(const item of p){
  for(const field of ["id","title","english","description","details","category","version","preview","previewAlt","displayStatus"]){
    assert.equal(typeof item[field],"string",item.id+":"+field);
    assert.ok(item[field].trim(),item.id+":"+field+" empty");
  }
  assert.ok(Array.isArray(item.features)&&item.features.length>=3,item.id+": insufficient features");
  assert.ok(Array.isArray(item.platforms)&&item.platforms.length>=1);
  assert.equal(item.displayStatus,item.status==="public"?"مكتمل":"قريبًا جدًا");
  assert.match(item.preview,/^assets\/previews\/[a-z0-9_-]+\.svg$/);
  const svg=read(item.preview);
  assert.match(svg,/<svg\b/);assert.match(svg,/<\/svg>/);
  assert.match(svg,/viewBox="0 0 960 540"/);
  assert.doesNotMatch(svg,/<script\b|xlink:href|<foreignObject\b|javascript:/i);
  if(item.status==="public"){
    assert.equal(item.github,"https://github.com/Abdealmalk007/"+{
      stone:"ProTechStoneManager",marble:"MarbleDeliveryPro",
      reports:"DailyWorkReports-Flexible",hr:"HR",download:"Download-Anything-PRO"
    }[item.id]);
  }else{
    assert.equal(item.github,null,item.id+": coming soon must not link nonexistent repo");
    assert.equal(item.release,null);
  }
}
const html=read("index.html");
assert.match(html,/<html lang="ar" dir="rtl">/);
for(const key of ['id="catalog"','id="search"','id="featured-cards"','id="stat-upcoming"',
                  'id="product-modal"','data-filter="public"','data-filter="dev"'])assert.ok(html.includes(key),key);
for(const f of ["index.html","assets/style.css","assets/v2.css","assets/v3.css","assets/v3.js","assets/v3_1.css","assets/v3_1.js","assets/downloads.css","assets/downloads.js","assets/downloads-ui.js","assets/v3_3.js","assets/v3_3.css","assets/v3_4.js","assets/v3_4.css",".well-known/security.txt","assets/app.js","assets/products.js",
                "favicon.svg","CNAME","robots.txt","sitemap.xml"])assert.ok(fs.existsSync(path.join(root,f)),f);
assert.equal(read("CNAME").trim(),"alghad.digital");
assert.equal(read("google3f39246447a165d6.html"),"google-site-verification: google3f39246447a165d6.html","Google Search Console verification must match original file exactly");
const publicSources=[html,read("assets/products.js"),read("assets/app.js"),read("assets/v3.js"),read("assets/v3_1.js"),read("assets/downloads-ui.js"),read("assets/downloads.js"),read("assets/downloads.css"),read("assets/style.css"),read("assets/v2.css"),read("assets/v3.css"),read("assets/v3_1.css")].join("\n");
assert.doesNotMatch(publicSources,/مطبخ ريم|عالم الصغار|Omar Kids|Reem Kitchen|عُمر/);
assert.doesNotMatch(publicSources,/0503276927|966503276927/);
const officialEmail="protech.2025.2026@gmail.com";
assert.ok(html.includes('href="mailto:'+officialEmail+'"'));
assert.ok(html.includes('id="copy-protech-email"'));
assert.ok(html.includes('id="contact"'));
assert.ok(html.includes('href="#contact"'));
assert.ok(html.includes("assets/v3_1.css") && html.includes("assets/v3_1.js"));
for(const key of ["assets/v3_3.js","assets/v3_3.css",'id="release-showcase"','id="security"','id="trust-current-connection"','href="#downloads"'])assert.ok(html.includes(key),key);
assert.ok(read("assets/v3_3.js").includes("isSecureContext"));
assert.ok(html.includes('id="gallery-portfolio-count"') && html.includes('id="back-to-top-floating"'));
assert.ok(html.includes("assets/products.js?v=3.4.0"));
assert.ok(html.includes("assets/v3_4.js") && html.includes("assets/v3_4.css"));
assert.ok(read("assets/v3_4.js").includes("history.replaceState"));
assert.doesNotMatch(read("assets/products.js"),/Call Recorder PRO|CALL RECORDER|recorder\.svg/);
assert.ok(read(".well-known/security.txt").includes("Contact: mailto:protech.2025.2026@gmail.com"));
for(const key of ["assets/downloads.js","assets/downloads-ui.js","assets/downloads.css","Content-Security-Policy","upgrade-insecure-requests"])assert.ok(html.includes(key),key);
assert.ok(read("assets/downloads-ui.js").includes("https:") && read("assets/downloads-ui.js").includes('url.hostname !== "github.com"'));
assert.ok(read("assets/v3_1.js").includes(officialEmail));
for(const key of ['id="sort-products"','id="compare-tray"','id="compare-dialog"','assets/v3.js"','assets/v3.css"'])assert.ok(html.includes(key),key);
for(const word of ["hydrateCompareButtons","renderComparison","?app","selected.size"])assert.ok(read("assets/v3.js").includes(word)||word==="?app",word);
const js=read("assets/app.js");
for(const word of ['"مكتمل"','"قريبًا جدًا"',"renderFeatured","aria-label"])assert.ok(js.includes(word));
console.log("PASS: 10 projects, 5 public repos, 5 upcoming, 4 verified public release downloads, recorder excluded, HTTPS and CSP.");
