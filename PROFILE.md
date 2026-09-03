# Ricky — internship fit profile

Eternity / cron use this when ranking LinkedIn / careers / seed-list hits.

## Always read first

- **Portfolio:** https://ricky-s-portfolio-olive.vercel.app/  
- **Resume:** https://ricky-s-portfolio-olive.vercel.app/resume.pdf  
- **Local snapshot:** [`PORTFOLIO.md`](./PORTFOLIO.md) (refresh from live site if stale)

Ricky is a **Data Analytics (Biomedical & Public Health)** undergrad at OSU ’28 (AIMed Lab / PhysioNet, healthcare viz, medical imaging AI). Strong fit for **AI/ML**, **medical / pharma data analysis**, and **financial / investment analytics** — not prop-trading Quant.

## Hard requirements (always)

- **Summer 2027 only** — skip Fall 2026, Spring 2027, Winter, Rolling (unless the posting is explicitly Summer 2027)
- **United States only** — onsite/hybrid/remote must be US-based
- **Undergraduate (BS) only** — skip MS-only and PhD-only

## Strong yes (priority order)

### 1. AI / Machine Learning

- LLMs, NLP, RL, multimodal, computer vision, applied ML
- ML infra / GPU / inference / training platforms
- SWE with clear ML / data-for-ML flavor

### 2. Bio-AI / medicine / pharma / biomedical data

- AI in medicine / healthcare / clinical (imaging, clinical ML, digital health, EHR/NLP)
- Medical / clinical **data analysis** & real-world evidence analytics
- AI in pharma / drug discovery / R&D informatics
- Biomedical data analytics: bioinformatics, computational biology, genomics, biomarker analytics
- Roles matching PhysioNet, DataFest health, doctor-in-the-loop imaging

### 3. Financial / investment analytics (yes)

- **Financial analytics**, investment analytics, risk analytics, portfolio analytics
- Markets / wealth / asset-management **data science** or **data analytics** (not desk trading)
- Examples: JPMorgan Chase, Goldman Sachs, Morgan Stanley, BlackRock, Fidelity, Capital One (analytics/DS tracks)
- Prefer titles with: data analytics, data science, AI/ML, quantitative analytics *for business/risk/investments* when undergrad-eligible

### 4. Related SWE / data science (secondary)

- Strong SWE or general data-science internships at priority tech companies

## Search scope

**Search wide, list narrow.** Cron actively crawls **~270 companies** across:

1. **Big tech** — FAANG+, NVIDIA, Databricks, Snowflake, IBM, Oracle, …
2. **Consumer / media / apps** — Disney, Netflix, Uber, Spotify, Stripe, Salesforce, Roblox, …
3. **Pharma / bio / med-tech** — J&J, Lilly, Pfizer, Merck, Amgen, Moderna, Illumina, Recursion, …
4. **Finance analytics** — JPMorgan, Goldman, Morgan Stanley, BlackRock, Citi, …
5. **Fortune 500** — Tesla, Boeing, Lockheed, UnitedHealth, Walmart, Broadcom, Honeywell, …

LinkedIn runs parallel seed queries for the same buckets.  
**Listing** still filters hard: Summer 2027 · US · undergrad · verified apply link · fit score (AI/ML, bio/pharma data, finance analytics preferred; general SWE ok).

## Priority companies (fit ranking, not search limits)

1. **Big tech AI:** NVIDIA, Google / DeepMind, Microsoft, Amazon, Meta, Apple  
2. **Frontier AI labs:** OpenAI, Anthropic, Cohere, Mistral, Hugging Face, Scale AI, W&B  
3. **Bio-AI / biotech:** Recursion, Insitro, Schrödinger, Atomwise, Generate Biomedicines, Deep Genomics, Genesis Therapeutics, Isomorphic Labs, BenchSci, PathAI, Owkin, Tempus, Flatiron Health, Verily, Illumina, 10x Genomics  
4. **Pharma / medicine data + AI:** Pfizer, **Johnson & Johnson / Janssen**, **Eli Lilly**, Moderna, Genentech / Roche, Amgen, Gilead, Merck, Novartis, AbbVie, Biogen, Bristol Myers Squibb, IQVIA, Natera, Guardant Health  
5. **Finance analytics:** JPMorgan Chase, Goldman Sachs, Morgan Stanley, BlackRock, Fidelity, Bank of America, Citi (analytics / DS / AI tracks only)
6. **Consumer / big corp SWE:** Disney, Netflix, Uber, Spotify, Stripe, Salesforce, Adobe, Shopify, Roblox, …

## Hard no

- Invented / unverified postings
- Fall 2026 / off-season roles
- MS-only or PhD-only roles
- Non-US locations
- Auto-submitting applications
- Pure ops / audit / HR / marketing / industrial BA
- **Prop trading / market-making / “Quant Trading Intern”** at HRT, Citadel Securities, Optiver trading desks, etc. (different from bank financial analytics)

## LinkedIn / search seeds

See `scripts/search_targets.py` (`LINKEDIN_SEEDS`) — rotates across AI/ML, big tech, consumer, pharma, finance, and healthcare queries each cron run.

Examples:
- `internship "Summer 2027" ("machine learning" OR "artificial intelligence" OR "data science") "United States"`
- `internship "Summer 2027" ("data analytics" OR "financial analytics" OR "investment analytics") (JPMorgan OR "Goldman Sachs" OR "Morgan Stanley" OR BlackRock) "United States"`
- `internship "Summer 2027" ("data science" OR "machine learning" OR analytics) (Pfizer OR "Johnson & Johnson" OR "Eli Lilly" OR Merck OR Amgen) "United States"`
- `internship "Summer 2027" (biotech OR pharmaceutical OR "computational biology" OR bioinformatics OR genomics) "United States"`
- `internship "Summer 2027" ("machine learning" OR "data science" OR AI) (pharma OR medical OR clinical OR biomedical OR healthcare) "United States"`
- `intern "Summer 2027" (Disney OR Netflix OR Uber OR Spotify OR Stripe) software engineering "United States"`

Verify season = Summer 2027, location = US, degree = undergraduate before adding to `openings.json`.
