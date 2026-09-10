# Classification (Phase 4)

Automated keyword labels are **suggestions**. The competitive map and any later ranking may use only rows that are:

1. `review_status = reviewed`
2. `disease_area = cf`
3. `map_eligible = 1`

Unreviewed rows are kept in `trial_classifications.csv` so the suggestion is inspectable. They never enter `map_assets.csv` or `competitive_map.csv`.

## Two overlays

| File | Grain | What a row means |
|---|---|---|
| `data/external/trial_review_overrides.csv` | NCT ID | Manual review of decision-critical trials (active industry CF, NCFB-flagged actives, key academic therapeutics, known heuristic false positives) |
| `data/external/program_reviews.csv` | CFF `program_id` | Active vs discontinued vs not-CF-primary vs preclinical-listing-only |

Empty override fields keep the auto-suggestion. `review_status` on an override row is always `reviewed`. A non-CF `disease_area` forces `map_eligible`, `whitespace_relevant`, and `crowding_unit` to 0.

## Auto-suggest

`src/cf_atlas/classify.py` applies first-match keyword rules to title, summary, conditions, and intervention names, plus the Phase 3 NCFB heuristic. Missing ClinicalTrials.gov phase is `not_applicable`, not Phase 0.

## Map grain

The competitive map is **program / asset**, not trial:

- CFF programs with a matching NCT inherit the trial’s clinical stage when present.
- Complementary molecules in one combination (SION-451 + SION-109 + SION-2222) count as **one** crowding unit.
- Earlier Vertex modulators (Kalydeco, Orkambi, Symdeko) stay visible as approved products but do not each add a crowding unit on top of Trikafta/Alyftrek.
- Trial-only assets (ABCI, BI 3720931, BMD003, NHS7108, VX-581, VX-272, selected academic therapeutics) appear when they are reviewed, CF, and map-eligible.

`crowding_unit=1` is the count used for strategy × stage tallies and crowding bands (none / low / moderate / high). `whitespace_relevant=1` marks investigational assets that are not approved-product label expansions or standard of care.

## What Phase 4 does not do

- No opportunity scores (Phase 5).
- Preclinical coverage is only as complete as the CFF pipeline page.
- Academic repurposing studies can be map-visible with `crowding_unit=0` so they do not inflate industry crowding.
