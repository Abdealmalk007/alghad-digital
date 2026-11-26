#!/usr/bin/env python3
"""ALGHAD DIGITAL V6.2 — original Dawn/G vector identity and matching raster assets."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
NAVY="#101D35"; CYAN="#65E8D5"; BLUE="#78A7FF"; GOLD="#F9C76A"
G=[(30,10),(43,10),(43,18),(33,18),(20,29),(20,38),(29,47),(40,47),(45,42),(45,36),(33,36),(33,28),(53,28),(53,45),(43,55),(26,55),(11,41),(11,25)]
PIXEL=[(48,10),(56,10),(56,18),(48,18)]
points=lambda p:" ".join(f"{x},{y}" for x,y in p)
SVG=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Alghad Digital Dawn G"><rect width="64" height="64" rx="14" fill="{NAVY}"/><polygon points="{points(G)}" fill="{CYAN}"/><polygon points="{points(PIXEL)}" fill="{GOLD}"/></svg>\n'
def build_vector_raster(n=512):
    k=n*4/64; im=Image.new("RGBA",(n*4,n*4),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,n*4-1,n*4-1),radius=round(14*k),fill=NAVY)
    for poly,color in [(G,CYAN),(PIXEL,GOLD)]:
        d.polygon([(round(x*k),round(y*k)) for x,y in poly],fill=color)
    return im.resize((n,n),Image.Resampling.LANCZOS)
def main():
    (ROOT/"favicon.svg").write_text(SVG,encoding="utf8")
    b=ROOT/"assets/brand";b.mkdir(exist_ok=True)
    (b/"dawn-g.svg").write_text(SVG,encoding="utf8")
    icon=build_vector_raster()
    for size,name in [(16,"favicon-16.png"),(32,"favicon-32.png"),(48,"favicon-48.png"),(180,"apple-touch-icon.png"),(192,"icon-192.png"),(512,"icon-512.png")]:
        icon.resize((size,size),Image.Resampling.LANCZOS).save(ROOT/name,optimize=True)
    icon.save(ROOT/"favicon.ico",format="ICO",sizes=[(16,16),(32,32),(48,48),(64,64)],bitmap_format="png")
    manifest=json.loads((ROOT/"site.webmanifest").read_text(encoding="utf8"));manifest.update(theme_color=NAVY,background_color=NAVY)
    (ROOT/"site.webmanifest").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    icon.save(b/"profile-512.png",optimize=True)
    print("DAWN_G_ASSETS_PASS")
if __name__=="__main__":main()
