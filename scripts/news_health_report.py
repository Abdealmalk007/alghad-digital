from __future__ import annotations
"""Summarize news freshness in Actions logs without inventing or suppressing headlines.

Python >=3.12, standard library only. Does not alter or send news data.
If feeds contain no recent headlines, emit a visible warning but preserve the
attributed old snapshot; a feed quiet period is not a publishing failure.
"""
import datetime as dt
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NOW=dt.datetime.now(dt.timezone.utc)
DATASETS={
    "General news": ROOT/"assets/news.json",
    "Official AI, companies and cars": ROOT/"assets/industry-news.json",
}

def date_of(value:str)->dt.datetime:
    value=(value or "").strip()
    if not value:
        raise ValueError("Missing date")
    return dt.datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(dt.timezone.utc)

def analyze(name:str,path:Path)->tuple[str,int,float,float]:
    payload=json.loads(path.read_text(encoding="utf-8"))
    created=date_of(payload["generated_at"])
    if name=="General news":
        articles=payload["articles"]
    else:
        topics=payload["topics"]
        assert set(topics)=={"ai","companies","cars"}
        articles=[a for section in topics.values() for a in section["articles"]]
    assert articles and all(isinstance(a.get("published_at"),str) for a in articles)
    newest=max(date_of(a["published_at"]) for a in articles)
    age=max(0.0,(NOW-newest).total_seconds()/3600)
    snapshot_age=max(0.0,(NOW-created).total_seconds()/3600)
    return name,len(articles),age,snapshot_age

def main()->int:
    results=[analyze(name,path) for name,path in DATASETS.items()]
    lines=["## News freshness verification","",
           f"UTC check: {NOW.isoformat(timespec='seconds')}","",
           "| Source | Articles | Newest headline age | Snapshot age |",
           "|---|---:|---:|---:|"]
    for name,count,article_age,snapshot_age in results:
        print(f"NEWS_HEALTH {name}: items={count} newest_age_hours={article_age:.1f} snapshot_age_hours={snapshot_age:.1f}",flush=True)
        lines.append(f"| {name} | {count} | {article_age:.1f} h | {snapshot_age:.1f} h |")
        if article_age>36:
            print(f"::warning::No recent headlines in {name} feed snapshot; newest item is {article_age:.1f} hours old.",flush=True)
        if snapshot_age>12:
            print(f"::warning::Snapshot creation of {name} is {snapshot_age:.1f} hours old.",flush=True)
    lines += ["","GitHub scheduled workflows are best-effort; the extra scheduled runs provide redundancy, not a guaranteed wall-clock execution time."]
    print("\n".join(lines),flush=True)
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("\n".join(lines)+"\n")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
