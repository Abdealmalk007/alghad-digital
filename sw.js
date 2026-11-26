/* V7: bounded public offline cache; never caches tracking, downloads or credentials. */
const CACHE="alghad-v7-2", FALLBACK="/offline.html";
const CORE=[FALLBACK,"/assets/offline.css","/assets/brand/dawn-g.svg","/icon-192.png","/icon-512.png"];
const NEWS=new Set(["/assets/news.json","/assets/news-data.js","/assets/industry-news.json","/assets/industry-news-data.js","/assets/top5-news.json"]);
const canStore=r=>r.ok&&r.type==="basic"&&!/private|no-store/i.test(r.headers.get("cache-control")||"");
self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE))));
self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith("alghad-v7-")&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener("message",e=>{if(e.data==="SKIP_WAITING")self.skipWaiting()});
self.addEventListener("fetch",e=>{const r=e.request,u=new URL(r.url);if(r.method!=="GET"||u.origin!==self.location.origin||r.headers.has("authorization")||r.headers.has("range")||u.search||/\.(exe|msi|apk|zip|bundle|7z)$/i.test(u.pathname)||/analytics|gtag|collect/i.test(u.pathname))return;
if(r.mode==="navigate"){e.respondWith(fetch(r).catch(()=>caches.match(FALLBACK)));return;}
if(NEWS.has(u.pathname)){e.respondWith(caches.open(CACHE).then(async c=>{try{const res=await fetch(r);if(canStore(res))await c.put(r,res.clone());return res}catch(err){return await c.match(r)||Response.error()}}));return;}
if(!CORE.includes(u.pathname)&&!/^\/assets\/(?:fonts|brand)\/[a-z0-9._/-]+\.(?:woff2|svg|png)$/i.test(u.pathname))return;
e.respondWith(caches.open(CACHE).then(async c=>{const hit=await c.match(r);if(hit)return hit;const res=await fetch(r);if(canStore(res))await c.put(r,res.clone());return res}));
});