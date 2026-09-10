# Phase 7–8 — Challenge memos

Completed 2026-09-09.

Seven white-space memos. Each one has FACT / ANALYSIS / INTERPRETATION / HYPOTHESIS, a bull case, a bear case, counterarguments, remaining diligence, and kill criteria. No thesis is only a bull case.

```bash
python -m cf_atlas theses
python -m cf_atlas export-app
```

`score` also regenerates the memos.

| Artifact | Role |
|---|---|
| `data/external/thesis_challenges.json` | Curated long-form challenge fields |
| `data/external/opportunity_theses.csv` | Short cards (one-liner, would-have-to-be-true, kill criteria) |
| `docs/theses/` | Generated markdown memos |
| `/opportunities` | Ranked needs plus short cards |
| `/opportunities/H1` … `/opportunities/H7` | Full challenge memos |

Theses still inherit the parent need score. There is no second index.

N2 (eligible not prescribed) and N7 (aging) stay scored and in the investigation set. They are not default company-formation cards.

Stop condition: 5–7 white-space memos with counterarguments and kill criteria.
