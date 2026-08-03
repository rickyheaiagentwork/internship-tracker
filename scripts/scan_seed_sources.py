#!/usr/bin/env python3
"""Seed-source helper for daily Summer 2027 US undergrad scans.

Pulls community internship lists and prints candidate Apply URLs that look like
Summer 2027 + undergrad-eligible. Eternity/TOAA must still verify each URL
before adding to data/openings.json.
"""
from __future__ import annotations

import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENINGS = ROOT / "data" / "openings.json"

SOURCES = [
    "https://raw.githubusercontent.com/sndsh404/summer-2027-internships/main/README.md",
    "https://raw.githubusercontent.com/speedyapply/2027-SWE-College-Jobs/main/README.md",
]

APPLY_RE = re.compile(r"\[(?:apply|Apply)\]\((https?://[^)]+)\)")
ROW_RE = re.compile(r"^\|([^|]+)\|([^|]+)\|([^|]+)\|.*\[(?:apply|Apply)\]\((https?://[^)]+)\)", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 internship-scanner"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def existing_urls() -> set[str]:
    import json

    if not OPENINGS.exists():
        return set()
    items = json.loads(OPENINGS.read_text())
    urls = set()
    for i in items:
        for k in ("application_url", "posting_url"):
            if i.get(k):
                urls.add(i[k].rstrip("/"))
    return urls


def looks_relevant(company: str, role: str, loc: str) -> bool:
    blob = f"{company} {role} {loc}".lower()
    if "phd" in blob and "bachelor" not in blob and "undergrad" not in blob and "bs" not in blob:
        # keep if role is general SWE intern (often multi-level)
        if "software" not in blob and "engineer" not in blob:
            return False
    if any(x in blob for x in ["fall 2026", "spring 2027", "winter 2027", "co-op"]):
        if "summer 2027" not in blob and "2027 internship" not in blob:
            return False
    if any(x in blob for x in ["ireland", "dublin", "india", "london", "toronto", "canada"]):
        return False
    return "intern" in blob or "internship" in blob


def main() -> None:
    known = existing_urls()
    seen = set()
    print("# Seed candidates (verify before adding)")
    print("# Filters hint: Summer 2027 · US · undergraduate\n")
    for src in SOURCES:
        try:
            text = fetch(src)
        except Exception as e:
            print(f"# FAIL {src}: {e}")
            continue
        print(f"# source: {src}")
        for line in text.splitlines():
            m = ROW_RE.search(line)
            if not m:
                continue
            company, role, loc, url = [x.strip() for x in m.groups()]
            if not looks_relevant(company, role, loc):
                continue
            if "2027" not in f"{role} {line}" and "summer 2027" not in line.lower():
                continue
            key = url.rstrip("/")
            if key in known or key in seen:
                continue
            seen.add(key)
            print(f"- {company} | {role} | {loc} | {url}")
        print()
    print(f"# {len(seen)} new-looking candidates (not already in openings.json)")


if __name__ == "__main__":
    main()
