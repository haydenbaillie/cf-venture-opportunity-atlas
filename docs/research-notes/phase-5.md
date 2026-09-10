# Phase 5 — Opportunity scores

Completed 2026-09-09. Command: `python -m cf_atlas score`.

This is an **exploratory prioritization index**, not a reason to fund a company. Display format: `Opportunity Score: 77/100 · Evidence: Moderate`. Evidence confidence is never averaged into the number.

## Formula

Score = 20 × Σ (wᵢ × sᵢ) with sᵢ on a 1–5 rubric. Default weights: need 25%, gap 20%, whitespace 20%, tractability 15%, economic 10%, why-now 10%.

Whitespace uses Phase 4 reviewed coverage only. Auto-suggested yoga, imaging, and NCFB studies are not in the index.

## Default ranking

| Rank | Need | Score | Evidence | Industry investigational crowding |
|---|---|---|---|---|
| 1 | N5 CFRD / metabolic | 77 | Moderate | none (0) |
| 2 | N1 mutation-agnostic restoration | 72 | High | high (13) |
| 3 | N4 chronic infection | 66 | Moderate | low (1) |
| 4 (tie) | N3 residual lung disease | 62 | Moderate | none CF-specific; adjacent NCFB DPP1 |
| 4 (tie) | N8 care delivery | 62 | Moderate | no product map; 17 unreviewed behavioral studies |
| 6 | N7 aging | 61 | Moderate | none |
| 7 | N6 GI / CFLD | 60 | Moderate | moderate (2) |
| 8 | N2 eligible not prescribed | 46 | Moderate | moderate next-gen modulator race |

N5 outranks N1 because N1 is crowded, not because CFRD is a larger causal gap. N1 still has the cleanest remaining CFTR-function hole (treatment-gap 5/5) and High evidence.

## Rank stability

The default top three — **N5, N1, N4** — keep that membership under all four weight presets and under ±10 percentage-point shifts of each default weight (16 scenarios). Order inside the top three moves:

- Patient-impact preset: N1 (79) above N5 (74)
- Commercial preset and +10pp whitespace: N5, then N4, then N1
- N2 stays last in every preset (44–48)

N3 whitespace is scored 3, not 5, because late-stage NCFB DPP1 programs are adjacent crowding.

## Seven theses (HYPOTHESIS, with kill criteria)

These inherit the parent need score. They are not a second index.

| ID | Stance | Thesis |
|---|---|---|
| H1 | pursue diligence | CF-specific metabolic therapy beyond insulin (N5, 77) |
| H2 | pursue diligence | CFTR-independent anion transport / ABCI-class (N1, 72) |
| H3 | pursue diligence | Persistent PA/NTM beyond inhaled-antibiotic SoC (N4, 66) |
| H4 | watch adjacent | Residual inflammation on HEMT vs NCFB DPP1 (N3, 62) |
| H5 | pursue diligence | Disease-modifying CFLD, not another PERT (N6, 60) |
| H6 | services, not a drug | Adult-era treatment burden (N8, 62) |
| H7 | watch incumbents | Nucleic-acid CFTR restoration is causal and crowded (N1, 72) |

N2 and N7 are scored and kept in the investigation set. They are not default company-formation cards: N2 is an incumbent modulator race plus a mixed 623-person group; N7 is a demographic fact without a single CF-specific target.

## Outputs

- `data/processed/scoring/*.csv`
- `assets/figures/need_opportunity_scores.png`
- `assets/figures/score_preset_comparison.png`

Phase 6 is the six-route Next.js app in `app/`. Integer scores on thesis cards belong there; the numbers above are already the Phase 5 source of truth.

Phase 7–8 expands each thesis into a challenge memo. See [phase-7.md](phase-7.md).
