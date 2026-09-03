"""Shared fit filters for internship search (PROFILE-aligned)."""
from __future__ import annotations

import re
import urllib.request
from typing import Any

UA = "Mozilla/5.0 internship-active-scan/2.0"

BIO_AI_KW = re.compile(
    r"\b("
    r"bio[- ]?ai|computational biology|bioinformatics|biomedical|biotech|"
    r"genomic|genomics|drug discovery|pharma|pharmaceutical|clinical (ml|ai|data)|"
    r"healthcare|health ?tech|digital health|oncology|pathology"
    r")\b",
    re.I,
)
AI_ML_KW = re.compile(
    r"\b("
    r"machine learning|artificial intelligence|\bai\b|\bml\b|"
    r"deep learning|llm|nlp|computer vision|data science|"
    r"applied scientist|research scientist|interpretability"
    r")\b",
    re.I,
)
BIO_COMPANIES = re.compile(
    r"\b("
    r"recursion|insitro|schr.?dinger|atomwise|generate|deep genomics|"
    r"isomorphic|benchsci|pathai|owkin|tempus|flatiron|verily|illumina|10x|"
    r"moderna|genentech|roche|amgen|gilead|pfizer|merck|novartis|abbvie|"
    r"janssen|johnson|lilly|eli lilly|astrazeneca|guardant|natera|iqvia|"
    r"philips|abbott|medtronic|stryker|boston scientific|biogen|regeneron|"
    r"thermo fisher|danaher|bristol myers|bms"
    r")\b",
    re.I,
)
FINANCE_ANALYTICS_KW = re.compile(
    r"\b("
    r"financial analytics|investment analytics|risk analytics|"
    r"portfolio analytics|data analytics|quantitative analytics|"
    r"markets analytics|wealth analytics|equity research|investment research|"
    r"investment management|capital markets|global research|pricing strategy|"
    r"data and analytics"
    r")\b",
    re.I,
)
FINANCE_ROLE_KW = re.compile(
    r"\b("
    r"financial analytics|investment analytics|risk analytics|"
    r"portfolio analytics|quantitative analytics|markets analytics|"
    r"wealth analytics|equity research|investment research|investment management|"
    r"capital markets|global research|pricing strategy|data and analytics|"
    r"quantitative (research|developer|analyst|strategy)|quant (research|developer|analyst)|"
    r"markets intern|trading intern|macro analyst"
    r")\b",
    re.I,
)
FINANCE_COMPANIES = re.compile(
    r"\b("
    r"jpmorgan|jp morgan|chase|goldman|morgan stanley|blackrock|"
    r"fidelity|bank of america|bofa|citigroup|\bciti\b|capital one|"
    r"wells fargo|bny|deutsche bank|ubs|credit suisse|barclays|"
    r"huntington|new york life|american express|visa|mastercard|"
    r"interactive brokers|freddie mac|fannie mae|standard chartered|"
    r"arrowstreet|point72|virtu|voloridge|susquehanna|d\.?e\.? shaw|"
    r"akuna|aquatic capital|castleton|optiver|pdt partners|the trade desk|"
    r"federal reserve"
    r")\b",
    re.I,
)
PROP_TRADING_REJECT = re.compile(
    r"\b("
    r"quant trading|market making|prop trading|proprietary trading|"
    r"quantitative trading|trading intern"
    r")\b",
    re.I,
)
TRADING_SHOP = re.compile(
    r"\b(hudson river trading|hrt|citadel securities|jane street|optiver|"
    r"two sigma|imc trading|five rings|akuna|old mission|tower research|"
    r"chicago trading|voloridge|point72|pdt partners|virtu)\b",
    re.I,
)


def fetch(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]


def normalize_role_title(role: str) -> str:
    r = role.lower()
    r = re.sub(r"[\U0001F1E6-\U0001F1FF]{2}", "", r)
    r = re.sub(r"\b(summer|fall|spring|winter)\s*20\d{2}\b", "", r)
    r = re.sub(r"\b20\d{2}\b", "", r)
    r = re.sub(r"\([^)]*\)", " ", r)
    r = re.sub(r"\b(united states|usa|u\.s\.)\b", "", r)
    r = re.sub(r"\b(new york|san francisco|boston|chicago|austin|redmond|mountain view|palo alto)\b", "", r)
    r = re.sub(r"[^a-z0-9]+", " ", r)
    return re.sub(r"\s+", " ", r).strip()


def role_fingerprint(company: str, role: str) -> str:
    return f"{company.lower().strip()}::{normalize_role_title(role)}"


def url_priority(url: str) -> int:
    u = url.lower()
    if "linkedin.com" in u:
        return 1
    if any(
        x in u
        for x in [
            "google.com/about/careers",
            "jobs.apple.com",
            "amazon.jobs",
            "apply.careers.microsoft.com",
            "careers.microsoft.com",
            "metacareers.com",
            "nvidia.wd",
            "careers.jpmorgan.com",
            "careers.blackrock.com",
            "stripe.com/jobs",
            "jobs.disneycareers.com",
            "jobs.netflix.com",
        ]
    ):
        return 10
    if any(x in u for x in ["greenhouse.io", "lever.co", "ashbyhq.com", "myworkdayjobs"]):
        return 6
    return 4


