"use strict";
/* Product-first redesign proof: functional no-JS HTML, safe official releases,
 * transparent statuses, editorial news secondary, and crawlable support pages. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const load=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const html=load("index.html");
const sections=["home","products","downloads","about","featured","free-tools",
                "security","faq","news","contact"];
const positions=sections.map(id=>{
 const value=html.indexOf('id="'+id+'"');
 assert.ok(value>0,"Missing priority section "+id);
 return value;
});
for(let i=1;i<positions.length;i++) assert.ok(
 positions[i]>positions[i-1],
 "Product-first section order broken at "+sections[i]);
assert.ok(!html.includes('id="ai-news"'));
assert.ok(!html.includes('id="tech-companies"'));
assert.ok(!html.includes('id="car-news"'));
assert.ok(!html.includes('src="assets/industry-news.js"'));
assert.ok(!html.includes('src="assets/industry-news-data.js"'));
assert.ok(html.includes('href="/ai-news/"'));
assert.ok(html.includes('href="/tech-companies/"'));
assert.ok(html.includes('href="/cars/"'));
assert.ok(html.includes('href="assets/product-first.css"'));
assert.ok(!html.includes('name="keywords"'));
assert.ok(html.includes('href="/privacy/"')&&html.includes('href="/security/"'));
assert.ok(html.includes('href="/about/"'));
assert.ok(!html.includes("wa.me/966503276927"),"Do not expose private phone in public site");
assert.ok(html.includes('href="#contact" class="button button-sm button-primary header-cta"'));
assert.ok(!html.includes('info@alghad.digital'),"Do not publicize unconfigured domain email");
const marks=[
 ["PRODUCTS",8,"data-prerender-product"],
 ["DOWNLOADS",5,"data-prerender-release"],
 ["NEWS",4,'class="pre-news-row"']
];
for(const [part,count,needle] of marks){
 const start='<!-- PRE_RENDER_'+part+'_START -->',end='<!-- PRE_RENDER_'+part+'_END -->';
 const a=html.indexOf(start),b=html.indexOf(end);
 assert.ok(a>0&&b>a,"Missing "+part+" HTML fallback");
 const source=html.slice(a,b);
 assert.equal(source.split(needle).length-1,count,"Incorrect "+part+" fallback count");
}
const productBlock=html.slice(html.indexOf("<!-- PRE_RENDER_PRODUCTS_START -->"),
                              html.indexOf("<!-- PRE_RENDER_PRODUCTS_END -->"));
const releaseBlock=html.slice(html.indexOf("<!-- PRE_RENDER_DOWNLOADS_START -->"),
                              html.indexOf("<!-- PRE_RENDER_DOWNLOADS_END -->"));
assert.ok(productBlock.includes('Beta · نسخة عامة للتجربة'));
assert.ok(productBlock.includes('Beta · نسخة عامة للتجربة'));
assert.ok(!productBlock.includes('تنزيل المصدر ZIP'));
assert.ok(productBlock.includes('ProTechStoneManager_Setup_v2.0.0_UNSIGNED.exe'));
assert.ok(productBlock.includes('قريبًا'));
assert.ok(releaseBlock.includes('SHA-256'));
assert.equal((releaseBlock.match(/https:\/\/github\.com\/Abdealmalk007\//g)||[]).length,5);
assert.ok(!/\/releases\/tag\/untagged/.test(html),"No draft links");
assert.ok(!/\.apk[^"]*Debug/i.test(html),"Debug APK must not be promoted");
const appJS=load("assets/app.js");
assert.ok(appJS.includes('Beta · نسخة تجريبية'));
assert.ok(appJS.includes('مستودع منشور'));
for(const page of ["about/index.html","security/index.html","privacy/index.html"]){
 const code=load(page);
 assert.ok(code.includes('name="description"'));
 assert.ok(code.includes('link rel="canonical"'));
 assert.ok(code.includes('favicon.svg'));
 assert.ok(code.includes('og:image'));
}
const footer=html.slice(html.indexOf('product-first-footer-links'),html.indexOf('</footer>'));
assert.ok(footer.includes('/security/')&&footer.includes('/privacy/'));
const published=load("assets/downloads.js");
assert.ok(published.includes("Download-Anything-PRO"));
assert.ok(!html.includes("Call Recorder PRO"));
const yaml=load(".github/workflows/update-tech-news.yml");
assert.ok(yaml.includes('cron: "30 4 * * *"'));
assert.ok(yaml.includes('python scripts/prerender_home.py'));
assert.ok(yaml.includes('python scripts/build_support_pages.py'));
assert.ok(yaml.includes('node tests/product-first-test.cjs'));
assert.ok(yaml.includes('git add -- about/index.html security/index.html privacy/index.html'));
const facts=path.join(root,"assets/release-facts.json");
if(fs.existsSync(facts)){
 const f=JSON.parse(fs.readFileSync(facts,"utf8"));
 assert.equal(f.version,1);
 for(const [id,entry] of Object.entries(f.releases)){
  assert.ok(["stone","marble","hr","reports","download"].includes(id));
  assert.equal(entry.prerelease,true);
  assert.ok(Number.isFinite(Date.parse(entry.published_at)));
  for(const asset of entry.assets){
   assert.ok(asset.url.startsWith("https://github.com/Abdealmalk007/"));
   assert.ok(asset.sha256===null||/^[0-9a-f]{64}$/.test(asset.sha256));
  }
 }
}
console.log("PRODUCT_FIRST_QA_PASS HOME_ORDER="+sections.join(">")+" NO_JS_PRODUCTS=8 NO_JS_RELEASES=5 NO_JS_NEWS=4 SUPPORT=3");
