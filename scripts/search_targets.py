"""Company career sites to actively crawl (search targets, not a watchlist)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Core configs with tuned search URLs
COMPANIES: list[dict] = [
    {
        "name": "Amazon",
        "base_url": "https://amazon.jobs",
        "search_url": "https://amazon.jobs/en/search?base_query=software%20development%20engineer%20intern%202027&country%5B%5D=USA",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/en/jobs/\d+"],
    },
    {
        "name": "Google",
        "base_url": "https://careers.google.com",
        "search_url": "https://www.google.com/about/careers/applications/jobs/results/?q=software%20engineering%20intern%202027&location=United%20States",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"/jobs/\d+"],
    },
    {
        "name": "Apple",
        "base_url": "https://jobs.apple.com",
        "search_url": "https://jobs.apple.com/en-us/search?search=intern%202027&sort=relevance",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/en-us/details/\d+", r"/en-us/job/\d+"],
    },
    {
        "name": "NVIDIA",
        "base_url": "https://nvidia.wd5.myworkdayjobs.com",
        "search_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"myworkdayjobs\.com/.*/job/"],
    },
    {
        "name": "Meta",
        "base_url": "https://www.metacareers.com",
        "search_url": "https://www.metacareers.com/jobs?query=software%20engineering%20intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/jobs/\d+"],
    },
    {
        "name": "Microsoft",
        "base_url": "https://careers.microsoft.com",
        "search_url": "https://careers.microsoft.com/us/en/search-results?keywords=software%20engineering%20intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"/us/en/job/\d+"],
    },
    {
        "name": "OpenAI",
        "base_url": "https://openai.com",
        "search_url": "https://openai.com/careers/search/?q=intern",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"/careers/"],
    },
    {
        "name": "Anthropic",
        "base_url": "https://www.anthropic.com",
        "search_url": "https://www.anthropic.com/careers",
        "filters": ["intern", "internship", "summer", "2027", "student"],
        "job_url_patterns": [r"/careers/"],
    },
    {
        "name": "Johnson & Johnson",
        "base_url": "https://jobs.jnj.com",
        "search_url": "https://jobs.jnj.com/en/jobs/?search=intern%202027&country=United+States",
        "filters": ["intern", "internship", "summer", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"/job/\d+", r"/en/jobs/"],
    },
    {
        "name": "Eli Lilly",
        "base_url": "https://careers.lilly.com",
        "search_url": "https://careers.lilly.com/us/en/search-results?keywords=intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"/us/en/job/\d+"],
    },
    {
        "name": "Pfizer",
        "base_url": "https://pfizer.wd1.myworkdayjobs.com",
        "search_url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers?q=intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"myworkdayjobs\.com/.*/job/"],
    },
    {
        "name": "JPMorgan Chase",
        "base_url": "https://careers.jpmorgan.com",
        "search_url": "https://careers.jpmorgan.com/us/en/students/programs/software-engineer-fulltime-2025",
        "filters": ["intern", "internship", "summer", "2027", "analytics", "data", "software", "engineering"],
        "job_url_patterns": [r"/job/", r"/jobs/"],
    },
    {
        "name": "Goldman Sachs",
        "base_url": "https://www.goldmansachs.com",
        "search_url": "https://www.goldmansachs.com/careers/students/programs/americas/summer-analyst-program.html",
        "filters": ["intern", "internship", "summer", "2027", "analyst", "engineering", "data"],
        "job_url_patterns": [r"/careers/", r"gh_jid=", r"myworkdayjobs"],
    },
    {
        "name": "BlackRock",
        "base_url": "https://careers.blackrock.com",
        "search_url": "https://careers.blackrock.com/search-jobs/intern%202027",
        "filters": ["intern", "internship", "summer", "2027", "analytics", "data", "software"],
        "job_url_patterns": [r"/job/", r"blackrock\.com/job/"],
    },
    {
        "name": "Recursion",
        "base_url": "https://www.recursion.com",
        "search_url": "https://www.recursion.com/careers",
        "filters": ["intern", "internship", "summer", "2027", "machine", "learning", "data"],
        "job_url_patterns": [r"/careers/", r"greenhouse\.io"],
    },
    {
        "name": "Tempus",
        "base_url": "https://www.tempus.com",
        "search_url": "https://www.tempus.com/careers/",
        "filters": ["intern", "internship", "summer", "2027", "data", "machine", "learning"],
        "job_url_patterns": [r"/careers/", r"greenhouse\.io", r"lever\.co"],
    },
]

LINKEDIN_SEEDS: list[str] = [
    'internship "Summer 2027" ("machine learning" OR "artificial intelligence" OR "data science") "United States"',
    'internship "Summer 2027" ("data analytics" OR "financial analytics" OR "investment analytics") (JPMorgan OR "Goldman Sachs" OR "Morgan Stanley" OR BlackRock) "United States"',
    'internship "Summer 2027" ("data science" OR "machine learning" OR analytics) (Pfizer OR "Johnson & Johnson" OR "Eli Lilly" OR Merck OR Amgen) "United States"',
    'internship "Summer 2027" (biotech OR pharmaceutical OR "computational biology" OR bioinformatics OR genomics) "United States"',
    'internship "Summer 2027" ("machine learning" OR "data science" OR AI) (pharma OR medical OR clinical OR biomedical OR healthcare) "United States"',
    'intern "Summer 2027" (Amazon OR Apple OR Meta OR Google OR Microsoft OR NVIDIA) software engineering "United States"',
    'intern "Summer 2027" (Anthropic OR OpenAI OR NVIDIA OR DeepMind OR "Scale AI") "United States"',
    'intern "Summer 2027" (Recursion OR Insitro OR Tempus OR Illumina OR PathAI) "United States"',
]


def _generic_from_watchlist() -> list[dict]:
    """Build generic crawl targets from legacy watchlist careers URLs."""
    path = ROOT / "data" / "watchlist.json"
    if not path.exists():
        return []
    try:
        rows = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    existing = {c["name"].lower() for c in COMPANIES}
    out: list[dict] = []
    for row in rows:
        name = (row.get("company") or "").strip()
        url = (row.get("careers_url") or "").strip()
        if not name or not url or name.lower() in existing:
            continue
        out.append(
            {
                "name": name,
                "base_url": re.sub(r"/[^/]*$", "", url) or url,
                "search_url": url,
                "filters": ["intern", "internship", "summer", "2027", "student", "software", "data", "science", "analytics", "machine", "learning"],
                "job_url_patterns": [
                    r"/job/",
                    r"/jobs/",
                    r"myworkdayjobs",
                    r"greenhouse\.io",
                    r"lever\.co",
                    r"smartrecruiters",
                    r"ashbyhq",
                ],
            }
        )
        existing.add(name.lower())
    return out


def all_companies() -> list[dict]:
    return COMPANIES + _generic_from_watchlist()


def batch_companies(index: int, batch_size: int = 4) -> list[dict]:
    companies = all_companies()
    if not companies:
        return []
    start = (index * batch_size) % len(companies)
    batch: list[dict] = []
    for i in range(batch_size):
        batch.append(companies[(start + i) % len(companies)])
    return batch


def linkedin_seed(index: int) -> str:
    return LINKEDIN_SEEDS[index % len(LINKEDIN_SEEDS)]
