from __future__ import annotations

import sqlite3
from pathlib import Path

from cf_atlas.db import build_db
from cf_atlas.ingest import process_studies, read_raw_jsonl, write_processed
from cf_atlas.paths import external_dir

FIXTURE = Path(__file__).parent / "fixtures" / "studies.jsonl"


def test_build_db_from_fixture(tmp_path: Path):
    studies = list(read_raw_jsonl(FIXTURE))
    trials, interventions, collaborators = process_studies(
        studies,
        retrieved_at="2026-09-09T12:00:00+00:00",
        source_id="clinicaltrials_gov_api_v2",
    )
    processed = tmp_path / "processed"
    processed.mkdir()
    original_processed = write_processed
    # write_processed always uses repo processed_dir; write locally instead
    trials.to_csv(processed / "trials.csv", index=False)
    interventions.to_csv(processed / "trial_interventions.csv", index=False)
    collaborators.to_csv(processed / "trial_collaborators.csv", index=False)

    db_path = tmp_path / "atlas.sqlite"
    result = build_db(
        sqlite_file=db_path,
        processed=processed,
        external=external_dir(),
    )

    assert db_path.exists()
    assert result["trials"] == 2
    assert result["unmet_needs"] == 8
    conn = sqlite3.connect(db_path)
    try:
        trial_count = conn.execute("SELECT COUNT(*) FROM trials").fetchone()[0]
        meta = dict(conn.execute("SELECT key, value FROM meta"))
        n1 = conn.execute(
            "SELECT category FROM unmet_needs WHERE need_id = 'N7'"
        ).fetchone()[0]
        weights = conn.execute(
            "SELECT SUM(weight) FROM scoring_weights WHERE preset_id = 'default'"
        ).fetchone()[0]
        source = conn.execute(
            "SELECT access_method FROM sources WHERE source_id = 'clinicaltrials_gov_api_v2'"
        ).fetchone()[0]
    finally:
        conn.close()

    assert trial_count == 2
    assert meta["trial_count"] == "2"
    assert meta["trials_retrieved_at_max"] == "2026-09-09T12:00:00+00:00"
    assert n1 == "Aging with CF"
    assert abs(weights - 1.0) < 1e-9
    assert source == "programmatic"
    assert original_processed is write_processed
