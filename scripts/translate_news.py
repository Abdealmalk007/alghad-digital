#!/usr/bin/env python3
"""Translate English RSS news headlines to Arabic with a verified free translation API.

Python 3.12, standard library only.
Source links, original titles, timestamps and publisher attribution are immutable.
Outputs: assets/news[.json,-data.js], assets/industry-news[.json,-data.js],
         assets/translation-cache.json (stable reusable cache).
New English headlines are sent to MyMemory Translation API (en|ar) with the public
project contact email for its documented free character quota; no API secrets.
On API errors, the English original remains visible with an explicit untranslated label.
"""

from __future__ import annotations

import concurrent.futures
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "assets" / "translation-cache.json"
TRANSLATION_ENDPOINT = "https://api.mymemory.translated.net/get"
PUBLIC_CONTACT = "protech.2025.2026@gmail.com"
API_TIMEOUT = 14
MAX_DAILY_CHARS = 16000
MAX_CALLS = 90
ARABIC_LETTERS = re.compile(r"[\u0621-\u064a]")
UNWANTED = re.compile(r"MYMEMORY WARNING|YOU USED ALL AVAILABLE FREE TRANSLATIONS|QUOTA EXCEEDED|PLEASE ENTER YOUR", re.I)
ENGLISH_WORDS = re.compile(r"[A-Za-z]{2,}")


def cache_key(title: str) -> str:
    return hashlib.sha256(title.strip().encode("utf-8")).hexdigest()


def is_english_title(title: str) -> bool:
    """Translate whole-English headlines, not Arabic text with English brand names."""
    return bool(ENGLISH_WORDS.search(title)) and not bool(ARABIC_LETTERS.search(title))


def valid_translation(english: str, translation: object) -> bool:
    if not isinstance(translation, str):
        return False
    candidate = re.sub(r"\s+", " ", html.unescape(translation)).strip()
    return (4 <= len(candidate) <= 500 and
            len(ARABIC_LETTERS.findall(candidate)) >= 4 and
            candidate.casefold() != english.strip().casefold() and
            not UNWANTED.search(candidate) and
            not re.search(r"<[^>]*>", candidate))


