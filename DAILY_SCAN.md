# Daily internship scan (Eternity / TOAA cron)

Repo: `/home/jarvis/.openclaw/workspace/toaa/internship-tracker`  
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

## Autonomy

This runbook is an **authorized standing order**. Cron runs are **Mode B / auto:** — do **not** wait for Ricky to reply `approve`. Execute fully, then Telegram `[RESULT]`.

## Hard filters

1. **Summer 2027 only**
2. **United States only** (reject Canada/UK/EU/China/etc.)
3. **Undergraduate (BS) only** — skip MS-only / PhD-only
4. Never invent roles. Never auto-apply.

## Prefer (from PROFILE)

Prioritize **AI/ML**, **biomedical data analytics**, and **AI in medicine / pharma / drug discovery**.  
**Skip Quant / trading finance.**  
Read [`PORTFOLIO.md`](./PORTFOLIO.md) and fetch https://ricky-s-portfolio-olive.vercel.app/ (+ resume.pdf) when judging fit.

## Steps every run

1. `cd /home/jarvis/.openclaw/workspace/toaa/internship-tracker && git pull`
2. Read `PROFILE.md`, `ETERNITY.md`, `data/openings.json`, `data/watchlist.json`
3. Run seed helper: `python3 scripts/scan_seed_sources.py`
4. Also search LinkedIn Jobs / company careers / Greenhouse for PROFILE seeds
5. For each candidate: open apply URL; confirm Summer 2027 + US + undergrad
6. Append verified entries to `data/openings.json` with `application_url`, `verified_at=today`, `degree_level=["BS"]`, `location` starting with `United States`
7. Promote watchlist → open when a real US undergrad Summer 2027 posting appears
8. `python3 scripts/sync_readme.py`
9. Commit + `git push origin main`
10. Telegram summary: N new companies/roles + Apply links (from README)

## If network fails

Add **nothing**. Report the failure. Do not fabricate openings.
