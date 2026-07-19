# Example: Browse company careers page and collect listings
from browser_use import Agent, ChatBrowserUse
import asyncio

async def main():
    agent = Agent(
        task="""
        Navigate to https://company.com/careers
        - Scroll through all available pages
        - For each job listing, extract:
          1. Job title
          2. Location (remote/hybrid/on-site)
          3. Application URL
          4. Department/team
          5. Required skills/qualifications
        Return as structured JSON array.
        """,
        llm=ChatBrowserUse(model='anthropic/claude-sonnet-4-6')
    )
    result = await agent.run()
    return result

if __name__ == "__main__":
    asyncio.run(main())
