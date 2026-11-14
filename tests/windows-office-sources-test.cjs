"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
for(const [rel,lang] of [["windows-office/index.html","ar"],["en/windows-office/index.html","en"]]){
 const page=read(rel), start=page.indexOf('<section id="windows-office-downloads"'),end=page.indexOf("</section>",start);
 assert.ok(start>=0&&end>start,rel+" missing section");
 const section=page.slice(start,end);
 assert.equal((section.match(/<article class="external-software-source">/g)||[]).length,7);
 assert.ok(section.includes("https://windowstan.com/")&&section.includes("https://windowstan.com/win/")&&section.includes("https://windowstan.com/microsoft-office/"));
 const microsoft=[...section.matchAll(/href="(https:\/\/(?:www\.microsoft\.com|support\.microsoft\.com)[^"]+)"/g)];
 assert.equal(microsoft.length,5);
 assert.ok(microsoft[0].index<section.indexOf("windowstan.com"));
 for(const m of microsoft)assert.ok(m[1].includes(lang==="ar"?"/ar-sa/":"/en-us/"));
 const a=[...section.matchAll(/<a\b([^>]+)>/g)].map(m=>m[1]);
 assert.equal(a.length,8);assert.ok(a.every(v=>v.includes('target="_blank"')&&v.includes('rel="noopener noreferrer')));
 assert.equal(a.filter(v=>v.includes("windowstan.com")&&v.includes("nofollow")).length,3);
 assert.ok(lang==="ar"?section.includes("غير تابع")&&section.includes("لا نضمن"):section.includes("third-party")&&section.includes("not a verified"));
 assert.ok(!/\.iso(?:\?|")|\.exe(?:\?|")/i.test(section));
 const route=lang==="ar"?"/windows-office/":"/en/windows-office/";
 assert.ok(page.includes('<link rel="canonical" href="https://alghad.digital'+route+'">'));
 assert.ok(page.includes(lang==="ar"?"برامج الويندوز والاوفيس":"Windows & Office Programs"));
 assert.equal((page.match(/<h1\b/g)||[]).length,1);
}
for(const rel of ["programs/index.html","en/programs/index.html"]){
 assert.ok(!read(rel).includes('id="windows-office-downloads"'),"Mixed source section: "+rel);
 assert.ok(!read(rel).includes("windowstan.com"),"Archive is not part of ProTech program listings: "+rel);
}
assert.ok(read("index.html").includes('href="/windows-office/" class="nav-link"'));
assert.ok(read("index.html").includes('href="windows-office/"'));
assert.ok(read("en/index.html").includes('href="/en/windows-office/"'));
assert.ok(!read("index.html").includes("programs/#windows-office-downloads"));
assert.ok(!read("index.html").includes("windows-office-catalog-shortcut"));
const sitemap=read("sitemap.xml");
assert.ok(sitemap.includes("<loc>https://alghad.digital/windows-office/</loc>"));
assert.ok(sitemap.includes("<loc>https://alghad.digital/en/windows-office/</loc>"));
assert.equal((sitemap.match(/<loc>/g)||[]).length,42);
assert.ok(read("scripts/build_seo.py").includes("render_windows_office()"));
assert.ok(read("scripts/build_en.py").includes("render_windows_office()"));
assert.ok(read(".github/workflows/update-tech-news.yml").includes("node tests/windows-office-sources-test.cjs"));
console.log("WINDOWS_OFFICE_SEPARATE_PASS: two indexable pages, 7 source categories, 5 Microsoft links and external archive, no catalog mixing");
