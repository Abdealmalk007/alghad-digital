#!/usr/bin/env python3
"""Retrieve verifiable GitHub release publish dates, sizes, and SHA-256 digests.

Source of truth: official GitHub Releases API for already-approved asset URLs only.
Never create new public download links or publish drafts automatically.
If network/API validation fails retain the previous verified snapshot.
"""
from __future__ import annotations
from pathlib import Path
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.request
import time

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"assets"/"release-facts.json"
SOURCE=r'''
const fs=require("fs"),path=require("path"),vm=require("vm");
const context={window:{}}, root=process.argv[1];
vm.runInNewContext(fs.readFileSync(path.join(root,"assets/downloads.js"),"utf8"),
  context,{timeout:1500});
process.stdout.write(JSON.stringify(context.window.AL_GHAD_DOWNLOADS));
'''

def read_manifest():
    out=subprocess.run(["node","-e",SOURCE,str(ROOT)],check=True,
                       capture_output=True,text=True,encoding="utf-8",timeout=16)
    return json.loads(out.stdout)

def fetch(repo,version):
    url=f"https://api.github.com/repos/Abdealmalk007/{repo}/releases/tags/v{version}"
    headers={"User-Agent":"AlghadDigital-OfficialReleases/1.0",
             "Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
    token=os.environ.get("GITHUB_TOKEN","").strip()
    if token:headers["Authorization"]="Bearer "+token
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=17) as r:
        assert r.status==200
        body=r.read(2_000_000)
    return json.loads(body)

def main():
    manifest=read_manifest()
    result={}
    for id in ("stone","marble","hr","reports","download"):
        approved=manifest[id]
        assert approved["channel"]=="preview"
        response=None
        for attempt in range(2):
            try:
                response=fetch(approved["repository"],approved["release"].rsplit("/",1)[-1][1:])
                break
            except Exception as error:
                print("OFFICIAL_RELEASE_FETCH_RETRY="+id+" "+type(error).__name__,file=sys.stderr,flush=True)
                if attempt==0:time.sleep(1)
        if response is None:
            print("SKIPPED_UNVERIFIED_RELEASE="+id,file=sys.stderr,flush=True)
            continue
        assert response.get("draft") is False and response.get("prerelease") is True
        assert response.get("tag_name")==approved["release"].rsplit("/",1)[-1]
        records={asset["browser_download_url"]:asset for asset in response.get("assets",[])}
        assets=[]
        for entry in approved["files"]:
            url=entry["url"]
            asset=records.get(url)
            if not asset or asset.get("size")!=entry["bytes"]:
                raise ValueError(f"Approved asset missing or size mismatch {id} {url}")
            digest=asset.get("digest")
            match=re.fullmatch(r"sha256:([0-9a-fA-F]{64})",digest or "")
            assets.append({
                "name":asset["name"],
                "url":url,
                "bytes":entry["bytes"],
                "sha256":match.group(1).lower() if match else None,
                "recommended":bool(entry["recommended"])
            })
        published=response.get("published_at")
        assert isinstance(published,str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",published)
        result[id]={
            "repository":approved["repository"],
            "version":approved["version"],
            "published_at":published,
            "tag_url":approved["release"],
            "prerelease":True,
            "assets":assets
        }
    if not result:
        raise RuntimeError("All GitHub API release lookups were unavailable")
    payload={
       "version":1,
       "verified_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z"),
       "source":"Official GitHub Releases API; SHA-256 digest fields are supplied by GitHub",
       "releases":result
    }
    stage=OUTPUT.with_suffix(".json.tmp")
    stage.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    stage.replace(OUTPUT)
    print("GITHUB_RELEASE_FACTS_VERIFIED="+str(len(result)))
    print("DIGEST_COUNT="+str(sum(bool(a["sha256"]) for release in result.values() for a in release["assets"])))
    for id,rel in result.items():
        print("RELEASE",id,rel["version"],rel["published_at"])

if __name__=="__main__":
    try:main()
    except Exception as e:
        print("RELEASE_FACTS_FETCH_ERROR="+type(e).__name__+": "+str(e)[:180],file=sys.stderr)
        if OUTPUT.is_file():
            print("PRESERVING_PRIOR_VERIFIED_RELEASE_FACTS",file=sys.stderr)
            raise SystemExit(0)
        raise
