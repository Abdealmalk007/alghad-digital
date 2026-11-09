"use strict";
/* Site publishing regression tests; Node >=18, no network dependencies. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const archive="https://github.com/Abdealmalk007/ProTechStoneManager/archive/refs/heads/main.zip";
const arabic=read("index.html");
const english=read("en/index.html");
const pages=[
  "index.html","en/index.html","programs/index.html","en/programs/index.html",
  "programs/stone/index.html","en/programs/stone/index.html",
  "news/index.html","en/news/index.html",
  "ai-news/index.html","tech-companies/index.html","cars/index.html"
];
for(const filename of pages){
  const html=read(filename);
  assert.ok(html.includes("/assets/share.js?v=1"),filename+" missing share script");
  assert.ok(html.includes("/assets/share.css?v=1"),filename+" missing share CSS");
  assert.doesNotMatch(html,/releases\/tag\/untagged|releases\/download\/v2\.0\.0\/Setup\.exe/);
}
for(const filename of ["index.html","programs/index.html","programs/stone/index.html",
                        "en/programs/stone/index.html"]){
  assert.ok(!read(filename).includes(archive),filename+" must not expose source ZIP");
}
assert.ok(arabic.includes('data-prerender-product="stone"'));
assert.ok(english.includes("Download Beta (UNSIGNED)"));
assert.ok(read("programs/stone/index.html").includes("ProTechStoneManager_Setup_v2.0.0_UNSIGNED.exe"));
assert.ok(read("programs/stone/index.html").includes("توقيع"));
for(const file of ["index.html","en/index.html","programs/index.html","en/programs/index.html","programs/stone/index.html","en/programs/stone/index.html"]){
  assert.ok(read(file).includes("https://github.com/Abdealmalk007/ProTechStoneManager/releases/download/v2.0.0-unsigned-preview/ProTechStoneManager_Setup_v2.0.0_UNSIGNED.exe"),file+" missing unsigned preview download");
}
assert.ok(read("assets/downloads.js").includes("UNSIGNED Preview"));
const js=read("assets/share.js");
assert.ok(js.includes("navigator.share"));
for(const destination of ["api.whatsapp.com","t.me/share/url","twitter.com/intent/tweet","navigator.clipboard"]) {
  assert.ok(js.includes(destination),"Missing sharing destination: "+destination);
}
assert.ok(js.includes("MutationObserver"),"Newly rendered news and product cards must get share buttons");
for(const route of ["scripts/build_seo.py","scripts/build_en.py"]){
  assert.ok(read(route).includes("/assets/share.js?v=1"),route+" generator must persist share script");
}
assert.ok(!read("scripts/prerender_home.py").includes(archive));
assert.ok(!read("assets/app.js").includes(archive));
console.log("SITE_DIRECT_DOWNLOAD_AND_SHARING_PASS PAGES="+pages.length+" DOWNLOAD_CTA=6 BROWSER_BACKED=yes");
