# Scoring rubrics

The CF Venture Opportunity Score is an **exploratory prioritization index**. It does not imply mathematical certainty and must never be presented as a reason to fund a company.

No category scores are assigned in Phase 2. This file defines the model so later scoring is auditable. Phase 5 assigned the 1–5 scores in `data/external/component_scores.csv` and wrote `data/processed/scoring/`.

## Formula

Each unmet-need category receives six component scores on a **1–5** rubric.

\[
\text{Score} = 20 \times \sum_i (w_i \times s_i)
\]

With weights summing to 1, the index runs from 20 to 100. Display as an integer `/100`. Always show component scores and weights.

## Default weights

| Component | Weight | 1 | 3 | 5 |
|---|---|---|---|---|
| Patient need | 25% | Small residual group and modest burden | Material residual burden in a defined subgroup | Large residual population and/or severe morbidity, mortality, or QoL gap |
| Treatment gap | 20% | Effective, accessible options for most of the group | Partial options or large residual disease on treatment | No adequate disease-modifying option, or a large excluded / intolerant group |
| Competitive white space | 20% | Many well-resourced active programs | Several programs or late-stage crowding in an adjacent indication | Few active programs aimed at this specific problem |
| Scientific / clinical tractability | 15% | Unclear biology or no feasible endpoint | Plausible biology, messy endpoints | Clear biology, measurable endpoint, therapeutic precedent |
| Economic / commercial relevance | 10% | Episodic or poorly reimbursable | Chronic with mixed payer logic | Chronic, costly residual burden with plausible payer value |
| Momentum / why now | 10% | No recent enabling change | Incremental change | A concrete recent shift in technology, regulation, demographics, or failed incumbents |

Economic relevance is **not** a TAM. Do not scale 33,989 US Registry participants to a global market without a separate cited source.

## Evidence confidence (separate)

Never fold this into the 0–100 index.

- **High** — multiple primary sources (e.g. CFF + FDA/CT.gov + peer-reviewed)
- **Moderate** — credible but incomplete or indirect
- **Low** — thin, assumption-heavy, or mostly unreviewed pipeline narrative

Display as: `Opportunity Score: 72/100 · Evidence: Moderate`.

## Presets

Stored in `data/external/scoring_weights.csv`. These are analytical perspectives, not truths.

- **default** — weights above
- **patient_impact** — up-weights need and gap
- **venture_creation** — up-weights whitespace and tractability
- **commercial** — up-weights economic relevance and whitespace

Phase 5 added rank-stability under ±10 percentage-point weight shifts. On the 9 Sep 2026 snapshot, default top-three membership (N5, N1, N4) was stable across presets and those shifts; order inside the top three was not.

## What trial counts may and may not do

Trial and program counts may inform the **competitive white space** component after human review. They must not set patient need, tractability, or why-now by themselves.

## Theses

Theses inherit the parent need score. They are not a second index. Each default card must have kill criteria and a bear case (`data/external/thesis_challenges.json`).

