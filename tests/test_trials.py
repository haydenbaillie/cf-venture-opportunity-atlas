from __future__ import annotations

import json
from pathlib import Path

from cf_atlas.ingest import process_studies, read_raw_jsonl
from cf_atlas.trials import flatten_trial

FIXTURE = Path(__file__).parent / "fixtures" / "studies.jsonl"


def test_flatten_trial_phase_and_sponsor():
    study = json.loads(FIXTURE.read_text(encoding="utf-8").splitlines()[0])
    row = flatten_trial(study, retrieved_at="2026-09-09T00:00:00+00:00", source_id="test")
    assert row["nct_id"] == "NCT00000001"
    assert row["phase"] == "PHASE2"
    assert row["lead_sponsor_class"] == "INDUSTRY"
    assert row["overall_status"] == "RECRUITING"
    assert row["enrollment_count"] == 40
    assert row["is_fda_regulated_drug"] == 1
    assert "ppFEV1" in row["primary_outcomes"]


def test_process_fixture_jsonl():
    studies = list(read_raw_jsonl(FIXTURE))
    trials, interventions, collaborators = process_studies(
        studies,
        retrieved_at="2026-09-09T00:00:00+00:00",
        source_id="test",
    )
    assert len(trials) == 2
    assert set(trials["nct_id"]) == {"NCT00000001", "NCT00000002"}
    assert trials.loc[trials["nct_id"] == "NCT00000002", "phase"].iloc[0] == "PHASE1;PHASE2"
    assert len(interventions) == 2
    assert "mockaftor" in set(interventions["intervention_name"])
    assert len(collaborators) == 1
    assert collaborators.iloc[0]["name"] == "Cystic Fibrosis Foundation"
