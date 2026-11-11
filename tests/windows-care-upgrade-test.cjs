"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),vm=require("node:vm"),path=require("node:path");
const root=path.resolve(__dirname,"..");
const source=(n)=>fs.readFileSync(path.join(root,n),"utf8");
const ctx={window:{}};
vm.runInNewContext(source("assets/products.js"),ctx,{timeout:1300});
vm.runInNewContext(source("assets/downloads.js"),ctx,{timeout:1300});
const p=ctx.window.AL_GHAD_PRODUCTS.find(x=>x.id==="care");
const d=ctx.window.AL_GHAD_DOWNLOADS.care;
assert.equal(p.version,"3.3.1");
assert.equal(d.version,"3.3.1");
assert.equal(p.status,"public");
assert.equal(d.channel,"preview");
assert.ok(d.release.endsWith("/v3.3.1-responsive-portable-preview"));
assert.equal(d.files.length,3);
assert.equal(d.files.filter(x=>x.recommended).length,1);
const EXE=d.files.find(x=>x.url.endsWith("/ProTech_Windows_Care_Setup.exe"));
const SETUP=d.files.find(x=>x.url.endsWith("/ProTech_Windows_Care_Installer_v3.3.1.exe"));
const ZIP=d.files.find(x=>x.url.endsWith("/ProTech_Windows_Care_Portable.zip"));
assert.ok(EXE&&SETUP&&ZIP);
assert.equal(EXE.bytes,99328);
assert.equal(SETUP.bytes,270336);
assert.equal(ZIP.bytes,89461);
for(const f of d.files)assert.ok(f.url.startsWith(p.github+"/releases/download/v3.3.1-responsive-portable-preview/"));
const facts=JSON.parse(source("assets/release-facts.json")).releases.care;
assert.equal(facts.version,"3.3.1");
assert.equal(facts.prerelease,true);
assert.equal(facts.assets.length,3);
for(const f of d.files){
 const remote=facts.assets.find(x=>x.url===f.url);
 assert.ok(remote&&remote.bytes===f.bytes&&/^[a-f0-9]{64}$/.test(remote.sha256));
}
const expected={
 "ProTech_Windows_Care_Setup.exe":"1eb1e61542c99a1a623177b63b10de47d4ea69e0e572e60453cf88aee903d419",
 "ProTech_Windows_Care_Installer_v3.3.1.exe":"0898f8de8d0db6f1f1b6ff540ccb9d0cfec7cfc1622239a2a10e2f98bf615e10",
 "ProTech_Windows_Care_Portable.zip":"272d2b353a1527bcb51ebbcccbb3c95ab64fdfcfdb247b20fed21c3d2cabb339"
};
for(const [name,sha] of Object.entries(expected)){
 assert.equal(facts.assets.find(x=>x.name===name).sha256,sha);
}
const routes=["index.html","en/index.html","programs/index.html","en/programs/index.html",
 "programs/care/index.html","en/programs/care/index.html","protech/index.html","en/protech/index.html"];
for(const route of routes){
 const html=source(route);
 assert.ok(html.includes("ProTechWindowsCare/releases/download/v3.3.1-responsive-portable-preview/"),route);
 assert.ok(!html.includes("ProTechWindowsCare/releases/download/v3.3.0-portable-preview/"),route);
 assert.ok(!html.includes("ProTechWindowsCare/releases/tag/v3.3.0-portable-preview"),route);
}
for(const route of ["programs/care/index.html","en/programs/care/index.html"]){
 const html=source(route);
 assert.ok(html.includes("/ProTech_Windows_Care_Installer_v3.3.1.exe"),route);
 assert.ok(html.includes("/ProTech_Windows_Care_Setup.exe"),route);
 assert.ok(html.includes("/ProTech_Windows_Care_Portable.zip"),route);
 assert.ok(html.includes("3.3.1"));
}
assert.ok(d.note.includes("NotSigned") && d.note.includes("VM"));
assert.ok(source("index.html").includes('href="/assets/site-search.css') || source("index.html").includes('/assets/site-search.css'));
assert.ok(source(".github/workflows/update-tech-news.yml").includes('cron: "30 4 * * *"'));
console.log("WINDOWS_CARE_V331_SITE_RELEASE_TEST_PASS",JSON.stringify({version:"3.3.1",variants:3,sha256Verified:3,routeCount:routes.length}));
