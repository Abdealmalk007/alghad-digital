"use strict";
/* Real Chrome headless integration test; Node.js >= 22, no npm dependencies. */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const http = require("node:http");
const {spawn} = require("node:child_process");
const root = path.resolve(__dirname, "..");
const releaseFacts = require("./release-facts.cjs")(root);
const qaDir = path.resolve(root, "..", "AlghadDigitalSite_QA", "V7_RC_REPORTS");
const chromePath = process.env.CHROME_PATH ||
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function startLocalPreview() {
  const mime={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",
    ".js":"text/javascript; charset=utf-8",".svg":"image/svg+xml",".json":"application/json; charset=utf-8",".woff2":"font/woff2",".webmanifest":"application/manifest+json",".png":"image/png"};
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
    // Chrome can expose an empty startup tab alongside the requested local preview.
    const page = pages.find(p => p.type==="page" && p.url===fileUrl)
      || pages.find(p => p.type==="page" && p.url.startsWith(fileUrl))
      || pages.find(p => p.type==="page");
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
    await send("Network.enable");
    // Some headless Chrome builds start with about:blank despite a startup URL.
    // Navigate only in that case; avoid needless reloads in the normal path.
    if(await evaluate("location.href")==="about:blank"){
      await send("Page.navigate",{url:fileUrl});
    }
    const waitReady=async()=>{for(let i=0;i<120;i++){if(await evaluate('document.readyState==="complete" && document.querySelectorAll("[data-v6-priority]").length===4'))return;await delay(100);}throw Error("page not ready");};
    const results=[];
    for(const lang of ["ar","en"]){
      await send("Page.navigate",{url:new URL(lang==="en"?"en/":"",fileUrl).href});await delay(500);await waitReady();
      for(const mode of ["dark","light"]){
      await evaluate('window.AlghadTheme.set("'+mode+'")');
      for(const width of [320,360,390,430,768,1024,1280,1440,1920]){
        await send("Emulation.setDeviceMetricsOverride",{width,height:900,deviceScaleFactor:1,mobile:width<500});await delay(250);
        const data=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,ids:[...document.querySelectorAll("[data-v6-priority]")].map(x=>x.dataset.v6Priority),columns:getComputedStyle(document.querySelector(".v6-grid")).gridTemplateColumns,images:[...document.querySelectorAll(".v6-card img")].every(x=>x.complete&&x.naturalWidth>0)})');
        assert.deepEqual(data.ids,["smart-excel","reports","hr","download"]);assert.ok(data.scroll<=data.width+2,JSON.stringify(data));
        results.push({lang,mode,width,scroll:data.scroll,columns:data.columns});
        if(width===390||width===1440){const shot=await send("Page.captureScreenshot",{format:"png"});fs.writeFileSync(path.join(qaDir,"v7-"+lang+"-"+mode+"-"+width+".png"),Buffer.from(shot.data,"base64"));}
      }
      }
      const themeCheck=await evaluate('(()=>{const b=document.querySelector("#theme-toggle,.v6-theme"),before=document.documentElement.dataset.v7Theme;b.click();const after=document.documentElement.dataset.v7Theme;b.click();return [before,after,document.documentElement.dataset.v7Theme]})()');assert.notEqual(themeCheck[0],themeCheck[1]);assert.equal(themeCheck[0],themeCheck[2]);
      const font=await evaluate('document.fonts.ready.then(()=>({loaded:[...document.fonts].some(f=>f.family.includes("IBM Plex Sans Arabic")&&f.status==="loaded"),family:getComputedStyle(document.body).fontFamily}))');assert.ok(font.loaded,JSON.stringify(font));assert.ok(font.family.includes("IBM Plex Sans Arabic"));
      const search=await evaluate('(()=>{document.getElementById("sitewide-search-trigger").click();const i=document.querySelector(".sitewide-search-input");i.value="SmartExcelAnalyzer";i.dispatchEvent(new Event("input",{bubbles:true}));return !document.getElementById("sitewide-search-layer").hidden})()');assert.ok(search);let found=false;for(let t=0;t<60;t++){if(await evaluate('document.querySelector(".sitewide-search-list").textContent.toLowerCase().includes("smartexcelanalyzer")')){found=true;break}await delay(200)}assert.ok(found,"Search index result missing");await evaluate('document.dispatchEvent(new KeyboardEvent("keydown",{key:"Escape",bubbles:true}));');assert.ok(await evaluate('document.getElementById("sitewide-search-layer").hidden'));
      const check=await evaluate('(()=>{const a=document.querySelector(".v6-download");a.addEventListener("click",e=>e.preventDefault());let n=0;window.gtag=()=>n++;localStorage.setItem("alghad_analytics_consent_v1","no");a.click();const denied=n;localStorage.setItem("alghad_analytics_consent_v1","yes");a.click();localStorage.removeItem("alghad_analytics_consent_v1");return [denied,n]})()');assert.deepEqual(check,[0,1]);
    }
    await send("Emulation.setDeviceMetricsOverride",{width:390,height:900,deviceScaleFactor:1,mobile:true});
    const ready=await evaluate('Promise.race([navigator.serviceWorker.ready.then(r=>!!r.active),new Promise(r=>setTimeout(()=>r(false),10000))])');assert.ok(ready,"Service worker must activate");
    if(!await evaluate('!!navigator.serviceWorker.controller')){await send("Page.reload");await delay(1000)}
    assert.ok(await evaluate('!!navigator.serviceWorker.controller'),"Page controlled by SW");
    if(preview){preview.server.closeAllConnections();await new Promise(r=>preview.server.close(r));}else{await send("Network.emulateNetworkConditions",{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});}
    await send("Page.navigate",{url:new URL("programs/hr/",fileUrl).href});let offline=false;for(let t=0;t<60;t++){try{if(await evaluate('document.title.includes("Offline")')){offline=true;break}}catch(_){}await delay(200)}assert.ok(offline,"Offline fallback failed: "+JSON.stringify(await evaluate('({title:document.title,url:location.href,body:document.body?.innerText.slice(0,150)})')));
    await send("Network.emulateNetworkConditions",{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});
    console.log("V7_PWA_OFFLINE_SEARCH_FONT_PASS");
    console.log("V7_BROWSER_PASS",JSON.stringify(results),"runtimeErrors",JSON.stringify(exceptions));assert.equal(exceptions.length,0);
  } finally {if(socket)socket.close();chrome.kill();if(preview&&preview.server.listening)preview.server.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1});