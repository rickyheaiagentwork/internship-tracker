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
    _t("Disney", "https://www.disneycareers.com/en/search-jobs/intern?k=intern&l=United%20States", require_intern_title=True),
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
    _t("Wells Fargo", "https://www.wellsfargojobs.com/en/jobs/?search=intern"),
    _t("Charles Schwab", "https://jobs.schwab.com/search-jobs/intern"),
    _t("State Street", "https://careers.statestreet.com/global/en/search-results?keywords=intern"),
    _t("Northern Trust", "https://ntrs.wd1.myworkdayjobs.com/northerntrust?q=intern"),
]

# Fortune 500 — aerospace, defense, energy, healthcare, retail, industrial, semis
FORTUNE_500: list[dict] = [
    # Aerospace & defense
    _t("Lockheed Martin", "https://www.lockheedmartinjobs.com/search-jobs/intern"),
    _t("Boeing", "https://jobs.boeing.com/job-search?keyword=intern"),
    _t("RTX", "https://careers.rtx.com/global/en/search-results?keywords=intern"),
    _t("Northrop Grumman", "https://ngc.wd1.myworkdayjobs.com/Northrop_Grumman_External_Site?q=intern"),
    _t("General Dynamics", "https://gdit.wd5.myworkdayjobs.com/External_Career_Site?q=intern"),
    _t("L3Harris", "https://careers.l3harris.com/search-jobs/intern"),
    _t("Textron", "https://textron.taleo.net/careersection/textron/jobsearch.ftl?keyword=intern"),
    # Automotive & transport
    _t("Tesla", "https://www.tesla.com/careers/search?query=intern"),
    _t("General Motors", "https://search-careers.gm.com/en/jobs/?search=intern"),
    _t("Ford", "https://efds.fa.em5.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?keyword=intern"),
    _t("FedEx", "https://careers.fedex.com/fedex/jobs?keywords=intern"),
    _t("UPS", "https://www.jobs-ups.com/search-jobs/intern"),
    # Telecom & media
    _t("Verizon", "https://mycareer.verizon.com/jobs?keywords=intern"),
    _t("AT&T", "https://www.att.jobs/search-jobs/intern"),
    _t("T-Mobile", "https://careers.t-mobile.com/search-jobs/intern"),
    _t("Comcast", "https://jobs.comcast.com/search-jobs/intern"),
    _t("Charter Communications", "https://jobs.spectrum.com/search-jobs/intern"),
    # Energy
    _t("ExxonMobil", "https://jobs.exxonmobil.com/search-jobs/intern"),
    _t("Chevron", "https://careers.chevron.com/search-jobs/intern"),
    _t("ConocoPhillips", "https://careers.conocophillips.com/search-jobs/intern"),
    _t("Schlumberger", "https://careers.slb.com/search-jobs/intern"),
    # Healthcare & insurance
    _t("UnitedHealth Group", "https://careers.unitedhealthgroup.com/search-jobs/intern"),
    _t("CVS Health", "https://jobs.cvshealth.com/us/en/search-results?keywords=intern"),
    _t("McKesson", "https://mckesson.wd3.myworkdayjobs.com/External_Careers?q=intern"),
    _t("Elevance Health", "https://careers.elevancehealth.com/search-jobs/intern"),
    _t("Cigna", "https://jobs.thecignagroup.com/us/en/search-results?keywords=intern"),
    _t("Humana", "https://careers.humana.com/us/en/search-results?keywords=intern"),
    _t("Abbott", "https://abbott.wd5.myworkdayjobs.com/abbottcareers?q=intern"),
    _t("Medtronic", "https://medtronic.wd1.myworkdayjobs.com/MedtronicCareers?q=intern"),
    _t("Stryker", "https://stryker.wd1.myworkdayjobs.com/Stryker_Careers?q=intern"),
    _t("Boston Scientific", "https://jobs.bostonscientific.com/search-jobs/intern"),
    _t("Biogen", "https://biib.wd1.myworkdayjobs.com/external?q=intern"),
    _t("Regeneron", "https://careers.regeneron.com/search-jobs/intern"),
    _t("Danaher", "https://jobs.danaher.com/global/en/search-results?keywords=intern"),
    _t("Thermo Fisher Scientific", "https://jobs.thermofisher.com/global/en/search-results?keywords=intern"),
    _t("GE HealthCare", "https://careers.gehealthcare.com/global/en/search-results?keywords=intern"),
    _t("HCA Healthcare", "https://careers.hcahealthcare.com/search-jobs/intern"),
    _t("State Farm", "https://jobs.statefarm.com/main/jobs?keywords=intern"),
    _t("Progressive", "https://careers.progressive.com/search-jobs/intern"),
    _t("Allstate", "https://www.allstate.jobs/search-jobs/intern"),
    # Retail & consumer
    _t("Walmart", "https://careers.walmart.com/results?q=intern"),
    _t("Target", "https://corporate.target.com/careers/search?query=intern"),
    _t("Costco", "https://www.costco.com/jobs.html?keyword=intern"),
    _t("Home Depot", "https://careers.homedepot.com/job-search-results?keyword=intern"),
    _t("Lowe's", "https://talent.lowes.com/us/en/search-results?keywords=intern"),
    _t("Nike", "https://jobs.nike.com/search-jobs/intern"),
    _t("Procter & Gamble", "https://www.pgcareers.com/global/en/search-results?keywords=intern"),
    _t("PepsiCo", "https://www.pepsicojobs.com/search-jobs/intern"),
    _t("Mondelez International", "https://careers.mondelezinternational.com/search-jobs/intern"),
    _t("Starbucks", "https://careers.starbucks.com/search-jobs/intern"),
    _t("McDonald's", "https://careers.mcdonalds.com/search-jobs/intern"),
    _t("Colgate-Palmolive", "https://jobs.colgate.com/search-jobs/intern"),
    # Industrial & manufacturing
    _t("Honeywell", "https://careers.honeywell.com/us/en/search-results?keywords=intern"),
    _t("3M", "https://3m.wd1.myworkdayjobs.com/Search?q=intern"),
    _t("General Electric", "https://careers.ge.com/global/en/search-results?keywords=intern"),
    _t("Caterpillar", "https://cat.wd5.myworkdayjobs.com/CaterpillarCareers?q=intern"),
    _t("Deere & Company", "https://jobs.deere.com/search-jobs/intern"),
    _t("Emerson", "https://hdjq.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?keyword=intern"),
    _t("Parker Hannifin", "https://jobs.parker.com/search-jobs/intern"),
    _t("Johnson Controls", "https://jobs.johnsoncontrols.com/search-jobs/intern"),
    _t("Raymond James", "https://raymondjames.wd1.myworkdayjobs.com/RaymondJamesEarlyCareers?q=intern"),
    # Semiconductors & hardware
    _t("Broadcom", "https://broadcom.wd1.myworkdayjobs.com/External_Career?q=intern"),
    _t("Micron Technology", "https://micron.wd1.myworkdayjobs.com/External?q=intern"),
    _t("Texas Instruments", "https://careers.ti.com/en/sites/CX/jobs?keyword=intern"),
    _t("Applied Materials", "https://amat.wd1.myworkdayjobs.com/External?q=intern"),
    _t("Lam Research", "https://lamresearch.wd1.myworkdayjobs.com/External?q=intern"),
    _t("KLA", "https://kla.wd1.myworkdayjobs.com/Search?q=intern"),
    _t("HP", "https://jobs.hp.com/en/search-jobs/intern"),
    _t("HPE", "https://careers.hpe.com/us/en/search-results?keywords=intern"),
    _t("Western Digital", "https://jobs.smartrecruiters.com/WesternDigital/intern"),
    _t("Seagate", "https://seagatecareers.com/search-jobs/intern"),
    # Consulting & IT services (tech-heavy tracks)
    _t("Accenture", "https://www.accenture.com/us-en/careers/jobsearch?jk=intern"),
    _t("Deloitte", "https://apply.deloitte.com/careers/SearchJobs/intern"),
    _t("IBM Consulting", "https://www.ibm.com/careers/search?field_keyword_08%5B0%5D=Intern"),
    # Additional big tech / software not in BIG_TECH
    _t("Cloudflare", "https://boards.greenhouse.io/cloudflare?keyword=intern"),
    _t("MongoDB", "https://www.mongodb.com/careers/search?query=intern"),
    _t("Datadog", "https://careers.datadoghq.com/all-jobs?query=intern"),
    _t("CrowdStrike", "https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers?q=intern"),
    _t("Palo Alto Networks", "https://jobs.paloaltonetworks.com/en/search-jobs/intern"),
    _t("Fortinet", "https://edel.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?keyword=intern"),
    _t("Splunk", "https://careers.cisco.com/jobs/SearchJobs/intern?listFilterMode=1"),
    _t("Okta", "https://www.okta.com/company/careers/job-listing/?keywords=intern"),
    _t("Zscaler", "https://job-boards.greenhouse.io/zscaler"),
    _t("Snowflake", "https://careers.snowflake.com/us/en/search-results?keywords=intern"),
    _t("Unity", "https://unity.com/careers/positions?query=intern"),
    _t("Autodesk", "https://autodesk.wd1.myworkdayjobs.com/Ext?q=intern"),
    _t("Synopsys", "https://careers.synopsys.com/search-jobs/intern"),
    _t("Cadence", "https://cadence.wd1.myworkdayjobs.com/External_Careers?q=intern"),
    _t("Ansys", "https://careers.ansys.com/search-jobs/intern"),
]

