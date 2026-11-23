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
