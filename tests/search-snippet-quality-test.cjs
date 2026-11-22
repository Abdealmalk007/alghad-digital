"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const sitemap=fs.readFileSync(path.join(root,"sitemap.xml"),"utf8");
const urls=[...sitemap.matchAll(/<loc>(https:\/\/alghad\.digital\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(urls.length,46);
let descriptions=0,titles=0,headings=0,social=0;
for(const url of urls){
  const rel=url.replace("https://alghad.digital/","")+"index.html";
  const html=fs.readFileSync(path.join(root,rel),"utf8");
  const title=html.match(/<title>([^<]+)<\/title>/i)?.[1].replaceAll("&amp;","&");
  const description=html.match(/<meta name="description" content="([^"]*)"/i)?.[1];
  assert.ok(title && title.length<=64,"Title length: "+rel+" "+title?.length);
  assert.ok(description && description.length<=160,"Description length: "+rel+" "+description?.length);
  assert.match(html,/<link rel="canonical" href="/);
  titles++;descriptions++;
  if(html.includes('property="og:description"')){
    const og=html.match(/<meta property="og:description" content="([^"]*)"/i)?.[1];
    assert.equal(og,description,"Inconsistent OG description: "+rel);
    social++;
  }
  if(/^en\/(ai-news|cars|free-windows-tools|tech-companies)\/index\.html$/.test(rel)){
    assert.doesNotMatch(html,/<h3\b/i,"Orphan H3: "+rel);
    const hs=[...html.matchAll(/<h([1-6])\b/gi)].map(m=>Number(m[1]));
    assert.ok(hs.length>2);
    for(let i=1;i<hs.length;i++)assert.ok(hs[i]<=hs[i-1]+1,"Skipped heading level: "+rel);
    headings++;
  }
}
assert.equal(headings,4);
const work=fs.readFileSync(path.join(root,".github/workflows/update-tech-news.yml"),"utf8");
assert.match(work,/run: python scripts\/polish_search_snippets\.py/);
assert.match(work,/node tests\/search-snippet-quality-test\.cjs/);
const about=fs.readFileSync(path.join(root,"en/about/index.html"),"utf8");
assert.ok(about.includes('id="about-download-guidance"'));
assert.ok(about.includes('href="/en/security/"'));
assert.ok(about.includes('href="/en/programs/"'));
assert.equal((about.match(/id="about-download-guidance"/g)||[]).length,1);
console.log("SEO_SNIPPET_QUALITY_PASS",JSON.stringify({titles,descriptions,headings,social,aboutGuide:true}));
