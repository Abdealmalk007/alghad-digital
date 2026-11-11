"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const home=read("index.html");
const brand=read("protech/index.html");
const siteUrl="https://alghad.digital/";

const block=home.match(/<!-- SEO JSONLD START --><script type="application\/ld\+json">(.*?)<\/script><!-- SEO JSONLD END -->/s);
assert.ok(block,"Official site identity data must be in source HTML");
const graph=JSON.parse(block[1])["@graph"];
assert.equal(graph.length,2);
const website=graph.find(x=>x["@type"]==="WebSite");
const org=graph.find(x=>x["@type"]==="Organization");
assert.ok(website&&org);
assert.equal(website.name,"الغد ديجتال");
assert.equal(website.url,siteUrl);
assert.ok(website.alternateName.includes("Alghad Digital"));
assert.ok(website.alternateName.includes("جيل الغد"));
assert.equal(org.name,"ProTech");
assert.ok(org.alternateName.includes("Pro Tech"));
assert.ok(org.alternateName.includes("بروتك"));
assert.equal(org.url,siteUrl+"protech/");
assert.equal(website.publisher["@id"],org["@id"]);
assert.ok(org.sameAs.includes("https://github.com/Abdealmalk007"));
assert.equal((home.match(/"@type":"WebSite"/g)||[]).length,1,"Unique official site identity");
assert.ok(home.includes('href="protech/"'),"Homepage contains developer link");
assert.ok(home.includes("جيل الغد"),"Search alias must appear visibly, not only in schema");
assert.ok(home.includes("بروتك"));
assert.ok(home.includes('<meta name="description"'));
assert.ok(!home.includes('name="keywords"'));
assert.ok(!/Call Recorder PRO|مطبخ ريم|برنامج عمر/.test(home));
const title=home.match(/<title>(.*?)<\/title>/s)?.[1]||"";
assert.ok(title.startsWith("الغد ديجتال"));
assert.ok(title.includes("Pro Tech"));
assert.ok(title.length<80);

assert.match(brand,/<h1>Pro Tech \(بروتك\) — برامج الغد ديجتال<\/h1>/);
assert.match(brand,/<link rel="canonical" href="https:\/\/alghad\.digital\/protech\/">/);
assert.equal((brand.match(/class="directory-card brand-product-card"/g)||[]).length,8);
assert.equal((brand.match(/إصدار Beta\/Preview متاح للتنزيل/g)||[]).length,6);
assert.ok(brand.includes("جيل الغد"));
assert.ok(brand.includes("mailto:protech.2025.2026@gmail.com"));
const brandMarkup=brand.match(/<script type="application\/ld\+json">(.*?)<\/script>/s);
const brandSchema=JSON.parse(brandMarkup[1]);
assert.equal(brandSchema["@type"],"AboutPage");
assert.equal(brandSchema.mainEntity.name,"ProTech");

const intents={
  stone:"برنامج إدارة الرخام والبورسلان",
  marble:"برنامج إدارة وتسليم أعمال الرخام",
  reports:"برنامج تقارير العمل اليومية",
  hr:"برنامج إدارة الموارد البشرية والموظفين",
  download:"تطبيق تحميل الفيديو والصوت للأندرويد",
  kitchen:"برنامج تصميم المطابخ ثنائي وثلاثي الأبعاد",
  care:"برنامج صيانة وتحسين نظام Windows",
  quotes:"برنامج عروض الأسعار والعقود"
};
for(const [slug,intent] of Object.entries(intents)){
  const code=read("programs/"+slug+"/index.html");
  const meta=code.match(/<meta name="description" content="(.*?)"/s)?.[1]||"";
  const pagetitle=code.match(/<title>(.*?)<\/title>/s)?.[1]||"";
  assert.ok(pagetitle.includes(intent),slug+" unique search title");
  assert.ok(meta.includes(intent),slug+" unique search description");
  assert.ok(code.includes("من يبحث عن "+intent),slug+" user-facing search intent");
  assert.ok(code.includes("ProTech"),slug+" developer link");
  assert.ok(brand.includes('href="../programs/'+slug+'/"'),slug+" developer page link");
  assert.ok(code.includes('href="../../protech/"'),slug+" product pages crosslink to developer");
}
const sitemap=read("sitemap.xml");
const total=(sitemap.match(/<loc>/g)||[]).length;
assert.equal(total,38,"19 Arabic and 19 English canonical pages included in sitemap");
assert.ok(sitemap.includes("<loc>https://alghad.digital/en/protech/</loc>"));
assert.ok(sitemap.includes("<loc>https://alghad.digital/protech/</loc>"));
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes('cron: "30 4 * * *"'),"Preserve 7:30 Riyadh news update");
assert.ok(workflow.includes("node tests/brand-seo-test.cjs"),"Automatic SEO regression verification");
assert.ok(workflow.includes("protech/index.html"),"Automated brand page update");
const publisher=read("Publish_To_GitHub.ps1");
assert.ok(publisher.includes("protech/index.html"));
assert.ok(publisher.includes("tests/brand-seo-test.cjs"));
console.log("BRAND_SEARCH_SEO_PASS PAGES="+total+" BRAND_LINKS=10 VERIFIED_DOWNLOADS=6 ALIASES=ProTech,Pro Tech,بروتك,جيل الغد");
