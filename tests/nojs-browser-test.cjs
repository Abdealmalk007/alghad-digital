"use strict";
/* Headless Chrome proof: actual HTML product downloads work with JS disabled. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const os=require("node:os");
const {spawn}=require("node:child_process");
const {pathToFileURL}=require("node:url");
const root=path.resolve(__dirname,"..");
const qa=path.resolve(root,"..","AlghadDigitalSite_QA");
const chromePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const delay=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 assert.ok(fs.existsSync(chromePath));
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),"alghad-nojs-"));
 const browser=spawn(chromePath,["--headless=new","--disable-gpu",
   "--no-first-run","--disable-extensions","--remote-debugging-port=0",
   "--remote-allow-origins=*","--user-data-dir="+profile,
   "--window-size=1440,900","about:blank"],{stdio:"ignore",windowsHide:true});
 let socket;
 try{
  const active=path.join(profile,"DevToolsActivePort");
  for(let i=0;i<100&&!fs.existsSync(active);i++)await delay(100);
  assert.ok(fs.existsSync(active),"Chrome CDP unavailable");
  const port=fs.readFileSync(active,"utf8").split(/\r?\n/)[0].trim();
  const pages=await (await fetch("http://127.0.0.1:"+port+"/json/list")).json();
  const tab=pages.find(p=>p.type==="page");
  assert.ok(tab);
  socket=new WebSocket(tab.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
    socket.addEventListener("open",resolve,{once:true});
    socket.addEventListener("error",reject,{once:true});
  });
  let id=0;const pending=new Map();
  socket.addEventListener("message",event=>{
    const item=JSON.parse(event.data);
    if(item.id&&pending.has(item.id)){
      const promise=pending.get(item.id);pending.delete(item.id);
      if(item.error)promise.reject(Error(item.error.message));
      else promise.resolve(item.result);
    }
  });
  const send=(method,params={})=>new Promise((resolve,reject)=>{
    const num=++id;pending.set(num,{resolve,reject});
    socket.send(JSON.stringify({id:num,method,params}));
    const timeout=setTimeout(()=>{if(pending.has(num)){pending.delete(num);reject(Error("Timeout "+method));}},25000);
    timeout.unref();
  });
  await send("Page.enable");
  await send("DOM.enable");
  await send("Emulation.setScriptExecutionDisabled",{value:true});
  await send("Page.navigate",{url:pathToFileURL(path.join(root,"index.html")).href});
  let outer="";
  for(let i=0;i<80;i++){
    await delay(120);
    const doc=await send("DOM.getDocument",{depth:1});
    const response=await send("DOM.getOuterHTML",{nodeId:doc.root.nodeId});
    outer=response.outerHTML||"";
    if(outer.includes("data-prerender-product="))break;
  }
  const counts={
    preRenderedProducts:(outer.match(/data-prerender-product=/g)||[]).length,
    preRenderedDownloads:(outer.match(/data-prerender-release=/g)||[]).length,
    preRenderedNews:(outer.match(/class="pre-news-row"/g)||[]).length,
    dynamicProductCards:(outer.match(/class="product-card neo-card"/g)||[]).length,
  };
  assert.equal(counts.preRenderedProducts,8,JSON.stringify(counts));
  assert.equal(counts.preRenderedDownloads,5,JSON.stringify(counts));
  assert.equal(counts.preRenderedNews,4,JSON.stringify(counts));
  assert.equal(counts.dynamicProductCards,0,JSON.stringify(counts));
  assert.ok(outer.indexOf('id="products"')<outer.indexOf('id="news"'));
  assert.ok(outer.indexOf('id="downloads"')<outer.indexOf('id="news"'));
  fs.mkdirSync(qa,{recursive:true});
  const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false,fromSurface:true});
  fs.writeFileSync(path.join(qa,"product-first-nojs-chrome.png"),Buffer.from(shot.data,"base64"));
  console.log("NO_JS_CDP_PASS",counts,"SCREENSHOT=product-first-nojs-chrome.png");
 }finally{
   if(socket)try{socket.close()}catch(_){}
   browser.kill();
 }
}
main().catch(e=>{console.error("NO_JS_CDP_FAILED",e.message);process.exitCode=1});
