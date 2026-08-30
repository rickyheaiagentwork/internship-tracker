#!/usr/bin/env python3
"""Playwright career-site search for one company config."""
from __future__ import annotations

import asyncio
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_filters import looks_candidate  # noqa: E402


def _matches_filter(title: str, filters: list[str]) -> bool:
    if not title:
        return False
    low = title.lower()
    return any(f in low for f in filters)


async def crawl_company(company: dict, *, max_jobs: int = 30) -> list[dict]:
    jobs: list[dict] = []
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
        api_texts: list[str] = []

        async def on_response(response) -> None:
            try:
                rurl = response.url
                if any(kw in rurl.lower() for kw in ["jobs", "search", "listings", "results", "careers"]):
                    body = await response.text()
                    if len(body) > 80:
                        api_texts.append(body)
            except Exception:
                pass

        page.on("response", on_response)
        try:
            await page.goto(company["search_url"], wait_until="domcontentloaded", timeout=45000)
            await asyncio.sleep(4)
            for _ in range(3):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(0.8)

            seen: set[str] = set()
            links = await page.query_selector_all("a[href]")
            for link in links:
                if len(jobs) >= max_jobs:
                    break
                href = await link.get_attribute("href")
                if not href:
                    continue
                if href.startswith("/") and company.get("base_url"):
                    href = company["base_url"].rstrip("/") + href
                if not href.startswith("http"):
                    continue
                if not any(re.search(pat, href) for pat in company["job_url_patterns"]):
                    continue
                key = href.rstrip("/")
                if key in seen:
                    continue
                try:
                    text = (await link.inner_text() or "").strip()
                except Exception:
                    text = ""
                if not _matches_filter(text, company["filters"]) and not looks_candidate(
                    company["name"], text, "United States"
                ):
                    continue
                seen.add(key)
                jobs.append(
                    {
                        "company": company["name"],
                        "title": text or f"{company['name']} Intern",
                        "location": "United States",
                        "url": href,
                        "source": f"careers:{company['name']}",
                    }
                )

            # API JSON fallback for SPAs
            for body in api_texts:
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    continue
                items = []
                if isinstance(data, dict):
                    for key in ("jobs", "results", "items", "data", "entries", "searchResult"):
                        if isinstance(data.get(key), list):
                            items = data[key]
                            break
                for item in items:
                    if not isinstance(item, dict) or len(jobs) >= max_jobs:
                        break
                    title = (
                        item.get("title")
                        or item.get("jobTitle")
                        or item.get("name")
                        or item.get("role")
                        or ""
                    )
                    job_url = item.get("url") or item.get("applyLink") or item.get("jobUrl") or ""
                    if not title or not job_url:
                        continue
                    if not _matches_filter(str(title), company["filters"]):
                        continue
                    key = str(job_url).rstrip("/")
                    if key in seen:
                        continue
                    seen.add(key)
                    jobs.append(
                        {
                            "company": company["name"],
                            "title": str(title).strip(),
                            "location": str(item.get("location") or "United States"),
                            "url": str(job_url),
                            "source": f"careers:{company['name']}",
                        }
                    )
        except Exception as exc:
            print(f"# careers error {company['name']}: {exc}", file=sys.stderr)
        finally:
            await browser.close()
    return jobs


async def crawl_batch(companies: list[dict]) -> list[dict]:
    all_jobs: list[dict] = []
    for company in companies:
        print(f"# crawling {company['name']}...")
        found = await crawl_company(company)
        print(f"#   {len(found)} raw hits")
        all_jobs.extend(found)
    # dedupe by URL
    seen: set[str] = set()
    unique: list[dict] = []
    for j in all_jobs:
        key = j["url"].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        unique.append(j)
    return unique


def main() -> int:
    import argparse

    from search_targets import batch_companies

    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()
    targets = batch_companies(args.index, args.batch_size)
    hits = asyncio.run(crawl_batch(targets))
    print(json.dumps(hits, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
