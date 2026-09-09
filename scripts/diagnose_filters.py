#!/usr/bin/env python3
"""Funnel diagnostic for the internship filters.

  capture  — pull RAW LinkedIn cards for a set of probe queries, save to a corpus file
  replay   — run the saved corpus through every filter stage and report where roles die

Nothing here writes to data/openings.json; it only measures the filters.
"""
from __future__ import annotations

import argparse
import asyncio
import collections
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CORPUS = Path("/tmp/eternity_corpus.json")
PAGE_CACHE = Path("/tmp/eternity_pages")

PROBE_QUERIES = [
    'internship "Summer 2027" "United States"',
    'internship "Summer 2027" software engineer',
    'internship "Summer 2027" ("machine learning" OR "data science" OR "artificial intelligence")',
    '"Summer 2027" intern (data OR analytics OR "data engineering")',
    '"Summer 2027" intern (biomedical OR clinical OR pharmaceutical OR biotech)',
    '"Summer 2027" intern (cybersecurity OR "information technology" OR cloud OR devops)',
    '"Summer 2027" ("summer analyst" OR "co-op" OR "university program") technology',
    '2027 summer intern hardware OR electrical OR robotics',
]


async def grab(query: str, max_scroll: int = 6) -> list[dict]:
    from playwright.async_api import async_playwright

    url = (
        "https://www.linkedin.com/jobs/search/?"
        f"keywords={quote_plus(query)}&location=United%20States&f_E=1&f_TPR=r604800"
    )
    out: list[dict] = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        ctx = await b.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4)
            for _ in range(max_scroll):
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(1)
            cards = await page.query_selector_all("div.base-card, div.job-search-card")
            seen: set[str] = set()
            for c in cards:
                le = await c.query_selector("a[href*='/jobs/view/']")
                if not le:
                    continue
                href = await le.get_attribute("href")
                te = await c.query_selector("h3, .base-search-card__title")
                ce = await c.query_selector("h4, .base-search-card__subtitle")
                loce = await c.query_selector(".job-search-card__location")
                title = ((await te.inner_text()) if te else "").strip()
                comp = ((await ce.inner_text()) if ce else "").strip()
                loc = ((await loce.inner_text()) if loce else "United States").strip()
                key = re.sub(r"\?.*$", "", href or "")
                if not title or not comp or key in seen:
                    continue
                seen.add(key)
                out.append(
                    {"company": comp, "title": title, "location": loc, "url": key, "query": query}
                )
        finally:
            await b.close()
    return out


async def capture(queries: list[str]) -> None:
    rows: list[dict] = []
    seen: set[str] = set()
    for q in queries:
        got = await grab(q)
        new = 0
        for r in got:
            if r["url"] in seen:
                continue
            seen.add(r["url"])
            rows.append(r)
            new += 1
        print(f"# {len(got):3} cards ({new:3} new) — {q}", flush=True)
    CORPUS.write_text(json.dumps(rows, indent=2))
    print(f"\nSaved {len(rows)} unique raw cards → {CORPUS}")


def _page(url: str, ff) -> tuple[str, str]:
    """Fetched HTML for a URL, cached on disk so replays are cheap."""
    PAGE_CACHE.mkdir(exist_ok=True)
    key = PAGE_CACHE / (re.sub(r"[^a-z0-9]+", "-", url.lower())[-120:] + ".html")
    if key.exists():
        body = key.read_text()
        return ("error" if body.startswith("\x00ERR") else "ok"), body
    try:
        code, html = ff.fetch(url, timeout=15)
        if code >= 400:
            html = f"\x00ERR http {code}"
    except Exception as exc:
        html = f"\x00ERR {type(exc).__name__}"
    key.write_text(html)
    return ("error" if html.startswith("\x00ERR") else "ok"), html


def replay(show: str | None, limit: int, offline: bool) -> None:
    import fit_filters as ff

    rows = json.loads(CORPUS.read_text())
    stages: collections.Counter = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)

    for r in rows:
        company, title, loc = r["company"], r["title"], r["location"]
        label = f"{company[:24]:24} | {title[:70]}"
        # Stage 1: title screen (as LinkedIn mode calls it — query text supplies the year)
        reason = ff.reject_reason(company, title, loc, r.get("query", ""))
        if reason:
            stages[f"1-{reason}"] += 1
            examples[f"1-{reason}"].append(label)
            continue
        score = ff.fit_score(company, title, loc)
        if offline:
            stages[f"KEPT-tier{ff.tier_for(score)}"] += 1
            examples[f"KEPT-tier{ff.tier_for(score)}"].append(
                f"{label}  [score={score} {ff.category_for(company, title)}]"
            )
            continue
        # Stage 2: live page verification
        state, html = _page(r["url"], ff)
        if state == "error":
            stages["2-fetch_error"] += 1
            examples["2-fetch_error"].append(f"{label}  [{html[:40]}]")
            continue
        info = ff.verify_posting(r["url"], html)
        if not info:
            stages["3-verify_posting"] += 1
            examples["3-verify_posting"].append(f"{label}  [{len(html)}b]")
            continue
        bucket = f"KEPT-{info['confidence']}"
        stages[bucket] += 1
        examples[bucket].append(
            f"{label}  [score={score} tier{ff.tier_for(score)} {ff.category_for(company, title)}]"
        )

    total = len(rows)
    kept = sum(v for k, v in stages.items() if k.startswith("KEPT"))
    print(f"\n=== funnel over {total} raw cards — kept {kept} ({kept/total:.1%}) ===")
    for k, v in sorted(stages.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"{v:4}  ({v/total:5.1%})  {k}")

    if show:
        print(f"\n=== {show} (first {limit}) ===")
        for line in examples.get(show, [])[:limit]:
            print(f"  {line}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["capture", "replay"])
    ap.add_argument("--show", help="stage name to list examples for")
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--offline", action="store_true", help="skip live verification (replay)")
    ap.add_argument("--query", action="append", help="override probe queries (capture)")
    args = ap.parse_args()

    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/home/jarvis/.cache/ms-playwright")
    if args.action == "capture":
        asyncio.run(capture(args.query or PROBE_QUERIES))
    else:
        replay(args.show, args.limit, args.offline)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
