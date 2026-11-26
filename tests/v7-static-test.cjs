"use strict";
const assert=require("node:assert/strict"),fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto"),cp=require("node:child_process");
const root=path.resolve(__dirname,".."),read=f=>fs.readFileSync(path.join(root,f),"utf8").replace(/\r\n/g,"\n");
const refs=[...read("sitemap.xml").matchAll(/<loc>https:\/\/alghad\.digital\/([^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(refs.length,50);
for(const route of refs){
 const h=read(route+"index.html");
 assert.equal((h.match(/V7_ASSETS_BEGIN/g)||[]).length,1);
 assert.equal((h.match(/V7_BOOT_BEGIN/g)||[]).length,1);
 assert.ok(h.includes("/assets/fonts/plex.css?v=5.3.1")&&h.includes("/assets/v7.css?v=7.0.0"));
 const boot=h.match(/<script id="v7-theme-bootstrap">([\s\S]*?)<\/script>/)?.[1];
 assert.equal(boot,read("assets/v7-theme.js").trim());
 const hash="'sha256-"+crypto.createHash("sha256").update(boot).digest("base64")+"'";
 const csp=h.match(/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/)?.[1];
 assert.ok(csp.includes("script-src 'self' "+hash));
 if(csp.includes("script-src-elem"))assert.ok(csp.includes("script-src-elem 'self' "+hash));
 assert.ok(!/script-src[^;]*unsafe-inline/.test(csp));
 assert.ok(h.indexOf("Content-Security-Policy")<h.indexOf("v7-theme-bootstrap"));
 assert.ok(h.indexOf("v7-theme-bootstrap")<h.indexOf('rel="stylesheet"'));
 assert.ok(h.includes("worker-src 'self'"));
 assert.ok(h.includes('rel="canonical"'));
 assert.ok(h.includes('lang="'+(route.startsWith("en/")?"en":"ar")+'"'));
}
assert.equal(read("favicon.svg").trim(),read("assets/brand/dawn-g.svg").trim());
assert.ok(read("assets/fonts/OFL-LICENSE.txt").includes("SIL OPEN FONT LICENSE"));
for(const w of [400,500,600,700])for(const s of ["arabic","latin","latin-ext"]){const file="assets/fonts/optimized/ibm-plex-sans-arabic-"+s+"-"+w+"-normal.woff2";assert.equal(fs.readFileSync(path.join(root,file)).toString("ascii",0,4),"wOF2");assert.ok(read("assets/fonts/plex.css").includes(file));const original=file.replace("/optimized/","/");assert.ok(fs.statSync(path.join(root,file)).size<fs.statSync(path.join(root,original)).size)}
assert.equal(JSON.parse(read("site.webmanifest")).display,"standalone");
assert.ok(read("sw.js").includes('r.method!=="GET"'));assert.ok(read("sw.js").includes('u.origin!==self.location.origin'));assert.ok(read("sw.js").includes('authorization'));
assert.ok(read("offline.html").includes('content="noindex"'));
assert.ok(read("index.html").includes("تقنيات اليوم.")&&read("en/index.html").includes("Tomorrow’s solutions."));
console.log("V7_STATIC_PASS pages="+refs.length+" fontWeights=4 offline=bounded");
