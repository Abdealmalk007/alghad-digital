#!/usr/bin/env python3
"""Generate branded social/cover images with the exact Dawn G emblem."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from generate_brand_icons import build_vector_raster,NAVY,CYAN,GOLD,BLUE
root=Path(__file__).resolve().parents[1]
fontdir=Path(r"C:\Windows\Fonts")
def font(name,size):return ImageFont.truetype(str(fontdir/name),size)
def cover(w,h,out):
    im=Image.new("RGB",(w,h),NAVY);d=ImageDraw.Draw(im)
    scale=w/1200
    def p(x,y):return round(x*scale),round(y*scale)
    d.polygon([p(850,0),p(1200,0),p(1200,630),p(690,630)],fill="#1B304D")
    for x in range(900,1200,44):
        for y in range(40,630,44):
            d.ellipse((*p(x,y),*p(x+3,y+3)),fill="#354B68")
    emblem=build_vector_raster(round(290*scale))
    im.paste(emblem,p(835,155),emblem)
    d.text(p(66,112),"ALGHAD",font=font("segoeuib.ttf",round(92*scale)),fill="#F1F6FF")
    d.text(p(66,215),"DIGITAL",font=font("segoeuib.ttf",round(92*scale)),fill=CYAN)
    d.text(p(70,341),"SOFTWARE  /  TECH  /  TOOLS",font=font("segoeui.ttf",round(27*scale)),fill="#B4C5D9")
    d.rectangle((*p(70,414),*p(145,421)),fill=GOLD)
    d.text(p(70,465),"PROTECH SOFTWARE",font=font("segoeuib.ttf",round(26*scale)),fill=BLUE)
    d.text(p(70,518),"alghad.digital",font=font("segoeui.ttf",round(26*scale)),fill="#F1F6FF")
    im.save(out,optimize=True)
cover(1200,630,root/"assets/social/alghad-digital.png")
cover(1500,788,root/"assets/brand/cover.png")
print("DAWN_SOCIAL_PASS")
