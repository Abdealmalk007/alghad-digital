"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=p=>fs.readFileSync(path.join(root,p),"utf8");
const workflow=read(".github/workflows/update-tech-news.yml");
const schedule=[...workflow.matchAll(/^\s*- cron: "([0-9* ,/]+)"\s*(?:#.*)?$/gm)].map(m=>m[1]);
assert.deepEqual(schedule,["30 4 * * *","17 5 * * *","47 7 * * *","13 11 * * *"]);
assert.ok(workflow.includes("workflow_dispatch:"));
assert.ok(workflow.includes("cancel-in-progress: false"),"Preserve serialized updates");
const steps=[
 "scripts/update_news.py",
 "scripts/update_industry_news.py",
 "scripts/translate_news.py",
 "scripts/news_health_report.py",
 "scripts/prerender_home.py",
 "scripts/build_seo.py",
 "scripts/build_en.py",
 "scripts/build_program_experience.py",
 "scripts/build_site_search.py",
 "tests/news-refresh-reliability-test.cjs",
];
for(const x of steps)assert.ok(workflow.includes(x),"Missing workflow step "+x);
for(let i=1;i<steps.length;i++)assert.ok(workflow.indexOf(steps[i])>workflow.indexOf(steps[i-1]),"Incorrect workflow order "+steps[i]);
const general=JSON.parse(read("assets/news.json"));
const industry=JSON.parse(read("assets/industry-news.json"));
assert.ok(general.articles.length>=5);
assert.equal(new Set(Object.keys(industry.topics)).size,3);
assert.ok(general.generated_at && industry.generated_at);
assert.ok(read("scripts/news_health_report.py").includes("GITHUB_STEP_SUMMARY"));
assert.ok(read("scripts/news_health_report.py").includes("published_at"));
console.log("NEWS_REFRESH_RELIABILITY_PASS",JSON.stringify({scheduleCount:schedule.length,main:"07:30 Asia/Riyadh",backup:["08:17","10:47","14:13"],articleCount:general.articles.length}));
