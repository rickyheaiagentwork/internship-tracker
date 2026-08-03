#!/usr/bin/env python3
"""Deterministic daily internship scan for OpenClaw cron.

No LLM required. Finds Summer 2027 US undergrad openings from seed lists,
verifies apply URLs, updates openings.json + README, commits, and prints a
Telegram-ready summary.
"""
from __future__ import annotations

import json
import re
import subprocess
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OPENINGS = DATA / "openings.json"
WATCH = DATA / "watchlist.json"
META = DATA / "meta.json"

SOURCES = [
    "https://raw.githubusercontent.com/sndsh404/summer-2027-internships/main/README.md",
    "https://raw.githubusercontent.com/speedyapply/2027-SWE-College-Jobs/main/README.md",
]

ROW_RE = re.compile(
    r"^\|([^|]+)\|([^|]+)\|([^|]+)\|.*\[(?:apply|Apply)\]\((https?://[^)]+)\)",
    re.I,
)

UA = "Mozilla/5.0 internship-cron-scan/1.0"
TODAY = date.today().isoformat()
MAX_NEW = 15
MAX_CHECK = 50

# Role / company keywords that match Ricky's PROFILE (AI/ML + bio/med/pharma)
BIO_AI_KW = re.compile(
    r"\b("
    r"bio[- ]?ai|computational biology|bioinformatics|biomedical|biotech|"
    r"genomic|genomics|multi[- ]?omics|proteomics|transcriptomics|"
    r"drug discovery|cheminformatics|computational chem|"
    r"pharma|pharmaceutical|medicine|medical imaging|clinical (ml|ai|data)|"
    r"healthcare|health ?tech|digital health|ehr|real[- ]world evidence|"
    r"biomarker|oncology|pathology ai|therapeutic"
    r")\b",
    re.I,
)
AI_ML_KW = re.compile(
    r"\b("
    r"machine learning|artificial intelligence|\bai\b|\bml\b|"
    r"deep learning|llm|nlp|computer vision|data science|"
    r"data analytics|applied scientist|research scientist|"
    r"model (training|inference)|gpu|interpretability"
    r")\b",
    re.I,
)
BIO_COMPANIES = re.compile(
    r"\b("
    r"recursion|insitro|schr.?dinger|atomwise|generate|deep genomics|"
    r"genesis|isomorphic|benchsci|pathai|owkin|tempus|flatiron|"
    r"verily|illumina|10x|moderna|genentech|roche|amgen|gilead|"
    r"pfizer|merck|novartis|abbvie|biogen|bristol|iqvia|natera|"
    r"guardant|bionemo|nvidia"
    r")\b",
    re.I,
)


def fetch(url: str, timeout: int = 25) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace")


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:48]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def save_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n")


def existing_urls(opens: list[dict]) -> set[str]:
    urls: set[str] = set()
    for o in opens:
        for k in ("application_url", "posting_url"):
            if o.get(k):
                urls.add(o[k].rstrip("/"))
    return urls


def looks_candidate(company: str, role: str, loc: str, line: str) -> bool:
    blob = f"{company} {role} {loc} {line}".lower()
    if "intern" not in blob and "internship" not in blob:
        return False
    if "2027" not in blob and "summer 2027" not in blob:
        return False
    # skip obvious off-season / non-US
    if any(x in blob for x in ["fall 2026", "spring 2027", "winter 2027"]) and "summer 2027" not in blob:
        return False
    if any(
        x in blob
        for x in [
            "ireland",
            "dublin",
            "india",
            "bengaluru",
            "hyderabad",
            "london",
            "toronto",
            "canada",
            "uk,",
            "shanghai",
            "remote - europe",
        ]
    ):
        return False
    # undergrad only — reject master's/PhD-titled roles in the seed table
    if re.search(r"master'?s|mba|ph\.?d|graduate student only", blob) and not re.search(
        r"bachelor|undergrad|\bbs\b", blob
    ):
        return False
    # off-profile junk (ops / audit / industrial BA — not SWE/ML)
    if re.search(
        r"\b(operations management|it audit|audit intern|business analyst|"
        r"gas compressor|accounting|finance rotational|hr intern|marketing intern)\b",
        blob,
    ):
        return False
    # no Quant / trading finance track (Ricky is Bio-AI / data analytics, not trading)
    if re.search(
        r"\b(quant trading|quantitative (intern|analyst|research|researcher|developer)|"
        r"market making|prop trading)\b",
        blob,
    ):
        return False
    return True


