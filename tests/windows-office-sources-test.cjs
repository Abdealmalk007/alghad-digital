"use strict";
/* Bilingual OS/Office source listings: official-first, external provenance, no binaries hosted here. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const load=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const cases=[["programs/index.html","ar"],["en/programs/index.html","en"]];
for (const [rel,lang] of cases){
  const page=load(rel);
  const start=page.indexOf('<section id="windows-office-downloads"');
  const end=page.indexOf("</section>",start);
  assert.ok(start>=0 && end>start,rel+" missing Windows/Office section");
  const section=page.slice(start,end);
  assert.equal((section.match(/<article class="external-software-source">/g)||[]).length,7,rel+" source count");
  assert.ok(section.includes("https://windowstan.com/"),"Supplied website must be linked");
  assert.ok(section.includes("https://windowstan.com/win/"));
  assert.ok(section.includes("https://windowstan.com/microsoft-office/"));
  const officialLinks=[...section.matchAll(/href="(https:\/\/(?:www\.microsoft\.com|support\.microsoft\.com)[^"]+)"/g)];
  assert.equal(officialLinks.length,5,rel+" must prioritize five official pages");
  assert.ok(officialLinks[0].index < section.indexOf("windowstan.com"),"Microsoft links must precede archives");
  for(const url of officialLinks.map(v=>v[1])){
    assert.ok(lang==="ar"? url.includes("/ar-sa/") : url.includes("/en-us/"),rel+" wrong locale: "+url);
  }
  const anchors=[...section.matchAll(/<a\b([^>]+)>/g)].map(v=>v[1]);
  assert.equal(anchors.length,8,"Seven resource cards plus the requested Windowstan home");
  assert.ok(anchors.every(x=>x.includes('target="_blank"') && x.includes('rel="noopener noreferrer')));
  assert.equal(anchors.filter(x=>x.includes("windowstan.com") && x.includes("nofollow")).length,3);
  assert.ok(section.includes("Windows 11") && section.includes("Windows 10")
      && section.includes("Office 2024") && section.includes("Office 2021"));
  assert.ok(lang==="ar" ? section.includes("غير تابع") && section.includes("لا نضمن") :
                           section.includes("third-party") && section.includes("not a verified"));
  assert.ok(!/\.iso(?:\?|")|\.exe(?:\?|")/i.test(section),
            "Only provider landing pages, not unverified binary links or activation bypasses");
}
assert.ok(load("index.html").includes('href="programs/#windows-office-downloads"'),
          "Homepage software directory should link to source section");
const source=load("scripts/software_sources.py");
assert.ok(source.includes("SOURCES=") && source.includes('if lang not in {"ar","en"}'));
assert.ok(load("scripts/build_seo.py").includes('render_software_sources("ar")'));
assert.ok(load("scripts/build_en.py").includes('render_software_sources("en")'));
const workflow=load(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes("node tests/windows-office-sources-test.cjs"),
          "Daily rebuild must verify external source block");
console.log("WINDOWS_OFFICE_SOURCES_PASS: 5 Microsoft pages, 2 Windowstan category links, 1 Windowstan homepage, AR/EN provenance labels");
