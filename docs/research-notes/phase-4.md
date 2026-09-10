# Phase 4 — Reviewed classification and competitive map

Completed 2026-09-09. Command: `python -m cf_atlas classify`.

Every row on the competitive map has `review_status=reviewed`, `disease_area=cf`, and `map_eligible=1`. Auto-suggested labels exist for the other 1,138 trials and must not be ranked.

## How the map was built

1. Keyword rules suggested a strategy and need ID for all 1,209 interventional CF-tagged studies.
2. The Phase 3 NCFB heuristic still flags 98 records, including the known false positive `NCT01851694`.
3. `data/external/trial_review_overrides.csv` reviewed 71 decision-critical trials (active industry CF, NCFB-flagged actives, key academic therapeutics, and that false positive).
4. `data/external/program_reviews.csv` reviewed all 57 CFF pipeline rows (active, discontinued, not-CF-primary, or preclinical listing only).
5. `map_assets.csv` is program-grain. Combination components (SION-109 / SION-2222) and earlier Vertex modulators do not each add a crowding unit.

## FACT / ANALYSIS counts

| Metric | Value |
|---|---|
| Trials classified | 1,209 |
| Reviewed trials | 71 |
| Auto-suggested only | 1,138 |
| Reviewed CF map-eligible trials | 40 |
| CFF programs reviewed | 57 |
| Map assets | 54 |
| Of those, investigational (`whitespace_relevant=1`) | 37 |
| `NCT01851694` disease area after override | cf |

## INTERPRETATION (not a ranking)

These are coverage observations from the reviewed map. They are not opportunity scores.

1. **N1 (mutation-agnostic restoration) is the crowded investigational column.** Industry whitespace crowding is high: gene therapy, mRNA, one splicing oligo, preclinical editing/delivery listings, plus ABCI as a CFTR-independent anion bypass. Discontinued historical programs (ataluren, eluforsen, MRT5005) are off the map.
2. **N2 next-generation modulators are a defined industry race, not an empty field.** Sionna (SION-719; SION-451 combination) and Vertex HV studies (VX-581, VX-272) sit on top of an approved HEMT franchise (Trikafta, Alyftrek). Pediatric OLEs of approved products are label expansion, not whitespace.
3. **N3 residual lung disease has almost no CF-specific industry drug in this reviewed set.** Brensocatib and verducatib were marked not-CF-primary. What remains map-visible is SoC mucolytics/hydrators plus two academic anti-inflammatories (anakinra, losartan).
4. **N4 infection is approved inhaled antibiotics plus a thin investigational layer.** Industry whitespace crowding is low: BiomX BX004. Academic phage and IV gallium are visible. AP-PA02 had no matching active CF-like trial in this snapshot.
5. **N5 CFRD is academic repurposing plus one device program.** Empagliflozin, dulaglutide, metformin, dorzagliatin, and verapamil are investigator-initiated. The bionic pancreas is the only crowding unit. There is no reviewed industry CF-specific metabolic drug on the map.
6. **N6 GI is PERT-class SoC plus two industry candidates (ANG003, NHS7108)** and academic constipation/motility repurposing. Adrulipase is marked discontinued.
7. **N7 aging has no therapeutic map asset.** Reviewed rows are supportive (bone, fertility). That is a coverage fact, not a thesis.
8. **N8 care delivery is busy in ClinicalTrials.gov and absent from the therapeutic map.** 17 auto-suggested active CF-like studies; none are map-eligible products. Do not force a drug score onto a services problem.

## What was excluded on purpose

- NCFB programs (ensifentrine, HSK31858, CSL787, SIMEOX, and the rest of the flagged active set)
- `NCT01851694` is CF/CFRD physiology, not a product, and not on the map
- CFF listings with past-tense descriptions and no matching active CF trial (Carbon, Carmine, Pioneering, ReCode/Intellia editing collab, SalioGen)
- Complementary Sionna molecules counted once

## Outputs

- `data/processed/classification/*.csv`
- `assets/figures/competitive_map_strategy_stage.png`
- `assets/figures/need_pipeline_coverage.png`

Phase 5 may score opportunities using only reviewed map-eligible rows. Do not score auto-suggested yoga, imaging, or NCFB studies.
