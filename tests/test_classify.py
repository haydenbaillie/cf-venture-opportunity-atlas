from __future__ import annotations

import pandas as pd
import pytest

from cf_atlas.classify import (
    apply_trial_overrides,
    build_map_assets,
    crowding_band,
    map_eligible_mask,
    normalize_stage,
    suggest_strategy,
    suggest_trial_row,
)
from cf_atlas.landscape import flag_ncfb
from cf_atlas.paths import sqlite_path


def test_strategy_rules_hit_known_assets():
    assert suggest_strategy("4D-710 in Adult Patients With Cystic Fibrosis")[0] == "gene_therapy"
    assert suggest_strategy("Study With Phage for CF Subjects BX004")[0] == "phage"
    assert suggest_strategy("Safety of ARCT-032 inhaled CFTR mRNA")[0] == "mrna"
    assert suggest_strategy("Yoga Outcomes Get Assessed in Cystic Fibrosis")[0] == "care_delivery"
    assert suggest_strategy("ABCI amphotericin B cystetic for inhalation")[0] == "anion_bypass"


def test_ncfb_heuristic_false_positive_is_overridable():
    title = "Beta-cell Response to Incretin Hormones in Cystic Fibrosis"
    assert flag_ncfb(title) is None
    blob = title + " non-cystic fibrosis comparison arm in the summary"
    assert flag_ncfb(blob)
    suggested = suggest_trial_row(blob, "NA", "DRUG", flag_ncfb(blob))
    assert suggested["disease_area"] == "ncfb"
    trials = pd.DataFrame(
        [
            {
                "nct_id": "NCT01851694",
                "brief_title": title,
                "official_title": "",
                "brief_summary": "non-cystic fibrosis comparison",
                "conditions": "Cystic Fibrosis",
                "overall_status": "RECRUITING",
                "lead_sponsor_class": "OTHER",
                "lead_sponsor_name": "University",
                "phase": "NA",
                "start_date": "2013-01-01",
                "retrieved_at": "2026-09-09",
                "source_id": "test",
                "intervention_types": "DRUG",
                "intervention_names": "Incretin",
                "ncfb_heuristic": flag_ncfb(blob),
                "is_active": True,
                "normalized_stage": "not_applicable",
            }
        ]
    )
    overrides = pd.DataFrame(
        [
            {
                "nct_id": "NCT01851694",
                "disease_area": "cf",
                "strategy": "metabolic_cfrd",
                "need_ids": "N5",
                "role": "supportive",
                "map_eligible": "0",
                "whitespace_relevant": "0",
                "crowding_unit": "0",
                "asset_name": "Incretin hormone physiology in CF",
                "company_name": "",
                "linked_program_id": "",
                "review_status": "reviewed",
                "review_notes": "heuristic false positive",
            }
        ]
    )
    classified = apply_trial_overrides(trials, overrides)
    row = classified.iloc[0]
    assert row["review_status"] == "reviewed"
    assert row["disease_area"] == "cf"
    assert row["strategy"] == "metabolic_cfrd"
    assert int(row["map_eligible"]) == 0


def test_auto_suggested_never_map_eligible():
    trials = pd.DataFrame(
        [
            {
                "nct_id": "NCT00000001",
                "brief_title": "4D-710 in Adult Patients With Cystic Fibrosis",
                "official_title": "",
                "brief_summary": "",
                "conditions": "Cystic Fibrosis",
                "overall_status": "RECRUITING",
                "lead_sponsor_class": "INDUSTRY",
                "lead_sponsor_name": "4DMT",
                "phase": "PHASE2",
                "start_date": "2022-01-01",
                "retrieved_at": "2026-09-09",
                "source_id": "test",
                "intervention_types": "BIOLOGICAL",
                "intervention_names": "4D-710",
                "ncfb_heuristic": None,
                "is_active": True,
                "normalized_stage": "phase_2",
            }
        ]
    )
    classified = apply_trial_overrides(trials, pd.DataFrame())
    assert classified.iloc[0]["review_status"] == "auto_suggested"
    assert int(classified.iloc[0]["map_eligible"]) == 0
    assert int(map_eligible_mask(classified).sum()) == 0


