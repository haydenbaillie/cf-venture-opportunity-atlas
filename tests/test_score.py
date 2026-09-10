from __future__ import annotations

import pandas as pd
import pytest

from cf_atlas.paths import external_dir, processed_dir
from cf_atlas.score import (
    COMPONENTS,
    compute_index,
    display_score,
    load_component_scores,
    load_weights,
    need_score_table,
    shift_weight,
    validate_whitespace_alignment,
)


def test_index_bounds_and_formula():
    weights = {c: 1 / 6 for c in COMPONENTS}
    assert display_score(compute_index({c: 1 for c in COMPONENTS}, weights)) == 20
    assert display_score(compute_index({c: 5 for c in COMPONENTS}, weights)) == 100
    mixed = dict.fromkeys(COMPONENTS, 3)
    mixed["patient_need"] = 5
    default = {
        "patient_need": 0.25,
        "treatment_gap": 0.20,
        "competitive_whitespace": 0.20,
        "tractability": 0.15,
        "economic": 0.10,
        "why_now": 0.10,
    }
    value = compute_index(mixed, default)
    expected = 20 * (0.25 * 5 + 0.20 * 3 + 0.20 * 3 + 0.15 * 3 + 0.10 * 3 + 0.10 * 3)
    assert abs(value - expected) < 1e-9
    assert 20 <= display_score(value) <= 100


def test_evidence_is_not_in_the_formula():
    weights = {c: 1 / 6 for c in COMPONENTS}
    scores = {c: 4 for c in COMPONENTS}
    assert compute_index(scores, weights) == compute_index(scores, weights)


def test_shifted_weights_renormalize():
    default = {
        "patient_need": 0.25,
        "treatment_gap": 0.20,
        "competitive_whitespace": 0.20,
        "tractability": 0.15,
        "economic": 0.10,
        "why_now": 0.10,
    }
    up = shift_weight(default, "competitive_whitespace", 0.10)
    down = shift_weight(default, "competitive_whitespace", -0.10)
    assert abs(sum(up.values()) - 1) < 1e-9
    assert abs(sum(down.values()) - 1) < 1e-9
    assert abs(up["competitive_whitespace"] - 0.30) < 1e-9
    assert abs(down["competitive_whitespace"] - 0.10) < 1e-9


def test_curated_scores_cover_all_needs():
    components = load_component_scores()
    weights = load_weights()
    assert set(components["need_id"]) == {f"N{i}" for i in range(1, 9)}
    assert set(components["component_id"]) == set(COMPONENTS)
    assert weights.groupby("preset_id")["weight"].sum().sub(1).abs().lt(1e-9).all()
    scored = need_score_table(components, weights)
    assert scored["display_default"].between(20, 100).all()
    assert scored["need_id"].is_unique


def test_theses_are_hypotheses_not_a_second_index():
    theses = pd.read_csv(external_dir() / "opportunity_theses.csv")
    assert 5 <= len(theses) <= 7
    assert theses["thesis_id"].is_unique
    assert set(theses["need_id"]) <= {f"N{i}" for i in range(1, 9)}
    assert theses["kill_criteria"].fillna("").ne("").all()


@pytest.mark.skipif(
    not (processed_dir() / "classification" / "need_pipeline_coverage.csv").exists(),
    reason="classify outputs are generated locally",
)
def test_whitespace_scores_follow_reviewed_crowding():
    from cf_atlas.score import attach_coverage, run_score

    coverage = pd.read_csv(processed_dir() / "classification" / "need_pipeline_coverage.csv")
    components = load_component_scores()
    weights = load_weights()
    scored = attach_coverage(need_score_table(components, weights), coverage)
    validate_whitespace_alignment(scored)
    result = run_score()
    assert result["needs_scored"] == 8
    theses = pd.read_csv(processed_dir() / "scoring" / "theses.csv")
    assert theses["parent_need_score"].between(20, 100).all()
    # Auto-suggested care-delivery trials must not create an N8 product crowding score of 1.
    n8 = scored.loc[scored["need_id"] == "N8"].iloc[0]
    assert int(n8["competitive_whitespace"]) >= 4
    stability = pd.read_csv(processed_dir() / "scoring" / "rank_stability.csv")
    assert not stability["scenario"].str.contains("preset:line").any()
    assert set(stability.loc[stability["scenario"].str.startswith("preset:"), "scenario"]) == {
        "preset:default",
        "preset:patient_impact",
        "preset:venture_creation",
        "preset:commercial",
    }
