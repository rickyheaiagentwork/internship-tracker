#!/usr/bin/env python3
"""Regenerate README.md apply tables from data/*.json"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "README.md"

HEADER = """# Internship Tracker — Ricky He

**Just use this README.** Click **Apply** — no server, no `index.html` needed.

Verified **{verified}**. Open = live apply link. Watch = not posted yet (don’t invent roles).

**Fit focus:** AI/ML · SWE · Bio-AI · Fall 2026 · Summer 2027  
**Agent rules:** [`ETERNITY.md`](./ETERNITY.md) · **Profile:** [`PROFILE.md`](./PROFILE.md)

---

## Open — Apply now

| Company | Role | Season | Category | Apply |
|---------|------|--------|----------|-------|
"""

WATCH_HEADER = """
---

## Watchlist — check later (no fake Apply links)

| Company | Target | Expected open | Page |
|---------|--------|---------------|------|
"""

FOOTER = """
---

## Eternity scan runs

Eternity should periodically:

1. Search **LinkedIn Jobs** (+ company careers, Greenhouse, Workday) for roles matching [`PROFILE.md`](./PROFILE.md)
2. Keep only **verified** apply URLs
3. Update `data/openings.json` / `data/watchlist.json`
4. Regenerate this README: `python3 scripts/sync_readme.py`
5. Commit — Ricky clicks Apply himself (never auto-submit)

Details in [`ETERNITY.md`](./ETERNITY.md).

Machine-readable copy of the same links: [`data/openings.json`](./data/openings.json).
"""


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|")


def main() -> None:
    meta = json.loads((DATA / "meta.json").read_text())
    opens = json.loads((DATA / "openings.json").read_text())
    watch = json.loads((DATA / "watchlist.json").read_text())
    verified = meta.get("last_full_verify", "unknown")

    lines = [HEADER.format(verified=verified)]
    for i in sorted(opens, key=lambda x: (x.get("tier", 9), x["company"], x["role_title"])):
        url = i.get("application_url") or i.get("posting_url")
        lines.append(
            f"| {esc(i['company'])} | {esc(i['role_title'])} | {i['season']} | {i['category']} | [Apply]({url}) |"
        )
    lines.append(WATCH_HEADER)
    for i in sorted(watch, key=lambda x: (x.get("tier", 9), x["company"])):
        lines.append(
            f"| {esc(i['company'])} | {esc(i['target_role'])} | {esc(i['expected_open'])} | [Careers]({i['careers_url']}) |"
        )
    lines.append(FOOTER)
    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT} ({len(opens)} open, {len(watch)} watch)")


if __name__ == "__main__":
    main()
