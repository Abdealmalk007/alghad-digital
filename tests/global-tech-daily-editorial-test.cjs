"use strict";
/* Guards publisher attribution, live RSS selection, Arabic translation and daily CI. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const cp=require("node:child_process");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const news=JSON.parse(read("assets/news.json"));
const sources=["theverge","techcrunch","arstechnica","wired","engadget"];
const names=new Map(news.sources.map(s=>[s.id,s.name]));
const globalItems=news.articles.filter(item=>sources.includes(item.source));
const ar=read("news/index.html");
const en=read("en/news/index.html");
const workflow=read(".github/workflows/update-tech-news.yml");
assert.equal(sources.length,5);
assert.equal(news.sources.length,15);
assert.equal(news.articles.length,36);
assert.ok(ar.includes('id="global-tech-headlines-title"')||!globalItems.length);
assert.ok(ar.includes('global-other-news-title'));
assert.ok(en.includes("Top stories from global technology publishers")||!globalItems.length);
assert.ok(workflow.includes("python scripts/update_news.py"));
assert.ok(workflow.includes("python scripts/translate_news.py"));
assert.ok(workflow.includes("python scripts/build_seo.py"));
assert.ok(workflow.includes("python scripts/build_en.py"));
assert.ok(workflow.includes("node tests/global-tech-daily-editorial-test.cjs"));
const machine=globalItems.filter(x=>x.translation_status==="machine");
for(const item of globalItems){
 assert.equal(item.source_name,names.get(item.source));
 assert.ok(/^https:\/\//.test(item.url));
 assert.ok(Number.isFinite(Date.parse(item.published_at)));
 assert.ok(["machine","unavailable","original_ar"].includes(item.translation_status));
 assert.ok(!/\b(?:coupon|promo code|discount code|shopping guide|deals of the day|black friday deals)\b/i.test(item.title));
 if(item.translation_status==="machine"){
  assert.ok(typeof item.title_ar==="string" && /[\u0621-\u064a]{3,}/.test(item.title_ar));
  const safeTitle=item.title_ar.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#x27;");
  assert.ok(ar.includes(safeTitle),"Translated headline must appear in Arabic HTML: "+item.source);
 }
 assert.ok(ar.includes(item.source_name),"Arabic publisher credit not found: "+item.source_name);
 assert.ok(en.includes(item.source_name),"English publisher credit not found: "+item.source_name);
}
assert.ok(machine.length>=1 || globalItems.length===0,"Require real existing translated global news");
const py=[
 "from datetime import datetime,timezone",
 "import sys",
 "sys.path.insert(0,r'"+path.join(root,"scripts").replaceAll("\\","\\\\")+"')",
 "from global_tech_editorial import eligible_title,relevance_score,publisher_highlights",
 "now=datetime(2026,11,17,tzinfo=timezone.utc)",
 "assert eligible_title('Apple releases a security patch today','2026-11-17T05:00:00Z',now)",
 "assert not eligible_title('The best coupon codes for mobile apps','2026-11-17T05:00:00Z',now)",
 "assert not eligible_title('Google launches a new AI model','2026-10-01T05:00:00Z',now)",
 "assert relevance_score('Microsoft releases security updates','2026-11-17T05:00:00Z',now)>relevance_score('Review: how to buy a used phone','2026-11-17T05:00:00Z',now)",
 "rows=[{'source':'theverge','url':'https://www.theverge.com/a','title':'Google launches an AI model today','published_at':'2026-11-17T05:00:00Z'}, {'source':'techcrunch','url':'https://techcrunch.com/b','title':'OpenAI unveils a research breakthrough','published_at':'2026-11-17T04:00:00Z'}]",
 "assert len(publisher_highlights(rows,each=2,now=now))==2",
 "print('EDITORIAL_SCORE_FIXTURES_PASS')"
].join("\n");
const run=cp.spawnSync("python",["-c",py],{encoding:"utf8",timeout:20000});
assert.equal(run.status,0,run.stderr||run.stdout);
console.log("GLOBAL_TECH_DAILY_EDITORIAL_PASS",JSON.stringify({allArticles:news.articles.length,globalArticles:globalItems.length,translated:machine.length,sources:[...new Set(globalItems.map(x=>x.source))]}));
