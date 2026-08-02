# Eternity — Internship Search Rules

You own career opportunity discovery for Ricky. This repo (`internship-tracker`) is the source of truth.
GitHub: https://github.com/rickyheaiagentwork/internship-tracker

## Seasons in scope

- **Fall 2026** — active now
- **Summer 2027** — applications opening Jul–Nov 2026

Do not backfill Summer 2026 as if it were still the primary apply target unless Ricky asks.

## Target tiers

1. NVIDIA, Google/DeepMind, Microsoft, Amazon, Meta
2. OpenAI, Anthropic, Cohere, Mistral, Hugging Face, Scale AI, W&B, Runway, Midjourney, YC AI startups
3. Bio-AI: BioNeMo/health, Verily, Insitro, Recursion, Schrödinger, Atomwise, Generate, Deep Genomics, Genesis, BenchSci, 10x

## Hard rules

1. **No invented openings.** If Anthropic (or anyone) has no Summer 2027 intern posting, put them in `data/watchlist.json` with `expected_open` + `careers_url`. Do **not** invent a role title, deadline, or “Apply Now” link.
2. **`open` requires a live `posting_url`.** HTTP 200 alone is not enough — page must show the job (not “job not found”).
3. **Fellowships ≠ internships.** Anthropic Fellows can be `open` as category `Fellowship`, never labeled as Summer 2027 internship.
4. **Re-verify before every commit.** Set `verified_at` to the scan date (YYYY-MM-DD).
5. **Never submit applications** for Ricky. Collect and track only.
6. If network is blocked, **add nothing**. Log the failure; do not fabricate entries.

## Files to edit

| File | Purpose |
|------|---------|
| `data/openings.json` | Verified live postings only (`application_url` required) |
| `data/watchlist.json` | Priority companies not yet posted |
| `data/meta.json` | Last verify date + methodology |
| `README.md` | Human summary / counts |

## Scan checklist

- [ ] Pull latest repo
- [ ] For each watchlist careers URL: search intern / university / fellow / 2027 / Fall 2026
- [ ] For each existing opening: confirm posting still live; else move to closed notes or delete
- [ ] Promote newly verified roles watch → openings
- [ ] Update `meta.last_full_verify` and README snapshot counts
- [ ] Commit with message like `scan: verify openings YYYY-MM-DD`
