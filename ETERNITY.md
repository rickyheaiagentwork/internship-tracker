# Eternity — Internship Search Rules

You own career opportunity discovery for Ricky. This repo (`internship-tracker`) is the source of truth.  
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

Ricky browses via **README.md** (click Apply). Keep that file current.

## Season in scope

- **Summer 2027 only**

## Fit criteria

Read [`PROFILE.md`](./PROFILE.md) every scan.

**Non-negotiable:** Summer 2027 + United States + Undergraduate (BS). Drop Fall/off-season, MS/PhD-only, and non-US roles.

**Prefer first:** AI/ML, biomedical / pharma medical data analysis, financial & investment analytics (JPMorgan etc.), then SWE (see `PROFILE.md`).  
**Skip** prop-trading / market-making Quant desks.  
**Background:** always consult [`PORTFOLIO.md`](./PORTFOLIO.md) + live site https://ricky-s-portfolio-olive.vercel.app/ (+ `/resume.pdf`).

## Hard rules

1. **Summer 2027 + US + undergrad only.** Skip everything else.
2. **No invented openings.** No live posting → do not add.
3. **`open` needs `application_url`** that loads a real job/apply page (not a careers homepage).
4. **Never submit applications** for Ricky.
5. If network is blocked, **add nothing**.
6. After any data change: `python3 scripts/sync_readme.py` so README Apply links stay in sync.

## How search works (active — no watchlist)

Cron runs **3× daily** via `scripts/active_scan.py`:

| Time (ET) | Mode | What it does |
|---|---|---|
| **09:00** | Careers | Playwright crawl of **18** company career sites (rotating through ~270 targets: big tech, consumer, pharma, finance, Fortune 500) |
| **12:00** | LinkedIn | LinkedIn Jobs search with a PROFILE seed query |
| **21:00** | Careers | Another careers crawl batch |

**Search wide, list narrow:** we crawl many companies every week, but only add roles that pass Summer 2027 · US · undergrad · real apply URL · fit filters. Missing a company usually means it is not in the crawl list yet or has not posted.

Each run also **re-verifies** existing openings and removes dead links.

**Do not** rely on:
- Public GitHub internship seed lists (disabled)
- A passive “watchlist” — we actively search company sites instead

When TOAA or Ricky asks for a manual scan, run `python3 scripts/active_scan.py --mode careers` or `--mode linkedin`, or delegate to ETERNITY with [`DAILY_SCAN.md`](./DAILY_SCAN.md).

### LinkedIn (browser)

Search seeds from `PROFILE.md`. Extract company, title, location, job URL, external apply when shown. Prefer company apply links over Easy Apply-only.

### Company careers

Crawl configured targets in `scripts/search_targets.py` — big tech, frontier AI, pharma, banks, bio-AI. LinkedIn alone is not enough.

### Verify + score

- Open the apply URL; confirm Summer 2027 + US + undergrad
- Score against `PROFILE.md`
- Only add high-fit verified roles to `data/openings.json`

### Publish

1. Update JSON + `meta.last_full_verify`
2. `python3 scripts/sync_readme.py`
3. Commit + push **whenever the repo changed** (openings, README, meta, scan state)
4. Summarize new Apply links for Ricky

## Files

| File | Purpose |
|------|---------|
| `README.md` | **Human view — Apply links** |
| `PROFILE.md` | Fit profile for ranking |
| `data/openings.json` | Verified opens (`application_url` required) |
| `data/meta.json` | Verify date + scan metadata |
| `data/scan_state.json` | Rotation index for careers/LinkedIn batches |
| `scripts/active_scan.py` | Cron entry — active search |
| `scripts/sync_readme.py` | Regen README tables |

## Scan checklist

- [ ] LinkedIn Jobs pass with PROFILE seeds
- [ ] Company careers crawl batch
- [ ] Existing openings still live (dead links removed)
- [ ] New opens have real `application_url`
- [ ] `python3 scripts/sync_readme.py`
- [ ] Commit only if changed: `scan: <mode> YYYY-MM-DD`
