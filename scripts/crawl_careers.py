#!/usr/bin/env python3
"""
Career page crawler — Playwright-based scraping of company career sites.

Usage:
    python3 crawl_careers.py [--company AMAZON] [--all] [--output openings.json]
"""

import argparse
import asyncio
import json
import re
import sys
from datetime import datetime, timezone

from playwright.async_api import async_playwright, Page, Browser

# ---------------------------------------------------------------------------
# Company configurations
# ---------------------------------------------------------------------------

COMPANIES = [
    {
        "name": "Amazon",
        "base_url": "https://amazon.jobs",
        "search_url": "https://amazon.jobs/en/search?category%5B%5D=software-development&category_type=studentprograms&distanceType=Mi&radius=24km&latitude=&longitude=&loc_group_id=&loc_query=&base_query=&city=&country=&region=&county=&query_options=",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/en/jobs/\d+/[a-z0-9-]+"],
    },
    {
        "name": "Google",
        "base_url": "https://careers.google.com",
        "search_url": "https://www.google.com/about/careers/applications/jobs/results/?search=software%20engineering%20intern%202027&location=United%20States",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"/jobs/\d+/[a-z0-9-]+"],
    },
    {
        "name": "Apple",
        "base_url": "https://jobs.apple.com",
        "search_url": "https://jobs.apple.com/en-us/search?search=software%20engineer%20intern&team=apls-engineering",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/en-us/job/\d+"],
    },
    {
        "name": "Nvidia",
        "base_url": "https://nvidia.careers",
        "search_url": "https://nvidia.careers/search?keyword=software%20engineering%20intern&department=Software%20Engineering&department=Hardware%20Engineering&location=United%20States&category=Internship",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/jobs/\d+/[a-z0-9-]+"],
    },
    {
        "name": "Meta",
        "base_url": "https://www.metacareers.com",
        "search_url": "https://www.metacareers.com/jobs?query=software%20engineering%20intern&category[]=Internship&location[]=United%20States",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/jobs/\d+"],
    },
    {
        "name": "Johnson & Johnson",
        "base_url": "https://jobs.jnj.com",
        "search_url": "https://jobs.jnj.com/search-jobs?search=intern",
        "filters": ["intern", "internship", "summer", "2027", "student", "software", "data", "engineering", "science"],
        "job_url_patterns": [r"/job/\d+"],
    },
    {
        "name": "Eli Lilly",
        "base_url": "https://careers.lilly.com",
        "search_url": "https://careers.lilly.com/us/en?search=intern&location=United%20States",
        "filters": ["intern", "internship", "summer", "2027", "student", "software", "data", "engineering", "science", "technology"],
        "job_url_patterns": [r"/us/en/job/\d+"],
    },
    {
        "name": "Pfizer",
        "base_url": "https://www.pfizer.com",
        "search_url": "https://www.pfizer.com/en/about/careers/jobs-search?search=intern",
        "filters": ["intern", "internship", "summer", "2027", "student", "software", "data", "engineering", "science", "technology", "digital"],
        "job_url_patterns": [r"/en/about/careers/jobs/\d+"],
    },
]

# Priority regexes for scoring
PRIORITY_RE = re.compile(
    r'\b(software\s*engineer|swe|machine\s*learning|ml\s*engineer|'
    r'ml\s*intern|software\s*intern|full\s*stack|'
    r'data\s*scient|data\s*engineer|'
    r'tensorflow|pytorch|deep\s*learning|'
    r'computer\s*vision|nlp|llm|generative\s*ai|'
    r'ai\s*intern|ai\s*engineer)\b',
    re.I,
)

BIO_COMPANIES_RE = re.compile(
    r'\b(johnson\s*\&\s*jones|j\&j|jnj|glaxosmithkline|gsk|'
    r'pfizer|merck|moderna|bio|biotech|'
    r'boston\s*scientific|abbott|novartis|'
    r'astrazeneca|lilly|eli\s*lilly|'
    r'janssen|amgen|gilead|'
    r'genentech|regeneron|'
    r'celgene|vertex|bio-techne|thermofisher)\b',
    re.I,
)


def priority_score(title, company_name):
    """Score a job listing for priority matching."""
    score = 0
    if title and PRIORITY_RE.search(title):
        score += 3
    if company_name and BIO_COMPANIES_RE.search(company_name):
        score += 2
    return score


def matches_filter(title, filters):
    """Check if a job title matches any of the filters."""
    if not title:
        return False
    text_lower = title.lower()
    return any(f in text_lower for f in filters)


