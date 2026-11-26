"use strict";
/* Owner-authorized WhatsApp contact, HTML CSP, and collision constraints. Node 22+. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=(p)=>fs.readFileSync(path.join(root,p),"utf8");
const sitemap=read("sitemap.xml");
const paths=[...sitemap.matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(paths.length,50);
assert.equal(new Set(paths).size,50);
const phone="966503276927",contactBase="https://wa.me/"+phone;
const cspRequired=[
  "default-src 'self'",
  "script-src 'self'",
  "script-src-attr 'none'",
  "style-src-elem 'self'",
  "frame-src 'none'",
  "worker-src 'self'",
  "manifest-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "upgrade-insecure-requests",
];
const programs=new Set(["smart-excel","stone","marble","reports","hr","kitchen","download","care","quotes","google-maps-reviews-tracker","protech-music","astool"]);
let programContacts=0;
for(const route of paths){
  const file=route.replace(/^\//,"")+"index.html",html=read(file);
  assert.equal((html.match(/class="protech-whatsapp-float"/g)||[]).length,1,route);
  assert.equal((html.match(/PROTECH_CONTACT_SAFE_BEGIN/g)||[]).length,1,route);
  assert.equal((html.match(/PROTECH_CONTACT_SAFE_END/g)||[]).length,1,route);
  assert.equal((html.match(/\/assets\/contact-safe\.css\?v=1/g)||[]).length,1,route);
  const href=html.match(/<a class="protech-whatsapp-float"\s+href="([^"]+)"/)?.[1];
  assert.ok(href,route);
  const url=new URL(href.replace(/&amp;/g,"&"));
  assert.equal(url.origin,"https://wa.me",route);
  assert.equal(url.pathname,"/"+phone,route);
  assert.equal(url.searchParams.size,1,route);
  assert.ok(url.searchParams.get("text")?.length>15,route);
  assert.ok(!href.includes("+"),"Link must use percent encoding: "+route);
  const normalized=route.startsWith("/en/")?route.slice(3):route;
  const item=normalized.match(/^\/programs\/([a-z0-9-]+)\/$/);
  if(item){
    assert.ok(programs.has(item[1]));
    programContacts++;
    assert.ok(url.searchParams.get("text").toLowerCase().includes("protech")||url.searchParams.get("text").includes("برنامج"),route);
  }
  assert.ok(html.includes('target="_blank" rel="noopener noreferrer"'),route);
  assert.ok(!html.includes("0503276927"),"Don't expose local-number variant");
  assert.ok(!/whatsapp:\/\/|api\.whatsapp\.com\/send/i.test(html));
  const matches=[...html.matchAll(/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/g)];
  assert.equal(matches.length,1,route);
  const csp=matches[0][1];
  for(const directive of cspRequired) assert.ok(csp.includes(directive),"CSP "+directive+" missing: "+route);
  assert.ok(!/script-src[^;]*unsafe-inline/.test(csp),route);
  assert.ok(!/\bstyle-src\s+[^;]*'unsafe-inline'/.test(csp),"Style elements still broadly inline: "+route);
  assert.ok(!csp.includes("frame-ancestors"),"Must not pretend frame-ancestors is effective in meta");
  assert.equal((html.match(/<link rel="canonical"/g)||[]).length,1,route);
}
assert.equal(programContacts,programs.size*2);
const css=read("assets/contact-safe.css");
assert.ok(css.includes("inset-inline-end")&&css.includes("safe-area-inset-bottom"));
assert.ok(css.includes("body.sitewide-search-open .protech-whatsapp-float"));
assert.ok(css.includes("body:has(dialog[open])"));
assert.ok(css.includes("@media (max-width: 600px)"));
assert.ok(css.includes("@media print"));
assert.ok(read("assets/site-search.css").includes("inset-inline-end"));
assert.ok(read("assets/v3_4.css").includes("inset-inline-start"));
const source=read("scripts/build_contact_security.py");
assert.ok(source.includes('SITEMAP_RE')&&source.includes('CSP_RE'));
assert.ok(!source.includes("eval("));
const flow=read(".github/workflows/update-tech-news.yml");
const order=["python scripts/build_program_experience.py","python scripts/build_contact_security.py","python scripts/build_site_search.py"];
for(const v of order)assert.ok(flow.includes(v),v);
for(let i=1;i<order.length;i++)assert.ok(flow.indexOf(order[i])>flow.indexOf(order[i-1]),"Workflow build order wrong");
assert.ok(flow.includes("node tests/contact-security-test.cjs"));
assert.ok(read("docs/HTTP_SECURITY_HEADERS.md").includes("GitHub Pages"));
assert.ok(read("docs/HTTP_SECURITY_HEADERS.md").includes("Strict-Transport-Security"));
console.log("CONTACT_AND_CSP_VERIFIED",JSON.stringify({pages:paths.length,waLinks:paths.length,programContexts:programContacts,cspPages:paths.length,collisionSafeCSS:true,httpHeadersPendingEdge:true}));
