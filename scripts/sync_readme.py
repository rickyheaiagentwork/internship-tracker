#!/usr/bin/env python3
"""Regenerate README.md apply tables from data/openings.json"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "README.md"

HEADER = """# Internship Tracker — Ricky He

**Just use this README.** Click **Apply** — no server needed.

Verified **{verified}**. Every role below was found by **active search** (LinkedIn + company career sites).

**Filters:** Summer 2027 · United States · Undergraduate (BS)  
**Focus:** AI/ML · biomedical / pharma data · financial & investment analytics  
**Portfolio:** [ricky-s-portfolio-olive.vercel.app](https://ricky-s-portfolio-olive.vercel.app/) · [`PORTFOLIO.md`](./PORTFOLIO.md) · [Resume](https://ricky-s-portfolio-olive.vercel.app/resume.pdf)  
**Rules:** [`ETERNITY.md`](./ETERNITY.md) · **Profile:** [`PROFILE.md`](./PROFILE.md)

---

## Open — Apply now ({n_open})
"""

FOOTER = """
---

## How updates work

1. **09:00 / 21:00 ET** — crawl company career sites (Amazon, Google, pharma, banks, …)
2. **12:00 ET** — LinkedIn Jobs search (PROFILE seeds)
3. Only verified Summer 2027 · US · BS roles are listed — no watchlist, no seed-list re-posting
4. Ricky clicks Apply — never auto-submit

Details: [`ETERNITY.md`](./ETERNITY.md) · raw data: [`data/openings.json`](./data/openings.json)
"""

CATEGORY_ORDER = ["AI/ML", "Bio-AI", "Finance", "SWE", "PM", "Other"]


def esc(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def clean_title(title: str, season: str) -> str:
    t = title or ""
    t = re.sub(r"[\U0001F1E6-\U0001F1FF]{2}", "", t)
    t = t.replace("🇺🇸", "").strip()
    t = re.sub(r"\s*\(\s*Summer\s*2027\s*\)\s*", " ", t, flags=re.I)
    t = re.sub(r"\(\s*Summer\s*2027\s*,\s*", "(", t, flags=re.I)
    t = re.sub(r"\s*[—–-]\s*Summer\s*2027\b", "", t, flags=re.I)
    t = re.sub(r"^Summer\s*2027\s*[—–-]?\s*", "", t, flags=re.I)
    t = re.sub(r",\s*Summer\s*2027\b", "", t, flags=re.I)
    t = re.sub(r"^Summer\s+Intern\s+2027\s*[—–-]?\s*", "", t, flags=re.I)
    t = re.sub(r"\s{2,}", " ", t).strip(" —–,")
    return esc(t)


def category_of(row: dict) -> str:
    c = (row.get("category") or "Other").strip()
    if c in CATEGORY_ORDER:
        return c
    return "Other"


def table_for(rows: list[dict]) -> str:
    lines = [
        "| Company | Role | Category | Apply |",
        "|---|---|---|---|",
    ]
    for i in sorted(rows, key=lambda x: (x.get("tier", 9), x["company"].lower(), x["role_title"].lower())):
        url = i.get("application_url") or i.get("posting_url")
        lines.append(
            f"| {esc(i['company'])} | {clean_title(i['role_title'], i.get('season', ''))} | {category_of(i)} | [Apply]({url}) |"
        )
    return "\n".join(lines)


def main() -> None:
    meta = json.loads((DATA / "meta.json").read_text())
    opens = json.loads((DATA / "openings.json").read_text())
    verified = meta.get("last_full_verify", "unknown")

    by_cat: dict[str, list] = {c: [] for c in CATEGORY_ORDER}
    for o in opens:
        by_cat.setdefault(category_of(o), []).append(o)

    parts = [HEADER.format(verified=verified, n_open=len(opens)).rstrip()]

    for cat in CATEGORY_ORDER:
        rows = by_cat.get(cat) or []
        if not rows:
            continue
        parts.append(f"\n### {cat} ({len(rows)})\n")
        parts.append(table_for(rows))

    parts.append(FOOTER.strip())

    text = "\n".join(parts).rstrip() + "\n"
    text = re.sub(r"(\|---\|.*\|)\n\n+(\|)", r"\1\n\2", text)
    OUT.write_text(text)
    print(f"Wrote {OUT} ({len(opens)} open)")


if __name__ == "__main__":
    main()
