# Security

This repo is **public** on GitHub. Keep it that way — no secrets.

## Never commit

- API keys, tokens, passwords, `.env` files
- GitHub PATs, LinkedIn session cookies, SSH private keys
- `USER.local.md` (Telegram routing / private contact info)
- `memory/` agent session logs
- `bin/` local delegation scripts
- `.openclaw/` machine state

All of the above are listed in `.gitignore`.

## What is safe to publish

- `data/openings.json` — public job posting URLs only
- `README.md` — apply links
- `PROFILE.md` / `PORTFOLIO.md` — career fit (no school email; use live resume for contact)

## Git auth

Pushes use the host machine's git credential helper — **no tokens in this repo**. If a token is ever pasted into a file, rotate it immediately and remove it from git history.

## Reporting

If you find exposed credentials in an old commit, rotate the credential and open an issue or purge history with `git filter-repo`.
