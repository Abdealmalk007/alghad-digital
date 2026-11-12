"use strict";
/* Static, bilingual benefits + WhatsApp contact regression checks.
   Node 22+, no external libraries. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const urlMap=[...read("sitemap.xml").matchAll(/<loc>https:\/\/alghad\.digital(\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(urlMap.length,40);
assert.equal(new Set(urlMap).size,40);
const context={window:{}};
vm.runInNewContext(read("assets/products.js"),context,{timeout:1000});
const products=context.window.AL_GHAD_PRODUCTS;
assert.equal(products.length,9);
const phone="966503276927";
const paths=["index.html","en/index.html"];
const exactCss='/assets/program-experience.css?v=1';
function anchors(html) {
  return [...html.matchAll(/<a\b[^>]*class="([^"]*\bprotech-(?:whatsapp-float|program-whatsapp)\b[^"]*)"[^>]*href="([^"]+)"[^>]*>/g)];
}
for(const url of urlMap){
 const file=url.replace(/^\//,"")+"index.html";
 const html=read(file);
 assert.equal(html.split(exactCss).length-1,1,"CSS present once "+file);
 assert.equal(html.split("PROTECH_WHATSAPP_BEGIN").length-1,1,"floating WhatsApp once "+file);
 assert.equal(html.split("PROTECH_WHATSAPP_END").length-1,1,"floating WhatsApp ends once "+file);
 const float=html.match(/<a class="protech-whatsapp-float" href="([^"]+)"[^>]*>/);
 assert.ok(float,"Missing WhatsApp contact "+file);
 assert.ok(float[1].startsWith("https://wa.me/"+phone+"?text="),"Incorrect phone "+file);
 assert.ok(float[1].includes("%"),"Pre-filled message must be encoded");
 assert.ok(html.includes('target="_blank" rel="noopener noreferrer"'),"External link safety "+file);
 assert.equal((html.match(/<link rel="canonical"/g)||[]).length,1,"Preserve canonical SEO "+file);
}
for(const p of products){
 const slug=p.id;
 for(const lang of ["ar","en"]){
  const filename=(lang==="en"?"en/":"")+"programs/"+slug+"/index.html";
  const html=read(filename);
  assert.equal(html.split("PROTECH_PROGRAM_EXPERIENCE_BEGIN").length-1,1,"Exactly one benefit section "+filename);
  assert.equal(html.split("PROTECH_PROGRAM_EXPERIENCE_END").length-1,1);
  const cards=html.match(/<article class="protech-benefit-card">/g)||[];
  assert.equal(cards.length,4,"Four user outcomes "+filename);
  const programWhatsapp=html.match(/<a class="protech-program-whatsapp" href="([^"]+)"[^>]*>/);
  assert.ok(programWhatsapp,"Missing specific WhatsApp CTA "+filename);
  const link=programWhatsapp[1];
  assert.ok(link.startsWith("https://wa.me/"+phone+"?text="));
  const message=decodeURIComponent(link.split("?text=")[1].split("&")[0]);
  assert.ok(message.includes(p.title),"WhatsApp prefill must name product "+filename);
  assert.ok((html.match(/<h3>/g)||[]).length>=4,"Benefit headings "+filename);
  if(lang==="ar"){
   assert.ok(html.includes("كيف سيفيدك "+p.title.replaceAll("&","&amp;")+"؟"));
   assert.ok(html.includes("مميزات "+p.title.replaceAll("&","&amp;")));
  } else {
   assert.ok(html.includes("What will you gain from "+p.title.replaceAll("&","&amp;")+"?"));
   assert.ok(html.includes("Key capabilities"));
  }
  if(slug==="kitchen")assert.ok(html.includes(lang==="ar"?"قيد التطوير — فوائد مستهدفة":"In development — planned outcomes"));
  else assert.ok(html.includes(lang==="ar"?"إصدار تجريبي — اختبر قبل الاعتماد":"Preview release — test before production"));
  // User-visible benefit claims must not contain invented guaranteed savings.
  assert.ok(!html.includes("وفر 90%")&&!html.includes("save 90%"));
 }
}
const style=read("assets/program-experience.css");
assert.ok(style.includes(".protech-benefit-grid")&&style.includes(".protech-whatsapp-float"));
assert.ok(style.includes("@media (max-width: 700px)"));
assert.ok(style.includes("prefers-reduced-motion"));
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'));
assert.ok(workflow.includes("python scripts/build_program_experience.py"));
assert.ok(workflow.includes("node tests/program-experience-test.cjs"));
assert.ok(workflow.indexOf("scripts/build_program_experience.py")>workflow.indexOf("scripts/build_topic_tags.py"));
assert.ok(workflow.indexOf("scripts/build_site_search.py")>workflow.indexOf("scripts/build_program_experience.py"));
console.log("PROGRAM_EXPERIENCE_PASS",JSON.stringify({pages:urlMap.length,programPages:18,benefitCards:72,whatsappLinks:58,phone,locales:["ar","en"]}));
