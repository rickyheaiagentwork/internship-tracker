"""Company career sites to actively crawl — search wide, list only verified fits."""
from __future__ import annotations

import re

DEFAULT_FILTERS = [
    "intern",
    "internship",
    "summer",
    "2027",
    "student",
    "undergraduate",
    "university",
    "software",
    "engineer",
    "data",
    "science",
    "analytics",
    "machine",
    "learning",
    "technology",
]

DEFAULT_PATTERNS = [
    r"/job/",
    r"/jobs/",
    r"myworkdayjobs",
    r"greenhouse\.io",
    r"lever\.co",
    r"smartrecruiters",
    r"ashbyhq",
    r"wd\d+\.myworkdayjobs",
    r"careers\.[^/]+/job",
]


def _t(
    name: str,
    search_url: str,
    base_url: str = "",
    *,
    filters: list[str] | None = None,
    job_url_patterns: list[str] | None = None,
    **flags: object,
) -> dict:
    base = base_url or re.sub(r"/[^/?#]*([?#].*)?$", "", search_url).rstrip("/")
    entry: dict = {
        "name": name,
        "base_url": base,
        "search_url": search_url,
        "filters": filters or DEFAULT_FILTERS,
        "job_url_patterns": job_url_patterns or DEFAULT_PATTERNS,
    }
    entry.update(flags)
    return entry


