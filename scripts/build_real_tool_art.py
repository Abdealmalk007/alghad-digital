#!/usr/bin/env python3
"""Rebuild branded utility-card illustrations using authentic, locally stored vendor icons.

No network, code execution in images, hotlinking or synthetic vendor branding.
Python 3.12+ / stdlib. The actual icon pixels are supplied by their publishers.
"""
from __future__ import annotations
import base64
import hashlib
from html import escape
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/tools"
LOGO_ROOT = ASSET_ROOT / "vendor"
MAX_LOGO_BYTES = 450000
COLORS = {
    "everything": ("#0f4b6e", "#0b1229", "#78e3ff"),
    "ventoy": ("#255b77", "#171330", "#83f5df"),
    "rufus": ("#20415c", "#0b1933", "#ffd28e"),
    "irfanview": ("#574365", "#1a1c34", "#e0b0ff"),
    "fileconverter": ("#164c53", "#11283e", "#93f1d7"),
    "vlc": ("#5b4627", "#1c2336", "#ffd17c"),
    "fdm": ("#13547a", "#142544", "#94d6ff"),
    "powertoys": ("#1b4c7f", "#161b44", "#9abaff"),
}
def main() -> None:
    catalog = json.loads((ROOT / "assets/tools.json").read_text(encoding="utf-8"))
    records = json.loads((LOGO_ROOT / "SOURCES.json").read_text(encoding="utf-8"))["assets"]
    ids = [item["id"] for item in catalog["items"]]
    if len(ids) != len(set(ids)) or set(ids) != set(COLORS) or set(ids) != set(records):
        raise ValueError("Windows utilities and authenticated vendor art do not match")
    for item in catalog["items"]:
        ident = item["id"]
        name = item["name"]
        if item["image"] != f"assets/tools/{ident}.svg":
            raise ValueError("Unexpected asset reference: " + ident)
        icon = LOGO_ROOT / f"{ident}.png"
        payload = icon.read_bytes()
        actual_sha = hashlib.sha256(payload).hexdigest()
        if payload[:8] != bytes.fromhex("89504e470d0a1a0a"):
            raise ValueError(f"Not a PNG: {ident}")
        if not 500 <= len(payload) <= MAX_LOGO_BYTES or actual_sha != records[ident]["sha256"]:
            raise ValueError(f"Vendor logo integrity mismatch: {ident}")
        grad_a, grad_b, glow = COLORS[ident]
        title = escape(name, quote=True)
        short = escape(item.get("english", name).upper(), quote=True)
        image_b64 = base64.b64encode(payload).decode("ascii")
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 540" role="img" aria-label="Original {title} application icon on an ALGHAD DIGITAL preview card">
  <title>{title} — official application icon</title>
  <desc>Original publisher logo shown on a customized background. Logo rights remain with its publisher.</desc>
  <defs>
    <linearGradient id="back" x2="1" y2="1"><stop stop-color="{grad_a}"/><stop offset="1" stop-color="{grad_b}"/></linearGradient>
    <radialGradient id="glow"><stop stop-color="{glow}" stop-opacity=".24"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>
    <filter id="shadow"><feDropShadow dx="0" dy="14" stdDeviation="20" flood-color="#000" flood-opacity=".30"/></filter>
  </defs>
  <rect width="960" height="540" fill="url(#back)"/>
  <circle cx="745" cy="115" r="330" fill="url(#glow)"/>
  <g stroke="{glow}" stroke-width="1" opacity=".09"><path d="M0 108H960M0 216H960M0 324H960M0 432H960M160 0V540M320 0V540M480 0V540M640 0V540M800 0V540"/></g>
  <rect x="311" y="57" width="338" height="354" rx="48" fill="#061725" fill-opacity=".40" stroke="{glow}" stroke-opacity=".32"/>
  <image x="318" y="81" width="324" height="324" href="data:image/png;base64,{image_b64}" preserveAspectRatio="xMidYMid meet" filter="url(#shadow)"/>
  <text x="52" y="478" fill="#f4faff" font-family="Arial,sans-serif" font-size="27" font-weight="800" letter-spacing="2">{short}</text>
  <text x="909" y="479" fill="{glow}" font-family="Arial,sans-serif" font-size="14" font-weight="700" text-anchor="end" letter-spacing="1">OFFICIAL APP ICON</text>
</svg>
'''
        ET.fromstring(svg)
        dest = ASSET_ROOT / f"{ident}.svg"
        dest.write_text(svg, encoding="utf-8", newline="\n")
        print(f"VERIFIED_VENDOR_ICON={ident} ORIGINAL_LOGO_SHA256={actual_sha[:16]} ART_BYTES={dest.stat().st_size}")
    print("REAL_WINDOWS_TOOL_ICON_ASSETS_PASS", len(ids))
if __name__ == "__main__":
    main()
