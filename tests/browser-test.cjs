"use strict";
/* Real Chrome headless integration test; Node.js >= 22, no npm dependencies. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const {spawn} = require("node:child_process");
const root = path.resolve(__dirname, "..");
const qaDir = path.resolve(root, "..", "AlghadDigitalSite_QA");
const chromePath = process.env.CHROME_PATH ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const fileUrl = new URL("file:///" + path.join(root, "index.html").replace(/\\/g, "/")).href;
async function main() {
  assert.ok(fs.existsSync(chromePath), "Chrome is required for browser integration test");
  fs.mkdirSync(qaDir, {recursive: true});
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
        setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(Error("CDP timeout: "+method));}},12000);
      });
    }
    async function evaluate(expression) {
      const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
      if(r.exceptionDetails)throw Error("JS exception: "+r.exceptionDetails.text);
      return r.result.value;
    }
    await send("Page.enable");
    await send("Runtime.enable");
    let count=0;
    for(let i=0;i<60;i++){
      count=await evaluate('document.querySelectorAll(".product-card").length');
      if(count===10)break;
      await delay(100);
    }
    assert.equal(count,10,"All allowed project cards should be rendered");
    const showcase=await evaluate('({cards:document.querySelectorAll(".showcase-release").length,downloads:document.querySelectorAll(".showcase-release-cta").length,security:!!document.getElementById("security"),navDownloads:!!document.querySelector(\'.nav a[href="#downloads"]\'),title:document.getElementById("downloads-title")?.textContent})');
    assert.equal(showcase.cards,5,"Four public release cards plus unavailable Stone Manager");
    assert.equal(showcase.downloads,4,"Four official GitHub downloads");
    assert.equal(showcase.security,true,"Security information section should exist");
    assert.equal(showcase.navDownloads,true,"Downloads should be discoverable in navigation");
    const unsafe=await evaluate('([...document.querySelectorAll(".showcase-release-cta")].filter(a=>!a.href.startsWith("https://github.com/Abdealmalk007/")).length)');
    assert.equal(unsafe,0,"Releases can link only to official GitHub asset URLs");
    let downloadCount=0;
    for(let i=0;i<40;i++){
      downloadCount=await evaluate('document.querySelectorAll(".direct-download-card").length');
      if(downloadCount===4) break;
      await delay(100);
    }
    assert.equal(downloadCount,4,"Four publicly downloadable cards");
    assert.equal(await evaluate('window.AL_GHAD_PRODUCTS.some(p=>p.id==="recorder")'),false);
    assert.equal(await evaluate('document.querySelector(\'[data-id="recorder"]\')===null'),true);
    assert.equal(await evaluate('document.getElementById("stat-apps").textContent'),"10");
    assert.equal(await evaluate('document.getElementById("stat-upcoming").textContent'),"05");
    assert.equal(await evaluate('document.getElementById("gallery-portfolio-count").textContent'),"10");
    const hiddenRemoved = await evaluate('(() => { const s=document.querySelector("#search"); s.value="Call Recorder PRO";s.dispatchEvent(new Event("input",{bubbles:true}));return document.querySelectorAll(".product-card").length; })()');
    assert.equal(hiddenRemoved,0,"Removed app must not appear in search");
    await evaluate('(() => { const s=document.querySelector("#search");s.value="";s.dispatchEvent(new Event("input",{bubbles:true})); })()');
    assert.ok(await evaluate('Boolean(document.getElementById("back-to-top-floating"))'));

    for(const [id,expected] of Object.entries({download:2,hr:2,marble:2,reports:1,stone:0})){
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
    assert.equal(await evaluate('document.querySelectorAll(".compare-toggle").length'),10);
    const initial=await evaluate('document.querySelector(".product-card .card-title").textContent');
    await evaluate('document.querySelector("#sort-products").value="name";document.querySelector("#sort-products").dispatchEvent(new Event("change"))');
    const sorted=await evaluate('document.querySelector(".product-card .card-title").textContent');
    assert.notEqual(initial,sorted,"Sorting must rearrange cards");
    await evaluate('document.querySelector("[data-filter=public]").click()');
    assert.equal(await evaluate('document.querySelectorAll(".product-card").length'),5);
    assert.equal(await evaluate('document.querySelectorAll(".direct-download-card").length'),4);
    await evaluate('document.querySelector("[data-filter=all]").click()');
    await evaluate('Array.from(document.querySelectorAll(".compare-toggle")).slice(0,2).forEach(b=>b.click());document.getElementById("compare-open").click()');
    assert.equal(await evaluate('document.getElementById("compare-dialog").open'),true);
    assert.equal(await evaluate('document.querySelectorAll(".compare-panel").length'),2);
    await evaluate('document.querySelector(".compare-close").click();document.querySelector("#compare-clear").click()');
    await evaluate('document.querySelector("[data-detail=stone]").click()');
    await delay(100);
    assert.equal(await evaluate('document.querySelector("#product-modal").open'),true);
    assert.equal(await evaluate('!!document.querySelector("[data-share-app=stone]")'),true);
    assert.equal(await evaluate('new URL(location.href).searchParams.get("app")'),"stone");
    await evaluate('document.querySelector("#modal-close").click()');
    await delay(120);
    assert.equal(await evaluate('new URL(location.href).searchParams.has("app")'),false);
    const contactAddress = "protech.2025.2026@gmail.com";
    assert.equal(await evaluate('document.querySelector(".contact-email-link").textContent.trim()'),contactAddress);
    assert.equal(await evaluate('document.querySelector(".contact-email-link").getAttribute("href")'),"mailto:"+contactAddress);
    assert.equal(await evaluate('document.querySelectorAll(\'a[href="#contact"]\').length'),1);
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
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const mobilePath=path.join(qaDir,"mobile-emulated.png");
    fs.writeFileSync(mobilePath,Buffer.from(shot.data,"base64"));
    await evaluate('document.getElementById("downloads").scrollIntoView({behavior:"instant"})');
    await delay(240);
    const releasesMetrics=await evaluate('({vw:innerWidth,page:document.documentElement.scrollWidth,sectionLeft:document.getElementById("downloads").getBoundingClientRect().left,sectionRight:document.getElementById("downloads").getBoundingClientRect().right,cardCount:document.querySelectorAll(".showcase-release").length})');
    assert.equal(releasesMetrics.cardCount,5);
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
    assert.deepEqual(exceptions,[],"Uncaught runtime exceptions");
    const report={showcase:showcase,releasesMobile:releasesMetrics,releaseScreenshot:releaseShotPath,securityScreenshot:securityShotPath, result:"PASS",cards:count,published:5,directDownloadCards:4,verifiedDownloadVariants:7,stonePublicDownload:"unavailable",compared:2,sorted:true,share:true,deepLink:true,contact:true,contactAddress,mobile:metrics,contactMobile:contactMetrics,downloadModalMobile:modalViewport,downloadModalScreenshot:modalShotPath,viewports,screenshot:mobilePath,contactScreenshot:contactPath};
    fs.writeFileSync(path.join(qaDir,"browser-report.json"),JSON.stringify(report,null,2),"utf8");
    console.log(JSON.stringify(report));
  } finally {
    if(socket) socket.close();
    chrome.kill();
  }
}
main().catch(e => {console.error("BROWSER_QA_FAILED:",e.stack||e.message);process.exitCode=1;});
