#!/usr/bin/env python3
"""Import Summer 2027 US internships from intern-list.com (Jobright mini-sites)."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fit_filters import (  # noqa: E402
    TRADING_SHOP,
    category_for,
    dedupe_openings,
    fit_score,
    looks_candidate,
    normalize_role_title,
    role_fingerprint,
    slug,
)
from import_interndock import (  # noqa: E402
    KEEP_TITLE,
    PRIORITY_CO,
    SKIP_TITLE,
    is_fit,
    parse_directory,
    url_ok,
)

TODAY = date.today().isoformat()
UA = "Mozilla/5.0 internship-internlist-import/1.0"
API = "https://swan-api.jobright.ai/swan/mini-sites/list"
CATEGORIES = [
    "intern:us:swe",
    "intern:us:ml_ai",
    "intern:us:data_analysis",
    "intern:us:product_management",
]
PAGE = 50
MAX_PER_CAT = 400
DOCK = Path("/home/jarvis/.cursor/projects/home-jarvis/uploads/summer-2027-internships-complete-directory-0.md")


def api_list(category: str, position: int, count: int = PAGE, company: str = "") -> dict:
    body: dict = {"category": category}
    if company:
        body["company"] = company
    req = urllib.request.Request(
        f"{API}?position={position}&count={count}",
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "User-Agent": UA,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://www.intern-list.com",
            "Referer": "https://www.intern-list.com/",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get("result") or {}


def fetch_category(category: str) -> list[dict]:
    first = api_list(category, 0)
    total = int(first.get("total") or 0)
    jobs = list(first.get("jobList") or [])
    pos = PAGE
    limit = min(total, MAX_PER_CAT)
    while pos < limit:
        chunk = api_list(category, pos).get("jobList") or []
        if not chunk:
            break
        jobs.extend(chunk)
        pos += PAGE
    return jobs


def summer_2027(props: dict) -> bool:
    hire = (props.get("hireTime") or "").lower()
    title = props.get("title") or ""
    extra = props.get("qualifications") or ""
    if "2026-fall" in hire or "2026-spring" in hire or "2027-spring" in hire:
        return False
    if "spring 2027" in title.lower() and "summer 2027" not in title.lower():
        return False
    if "fall 2026" in title.lower():
        return False
    if "2027-summer" in hire or "summer 2027" in title.lower() or "internships: " in title.lower() and "2027" in title:
        return True
    if "2027" in title and "intern" in title.lower():
        return True
    if looks_candidate(props.get("company", ""), title, props.get("location", ""), page_text=f"{hire} {extra}"):
        return "2027" in f"{hire} {title} {extra}"
    return False


def dock_index(rows: list[dict]) -> dict[str, list[dict]]:
    by: dict[str, list[dict]] = {}
    for r in rows:
        by.setdefault(r["company"].lower().strip(), []).append(r)
        # also short names
        by.setdefault(re.sub(r"[^a-z0-9]+", " ", r["company"].lower()).strip(), []).append(r)
    return by


def match_url(company: str, title: str, idx: dict[str, list[dict]]) -> str | None:
    key = company.lower().strip()
    cands = idx.get(key) or idx.get(re.sub(r"[^a-z0-9]+", " ", key).strip()) or []
    nt = normalize_role_title(title)
    for r in cands:
        if normalize_role_title(r["title"]) == nt:
            return r["url"]
    # looser: shared tokens
    words = set(nt.split())
    best = None
    best_n = 0
    for r in cands:
        other = set(normalize_role_title(r["title"]).split())
        n = len(words & other)
        if n >= 3 and n > best_n:
            best, best_n = r["url"], n
    return best


def main() -> None:
    openings_path = ROOT / "data" / "openings.json"
    opens = json.loads(openings_path.read_text())
    existing_urls = set()
    fps = set()
    for o in opens:
        for k in ("application_url", "posting_url"):
            if o.get(k):
                existing_urls.add(o[k].rstrip("/").lower())
        fps.add(role_fingerprint(o["company"], o["role_title"]))

    dock_rows = [r for r in parse_directory(DOCK) if is_fit(r)]
    idx = dock_index(dock_rows)

    raw: list[dict] = []
    for cat in CATEGORIES:
        jobs = fetch_category(cat)
        print(f"{cat}: {len(jobs)}")
        raw.extend(jobs)

    seen_id: set[str] = set()
    matched: list[dict] = []
    skipped_no_url = 0
    for job in raw:
        jid = job.get("jobId") or ""
        if jid in seen_id:
            continue
        seen_id.add(jid)
        p = job.get("properties") or {}
        company = (p.get("company") or "").strip()
        title = (p.get("title") or "").strip()
        loc = (p.get("location") or "United States").strip()
        if not company or not title:
            continue
        if not summer_2027(p):
            continue
        row = {"company": company, "title": title, "loc": loc, "section": "software engineering", "url": ""}
        if SKIP_TITLE.search(f"{company} {title}"):
            continue
        if TRADING_SHOP.search(f"{company} {title}"):
            continue
        if re.search(r"\b(canada|ontario|india|london|united kingdom)\b", loc, re.I):
            continue
        if not KEEP_TITLE.search(title) and not PRIORITY_CO.search(company):
            continue
        if not looks_candidate(company, title, loc, page_text=str(p.get("hireTime") or "") + " " + (p.get("qualifications") or "")):
            continue
        if fit_score(company, title, loc) < 20 and not KEEP_TITLE.search(title):
            continue
        fp = role_fingerprint(company, title)
        if fp in fps:
            continue
        url = match_url(company, title, idx)
        if not url:
            skipped_no_url += 1
            continue
        if url.rstrip("/").lower() in existing_urls:
            continue
        matched.append({"company": company, "title": title, "loc": loc, "url": url})
        fps.add(fp)
        existing_urls.add(url.rstrip("/").lower())

    print(f"unique_jobs={len(seen_id)} matched_urls={len(matched)} skipped_no_employer_url={skipped_no_url}")

    added: list[dict] = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(url_ok, r["url"]): r for r in matched}
        for fut in as_completed(futs):
            r = futs[fut]
            try:
                ok = fut.result()
            except Exception:
                ok = False
            if not ok:
                continue
            loc = r["loc"]
            if "united states" not in loc.lower() and not loc.lower().startswith("united states"):
                loc = f"United States ({loc})" if loc else "United States"
            score = fit_score(r["company"], r["title"], r["loc"])
            entry = {
                "id": f"{slug(r['company'])}-{slug(r['title'])[:40]}-s27",
                "company": r["company"],
                "role_title": r["title"] if "2027" in r["title"] or "Summer" in r["title"] else f"{r['title']} (Summer 2027)",
                "season": "Summer 2027",
                "listing_status": "open",
                "verified_at": TODAY,
                "posting_url": r["url"],
                "application_url": r["url"],
                "tier": 1 if score >= 100 else 2,
                "category": category_for(r["company"], r["title"]),
                "degree_level": ["BS"],
                "location": loc,
                "work_model": "Onsite",
                "application_status": "Not started",
                "notes": "Verified Summer 2027 US undergrad posting. Re-verify before applying.",
                "fit_score": score,
                "source": "careers",
            }
            n = 2
            base = entry["id"]
            ids = {o["id"] for o in opens} | {a["id"] for a in added}
            while entry["id"] in ids:
                entry["id"] = f"{base}-{n}"
                n += 1
            added.append(entry)
            print(f"+ {entry['company']}: {entry['role_title'][:70]}")

    opens.extend(added)
    opens = dedupe_openings(opens)
    opens.sort(key=lambda x: (x.get("tier", 9), x["company"].lower(), x["role_title"].lower()))
    openings_path.write_text(json.dumps(opens, indent=2) + "\n")
    print(f"added={len(added)} total={len(opens)}")


if __name__ == "__main__":
    main()
