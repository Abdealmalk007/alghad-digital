"use strict";
/* Bilingual benefits, email-only contact, and safe recurring site generation. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const urls=[...read("sitemap.xml").matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(urls.length,40);
assert.equal(new Set(urls).size,40);
const ctx={window:{}};
vm.runInNewContext(read("assets/products.js"),ctx,{timeout:1000});
const products=ctx.window.AL_GHAD_PRODUCTS;
assert.equal(products.length,9);
const email="protech.2025.2026@gmail.com";
const css='/assets/program-experience.css?v=1';
for(const route of urls){
  const file=route.replace(/^\//,"")+"index.html";
  const html=read(file);
  assert.equal(html.split(css).length-1,1,"Experience CSS not included once: "+file);
  assert.doesNotMatch(html,/(?:https?:\/\/)?wa\.me\/|protech-whatsapp-float|protech-program-whatsapp|PROTECH_WHATSAPP_BEGIN|0503276927|966503276927/,
                      "Personal phone or WhatsApp contact remains in "+file);
  assert.equal((html.match(/<link rel="canonical"/g)||[]).length,1);
  assert.ok(html.includes('href="mailto:'+email),file+" missing email contact");
}
for(const product of products){
  for(const lang of ["ar","en"]){
    const page=(lang==="en"?"en/":"")+"programs/"+product.id+"/index.html";
    const html=read(page);
    assert.equal(html.split("PROTECH_PROGRAM_EXPERIENCE_BEGIN").length-1,1,page);
    assert.equal(html.split("PROTECH_PROGRAM_EXPERIENCE_END").length-1,1,page);
    assert.equal((html.match(/<article class="protech-benefit-card">/g)||[]).length,4,page);
    const cta=html.match(/<a class="protech-program-email" href="([^"]+)"[^>]*>/);
    assert.ok(cta,"Missing email-only CTA: "+page);
    assert.ok(cta[1].startsWith("mailto:"+email+"?subject="),page);
    assert.ok(decodeURIComponent(cta[1].split("?subject=")[1]).includes(product.title),page);
    assert.ok(html.includes(lang==="ar"?"كيف سيفيدك ":"What will you gain from "));
  }
}
const cssSource=read("assets/program-experience.css");
assert.ok(cssSource.includes(".protech-program-email")&&cssSource.includes(".protech-benefit-grid"));
assert.doesNotMatch(cssSource,/whatsapp/i);
const generator=read("scripts/build_program_experience.py");
assert.ok(generator.includes("mailto:")&&generator.includes("email_link("));
assert.doesNotMatch(generator,/https:\/\/wa\.me|0503276927|966503276927/);
const backCss=read("assets/v3_4.css");
const backJs=read("assets/v3_4.js");
const searchCss=read("assets/site-search.css");
assert.ok(backCss.includes("inset-inline-start:")&&searchCss.includes("inset-inline-end:"),
          "Search and back-to-top must anchor to opposite logical edges in RTL/LTR");
assert.ok(backCss.includes("body.sitewide-search-open .back-to-top-floating"));
assert.ok(backJs.includes("searchOpen")&&backJs.includes("getBoundingClientRect()"),
          "Back to top must hide during search and check visual collision");
const workflow=read(".github/workflows/update-tech-news.yml");
for(const required of ['cron: "30 4 * * *"','python scripts/build_program_experience.py',
                       'node tests/program-experience-test.cjs','python scripts/build_site_search.py']){
  assert.ok(workflow.includes(required),"Daily rebuild cannot regress: "+required);
}
console.log("EMAIL_ONLY_EXPERIENCE_PASS",JSON.stringify({pages:urls.length,products:18,benefitCards:72,emailCtas:18,phoneLinks:0,searchBackCollisionGuard:true}));
