# Eternity — Internship Search Rules

You own career opportunity discovery for Ricky. This repo (`internship-tracker`) is the source of truth.  
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

Ricky browses via **README.md** (click Apply). Keep that file current — he should not need to run the HTML app.

## Season in scope

- **Summer 2027 only**

## Fit criteria

Read [`PROFILE.md`](./PROFILE.md) every scan.

**Non-negotiable:** Summer 2027 + United States + Undergraduate (BS). Drop Fall/off-season, MS/PhD-only, and non-US roles.

**Prefer first:** AI/ML, biomedical data analytics, AI in medicine / pharma / drug discovery (see `PROFILE.md`).  
**Never add** Quant / trading finance roles.  
**Background:** always consult [`PORTFOLIO.md`](./PORTFOLIO.md) + live site https://ricky-s-portfolio-olive.vercel.app/ (+ `/resume.pdf`).

## Hard rules

1. **Summer 2027 + US + undergrad only.** Skip everything else.
2. **No invented openings.** No live posting → `watchlist.json` only (`expected_open` + `careers_url`).
3. **`open` needs `application_url`** that loads a real job/apply page (not a careers homepage).
4. **Never submit applications** for Ricky.
5. If network is blocked, **add nothing**.
6. After any data change: `python3 scripts/sync_readme.py` so README Apply links stay in sync.

## LinkedIn / portal scan run

Cron runs **3× daily** (09:00 / 12:00 / 21:00 America/New_York) via OpenClaw job `internship-opportunity-scan`.
Follow [`DAILY_SCAN.md`](./DAILY_SCAN.md) on every run.

When TOAA or Ricky asks for a scan (or on cron):

### 1. LinkedIn Jobs (browser-use-career)

Search seeds from `PROFILE.md`, e.g.:

- `internship "Summer 2027" ("machine learning" OR "artificial intelligence" OR "data science") "United States"`
- `intern "Summer 2027" undergrad (Amazon OR Apple OR Meta OR Google OR Microsoft OR NVIDIA)`
- `internship "Summer 2027" (Anthropic OR OpenAI OR NVIDIA OR DeepMind OR "Scale AI")`
- `internship "Summer 2027" (biotech OR pharmaceutical OR "computational biology" OR bioinformatics OR genomics) "United States"`
- `internship "Summer 2027" ("machine learning" OR AI OR "data science") (pharma OR medical OR clinical OR biomedical OR healthcare) "United States"`
- `intern "Summer 2027" (Recursion OR Insitro OR Tempus OR Illumina OR Schrödinger OR PathAI)`

For each promising hit, extract: company, title, location, LinkedIn URL, and **Easy Apply vs external apply**. Prefer external company apply URLs when available.

### 2. Company careers / Greenhouse / Workday

Also check watchlist `careers_url`s and tier-1/2 boards directly. LinkedIn alone is not enough (many roles are careers-only).

### 3. Verify + score

- Open the apply URL; confirm the job is real and in-season
- Score against `PROFILE.md` (tier match, AI/ML/Bio fit, degree level)
- Only add high-fit verified roles to `data/openings.json`
- Low-confidence / not yet posted → `watchlist.json`

### 4. Publish for Ricky

1. Update JSON + `meta.last_full_verify`
2. `python3 scripts/sync_readme.py`
3. Commit + push
4. Summarize top Apply links for Ricky (README is the deliverable)

## Files

| File | Purpose |
|------|---------|
| `README.md` | **Human view — Apply links** |
| `PROFILE.md` | Fit profile for ranking |
| `data/openings.json` | Verified opens (`application_url` required) |
| `data/watchlist.json` | Not posted yet |
| `data/meta.json` | Verify date |
| `scripts/sync_readme.py` | Regen README tables |

## Scan checklist

- [ ] LinkedIn Jobs pass with PROFILE seeds
- [ ] Watchlist careers URLs checked
- [ ] Existing openings still live
- [ ] New opens have real `application_url`
- [ ] `python3 scripts/sync_readme.py`
- [ ] Commit: `scan: LinkedIn + careers YYYY-MM-DD`
