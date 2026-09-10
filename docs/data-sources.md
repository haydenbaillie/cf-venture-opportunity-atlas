# Data sources

Retrieval date for this catalog: **2026-09-09**. Machine-readable copy: `data/external/sources.csv`.

## Programmatic

### ClinicalTrials.gov Data API v2

- Organization: U.S. National Library of Medicine
- URL: https://clinicaltrials.gov/api/v2/studies
- Docs: https://clinicaltrials.gov/data-api/api
- Access: no API key
- MVP query: condition `cystic fibrosis`, `filter.advanced=AREA[StudyType]INTERVENTIONAL`
- Live check and ingest on 9 Sep 2026: 1,768 studies for the condition query; **1,209 interventional studies saved** (`retrieved_at` 2026-09-09T22:49:42Z)
- Use: NCT ID, title, sponsor, phase, status, dates, enrollment, eligibility, interventions, outcomes
- Limits: sponsor-reported; noisy condition tags; almost no preclinical coverage

### openFDA Drugs@FDA (reserved)

- URL: https://api.fda.gov/drug/drugsfda.json
- Access: programmatic; optional key raises rate limits
- Not ingested in Phase 2. Approval rows currently come from labels and CFF listings.

### PubMed E-utilities (reserved)

- Docs: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- Not ingested in Phase 2.

## Manual / public documents

### CFF Patient Registry 2024 Annual Data Report

- Organization: Cystic Fibrosis Foundation
- URL: https://www.cff.org/media/38406/download
- Publication: October 2025
- Access: public PDF; **no patient-level API**
- Use: demographics, survival, modulator subgroups, infection, pulmonary outcomes, CFRD, GI/liver, aging, utilization
- Transcription method: manual from published tables and narrative, stored in `data/external/registry_stats.csv`

### CFF Drug Development Pipeline

- URL: https://www.cff.org/Trials/Pipeline
- Access: interactive webpage, **not an API**
- Use: preclinical programs and CFF therapeutic-approach labels
- Limits: includes discontinued assets; stage labels can lag

### FDA labels

- Trikafta USPI: https://pi.vrtx.com/files/uspi_elexacaftor_tezacaftor_ivacaftor.pdf
- Kalydeco label: https://www.accessdata.fda.gov/drugsatfda_docs/label/2025/203188s042,207925s020lbl.pdf
- Alyftrek label: https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/218730s001lbl.pdf
- Use: indication, genotype scope, age, initial approval year

### FDA Orphan Drug Designations

- URL: https://www.accessdata.fda.gov/scripts/opdlisting/oopd/
- Access: search form + Excel download; **no public API**
- Not ingested in Phase 2.

### CFTR2

- URL: https://cftr2.org/
- Access: variant pages; **no public API**
- Not ingested in Phase 2.
