"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const hosts=new Set(["officecdn.microsoft.com","software-static.download.prss.microsoft.com"]);
const urls=[];
for(const [rel,lang] of [["windows-office/index.html","ar"],["en/windows-office/index.html","en"]]){
 const html=read(rel);
 const start=html.indexOf('<section id="windows-office-downloads"');
 const end=html.indexOf("</section>",start);
 assert.ok(start>=0&&end>start,rel);
 const section=html.slice(start,end);
 assert.equal((section.match(/class="external-software-source microsoft-direct-source"/g)||[]).length,4);
 const anchors=[...section.matchAll(/<a\b([^>]+)>/g)].map(x=>x[1]);
 assert.equal(anchors.length,8,rel);
 const hrefs=anchors.map(x=>x.match(/href="([^"]+)"/)?.[1]);
 assert.equal(new Set(hrefs).size,8);
 const counts={ar:0,en:0,iso:0,img:0};
 for(let i=0;i<anchors.length;i++){
  const attrs=anchors[i],url=new URL(hrefs[i]);
  assert.equal(url.protocol,"https:");
  assert.ok(hosts.has(url.hostname),"Non-official host: "+url.hostname);
  assert.ok(!url.search&&!url.hash);
  assert.ok(/\.(iso|img)$/i.test(url.pathname));
  assert.ok(attrs.includes("microsoft-direct-file")&&attrs.includes("data-download-language"));
  assert.ok(!attrs.includes('target="_blank"'));
  const langTag=attrs.match(/data-download-language="(ar|en)"/)?.[1];
  assert.ok(langTag);counts[langTag]++;
  const type=url.pathname.toLowerCase().endsWith(".iso")?"iso":"img";
  assert.ok(attrs.includes('data-microsoft-file="'+type+'"'));
  counts[type]++;
  assert.equal(url.hostname,type==="iso"?"software-static.download.prss.microsoft.com":"officecdn.microsoft.com");
  urls.push(hrefs[i]);
 }
 assert.deepEqual(counts,{ar:4,en:4,iso:2,img:6},rel);
 for(const name of ["Home2024Retail.img","ProPlus2024Retail.img","ProPlus2021Retail.img","25H2"])assert.ok(section.includes(name),name);
 assert.ok(section.includes(lang==="ar"?"تنزيل عربي":"Download Arabic"));
 assert.ok(section.includes(lang==="ar"?"تنزيل إنجليزي":"Download English"));
 assert.ok(section.includes(lang==="ar"?"13 أكتوبر 2026":"October 13, 2026"));
 assert.ok(!/windowstan|https:\/\/(?:www\.microsoft\.com|support\.microsoft\.com)/i.test(html));
 assert.ok(html.includes('<link rel="stylesheet" href="/assets/microsoft-direct.css?v=1">'));
 assert.equal((html.match(/<h1\b/g)||[]).length,1);
 const route=lang==="ar"?"/windows-office/":"/en/windows-office/";
 assert.ok(html.includes('<link rel="canonical" href="https://alghad.digital'+route+'">'));
}
assert.deepEqual(urls.slice(0,8),urls.slice(8));
for(const f of ["scripts/software_sources.py","scripts/build_seo.py","scripts/build_en.py","assets/site-search-index.js"]){
 assert.ok(!read(f).toLowerCase().includes("windowstan"),f);
}
for(const f of ["programs/index.html","en/programs/index.html"])assert.ok(!read(f).includes('id="windows-office-downloads"'));
assert.ok(read("index.html").includes('href="/windows-office/"'));
assert.ok(read("en/index.html").includes('href="/en/windows-office/"'));
const sitemap=read("sitemap.xml");
assert.equal((sitemap.match(/<loc>/g)||[]).length,42);
assert.ok(sitemap.includes("<loc>https://alghad.digital/windows-office/</loc>"));
assert.ok(sitemap.includes("<loc>https://alghad.digital/en/windows-office/</loc>"));
assert.ok(read(".github/workflows/update-tech-news.yml").includes("node tests/windows-office-sources-test.cjs"));
assert.ok(read(".github/workflows/update-tech-news.yml").includes("python scripts/check_microsoft_media_health.py"));
assert.ok(read("scripts/check_microsoft_media_health.py").includes("method=\"HEAD\""));
assert.ok(read("assets/microsoft-direct.css").includes("@media (max-width: 460px)"));
console.log("MICROSOFT_OFFICIAL_DIRECT_MEDIA_PASS",JSON.stringify({pages:2,buttonsPerPage:8,categories:4,iso:2,img:6,thirdParty:0,externalLandingPages:0}));
