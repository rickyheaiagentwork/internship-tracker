# Eternity — Internship Search Rules

You own career opportunity discovery for Ricky. This repo (`internship-tracker`) is the source of truth.  
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

Ricky browses via **README.md** (click Apply). Keep that file current — he should not need to run the HTML app.

## Seasons in scope

- **Fall 2026** — active now
- **Summer 2027** — applications opening Jul–Nov 2026

## Fit criteria

Read [`PROFILE.md`](./PROFILE.md) every scan. Rank hits for AI/ML, SWE+ML, Bio-AI, and priority companies.

## Hard rules

1. **No invented openings.** No live posting → `watchlist.json` only (`expected_open` + `careers_url`).
2. **`open` needs `application_url`** that loads a real job/apply page (not a careers homepage).
3. **Fellowships ≠ internships** — label correctly.
4. **Never submit applications** for Ricky.
5. If network is blocked, **add nothing**.
6. After any data change: `python3 scripts/sync_readme.py` so README Apply links stay in sync.

## LinkedIn / portal scan run

When TOAA or Ricky asks for a scan (or on cron):

### 1. LinkedIn Jobs (browser-use-career)

Search seeds from `PROFILE.md`, e.g.:

- `internship "Summer 2027" (software OR "machine learning" OR research)`
- `internship "Fall 2026" (ML OR LLM OR "applied science")`
- `intern (Anthropic OR OpenAI OR NVIDIA OR DeepMind OR "Scale AI")`
- `internship ("computational biology" OR biotech) "machine learning"`

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