# More Fortune 500 + tech employers with US intern programs
FORTUNE_500_EXTRA: list[dict] = [
    # Insurance & financial services
    _t("MetLife", "https://jobs.metlife.com/en/search-jobs/intern"),
    _t("Prudential", "https://jobs.prudential.com/us/en/search-results?keywords=intern"),
    _t("AIG", "https://aig.wd1.myworkdayjobs.com/aig?q=intern"),
    _t("Travelers", "https://careers.travelers.com/job-search-results?keyword=intern"),
    _t("Liberty Mutual", "https://jobs.libertymutualgroup.com/search-jobs/intern"),
    _t("Nationwide", "https://nationwide.wd1.myworkdayjobs.com/Nationwide_Career?q=intern"),
    _t("PNC", "https://careers.pnc.com/global/en/search-results?keywords=intern"),
    _t("Truist", "https://careers.truist.com/us/en/search-results?keywords=intern"),
    _t("U.S. Bank", "https://careers.usbank.com/global/en/search-results?keywords=intern"),
    _t("TD Bank", "https://jobs.td.com/en/search-jobs/intern"),
    _t("Discover", "https://jobs.discover.com/search-jobs/intern"),
    _t("Synchrony", "https://careers.synchrony.com/search-jobs/intern"),
    _t("TIAA", "https://tiaa.wd1.myworkdayjobs.com/Search?q=intern"),
    _t("Franklin Templeton", "https://franklintempleton.wd5.myworkdayjobs.com/Primary-External-1?q=intern"),
    _t("Invesco", "https://invesco.wd1.myworkdayjobs.com/IVZ?q=intern"),
    # Defense contractors & gov-tech
    _t("Leidos", "https://careers.leidos.com/search-jobs/intern"),
    _t("Booz Allen Hamilton", "https://careers.boozallen.com/search-jobs/intern"),
    _t("SAIC", "https://jobs.saic.com/search-jobs/intern"),
    _t("CACI", "https://careers.caci.com/global/en/search-results?keywords=intern"),
    _t("BAE Systems", "https://jobs.baesystems.com/global/en/search-results?keywords=intern"),
    _t("Huntington Ingalls", "https://careers.huntingtoningalls.com/search-jobs/intern"),
    _t("General Atomics", "https://sjobs.brassring.com/TGnewUI/Search/Home/Home?partnerid=25539&siteid=5313#keyWord=intern"),
    # Healthcare systems & health-tech
    _t("Epic Systems", "https://careers.epic.com/jobs/?keyword=intern"),
    _t("Veeva Systems", "https://careers.veeva.com/search-jobs/intern"),
    _t("Cerner", "https://careers.oracle.com/en/sites/jobsearch/jobs?keyword=intern%20cerner"),
    _t("Hologic", "https://careers.hologic.com/search-jobs/intern"),
    _t("Edwards Lifesciences", "https://careers.edwards.com/search-jobs/intern"),
    _t("Intuitive Surgical", "https://careers.intuitive.com/en/search-jobs/intern"),
    _t("Zimmer Biomet", "https://zimmerbiomet.wd1.myworkdayjobs.com/ZB?q=intern"),
    _t("Baxter", "https://jobs.baxter.com/en/search-jobs/intern"),
    _t("BD", "https://jobs.bd.com/en/search-jobs/intern"),
    # Retail & e-commerce
    _t("Kroger", "https://jobs.kroger.com/search-jobs/intern"),
    _t("Albertsons", "https://careers.albertsonscompanies.com/search-jobs/intern"),
    _t("Sysco", "https://careers.sysco.com/search-jobs/intern"),
    _t("Best Buy", "https://jobs.bestbuy.com/bby/search-jobs/intern"),
    _t("eBay", "https://jobs.ebayinc.com/us/en/search-results?keywords=intern"),
    _t("Etsy", "https://careers.etsy.com/jobs/search?query=intern"),
    _t("Wayfair", "https://www.wayfair.com/careers/jobs?query=intern"),
    _t("Chewy", "https://careers.chewy.com/us/en/search-results?keywords=intern"),
    _t("Gap", "https://jobs.gapinc.com/gapinc/search-jobs/intern"),
    _t("TJX", "https://jobs.tjx.com/search-jobs/intern"),
    # Travel, hospitality, entertainment
    _t("Marriott", "https://careers.marriott.com/search-jobs/intern"),
    _t("Hilton", "https://jobs.hilton.com/us/en/search-results?keywords=intern"),
    _t("Expedia", "https://careers.expediagroup.com/search-jobs/intern"),
    _t("Booking Holdings", "https://careers.bookingholdings.com/search-jobs/intern"),
    _t("Live Nation", "https://livenation.wd1.myworkdayjobs.com/LNExternalSite?q=intern"),
    _t("Warner Bros Discovery", "https://careers.wbd.com/global/en/search-results?keywords=intern"),
    _t("Paramount", "https://careers.paramount.com/search-jobs/intern"),
    # Auto / mobility / space
    _t("Rivian", "https://careers.rivian.com/careers?query=intern"),
    _t("Lucid Motors", "https://lucidmotors.com/careers/search?query=intern"),
    _t("Waymo", "https://careers.withwaymo.com/jobs?query=intern"),
    _t("SpaceX", "https://www.spacex.com/careers/?query=intern"),
    _t("Blue Origin", "https://www.blueorigin.com/careers/search?query=intern"),
    # Frontier AI / ML startups
    _t("Scale AI", "https://scale.com/careers?query=intern"),
    _t("Runway", "https://runwayml.com/careers"),
    _t("Weights & Biases", "https://wandb.ai/careers"),
    _t("Stability AI", "https://stability.ai/careers"),
    _t("Perplexity", "https://www.perplexity.ai/hub/careers"),
    _t("Character.AI", "https://jobs.ashbyhq.com/character"),
    _t("Adept", "https://www.adept.ai/careers"),
    _t("Inflection AI", "https://inflection.ai/careers"),
    # Software / infra / security
    _t("GitLab", "https://about.gitlab.com/jobs/all-jobs/?search=intern"),
    _t("HashiCorp", "https://www.hashicorp.com/en/careers/jobs?search=intern"),
    _t("Confluent", "https://careers.confluent.io/search-jobs/intern"),
    _t("Elastic", "https://jobs.elastic.co/search-jobs/intern"),
    _t("Akamai", "https://akamaicareers.inflightcloud.com/search-jobs/intern"),
    _t("Fastly", "https://www.fastly.com/about/jobs?search=intern"),
    _t("Rubrik", "https://www.rubrik.com/company/careers?search=intern"),
    _t("Pure Storage", "https://careers.purestorage.com/global/en/search-results?keywords=intern"),
    _t("NetApp", "https://careers.netapp.com/search-jobs/intern"),
    _t("Nutanix", "https://careers.nutanix.com/search-jobs/intern"),
    _t("DocuSign", "https://careers.docusign.com/search-jobs/intern"),
    _t("HubSpot", "https://www.hubspot.com/careers/jobs?query=intern"),
    _t("Asana", "https://asana.com/jobs/all?query=intern"),
    _t("Duolingo", "https://careers.duolingo.com/openings?query=intern"),
    _t("Figma", "https://www.figma.com/careers/?query=intern"),
    _t("Plaid", "https://plaid.com/careers/openings/?query=intern"),
    _t("Chime", "https://www.chime.com/careers/?query=intern"),
    _t("SoFi", "https://www.sofi.com/careers/?query=intern"),
    _t("Robinhood", "https://careers.robinhood.com/?query=intern"),
    # Industrial / chemicals / energy
    _t("DuPont", "https://careers.dupont.com/search-jobs/intern"),
    _t("Dow", "https://corporate.dow.com/en-us/careers/jobs.html?keyword=intern"),
    _t("Halliburton", "https://jobs.halliburton.com/search-jobs/intern"),
    _t("Baker Hughes", "https://careers.bakerhughes.com/global/en/search-results?keywords=intern"),
    _t("NextEra Energy", "https://careers.nexteraenergy.com/search-jobs/intern"),
    _t("Duke Energy", "https://careers.duke-energy.com/search-jobs/intern"),
    _t("Southern Company", "https://southerncompany.wd1.myworkdayjobs.com/SouthernCompany?q=intern"),
    # Consulting
    _t("McKinsey", "https://www.mckinsey.com/careers/search-jobs?query=intern"),
    _t("BCG", "https://careers.bcg.com/global/en/search-results?keywords=intern"),
    _t("Bain", "https://www.bain.com/careers/find-a-role/?keyword=intern"),
    _t("EY", "https://careers.ey.com/search-jobs/intern"),
    _t("KPMG", "https://www.kpmgcampus.com/careers/search?query=intern"),
    _t("PwC", "https://www.pwc.com/us/en/careers/university-student-programs.html"),
]

