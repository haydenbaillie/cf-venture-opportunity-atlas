# Phase 3 — Patient and pipeline landscape

Completed 2026-09-09. Every headline number below has a row in `data/processed/landscape/landscape_claims.csv`.

Command: `python -m cf_atlas landscape`

## The question for this phase

What has actually been solved in US cystic fibrosis care after highly effective modulators, and what remains visible in public aggregate data — without scoring opportunities yet.

## FACT: the US Registry after modulators

Source: CFF Patient Registry 2024 Annual Data Report (retrieved 2026-09-09).

- 33,989 people in the Registry
- Predicted median survival 65.4 years (38.0 in 2009)
- Adults ≥18: 61.6% (33.8% in 1994); ages 60+: 1,437 people
- ~92% eligible for at least one modulator after Alyftrek; 87.5% of ages ≥12 prescribed a modulator
- IV-treated pulmonary exacerbations 12.1% (35.8% in 2009)
- Mean FEV1 89.1% predicted among ages >7 (79.0% in 2009)
- P. aeruginosa 23.3% of cultured (52.0% in 2009)
- Lung transplants 61 (249 in 2019)

## FACT: residual groups that are still countable

- 2,434 ineligible by age or genotype; 1,226 ineligible adolescents/adults with data
- 623 people aged ≥12 in 2020 with no CFTRm prescription 2022–2024
- CFRD 19.2% of the transplant-censored complications population; 29.3% of adults
- PERT still 80.2%
- Adult anxiety 31.9%; adult depression 30.2%
- Mean 3.0 clinic visits (4.3 in 2019); dornase 80.6% and hypertonic saline 62.6% of ages ≥6

Do not add these counts. They use different denominators.

## ANALYSIS: ClinicalTrials.gov is not a clean CF pipeline

Snapshot: interventional studies, `query.cond=cystic fibrosis`, retrieved 2026-09-09T22:49:42Z.

- 1,209 records
- 98 flagged as likely non-CF bronchiectasis / “non-cystic fibrosis” tagging noise (title/summary heuristic)
- 1,111 remaining CF-like records
- 62 recruiting after the heuristic; 106 active-like
- Start-year peak 76 studies in 2015; 30 in 2026 (partial year)
- Of 13 recruiting flagged records, 9 are industry-sponsored — so raw “industry recruiting in CF” is inflated by NCFB programs

This heuristic is **not** Phase 4 classification. It exists so whitespace is not scored on bronchiectasis drugs that matched because the word “cystic fibrosis” appears in “non-cystic fibrosis bronchiectasis.”

## INTERPRETATION (not a ranking)

1. Modulators solved CFTR function for most US Registry patients. Remaining causal restoration is a defined minority (N1) plus a mixed eligible-not-prescribed group (N2).
2. Pulmonary crisis rates and chronic PA fell; they did not vanish. Residual lung disease (N3) and infection (N4) are still visible, especially in older adults.
3. CFRD, PERT use, CFLD, mental health, and visit/therapy burden are adult-era problems. N5–N8 belong in the investigation set; none of them is a funded thesis yet.
4. Competitive intensity cannot be read from the unfiltered CT.gov extract.

## Outputs

- `data/processed/landscape/*.csv`
- `assets/figures/*.png`
- `analysis/notebooks/01_patient_and_pipeline_landscape.ipynb`

Phase 4 is reviewed classification of programs and trials, using the NCFB heuristic as a starting filter rather than as truth.
