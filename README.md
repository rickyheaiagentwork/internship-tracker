# Internship Tracker

Verified Fall 2026 + Summer 2027 tracker for **Ricky He**.

**Rule:** live postings only in `data/openings.json`. Companies without a real posting go in `data/watchlist.json` — never invent roles (no fake Anthropic Summer 2027 intern, etc.).

## Quick start

```bash
python3 -m http.server 8765
# open http://localhost:8765
```

Each **Open** card has an **Apply** button that goes to the real application/job URL.

## Data

| File | Meaning |
|------|---------|
| [`data/openings.json`](./data/openings.json) | Verified open — includes `application_url` |
| [`data/watchlist.json`](./data/watchlist.json) | Priority targets not posted yet |
| [`data/meta.json`](./data/meta.json) | Last verify date + scan rules |
| [`ETERNITY.md`](./ETERNITY.md) | Agent scan rules |

## Snapshot (verified 2026-08-02)

- **19 open** with real apply links (Amazon, Apple, NVIDIA Fall, Scale AI, Anthropic Fellows, Figure, Databricks PM, …)
- **13 watch** (Anthropic intern, OpenAI, Google, Meta, Microsoft Summer 2027, Bio-AI, …)

## Eternity scans

1. Re-check every `application_url` still loads a real job page  
2. Promote watch → open only after verification  
3. Never fabricate deadlines or role titles  
4. Ricky submits applications manually  
