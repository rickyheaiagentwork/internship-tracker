# Example: Deep crawl a company's careers page to extract all open positions
from crawl4ai import *
import asyncio

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://example.com/careers",
            deep_crawl=True,  # Crawl all links within the careers section
            word_count_threshold=100,  # Skip thin/empty pages
        )
        
        # Result.markdown contains the cleaned content of every page crawled
        # Parse for job listings:
        # - Job titles (look for heading patterns)
        # - Application URLs (links ending in "apply" or with job-specific paths)
        # - Locations, departments, requirements from surrounding text
        
        print(f"Crawled {len(result.links)} pages")
        print(result.markdown[:2000])  # Preview first 2k chars

asyncio.run(main())
