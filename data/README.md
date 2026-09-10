# Data layout

```
data/
  raw/           original retrievals (API dumps, optional PDF copies)
  external/      hand-curated tables that are part of the published snapshot
  processed/     generated tidy CSVs and atlas.sqlite
```

## Rebuild

From the repository root, with the package installed (`pip install -e .`):

```bash
python -m cf_atlas rebuild
```

That command:

1. Calls ClinicalTrials.gov Data API v2 with `query.cond=cystic fibrosis` and `filter.advanced=AREA[StudyType]INTERVENTIONAL`.
2. Writes `data/raw/clinicaltrials/studies.jsonl` and `manifest.json`.
3. Writes `data/processed/trials.csv`, `trial_interventions.csv`, and `trial_collaborators.csv`.
4. Loads curated `data/external/*.csv` plus those processed tables into `data/processed/atlas.sqlite`.

`studies.jsonl` and `atlas.sqlite` are gitignored (`sqlite` is rebuilt from CSVs). `manifest.json` and the processed trial CSVs are the dated snapshot. After a clone:

```bash
python -m cf_atlas build-db
python -m cf_atlas landscape   # Phase 3 tables + figures
python -m cf_atlas classify    # Phase 4 reviewed map
python -m cf_atlas score       # Phase 5 opportunity index
python -m cf_atlas theses      # Phase 7–8 challenge memos
python -m cf_atlas export-app  # JSON snapshot for the Next.js app
```

## Curated files

| File | Grain |
|---|---|
| `external/sources.csv` | One retrieval of one artifact |
| `external/registry_stats.csv` | One CFF published metric × year × stratum |
| `external/unmet_needs.csv` | N1–N8 investigation categories |
| `external/therapies.csv` | Approved or standard-of-care products |
| `external/cff_pipeline.csv` | CFF webpage snapshot (includes likely discontinued assets) |
| `external/strategy_taxonomy.csv` | Classification vocabulary |
| `external/trial_review_overrides.csv` | Manual trial labels for the decision-critical subset |
| `external/program_reviews.csv` | Active / discontinued / not-CF-primary overlay on the CFF snapshot |
| `external/component_scores.csv` | Phase 5 1–5 rubric scores by need × component |
| `external/opportunity_theses.csv` | Seven hypothesis cards with kill criteria |
| `external/thesis_challenges.json` | Long-form bull/bear/diligence fields for those cards |
| `external/scoring_components.csv` | Rubric components |
| `external/scoring_weights.csv` | Default and scenario presets |

Do not invent patient-level rows. If a cross-tab is not in the published CFF tables, it does not belong here.

## Landscape outputs (Phase 3)

`python -m cf_atlas landscape` writes `data/processed/landscape/`:

- `landscape_claims.csv` — every headline number with layer (fact / analysis / interpretation / hypothesis) and `source_id`
- `solved_unsolved.csv` — domain-level solved vs remains
- `need_snapshots.csv` — N1–N8 anchors
- `ncfb_flagged_trials.csv` — likely non-CF bronchiectasis tagging noise
- trial year / status / phase / sponsor summaries

## Classification outputs (Phase 4)

`python -m cf_atlas classify` writes `data/processed/classification/`:

- `trial_classifications.csv` — auto-suggest plus review overlay for every NCT
- `program_classifications.csv` — CFF programs after `program_reviews.csv`
- `map_assets.csv` — reviewed, CF, map-eligible programs and unmatched trials
- `competitive_map.csv` — strategy × stage counts of `crowding_unit=1` assets
- `need_pipeline_coverage.csv` — N1–N8 coverage from the map (auto-suggested counts are context only)
- `classification_summary.csv` — headline counts including the NCT01851694 override check

## Scoring outputs (Phase 5)

`python -m cf_atlas score` writes `data/processed/scoring/`:

- `need_scores.csv` — 1–5 components plus 0–100 index under four weight presets
- `component_detail.csv` — rationale-bearing component rows joined to ranks
- `sensitivity.csv` — ±10 percentage-point weight shifts
- `rank_stability.csv` — top-three membership under presets and shifts
- `theses.csv` — seven hypothesis cards inheriting the parent need score
- `thesis_memos.json` — merged challenge memos (bull, bear, remaining diligence)

Markdown memos: `docs/theses/`. App routes: `/opportunities/H1` … `H7`.

