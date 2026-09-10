# Limitations

## Data that are not public

- CFF Patient Registry **patient-level** files
- A CFF pipeline JSON API
- FDA orphan-designation API (Excel download only)
- CFTR2 bulk API
- CMS identifiable CF claims (Research Identifiable Files require a DUA)

If a requested cross-tab (for example genotype × payer × FEV1) is not in the published Registry tables, this project will not fabricate it.

## Epidemiology caveats

- CFF figures are US accredited-care-center consenters, not the global CF population.
- Complication prevalence generally **excludes lung-transplant recipients**, so the denominator (~32,492 in 2024) is smaller than the demographic total (33,989).
- Alyftrek was approved 20 Dec 2024. Unless a figure says otherwise, 2024 eligibility charts still treat VTD-only patients as ineligible.
- Fewer clinic visits since 2020 reduced cultures and PFTs. Declines in infection and exacerbations are real and partly measurement-sensitive.
- “Eligible but not prescribed” is a mixed group (access, side effects, milder phenotype). It is not interchangeable with genotype-ineligible.

## Pipeline caveats

- ClinicalTrials.gov starts at human studies. Preclinical coverage depends on the CFF webpage and company pages and will be incomplete.
- The CFF pipeline page lists discontinued programs. Phase 4 `program_reviews.csv` marks those rows discontinued, inactive, or not-CF-primary; they stay in the snapshot but are off the competitive map.
- Keyword classification is a suggestion only. Rankings and the map use reviewed CF map-eligible rows.
- Private-company capitalization is not a reproducible public dataset.

## Scoring caveats

- The opportunity index is exploratory. It is not a funding recommendation and is not a valuation.
- Integer display only on thesis cards. Evidence confidence is never averaged into the score.
- Challenge memos are hypotheses with kill criteria. A high score is not a reason to form a company.

## Product caveats

- This is not medical advice.
- This is not a securities recommendation.
- No personal health information is used.
