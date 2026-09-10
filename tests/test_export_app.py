from cf_atlas.export_app import build_snapshot
from cf_atlas.paths import processed_dir


def test_snapshot_requires_processed_tables_shape():
    scoring = processed_dir() / "scoring" / "need_scores.csv"
    if not scoring.exists():
        return
    payload = build_snapshot()
    assert payload["meta"]["trials_retrieved_at"].startswith("2026-09-09")
    assert len(payload["need_scores"]) == 8
    assert len(payload["theses"]) == 7
    assert len(payload["held_out"]) == 2
    assert all(row["bear_case"] for row in payload["theses"])
    assert all(row["kill_criteria"] for row in payload["theses"])
    assert {row["need_id"] for row in payload["held_out"]} == {"N2", "N7"}
    assert all(int(row["map_eligible"]) == 1 for row in payload["map_assets"])
    assert all(row["review_status"] == "reviewed" for row in payload["map_assets"])
    ncfb_names = " ".join(str(row["asset_name"]) for row in payload["map_assets"])
    assert "Ensifentrine" not in ncfb_names
    assert "Brensocatib" not in ncfb_names