def pick_better_opening(current: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    cur_score = url_priority(current.get("application_url") or current.get("posting_url", ""))
    new_score = url_priority(candidate.get("application_url") or candidate.get("posting_url", ""))
    if new_score > cur_score:
        return candidate
    if new_score < cur_score:
        return current
    return candidate if candidate.get("verified_at", "") >= current.get("verified_at", "") else current


def dedupe_openings(openings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_role: dict[str, dict[str, Any]] = {}
    for opening in openings:
        key = role_fingerprint(opening["company"], opening["role_title"])
        if key in by_role:
            by_role[key] = pick_better_opening(by_role[key], opening)
        else:
            by_role[key] = opening
    return list(by_role.values())


def blob(company: str, role: str, loc: str = "") -> str:
    return f"{company} {role} {loc}".lower()


def looks_candidate(
    company: str,
    role: str,
    loc: str = "",
    extra: str = "",
    *,
    page_text: str = "",
) -> bool:
    title_text = f"{company} {role} {loc} {extra}".lower()
    full_text = f"{title_text} {page_text}".lower() if page_text else title_text
    if "intern" not in title_text and "internship" not in title_text:
        return False
    has_year = "2027" in full_text or "summer 2027" in full_text
    university_intern = bool(
        re.search(
            r"intern opportunities for university students|software engineering intern|"
            r"undergraduate intern|university intern|"
            r"nvidia 2027 internships",
            title_text,
        )
    )
    if not has_year and not university_intern:
        return False
    if any(x in title_text for x in ["fall 2026", "spring 2027", "winter 2027"]) and "summer 2027" not in full_text:
        return False
    if any(
        x in title_text
        for x in [
            "ireland",
            "dublin",
            "india",
            "bengaluru",
            "hyderabad",
            "london,",
            "london ",
            "toronto",
            "canada",
            "shanghai",
            "remote - europe",
            "china",
            "taiwan",
            "taipei",
            "mexico",
            "hong kong",
            "singapore",
            "tokyo",
            "ankara",
            "emea",
            "apac",
            "grange castle",
        ]
    ) and not re.search(
        r"united states|u\.s\.|usa|new york|san francisco|seattle|austin|boston|"
        r"california|washington|texas|massachusetts|chicago|redmond|mountain view|amers",
        title_text,
    ):
        return False
    if re.search(r"master'?s|mba|ph\.?d|graduate student only", title_text) and not re.search(
        r"bachelor|undergrad|\bbs\b", title_text
    ):
        return False
    if re.search(r"\b(phd|ph\.d|doctorate)\b", title_text) and not re.search(
        r"bachelor|undergrad|\bbs\b", title_text
    ):
        return False
    if re.search(r"\bms\b|master'?s degree", title_text) and not re.search(
        r"bachelor|undergrad|\bbs\b", title_text
    ):
        return False
    if re.search(
        r"\b(operations management|it audit|audit intern|business analyst|"
        r"gas compressor|accounting|hr intern|marketing intern)\b",
        title_text,
    ):
        return False
    if PROP_TRADING_REJECT.search(title_text):
        return False
    if TRADING_SHOP.search(title_text) and not FINANCE_ANALYTICS_KW.search(title_text) and not AI_ML_KW.search(title_text):
        if re.search(r"\b(quant|trading|market)\b", title_text):
            return False
    return True


def fit_score(company: str, role: str, loc: str = "") -> int:
    b = f"{company} {role} {loc}"
    score = 0
    if BIO_AI_KW.search(b) or BIO_COMPANIES.search(company):
        score += 100
    if AI_ML_KW.search(b):
        score += 80
    if FINANCE_COMPANIES.search(company) and (
        FINANCE_ANALYTICS_KW.search(b) or AI_ML_KW.search(b)
    ):
        score += 70
    elif FINANCE_ANALYTICS_KW.search(b) and re.search(
        r"financ|invest|risk|portfolio|wealth|asset", b, re.I
    ):
        score += 60
    if re.search(r"software|swe|engineer|developer|full[- ]?stack", b, re.I):
        score += 20
    if PROP_TRADING_REJECT.search(b):
        score -= 100
    if BIO_AI_KW.search(b) and AI_ML_KW.search(b):
        score += 40
    return score


def category_for(company: str, role: str) -> str:
    b = f"{company} {role}"
    r = role.lower()

    if "product" in r and "engineer" not in r and "software" not in r:
        return "PM"

    if BIO_AI_KW.search(b):
        return "Bio-AI"
    if BIO_COMPANIES.search(company) and (
        AI_ML_KW.search(b)
        or "data" in r
        or "informatics" in r
        or "computational" in r
        or "clinical" in r
    ):
        return "Bio-AI"

    if FINANCE_COMPANIES.search(company) and FINANCE_ROLE_KW.search(b):
        return "Finance"
    if FINANCE_ROLE_KW.search(b) and re.search(
        r"financ|invest|bank|markets|trading|wealth|portfolio|equity|quant",
        b,
        re.I,
    ):
        return "Finance"
    if FINANCE_ANALYTICS_KW.search(b):
        return "Finance"

    if any(
        x in r
        for x in [
            "machine learning",
            "artificial intelligence",
            "data science",
            "llm",
            "interpretability",
            "deep learning",
            "computer vision",
        ]
    ) or re.search(r"\b(ai|ml)\b", r):
        return "AI/ML"
    if "data analytics" in r:
        return "AI/ML"

    return "SWE"


def verify_posting(url: str, html: str | None = None) -> dict[str, Any] | None:
    try:
        if html is None:
            code, html = fetch(url)
            if code >= 400:
                return None
        else:
            code = 200
    except Exception:
        return None

    low = html.lower()
    if any(
        x in low
        for x in [
            "job not found",
            "no longer available",
            "this job has been closed",
            "position is no longer",
        ]
    ):
        title = re.search(r"<title>([^<]+)", html, re.I)
        t = (title.group(1) if title else "").lower()
        if "not found" in t or "no longer" in low[:2000]:
            return None

    if "ireland" in low and "dublin" in low and "united states" not in low:
        return None
    if any(x in low for x in ["bengaluru", "hyderabad, india", "amazon development centre ireland"]):
        return None
    if re.search(r"\b(emea|apac)\b", low) and not re.search(
        r"united states|u\.s\.|usa|new york|san francisco|seattle|amers", low
    ):
        return None
    if re.search(r"mexico city|hong kong sar|grange castle", low) and not re.search(
        r"united states|u\.s\.|usa|new york|san francisco|seattle|amers", low
    ):
        return None

    s27 = (
        ("summer 2027" in low)
        or ("summer-2027" in low)
        or bool(re.search(r"2027.{0,40}(intern|internship)", low))
        or bool(re.search(r"(intern|internship).{0,40}summer 2027", low))
        or bool(re.search(r"target start range.{0,80}summer 2027", low))
        or bool(
            re.search(r"intern opportunities for university students", low)
            and "2027" in low
        )
        or bool(re.search(r"nvidia 2027 internships", low))
        or bool(re.search(r"2027.{0,20}software engineering.{0,20}internship", low))
    )
    if not s27:
        return None

    masters_only = bool(
        re.search(
            r"master'?s (degree )?students? only|requires a master|must be (enrolled in|pursuing) a master|mba only",
            low,
        )
    ) and not re.search(r"bachelor|undergraduate|undergrad|\bbs\b", low)
    if masters_only:
        return None

    ug = any(
        x in low
        for x in [
            "bachelor",
            "undergraduate",
            "undergrad",
            "pursuing a bs",
            "bachelor's",
            "bs/ms",
            "bs,",
            "b.s.",
            " b.s ",
            " currently pursuing a degree",
            "pursuing a b.s",
        ]
    )
    phd_only = bool(re.search(r"pursuing a phd|phd students only|ph\.d\. only", low)) and not ug
    if phd_only:
        return None
    if not ug and "student" not in low and "university" not in low:
        return None

    usa = any(
        x in low
        for x in [
            "united states",
            "usa",
            "u.s.",
            "us, ca",
            "us, wa",
            "us, tx",
            "us, ny",
            "us-ca",
            "us-wa",
            "new york",
            "san francisco",
            "chicago",
            "seattle",
            "austin",
            "boston",
            "california",
            "colorado",
            "washington",
            "texas",
            "massachusetts",
            "santa clara",
            "remote - usa",
            "remote, usa",
        ]
    )
    if not usa:
        return None

    return {"ok": True}


def make_opening(
    company: str,
    role: str,
    url: str,
    *,
    loc: str = "United States",
    today: str,
    source: str,
    min_fit: int = 0,
    page_text: str = "",
) -> dict[str, Any] | None:
    if not looks_candidate(company, role, loc, page_text=page_text):
        return None
    score = fit_score(company, role, loc)
    if score < min_fit and score < 20:
        return None
    info = verify_posting(url, page_text or None)
    if not info:
        return None
    return {
        "id": f"{slug(company)}-{slug(role)[:40]}-s27",
        "company": company,
        "role_title": role if "2027" in role or "Summer" in role else f"{role} (Summer 2027)",
        "season": "Summer 2027",
        "listing_status": "open",
        "verified_at": today,
        "posting_url": url,
        "application_url": url,
        "tier": 1 if score >= 100 else 2,
        "category": category_for(company, role),
        "degree_level": ["BS"],
        "location": loc if loc.startswith("United States") else f"United States ({loc})",
        "work_model": "Onsite",
        "application_status": "Not started",
        "notes": f"Found via {source} on {today}. Re-verify before applying.",
        "fit_score": score,
        "source": source,
    }
