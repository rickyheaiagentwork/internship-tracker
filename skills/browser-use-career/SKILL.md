---
name: "browser-use-career"
description: "Career browsing skill for ETERNITY: browse careers pages, collect listings, navigate applications — no form submission"
---

# Browser Use Career Skill (for ETERNITY)

## When to use
Eternity needs real browser interaction — not just reading URLs. Examples:
- Browsing a company's careers page with pagination/navigation
- Logging into a job portal to view saved/searched listings
- Interacting with dynamic JS-rendered content that `web_fetch` can't handle
- Collecting and organizing job data for the internship tracker

## How to activate
1. Confirm task requires browser automation (not just fetching).
2. Use: `npx -y browser-use-cli@latest skill install`
3. Tell Eternity what to do in the browser.

## Procedure for Eternity

### Scenario 1: Browse a careers page and collect job listings
```
Use Browser Use CLI or Python library:
- Connect browser to target career site
- Navigate, click "Next", scroll as needed
- Extract job titles, URLs, requirements from each listing
- Return structured data (JSON) back to Eternity
```

### Scenario 2: Search and filter on job portals
```
- Connect browser to job portal (LinkedIn, Indeed, Glassdoor, etc.)
- Use site search/filter inputs to narrow results
- Scroll through paginated results
- Extract listings with metadata (title, company, location, salary if visible)
- Return structured data back to Eternity
```

### Scenario 3: Navigate multi-step processes
```
- Open target page
- Follow navigation clicks ("Apply", "Next", etc.)
- Wait for dynamic content to load
- Extract final data or complete action
```

## Key notes
- Browser Use works with any LLM provider — Eternity can use its own context.
- For stealth/proxy needs at scale, pair with Browser Use Cloud.
- **DO NOT submit applications on Ricky's behalf.** Only collect and present data. Final submission is always manual by Ricky.

## Integration example (Python)
```python
from browser_use import Agent, ChatBrowserUse

agent = Agent(
    task="Go to company.com/careers, find intern engineering roles, extract titles and apply links",
    llm=ChatBrowserUse(model='anthropic/claude-sonnet-4-6')
)
result = await agent.run()
# result contains conversation history + extracted data
```

## Do NOT use for
- Simple page scraping → use `web_fetch` instead
- Search queries → use `web_search` instead
- Submitting applications or forms → always manual by Ricky
- Any task that doesn't require clicking/typing/navigating in a browser
