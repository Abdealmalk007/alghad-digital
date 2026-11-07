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
    const port = fs.readFileSync(active,"utf8").split(/\r?\n/)[0];
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
      if(count===11)break;
      await delay(100);
    }
    assert.equal(count,11,"All project cards should be rendered");
    assert.equal(await evaluate('document.querySelectorAll(".compare-toggle").length'),11);
    const initial=await evaluate('document.querySelector(".product-card .card-title").textContent');
    await evaluate('document.querySelector("#sort-products").value="name";document.querySelector("#sort-products").dispatchEvent(new Event("change"))');
    const sorted=await evaluate('document.querySelector(".product-card .card-title").textContent');
    assert.notEqual(initial,sorted,"Sorting must rearrange cards");
    await evaluate('document.querySelector("[data-filter=public]").click()');
    assert.equal(await evaluate('document.querySelectorAll(".product-card").length'),5);
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
    await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
    await delay(250);
    const metrics=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,header:document.querySelector(".site-header").getBoundingClientRect().width,heading:({left:document.querySelector("#hero-title").getBoundingClientRect().left,right:document.querySelector("#hero-title").getBoundingClientRect().right})})');
    assert.equal(metrics.width,390,"Phone viewport width");
    assert.ok(metrics.scroll<=392,"Mobile horizontal overflow: "+JSON.stringify(metrics));
    assert.ok(metrics.heading.left>=-2 && metrics.heading.right<=392,"Hero heading clipped on mobile");
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
    const mobilePath=path.join(qaDir,"mobile-emulated.png");
    fs.writeFileSync(mobilePath,Buffer.from(shot.data,"base64"));
    assert.deepEqual(exceptions,[],"Uncaught runtime exceptions");
    const report={result:"PASS",cards:count,published:5,compared:2,sorted:true,share:true,deepLink:true,mobile:metrics,screenshot:mobilePath};
    fs.writeFileSync(path.join(qaDir,"browser-report.json"),JSON.stringify(report,null,2),"utf8");
    console.log(JSON.stringify(report));
  } finally {
    if(socket) socket.close();
    chrome.kill();
  }
}
main().catch(e => {console.error("BROWSER_QA_FAILED:",e.stack||e.message);process.exitCode=1;});
