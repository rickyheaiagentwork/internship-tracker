"""Shared fit filters for internship search (PROFILE-aligned).

Policy: **search wide, rank narrow.** Anything that is a real US undergrad
Summer 2027 technical internship is kept and tiered; only off-domain roles
(tax, audit, HR, marketing, environmental, …) and hard mismatches are dropped.
"""
from __future__ import annotations

import re
import urllib.request
from typing import Any

UA = "Mozilla/5.0 internship-active-scan/2.0"

BIO_AI_KW = re.compile(
    r"\b("
    r"bio[- ]?ai|computational biology|bioinformatics|biomedical|biotech|"
    r"genomic|genomics|drug discovery|pharma|pharmaceutical|clinical (ml|ai|data|informatics)|"
    r"healthcare|health ?tech|digital health|oncology|pathology|"
    r"life sciences?|medical (device|imaging|data)|proteomic|molecular|"
    r"immunolog|neuroscience|epidemiolog|biostatistic|translational"
    r")\b",
    re.I,
)
AI_ML_KW = re.compile(
    r"\b("
    r"machine learning|artificial intelligence|\bai\b|\bml\b|"
    r"deep learning|llm|nlp|natural language|computer vision|data science|data scientist|"
    r"applied scientist|research scientist|interpretability|"
    r"generative|foundation model|reinforcement learning|recommendation|"
    r"speech|perception|mlops|ai engineer"
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
    r"thermo fisher|danaher|bristol myers|bms|medpace|alcon|elanco|"
    r"beckman coulter|edwards lifesciences|corteva|agilent|bio-?rad|"
    r"vertex|takeda|sanofi|gsk|bayer|zoetis|baxter|becton|\bbd\b|hologic"
    r")\b",
    re.I,
)
FINANCE_ANALYTICS_KW = re.compile(
    r"\b("
    r"financial analytics|investment analytics|risk analytics|"
    r"portfolio analytics|data analytics|quantitative analytics|"
    r"markets analytics|wealth analytics|equity research|investment research|"
    r"investment management|capital markets|global research|pricing strategy|"
    r"data and analytics|financial engineering|credit risk|fraud"
    r")\b",
    re.I,
)
FINANCE_ROLE_KW = re.compile(
    r"\b("
    r"financial analytics|investment analytics|risk analytics|"
    r"portfolio analytics|quantitative analytics|markets analytics|"
    r"wealth analytics|equity research|investment research|investment management|"
    r"capital markets|global research|pricing strategy|data and analytics|"
    r"quantitative (research|developer|analyst|strategy|technology)|"
    r"quant (research|developer|analyst)|"
    r"markets intern|macro analyst|financial engineering|credit risk"
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
    r"federal reserve|truist|pnc|u\.?s\.? bank|state street|northern trust|"
    r"schwab|raymond james|stifel|jefferies|lazard|evercore|rbc|bnp paribas|"
    r"discover|synchrony|ally|regions|fifth third|keybank|m&t"
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

# ---------------------------------------------------------------------------
# Internship vocabulary — "intern" is only one of the words employers use.
# ---------------------------------------------------------------------------
INTERN_TITLE = re.compile(
    r"\b("
    r"intern|interns|interning|internship|internships|"
    r"co[- ]?op|coop|"
    r"summer (analyst|associate|scholar|program|fellow)|"
    r"campus (program|recruiting|hire|opportunit)|"
    r"university (program|recruiting|relations|talent)|"
    r"student (program|opportunit|position|worker)|"
    r"early (career|talent)|future talent|emerging talent|"
    r"apprentice|apprenticeship|trainee|externship|practicum|"
    r"fellowship|fellow"
    r")\b",
    re.I,
)

# Technical / scientific domains we care about — deliberately broad.
# Suffix wildcards matter: "\bcyber\b" never matches "Cybersecurity".
TECH_KW = re.compile(
    r"\b("
    r"software|swe|programming|developer|development|engineer\w*|"
    r"full[- ]?stack|front[- ]?end|back[- ]?end|web|mobile|ios|android|"
    r"computer\w*|comp sci|"
    r"data|analytic\w*|analyst|analytical|business intelligence|\bbi\b|database|"
    r"machine learning|artificial intelligence|\bai\b|\bml\b|deep learning|"
    r"llm|nlp|vision|robotic\w*|autonom\w*|embedded|firmware|hardware|"
    r"electric\w*|electronic\w*|\bece\b|semiconductor\w*|chip|silicon|vlsi|fpga|asic|"
    r"signal processing|photonic\w*|mechatronic\w*|avionic\w*|aerospace|"
    r"cloud|devops|\bsre\b|platform|infrastructure|network\w*|distributed|"
    r"cyber\w*|security|infosec|information (technology|systems|services)|informatics|"
    r"system\w*|simulation|modeling|computational|scientific|scien(ce|tist|ces)|"
    r"quantitative|statistic\w*|mathematic\w*|algorithm\w*|optimization|"
    r"research|\br&d\b|innovation|technolog\w*|technical|digital|"
    r"product manage\w*|technical program|automation|quality engineering|"
    r"game|graphics|\bapi\b|\bux\b|geospatial|\bgis\b|insights"
    r")\b",
    re.I,
)
# Case-sensitive: bare "IT" is a domain, bare "it" is a pronoun.
TECH_IT = re.compile(r"\bIT\b|\bI\.T\.")

# Strong technical signal — enough to override an off-domain word in the title
# (e.g. "Marketing Data Science Intern" is still a data science role).
STRONG_TECH = re.compile(
    r"\b("
    r"software|computer scien\w*|computer engineer\w*|"
    r"data (science|scientist|engineer|engineering|architecture)|"
    r"machine learning|artificial intelligence|\bai\b|\bml\b|deep learning|llm|"
    r"computer vision|robotic\w*|embedded|firmware|semiconductor\w*|"
    r"cyber ?security|cloud|devops|informatics|bioinformatics|computational"
    r")\b",
    re.I,
)

# Role families outside Ricky's domain. Rejected unless STRONG_TECH also matches.
OFF_DOMAIN = re.compile(
    r"\b("
    r"tax|audit|auditing|assurance|accounting|accountant|bookkeep|payroll|"
    r"actuar(y|ial|ies)|underwrit\w*|claims|"
    r"human resources|hr intern\w*|talent acquisition|recruiting coordinator|"
    r"marketing|brand|social media|advertising|public relations|copywrit|"
    r"sales|merchandis\w*|store (management|operations)|retail operations|"
    r"legal|paralegal|contracts|"
    r"environmental|forestry|geolog\w*|land development|landscape|surveying|"
    r"civil engineer\w*|structural engineer\w*|construction|"
    r"(landscape|building|design) architect\w*|architectural|"
    r"real estate|property management|facilities|"
    r"culinary|hospitality|nursing|nurse|pharmacy technician|physical therapy|"
    r"social work|teaching|athletic|event planning|interior design|fashion|"
    r"procurement|warehouse|"
    r"restructuring|due diligence|wealth management|private banking|"
    r"retail banking|investment banking|anti-money laundering|"
    r"management consulting|regulatory consulting"
    r")\b",
    re.I,
)

# ---------------------------------------------------------------------------
# Geography — word-boundary matching. (The old substring test rejected every
# Indiana / Indianapolis role because "Indianapolis" contains "india".)
# ---------------------------------------------------------------------------
US_SIGNAL = re.compile(
    r"(\b(united states|u\.?s\.?a?|usa|stateside|nationwide|remote)\b"
    r"|,\s*(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|"
    r"MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|"
    r"WA|WV|WI|WY|DC)\b"
    r"|\b(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|"
    r"florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|"
    r"maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|"
    r"nebraska|nevada|new hampshire|new jersey|new mexico|new york|north carolina|"
    r"north dakota|ohio|oklahoma|oregon|pennsylvania|rhode island|south carolina|"
    r"south dakota|tennessee|texas|utah|vermont|virginia|washington|west virginia|"
    r"wisconsin|wyoming|district of columbia)\b"
    r"|\b(san francisco|silicon valley|bay area|new york city|nyc|seattle|austin|"
    r"boston|chicago|denver|atlanta|dallas|houston|phoenix|philadelphia|"
    r"san diego|san jose|los angeles|portland|pittsburgh|detroit|minneapolis|"
    r"indianapolis|columbus|charlotte|nashville|raleigh|orlando|miami|tampa|"
    r"redmond|bellevue|mountain view|palo alto|sunnyvale|santa clara|menlo park|"
    r"cupertino|cambridge, ma|ann arbor|madison|st\.? louis|kansas city|"
    r"salt lake city|las vegas|amers|americas)\b)",
    re.I,
)
NON_US_SIGNAL = re.compile(
    r"\b("
    r"india|bengaluru|bangalore|hyderabad|pune|gurgaon|gurugram|noida|chennai|mumbai|"
    r"china|beijing|shanghai|shenzhen|guangzhou|taiwan|taipei|hsinchu|"
    r"japan|tokyo|osaka|korea|seoul|singapore|hong kong|"
    r"australia|sydney|melbourne|new zealand|"
    r"canada|toronto|vancouver|montreal|ottawa|waterloo, on|ontario|quebec|alberta|"
    r"mexico|guadalajara|monterrey|brazil|sao paulo|argentina|chile|colombia|costa rica|"
    r"ireland|dublin|grange castle|united kingdom|england|scotland|wales|"
    r"london|manchester|edinburgh|glasgow|bristol, uk|\buk\b|"
    r"france|paris|germany|berlin|munich|frankfurt|hamburg|"
    r"netherlands|amsterdam|belgium|brussels|spain|madrid|barcelona|"
    r"italy|milan|rome|switzerland|zurich|geneva|austria|vienna|"
    r"sweden|stockholm|denmark|copenhagen|norway|oslo|finland|helsinki|"
    r"poland|warsaw|krakow|romania|bucharest|czech|prague|hungary|budapest|"
    r"portugal|lisbon|greece|athens|"
    r"israel|tel aviv|turkey|ankara|istanbul|egypt|cairo|"
    r"south africa|nigeria|kenya|morocco|"
    r"uae|dubai|abu dhabi|qatar|doha|saudi|riyadh|"
    r"philippines|manila|vietnam|hanoi|thailand|bangkok|malaysia|kuala lumpur|"
    r"indonesia|jakarta|"
    r"emea|apac|latam|off-cycle"
    r")\b",
    re.I,
)

# Season / year handling
SEASON_YEAR = re.compile(r"\b20(?:1\d|2\d|3\d)\b")
OFF_SEASON = re.compile(
    r"\b(fall|autumn|spring|winter)\s*20(2[5-9])\b|\bwinter/spring\b|\bfall/winter\b",
    re.I,
)
GRAD_ONLY = re.compile(
    r"master'?s?(\s+(degree|student|candidate|program))?|\bmba\b|ph\.?\s?d|doctoral|doctorate|\bms/phd\b",
    re.I,
)
UNDERGRAD_SIGNAL = re.compile(r"bachelor|undergrad(uate)?|\bb\.?s\.?\b|\bbse\b|\bba\b|sophomore|junior|senior", re.I)


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
    if any(
        x in u
        for x in [
            "greenhouse.io",
            "lever.co",
            "ashbyhq.com",
            "myworkdayjobs",
            "icims.com",
            "smartrecruiters",
            "jobvite",
            "workable",
            "taleo",
            "oraclecloud",
            "successfactors",
            "eightfold",
            "avature",
        ]
    ):
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


def is_us(text: str) -> bool:
    """US unless a foreign location is named without any US signal."""
    if US_SIGNAL.search(text):
        return True
    return not NON_US_SIGNAL.search(text)


def is_technical(text: str) -> bool:
    return bool(TECH_KW.search(text) or TECH_IT.search(text))


def reject_reason(
    company: str,
    role: str,
    loc: str = "",
    extra: str = "",
    *,
    page_text: str = "",
) -> str | None:
    """Return why this listing is not a candidate, or None if it passes."""
    title_text = f"{company} {role} {loc}".strip()
    with_extra = f"{title_text} {extra}".strip()
    full_text = f"{with_extra} {page_text}" if page_text else with_extra

    if not INTERN_TITLE.search(title_text):
        return "not-an-internship-title"

    # Season / year. Prefer evidence in the title; fall back to page text.
    years = set(SEASON_YEAR.findall(role)) | set(SEASON_YEAR.findall(company))
    if years and "2027" not in years:
        return f"wrong-year({','.join(sorted(years))})"
    if not years and "2027" not in full_text:
        return "no-2027-evidence"
    if OFF_SEASON.search(title_text) and not re.search(r"summer\s*2027", full_text, re.I):
        return "off-season"

    if not is_us(title_text):
        return "non-us"

    if GRAD_ONLY.search(title_text) and not UNDERGRAD_SIGNAL.search(title_text):
        return "graduate-only"

    if PROP_TRADING_REJECT.search(title_text):
        return "prop-trading"
    if (
        TRADING_SHOP.search(title_text)
        and re.search(r"\b(quant|trading|market)\b", title_text, re.I)
        and not FINANCE_ANALYTICS_KW.search(title_text)
        and not AI_ML_KW.search(title_text)
    ):
        return "trading-shop"

    if OFF_DOMAIN.search(title_text) and not STRONG_TECH.search(title_text):
        return "off-domain"

    if not is_technical(title_text):
        return "non-technical"

    return None


def looks_candidate(
    company: str,
    role: str,
    loc: str = "",
    extra: str = "",
    *,
    page_text: str = "",
) -> bool:
    return reject_reason(company, role, loc, extra, page_text=page_text) is None


def fit_score(company: str, role: str, loc: str = "") -> int:
    b = f"{company} {role} {loc}"
    score = 0
    if BIO_AI_KW.search(b) or BIO_COMPANIES.search(company):
        score += 100
    if AI_ML_KW.search(b):
        score += 80
    if BIO_AI_KW.search(b) and AI_ML_KW.search(b):
        score += 40
    if FINANCE_COMPANIES.search(company) and (
        FINANCE_ANALYTICS_KW.search(b) or AI_ML_KW.search(b)
    ):
        score += 70
    elif FINANCE_ANALYTICS_KW.search(b) and re.search(
        r"financ|invest|risk|portfolio|wealth|asset", b, re.I
    ):
        score += 60
    if re.search(r"software|\bswe\b|engineer|developer|full[- ]?stack|computer science", b, re.I):
        score += 30
    if re.search(r"\bdata\b|analytics|business intelligence|\bbi\b|database|statistic", b, re.I):
        score += 25
    if re.search(r"research|\br&d\b|computational|informatics|simulation|scientist", b, re.I):
        score += 20
    if re.search(r"cyber|security|cloud|devops|\bsre\b|infrastructure|network|platform", b, re.I):
        score += 15
    if re.search(r"hardware|embedded|firmware|electrical|semiconductor|chip|robotics|fpga|asic", b, re.I):
        score += 15
    if TECH_IT.search(b) or re.search(r"information technology|digital|technolog", b, re.I):
        score += 10
    if PROP_TRADING_REJECT.search(b):
        score -= 100
    return score


def tier_for(score: int) -> int:
    if score >= 100:
        return 1
    if score >= 40:
        return 2
    return 3


def category_for(company: str, role: str) -> str:
    b = f"{company} {role}"
    r = role.lower()

    if "product manage" in r or ("product" in r and not re.search(r"engineer|software|data", r)):
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
    if FINANCE_ANALYTICS_KW.search(b) and re.search(r"financ|invest|risk|credit|fraud", b, re.I):
        return "Finance"

    if AI_ML_KW.search(r) or re.search(r"\b(ai|ml)\b", r):
        return "AI/ML"

    if re.search(r"cyber|security|information technology|\bit\b|infosec", r, re.I) or TECH_IT.search(role):
        return "Security & IT"

    if re.search(
        r"hardware|embedded|firmware|electrical|electronics|semiconductor|chip|silicon|"
        r"vlsi|fpga|asic|robotics|mechatronic|signal processing",
        r,
        re.I,
    ):
        return "Hardware"

    if re.search(r"\bdata\b|analytics|business intelligence|\bbi\b|database|informatics", r, re.I):
        return "Data"

    if re.search(r"research|\br&d\b|computational|simulation|scientist", r, re.I):
        return "Research"

    return "SWE"


def verify_posting(url: str, html: str | None = None) -> dict[str, Any] | None:
    """Confirm a posting is live and plausibly Summer 2027 / US / undergrad.

    Returns a dict with a `confidence` key, or None to reject. Pages that render
    their content in JavaScript (Workday, Greenhouse SPAs) come back as empty
    shells over plain HTTP; those are kept at low confidence instead of dropped,
    which is what used to make whole career sites invisible to the scan.
    """
    try:
        if html is None:
            code, html = fetch(url)
            if code >= 400:
                return None
    except Exception:
        return None

    low = html.lower()
    text = re.sub(r"<[^>]+>", " ", low)
    text = re.sub(r"\s+", " ", text)

    if any(
        x in low
        for x in [
            "job not found",
            "no longer available",
            "this job has been closed",
            "position is no longer",
            "posting has expired",
            "job posting is closed",
        ]
    ):
        return None

    # JS shell / blocked page: no usable text to judge. Keep, flag as unverified.
    if len(text) < 1200 or "intern" not in text:
        return {"ok": True, "confidence": "low", "evidence": "page-not-readable"}

    if not is_us(text[:20000]) and not re.search(r"multiple locations|various locations", text):
        return None

    if re.search(r"summer\s*20(2[0-6]|28|29)\b", text) and "2027" not in text:
        return None

    s27 = (
        "summer 2027" in text
        or "summer-2027" in low
        or bool(re.search(r"2027.{0,60}(intern|internship)", text))
        or bool(re.search(r"(intern|internship).{0,60}2027", text))
    )

    grad_only = bool(
        re.search(
            r"master'?s (degree )?students? only|requires a master|"
            r"must be (enrolled in|pursuing) a master|mba only|"
            r"phd students only|ph\.d\. only|doctoral candidates only",
            text,
        )
    ) and not UNDERGRAD_SIGNAL.search(text)
    if grad_only:
        return None

    ug = bool(UNDERGRAD_SIGNAL.search(text)) or "student" in text or "university" in text

    if s27 and ug:
        return {"ok": True, "confidence": "high", "evidence": "season+degree"}
    if s27 or ug:
        return {"ok": True, "confidence": "medium", "evidence": "season" if s27 else "degree"}
    return {"ok": True, "confidence": "low", "evidence": "title-only"}


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
    if score < min_fit:
        return None
    info = verify_posting(url, page_text or None)
    if not info:
        return None
    confidence = info.get("confidence", "high")
    note = f"Found via {source} on {today}. Re-verify before applying."
    if confidence != "high":
        note += f" Season/degree not confirmed from the page ({info.get('evidence')}) — check the listing."
    return {
        "id": f"{slug(company)}-{slug(role)[:40]}-s27",
        "company": company,
        "role_title": role if "2027" in role or "Summer" in role else f"{role} (Summer 2027)",
        "season": "Summer 2027",
        "listing_status": "open",
        "verified_at": today,
        "posting_url": url,
        "application_url": url,
        "tier": tier_for(score),
        "category": category_for(company, role),
        "degree_level": ["BS"],
        "location": loc if loc.startswith("United States") else f"United States ({loc})",
        "work_model": "Onsite",
        "application_status": "Not started",
        "notes": note,
        "fit_score": score,
        "verify_confidence": confidence,
        "source": source,
    }
