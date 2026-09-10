# Methodology

This project separates **facts** (cited public numbers), **analysis** (counts, joins, trends), **interpretation** (what those patterns may mean), and **hypotheses** (venture theses that must be pressure-tested).

## What Phase 2 implements

1. A dated ClinicalTrials.gov interventional-study snapshot.
2. A curated CFF 2024 Registry statistic table, transcribed from the published Annual Data Report rather than OCR-scraped.
3. A curated CFF pipeline snapshot transcribed from the public pipeline page.
4. A SQLite schema that can be rebuilt from those files.

It does **not** yet classify every trial, score opportunities, or present an application.

## Trial universe

Default query (verified 9 Sep 2026):

- Endpoint: `https://clinicaltrials.gov/api/v2/studies`
- `query.cond=cystic fibrosis`
- `filter.advanced=AREA[StudyType]INTERVENTIONAL`

`filter.studyType` is **not** a valid v2 parameter. Pagination uses `nextPageToken`. Records are sponsor-reported.

Each trial row stores `retrieved_at`. The database `meta` table stores `db_built_at` and the min/max trial retrieval timestamps.

A large share of interventional studies have no FDA phase (`phase` is empty). Those are often devices, behavioral, or other non-drug interventions. Do not treat missing phase as Phase 0.

The API returned HTTP 403 when called with a browser-like or custom research User-Agent from this environment; the default `httpx` client identifier succeeded. Ingest therefore does not override User-Agent.

A title/summary heuristic flags likely **non-cystic fibrosis bronchiectasis** records that matched `query.cond=cystic fibrosis`. That filter is analysis, not reviewed classification. Phase 4 must not score whitespace on the unfiltered extract.

## Classification (Phase 4)

See [classification.md](classification.md). Auto-suggested labels exist for every trial. The competitive map is built only from `review_status=reviewed`, `disease_area=cf`, and `map_eligible=1`. Command: `python -m cf_atlas classify`.

## Scoring (Phase 5)

See [scoring-rubrics.md](scoring-rubrics.md). Component scores are 1–5 expert rubrics on cited evidence, not a regression on trial counts. Evidence confidence is a separate High / Moderate / Low label. Command: `python -m cf_atlas score`. Rankings use Phase 4 reviewed coverage for whitespace only.

## Theses (Phase 7–8)

See [theses/README.md](theses/README.md). Seven challenge memos sit at `/opportunities/H1` through `/opportunities/H7`. Each memo has a bear case, counterarguments, remaining diligence, and kill criteria. Command: `python -m cf_atlas theses`.

N2 and N7 remain scored investigation categories. They are not default company-formation cards.

## What Phase 9 publishes

README, [executive-summary.md](executive-summary.md), [presentation/outline.md](presentation/outline.md), and app screenshots. The interactive app remains snapshot-backed.

## Epidemiology

CFF Patient Registry figures describe consenting people seen at US accredited care centers. Complication chapters generally exclude lung-transplant recipients. 2024 modulator-eligibility charts generally do not treat Alyftrek (approved 20 Dec 2024) as conferring eligibility unless the text says otherwise. Fewer in-person visits since 2020 reduce culture and PFT ascertainment.

## Geography

Do not mix US Registry denominators with worldwide trial counts without stating both geographies.
