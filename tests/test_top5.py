#!/usr/bin/env python3
"""Offline unit tests: genuine content, ranking, recency, safe URLs and empty feeds."""
from pathlib import Path
import datetime as dt
import importlib.util
import sys
from unittest.mock import patch
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/"scripts"))
import build_top5 as app
cfg=app.load("config/top5_categories.json")
now=app.NOW
def item(title,url,date,source="qa",topic="",official=False):
    return dict(original_title=title,url=url,source=source,source_name="Official QA Source",
                published_at=app.iso(date),fetched_at=app.iso(now),
                title_en=title,title_ar="",summary_en="",summary_ar="",topic=topic,official=official)
items=[
    item("New Windows security update for enterprise PC", "https://example.com/a",now-dt.timedelta(hours=10)),
    item("Windows browser update fixes vulnerability", "https://example.com/b",now-dt.timedelta(hours=20),"qa2"),
    item("Windows software update announced yesterday", "https://example.com/c",now-dt.timedelta(hours=40),"qa3"),
    item("Windows patch for enterprise laptops", "https://example.com/d",now-dt.timedelta(hours=75),"qa4"),
    item("Windows patch almost one month old", "https://example.com/e",now-dt.timedelta(days=12)),
    item("Cyber Monday sale: Windows app discounts", "https://example.com/f",now-dt.timedelta(hours=1)),
]
selected=app.select(items,cfg)
windows=selected["windows"]
assert len(windows)==4,len(windows)
assert [a["url"] for a in windows]==[
    "https://example.com/a","https://example.com/b","https://example.com/c","https://example.com/d"
],windows
assert len({a["url"] for a in windows})==len(windows)
assert all(a["rank"]==i for i,a in enumerate(windows,1))
assert not app.good_url("javascript:alert(1)")
assert not app.good_url("https://localhost/bad")
assert not app.good_url("https://evil.example.com/news","example.org")
assert not app.good_url("https://user:pass@legit.example.org/x")
assert app.good_url("https://news.example.org/real?utm_source=spam&id=3","example.org")=="https://news.example.org/real?id=3"
empty=app.select([],cfg)
assert all(not x for x in empty.values()),empty
try:
    app.validate(cfg,{"topics":{cat["id"]:[] for cat in cfg["categories"]},"max_items":5})
except Exception:
    raise
print("TOP5_UNIT_TEST_PASS categories=11 recency_buckets=yes promo_exclusion=yes URL_validation=yes empty_feeds=yes")

# Numerical fidelity must survive both fresh and cached translations.
import translate_news as translation
import top5_translate
import tempfile
import json
assert translation.same_numeric_facts("2027 and 1,100Hz", "٢٠٢٧ و١١٠٠ هرتز")
assert translation.same_numeric_facts("v3.3.1", "الإصدار ۳.۳.۱")
assert not translation.same_numeric_facts("2027", "٢٠٢٠")
assert not translation.same_numeric_facts("v3.3.1", "الإصدار 3.3.2")
assert not translation.valid_translation("Fiscal year 2027", "السنة المالية 2020")
assert translation.valid_translation("Fiscal year 2027", "السنة المالية ٢٠٢٧")
title="Fiscal year 2027"
key=translation.cache_key(title)
with patch.object(translation, "translate_title", return_value=None):
    cache, success, missing=translation.resolve_translations([title],{key:"السنة المالية 2020"})
    assert key not in cache and success==0 and missing==1
    article={"title":title}
    assert translation.decorate_item(article,cache)=="unavailable"
    assert article["title_ar"] is None
with tempfile.TemporaryDirectory() as temp:
    cache_path=Path(temp)/"cache.json"
    cache_path.write_text(json.dumps({"version":1,"pairs":{"ar:"+key:"السنة المالية 2020"}}),encoding="utf8")
    row={"original_title":title,"title_en":title,"title_ar":"السنة المالية 2020"}
    with patch.object(top5_translate,"CACHE",cache_path), patch.object(top5_translate,"translate",return_value=None):
        top5_translate.enrich({"test":[row]})
    assert row["title_ar"]==""
    assert not json.loads(cache_path.read_text(encoding="utf8"))["pairs"]
print("TRANSLATION_NUMERIC_INTEGRITY_PASS")

# Global uniqueness and specialist-first allocation.
rows=[a for section in selected.values() for a in section]
assert len(rows)==len({a["url"] for a in rows})
assert len(rows)==len({app.normalized_title(a["original_title"]) for a in rows})
assert all(a["url"] not in {x["url"] for x in windows} for a in selected["tech"])
app.validate(cfg,{"topics":selected})
print("TOP5_CROSS_CATEGORY_DEDUP_PASS")

car_items=[
    item("The 2027 Toyota 4Runner: Legendary Capability, Refined for the Road Ahead","https://example.com/4runner",now-dt.timedelta(hours=66),"toyota","cars",True),
    item("The 2027 Toyota Tacoma: Legendary Off-Road Prowess Enhanced by Streamlined Technology","https://example.com/tacoma",now-dt.timedelta(hours=67),"toyota","cars",True),
]
assert len(app.select(car_items,cfg)["cars"])==2
print("TOP5_CAR_MODEL_CLASSIFICATION_PASS")
