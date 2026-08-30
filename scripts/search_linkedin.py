#!/usr/bin/env python3
"""LinkedIn Jobs search via Playwright (public search pages)."""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_filters import looks_candidate  # noqa: E402


async def search_linkedin(query: str, *, max_results: int = 25) -> list[dict]:
    """Return raw hits: company, title, location, url."""
    url = (
        "https://www.linkedin.com/jobs/search/?"
        f"keywords={quote_plus(query)}"
        "&location=United%20States"
        "&f_E=1"  # internship
        "&f_TPR=r604800"  # past week
    )
    hits: list[dict] = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4)
            # Scroll to load more cards
            for _ in range(4):
                await page.mouse.wheel(0, 2000)
                await asyncio.sleep(1)

            cards = await page.query_selector_all(
                "div.base-card, li.jobs-search-results__list-item, div.job-search-card"
            )
            seen: set[str] = set()
            for card in cards:
                if len(hits) >= max_results:
                    break
                try:
                    link_el = await card.query_selector("a[href*='/jobs/view/']")
                    if not link_el:
                        continue
                    href = await link_el.get_attribute("href")
                    if not href or href in seen:
                        continue
                    title_el = await card.query_selector(
                        "h3, .base-search-card__title, .job-search-card__title"
                    )
                    company_el = await card.query_selector(
                        "h4, .base-search-card__subtitle, .job-search-card__subtitle"
                    )
                    loc_el = await card.query_selector(
                        ".job-search-card__location, .base-search-card__metadata"
                    )
                    title = ((await title_el.inner_text()) if title_el else "").strip()
                    company = ((await company_el.inner_text()) if company_el else "").strip()
                    location = ((await loc_el.inner_text()) if loc_el else "United States").strip()
                    if not title or not company:
                        continue
                    if not looks_candidate(company, title, location, query):
                        continue
                    seen.add(href)
                    clean = re.sub(r"\?.*$", "", href)
                    hits.append(
                        {
                            "company": company,
                            "title": title,
                            "location": location,
                            "url": clean,
                            "source": "linkedin",
                        }
                    )
                except Exception:
                    continue
        finally:
            await browser.close()
    return hits


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="?", help="LinkedIn search query")
    parser.add_argument("--max", type=int, default=25)
    args = parser.parse_args()
    if not args.query:
        print("usage: search_linkedin.py <query>", file=sys.stderr)
        return 2
    hits = asyncio.run(search_linkedin(args.query, max_results=args.max))
    for h in hits:
        print(f"{h['company']} | {h['title']} | {h['url']}")
    print(f"# {len(hits)} hits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
