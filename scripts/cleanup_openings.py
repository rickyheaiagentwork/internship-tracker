#!/usr/bin/env python3
"""Dedupe openings by company+role and refresh categories from fit_filters."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fit_filters import category_for, dedupe_openings, fit_score  # noqa: E402

OPENINGS = ROOT / "data" / "openings.json"


def main() -> None:
    openings = json.loads(OPENINGS.read_text())
    before = len(openings)

    for o in openings:
        o["category"] = category_for(o["company"], o["role_title"])
        o["fit_score"] = fit_score(o["company"], o["role_title"], o.get("location", ""))
        o["tier"] = 1 if o["fit_score"] >= 100 else 2

    openings = dedupe_openings(openings)
    openings.sort(key=lambda x: (x.get("tier", 9), x["company"].lower(), x["role_title"].lower()))

    OPENINGS.write_text(json.dumps(openings, indent=2) + "\n")
    print(f"Cleaned openings: {before} -> {len(openings)} ({before - len(openings)} removed)")


if __name__ == "__main__":
    main()