async def crawl_company(company):
    """Crawl a single company's career site. Returns list of job dicts."""
    jobs = []

    browser = None
    context = None
    page = None

    try:
        print(f"  Crawling {company['name']}...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
            )
            page = await context.new_page()

            await page.goto(company['search_url'], wait_until='networkidle', timeout=20000)
            await asyncio.sleep(3)

            # Collect all job URLs from page
            link_hrefs = set()
            links = await page.query_selector_all('a')
            for link in links:
                href = await link.get_attribute('href')
                if not href:
                    continue
                if href.startswith('/') and company['base_url']:
                    full_url = company['base_url'] + href
                    link_hrefs.add(full_url)
                elif href.startswith('http'):
                    link_hrefs.add(href)

            # Filter to known job URL patterns
            for href in link_hrefs:
                is_job = False
                for pattern in company['job_url_patterns']:
                    if re.search(pattern, href):
                        is_job = True
                        break

                if not is_job:
                    continue

                # Get the visible text of the link
                try:
                    text = (await link.text_content() or '').strip()
                except:
                    text = ''

                if not matches_filter(text, company['filters']):
                    continue

                score = priority_score(text, company['name'])

                jobs.append({
                    "title": text,
                    "company": company['name'],
                    "location": "Remote" if "remote" in text.lower() else "US",
                    "url": href,
                    "source": f"{company['name']}_crawl",
                    "confidence": 0.7 + (score * 0.1),
                    "date_found": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "priority": score,
                })

    except Exception as e:
        print(f"  Error crawling {company['name']}: {e}", file=sys.stderr)
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass

    return jobs


async def crawl_api_responses(company):
    """
    For SPAs that load jobs via API calls, intercept XHR responses.
    This is a fallback for when DOM scraping doesn't find job cards.
    """
    jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
        )
        page = await context.new_page()

        api_texts = []

        async def on_response(response):
            try:
                url = response.url if not callable(response.url) else response.url()
            except:
                url = str(response)

            if any(kw in url.lower() for kw in ['jobs', 'search', 'listings', 'results']):
                try:
                    body = await response.text()
                    if len(body) > 50:
                        api_texts.append({'url': url, 'text': body})
                except:
                    pass

        try:
            page.on('response', on_response)

            await page.goto(company['search_url'], wait_until='networkidle', timeout=20000)
            await asyncio.sleep(5)

            for resp in api_texts:
                text = resp['text']
                try:
                    data = json.loads(text)
                    if isinstance(data, dict):
                        for key in ['jobs', 'results', 'items', 'data', 'entries', 'searchResult']:
                            if key in data and isinstance(data[key], list):
                                for item in data[key]:
                                    if isinstance(item, dict):
                                        job_title = (
                                            item.get('title') or
                                            item.get('jobTitle') or
                                            item.get('name') or
                                            item.get('role') or
                                            ''
                                        )
                                        job_url = (
                                            item.get('url') or
                                            item.get('applyLink') or
                                            item.get('jobUrl') or
                                            ''
                                        )
                                        if job_title and matches_filter(job_title, company['filters']):
                                            score = priority_score(job_title, company['name'])
                                            if isinstance(job_url, str) and job_url not in ['', 'null', 'undefined']:
                                                jobs.append({
                                                    "title": job_title.strip(),
                                                    "company": company['name'],
                                                    "location": item.get('location') or item.get('city') or "US",
                                                    "url": job_url,
                                                    "source": f"{company['name']}_crawl",
                                                    "confidence": 0.75 + (score * 0.1),
                                                    "date_found": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                                                    "priority": score,
                                                })
                except json.JSONDecodeError:
                    pass

            await browser.close()

        except Exception as e:
            print(f"  API response error for {company['name']}: {e}", file=sys.stderr)
            try:
                await browser.close()
            except:
                pass

    return jobs


async def main():
    parser = argparse.ArgumentParser(description='Crawl company career sites for internships')
    parser.add_argument('--company', nargs='+', help='Specific companies to crawl')
    parser.add_argument('--all', action='store_true', help='Crawl all configured companies')
    parser.add_argument('--output', '-o', default='crawl_results.json', help='Output JSON file path')
    args = parser.parse_args()

    if args.company:
        names_lower = [c.lower() for c in args.company]
        targets = [c for c in COMPANIES if c['name'].lower() in names_lower or any(n in c['name'].lower() for n in names_lower)]
    elif args.all or not args.company:
        targets = COMPANIES
    else:
        targets = COMPANIES

    if not targets:
        print("No companies matched. Available:", [c['name'] for c in COMPANIES])
        sys.exit(1)

    print(f"Crawling {len(targets)} company career sites...")

    all_jobs = []
    for company in targets:
        jobs = await crawl_company(company)

        # If DOM scraping found nothing, try API response interception
        if not jobs:
            print(f"  DOM scrape found nothing for {company['name']}, trying API interception...")
            api_jobs = await crawl_api_responses(company)
            jobs.extend(api_jobs)

        all_jobs.extend(jobs)
        print(f"  Found {len(jobs)} job(s) at {company['name']}")
        for j in jobs[:3]:
            print(f"    - {j['title'][:60]} ({j['url'][:80]})")

    # Remove duplicates by URL
    seen = set()
    unique_jobs = []
    for j in all_jobs:
        url_key = j['url'].rstrip('/') if j['url'] else ''
        if url_key and url_key not in seen:
            seen.add(url_key)
            unique_jobs.append(j)

    print(f"\nTotal unique jobs found: {len(unique_jobs)}")
    for j in unique_jobs:
        print(f"  [{j['company']}] {j['title'][:60]} → {j['url'][:80]}")

    # Output
    with open(args.output, 'w') as f:
        json.dump(unique_jobs, f, indent=2)
    print(f"\nSaved to {args.output}")

    return unique_jobs


if __name__ == '__main__':
    asyncio.run(main())
