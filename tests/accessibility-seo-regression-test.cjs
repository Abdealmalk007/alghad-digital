"use strict";
/* Guard SEO and a11y improvements against scheduled regeneration. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=path.resolve(__dirname,"..");
const read=rel=>fs.readFileSync(path.join(root,rel),"utf8");
const sitemap=read("sitemap.xml");
const urls=[...sitemap.matchAll(/<loc>(https:\/\/alghad\.digital\/[^<]*)<\/loc>/g)].map(m=>m[1]);
assert.equal(urls.length,48);
assert.equal(new Set(urls).size,urls.length);
const robots=read("robots.txt");
assert.match(robots,/^User-agent:\s*\*\s*$/m);
assert.match(robots,/^Sitemap:\s*https:\/\/alghad\.digital\/sitemap\.xml\s*$/m);
let pages=0,schemas=0,withCsp=0,withSocial=0;
for(const url of urls){
  const file=url.replace("https://alghad.digital/","")+"index.html";
  const html=read(file);
  assert.match(html,/<meta charset="utf-8">/i,file);
  assert.match(html,/<title>[^<]{12,}<\/title>/i,file);
  assert.match(html,/<html lang="(?:ar|en)"/i,file);
  assert.doesNotMatch(html,/lang="auto"/i,file);
  assert.match(html,/rel="canonical"/i,file);
  assert.match(html,/max-image-preview:large/i,file);
  const contentPolicy=html.match(/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/i)?.[1];
  assert.ok(contentPolicy?.includes("connect-src 'self'"),"CSP same-origin fetch: "+file);
  assert.ok(contentPolicy?.includes("script-src-attr 'none'"),"No unsafe script attrs: "+file);
  withCsp++;
  const isEnglish=url.includes("/en/");
  const altLocale=isEnglish?"ar_SA":"en_US";
  if(html.includes('property="og:locale"')){
    assert.ok(html.includes('property="og:locale:alternate" content="'+altLocale+'"'),file);
    withSocial++;
  }
  assert.doesNotMatch(html,/<a\b[^>]*class="logo"[^>]*aria-label=/i,file);
  assert.doesNotMatch(html,/<a\b[^>]*class="contact-email-link"[^>]*aria-label=/i,file);
  assert.doesNotMatch(html,/aria-label="Switch to English">EN<\/a>/,file);
  assert.doesNotMatch(html,/aria-label="Switch to Arabic">AR<\/a>/,file);
  const scripts=[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  for(const match of scripts){
    const data=JSON.parse(match[1]);
    assert.equal(data["@context"],"https://schema.org","Schema JSON: "+file);
    schemas++;
  }
  pages++;
}
const downloads=read("assets/downloads-ui.js");
assert.ok(downloads.includes('text + " — " + label'),"Download label must contain visible text");
const editorial=read("assets/editorial.js");
assert.ok(editorial.includes('test(item.title) ? "ar" : "en"'),"News lang must be BCP-47");
assert.ok(!editorial.includes('headlineLink.lang=translated?"ar":"auto"'));
const css=read("assets/refinement.css");
assert.match(css,/\.footer a\.accent-text\s*\{[^}]*text-decoration:\s*underline/);
const home=read("index.html");
assert.ok(home.includes('class="contact-email-link"'));
assert.ok(home.includes('class="lang-toggle"'));
const workflow=read(".github/workflows/update-tech-news.yml");
assert.ok(workflow.includes("node tests/accessibility-seo-regression-test.cjs"));
assert.ok(workflow.includes("python scripts/build_contact_security.py"));
console.log("SEO_A11Y_CI_PASS",JSON.stringify({pages,withCsp,withSocial,structuredDataBlocks:schemas,robotsPresent:true,accessibilityPolicies:true}));
