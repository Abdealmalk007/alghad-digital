#!/usr/bin/env python3
"""Bounded, cached translations for selected attributed TOP 5 titles.

Preserves original publisher title and source URL. If the public API fails,
the original title remains visible with explicit original-language marking.
"""
from __future__ import annotations
import concurrent.futures
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/"assets/top5-translation-cache.json"
ENDPOINT="https://api.mymemory.translated.net/get"
EMAIL="protech.2025.2026@gmail.com"
MAX_NEW=18
MAX_CHARS=4500
AR=re.compile(r"[\u0621-\u064a]")
EN=re.compile(r"[a-zA-Z]")
UNWANTED=re.compile(r"MYMEMORY WARNING|QUOTA EXCEEDED|YOU USED ALL AVAILABLE|PLEASE ENTER",re.I)

def translate(raw: str, language: str) -> str | None:
    pair="en|ar" if language=="ar" else "ar|en"
    if len(raw)>300 or not raw.strip():return None
    try:
        q=urllib.parse.urlencode({"q":raw,"langpair":pair,"de":EMAIL})
        req=urllib.request.Request(ENDPOINT+"?"+q,headers={"User-Agent":"ALGHAD-TOP5/1.0"})
        with urllib.request.urlopen(req,timeout=7) as response:
            if response.status!=200:return None
            info=json.loads(response.read(50000))
        result=html.unescape(str(info.get("responseData",{}).get("translatedText",""))).strip()
        result=re.sub(r"\s+"," ",result)
        if not 8<=len(result)<=420 or result==raw or "<" in result or UNWANTED.search(result):
            return None
        if language=="ar" and len(AR.findall(result))<5:return None
        if language=="en" and len(EN.findall(result))<10:return None
        return result
    except (ValueError,KeyError,OSError,TimeoutError):
        return None

def enrich(topics: dict[str,list[dict]]) -> dict[str,list[dict]]:
    state=json.loads(CACHE.read_text(encoding="utf8")) if CACHE.is_file() else {"version":1,"pairs":{}}
    saved=state.setdefault("pairs",{})
    needed={}
    for records in topics.values():
        for a in records:
            for language in ("ar","en"):
                if a.get("title_"+language):continue
                original=a["original_title"]
                if language=="ar" and AR.search(original):continue
                if language=="en" and not AR.search(original):continue
                key=language+":"+hashlib.sha256(original.encode("utf8")).hexdigest()
                needed[key]=(original,language)
    used=0
    # Reuse successful translations before new API calls.
    for records in topics.values():
        for a in records:
            for language in ("ar","en"):
                key=language+":"+hashlib.sha256(a["original_title"].encode("utf8")).hexdigest()
                if not a.get("title_"+language) and key in saved:
                    a["title_"+language]=saved[key]
                    a["translation_status_"+language]="machine_cached"
    outstanding=[(key,value) for key,value in needed.items() if key not in saved]
    candidates=[]
    for key,entry in outstanding:
        if len(candidates)>=MAX_NEW:break
        if used+len(entry[0])>MAX_CHARS:break
        candidates.append((key,*entry))
        used+=len(entry[0])
    if candidates:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            translations=list(pool.map(lambda row:translate(row[1],row[2]),candidates))
        for (key,original,language),value in zip(candidates,translations):
            if value:saved[key]=value
        if translations.count(None):
            print("TOP5_TRANSLATION_UNAVAILABLE",translations.count(None),"out of",len(candidates))
    for records in topics.values():
        for a in records:
            for language in ("ar","en"):
                key=language+":"+hashlib.sha256(a["original_title"].encode("utf8")).hexdigest()
                if not a.get("title_"+language) and key in saved:
                    a["title_"+language]=saved[key]
                    a["translation_status_"+language]="machine"
    if not CACHE.is_file() or json.loads(CACHE.read_text(encoding="utf8"))!=state:
        CACHE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    return topics
