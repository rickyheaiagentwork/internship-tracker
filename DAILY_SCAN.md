# Daily internship scan (Eternity / TOAA cron)

Repo root: this directory (`internship-tracker/`)  
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

## Autonomy

Cron runs are **Mode B / auto** — execute fully, then Telegram `[RESULT]`. No Ricky approval needed.

## Hard filters

1. **Summer 2027 only**
2. **United States only**
3. **Undergraduate (BS) only**
4. Never invent roles. Never auto-apply.

## Prefer (from PROFILE)

AI/ML, biomedical / pharma medical data, financial / investment analytics. Skip prop-trading Quant desks.

## Active search (no watchlist, no seed lists)

Cron command: `python3 scripts/active_scan.py --mode auto`

| ET | Mode |
|---|---|
| 09:00, 21:00 | Company career site crawl (4 companies per run, rotates) |
| 12:00 | LinkedIn Jobs (PROFILE seed, rotates) |

Manual runs:
```bash
cd "$(git rev-parse --show-toplevel)"
python3 scripts/active_scan.py --mode careers
python3 scripts/active_scan.py --mode linkedin
```

## Manual / ETERNITY-assisted run

1. `git pull`
2. Read `PROFILE.md`, `ETERNITY.md`, `data/openings.json`
3. Run active search (above) or use browser-use-career for deeper LinkedIn/portal passes
4. Verify each candidate: Summer 2027 + US + undergrad + real apply URL
5. `python3 scripts/sync_readme.py`
6. Commit + push only if data changed
7. Telegram summary with new Apply links

## If network fails

Add **nothing**. Report the failure.
