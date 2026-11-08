#!/usr/bin/env python3
"""Build the approved Alghad A visual identity as deterministic favicon assets.

Dependencies: Python 3.11+ and Pillow (used only during asset generation).
Emits favicon SVG, ICO, PNG sizes, Apple Touch Icon and W3C web app manifest.
No remote images, third-party typography or copyrighted assets.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SCALE = 4
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Alghad Digital — Alghad A">
  <defs>
    <linearGradient id="alghad-bg" x1="0" y1="0" x2="1" y2="1" gradientUnits="objectBoundingBox">
      <stop stop-color="#143b49"/>
      <stop offset="0.53" stop-color="#0a2635"/>
      <stop offset="1" stop-color="#071725"/>
    </linearGradient>
  </defs>
  <rect x="0" y="0" width="64" height="64" rx="15" fill="url(#alghad-bg)"/>
  <rect x="0.7" y="0.7" width="62.6" height="62.6" rx="14.3" fill="none" stroke="#8eeadb" stroke-opacity=".16" stroke-width="1.4"/>
  <path d="M13.5 44.5 32 12l18.5 32.5H13.5Z" fill="none" stroke="#53e6c5" stroke-width="4.5" stroke-linejoin="round"/>
  <path d="m23 44.5 9-17 9 17M18 52h28" fill="none" stroke="#fff" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""
PADDING_BG = (7,23,37,255)
MINT = (83,230,197,255)
WHITE = (255,255,255,255)
RIM = (142,234,219,42)


def build_vector_raster(n: int = 512) -> Image.Image:
    """Draw in the same 64-unit coordinate system as favicon.svg, antialias at 8x."""
    resolution = n * SCALE
    ss = resolution / 64
    pixels = Image.new("RGBA", (resolution, resolution), PADDING_BG)
    rgb = pixels.load()
    for yy in range(resolution):
        for xx in range(resolution):
            t = min(1, max(0, (xx + yy) / (resolution * 2)))
            # Smooth dark-teal to midnight gradient, matching SVG visually.
            if t < .53:
                f = t/.53
                a,b=(20,59,73),(10,38,53)
            else:
                f = (t-.53)/.47
                a,b=(10,38,53),(7,23,37)
            rgb[xx,yy] = (round(a[0]*(1-f)+b[0]*f),
                          round(a[1]*(1-f)+b[1]*f),
                          round(a[2]*(1-f)+b[2]*f),255)

    mask=Image.new("L",(resolution,resolution),0)
    md=ImageDraw.Draw(mask)
    md.rounded_rectangle((0,0,resolution-1,resolution-1),radius=round(15*ss),fill=255)
    pixels.putalpha(mask)
    outline=ImageDraw.Draw(pixels)
    # Border and stroke widths approximate the matching SVG geometry.
    outline.rounded_rectangle((round(.7*ss),round(.7*ss),round(63.3*ss),round(63.3*ss)),
                              radius=round(14.3*ss),outline=RIM,width=max(1,round(1.4*ss)))
    outer=[(13.5,44.5),(32,12),(50.5,44.5),(13.5,44.5)]
    outline.line([(round(x*ss),round(y*ss)) for x,y in outer],fill=MINT,width=round(4.5*ss),joint="curve")
    for x,y in [(13.5,44.5),(32,12),(50.5,44.5)]:
        v=round(2.25*ss)
        outline.ellipse((round(x*ss)-v,round(y*ss)-v,round(x*ss)+v,round(y*ss)+v),fill=MINT)
    stroke=round(3.8*ss)
    for p in [[(23,44.5),(32,27.5),(41,44.5)],[(18,52),(46,52)]]:
        outline.line([(round(x*ss),round(y*ss)) for x,y in p],fill=WHITE,width=stroke,joint="curve")
        for x,y in (p[0],p[-1]):
            v=round((stroke/2))
            outline.ellipse((round(x*ss)-v,round(y*ss)-v,round(x*ss)+v,round(y*ss)+v),fill=WHITE)
    return pixels.resize((n,n),Image.Resampling.LANCZOS)


def main() -> None:
    (ROOT/"favicon.svg").write_text(SVG,encoding="utf-8",newline="\n")
    icon=build_vector_raster()
    for dim,filename in [(16,"favicon-16.png"),(32,"favicon-32.png"),
                          (48,"favicon-48.png"),(180,"apple-touch-icon.png"),
                          (192,"icon-192.png"),(512,"icon-512.png")]:
        icon.resize((dim,dim),Image.Resampling.LANCZOS).save(ROOT/filename,format="PNG",optimize=True)
    icon.save(ROOT/"favicon.ico",format="ICO",
              sizes=[(16,16),(32,32),(48,48),(64,64)],bitmap_format="png")
    manifest={
      "id":"/",
      "name":"Alghad Digital",
      "short_name":"Alghad",
      "description":"ProTech programs, digital tools and technology news",
      "start_url":"/",
      "scope":"/",
      "display":"browser",
      "background_color":"#071725",
      "theme_color":"#071725",
      "lang":"ar",
      "dir":"rtl",
      "icons":[
        {"src":"/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
        {"src":"/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"}
      ]
    }
    (ROOT/"site.webmanifest").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")

    # Compact QA contact sheet (not part of production).
    qa=Path(r"E:\ProTech\AlghadDigitalSite_QA")
    qa.mkdir(parents=True,exist_ok=True)
    canvas=Image.new("RGB",(1000,420),(244,248,251))
    draw=ImageDraw.Draw(canvas)
    for xx,size in [(45,16),(135,32),(260,48),(400,96),(620,192)]:
        scaled=icon.resize((size,size),Image.Resampling.LANCZOS)
        canvas.paste(scaled,(xx,125+(192-size)//2),scaled)
        draw.text((xx,335),str(size)+" px",fill=(20,48,66))
    canvas.save(qa/"Alghad_A_Icon_Preview_v4.png",optimize=True)
    print("FAVICON_ASSETS_CREATED=9")
    for file in ["favicon.svg","favicon.ico","favicon-16.png","favicon-32.png","favicon-48.png",
                 "apple-touch-icon.png","icon-192.png","icon-512.png","site.webmanifest"]:
        print("ASSET="+file+" BYTES="+str((ROOT/file).stat().st_size))
    print("PREVIEW="+str(qa/"Alghad_A_Icon_Preview_v4.png"))


if __name__=="__main__":
    main()
