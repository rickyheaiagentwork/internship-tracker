#!/usr/bin/env python3
"""Playwright career-site search for one company config."""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_filters import looks_candidate  # noqa: E402

# Cron runs without a login shell; point Playwright at the system browser cache.
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/home/jarvis/.cache/ms-playwright")


def _matches_filter(title: str, filters: list[str]) -> bool:
    if not title:
        return False
    low = title.lower()
    return any(f in low for f in filters)


_NON_US_TITLE = re.compile(
    r"\b("
    r"china|shanghai|beijing|taiwan|taipei|hsinchu|india|bengaluru|hyderabad|"
    r"ireland|dublin|uk|united kingdom|london|england|scotland|edinburgh|"
    r"toronto|ontario|canada|mexico|mexico city|ankara|turkey|"
    r"hong kong|singapore|tokyo|japan|australia|sydney|"
    r"emea|apac|off-cycle|grange castle|dublin"
    r")\b",
    re.I,
)

_US_TITLE = re.compile(
    r"\b("
    r"united states|u\.s\.|usa|new york|san francisco|seattle|austin|boston|"
    r"california|washington|texas|massachusetts|chicago|redmond|mountain view|"
    r"menlo park|sunnyvale|santa clara|amers|americas"
    r")\b",
    re.I,
)


def _is_non_us_title(title: str) -> bool:
    if not title:
        return False
    if _US_TITLE.search(title):
        return False
    return bool(_NON_US_TITLE.search(title))


def _passes_company_rules(company: dict, title: str) -> bool:
    low = title.lower()
    if company.get("require_intern_title") and "intern" not in low and "fellow" not in low:
        return False
    if company.get("require_us_title") and _is_non_us_title(title):
        return False
    return True


def _title_from_href(href: str) -> str:
    m = re.search(r"jobs/results/\d+-([^?]+)", href)
    if not m:
        return ""
    words = m.group(1).split("-")
    out: list[str] = []
    for w in words:
        wl = w.lower()
        if wl in {"bs", "ms", "phd", "ai", "ml", "llm", "nlp"}:
            out.append(w.upper())
        elif wl == "summer":
            out.append("Summer")
        else:
            out.append(w.capitalize())
    title = " ".join(out)
    title = re.sub(r"\bIntern\b", "Intern,", title, count=1)
    title = re.sub(r",\s*(BS|MS|PhD)\b", r", \1", title)
    return title


def _resolve_href(href: str, company: dict) -> str:
    if href.startswith("http"):
        return href
    base = company.get("base_url") or company.get("search_url", "")
    if not base:
        return href
    if href.startswith("./"):
        href = href[2:]
    if href.startswith("/"):
        origin = re.match(r"^(https?://[^/]+)", base)
        return (origin.group(1) if origin else base.rstrip("/")) + href
    return base.rstrip("/") + "/" + href.lstrip("/")


def _clean_title(text: str) -> str:
    text = re.sub(r"\s+", " ", text.replace("\n", " ")).strip()
    text = re.sub(r"\s+United States.*$", "", text, flags=re.I)
    text = re.sub(r"\s+Posted .*$", "", text, flags=re.I)
    return text.strip()


async def _enrich_job(page, job: dict) -> None:
    try:
        await page.goto(job["url"], wait_until="domcontentloaded", timeout=35000)
        await asyncio.sleep(2)
        body = await page.inner_text("body")
        job["page_text"] = body
        if not job.get("title") or job["title"].endswith("Intern"):
            for line in body.split("\n"):
                line = line.strip()
                if "intern" in line.lower() and len(line) < 140:
                    job["title"] = _clean_title(line)
                    break
    except Exception as exc:
        print(f"# enrich error {job.get('url', '')}: {exc}", file=sys.stderr)


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
                href = _resolve_href(href, company)
                if not href.startswith("http"):
                    continue
                if not any(re.search(pat, href) for pat in company["job_url_patterns"]):
                    continue
                key = href.split("?")[0].rstrip("/")
                if key in seen:
                    continue
                try:
                    text = _clean_title((await link.inner_text() or "").strip())
                except Exception:
                    text = ""
                if not text:
                    text = _title_from_href(href)
                if not _passes_company_rules(company, text):
                    continue
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
                        "url": href.split("?")[0],
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
                    if not _passes_company_rules(company, str(title)):
                        continue
                    if not _matches_filter(str(title), company["filters"]):
                        continue
                    key = str(job_url).split("?")[0].rstrip("/")
                    if key in seen:
                        continue
                    seen.add(key)
                    jobs.append(
                        {
                            "company": company["name"],
                            "title": str(title).strip(),
                            "location": str(item.get("location") or "United States"),
                            "url": str(job_url).split("?")[0],
                            "source": f"careers:{company['name']}",
                        }
                    )

            enrich = company.get("enrich_detail") or any(
                x in company.get("search_url", "").lower()
                for x in ("myworkdayjobs", "careers.lilly.com", "careers.jpmorgan.com", "oraclecloud.com")
            )
            if enrich:
                for job in jobs[:max_jobs]:
                    await _enrich_job(page, job)
                    if _is_non_us_title(job.get("title", "")):
                        job["_reject"] = True
            jobs = [j for j in jobs if not j.get("_reject")]
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
