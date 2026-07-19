---
name: "crawl4ai-bulk-collector"
description: "Bulk web crawler for LIVING TRIBUNAL research and ETERNITY career data: deep-crawl sites, extract structured data at scale"
---

# Crawl4AI Bulk Collector Skill (for LIVING TRIBUNAL & ETERNITY)

## When to use
- Need to extract data from **many pages** on a site (not just one)
- Deep crawling a career site to populate internship tracker with hundreds of entries
- Research requiring bulk extraction of structured content across multiple URLs
- Any task where `web_fetch` is too slow for single-page fetches

## How to activate
```bash
pip install crawl4ai
crawl4ai-setup  # post-install setup (downloads browser)
```
Then use the Python API or CLI (`crwl`).

## Procedure for LIVING TRIBUNAL (Research)

### Scenario: Research a topic across multiple sources
```python
from crawl4ai import *
import asyncio

async def deep_crawl():
    async with AsyncWebCrawler() as crawler:
        # Crawl an entire docs site or blog for research
        result = await crawler.arun(
            url="https://example.com/docs",
            warmup=False,  # run without LLM overhead if you want raw markdown
        )
        print(result.markdown)

asyncio.run(deep_crawl())
```

### Scenario: Extract structured data with LLM filtering
```python
result = await crawler.arun(
    url="https://example.com/page",
    hint="Extract all paper titles, authors, and abstracts",
)
# LLM filters the page to only relevant structured content
```

## Procedure for ETERNITY (Career / Internship Tracker)

### Scenario: Crawl a company's careers page for all open positions
```python
from crawl4ai import *
import asyncio

async def crawl_careers():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://company.com/careers",
            deep_crawl=True,  # follow links within the careers subdomain
        )
        # Parse markdown for job titles, locations, apply URLs
        return parse_job_listings(result.markdown)

asyncio.run(crawl_careers())
```

### Scenario: Crawl multiple company career pages for internship tracker
```python
# For each company in your list:
for company in companies:
    result = await crawler.arun(
        url=f"https://{company}.com/careers",
        deep_crawl=True,
        word_count_threshold=100,  # skip empty pages
    )
    jobs.append(parse_job_listings(result.markdown))
```

## CLI shortcut (quick single-page extract)
```bash
# Basic markdown extraction
crwl https://example.com/careers -o markdown

# Deep crawl with BFS, max 50 pages
crwl https://example.com/careers --deep-crawl bfs --max-pages 50

# LLM question-based extraction
crwl https://example.com/jobs -q "List all software engineering internships"
```

## Key notes
- Self-hosted: no API keys, no rate limits, runs locally
- Supports proxy rotation for anti-bot sites
- CSS/XPath selectors for targeted extraction (faster than LLM)
- For dynamic/JS-heavy pages with pagination that need clicking → use **browser-use-career** instead

## Do NOT use for
- Tasks requiring clicking buttons or filling forms → use browser-use-career
- Single-page fetches where `web_fetch` suffices
- Real-time interactive sessions (it's batch-oriented)