def test_map_assets_use_reviewed_cf_rows_only():
    programs = pd.DataFrame(
        [
            {
                "program_id": "cff-4d-710",
                "asset_name": "4D-710",
                "company_name": "4D Molecular Therapeutics",
                "activity_status": "active_clinical",
                "disease_area": "cf",
                "strategy": "gene_therapy",
                "need_ids": "N1",
                "role": "therapeutic",
                "map_eligible": 1,
                "whitespace_relevant": 1,
                "crowding_unit": 1,
                "nct_ids": "NCT05248230",
                "normalized_stage": "phase_2",
                "review_status": "reviewed",
                "review_notes": "",
            },
            {
                "program_id": "cff-brensocatib",
                "asset_name": "Brensocatib",
                "company_name": "Insmed",
                "activity_status": "not_cf_primary",
                "disease_area": "ncfb",
                "strategy": "anti_inflammatory",
                "need_ids": "N3",
                "role": "not_cf_primary",
                "map_eligible": 0,
                "whitespace_relevant": 0,
                "crowding_unit": 0,
                "nct_ids": "",
                "normalized_stage": "phase_2",
                "review_status": "reviewed",
                "review_notes": "NCFB",
            },
        ]
    )
    trials = pd.DataFrame(
        [
            {
                "nct_id": "NCT05248230",
                "brief_title": "4D-710",
                "lead_sponsor_class": "INDUSTRY",
                "lead_sponsor_name": "4D Molecular Therapeutics",
                "phase": "PHASE2",
                "normalized_stage": "phase_2",
                "disease_area": "cf",
                "strategy": "gene_therapy",
                "need_ids": "N1",
                "role": "therapeutic",
                "map_eligible": 1,
                "whitespace_relevant": 1,
                "crowding_unit": 1,
                "review_status": "reviewed",
                "asset_name": "4D-710",
                "company_name": "4D Molecular Therapeutics",
                "linked_program_id": "cff-4d-710",
                "review_notes": "",
            },
            {
                "nct_id": "NCT06559150",
                "brief_title": "Ensifentrine in NCFB",
                "lead_sponsor_class": "INDUSTRY",
                "lead_sponsor_name": "Verona",
                "phase": "PHASE2",
                "normalized_stage": "phase_2",
                "disease_area": "ncfb",
                "strategy": "anti_inflammatory",
                "need_ids": "",
                "role": "not_cf_primary",
                "map_eligible": 0,
                "whitespace_relevant": 0,
                "crowding_unit": 0,
                "review_status": "reviewed",
                "asset_name": "Ensifentrine",
                "company_name": "Verona",
                "linked_program_id": "",
                "review_notes": "",
            },
            {
                "nct_id": "NCT09999999",
                "brief_title": "Unreviewed yoga",
                "lead_sponsor_class": "OTHER",
                "lead_sponsor_name": "Hospital",
                "phase": "NA",
                "normalized_stage": "not_applicable",
                "disease_area": "cf",
                "strategy": "care_delivery",
                "need_ids": "N8",
                "role": "supportive",
                "map_eligible": 0,
                "whitespace_relevant": 0,
                "crowding_unit": 0,
                "review_status": "auto_suggested",
                "asset_name": "",
                "company_name": "Hospital",
                "linked_program_id": "",
                "review_notes": "",
            },
        ]
    )
    assets = build_map_assets(programs, trials)
    assert set(assets["asset_id"]) == {"cff-4d-710"}
    assert (assets["review_status"] == "reviewed").all()
    assert "Brensocatib" not in set(assets["asset_name"])
    assert "Ensifentrine" not in set(assets["asset_name"])


def test_normalize_stage_and_crowding_band():
    assert normalize_stage("PHASE1;PHASE2") == "phase_1"
    assert normalize_stage("PHASE4") == "approved"
    assert normalize_stage(None, "preclinical") == "preclinical"
    assert crowding_band(0) == "none"
    assert crowding_band(1) == "low"
    assert crowding_band(4) == "moderate"
    assert crowding_band(5) == "high"


def test_program_reviews_cover_every_cff_program():
    from cf_atlas.paths import external_dir

    programs = pd.read_csv(external_dir() / "cff_pipeline.csv")
    reviews = pd.read_csv(external_dir() / "program_reviews.csv")
    assert set(programs["program_id"]) == set(reviews["program_id"])
    assert reviews["review_status"].eq("reviewed").all()


def test_trial_overrides_have_unique_nct_ids():
    from cf_atlas.paths import external_dir

    overrides = pd.read_csv(external_dir() / "trial_review_overrides.csv")
    assert overrides["nct_id"].is_unique
    assert "NCT01851694" in set(overrides["nct_id"])
    incretin = overrides.loc[overrides["nct_id"] == "NCT01851694"].iloc[0]
    assert incretin["disease_area"] == "cf"
    ensifentrine = overrides.loc[overrides["nct_id"] == "NCT06559150"].iloc[0]
    assert ensifentrine["disease_area"] == "ncfb"
    assert int(ensifentrine["map_eligible"]) == 0


@pytest.mark.skipif(not sqlite_path().exists(), reason="atlas.sqlite is generated locally")
def test_classify_outputs_reviewed_map_only():
    from cf_atlas.classify import run_classify
    from cf_atlas.paths import processed_dir

    result = run_classify()
    assert result["nct01851694_cf"] == 1
    assets = pd.read_csv(processed_dir() / "classification" / "map_assets.csv")
    trials = pd.read_csv(processed_dir() / "classification" / "trial_classifications.csv")
    assert (assets["review_status"] == "reviewed").all()
    assert (assets["map_eligible"] == 1).all()
    names = set(assets["asset_name"].fillna("").astype(str))
    assert not any("Ensifentrine" in n for n in names)
    assert not any("Brensocatib" in n for n in names)
    incretin = trials.loc[trials["nct_id"] == "NCT01851694"].iloc[0]
    assert incretin["disease_area"] == "cf"
    assert incretin["review_status"] == "reviewed"
    assert int(incretin["map_eligible"]) == 0
    assert not assets["nct_ids"].fillna("").str.contains("NCT01851694").any()
