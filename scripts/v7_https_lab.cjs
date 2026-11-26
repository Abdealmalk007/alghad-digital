"use strict";
const fs=require("node:fs"),path=require("node:path"),http2=require("node:http2"),zlib=require("node:zlib"),crypto=require("node:crypto");
const [rootArg,portArg,key,cert,mode="normal"]=process.argv.slice(2),root=path.resolve(rootArg),port=Number(portArg);
const mime={".html":"text/html; charset=utf-8",".css":"text/css; charset=utf-8",".js":"application/javascript; charset=utf-8",".json":"application/json",".svg":"image/svg+xml",".woff2":"font/woff2",".png":"image/png",".webp":"image/webp",".ico":"image/x-icon",".webmanifest":"application/manifest+json",".txt":"text/plain"};
const cache=new Map(),derived=new Map();
if(mode==="bundle"){
 for(const route of ["/","/en/"]){
  const p=path.join(root,route===" /"?"index.html":route.slice(1),"index.html");
  let source=fs.readFileSync(p,"utf8");const pattern=/<link rel="stylesheet" href="([^"]+)"[^>]*>/g;
  const matches=[...source.matchAll(pattern)];let css="";
  for(const m of matches){const loc=new URL(m[1],"https://example.invalid"+route);if(loc.origin!=="https://example.invalid")throw Error(m[1]);const p=path.join(root,loc.pathname.slice(1)),c=fs.readFileSync(p,"utf8");if(/@import\b|@charset\b/i.test(c))throw Error(p);for(const u of c.matchAll(/url\(\s*(['"]?)([^)'"]+)\1\s*\)/g)){if(!/^(?:\/|data:|https:)/.test(u[2]))throw Error("relative CSS URL: "+u[2]);}css+="\n/* "+loc.pathname+" */\n"+c;}
  const id=crypto.createHash("sha256").update(css).digest("hex").slice(0,12),url="/assets/lab-"+id+".css";let first=true;source=source.replace(pattern,()=>{if(!first)return "";first=false;return '<link rel="stylesheet" href="'+url+'">';});derived.set(route,Buffer.from(source));derived.set(url,Buffer.from(css));console.log("LAB_BUNDLE",route,matches.length,css.length,url);
 }
}
const srv=http2.createSecureServer({key:fs.readFileSync(key),cert:fs.readFileSync(cert),allowHTTP1:true},(req,res)=>{
 try{const u=new URL(req.url,"https://localhost"),rel=decodeURIComponent(u.pathname).replace(/^\/+/,""),p=path.resolve(root,rel+(u.pathname.endsWith("/")?"index.html":""));if(!p.startsWith(root+path.sep))throw Error("path");const ext=path.extname(p),type=mime[ext]||"application/octet-stream";const text=/\.(html|css|js|json|svg|webmanifest|txt)$/.test(ext);let enc="";if(text){const a=req.headers["accept-encoding"]||"";if(/\bbr\b/.test(a))enc="br";else if(/\bgzip\b/.test(a))enc="gzip";}
 const k=u.pathname+"|"+enc;let buf=cache.get(k);if(!buf){buf=derived.get(u.pathname)||fs.readFileSync(p);if(enc==="br")buf=zlib.brotliCompressSync(buf,{params:{[zlib.constants.BROTLI_PARAM_QUALITY]:5}});else if(enc==="gzip")buf=zlib.gzipSync(buf);cache.set(k,buf);}
 res.writeHead(200,{"content-type":type,"content-length":buf.length,"cache-control":"no-cache","vary":"Accept-Encoding",...(enc?{"content-encoding":enc}:{})});res.end(req.method==="HEAD"?undefined:buf);
 }catch(e){res.writeHead(404);res.end("Not found");}
});srv.listen(port,"127.0.0.1",()=>console.log("READY",mode,port));