def fit_score(company: str, role: str, loc: str = "") -> int:
    """Higher = check / add first. Matches PROFILE priority."""
    blob = f"{company} {role} {loc}"
    score = 0
    if BIO_AI_KW.search(blob) or BIO_COMPANIES.search(company):
        score += 100
    if AI_ML_KW.search(blob):
        score += 80
    if re.search(r"software|swe|engineer|developer|full[- ]?stack", blob, re.I):
        score += 20
    if re.search(r"\bquant|trading|market making\b", blob, re.I) and not AI_ML_KW.search(blob):
        score -= 100  # hard deprioritize; looks_candidate should already reject pure quant
    if BIO_AI_KW.search(blob) and AI_ML_KW.search(blob):
        score += 40  # AI + bio/med combo = best fit
    return score


def verify(url: str) -> dict[str, Any] | None:
    try:
        code, html = fetch(url)
    except Exception as e:
        return None
    if code >= 400:
        return None
    low = html.lower()
    if any(
        x in low
        for x in [
            "job not found",
            "no longer available",
            "this job has been closed",
            "position is no longer",
            "page not found",
        ]
    ):
        # avoid false positives on nav chrome containing "404"
        title = re.search(r"<title>([^<]+)", html, re.I)
        t = (title.group(1) if title else "").lower()
        if "not found" in t or "404" in t or "no longer" in low[:2000]:
            return None

    if "ireland" in low and "dublin" in low and "united states" not in low:
        return None
    if any(x in low for x in ["bengaluru", "hyderabad, india", "amazon development centre ireland"]):
        return None

    s27 = ("summer 2027" in low) or ("summer-2027" in low) or bool(
        re.search(r"2027.{0,40}(intern|internship)", low)
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
            " currently pursuing a degree",
        ]
    )
    # many SWE intern pages say "student" without bachelor — accept if not phd/masters-only
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
            "remote - usa",
            "remote, usa",
        ]
    )
    if not usa:
        return None

    return {"ok": True, "ug": ug, "s27": s27, "usa": usa}


def gather_seeds() -> list[tuple[str, str, str, str]]:
    out: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for src in SOURCES:
        try:
            _, text = fetch(src, timeout=40)
        except Exception as e:
            print(f"# seed fail {src}: {e}")
            continue
        for line in text.splitlines():
            m = ROW_RE.search(line)
            if not m:
                continue
            company, role, loc, url = [x.strip() for x in m.groups()]
            if not looks_candidate(company, role, loc, line):
                continue
            key = url.rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            out.append((company, role, loc, url))
    # PROFILE priority: Bio-AI / AI-ML first, then SWE, trading last
    out.sort(key=lambda t: fit_score(t[0], t[1], t[2]), reverse=True)
    return out


def category_for(company: str, role: str) -> str:
    blob = f"{company} {role}"
    r = role.lower()
    if BIO_AI_KW.search(blob) or (
        BIO_COMPANIES.search(company) and AI_ML_KW.search(blob)
    ):
        return "Bio-AI"
    if any(
        x in r
        for x in [
            "machine learning",
            "artificial intelligence",
            "data science",
            "data analytics",
            "llm",
            "interpretability",
            "deep learning",
            "computer vision",
        ]
    ) or re.search(r"\b(ai|ml)\b", r):
        return "AI/ML"
    if "product" in r and "engineer" not in r and "software" not in r:
        return "PM"
    return "SWE"


