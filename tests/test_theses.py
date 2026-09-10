from cf_atlas.paths import processed_dir
from cf_atlas.theses import load_challenges, merge_memos, validate_challenges


def test_every_thesis_has_a_bear_case_and_kill_criteria():
    payload = validate_challenges()
    assert 5 <= len(payload["theses"]) <= 7
    theses_csv = processed_dir() / "scoring" / "theses.csv"
    if not theses_csv.exists():
        return
    import pandas as pd

    memos = merge_memos(pd.read_csv(theses_csv), payload)
    assert {row["thesis_id"] for row in memos} == {row["thesis_id"] for row in payload["theses"]}
    for memo in memos:
        assert memo["bear_case"].strip()
        assert memo["kill_criteria"].strip()
        assert memo["what_would_have_to_be_true"].strip()
        assert memo["counterarguments"]
        assert memo["remaining_diligence"]
        assert memo["kill_criteria"].lower().startswith("kill")
        assert memo["bull_case"].strip() != memo["bear_case"].strip()
        assert memo["parent_need_score"] == memo["display_default"]


def test_held_out_needs_are_not_default_newcos():
    payload = load_challenges()
    assert {row["need_id"] for row in payload["held_out"]} == {"N2", "N7"}
    thesis_needs = {row.get("need_id") for row in payload["theses"]}
    assert "N2" not in thesis_needs
    assert "N7" not in thesis_needs
