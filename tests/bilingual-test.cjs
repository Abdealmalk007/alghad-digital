"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const domain="https://alghad.digital";
const routes=["/","/programs/","/news/","/free-windows-tools/","/ai-news/",
 "/tech-companies/","/cars/","/about/","/security/","/privacy/","/protech/",
 ...["smart-excel","stone","marble","reports","hr","kitchen","download","care","quotes"].map(x=>"/programs/"+x+"/")];
assert.equal(routes.length,20);
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const english=[];
const arabic=[];
for(const route of routes){
  const relative=route.slice(1);
  const a=read((relative||"")+"index.html");
  const e=read("en/"+relative+"index.html");
  const arUrl=domain+route;
  const enUrl=domain+"/en/"+relative;
  assert.ok(a.includes('<html lang="ar" dir="rtl">'),"Arabic RTL: "+route);
  assert.ok(e.includes('<html lang="en" dir="ltr">'),"English LTR: "+route);
  assert.ok(a.includes('hreflang="ar" href="'+arUrl+'"'),"Arabic hreflang ar "+route);
  assert.ok(a.includes('hreflang="en" href="'+enUrl+'"'),"Arabic hreflang en "+route);
  assert.ok(e.includes('hreflang="en" href="'+enUrl+'"'),"English hreflang en "+route);
  assert.ok(e.includes('hreflang="ar" href="'+arUrl+'"'),"English hreflang ar "+route);
  assert.ok(e.includes('hreflang="x-default" href="'+arUrl+'"'),"x-default Arabic "+route);
  assert.ok(a.includes('<link rel="canonical" href="'+arUrl+'">'),"Arabic canonical "+route);
  assert.ok(e.includes('<link rel="canonical" href="'+enUrl+'">'),"English canonical "+route);
  assert.ok(e.includes('href="'+arUrl+'" hreflang="ar"'),"AR switch backlink "+route);
  assert.ok(a.includes('href="'+enUrl+'"'),"EN switch hyperlink "+route);
  assert.ok(e.includes('class="en-lang-switch"'),"Visible AR button "+route);
  assert.ok(a.includes('class="lang-toggle"'),"Visible EN button "+route);
  const heading=(e.match(/<h1\b[^>]*>([\s\S]*?)<\/h1>/g)||[]);
  assert.equal(heading.length,1,"Single EN H1 "+route);
  assert.ok(e.includes('name="description"'),"EN description "+route);
  assert.ok(!e.includes('name="keywords"'),"No obsolete SEO keywords "+route);
  assert.ok(!/Call Recorder PRO|Kids App Omar|Reem Recipes/.test(e),"Excluded projects stay excluded");
  assert.ok(e.includes('property="og:locale" content="en_US"'));
  assert.ok(e.includes('href="/assets/en.css"'));
  assert.ok(e.includes('src="/icon-192.png?v=4"'));
  assert.ok(e.includes('mailto:protech.2025.2026@gmail.com'));
  english.push(e);
  arabic.push(a);
}
assert.equal(english.length,20);
const homepage=english[0];
assert.ok(homepage.indexOf('id="programs"')<homepage.indexOf('id="news"'),"Product-first English homepage");
assert.ok(homepage.includes('id="downloads"'));
assert.ok(homepage.indexOf('id="downloads"')<homepage.indexOf('id="news"'),"Downloads before news");
assert.equal((homepage.match(/class="en-product-card" data-product=/g)||[]).length,9,"9 full English product cards");
assert.equal((homepage.match(/class="en-release-card"/g)||[] ).length,8,"8 verified preview download choices");
assert.equal((english[10].match(/class="en-product-card" data-product=/g)||[]).length,9,"All programs on EN ProTech profile");
assert.ok(homepage.includes('id="en-search"'),"English search");
assert.ok(homepage.includes('data-en-filter="public"'),"English filter");
assert.ok(!english.some(s=>s.includes("href=\"#"))||homepage.includes('href="#downloads"'));
// Validate all EN release assets are official and approved. Never publish guessed files.
const releaseUrls=(homepage.match(/https:\/\/github\.com\/Abdealmalk007\/[^" ]+\/releases\/download\/[^"]+/g)||[]);
assert.equal(new Set(releaseUrls).size,8,"Eight unique published download files; release links may be repeated in cards");
for(const u of releaseUrls)assert.match(u,/^https:\/\/github\.com\/Abdealmalk007\/[A-Za-z0-9_.-]+\/releases\/download\/[^"<> ]+$/);
// Product pages with no release must not offer made-up buttons.
for(const slug of ["kitchen"]){
  const page=read("en/programs/"+slug+"/index.html");
  assert.ok(!page.includes('class="en-download-item"'),"No fake downloads "+slug);
}
for(const slug of ["stone","download","hr","marble","reports","quotes","care"]){
  const page=read("en/programs/"+slug+"/index.html");
  assert.ok(page.includes('class="en-download-item"'),"Real release variants "+slug);
}
const sitemap=read("sitemap.xml");
assert.equal((sitemap.match(/<loc>/g)||[]).length,40);
for(const route of routes){
  assert.ok(sitemap.includes("<loc>"+domain+route+"</loc>"));
  assert.ok(sitemap.includes("<loc>"+domain+"/en/"+route.slice(1)+"</loc>"));
}
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'),"Keep 7:30 daily job");
assert.ok(workflow.includes("python scripts/build_en.py"),"Daily rebuild EN");
assert.ok(workflow.includes("node tests/bilingual-test.cjs"),"Daily bilingual QA");
assert.ok(workflow.includes("git add -- en/"),"Daily stage of English content");
const publisher=read("Publish_To_GitHub.ps1");
assert.ok(publisher.includes("scripts/build_en.py"));
assert.ok(publisher.includes("tests/bilingual-test.cjs"));
assert.ok(publisher.includes("$englishPages.Count -ne 22"));
const css=read("assets/en.css");
assert.ok(css.includes(".en-lang-switch"));
const src=read("assets/en.js");
assert.ok(src.includes('data-en-filter')||src.includes("dataset.enFilter"));
console.log("BILINGUAL_QA_PASS AR=20 EN=20 TOTAL_SITEMAP=40 REAL_DOWNLOADS=8 ARABIC_DEFAULT=yes");
