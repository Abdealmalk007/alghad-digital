"use strict";
/* Real Chrome headless integration test; Node.js >= 22, no npm dependencies. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const http = require("node:http");
const {spawn} = require("node:child_process");
const root = path.resolve(__dirname, "..");
const qaDir = path.resolve(root, "..", "AlghadDigitalSite_QA");
const chromePath = process.env.CHROME_PATH ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function startLocalPreview() {
  const mime={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",
    ".js":"text/javascript; charset=utf-8",".svg":"image/svg+xml",".json":"application/json; charset=utf-8"};
  const server=http.createServer((req,res)=>{
    try{
      const target=new URL(req.url,"http://127.0.0.1");
      const pathname=decodeURIComponent(target.pathname);
      const local=path.resolve(root,"."+(pathname==="/"?"/index.html":pathname.endsWith("/")?pathname+"index.html":pathname));
      if(!local.startsWith(root+path.sep) || !fs.existsSync(local) || !fs.statSync(local).isFile()){
        res.writeHead(404);res.end("Not Found");return;
      }
      res.writeHead(200,{"Content-Type":mime[path.extname(local)]||"application/octet-stream"});
      fs.createReadStream(local).pipe(res);
    }catch(_){res.writeHead(400);res.end("Invalid Request")}
  });
  await new Promise((resolve,reject)=>{
    server.once("error",reject);
    server.listen(0,"127.0.0.1",resolve);
  });
  return {server,url:"http://127.0.0.1:"+server.address().port+"/"};
}
async function main() {
  assert.ok(fs.existsSync(chromePath), "Chrome is required for browser integration test");
  fs.mkdirSync(qaDir, {recursive: true});
  const preview=process.env.ALGHAD_TEST_URL?null:await startLocalPreview();
  const fileUrl=process.env.ALGHAD_TEST_URL||preview.url;
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "alghad-cdp-"));
  const chrome = spawn(chromePath, [
    "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
    "--disable-background-networking", "--disable-extensions", "--remote-debugging-port=0",
    "--remote-allow-origins=*", "--user-data-dir=" + profile, "--window-size=1440,900",
    fileUrl
  ], {stdio:"ignore", windowsHide:true});
  let socket;
  try {
    const active = path.join(profile,"DevToolsActivePort");
    for(let i=0; i<120 && !fs.existsSync(active); i++) await delay(100);
    assert.ok(fs.existsSync(active), "Chrome debugging endpoint did not start");
    let port;
    for (let attempt=0; attempt<50; attempt++) {
      try {
        port=fs.readFileSync(active,"utf8").split(/\r?\n/)[0];
        if (/^\d+$/.test(port)) break;
      } catch (error) {
        if (!["EBUSY","ENOENT","EACCES"].includes(error.code)) throw error;
      }
      await delay(100);
    }
    assert.match(port||"",/^\d+$/,"Chrome debugging port unavailable");
    let pages;
    for(let i=0;i<40;i++) {
      try { pages=await (await fetch("http://127.0.0.1:"+port+"/json/list")).json(); if(pages.length)break; } catch (_) {}
      await delay(100);
    }
    const page = pages.find(p => p.type==="page");
    assert.ok(page, "No page target");
    socket = new WebSocket(page.webSocketDebuggerUrl);
    await new Promise((resolve,reject) => {
      socket.addEventListener("open",resolve,{once:true});
      socket.addEventListener("error",reject,{once:true});
    });
    let seq=0;
    const pending=new Map(), exceptions=[];
    socket.addEventListener("message",e => {
      const m=JSON.parse(e.data);
      if(m.method==="Runtime.exceptionThrown") exceptions.push(m.params.exceptionDetails.text);
      if(m.id && pending.has(m.id)) {
        const callback=pending.get(m.id); pending.delete(m.id);
        if(m.error) callback.reject(Error(m.error.message)); else callback.resolve(m.result);
      }
    });
    function send(method,params={}) {
      return new Promise((resolve,reject) => {
        const id=++seq;
        pending.set(id,{resolve,reject});
        socket.send(JSON.stringify({id,method,params}));
        const timeout=setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(Error("CDP timeout: "+method));}},40000);
        timeout.unref();
      });
    }
    async function evaluate(expression) {
      const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
      if(r.exceptionDetails)throw Error("JS exception: "+r.exceptionDetails.text);
      return r.result.value;
    }
    await send("Page.enable");
    await send("Runtime.enable");
    // Chrome initially navigates to the target URL; no second CDP navigation.
    let count=0;
    for(let i=0;i<120;i++){
      count=await evaluate('document.querySelectorAll(".product-card").length');
      if(count===8)break;
      await delay(100);
    }
    if(count!==8) console.error("LOCAL_PAGE_DIAGNOSTIC", await evaluate('({href:location.href,ready:document.readyState,html:document.documentElement.outerHTML.length,app:!!window.AL_GHAD_PRODUCTS,products:window.AL_GHAD_PRODUCTS?.length,head:document.querySelector("#catalog")?.outerHTML.slice(0,160)})'),exceptions);
    assert.equal(count,8,"All allowed project cards should be rendered");
    // Product cards can render before independent editorial scripts finish loading.
    for(let attempt=0;attempt<80;attempt++){
      const done=await evaluate('document.readyState==="complete" && document.querySelectorAll(".editorial-story").length>=5 && document.querySelectorAll(".windows-tool-card").length===8');
      if(done)break;
      await delay(100);
    }
    const editorialCounts=await evaluate('({news:document.querySelectorAll(".editorial-story").length,tools:document.querySelectorAll(".windows-tool-card").length,sources:document.querySelectorAll(".source-directory-link").length,headlineCount:window.AL_GHAD_NEWS?.articles.length})');
    assert.ok(editorialCounts.news>=5,"News cards should render from attributed headlines");
    assert.equal(editorialCounts.tools,8,"All eight free Windows tools should be displayed");
    assert.ok(editorialCounts.sources>=10,"Official news source directory");
    assert.ok(editorialCounts.headlineCount>=5);
    // Verify real, first-party sitewide search across programs and refreshed news.
    assert.equal(await evaluate('document.querySelectorAll("#sitewide-search-trigger").length'),1,"Search control should exist");
    await evaluate('document.getElementById("sitewide-search-trigger").click()');
    for(let attempt=0;attempt<70;attempt++){
      if(await evaluate('window.AL_GHAD_SITE_SEARCH?.records?.length>=50')) break;
      await delay(100);
    }
    assert.ok(await evaluate('window.AL_GHAD_SITE_SEARCH?.records?.length>=50'),"Search index must include pages and real news");
    await evaluate('(() => { const i=document.querySelector(".sitewide-search-input");i.value="عقود";i.dispatchEvent(new Event("input",{bubbles:true})); })()');
    await delay(230);
    assert.ok(await evaluate('document.querySelectorAll(".sitewide-search-card").length>=1'),"Arabic sitewide search yields results");
    assert.ok(await evaluate('!!document.querySelector(\'.sitewide-search-list a[href="/programs/quotes/"]\')'),"Quotes page found");
    await evaluate('(() => { const i=document.querySelector(".sitewide-search-input");i.value="OpenAI";i.dispatchEvent(new Event("input",{bubbles:true})); document.querySelector(\'.sitewide-search-filter[data-kind="news"]\').click(); })()');
    await delay(250);
    assert.ok(await evaluate('document.querySelectorAll(".sitewide-search-card").length>=1'),"News search finds publisher headlines");
    await evaluate('document.querySelector(".sitewide-search-close").click()');
    assert.ok(await evaluate('document.getElementById("sitewide-search-layer").hidden'),"Search overlay closes cleanly");
    for(let attempt=0;attempt<30;attempt++){
      const shares=await evaluate('({products:document.querySelectorAll(".product-card .alghad-share-button").length,news:document.querySelectorAll(".editorial-story .alghad-share-button").length})');
      if(shares.products===8 && shares.news>=5)break;
      await delay(100);
    }
    assert.equal(await evaluate('document.querySelectorAll(".product-card .alghad-share-button").length'),8,"Each product needs a visible share action");
    assert.ok(await evaluate('document.querySelectorAll(".editorial-story .alghad-share-button").length>=5'),"Share actions must appear for news");
    assert.equal(await evaluate('document.querySelector(\'.product-card[data-id="stone"] .alghad-share-button\').dataset.shareUrl'),"https://alghad.digital/programs/stone/");
    const industry=await evaluate('({heavyHomeSections:document.querySelectorAll("[data-industry-topic]").length,hubs:document.querySelectorAll(".home-news-category-links a").length})');
    assert.equal(industry.heavyHomeSections,0,"Full industry news must remain off primary software homepage");
    assert.equal(industry.hubs,4,"Dedicated newsroom links remain available");
    const mainOrder=await evaluate('([...document.querySelectorAll("main > section[id]")].map(s=>s.id))');
    assert.ok(mainOrder.indexOf("products")<mainOrder.indexOf("downloads"));
    assert.ok(mainOrder.indexOf("downloads")<mainOrder.indexOf("news"));
    const badges=await evaluate('([...document.querySelectorAll(".product-card .status")].map(s=>s.textContent.trim()))');
    assert.ok(badges.some(s=>s.includes("Beta")),"Preview releases must be marked Beta");
    assert.ok(fs.readFileSync(path.join(root,"programs/stone/index.html"),"utf8").includes("غير موقّع"),"Stone installer remains clearly unsigned");
    assert.ok(badges.some(s=>s.includes("قريبًا")),"Upcoming products must be honest");
    const badNewsLinks=await evaluate('([...document.querySelectorAll(".editorial-headline-link")].filter(a=>a.protocol!=="https:").length)');
    assert.equal(badNewsLinks,0,"All article links should use HTTPS");
    const badVendorLinks=await evaluate('([...document.querySelectorAll(".windows-tool-button")].filter(a=>a.protocol!=="https:").length)');
    assert.equal(badVendorLinks,0,"All vendor links should use HTTPS");
    await evaluate('document.querySelector(\'[data-news-category="الذكاء الاصطناعي"]\').click()');
    assert.equal(await evaluate('document.querySelector(\'[data-news-category="الذكاء الاصطناعي"]\').getAttribute("aria-pressed")'),"true");
    await evaluate('document.querySelector(\'[data-news-category="الكل"]\').click()');
    await evaluate('(() => {const field=document.getElementById("windows-tools-search");field.value="Ventoy";field.dispatchEvent(new Event("input",{bubbles:true}));})()');
    assert.equal(await evaluate('document.querySelectorAll(".windows-tool-card").length'),1,"Utility search must filter tools");
    await evaluate('(() => {const field=document.getElementById("windows-tools-search");field.value="";field.dispatchEvent(new Event("input",{bubbles:true}));})()');
    assert.equal(await evaluate('document.querySelectorAll(".windows-tool-card").length'),8);

    const showcase=await evaluate('({cards:document.querySelectorAll(".showcase-release").length,downloads:document.querySelectorAll(".showcase-release-cta").length,security:!!document.getElementById("security"),navDownloads:!!document.querySelector(\'.nav a[href="#downloads"]\'),title:document.getElementById("downloads-title")?.textContent})');
    assert.equal(showcase.cards,7,"Seven verified release cards including unsigned Portable Windows Care");
    assert.equal(showcase.downloads,7,"Seven official GitHub downloads");
    for(let attempt=0;attempt<25;attempt++){
      if(await evaluate('document.querySelectorAll(".showcase-release .alghad-share-button").length===7'))break;
      await delay(100);
    }
    assert.equal(await evaluate('document.querySelectorAll(".showcase-release .alghad-share-button").length'),7,"Showcase cards need share buttons");
    assert.equal(await evaluate('document.querySelectorAll(".showcase-release-details").length'),0,"Extra details shortcuts removed");
    assert.equal(showcase.security,true,"Security information section should exist");
    assert.equal(showcase.navDownloads,true,"Downloads should be discoverable in navigation");
    const unsafe=await evaluate('([...document.querySelectorAll(".showcase-release-cta")].filter(a=>!a.href.startsWith("https://github.com/Abdealmalk007/")).length)');
    assert.equal(unsafe,0,"Releases can link only to official GitHub asset URLs");
    let downloadCount=0;
    for(let i=0;i<40;i++){
      downloadCount=await evaluate('document.querySelectorAll(".direct-download-card").length');
      if(downloadCount===7) break;
      await delay(100);
    }
    assert.equal(downloadCount,7,"Seven publicly downloadable cards");
    assert.equal(await evaluate('window.AL_GHAD_PRODUCTS.some(p=>p.id==="recorder")'),false);
    assert.equal(await evaluate('document.querySelector(\'[data-id="recorder"]\')===null'),true);
    assert.equal(await evaluate('document.getElementById("stat-apps").textContent'),"08");
    assert.equal(await evaluate('document.getElementById("stat-upcoming").textContent'),"01");
    assert.equal(await evaluate('document.getElementById("gallery-portfolio-count").textContent'),"08");
    const hiddenRemoved = await evaluate('(() => { const s=document.querySelector("#search"); s.value="Call Recorder PRO";s.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelectorAll(".product-card").length; })()');
    assert.equal(hiddenRemoved,0,"Removed app must not appear in search");
    await evaluate('(() => { const s=document.querySelector("#search");s.value="";s.dispatchEvent(new Event("input",{bubbles:true})); })()');
    assert.ok(await evaluate('Boolean(document.getElementById("back-to-top-floating"))'));

    for(const [id,expected] of Object.entries({download:2,hr:2,marble:2,reports:1,stone:1,quotes:1})){
      const hrefs=await evaluate('([...document.querySelectorAll(".direct-download-card")].map(a=>a.getAttribute("href")) )');
      for(const href of hrefs) assert.match(href,/^https:\/\/github\.com\/Abdealmalk007\//);
      await evaluate('document.querySelector(\'[data-detail="'+id+'"]\').click()');
      await delay(100);
      assert.equal(await evaluate('document.getElementById("product-modal").open'),true);
      assert.equal(await evaluate('document.querySelectorAll("#product-modal .download-section").length'),1);
      const countLinks=await evaluate('document.querySelectorAll("#product-modal .download-variant-link").length');
      assert.equal(countLinks,expected,"Download variants for "+id);
      if(expected>0){
        const bad=await evaluate('([...document.querySelectorAll("#product-modal .download-variant-link")].filter(a=>!a.href.startsWith("https://github.com/Abdealmalk007/")).length)');
        assert.equal(bad,0,"Only official GitHub binaries");
        assert.equal(await evaluate('document.querySelectorAll("#product-modal .download-caution").length'),1);
      } else assert.equal(await evaluate('document.querySelectorAll("#product-modal .download-unavailable").length'),1);
      await evaluate('document.getElementById("modal-close").click()');
      await delay(80);
    }
    await evaluate('document.querySelector(\'[data-detail="kitchen"]\').click()');
    assert.equal(await evaluate('document.querySelectorAll("#product-modal .download-section").length'),0);
    await evaluate('document.getElementById("modal-close").click()');
    await delay(80);
    assert.equal(await evaluate('document.querySelectorAll(".compare-toggle").length'),0,"Compare controls removed");
    assert.equal(await evaluate('document.getElementById("compare-tray")===null'),true);
    assert.equal(await evaluate('document.querySelectorAll(".product-card .alghad-share-button").length'),8);
    assert.equal(await evaluate('document.querySelectorAll(".product-card .direct-download-card").length'),7);
    assert.equal(await evaluate('document.querySelectorAll(".product-card .card-link").length'),0,"GitHub shortcuts removed");
    const initial=await evaluate('document.querySelector(".product-card .card-title").textContent');
    await evaluate('document.querySelector("#sort-products").value="name";document.querySelector("#sort-products").dispatchEvent(new Event("change"))');
    const sorted=await evaluate('document.querySelector(".product-card .card-title").textContent');
    assert.notEqual(initial,sorted,"Sorting must rearrange cards");
    await evaluate('document.querySelector("[data-filter=public]").click()');
    assert.equal(await evaluate('document.querySelectorAll(".product-card").length'),7);
    assert.equal(await evaluate('document.querySelectorAll(".direct-download-card").length'),7);
    await evaluate('document.querySelector("[data-filter=all]").click()');
    assert.equal(await evaluate('document.querySelectorAll(".compare-panel").length'),0);
    await evaluate('document.querySelector("[data-detail=stone]").click()');
    await delay(100);
    assert.equal(await evaluate('document.querySelector("#product-modal").open'),true);
    for(let i=0;i<25;i++){
      if(await evaluate('!!document.querySelector("#product-modal .alghad-share-button")'))break;
      await delay(100);
    }
    assert.equal(await evaluate('!!document.querySelector("#product-modal .alghad-share-button")'),true);
    for(let attempt=0;attempt<30;attempt++){
      if(await evaluate('new URL(location.href).searchParams.get("app")')==="stone")break;
      await delay(100);
    }
    assert.equal(await evaluate('new URL(location.href).searchParams.get("app")'),"stone");
    await evaluate('document.querySelector("#modal-close").click()');
    for(let i=0;i<20;i++){
      if(!await evaluate('new URL(location.href).searchParams.has("app")'))break;
      await delay(100);
    }
    assert.equal(await evaluate('new URL(location.href).searchParams.has("app")'),false);
    const contactAddress = "protech.2025.2026@gmail.com";
    assert.equal(await evaluate('document.querySelector(".contact-email-link").textContent.trim()'),contactAddress);
    assert.equal(await evaluate('document.querySelector(".contact-email-link").getAttribute("href")'),"mailto:"+contactAddress);
    assert.equal(await evaluate('document.querySelectorAll(\'a[href="#contact"]\').length'),2,"Header contact CTA and hero support CTA");
    await evaluate('document.getElementById("copy-protech-email").click()');
    await delay(150);
    assert.ok((await evaluate('document.getElementById("contact-copy-note").textContent')).length>0);
    await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
    await delay(250);
    const metrics=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,header:document.querySelector(".site-header").getBoundingClientRect().width,heading:({left:document.querySelector("#hero-title").getBoundingClientRect().left,right:document.querySelector("#hero-title").getBoundingClientRect().right})})');
    assert.equal(metrics.width,390,"Phone viewport width");
    assert.ok(metrics.scroll<=392,"Mobile horizontal overflow: "+JSON.stringify(metrics));
    assert.ok(metrics.heading.left>=-2 && metrics.heading.right<=392,"Hero heading clipped on mobile");
    const contactMetrics=await evaluate('({left:document.querySelector(".contact-panel").getBoundingClientRect().left,right:document.querySelector(".contact-panel").getBoundingClientRect().right,emailWidth:document.querySelector(".contact-email-link").getBoundingClientRect().width})');
    assert.ok(contactMetrics.left>=-2 && contactMetrics.right<=392,"Contact panel clipped: "+JSON.stringify(contactMetrics));
    assert.ok(contactMetrics.emailWidth>150,"Email contact link missing on mobile");

    await evaluate('document.querySelector(\'[data-detail="download"]\').click()');
    await delay(150);
    const modalViewport=await evaluate('({vw:innerWidth,left:document.getElementById("product-modal").getBoundingClientRect().left,right:document.getElementById("product-modal").getBoundingClientRect().right,contentWidth:document.getElementById("product-modal").scrollWidth,clientWidth:document.getElementById("product-modal").clientWidth})');
    assert.ok(modalViewport.left>=-2 && modalViewport.right<=392,"Modal viewport clipping: "+JSON.stringify(modalViewport));
    assert.ok(modalViewport.contentWidth<=modalViewport.clientWidth+2,"Modal contents overflow: "+JSON.stringify(modalViewport));
    const modalShot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const modalShotPath=path.join(qaDir,"download-modal-mobile.png");
    fs.writeFileSync(modalShotPath,Buffer.from(modalShot.data,"base64"));
    await evaluate('document.getElementById("modal-close").click()');
    await delay(90);
    await evaluate('document.getElementById("news").scrollIntoView({behavior:"instant"})');
    await delay(340);
    const newsMobile=await evaluate('({cards:document.querySelectorAll(".editorial-story").length,overflow:document.documentElement.scrollWidth,sectionWidth:document.getElementById("news").getBoundingClientRect().width})');
    assert.ok(newsMobile.overflow<=392,"News section mobile overflow");
    const newsImage=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    fs.writeFileSync(path.join(qaDir,"editorial-news-mobile.png"),Buffer.from(newsImage.data,"base64"));
    await evaluate('document.getElementById("free-tools").scrollIntoView({behavior:"instant"})');
    await delay(340);
    const toolsMobile=await evaluate('({cards:document.querySelectorAll(".windows-tool-card").length,overflow:document.documentElement.scrollWidth,sectionWidth:document.getElementById("free-tools").getBoundingClientRect().width})');
    assert.equal(toolsMobile.cards,8);
    assert.ok(toolsMobile.overflow<=392,"Windows tools section mobile overflow");
    const toolsImage=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    fs.writeFileSync(path.join(qaDir,"editorial-tools-mobile.png"),Buffer.from(toolsImage.data,"base64"));
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const mobilePath=path.join(qaDir,"mobile-emulated.png");
    fs.writeFileSync(mobilePath,Buffer.from(shot.data,"base64"));
    await evaluate('document.getElementById("downloads").scrollIntoView({behavior:"instant"})');
    await delay(240);
    const releasesMetrics=await evaluate('({vw:innerWidth,page:document.documentElement.scrollWidth,sectionLeft:document.getElementById("downloads").getBoundingClientRect().left,sectionRight:document.getElementById("downloads").getBoundingClientRect().right,cardCount:document.querySelectorAll(".showcase-release").length})');
    assert.equal(releasesMetrics.cardCount,7);
    assert.ok(releasesMetrics.page<=392,"Release section overflow: "+JSON.stringify(releasesMetrics));
    const releaseShot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const releaseShotPath=path.join(qaDir,"releases-mobile-v33.png");
    fs.writeFileSync(releaseShotPath,Buffer.from(releaseShot.data,"base64"));
    await evaluate('document.getElementById("security").scrollIntoView({behavior:"instant"})');
    await delay(240);
    const securityShot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const securityShotPath=path.join(qaDir,"security-mobile-v33.png");
    fs.writeFileSync(securityShotPath,Buffer.from(securityShot.data,"base64"));

    await evaluate('document.getElementById("contact").scrollIntoView({behavior:"instant"})');
    await delay(260);
    const contactShot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const contactPath=path.join(qaDir,"contact-mobile.png");
    fs.writeFileSync(contactPath,Buffer.from(contactShot.data,"base64"));

    const viewports=[];
    for(const width of [320,768,1440]){
      await send("Emulation.setDeviceMetricsOverride",{width,height:900,deviceScaleFactor:1,mobile:width<820});
      await delay(180);
      const value=await evaluate('({viewport:innerWidth,page:document.documentElement.scrollWidth,contactRight:document.querySelector(".contact-panel").getBoundingClientRect().right,contactLeft:document.querySelector(".contact-panel").getBoundingClientRect().left})');
      assert.ok(value.page<=width+2,"Overflow at "+width+"px: "+JSON.stringify(value));
      assert.ok(value.contactLeft>=-2 && value.contactRight<=width+2,"Contact clipping at "+width+"px");
      viewports.push(value);
    }
    // Full industry news are intentionally omitted from the homepage, and
    // tested as accessible independent pages in the crawlability loop below.
    const seoPages=[];
    await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
    for(const target of ["/programs/download/","/programs/kitchen/","/news/","/free-windows-tools/","/ai-news/","/tech-companies/","/cars/","/protech/","/about/","/security/","/privacy/"]){
      await send("Page.navigate",{url:new URL(target,fileUrl).href});
      let value;
      for(let i=0;i<50;i++){
        await delay(100);
        value=await evaluate('({path:location.pathname,ready:document.readyState,h1:document.querySelector("h1")?.textContent,viewport:innerWidth,page:document.documentElement.scrollWidth,headerWidth:document.querySelector(".site-header")?.getBoundingClientRect().width,lang:document.documentElement.lang})');
        if(value.path===target&&value.ready==="complete"&&value.h1)break;
      }
      assert.equal(value.path,target,"SEO page navigation: "+target);
      assert.equal(value.lang,"ar","Arabic SEO page: "+target);
      assert.ok(value.h1.length>6,"Visible SEO page heading: "+target);
      assert.ok(value.page<=392,"SEO page horizontal overflow: "+target+" "+JSON.stringify(value));
      assert.ok(value.headerWidth<=392,"SEO page header overflow: "+target);
      seoPages.push(value);
      if(target==="/programs/download/"){
        const img=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
        fs.writeFileSync(path.join(qaDir,"seo-program-mobile-v36.png"),Buffer.from(img.data,"base64"));
      }
    }
    // English static edition: real Chrome navigation, LTR, responsive layout,
    // same-page Arabic switch and optional search/filter enhancement.
    const enPages=[];
    await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
    for(const target of ["/en/","/en/programs/","/en/programs/download/","/en/programs/kitchen/",
                         "/en/news/","/en/ai-news/","/en/cars/","/en/about/","/en/security/","/en/privacy/"]){
      await send("Page.navigate",{url:new URL(target,fileUrl).href});
      let value;
      for(let i=0;i<75;i++){
        await delay(100);
        value=await evaluate('({path:location.pathname,ready:document.readyState,h1:document.querySelector("h1")?.innerText,viewport:innerWidth,scroll:document.documentElement.scrollWidth,lang:document.documentElement.lang,dir:document.documentElement.dir,ar:document.querySelector(".en-lang-switch")?.getAttribute("href"),navbar:document.querySelector(".en-header")?.getBoundingClientRect().width})');
        if(value.path===target&&value.ready==="complete"&&value.h1)break;
      }
      assert.equal(value.path,target,"English route "+target);
      assert.equal(value.lang,"en","English document language "+target);
      assert.equal(value.dir,"ltr","LTR layout "+target);
      assert.ok(value.h1.length>=6,"English heading "+target);
      assert.ok(value.scroll<=392,"English mobile overflow "+target+" "+JSON.stringify(value));
      assert.ok(value.navbar<=392,"English header overflow "+target);
      assert.equal(value.ar,"https://alghad.digital"+(target.replace(/^\/en/,"")||"/"),"English AR switch "+target);
      enPages.push(value);
      if(target==="/en/"){
        const count=await evaluate('document.querySelectorAll(".en-product-card[data-product]").length');
        assert.equal(count,8,"English cards visible");
        const filters=await evaluate('({hasSearch:!!document.querySelector("#en-search"),count:document.querySelectorAll(".en-release-card").length})');
        assert.equal(filters.hasSearch,true);
        assert.equal(filters.count,7,"Verified preview releases");
        await evaluate('document.querySelector("#en-search").value="Kitchen";document.querySelector("#en-search").dispatchEvent(new Event("input",{bubbles:true}))');
        assert.equal(await evaluate('document.querySelectorAll(".en-product-card[data-product]:not([hidden])").length'),1,"English search works");
        await evaluate('document.querySelector("#en-search").value="";document.querySelector("#en-search").dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("[data-en-filter=public]").click()');
        assert.equal(await evaluate('document.querySelectorAll(".en-product-card[data-product]:not([hidden])").length'),7,"English published filter");
        const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
        fs.writeFileSync(path.join(qaDir,"english-home-mobile-v42.png"),Buffer.from(shot.data,"base64"));
      }
    }
    for(const width of [320,768,1440]){
      await send("Page.navigate",{url:new URL("/en/",fileUrl).href});
      for(let attempt=0;attempt<40;attempt++){
        if(await evaluate('document.readyState==="complete"&&document.querySelectorAll(".en-product-card").length===8'))break;
        await delay(100);
      }
      await send("Emulation.setDeviceMetricsOverride",{width,height:900,deviceScaleFactor:1,mobile:width<820});
      await delay(150);
      const layout=await evaluate('({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,header:document.querySelector(".en-header")?.getBoundingClientRect().width})');
      assert.ok(layout.documentWidth<=width+2,"EN responsive overflow at "+width+"px: "+JSON.stringify(layout));
    }
    assert.deepEqual(exceptions,[],"Uncaught runtime exceptions");
    const report={seoPages,enPages,industry,editorial:editorialCounts,newsMobile,toolsMobile,showcase:showcase,releasesMobile:releasesMetrics,releaseScreenshot:releaseShotPath,securityScreenshot:securityShotPath, result:"PASS",cards:count,published:7,directDownloadCards:7,verifiedDownloadVariants:12,stonePublicDownload:"unsigned-beta-preview",compared:0,sorted:true,share:true,deepLink:true,contact:true,contactAddress,mobile:metrics,contactMobile:contactMetrics,downloadModalMobile:modalViewport,downloadModalScreenshot:modalShotPath,viewports,screenshot:mobilePath,contactScreenshot:contactPath};
    fs.writeFileSync(path.join(qaDir,"browser-report.json"),JSON.stringify(report,null,2),"utf8");
    console.log(JSON.stringify(report));
  } finally {
    if(socket) socket.close();
    chrome.kill();
    if(preview) await new Promise(resolve=>preview.server.close(resolve));
  }
}
main().catch(e => {console.error("BROWSER_QA_FAILED:",e.stack||e.message);process.exitCode=1;});
