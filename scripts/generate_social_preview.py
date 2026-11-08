#!/usr/bin/env python3
"""Generate an original lightweight 1200x630 social preview for Alghad Digital.
Run locally with Pillow 10+. Asset is committed; CI doesn't require Pillow.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from math import hypot

root=Path(__file__).resolve().parents[1]
output=root/"assets"/"social"/"alghad-digital.png"
output.parent.mkdir(parents=True,exist_ok=True)
W,H=1200,630
im=Image.new("RGB",(W,H))
px=im.load()
for y in range(H):
    for x in range(W):
        glow=max(0,1-hypot((x-945)/940,(y-140)/760))
        c=(x+y)/(W+H)
        px[x,y]=(int(6+11*c+12*glow),int(23+20*c+25*glow),int(40+27*c+31*glow))
d=ImageDraw.Draw(im,"RGBA")
for k in range(0,W+1,74):
    d.line((k,0,k,H),fill=(126,228,225,19),width=1)
for k in range(0,H+1,74):
    d.line((0,k,W,k),fill=(126,228,225,15),width=1)
for radius in (210,280,350,420):
    d.arc((940-radius,295-radius,940+radius,295+radius),220,355,fill=(98,235,216,45),width=2)
d.rounded_rectangle((66,63,1134,570),radius=26,outline=(128,246,223,72),width=2,fill=(11,34,52,90))
# Distinctive geometric angular brand glyph
d.rounded_rectangle((106,118,221,233),radius=21,fill=(31,112,120,95),outline=(98,239,216,230),width=3)
d.line([(130,196),(163,149),(196,196)],fill=(111,244,224,250),width=8,joint="curve")
d.line([(145,187),(182,187)],fill=(111,244,224,210),width=5)
fontdir=Path(r"C:\Windows\Fonts")
def font(file,size):
    return ImageFont.truetype(str(fontdir/file),size)
large=font("segoeuib.ttf",86)
medium=font("segoeuib.ttf",32)
small=font("segoeui.ttf",26)
d.text((107,268),"ALGHAD",font=large,fill=(238,254,252,255),stroke_width=0)
d.text((109,363),"DIGITAL",font=large,fill=(98,241,216,255))
d.rounded_rectangle((106,469,510,521),radius=15,fill=(92,220,206,33),outline=(91,230,215,110),width=1)
d.text((124,479),"PROTECH SOFTWARE",font=medium,fill=(221,254,252,255))
d.text((690,483),"APPS  /  TECH NEWS  /  TOOLS",font=small,fill=(173,213,226,255))
im.save(output,optimize=True,compress_level=9)
assert im.size==(1200,630) and output.stat().st_size<600_000
print("OG_IMAGE="+str(output))
print("SIZE="+str(im.size)+" BYTES="+str(output.stat().st_size))
