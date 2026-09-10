# Application

Interactive research interface for the CF Venture Opportunity Atlas.

```bash
python -m cf_atlas export-app
cd app
npm install
npm run dev
```

Opens at [http://localhost:3000](http://localhost:3000).

Routes:

- `/` Home — research question and data-as-of stamp
- `/landscape` — patient and approved-therapy snapshot
- `/pipeline` — ClinicalTrials.gov-derived trial views
- `/map` — strategy × stage and reviewed assets
- `/opportunities` — ranked cards, weight presets, kill criteria
- `/methodology` — sources, rubrics, limitations

The app reads `src/data/snapshot.json`, a dated export of processed tables. It does not call live APIs.

This is not medical advice and not a securities recommendation.