BATCH_ORDER: list[list[dict]] = [
    TUNED,
    BIG_TECH,
    CONSUMER,
    BIO_PHARMA,
    FINANCE,
    FORTUNE_500,
    FORTUNE_500_EXTRA,
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
    # Fortune 500 — defense, auto, healthcare, retail
    'intern "Summer 2027" (Tesla OR Boeing OR Lockheed OR "General Motors" OR Ford) engineering "United States"',
    'internship "Summer 2027" ("data science" OR software OR analytics) (UnitedHealth OR Abbott OR Medtronic OR "Thermo Fisher") "United States"',
    'intern "Summer 2027" (Walmart OR Target OR Nike OR "Procter & Gamble") technology OR data "United States"',
    'internship "Summer 2027" software engineering (Broadcom OR Micron OR "Texas Instruments" OR "Applied Materials") "United States"',
    # More Fortune 500 + fintech / software
    'intern "Summer 2027" (SpaceX OR Rivian OR Waymo OR "Blue Origin") engineering "United States"',
    'internship "Summer 2027" software (GitLab OR HashiCorp OR Confluent OR Elastic OR Datadog) "United States"',
    'intern "Summer 2027" (Epic OR Veeva OR "UnitedHealth" OR Cigna) ("software" OR "data science") "United States"',
    'internship "Summer 2027" (Leidos OR "Booz Allen" OR SAIC OR "BAE Systems") engineering "United States"',
    'intern "Summer 2027" (Robinhood OR Chime OR SoFi OR Plaid OR Stripe) engineering "United States"',
    'internship "Summer 2027" ("machine learning" OR AI) (Scale OR Perplexity OR Cohere OR "Hugging Face") "United States"',
    'intern "Summer 2027" (Marriott OR Expedia OR "Warner Bros" OR Paramount) technology "United States"',
    'internship "Summer 2027" ("data analytics" OR "data science") (PNC OR Truist OR "Wells Fargo" OR Discover) "United States"',
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


def batch_companies(index: int, batch_size: int = 18) -> list[dict]:
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
        "fortune_500": len(FORTUNE_500),
        "fortune_500_extra": len(FORTUNE_500_EXTRA),
        "total_unique": len(all_companies()),
        "linkedin_seeds": len(LINKEDIN_SEEDS),
    }
