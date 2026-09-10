# Analysis

Python package: `src/cf_atlas`.

```bash
python -m cf_atlas ingest-trials
python -m cf_atlas build-db
python -m cf_atlas landscape
python -m cf_atlas classify
python -m cf_atlas score
python -m cf_atlas theses
python -m cf_atlas export-app
```

Notebooks read those outputs. Do not treat notebook cells as a source of truth; persist cited figures into `data/processed/landscape`, `data/processed/classification`, `data/processed/scoring`, or `docs/`.

Phase 3 notebook: `analysis/notebooks/01_patient_and_pipeline_landscape.ipynb`.