def git_commit_push(msg: str) -> None:
    subprocess.run(["git", "add", "-A"], cwd=ROOT, check=False)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    if not st.stdout.strip():
        print("# no git changes")
        return
    # use existing identity from last commit
    an = subprocess.check_output(["git", "log", "-1", "--format=%an"], cwd=ROOT, text=True).strip()
    ae = subprocess.check_output(["git", "log", "-1", "--format=%ae"], cwd=ROOT, text=True).strip()
    import os

    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": an,
            "GIT_AUTHOR_EMAIL": ae,
            "GIT_COMMITTER_NAME": an,
            "GIT_COMMITTER_EMAIL": ae,
        }
    )
    subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, env=env, check=False)
    subprocess.run(["git", "push", "origin", "main"], cwd=ROOT, check=False)


def main() -> int:
    print(f"# internship cron scan {TODAY}")
    opens: list[dict] = load_json(OPENINGS, [])
    known = existing_urls(opens)
    seeds = gather_seeds()
    print(f"# seeds={len(seeds)} known_opens={len(opens)}")

    added: list[dict] = []
    checked = 0
    for company, role, loc, url in seeds:
        if len(added) >= MAX_NEW or checked >= MAX_CHECK:
            break
        if url.rstrip("/") in known:
            continue
        checked += 1
        info = verify(url)
        if not info:
            print(f"# skip {company}: verify failed | {url}")
            continue
        entry = {
            "id": f"{slug(company)}-{slug(role)[:40]}-s27",
            "company": company,
            "role_title": role if "2027" in role or "Summer" in role else f"{role} (Summer 2027)",
            "season": "Summer 2027",
            "listing_status": "open",
            "verified_at": TODAY,
            "posting_url": url,
            "application_url": url,
            "tier": 1 if fit_score(company, role) >= 100 else 2,
            "category": category_for(company, role),
            "degree_level": ["BS"],
            "location": loc if loc.lower().startswith("united states") or "US" in loc or any(x in loc for x in ["CA", "NY", "IL", "WA", "TX", "MA", "CO", "FL", "VA", "NH"]) else f"United States ({loc})",
            "work_model": "Onsite",
            "application_status": "Not started",
            "notes": f"Auto-added by cron_scan.py on {TODAY}. Re-verify before applying.",
            "fit_score": fit_score(company, role),
        }
        # de-dupe ids
        ids = {o["id"] for o in opens}
        base = entry["id"]
        n = 2
        while entry["id"] in ids:
            entry["id"] = f"{base}-{n}"
            n += 1
        opens.append(entry)
        known.add(url.rstrip("/"))
        added.append(entry)
        print(f"# ADD {company} | {role} | {url}")

    save_json(OPENINGS, opens)
    meta = load_json(META, {})
    meta["last_full_verify"] = TODAY
    meta["last_cron_scan"] = TODAY
    meta["last_cron_added"] = len(added)
    save_json(META, meta)

    subprocess.run(["python3", str(ROOT / "scripts" / "sync_readme.py")], cwd=ROOT, check=False)
    git_commit_push(f"scan: cron {TODAY} (+{len(added)} openings)")

    # Telegram-ready summary (stdout captured by cron delivery)
    print()
    print(f"[RESULT] Internship scan {TODAY}")
    print(f"Checked {checked} candidates from seed lists. Added {len(added)} new Summer 2027 US undergrad openings.")
    print(f"Tracker now has {len(opens)} open roles.")
    if added:
        print("New Apply links:")
        for a in added:
            print(f"- {a['company']}: {a['role_title']}")
            print(f"  {a['application_url']}")
    else:
        print("No new verified openings this run (filters: Summer 2027 · US · undergrad).")
    print(f"README: https://github.com/rickyheaiagentwork/internship-tracker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
