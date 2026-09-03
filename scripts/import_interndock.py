#!/usr/bin/env python3
"""Import Summer 2027 roles from Intern Dock directory that match PROFILE."""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fit_filters import (  # noqa: E402
    TRADING_SHOP,
    category_for,
    dedupe_openings,
    fit_score,
    looks_candidate,
    role_fingerprint,
    slug,
)

TODAY = date.today().isoformat()
UA = "Mozilla/5.0 internship-interndock-import/1.0"
KEEP_SECTIONS = {
    "software engineering",
    "data science / analytics / ai",
    "product management",
    "finance / investment banking",
}
NON_US = re.compile(
    r"\b(canada|ontario|quebec|british columbia|manitoba|alberta|toronto|"
    r"london|united kingdom|england|ireland|india|pune|bengaluru|hyderabad|"
    r"singapore|hong kong|mexico|china|taiwan|japan|australia|germany|"
    r"france|emea|apac)\b",
    re.I,
)
US_HINT = re.compile(
    r"\b(united states|usa|u\.s\.|california|new york|texas|washington|"
    r"massachusetts|illinois|colorado|florida|georgia|virginia|arizona|"
    r"minnesota|ohio|michigan|north carolina|pennsylvania|oregon|"
    r"remote)\b",
    re.I,
)
SKIP_TITLE = re.compile(
    r"\b("
    r"phd|ph\.d|master'?s intern|mba intern|mba -|mba,|"
    r"accounting|audit|tax intern|underwriting|actuarial|"
    r"marketing intern|sales intern|hr intern|human resources|"
    r"mechanical|electrical engineer intern|civil engineer|"
    r"construction|field engineer|reservoir|avionics software internship - graduate|"
    r"hardware asic|mixed signal|vlsi|antenna|"
    r"investment banking|sales and trading|markets sales|"
    r"trading intern|quant trading|quantitative trader|"
    r"cyber security intern|information security|"
    r"finance intern|finance rotation|undergraduate finance|"
    r"product innovation intern - credit"
    r")\b",
    re.I,
)
KEEP_TITLE = re.compile(
    r"\b("
    r"software (engineer|engineering|developer)|swe|"
    r"machine learning|artificial intelligence|\bai\b|\bml\b|"
    r"data science|data scientist|data analytics|data engineer|"
    r"deep learning|computer vision|applied scientist|"
    r"quantitative (research|developer|analyst)|"
    r"investment research|equity research|"
    r"product manager|product management|"
    r"bioinformatics|computational biology|genomics"
    r")\b",
    re.I,
)
PRIORITY_CO = re.compile(
    r"\b("
    r"google|apple|microsoft|amazon|meta|nvidia|adobe|salesforce|"
    r"databricks|datadog|roblox|tiktok|stripe|netflix|disney|"
    r"uber|airbnb|spotify|snap|pinterest|intuit|oracle|ibm|"
    r"capital one|american express|jpmorgan|goldman|morgan stanley|"
    r"blackrock|citi|bank of america|mastercard|visa|fidelity|"
    r"pfizer|lilly|johnson|amgen|merck|genentech|moderna|"
    r"booz allen|blue origin|spacex|tesla|amd|"
    r"3m|corning|caterpillar|ge |gevernova|home depot|"
    r"c3 ai|bytedance|waymo|anduril|appian"
    r")\b",
    re.I,
)


def parse_directory(path: Path) -> list[dict]:
    lines = path.read_text(errors="replace").splitlines()
    section = ""
    company = ""
    out: list[dict] = []
    role_re = re.compile(r"^- (.+?) — \[Apply\]\((https?://[^)]+)\)(?: — (.+))?$")
    for line in lines:
        if line.startswith("## "):
            section = re.sub(r"\s*\(.*\)\s*$", "", line[3:]).strip().lower()
            company = ""
            continue
        if line.startswith("### "):
            company = line[4:].strip()
            continue
        if not any(section.startswith(s) for s in KEEP_SECTIONS):
            continue
        m = role_re.match(line.strip())
        if not m or not company:
            continue
        title, url, loc = m.group(1).strip(), m.group(2).strip(), (m.group(3) or "").strip()
        loc = re.sub(r"\s*Just posted\s*$", "", loc).strip()
        out.append({"company": company, "title": title, "url": url, "loc": loc, "section": section})
    return out


