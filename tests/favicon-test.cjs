"use strict";
/* Auditable checks for the approved Alghad A favicon family. */
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");

const root=path.resolve(__dirname,"..");
const load=name=>fs.readFileSync(path.join(root,name));
const text=name=>load(name).toString("utf8");
const pngMagic=Buffer.from("89504e470d0a1a0a","hex");
const dimensions=[
  ["favicon-16.png",16],["favicon-32.png",32],["favicon-48.png",48],
  ["apple-touch-icon.png",180],["icon-192.png",192],["icon-512.png",512]
];
for(const [filename,size] of dimensions){
  const bytes=load(filename);
  assert.ok(bytes.length>100,"Nonempty "+filename);
  assert.ok(bytes.subarray(0,8).equals(pngMagic),"Valid PNG: "+filename);
  assert.equal(bytes.readUInt32BE(16),size,"PNG width: "+filename);
  assert.equal(bytes.readUInt32BE(20),size,"PNG height: "+filename);
  const ct=bytes.readUInt8(25);
  assert.ok([2,6].includes(ct),"RGB/RGBA PNG: "+filename);
}
const ico=load("favicon.ico");
assert.equal(ico.readUInt16LE(0),0);
assert.equal(ico.readUInt16LE(2),1);
assert.equal(ico.readUInt16LE(4),4);
const icoSizes=[];
for(let i=0;i<4;i++){
  const entry=6+i*16;
  const w=ico[entry]||256;
  const h=ico[entry+1]||256;
  assert.equal(w,h,"ICO square frame");
  const length=ico.readUInt32LE(entry+8);
  const offset=ico.readUInt32LE(entry+12);
  assert.ok(length>120&&offset>=70&&offset+length<=ico.length,"ICO frame bounds");
  icoSizes.push(w);
}
assert.deepEqual(icoSizes.sort((a,b)=>a-b),[16,32,48,64]);
const svg=text("favicon.svg");
assert.match(svg,/viewBox="0 0 64 64"/);
assert.match(svg,/#53e6c5/);
assert.match(svg,/stroke="#fff"/);
assert.match(svg,/fill="url\(#alghad-bg\)"/);
assert.doesNotMatch(svg,/<script\b|<foreignObject\b|(?:xlink:)?href=|javascript:/i);

const manifest=JSON.parse(text("site.webmanifest"));
assert.equal(manifest.name,"Alghad Digital");
assert.equal(manifest.start_url,"/");
assert.equal(manifest.scope,"/");
assert.equal(manifest.theme_color,"#071725");
assert.deepEqual(manifest.icons.map(i=>i.sizes),["192x192","512x512"]);
for(const icon of manifest.icons){
  assert.equal(icon.type,"image/png");
  assert.ok(fs.existsSync(path.join(root,icon.src.slice(1))));
}
const pageNames=["index.html","programs/index.html","news/index.html",
 "free-windows-tools/index.html","ai-news/index.html","tech-companies/index.html","cars/index.html","protech/index.html","about/index.html","security/index.html","privacy/index.html"];
for(const slug of ["stone","marble","reports","hr","download",
                   "kitchen","care","quotes","tv"]){
 pageNames.push("programs/"+slug+"/index.html");
}
for(const p of pageNames){
  const html=text(p);
  for(const ref of ["/favicon.svg?v=4","/favicon.ico?v=4","/favicon-16.png?v=4",
                    "/favicon-32.png?v=4","/favicon-48.png?v=4",
                    "/apple-touch-icon.png?v=4","/site.webmanifest"]){
    assert.ok(html.includes(ref),"Icon tag missing in "+p+": "+ref);
  }
  assert.ok(html.includes("<link rel=\"canonical\""),"Canonical retained: "+p);
}
const main=text("index.html");
assert.ok(main.includes("M13.5 44.5 32 12l18.5 32.5H13.5Z"),
  "Visible main navigation monogram must match favicon");
const subpage=text("programs/download/index.html");
assert.ok(subpage.includes('src="../../icon-192.png?v=4"'),
  "Static landing pages must use the new icon");
console.log("FAVICON_QA_PASS PNG=6 ICO_SIZES="+icoSizes.join(",")+
            " SVG=1 MANIFEST=1 INDEXABLE_PAGES="+pageNames.length);