# Hand-tuned crawls (SPA / tricky sites)
TUNED: list[dict] = [
    {
        "name": "Amazon",
        "base_url": "https://amazon.jobs",
        "search_url": "https://amazon.jobs/en/search?base_query=software%20development%20engineer%20intern%202027&country%5B%5D=USA",
        "filters": ["intern", "internship", "summer", "2027", "student", "undergraduate"],
        "job_url_patterns": [r"/en/jobs/\d+"],
    },
    {
        "name": "Google",
        "base_url": "https://www.google.com/about/careers/applications/",
        "search_url": "https://www.google.com/about/careers/applications/jobs/results/?q=software%20engineering%20intern%202027&location=United%20States",
        "filters": ["intern", "internship", "summer", "2027", "student", "bs"],
        "job_url_patterns": [r"jobs/results/\d+-"],
        "enrich_detail": True,
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
        "search_url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite?q=software+engineering+intern+2027+united+states",
        "filters": ["intern", "internship", "2027", "student", "software"],
        "job_url_patterns": [r"/job/", r"myworkdayjobs\.com/.*/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "Meta",
        "base_url": "https://www.metacareers.com",
        "search_url": "https://www.metacareers.com/jobsearch/?teams[0]=University%20Grad%20-%20Engineering%2C%20Tech%20%26%20Design&query=2027%20intern",
        "filters": ["intern", "internship", "2027", "student", "undergraduate", "university"],
        "job_url_patterns": [r"job_details/\d+"],
        "enrich_detail": True,
        "require_intern_title": True,
    },
    {
        "name": "Microsoft",
        "base_url": "https://apply.careers.microsoft.com",
        "search_url": "https://apply.careers.microsoft.com/careers?query=intern%20university%202027",
        "filters": ["intern", "internship", "university", "student", "software"],
        "job_url_patterns": [r"/careers/job/\d+"],
        "enrich_detail": True,
    },
    {
        "name": "OpenAI",
        "base_url": "https://jobs.ashbyhq.com",
        "search_url": "https://jobs.ashbyhq.com/openai",
        "filters": ["intern", "internship"],
        "job_url_patterns": [r"ashbyhq.com/openai/[a-f0-9-]{36}"],
        "require_intern_title": True,
    },
    {
        "name": "Anthropic",
        "base_url": "https://job-boards.greenhouse.io",
        "search_url": "https://job-boards.greenhouse.io/anthropic",
        "filters": ["intern", "internship", "fellow"],
        "job_url_patterns": [r"greenhouse.io/anthropic/jobs/\d+"],
        "require_intern_title": True,
    },
    {
        "name": "Johnson & Johnson",
        "base_url": "https://jobs.jnj.com",
        "search_url": "https://jobs.jnj.com/en/jobs/?search=intern&country=United+States&sortBy=date",
        "filters": ["intern", "internship", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"jobs\.jnj\.com/.*/job/", r"/en/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "Eli Lilly",
        "base_url": "https://careers.lilly.com",
        "search_url": "https://careers.lilly.com/us/en/search-results?keywords=intern%202027",
        "filters": ["intern", "internship", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"/us/en/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "Pfizer",
        "base_url": "https://pfizer.wd1.myworkdayjobs.com",
        "search_url": "https://pfizer.wd1.myworkdayjobs.com/PfizerCareers?q=intern%202027&locationCountry=US",
        "filters": ["intern", "internship", "2027", "data", "software", "science", "analytics"],
        "job_url_patterns": [r"/job/", r"myworkdayjobs\.com/.*/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "JPMorgan Chase",
        "base_url": "https://careers.jpmorgan.com",
        "search_url": "https://careers.jpmorgan.com/us/en/search-results?keywords=2027%20software%20engineer%20intern",
        "filters": ["intern", "internship", "summer", "2027", "analytics", "data", "software", "engineering", "analyst"],
        "job_url_patterns": [r"/us/en/job/", r"/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "Goldman Sachs",
        "base_url": "https://hdpc.fa.us2.oraclecloud.com",
        "search_url": "https://hdpc.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/jobs?keyword=2027%20summer%20intern",
        "filters": ["intern", "internship", "summer", "2027", "analyst", "engineering", "data"],
        "job_url_patterns": [r"/jobs/preview/", r"/job/"],
        "enrich_detail": True,
        "require_us_title": True,
    },
    {
        "name": "BlackRock",
        "base_url": "https://careers.blackrock.com",
        "search_url": "https://careers.blackrock.com/search-jobs/intern%202027%20united%20states",
        "filters": ["intern", "internship", "summer", "2027", "analytics", "data", "software", "amers"],
        "job_url_patterns": [r"careers\.blackrock\.com/job/"],
        "require_us_title": True,
    },
    {
        "name": "Recursion",
        "base_url": "https://job-boards.greenhouse.io",
        "search_url": "https://job-boards.greenhouse.io/recursionpharmaceuticals",
        "filters": ["intern", "internship", "summer", "2027", "machine", "learning", "data"],
        "job_url_patterns": [r"greenhouse.io/recursionpharmaceuticals/jobs/\d+"],
        "require_intern_title": True,
        "require_us_title": True,
    },
    {
        "name": "Tempus",
        "base_url": "https://job-boards.greenhouse.io",
        "search_url": "https://job-boards.greenhouse.io/tempusai",
        "filters": ["intern", "internship", "summer", "2027", "data", "machine", "learning"],
        "job_url_patterns": [r"greenhouse.io/tempusai/jobs/\d+"],
        "require_intern_title": True,
        "require_us_title": True,
    },
]

# Extra big tech / infra (beyond FAANG)
BIG_TECH: list[dict] = [
    _t("Google DeepMind", "https://deepmind.google/careers/", require_intern_title=True),
    _t("Cohere", "https://cohere.com/careers", require_intern_title=True),
    _t("Hugging Face", "https://huggingface.co/jobs", require_intern_title=True),
    _t("Mistral AI", "https://mistral.ai/careers", require_intern_title=True, require_us_title=True),
    _t("Databricks", "https://www.databricks.com/company/careers/open-positions?keywords=intern"),
    _t("Snowflake", "https://careers.snowflake.com/us/en/search-results?keywords=intern"),
    _t("Palantir", "https://jobs.lever.co/palantir?commitment=Internship"),
    _t("IBM", "https://www.ibm.com/careers/search?field_keyword_08%5B0%5D=Intern&field_keyword_05%5B0%5D=United%20States"),
    _t("Oracle", "https://careers.oracle.com/en/sites/jobsearch/jobs?keyword=intern"),
    _t("Cisco", "https://jobs.cisco.com/jobs/SearchJobs/intern?listFilterMode=1"),
    _t("Intel", "https://jobs.intel.com/en/search-jobs/intern"),
    _t("AMD", "https://careers.amd.com/careers-home/jobs?keywords=intern%202027"),
    _t("Qualcomm", "https://careers.qualcomm.com/careers?query=intern"),
    _t("ServiceNow", "https://careers.servicenow.com/jobs?keywords=intern"),
    _t("Workday", "https://workday.wd5.myworkdayjobs.com/Workday?q=intern"),
    _t("Atlassian", "https://www.atlassian.com/company/careers/all-jobs?team=Interns"),
    _t("Autodesk", "https://autodesk.wd1.myworkdayjobs.com/Ext?q=intern"),
    _t("Dell", "https://jobs.dell.com/en/search-jobs/intern"),
    _t("SAP", "https://jobs.sap.com/search/?q=intern"),
]

# Consumer / media / marketplace / fintech apps
CONSUMER: list[dict] = [
    _t("Disney", "https://jobs.disneycareers.com/search-jobs?k=intern&l=United%20States"),
    _t("Netflix", "https://jobs.netflix.com/search?query=intern"),
    _t("Spotify", "https://lifeatspotify.com/jobs?l=united-states"),
    _t("Uber", "https://www.uber.com/us/en/careers/list/?query=intern"),
    _t("Lyft", "https://www.lyft.com/careers?search=intern"),
    _t("Airbnb", "https://careers.airbnb.com/positions/?search=intern"),
    _t("DoorDash", "https://careers.doordash.com/jobs?query=intern"),
    _t("Stripe", "https://stripe.com/jobs/search?query=intern"),
    _t("PayPal", "https://paypal.eightfold.ai/careers?query=intern"),
    _t("Block", "https://block.xyz/careers/jobs?query=intern"),
    _t("Salesforce", "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site?q=intern%202027"),
    _t("Adobe", "https://careers.adobe.com/us/en/search-results?keywords=intern"),
    _t("Intuit", "https://jobs.intuit.com/search-jobs/intern"),
    _t("Shopify", "https://www.shopify.com/careers/search?query=intern"),
    _t("Roblox", "https://careers.roblox.com/jobs?query=intern"),
    _t("Snap", "https://careers.snap.com/jobs?query=intern"),
    _t("Pinterest", "https://www.pinterestcareers.com/jobs/?search=intern"),
    _t("Reddit", "https://www.redditinc.com/careers?query=intern"),
    _t("TikTok", "https://careers.tiktok.com/search?keyword=intern"),
    _t("Electronic Arts", "https://ea.gr8people.com/jobs?keyword=intern"),
    _t("Coinbase", "https://www.coinbase.com/careers/positions?query=intern"),
    _t("Twilio", "https://www.twilio.com/en-us/company/jobs?search=intern"),
    _t("Zoom", "https://careers.zoom.us/us/en/search-results?keywords=intern"),
]

# Pharma, biotech, med-tech, bio-AI
BIO_PHARMA: list[dict] = [
    _t("Merck", "https://jobs.merck.com/us/en/search-results?keywords=intern"),
    _t("Amgen", "https://careers.amgen.com/en/search-jobs/intern"),
    _t("Gilead Sciences", "https://www.gilead.com/careers", require_us_title=True),
    _t("Moderna", "https://www.modernatx.com/careers"),
    _t("Genentech", "https://careers.gene.com/us/en/search-results?keywords=intern"),
    _t("Novartis", "https://www.novartis.com/careers/students"),
    _t("AbbVie", "https://careers.abbvie.com/students"),
    _t("Bristol Myers Squibb", "https://careers.bms.com/students"),
    _t("AstraZeneca", "https://careers.astrazeneca.com/students"),
    _t("IQVIA", "https://jobs.iqvia.com/en/search-jobs/intern"),
    _t("Natera", "https://www.natera.com/company/careers/"),
    _t("Guardant Health", "https://guardanthealth.com/careers/"),
    _t("Illumina", "https://www.illumina.com/company/careers.html"),
    _t("10x Genomics", "https://www.10xgenomics.com/careers"),
    _t("Verily", "https://verily.com/careers"),
    _t("Flatiron Health", "https://flatiron.com/careers"),
    _t("PathAI", "https://www.pathai.com/careers"),
    _t("Owkin", "https://www.owkin.com/careers"),
    _t("Insitro", "https://www.insitro.com/careers/"),
    _t("Schrödinger", "https://www.schrodinger.com/careers/"),
    _t("Generate Biomedicines", "https://generatebiomedicines.com/careers"),
    _t("Atomwise", "https://www.atomwise.com/careers/"),
    _t("Isomorphic Labs", "https://www.isomorphiclabs.com/careers"),
    _t("BenchSci", "https://www.benchsci.com/careers"),
]

# Banks / asset managers (analytics & tech tracks — not prop trading)
FINANCE: list[dict] = [
    _t("Morgan Stanley", "https://www.morganstanley.com/careers/career-opportunities-search?search=intern"),
    _t("Fidelity Investments", "https://jobs.fidelity.com/students-and-graduates/"),
    _t("Bank of America", "https://campus.bankofamerica.com/en-us/search-jobs?keywords=intern"),
    _t("Citi", "https://www.citigroup.com/global/careers/students-and-graduates"),
    _t("Capital One", "https://www.capitalonecareers.com/search-jobs/intern"),
    _t("American Express", "https://aexp.eightfold.ai/careers?query=intern"),
    _t("Visa", "https://careers.smartrecruiters.com/Visa/intern"),
    _t("Mastercard", "https://careers.mastercard.com/us/en/search-results?keywords=intern"),
]

BATCH_ORDER: list[list[dict]] = [
    TUNED,
    BIG_TECH,
    CONSUMER,
    BIO_PHARMA,
    FINANCE,
]

LINKEDIN_SEEDS: list[str] = [
    # AI / ML
    'internship "Summer 2027" ("machine learning" OR "artificial intelligence" OR "data science") "United States"',
    'intern "Summer 2027" (Anthropic OR OpenAI OR NVIDIA OR DeepMind OR "Scale AI") "United States"',
    # Big tech
    'intern "Summer 2027" (Amazon OR Apple OR Meta OR Google OR Microsoft OR NVIDIA) software engineering "United States"',
    'internship "Summer 2027" software engineering intern (Databricks OR Snowflake OR Salesforce OR Adobe OR IBM) "United States"',
    # Consumer / media
    'intern "Summer 2027" (Disney OR Netflix OR Uber OR Spotify OR Stripe OR Roblox) software engineering "United States"',
    'internship "Summer 2027" (Airbnb OR DoorDash OR Snap OR Pinterest OR TikTok) engineering "United States"',
    # Pharma / bio
    'internship "Summer 2027" ("data science" OR "machine learning" OR analytics) (Pfizer OR "Johnson & Johnson" OR "Eli Lilly" OR Merck OR Amgen) "United States"',
    'internship "Summer 2027" (biotech OR pharmaceutical OR "computational biology" OR bioinformatics OR genomics) "United States"',
    'intern "Summer 2027" (Recursion OR Insitro OR Tempus OR Illumina OR PathAI OR Moderna) "United States"',
    # Finance analytics
    'internship "Summer 2027" ("data analytics" OR "financial analytics" OR "investment analytics") (JPMorgan OR "Goldman Sachs" OR "Morgan Stanley" OR BlackRock) "United States"',
    # Healthcare data broadly
    'internship "Summer 2027" ("machine learning" OR "data science" OR AI) (pharma OR medical OR clinical OR biomedical OR healthcare) "United States"',
]


def _dedupe(companies: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for c in companies:
        key = c["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(c)
    return out


def all_companies() -> list[dict]:
    merged: list[dict] = []
    for batch in BATCH_ORDER:
        merged.extend(batch)
    return _dedupe(merged)


def batch_companies(index: int, batch_size: int = 6) -> list[dict]:
    companies = all_companies()
    if not companies:
        return []
    start = (index * batch_size) % len(companies)
    return [companies[(start + i) % len(companies)] for i in range(batch_size)]


def linkedin_seed(index: int) -> str:
    return LINKEDIN_SEEDS[index % len(LINKEDIN_SEEDS)]


def batch_stats() -> dict[str, int]:
    return {
        "tuned": len(TUNED),
        "big_tech": len(BIG_TECH),
        "consumer": len(CONSUMER),
        "bio_pharma": len(BIO_PHARMA),
        "finance": len(FINANCE),
        "total_unique": len(all_companies()),
        "linkedin_seeds": len(LINKEDIN_SEEDS),
    }
