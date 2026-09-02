#!/usr/bin/env python3
"""Active internship search: LinkedIn + company careers (no seed lists, no watchlist.

Cron entry point. Modes (auto by ET hour when --mode auto):
  09:00 / 21:00 ET -> careers crawl (rotating company batch)
  12:00 ET         -> LinkedIn Jobs search (rotating PROFILE seed)

Every run also re-verifies existing openings and prunes dead links.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/home/jarvis/.cache/ms-playwright")

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OPENINGS = DATA / "openings.json"
META = DATA / "meta.json"
STATE = DATA / "scan_state.json"

sys.path.insert(0, str(ROOT / "scripts"))
from fit_filters import fetch, make_opening, slug, verify_posting  # noqa: E402
from search_careers import crawl_batch  # noqa: E402
from search_linkedin import search_linkedin  # noqa: E402
from search_targets import batch_companies, linkedin_seed  # noqa: E402

TZ = ZoneInfo("America/New_York")
TODAY = date.today().isoformat()
MAX_NEW = 20


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n")


def load_state() -> dict:
    return load_json(
        STATE,
        {"careers_index": 0, "linkedin_index": 0},
    )


def save_state(state: dict) -> None:
    save_json(STATE, state)


def existing_urls(opens: list[dict]) -> set[str]:
    urls: set[str] = set()
    for o in opens:
        for k in ("application_url", "posting_url"):
            if o.get(k):
                urls.add(o[k].rstrip("/"))
    return urls


def dedupe_ids(opens: list[dict], entry: dict) -> None:
    ids = {o["id"] for o in opens}
    base = entry["id"]
    n = 2
    while entry["id"] in ids:
        entry["id"] = f"{base}-{n}"
        n += 1


def merge_hits(opens: list[dict], hits: list[dict], source: str) -> list[dict]:
    known = existing_urls(opens)
    added: list[dict] = []
    for h in hits:
        if len(added) >= MAX_NEW:
            break
        url = h["url"].rstrip("/")
        if url in known:
            continue
        entry = make_opening(
            h["company"],
            h["title"],
            h["url"],
            loc=h.get("location", "United States"),
            today=TODAY,
            source=h.get("source", source),
            page_text=h.get("page_text", ""),
        )
        if not entry:
            continue
        dedupe_ids(opens, entry)
        opens.append(entry)
        known.add(url)
        added.append(entry)
    return added


def verify_existing(opens: list[dict]) -> tuple[list[dict], int]:
    """Drop dead postings; return (kept, removed_count)."""
    kept: list[dict] = []
    removed = 0
    for o in opens:
        url = o.get("application_url") or o.get("posting_url")
        if not url:
            removed += 1
            continue
        try:
            code, html = fetch(url, timeout=20)
            if code >= 400:
                removed += 1
                continue
            if not verify_posting(url, html):
                removed += 1
                continue
            o["verified_at"] = TODAY
            kept.append(o)
        except Exception:
            # keep on transient network errors
            kept.append(o)
    return kept, removed


def git_commit_push(msg: str) -> bool:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    if not st.stdout.strip():
        print("# no git changes")
        return False
    an = subprocess.check_output(["git", "log", "-1", "--format=%an"], cwd=ROOT, text=True).strip()
    ae = subprocess.check_output(["git", "log", "-1", "--format=%ae"], cwd=ROOT, text=True).strip()
    import os

    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": an,
            "GIT_AUTHOR_EMAIL": ae,
            "GIT_COMMITTER_NAME": an,
            "GIT_COMMITTER_EMAIL": ae,
        }
    )
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, env=env, check=False)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=False)
    return True


def resolve_mode(mode: str) -> str:
    if mode != "auto":
        return mode
    hour = datetime.now(TZ).hour
    if hour == 12:
        return "linkedin"
    return "careers"


def print_summary(mode: str, added: list[dict], removed: int, opens: list[dict], detail: str) -> None:
    print()
    print(f"[RESULT] Active internship search ({mode}) — {TODAY}")
    print(detail)
    if removed:
        print(f"Removed {removed} dead/expired posting(s).")
    print(f"Added {len(added)} new verified opening(s). Tracker: {len(opens)} live roles.")
    if added:
        print("New Apply links:")
        for a in added[:12]:
            print(f"- {a['company']}: {a['role_title']}")
            print(f"  {a['application_url']}")
        if len(added) > 12:
            print(f"  …and {len(added) - 12} more in README")
    elif not removed:
        print("No new verified openings this run.")
    print("README: https://github.com/rickyheaiagentwork/internship-tracker")


async def run_careers(state: dict) -> tuple[list[dict], str]:
    idx = int(state.get("careers_index", 0))
    batch = batch_companies(idx, batch_size=6)
    names = ", ".join(c["name"] for c in batch)
    hits = await crawl_batch(batch)
    state["careers_index"] = idx + 1
    state["last_careers_run"] = TODAY
    return hits, f"Careers crawl: {names} → {len(hits)} raw hit(s)."


async def run_linkedin(state: dict) -> tuple[list[dict], str]:
    idx = int(state.get("linkedin_index", 0))
    query = linkedin_seed(idx)
    hits = await search_linkedin(query, max_results=30)
    state["linkedin_index"] = idx + 1
    state["last_linkedin_run"] = TODAY
    short = query if len(query) <= 80 else query[:77] + "..."
    return hits, f"LinkedIn search: «{short}» → {len(hits)} raw hit(s)."


async def async_main(mode: str) -> int:
    print(f"# active_scan mode={mode} date={TODAY}")
    state = load_state()
    opens: list[dict] = load_json(OPENINGS, [])

    if mode == "careers":
        hits, detail = await run_careers(state)
        source = "careers"
    elif mode == "linkedin":
        hits, detail = await run_linkedin(state)
        source = "linkedin"
    else:
        print(f"unknown mode: {mode}", file=sys.stderr)
        return 2

    added = merge_hits(opens, hits, source)
    opens, removed = verify_existing(opens)

    save_json(OPENINGS, opens)
    meta = load_json(META, {})
    meta["last_full_verify"] = TODAY
    meta["last_active_scan"] = TODAY
    meta["last_scan_mode"] = mode
    meta["last_scan_added"] = len(added)
    meta["last_scan_removed"] = removed
    meta["search_method"] = "active: LinkedIn + company careers (no seed lists)"
    save_json(META, meta)
    save_state(state)

    subprocess.run(["python3", str(ROOT / "scripts" / "sync_readme.py")], cwd=ROOT, check=False)
    if added or removed:
        git_commit_push(f"scan: {mode} {TODAY} (+{len(added)} -{removed})")
    else:
        print("# skip git push — no data changes")

    print_summary(mode, added, removed, opens, detail)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Active internship search (LinkedIn + careers)")
    parser.add_argument("--mode", default="auto", choices=["auto", "careers", "linkedin"])
    args = parser.parse_args()
    mode = resolve_mode(args.mode)
    return asyncio.run(async_main(mode))


if __name__ == "__main__":
    raise SystemExit(main())
