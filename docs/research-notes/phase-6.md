# Phase 6 — Interactive app

Completed 2026-09-09.

Six snapshot-backed routes, no live APIs.

```bash
python -m cf_atlas export-app
cd app
npm install
npm run dev
```

| Route | What a reader sees |
|---|---|
| `/` | Research question, data-as-of stamp, how to read FACT / ANALYSIS / HYPOTHESIS |
| `/landscape` | Solved vs remains from CFF 2024, residual counts that must not be added |
| `/pipeline` | 1,209 CF-tagged studies, NCFB heuristic, starts-by-year, NCT01851694 note |
| `/map` | Reviewed CF strategy × stage grid and asset list |
| `/opportunities` | Live 0–100 index under presets/sliders, seven theses with kill criteria |
| `/methodology` | Sources, classification rule, scoring formula, limitations, disclaimer |

The UI reads `app/src/data/snapshot.json`. Rebuild that file after `landscape`, `classify`, or `score`.

Stop condition: a reader can go from the question to the map to a thesis without opening a notebook. Integer scores on thesis cards display as `Opportunity Score: nn/100 · Evidence: …`.

Phase 7–8 adds `/opportunities/H1` … `H7` challenge memos. See [phase-7.md](phase-7.md).
