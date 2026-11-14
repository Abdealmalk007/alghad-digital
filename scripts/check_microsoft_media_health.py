#!/usr/bin/env python3
"""Read-only HEAD checks for official Microsoft CDN media.

Uses no proxy or repackaging and never downloads large ISO/IMG bodies.
Soft-fails per URL: workflow monitoring should not block news publication when
Microsoft CDN is temporarily unavailable or refuses Actions IP addresses.
"""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen
import os
from software_sources import SOURCES,ALLOWED_HOSTS

TIMEOUT_SECONDS=9

def check(label:str,url:str,minimum:int)->tuple[bool,str]:
    parsed=urlsplit(url)
    if parsed.scheme!="https" or parsed.hostname not in ALLOWED_HOSTS:
        return False,"Unapproved host"
    req=Request(url,method="HEAD",headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/154.0.0.0 Safari/537.36",
        "Accept":"*/*",
    })
    try:
        with urlopen(req,timeout=TIMEOUT_SECONDS) as response:
            final=urlsplit(response.url)
            length=int(response.headers.get("Content-Length") or 0)
            disposition=response.headers.get("Content-Disposition") or ""
            content_type=response.headers.get("Content-Type") or ""
            ok=(response.status==200 and final.hostname==parsed.hostname
                and final.path==parsed.path
                and length==minimum and length>4_000_000_000
                and "attachment" in disposition.lower()
                and "text/html" not in content_type.lower())
            return ok,("HTTP "+str(response.status)+", bytes="+str(length)+", download="+str("attachment" in disposition.lower()))
    except Exception as e:
        return False,type(e).__name__+": "+str(e)[:150]

def main()->int:
    now=datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary=["## Microsoft direct-media availability","",f"Checked UTC: {now}","",
             "| Original file | Language | Link test |","|---|---|---|"]
    good=bad=0
    for source in SOURCES:
        for download in source.downloads:
            label=source.name+" "+download.language
            ok,details=check(label,download.url,download.size_bytes)
            good+=int(ok);bad+=int(not ok)
            print("CDN_HEALTH",label,"OK" if ok else "WARNING",details,flush=True)
            summary.append("| "+source.name+" | "+download.language+" | "+
                ("OK" if ok else "Warning: "+details.replace("|","/"))+" |")
            if not ok:
                print("::warning::Microsoft direct-media link needs review: "+label+" ("+details+")",flush=True)
    summary+=["","A warning does not imply a modified or malicious download. CDN restrictions and regional availability vary."]
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:
            f.write("\n".join(summary)+"\n")
    print("MICROSOFT_DIRECT_MEDIA_HEALTH good="+str(good)+" warnings="+str(bad),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