def translate_title(english: str, *, email: str = PUBLIC_CONTACT) -> str | None:
    if not is_english_title(english):
        return None
    if len(english.encode("utf-8")) > 500:
        return None
    params = urllib.parse.urlencode({
        "q": english,
        "langpair": "en|ar",
        "de": email,
        "mt": "1",
    })
    request = urllib.request.Request(
        TRANSLATION_ENDPOINT + "?" + params,
        headers={
            "User-Agent": "AlghadDigital/1.0 (+https://alghad.digital/)",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
            if response.status != 200:
                return None
            obj = json.loads(response.read(35000))
        if int(obj.get("responseStatus", 0)) != 200 or obj.get("quotaFinished") is True:
            return None
        value = obj.get("responseData", {}).get("translatedText", "")
        if not valid_translation(english, value):
            return None
        return re.sub(r"\s+", " ", html.unescape(value)).strip()
    except (OSError, ValueError, KeyError, TimeoutError, json.JSONDecodeError):
        return None


def read_cache() -> dict[str, str]:
    if not CACHE.exists():
        return {}
    try:
        obj = json.loads(CACHE.read_text(encoding="utf-8"))
        if obj.get("version") != 1 or not isinstance(obj.get("entries"), dict):
            return {}
        return {k: v for k, v in obj["entries"].items()
                if isinstance(k, str) and re.fullmatch("[0-9a-f]{64}", k)
                and valid_translation("_untranslated_", v)}
    except (OSError, ValueError, TypeError):
        return {}


def read_news() -> tuple[dict, dict]:
    general = json.loads((ROOT / "assets" / "news.json").read_text(encoding="utf-8"))
    industry = json.loads((ROOT / "assets" / "industry-news.json").read_text(encoding="utf-8"))
    assert isinstance(general["articles"], list) and general["articles"]
    assert set(industry["topics"]) == {"ai", "companies", "cars"}
    return general, industry


def collect_titles(general: dict, industry: dict) -> list[str]:
    titles = {
        item["title"] for item in general["articles"]
        if isinstance(item.get("title"), str) and is_english_title(item["title"])
    }
    for section in industry["topics"].values():
        titles.update(
            item["title"] for item in section["articles"]
            if isinstance(item.get("title"), str) and is_english_title(item["title"])
        )
    return sorted(titles)


def resolve_translations(titles: list[str], cached: dict[str, str]) -> tuple[dict[str, str], int, int]:
    unique = {cache_key(t): t for t in titles}
    missing = [(key, title) for key, title in unique.items() if key not in cached]
    selected = []
    chars = 0
    for key, title in missing:
        length = len(title)
        if len(title.encode("utf-8")) > 500:
            continue
        if len(selected) >= MAX_CALLS or chars + length > MAX_DAILY_CHARS:
            break
        selected.append((key, title))
        chars += length

    print(f"TRANSLATION_REQUESTS={len(selected)} REUSED={len(unique)-len(missing)} CHARS={chars}", flush=True)
    # Maximum of three workers: conservative request pacing, 7-minute workflow cap.
    def request_one(pair: tuple[str, str]) -> tuple[str, str | None]:
        key, title = pair
        return key, translate_title(title)

    success = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for key, translation in executor.map(request_one, selected):
            if translation:
                cached[key] = translation
                success += 1
    return cached, success, len(missing)


def decorate_item(item: dict, cached: dict[str, str]) -> str:
    original = item["title"]
    if not is_english_title(original):
        item["title_ar"] = original
        item["translation_status"] = "original_ar"
        item.pop("translation_provider", None)
        return "original_ar"

    translated = cached.get(cache_key(original))
    if translated and valid_translation(original, translated):
        item["title_ar"] = translated
        item["translation_status"] = "machine"
        item["translation_provider"] = "MyMemory"
        return "machine"

    item["title_ar"] = None
    item["translation_status"] = "unavailable"
    item.pop("translation_provider", None)
    return "unavailable"


def stage(path: Path, text: str) -> Path:
    tmp = path.with_suffix(path.suffix + ".translation-tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    return tmp


def write_snapshots(general: dict, industry: dict, cached: dict[str, str]) -> None:
    cache_text = json.dumps({"version": 1, "provider": "MyMemory Translation API",
                             "language_pair": "en|ar", "entries": cached},
                            ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    summary = ("Machine-translated headlines are for convenience and may be imperfect. "
               "The original source headline remains available. Translation is by Alghad Digital, "
               "not the original publisher.")
    general["translation_note"] = summary
    industry["translation_note"] = summary
    industry["language_note"] = (
        "Arabic machine translations are displayed when available; original-language "
        "headlines and official source links are preserved."
    )

    outputs = {
        ROOT / "assets" / "news.json": json.dumps(general, ensure_ascii=False, indent=2) + "\n",
        ROOT / "assets" / "news-data.js": "window.AL_GHAD_NEWS = " +
             json.dumps(general, ensure_ascii=True, separators=(",", ":")) + ";\n",
        ROOT / "assets" / "industry-news.json": json.dumps(industry, ensure_ascii=False, indent=2) + "\n",
        ROOT / "assets" / "industry-news-data.js": "window.AL_GHAD_INDUSTRY_NEWS = " +
             json.dumps(industry, ensure_ascii=True, separators=(",", ":")) + ";\n",
        CACHE: cache_text,
    }
    staged = [(target, stage(target, contents)) for target, contents in outputs.items()]
    for target, tmp in staged:
        tmp.replace(target)


def main() -> int:
    general, industry = read_news()
    titles = collect_titles(general, industry)
    cached = read_cache()
    cached, new_success, missing = resolve_translations(titles, cached)
    statuses = {"machine": 0, "original_ar": 0, "unavailable": 0}
    for item in general["articles"]:
        statuses[decorate_item(item, cached)] += 1
    for section in industry["topics"].values():
        for item in section["articles"]:
            statuses[decorate_item(item, cached)] += 1

    # Keep a bounded cache of current headlines and cached news still in active rotation.
    keys = {cache_key(title) for title in titles}
    cached = {key: value for key, value in cached.items() if key in keys}
    write_snapshots(general, industry, cached)
    print("TRANSLATION_NEW_SUCCESS=" + str(new_success))
    print("TRANSLATION_STILL_MISSING=" + str(statuses["unavailable"]))
    print("TRANSLATION_MACHINE_ITEMS=" + str(statuses["machine"]))
    print("TRANSLATION_ORIGINAL_AR_ITEMS=" + str(statuses["original_ar"]))
    print("TRANSLATION_CACHE_ENTRIES=" + str(len(cached)))
    if statuses["unavailable"]:
        print("WARNING: Some untranslated English headlines remain marked unavailable; source links preserved.",file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