def is_fit(row: dict) -> bool:
    company, title, loc = row["company"], row["title"], row["loc"]
    blob = f"{company} {title} {loc}"
    if SKIP_TITLE.search(blob):
        return False
    if TRADING_SHOP.search(blob):
        return False
    if loc and NON_US.search(loc) and not US_HINT.search(loc):
        return False
    if loc and NON_US.search(loc) and not re.search(r"united states|usa", loc, re.I):
        # Canada / UK / India with no US mention
        if re.search(r"canada|ontario|united kingdom|india|pune|london", loc, re.I):
            return False
    if row["section"].startswith("finance"):
        if not re.search(
            r"data|analytics|technology|software|machine learning|ai\b|quant|"
            r"research|investment research|equity",
            title,
            re.I,
        ):
            return False
        if re.search(r"investment banking|ibd|private wealth|underwriting", title, re.I):
            return False
    if row["section"].startswith("product"):
        if not PRIORITY_CO.search(company) and "databricks" not in company.lower():
            return False
    if not KEEP_TITLE.search(title) and not PRIORITY_CO.search(company):
        return False
    if not looks_candidate(company, title, loc):
        return False
    if fit_score(company, title, loc) < 20 and not KEEP_TITLE.search(title):
        return False
    return True


def url_ok(url: str, timeout: int = 18) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.status >= 400:
                return False
            snippet = r.read(4000).decode("utf-8", "replace").lower()
    except urllib.error.HTTPError as e:
        return e.code < 400
    except Exception:
        return False
    if any(x in snippet for x in ["job not found", "page not found", "this job has been closed"]):
        return False
    return True


def existing_keys(opens: list[dict]) -> tuple[set[str], set[str]]:
    urls = set()
    fps = set()
    for o in opens:
        for k in ("application_url", "posting_url"):
            if o.get(k):
                urls.add(o[k].rstrip("/").lower())
        fps.add(role_fingerprint(o["company"], o["role_title"]))
    return urls, fps


def main() -> None:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/home/jarvis/.cursor/projects/home-jarvis/uploads/summer-2027-internships-complete-directory-0.md"
    )
    openings_path = ROOT / "data" / "openings.json"
    opens = json.loads(openings_path.read_text())
    urls, fps = existing_keys(opens)

    parsed = parse_directory(src)
    candidates = [r for r in parsed if is_fit(r)]
    # unique by url
    seen_u: set[str] = set()
    uniq: list[dict] = []
    for r in candidates:
        u = r["url"].rstrip("/").lower()
        if u in seen_u or u in urls:
            continue
        fp = role_fingerprint(r["company"], r["title"])
        if fp in fps:
            continue
        seen_u.add(u)
        uniq.append(r)
    print(f"parsed={len(parsed)} fit={len(candidates)} new={len(uniq)}")

    added: list[dict] = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        futs = {ex.submit(url_ok, r["url"]): r for r in uniq}
        for fut in as_completed(futs):
            r = futs[fut]
            ok = False
            try:
                ok = fut.result()
            except Exception:
                ok = False
            if not ok:
                continue
            loc = r["loc"] or "United States"
            if not loc.lower().startswith("united states") and "united states" not in loc.lower():
                loc = f"United States ({loc})" if loc else "United States"
            score = fit_score(r["company"], r["title"], r["loc"])
            entry = {
                "id": f"{slug(r['company'])}-{slug(r['title'])[:40]}-s27",
                "company": r["company"],
                "role_title": r["title"] if "2027" in r["title"] or "Summer" in r["title"] else f"{r['title']} (Summer 2027)",
                "season": "Summer 2027",
                "listing_status": "open",
                "verified_at": TODAY,
                "posting_url": r["url"],
                "application_url": r["url"],
                "tier": 1 if score >= 100 else 2,
                "category": category_for(r["company"], r["title"]),
                "degree_level": ["BS"],
                "location": loc,
                "work_model": "Onsite",
                "application_status": "Not started",
                "notes": f"Found via Intern Dock directory on {TODAY}. Re-verify before applying.",
                "fit_score": score,
                "source": "interndock",
            }
            n = 2
            base = entry["id"]
            ids = {o["id"] for o in opens} | {a["id"] for a in added}
            while entry["id"] in ids:
                entry["id"] = f"{base}-{n}"
                n += 1
            added.append(entry)
            fps.add(role_fingerprint(entry["company"], entry["role_title"]))
            print(f"+ {entry['company']}: {entry['role_title'][:70]}")

    opens.extend(added)
    opens = dedupe_openings(opens)
    opens.sort(key=lambda x: (x.get("tier", 9), x["company"].lower(), x["role_title"].lower()))
    openings_path.write_text(json.dumps(opens, indent=2) + "\n")
    print(f"added={len(added)} total={len(opens)}")


if __name__ == "__main__":
    main()
